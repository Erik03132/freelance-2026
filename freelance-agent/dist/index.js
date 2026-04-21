"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
const browser_1 = require("./services/browser");
const storage_1 = require("./services/storage");
const logger_1 = require("./services/logger");
const matcher_1 = require("./services/matcher");
const network_1 = require("./utils/network");
const kwork_1 = require("./adapters/kwork");
const freelance_1 = require("./adapters/freelance");
const flru_1 = require("./adapters/flru");
const scout_1 = require("./agents/scout");
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
/**
 * Freelance Agent - главная точка входа
 * Работает с публичными данными бирж (без авторизации)
 */
class FreelanceAgent {
    browser;
    storage;
    logger;
    matcher;
    networkChecker;
    config;
    adapters = new Map();
    scout;
    constructor() {
        // Инициализация сервисов
        this.browser = new browser_1.BrowserService(true, new logger_1.Logger()); // headless = true (для стабильности в этом окружении)
        this.storage = new storage_1.StorageService();
        this.logger = new logger_1.Logger();
        this.networkChecker = new network_1.NetworkChecker(this.logger);
        // Загрузить конфигурацию
        this.config = this.loadConfig();
        // Инициализировать матчер
        this.matcher = new matcher_1.MatcherService(this.config.profile);
        // Инициализировать хранилище
        this.storage.init();
        // Инициализировать Шерлока (Scout)
        this.scout = new scout_1.ScoutAgent(this.config.profile, process.cwd(), this.browser);
        this.logger.log('AGENT_INIT', 'Инициализация агента завершена (Шерлок на связи)');
    }
    /**
     * Загрузить конфигурацию из файлов
     */
    loadConfig() {
        const profilePath = path.join(__dirname, '..', 'config', 'profile.json');
        const platformsPath = path.join(__dirname, '..', 'config', 'platforms.json');
        const profile = JSON.parse(fs.readFileSync(profilePath, 'utf-8'));
        const platformsData = JSON.parse(fs.readFileSync(platformsPath, 'utf-8'));
        return {
            profile,
            platforms: platformsData.platforms
        };
    }
    /**
     * Зарегистрировать адаптер платформы
     */
    registerAdapter(adapter) {
        this.adapters.set(adapter.name, adapter);
        this.logger.log('AGENT_REGISTER', `Зарегистрирован адаптер: ${adapter.name}`);
    }
    /**
     * Запустить агент для указанной платформы
     */
    async run(platformName) {
        this.logger.log('AGENT_RUN', 'Запуск агента', { platform: platformName || 'all' });
        try {
            // Проверить интернет-соединение
            console.log('\n🔍 Проверка сетевого соединения...');
            const internetCheck = await this.networkChecker.checkInternet();
            if (!internetCheck.success) {
                console.log(internetCheck.error);
                console.log('\n💡 Советы:');
                console.log('   1. Проверьте подключение к интернету');
                console.log('   2. Отключите VPN/прокси, если используете');
                console.log('   3. Проверьте настройки сети в macOS');
                console.log('   4. Попробуйте позже или с другой сети\n');
                this.logger.log('AGENT_RUN', 'Нет интернета, завершение');
                return;
            }
            console.log('✅ Интернет подключён\n');
            // Запустить браузер
            await this.browser.launch();
            this.logger.log('BROWSER', 'Браузер запущен');
            // Определить, какие платформы запускать
            const platforms = platformName
                ? this.config.platforms.filter(p => p.name === platformName && p.enabled)
                : this.config.platforms.filter(p => p.enabled);
            if (platforms.length === 0) {
                this.logger.log('AGENT_RUN', 'Нет включённых платформ');
                return;
            }
            // Проверить доступность платформ
            console.log('🔍 Проверка доступности платформ...');
            const availablePlatforms = [];
            for (const platform of platforms) {
                const platformCheck = await this.networkChecker.checkPlatform(platform.jobsUrl);
                if (platformCheck.success) {
                    availablePlatforms.push(platform);
                    console.log(`  ✅ ${platform.displayName} — доступен`);
                }
                else {
                    console.log(`  ⚠️ ${platform.displayName} — недоступен`);
                    this.logger.log('PLATFORM_UNAVAILABLE', platformCheck.error || '', { platform: platform.name });
                }
            }
            if (availablePlatforms.length === 0) {
                console.log('\n❌ Ни одна платформа не доступна. Проверьте:');
                console.log('   • Блокировку сайтов (Роскомнадзор)');
                console.log('   • Проблемы с DNS');
                console.log('   • Временную недоступность сервисов\n');
                return;
            }
            console.log(`\n✅ Доступно платформ: ${availablePlatforms.length}\n`);
            this.logger.log('AGENT_RUN', `Платформы: ${availablePlatforms.map(p => p.displayName).join(', ')}`);
            const allResults = [];
            for (const platformConfig of availablePlatforms) {
                const scoredJobs = await this.processPlatform(platformConfig.name);
                // Добавляем в общий список для вывода (без детального анализа Шерлока)
                allResults.push(...scoredJobs);
            }
            // Вывести результаты
            this.printResults(allResults);
            // Сформировать отчёт
            this.generateReport(allResults);
            this.logger.log('AGENT_RUN', 'Завершение работы');
        }
        catch (error) {
            this.logger.error('AGENT_RUN', error);
            throw error;
        }
        finally {
            // Закрыть браузер
            await this.browser.close();
            this.storage.close();
        }
    }
    /**
     * Обработать платформу
     */
    async processPlatform(platformName) {
        this.logger.log('PLATFORM', `Обработка платформы: ${platformName}`);
        // Получить или создать адаптер
        const adapter = this.getAdapter(platformName);
        if (!adapter) {
            this.logger.log('PLATFORM', `Адаптер не найден: ${platformName}`);
            return [];
        }
        try {
            // Перейти к задачам (без авторизации)
            const navSuccess = await adapter.navigateToJobs();
            if (!navSuccess) {
                this.logger.log('PLATFORM', `Не удалось перейти к задачам: ${platformName}`);
                console.log(`  ⚠️ Пропуск платформы ${platformName} (ошибка сети)\n`);
                return [];
            }
            // Извлечь задачи
            const jobs = await adapter.extractJobs();
            this.logger.log('PLATFORM', `Извлечено ${jobs.length} задач с ${platformName}`);
            // Сохранить ВСЕ задачи в БД сразу после извлечения
            this.storage.saveJobs(jobs);
            // Оценить и отфильтровать задачи
            const scoredJobs = this.scoreAndFilterJobs(jobs);
            this.logger.log('PLATFORM', `Подходящих задач: ${scoredJobs.length}`);
            return scoredJobs;
        }
        catch (error) {
            this.logger.error('PLATFORM', error, { platform: platformName });
            return [];
        }
    }
    /**
     * Оценить и отфильтровать задачи
     */
    scoreAndFilterJobs(jobs) {
        const scoredJobs = [];
        for (const job of jobs) {
            // Рассчитать skill match score
            const skillMatchScore = this.matcher.calculateSkillMatch(job);
            // Рассчитать clarity score
            const clarityScore = this.matcher.calculateClarityScore(job);
            // Проверить пороги
            const passes = this.matcher.passesThresholds(job, skillMatchScore, clarityScore);
            this.logger.log('MATCHER', `Задача: ${job.title.slice(0, 40)}`, {
                skillMatch: skillMatchScore,
                clarity: clarityScore,
                budget: job.budget?.amount || job.budget?.min,
                passes
            });
            // Сохранить оценки в БД для всех задач
            const existingJob = this.storage.getJobs({ url: job.url })[0];
            if (existingJob && existingJob.id) {
                this.storage.updateJobScores(Number(existingJob.id), skillMatchScore, clarityScore);
            }
            if (passes) {
                scoredJobs.push({
                    job,
                    skillMatchScore,
                    clarityScore,
                    overallScore: Math.round((skillMatchScore * 0.7 + clarityScore * 0.3) * 100) / 100
                });
            }
        }
        // Сортировать по overall score (убывание)
        scoredJobs.sort((a, b) => b.overallScore - a.overallScore);
        return scoredJobs;
    }
    /**
     * Получить адаптер для платформы
     */
    getAdapter(platformName) {
        // Проверить кэш
        const cached = this.adapters.get(platformName);
        if (cached)
            return cached;
        // Создать новый адаптер
        let adapter = null;
        switch (platformName) {
            case 'kwork':
                adapter = new kwork_1.KworkAdapter(this.browser, this.logger);
                break;
            case 'freelance':
                adapter = new freelance_1.FreelanceAdapter(this.browser, this.logger);
                break;
            case 'flru':
                adapter = new flru_1.FLruAdapter(this.browser, this.logger);
                break;
            default:
                this.logger.log('ADAPTER', `Неизвестная платформа: ${platformName}`);
                return null;
        }
        this.adapters.set(platformName, adapter);
        return adapter;
    }
    /**
     * Вывести результаты в консоль
     */
    printResults(scoredJobs) {
        console.log('\n' + '='.repeat(80));
        console.log('  ПОДХОДЯЩИЕ ЗАДАЧИ');
        console.log('='.repeat(80) + '\n');
        if (scoredJobs.length === 0) {
            console.log('  😔 Подходящих задач не найдено\n');
            console.log('='.repeat(80) + '\n');
            return;
        }
        console.log(`  Найдено задач: ${scoredJobs.length}\n`);
        // Вывести топ-10 задач
        const topJobs = scoredJobs.slice(0, 10);
        for (let i = 0; i < topJobs.length; i++) {
            const { job, skillMatchScore, clarityScore, overallScore } = topJobs[i];
            const rank = i + 1;
            // Форматировать бюджет
            const budgetStr = job.budget
                ? job.budget.type === 'hourly'
                    ? `₽${job.budget.min || 0}–${job.budget.max || 0}/час`
                    : `₽${job.budget.amount || 0}`
                : 'договорная';
            // Индикаторы
            const skillIndicator = this.getScoreIndicator(skillMatchScore);
            const clarityIndicator = this.getScoreIndicator(clarityScore);
            const overallIndicator = this.getScoreIndicator(overallScore);
            console.log(`  ${rank}. ${job.title}`);
            console.log(`     Платформа: ${this.getPlatformDisplayName(job.platform)}`);
            console.log(`     Бюджет: ${budgetStr}`);
            console.log(`     🏁 Шерлок Score: ${topJobs[i].proposalResult?.score || 0}/100`);
            console.log(`     Рейтинг: ${overallIndicator} ${overallScore.toFixed(2)}`);
            console.log(`     └─ Соответствие навыкам: ${skillIndicator} ${(skillMatchScore * 100).toFixed(0)}%`);
            console.log(`     └─ Качество ТЗ: ${clarityIndicator} ${(clarityScore * 100).toFixed(0)}%`);
            console.log(`     Ссылка: ${job.url}`);
            if (topJobs[i].proposalResult?.proposal) {
                console.log(`\n     🤖 ЭКСПЕРТНЫЙ ОФФЕР:`);
                console.log(`     ---------------------------------------------------------`);
                const pLines = topJobs[i].proposalResult.proposal.split('\n');
                pLines.forEach(line => console.log(`     ${line}`));
                console.log(`     ---------------------------------------------------------`);
            }
            console.log('');
        }
        if (scoredJobs.length > 10) {
            console.log(`  ... и ещё ${scoredJobs.length - 10} задач (см. отчёт)\n`);
        }
        console.log('='.repeat(80));
        console.log('  💡 Перейдите по ссылке, чтобы откликнуться на задачу');
        console.log('='.repeat(80) + '\n');
    }
    /**
     * Получить индикатор рейтинга
     */
    getScoreIndicator(score) {
        if (score >= 0.8)
            return '🟢';
        if (score >= 0.6)
            return '🟡';
        return '🔴';
    }
    /**
     * Получить отображаемое имя платформы
     */
    getPlatformDisplayName(platform) {
        const platformConfig = this.config.platforms.find(p => p.name === platform);
        return platformConfig?.displayName || platform;
    }
    /**
     * Сгенерировать отчёт
     */
    generateReport(scoredJobs) {
        const today = new Date().toISOString().split('T')[0];
        // Сформировать отчёт
        const report = {
            date: today,
            totalJobs: scoredJobs.length,
            byPlatform: {},
            byStatus: {},
            averageScores: {
                skillMatch: 0,
                clarity: 0,
                overall: 0
            },
            topJobs: scoredJobs.slice(0, 20).map(sj => ({
                title: sj.job.title,
                platform: sj.job.platform,
                url: sj.job.url,
                budget: sj.job.budget,
                skillMatchScore: sj.skillMatchScore,
                clarityScore: sj.clarityScore,
                overallScore: sj.overallScore
            }))
        };
        // Подсчитать по платформам
        for (const sj of scoredJobs) {
            report.byPlatform[sj.job.platform] = (report.byPlatform[sj.job.platform] || 0) + 1;
            report.byStatus[sj.job.status || 'new'] = (report.byStatus[sj.job.status || 'new'] || 0) + 1;
        }
        // Подсчитать средние оценки
        if (scoredJobs.length > 0) {
            report.averageScores.skillMatch = Math.round(scoredJobs.reduce((sum, sj) => sum + sj.skillMatchScore, 0) / scoredJobs.length * 100) / 100;
            report.averageScores.clarity = Math.round(scoredJobs.reduce((sum, sj) => sum + sj.clarityScore, 0) / scoredJobs.length * 100) / 100;
            report.averageScores.overall = Math.round(scoredJobs.reduce((sum, sj) => sum + sj.overallScore, 0) / scoredJobs.length * 100) / 100;
        }
        // Сохранить отчёт
        const reportPath = path.join(__dirname, '..', 'reports', `report-${today}.json`);
        fs.mkdirSync(path.dirname(reportPath), { recursive: true });
        fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
        this.logger.log('REPORT', 'Отчёт сгенерирован', report);
    }
}
// Точка входа
async function main() {
    const args = process.argv.slice(2);
    const platformArg = args.find(arg => arg.startsWith('--platform='));
    const platform = platformArg ? platformArg.split('=')[1] : undefined;
    const agent = new FreelanceAgent();
    // Зарегистрировать адаптеры
    agent.registerAdapter(new kwork_1.KworkAdapter(agent['browser'], agent['logger']));
    agent.registerAdapter(new freelance_1.FreelanceAdapter(agent['browser'], agent['logger']));
    agent.registerAdapter(new flru_1.FLruAdapter(agent['browser'], agent['logger']));
    try {
        await agent.run(platform);
        process.exit(0);
    }
    catch (error) {
        console.error('Ошибка при запуске агента:', error);
        process.exit(1);
    }
}
// Запуск
main();
