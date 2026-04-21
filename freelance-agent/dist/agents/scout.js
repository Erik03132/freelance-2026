"use strict";
/**
 * Sherlock Agent (Агент-Шерлок, ранее Скаут)
 *
 * Элитный агент-аналитик. Его задача — найти «жемчужины» среди сотен задач.
 * 1. Глубокий анализ ТЗ (дедукция)
 * 2. Оценка выгодности (ROI): только те задачи, где ₽/час > 1000
 * 3. Приоритизация (Скоринг): выбор лучших 30 задач в день для Кворка
 * 4. Мульти-агентная маршрутизация (передача спецам)
 */
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
exports.ScoutAgent = void 0;
const constitution_1 = require("../constants/constitution");
const team_1 = require("../constants/team");
const specialists_1 = require("./specialists");
const ai_1 = require("../utils/ai");
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
// =========================================================
// SHERLOCK AGENT (Scout)
// =========================================================
class ScoutAgent {
    profile;
    services;
    learnedPatterns;
    projectRoot;
    browser;
    agentName = team_1.TEAM_ROLES.SHERLOCK.NAME;
    agentRole = team_1.TEAM_ROLES.SHERLOCK.CODE;
    expertise = team_1.TEAM_ROLES.SHERLOCK.EXPERTISE;
    constructor(profile, projectRoot, browser) {
        this.profile = profile;
        this.projectRoot = projectRoot;
        this.browser = browser;
        this.services = this.loadAvailableServices();
        this.learnedPatterns = this.loadLearnedPatterns();
    }
    // =========================================================
    // ОСНОВНОЙ МЕТОД: Полный анализ задачи
    // =========================================================
    /**
     * [LEGACY] Анализирует задачу шаблонным методом.
     * Используйте analyzeAndProposeExpert() для мульти-агентной системы.
     */
    analyzeAndPropose(job) {
        // 1. Определить категорию задачи
        const category = this.detectCategory(job);
        // 2. Оценить выполнимость
        const feasibility = this.assessFeasibility(job, category);
        // 3. Собрать предупреждения для оператора
        const warnings = this.generateWarnings(job, feasibility);
        // 4. Сформировать заметки для оператора
        const operatorNotes = this.generateOperatorNotes(job, feasibility);
        // 5. Сгенерировать предложение (только если задача выполнима)
        let proposal = '';
        if (feasibility.feasible) {
            proposal = this.generateProposal(job, feasibility);
        }
        else {
            proposal = `⛔ ЗАДАЧА НЕ РЕКОМЕНДОВАНА К ВЫПОЛНЕНИЮ\n\nПричины:\n${feasibility.reasons.map(r => `• ${r}`).join('\n')}`;
        }
        // 6. Обучение: сохранить паттерн анализа
        this.saveAnalysisPattern(job, feasibility);
        // 7. Расчет скоринга (Шерлок оценивает приоритет)
        const score = this.calculateTaskScore(feasibility, job);
        return { proposal, feasibility, warnings, operatorNotes, score };
    }
    // =========================================================
    // МУЛЬТИ-АГЕНТНАЯ СИСТЕМА (новый подход)
    // =========================================================
    /**
     * Анализирует задачу и делегирует генерацию предложения
     * специализированному агенту через Router.
     *
     * Пайплайн:
     * 1. Категоризация задачи
     * 2. Оценка выполнимости (feasibility)
     * 3. Маршрутизация → специализированный агент
     * 4. Генерация экспертного предложения с обоснованиями
     * 5. Самообучение
     */
    async analyzeAndProposeExpert(job) {
        const TODAY = new Date().toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' });
        console.log(`🕵️‍♂️ [Sherlock] Анализ запущен. Дата: ${TODAY}`);
        // 0. Обработка вложений
        if (!job.attachmentsContent && job.hasAttachments && job.attachmentUrls && job.attachmentUrls.length > 0 && this.browser) {
            console.log(`📎 [Sherlock] Обнаружено вложений: ${job.attachmentUrls.length}. Попытка автоматического анализа...`);
            const attachmentsSummary = await this.handleAttachments(job);
            if (attachmentsSummary) {
                job.attachmentsContent = attachmentsSummary;
                console.log(`📄 [Sherlock] Авто-анализ завершен. Добавлено ${attachmentsSummary.length} символов контекста.`);
            }
        }
        else if (job.attachmentsContent) {
            console.log(`📝 [Sherlock] Использую ручной контекст вложений (${job.attachmentsContent.length} символов).`);
        }
        const category = this.detectCategory(job);
        const taskNature = category === 'operational_manual' ? 'dynamic' : 'static';
        // 2. Маршрутизация
        const routing = (0, specialists_1.routeTask)(job, category);
        const specialist = (0, specialists_1.getAgent)(routing.primaryAgent);
        // 3. Оценить выполнимость (с учетом навыков специалиста)
        const feasibility = this.assessFeasibility(job, category, specialist);
        // 4. Собрать предупреждения и заметки
        const warnings = this.generateWarnings(job, feasibility);
        const operatorNotes = this.generateOperatorNotes(job, feasibility);
        // 5. Если задача не выполнима — не тратим ресурсы на специалиста
        if (!feasibility.feasible) {
            const isDynamic = taskNature === 'dynamic';
            const proposal = isDynamic
                ? `⛔ ДИНАМИЧЕСКАЯ ЗАДАЧА (НЕ НАШ ПРОФИЛЬ)\n\nОписание: Это операционная деятельность (размещение/общение), а не создание продукта.\nПричины:\n${feasibility.reasons.map(r => `• ${r}`).join('\n')}`
                : `⛔ ЗАДАЧА НЕ РЕКОМЕНДОВАНА К ВЫПОЛНЕНИЮ\n\nПричины:\n${feasibility.reasons.map(r => `• ${r}`).join('\n')}`;
            this.saveAnalysisPattern(job, feasibility);
            return { proposal, feasibility, warnings, operatorNotes, taskNature };
        }
        // 6. Шерлок задействует ГЛУБОКУЮ ДЕДУКЦИЮ (Deep Deduction)
        const deduction = await this.performDeepDeduction(job, category, specialist);
        // 7. Генерация экспертного предложения от специалиста
        const userName = this.profile.user?.name || 'Ваш исполнитель';
        const expertProposal = await specialist.generateProposal(job, userName, deduction);
        // 8. Обогащаем предупреждения
        if (routing.supportAgents.length > 0) {
            warnings.push(`🔀 Комплексная задача: ${routing.primaryAgent} + ${routing.supportAgents.join(', ')}`);
        }
        warnings.push(`🤖 Агент: ${specialist.emoji} ${specialist.agentName}`);
        if (deduction.winProbability > 70) {
            warnings.push(`🔥 ВЫСОКИЙ ШАНС (%): ${deduction.winProbability}% - откликаться приоритетно!`);
        }
        // 9. Формируем подробные заметки для оператора (Intelligence Report)
        const intelligenceReport = [
            `🕵️ ИНТЕЛЛЕКТ-ОТЧЕТ ШЕРЛОКА ДЛЯ "${job.title.toUpperCase()}"`,
            '',
            '🔍 ТЕХНИЧЕСКОЕ ИССЛЕДОВАНИЕ (Best Practices):',
            deduction.techResearch,
            '',
            '📉 АНАЛИЗ РЫНКА/КОНКУРЕНТОВ:',
            deduction.competitorAnalysis,
            '',
            '⚠️ ПОДВОДНЫЕ КАМНИ (API/Ограничения):',
            deduction.apiPitfalls,
            '',
            '🚀 ИДЕИ ДЛЯ ДОПРОДАЖ (UPSELL):',
            deduction.upsellIdeas.map(i => ` • ${i}`).join('\n'),
            '',
            '🌐 ТЕХНИЧЕСКАЯ РАЗВЕДКА САЙТА (Evidence):',
            deduction.siteTechStack || 'Сайт не обнаружен в ТЗ',
            '',
            '📊 ШАНС НА ПОБЕДУ:',
            `${deduction.winProbability}% (оценка на базе числа откликов и соответствия навыкам)`,
            '',
            '━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
            '🤖 МАРШРУТИЗАЦИЯ:',
            ` Рационализация: ${routing.rationale}`,
            ` Прототип: ${expertProposal.prototype ? `${expertProposal.prototype.type} (${expertProposal.prototype.completionPercent}%)` : 'нет'}`,
            ` Сроки: ~${expertProposal.totalHours} ч / ${expertProposal.totalDays} дн.`,
            '',
            operatorNotes
        ].join('\n');
        // 10. Самообучение
        this.saveAnalysisPattern(job, feasibility);
        return {
            proposal: expertProposal.fullText,
            expertProposal,
            feasibility,
            warnings,
            operatorNotes: intelligenceReport,
            routing,
            agentUsed: specialist.agentName,
            score: deduction.winProbability,
            deepDeduction: deduction,
            taskNature,
            executionPlan: await this.generateExecutionPlan(job, category, specialist, deduction, feasibility)
        };
    }
    /**
     * Генерация детального плана исполнения (Execution Plan)
     * по методологии "Суперагента" (Best Practices 2026).
     */
    async generateExecutionPlan(job, category, specialist, deduction, feasibility) {
        console.log(`🗺️ [Sherlock] Составление плана исполнения для "${job.title}"...`);
        const prompt = `
      Ты — Элитный AI-Архитектор (Chief Innovation Officer). Твоя задача — составить БЕЗАЛЬТЕРНАТИВНЫЙ инновационный план реализации проекта.
      
      КОНТЕКСТ ПРОЕКТА:
      Название: ${job.title}
      Описание: ${job.description}
      Трудоемкость: ~${feasibility.effortHours} часов
      Ведущий агент: ${specialist.agentName}
      Технологическое исследование: ${deduction.techResearch}
      
      ГЛАВНОЕ ПРАВИЛО (ИННОВАЦИОННЫЙ МАНИФЕСТ):
      Если проект масштабный (300+ страниц, SEO, региональное масштабирование) — категорически ЗАПРЕЩЕНО предлагать WordPress или простые шаблоны. 
      Вместо этого внедряй в план:
      1. Стек Next.js (SSG/ISR) + Headless CMS (Contentful/Strapi) — для скорости 100/100.
      2. Edge Computing & Serverless (Vercel/Netlify) — для мгновенного отклика.
      3. AI-driven Content Pipeline — для автоматизации 500+ страниц одним кликом.
      
      СТРУКТУРА ПЛАНА (ROADMAP):
      Каждый шаг дорожной карты должен звучать как технологическое преимущество, а не как рутинное действие. 
      Пример плохого шага: "Создание дизайна". 
      Пример хорошего шага: "Проектирование высококонверсионной дизайн-системы с элементами глассморфизма и нейро-оптимизацией".
      
      ОТВЕТЬ СТРОГО В ФОРМАТЕ JSON:
      {
        "goal": "Бизнес-цель: захват рынка через технологическое превосходство",
        "roles": [{"agentName": "...", "role": "Старший Архитектор", "tasks": ["..."]}],
        "roadmap": [
          {
            "week": 1, 
            "title": "Технологический фундамент & Headless Architecture", 
            "deliverable": "Развернутая Edge-инфраструктура и схема данных", 
            "responsible": "Архитектор Артемий",
            "minutes": 480
          }
        ],
        "rationale": "Выбранный стек Next.js вместо WP обеспечивает 10-кратное преимущество в скорости индексации и масштабирования.",
        "risks": ["..."],
        "expectedResult": "Сверхбыстрая SEO-платформа, готовая к захвату 500+ регионов.",
        "estimatedTotalHours": ${feasibility.effortHours},
        "estimatedCost": ${feasibility.rewardAnalysis.budgetAmount || feasibility.effortHours * 1500}
      }
    `;
        try {
            const response = await (0, ai_1.generateWithGemini)(prompt, "Ты — системный архитектор высшего уровня. Твоя задача — планирование проектов.");
            // Парсим JSON из ответа Gemini
            const jsonMatch = response.match(/\{[\s\S]*\}/);
            if (jsonMatch) {
                return JSON.parse(jsonMatch[0]);
            }
            throw new Error("Не удалось спарсить план исполнения");
        }
        catch (e) {
            console.error("Ошибка при генерации плана исполнения:", e);
            // fallback
            return {
                goal: "Реализация проекта согласно ТЗ",
                roles: [{ agentName: specialist.agentName, role: "Ведущий исполнитель", tasks: ["Разработка всего функционала"] }],
                roadmap: [{ week: 1, title: "Разработка MVP", deliverable: "Рабочий продукт", responsible: specialist.agentName }],
                rationale: "Прямая реализация функционала по ТЗ",
                risks: ["Недостаточно данных для детального планирования"],
                expectedResult: "Готовое решение",
                estimatedTotalHours: feasibility.effortHours,
                estimatedCost: feasibility.rewardAnalysis.budgetAmount || 0
            };
        }
    }
    // =========================================================
    // КАТЕГОРИЗАЦИЯ ЗАДАЧИ
    // =========================================================
    detectCategory(job) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        // 1. Приоритетные профессиональные категории
        // Мобильные приложения
        if (this.matchesAny(text, ['flutter', 'react native', 'swift', 'kotlin', 'мобильное приложение', 'ios app', 'android app', 'мобильн'])) {
            return 'mobile_app';
        }
        // Дизайн и Креатив (Рембрандт)
        if (this.matchesAny(text, ['дизайн', 'логотип', 'figma', 'макет', 'ui/ux', 'график', 'баннер', 'иллюстрация', 'оформление', 'креатив'])) {
            return 'design_ui';
        }
        if (this.matchesAny(text, ['директ', 'direct', 'ads', 'реклама', 'таргет', 'маркетинг', 'контекст', 'яндекс.директ', 'vk ads'])) {
            return 'marketing_ads';
        }
        // Чертежи и инженерия
        if (this.matchesAny(text, ['чертеж', 'чпу', 'стол', 'мебель', 'фанера', 'паз-шип', 'схема изделия', 'конструкторск'])) {
            return 'engineering_drafting';
        }
        // 2. Операционные/Динамические задачи (Ручной труд) - после профильных категорий
        if (this.matchesAny(text, [
            'разместить на сайт', 'размещение контента', 'выкладывать товар', 'наполнять сайт',
            'отвечать в мессенджерах', 'общение с клиентами', 'оператор чата', 'менеджер чата',
            'регистрация на сайтах', 'регистрироваться', 'ходить по сайтам', 'пройти опрос',
            'модерация', 'обзвон', 'холодные звонки', 'заполнение карточек',
            'инфографика', 'wildberries', 'ozon', 'маркетплейс', 'карточки товаров', 'вб', 'озон'
        ])) {
            return 'operational_manual';
        }
        // Десктопные
        if (this.matchesAny(text, ['electron', 'desktop app', 'десктопное', 'qt', 'wxwidgets', '.exe'])) {
            return 'desktop_app';
        }
        // Data Science
        if (this.matchesAny(text, ['machine learning', 'ml', 'нейросет', 'neural', 'tensorflow', 'pytorch', 'pandas', 'data science', 'модель обучения'])) {
            return 'data_science';
        }
        // DevOps
        if (this.matchesAny(text, ['ci/cd', 'devops', 'kubernetes', 'k8s', 'terraform', 'ansible', 'pipeline', 'деплой', 'инфраструктур'])) {
            return 'devops';
        }
        // Лекции / образование
        if (this.matchesAny(text, ['лекц', 'урок', 'презентац', 'обучени', 'курс', 'вебинар', 'учебн', 'менторинг', 'менторств'])) {
            return 'lecture_education';
        }
        // Telegram бот
        if (this.matchesAny(text, ['telegram', 'tg bot', 'телеграм']) && this.matchesAny(text, ['бот', 'bot'])) {
            return 'telegram_bot';
        }
        // Chrome extension
        if (this.matchesAny(text, ['chrome extension', 'расширение chrome', 'расширение для браузера', 'browser extension', 'manifest'])) {
            return 'chrome_extension';
        }
        // Парсинг
        if (this.matchesAny(text, ['парсинг', 'парсер', 'scraping', 'scraper', 'краулер', 'crawler', 'автоматический сбор данных'])) {
            return 'parsing_scraping';
        }
        // Дизайн
        if (this.matchesAny(text, ['дизайн', 'логотип', 'figma', 'макет', 'ui/ux', 'график', 'баннер', 'иллюстрация'])) {
            return 'design_ui';
        }
        // Тексты
        if (this.matchesAny(text, ['текст', 'стать', 'копирайт', 'контент', 'пост', 'seo текст', 'рерайт'])) {
            return 'text_content';
        }
        // Backend
        if (this.matchesAny(text, ['backend', 'бекенд', 'api', 'fastapi', 'django', 'flask', 'express', 'nestjs', 'rest api', 'graphql', 'серверн'])) {
            if (this.matchesAny(text, ['frontend', 'react', 'vue', 'angular', 'фронтенд', 'лендинг'])) {
                return 'web_fullstack';
            }
            return 'web_backend';
        }
        // Frontend
        if (this.matchesAny(text, ['react', 'vue', 'angular', 'next.js', 'nuxt', 'frontend', 'фронтенд', 'лендинг', 'верстк'])) {
            return 'web_frontend';
        }
        // Разработка вообще
        if (this.matchesAny(text, ['разработ', 'программ', 'сайт', 'приложен', 'код', 'скрипт'])) {
            return 'web_fullstack';
        }
        return 'other';
    }
    // =========================================================
    // ОЦЕНКА ВЫПОЛНИМОСТИ
    // =========================================================
    assessFeasibility(job, category, specialist) {
        const blockers = [];
        const missingServices = [];
        const reasons = [];
        const text = `${job.title} ${job.description}`.toLowerCase();
        // ---- 0. Проверка на "динамическую" / операционную задачу (КОНСТИТУЦИЯ) ----
        if (category === 'operational_manual') {
            reasons.push('Это операционная задача (динамическая), запрещенная Конституцией Проекта.');
            return {
                feasible: false,
                confidence: 0.99,
                reasons,
                blockers: [{
                        type: 'too_complex',
                        description: 'Операционная деятельность (ручной труд/модерация)',
                        severity: 'critical'
                    }],
                missingServices: [],
                effortHours: 0,
                rewardAnalysis: { budgetAmount: 0, budgetCurrency: 'RUB', hourlyRate: 0, worthIt: false, comment: 'Запрещено Конституцией (Rule 3)' },
                category
            };
        }
        // ---- 1. Проверка навыков ----
        const skillCoverage = this.checkSkillCoverage(job, category, specialist);
        if (skillCoverage < 0.1) {
            blockers.push({
                type: 'skill_gap',
                description: `Покрытие навыков: ${(skillCoverage * 100).toFixed(0)}% — слишком низкое`,
                severity: 'critical'
            });
            reasons.push(`Навыки не соответствуют задаче (${(skillCoverage * 100).toFixed(0)}%)`);
        }
        // ---- 2. Проверка доступных MCP-сервисов ----
        const serviceAnalysis = this.checkRequiredServices(category, text);
        missingServices.push(...serviceAnalysis.missing);
        if (serviceAnalysis.criticalMissing) {
            reasons.push(`Отсутствуют критически важные сервисы: ${serviceAnalysis.missing.filter(m => m.priority === 'required').map(m => m.serviceName).join(', ')}`);
        }
        // ---- 3. Проверка специфических блокеров ----
        // Нужен доступ к конкретным сайтам/сервисам
        if (this.matchesAny(text, ['доступ к', 'логин', 'пароль', 'учётн', 'аккаунт', 'авториз'])) {
            if (this.matchesAny(text, ['ваш аккаунт', 'ваш логин', 'ваш сайт', 'ваш сервер', 'доступы'])) {
                blockers.push({
                    type: 'credentials_required',
                    description: 'Задача требует доступа к аккаунту/серверу заказчика — нужно получить credentials',
                    severity: 'major'
                });
            }
        }
        // Нужен конкретный сайт/платформа
        if (this.matchesAny(text, ['1с', '1c', 'bitrix', 'битрикс', 'wordpress', 'shopify', 'wix', 'tilda', 'тильда'])) {
            const platform = this.extractSpecificPlatform(text);
            if (platform && !this.hasServiceFor(platform)) {
                missingServices.push({
                    serviceName: `${platform} Integration`,
                    serviceType: 'api',
                    purpose: `Работа с платформой ${platform}`,
                    howToConnect: `Подключить API или плагин для ${platform}`,
                    priority: 'required'
                });
            }
        }
        // Слишком размытое ТЗ
        if (job.description.length < 50 || this.isVagueDescription(text)) {
            blockers.push({
                type: 'unclear_requirements',
                description: 'Описание задачи слишком размытое для точной оценки',
                severity: 'major'
            });
            reasons.push('Недостаточно информации в ТЗ для точной оценки');
        }
        // Юридические риски (КОНСТИТУЦИЯ)
        if (this.matchesAny(text, [...constitution_1.CONSTITUTION.FILTERING.LEGAL, 'казино', 'ставки', 'adult', '18+', 'обход блокировк', 'взлом', 'кардинг', 'спам рассылк', 'накрутк'])) {
            blockers.push({
                type: 'legal',
                description: 'Задача содержит признаки нелегальной деятельности (Rule 3.2)',
                severity: 'critical'
            });
            reasons.push('Задача заблокирована фильтром безопасности (Legal)');
        }
        // ---- 4. Оценка трудоёмкости ----
        const effortHours = this.estimateEffort(category, text);
        // ---- 5. Анализ вознаграждения ----
        const rewardAnalysis = this.analyzeReward(job, effortHours);
        // ---- 6. Итоговое решение ----
        const hasCriticalBlockers = blockers.some(b => b.severity === 'critical');
        const hasMajorBlockers = blockers.filter(b => b.severity === 'major').length >= 2;
        // Гибкая логика бюджета: если навыки подходят на >80%, мы не бракуем задачу за бюджет,
        // а помечаем её как "под обсуждение цены".
        const isPerfectMatch = skillCoverage >= 0.8;
        const feasibleByReward = rewardAnalysis.worthIt || isPerfectMatch;
        const feasible = !hasCriticalBlockers && !hasMajorBlockers && feasibleByReward;
        if (feasible && reasons.length === 0) {
            if (isPerfectMatch && !rewardAnalysis.worthIt) {
                reasons.push('🔥 ИДЕАЛЬНЫЙ МАТЧ: Твои навыки подходят на 80%+. Бюджет на сайте маленький, но задача стоит того, чтобы предложить свою цену.');
            }
            else {
                reasons.push('Задача выполнима с текущими инструментами и навыками');
            }
        }
        if (!rewardAnalysis.worthIt && !hasCriticalBlockers) {
            reasons.push(rewardAnalysis.comment);
        }
        return {
            feasible,
            confidence: this.calculateConfidence(job, blockers, skillCoverage),
            reasons,
            blockers,
            missingServices,
            effortHours,
            rewardAnalysis,
            category
        };
    }
    // =========================================================
    // ПРОВЕРКА MCP-СЕРВИСОВ
    // =========================================================
    checkRequiredServices(category, text) {
        const missing = [];
        // Категории, требующие специфических сервисов
        const serviceRequirements = {
            'stitch': {
                categories: ['web_frontend', 'web_fullstack', 'design_ui'],
                priority: 'recommended'
            },
            'gemini': {
                categories: ['lecture_education', 'text_content', 'web_fullstack', 'web_backend', 'web_frontend'],
                priority: 'recommended'
            },
            'browserUse': {
                categories: ['parsing_scraping'],
                priority: 'required'
            }
        };
        for (const [serviceKey, req] of Object.entries(serviceRequirements)) {
            if (req.categories.includes(category)) {
                const service = this.services[serviceKey];
                if (!service || !service.enabled) {
                    missing.push({
                        serviceName: serviceKey,
                        serviceType: 'mcp',
                        purpose: service?.purpose || `Необходим для задач типа ${category}`,
                        howToConnect: `Подключить ${serviceKey} через MCP в настройках Antigravity`,
                        priority: req.priority
                    });
                }
            }
        }
        // Специфические сервисы по ключевым словам
        if (this.matchesAny(text, ['firebase', 'firestore'])) {
            if (!this.services['firebase']?.enabled) {
                missing.push({
                    serviceName: 'Firebase',
                    serviceType: 'mcp',
                    purpose: 'Работа с Firebase/Firestore',
                    howToConnect: 'Подключить Firebase MCP server или использовать Firebase CLI',
                    priority: 'recommended'
                });
            }
        }
        if (this.matchesAny(text, ['stripe', 'платёж', 'оплат'])) {
            missing.push({
                serviceName: 'Stripe / Payment API',
                serviceType: 'api',
                purpose: 'Интеграция платёжной системы',
                howToConnect: 'Получить API ключ Stripe и подключить SDK',
                priority: 'recommended'
            });
        }
        const criticalMissing = missing.some(m => m.priority === 'required');
        return { missing, criticalMissing };
    }
    // =========================================================
    // ОЦЕНКА ТРУДОЁМКОСТИ
    // =========================================================
    estimateEffort(category, text) {
        // Базовая трудоёмкость по категории (часы)
        const baseEffort = {
            'web_fullstack': 40,
            'web_frontend': 20,
            'web_backend': 25,
            'telegram_bot': 15,
            'chrome_extension': 15,
            'parsing_scraping': 12,
            'mobile_app': 60,
            'desktop_app': 50,
            'devops': 15,
            'data_science': 30,
            'design_ui': 12,
            'lecture_education': 8,
            'text_content': 6,
            'engineering_drafting': 25,
            'marketing_ads': 15,
            'operational_manual': 8,
            'other': 15
        };
        let effort = baseEffort[category] || 15;
        // Модификаторы
        if (this.matchesAny(text, ['авториз', 'jwt', 'oauth', 'регистрац']))
            effort += 5;
        if (this.matchesAny(text, ['админ панел', 'admin', 'cms']))
            effort += 10;
        if (this.matchesAny(text, ['интеграци', 'api', 'webhook']))
            effort += 5;
        if (this.matchesAny(text, ['тестирован', 'unit test', 'e2e']))
            effort += 5;
        if (this.matchesAny(text, ['деплой', 'deploy', 'docker', 'ci/cd']))
            effort += 3;
        if (this.matchesAny(text, ['адаптив', 'responsive', 'мобильн']))
            effort += 5;
        if (this.matchesAny(text, ['seo', 'оптимизаци']))
            effort += 3;
        if (this.matchesAny(text, ['простой', 'простая', 'несложн', 'небольш']))
            effort *= 0.6;
        if (this.matchesAny(text, ['сложн', 'комплексн', 'масштабн', 'enterprise']))
            effort *= 1.5;
        return Math.round(effort);
    }
    // =========================================================
    // АНАЛИЗ ВОЗНАГРАЖДЕНИЯ
    // =========================================================
    analyzeReward(job, effortHours) {
        let budgetAmount = null;
        let budgetCurrency = 'RUB';
        if (job.budget) {
            budgetAmount = job.budget.amount || job.budget.min || null;
            budgetCurrency = job.budget.currency || 'RUB';
        }
        if (!budgetAmount) {
            return { budgetAmount: null, budgetCurrency, hourlyRate: null, worthIt: true, comment: 'Бюджет открыт' };
        }
        let amountRub = budgetAmount;
        if (budgetCurrency === 'USD')
            amountRub = budgetAmount * 95;
        if (budgetCurrency === 'EUR')
            amountRub = budgetAmount * 103;
        const hourlyRate = Math.round(amountRub / effortHours);
        const MIN_RATE = constitution_1.CONSTITUTION.PRICING.HOURLY_RATE;
        // Мы всегда считаем задачу worthIt, так как предложим свою цену по Конституции.
        const worthIt = true;
        let comment;
        if (hourlyRate >= MIN_RATE * 1.5) {
            comment = `💰 ПРЕМИУМ: ~${hourlyRate} ₽/час (Выше нормы)`;
        }
        else if (hourlyRate >= MIN_RATE) {
            comment = `✅ ВЫГОДНО: ~${hourlyRate} ₽/час (Норма)`;
        }
        else {
            comment = `🆗 НИЗКИЙ БЮДЖЕТ: ~${hourlyRate} ₽/час (Предложим по прайсу ${MIN_RATE})`;
        }
        return { budgetAmount, budgetCurrency, hourlyRate, worthIt, comment };
    }
    // =========================================================
    // ГЕНЕРАЦИЯ ПРЕДЛОЖЕНИЯ
    // =========================================================
    generateProposal(job, feasibility) {
        const { category, effortHours, rewardAnalysis, missingServices } = feasibility;
        const techStack = this.determineTechStack(category, job);
        const plan = this.createImplementationPlan(category, job, techStack);
        const questions = this.generateClarifyingQuestions(category, job);
        const totalDays = (effortHours / 8).toFixed(1);
        const roundedPrice = Math.ceil((effortHours * 1500) / 100) * 100;
        let proposal = `Здравствуйте!

У меня есть опыт решения аналогичных задач. Предлагаю следующий план реализации:

${plan.map(step => `• ${step.title}: ${step.description}`).join('\n')}

${techStack.length > 0 ? `Для реализации использую надежный стек: ${techStack.join(', ')}.` : ''}

Срок выполнения ${totalDays} дня за ${roundedPrice} рублей.

Цена аргументирована сложностью реализации и необходимостью тщательного тестирования всех сценариев.

${questions.length > 0 ? `
У меня есть пара уточняющих вопросов:
${questions.slice(0, 3).map((q, i) => `${i + 1}. ${q}`).join('\n')}` : ''}

С уважением, 
${this.profile.user.name || 'Ваш исполнитель'}`;
        return proposal;
    }
    // =========================================================
    // ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    // =========================================================
    createUnderstanding(job) {
        const desc = job.description || '';
        // Берём первые 2 предложения
        const sentences = desc.split(/[.!?]/).filter(s => s.trim().length > 10).slice(0, 2);
        if (sentences.length > 0) {
            return `Понял задачу: ${sentences.join('. ').trim()}.`;
        }
        return `Понял задачу: ${job.title}.`;
    }
    determineTechStack(category, job) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        const stack = [];
        // Извлечь упомянутые технологии из ТЗ
        const knownTech = {
            'react': 'React 18+', 'next.js': 'Next.js 14', 'nextjs': 'Next.js 14',
            'vue': 'Vue 3', 'nuxt': 'Nuxt 3', 'angular': 'Angular 17+',
            'typescript': 'TypeScript', 'javascript': 'JavaScript (ES2024)',
            'node.js': 'Node.js 20+', 'nodejs': 'Node.js 20+', 'express': 'Express.js',
            'nestjs': 'NestJS', 'nest.js': 'NestJS',
            'python': 'Python 3.12+', 'fastapi': 'FastAPI', 'django': 'Django 5',
            'flask': 'Flask', 'postgresql': 'PostgreSQL', 'postgres': 'PostgreSQL',
            'mysql': 'MySQL', 'mongodb': 'MongoDB', 'redis': 'Redis',
            'docker': 'Docker + Docker Compose', 'kubernetes': 'Kubernetes',
            'aiogram': 'aiogram 3.x', 'telegraf': 'Telegraf.js',
            'playwright': 'Playwright', 'puppeteer': 'Puppeteer',
            'tailwind': 'Tailwind CSS', 'bootstrap': 'Bootstrap 5',
            'figma': 'Figma', 'graphql': 'GraphQL', 'prisma': 'Prisma ORM',
            'supabase': 'Supabase', 'firebase': 'Firebase',
        };
        for (const [keyword, techName] of Object.entries(knownTech)) {
            if (text.includes(keyword)) {
                if (!stack.includes(techName)) {
                    stack.push(techName);
                }
            }
        }
        // Если ничего не нашли — добавить стандартный стек по категории
        if (stack.length === 0) {
            const defaultStacks = {
                'web_fullstack': ['TypeScript', 'React 18+ / Next.js 14', 'Node.js 20+', 'PostgreSQL'],
                'web_frontend': ['TypeScript', 'React 18+', 'Tailwind CSS'],
                'web_backend': ['Python 3.12+', 'FastAPI', 'PostgreSQL'],
                'telegram_bot': ['Python 3.12+', 'aiogram 3.x', 'SQLite / PostgreSQL'],
                'chrome_extension': ['TypeScript', 'Chrome Extension API (Manifest V3)'],
                'parsing_scraping': ['Python 3.12+', 'Playwright / BeautifulSoup4'],
                'mobile_app': ['React Native / Flutter', 'TypeScript'],
                'desktop_app': ['Electron', 'TypeScript', 'React'],
                'devops': ['Docker', 'GitHub Actions / GitLab CI', 'Terraform'],
                'data_science': ['Python 3.12+', 'pandas', 'scikit-learn'],
                'design_ui': ['Figma', 'Adobe Color'],
                'lecture_education': ['Структурированная подача', 'Практические примеры кода'],
                'text_content': ['Грамотный русский язык', 'SEO-оптимизация'],
                'engineering_drafting': ['AutoCAD', 'Fusion 360', 'Компас-3D'],
                'marketing_ads': ['Yandex Direct', 'VK Ads', 'Google Ads'],
                'operational_manual': ['Manual Action', 'Operational Process'],
                'other': ['TypeScript', 'Node.js']
            };
            stack.push(...(defaultStacks[category] || ['TypeScript']));
        }
        return stack;
    }
    createImplementationPlan(category, job, techStack) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        const steps = [];
        // Общий шаг 1: Анализ
        steps.push({
            title: 'Анализ ТЗ и проектирование',
            description: 'Детальное изучение требований, уточнение деталей, проектирование архитектуры.',
            deliverable: 'Техническое описание и схема архитектуры',
            estimatedHours: '2-4 часа'
        });
        // Специфичные шаги по категории
        if (category === 'web_backend' || category === 'web_fullstack') {
            steps.push({
                title: 'Настройка проекта и БД',
                description: `Настройка ${techStack.slice(0, 2).join(', ')}, структура проекта, модели данных.`,
                deliverable: 'Рабочий шаблон с моделями',
                estimatedHours: '3-5 часов'
            });
            steps.push({
                title: 'Реализация бизнес-логики',
                description: 'API endpoints, валидация, обработка ошибок.',
                deliverable: 'Рабочее API',
                estimatedHours: '8-15 часов'
            });
        }
        if (category === 'web_frontend' || category === 'web_fullstack') {
            steps.push({
                title: 'Разработка интерфейса',
                description: 'Компоненты, страницы, роутинг, адаптивная вёрстка.',
                deliverable: 'Рабочий UI',
                estimatedHours: '6-12 часов'
            });
        }
        if (category === 'telegram_bot') {
            steps.push({
                title: 'Структура бота и хендлеры',
                description: 'Команды, сценарии диалогов, inline-кнопки, FSM.',
                deliverable: 'Рабочий бот с базовым функционалом',
                estimatedHours: '6-10 часов'
            });
        }
        if (category === 'parsing_scraping') {
            steps.push({
                title: 'Разработка парсера',
                description: 'Анализ структуры сайта, написание скрипта, обход защиты.',
                deliverable: 'Рабочий скрипт парсинга',
                estimatedHours: '6-12 часов'
            });
            steps.push({
                title: 'Обработка и экспорт данных',
                description: 'Очистка данных, экспорт в нужный формат.',
                deliverable: 'Данные в CSV/JSON/Excel',
                estimatedHours: '2-4 часа'
            });
        }
        if (category === 'lecture_education') {
            steps.push({
                title: 'Подготовка материала',
                description: 'Теория, практические примеры, визуальные материалы.',
                deliverable: 'Конспект + код',
                estimatedHours: '4-8 часов'
            });
        }
        // Общие завершающие шаги
        if (!['lecture_education', 'text_content', 'design_ui'].includes(category)) {
            steps.push({
                title: 'Тестирование',
                description: 'Проверка всех сценариев, исправление багов.',
                deliverable: 'Стабильная версия',
                estimatedHours: '2-4 часа'
            });
        }
        steps.push({
            title: 'Документация и сдача',
            description: 'README, инструкция по запуску, передача материалов.',
            deliverable: 'Готовый проект с документацией',
            estimatedHours: '1-3 часа'
        });
        return steps;
    }
    generateClarifyingQuestions(category, job) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        const questions = [];
        // Универсальные вопросы
        if (!this.matchesAny(text, ['срок', 'дедлайн', 'к числу'])) {
            questions.push('Есть ли дедлайн по проекту?');
        }
        // Специфичные вопросы
        if (['web_fullstack', 'web_frontend', 'web_backend'].includes(category)) {
            if (!this.matchesAny(text, ['figma', 'макет', 'дизайн'])) {
                questions.push('Есть ли готовый дизайн/макет интерфейса?');
            }
            if (!this.matchesAny(text, ['деплой', 'хостинг', 'сервер'])) {
                questions.push('Нужна ли помощь с развёртыванием на сервере?');
            }
        }
        if (category === 'telegram_bot') {
            questions.push('Есть ли уже созданный бот через @BotFather?');
        }
        if (category === 'parsing_scraping') {
            questions.push('Какой объём данных нужно собрать (примерное количество)?');
            questions.push('Как часто нужно обновлять данные?');
        }
        questions.push('Остались ли требования, не отражённые в описании?');
        return questions.slice(0, 4);
    }
    // =========================================================
    // ПРЕДУПРЕЖДЕНИЯ И ЗАМЕТКИ ДЛЯ ОПЕРАТОРА
    // =========================================================
    generateWarnings(job, feasibility) {
        const warnings = [];
        if (!feasibility.feasible) {
            warnings.push(`⛔ ЗАДАЧА НЕ РЕКОМЕНДОВАНА: ${feasibility.reasons.join('; ')}`);
        }
        for (const blocker of feasibility.blockers) {
            warnings.push(`${blocker.severity === 'critical' ? '🔴' : '🟡'} ${blocker.description}`);
        }
        for (const missing of feasibility.missingServices) {
            warnings.push(`🔧 Нужен сервис: ${missing.serviceName} (${missing.purpose}) — ${missing.howToConnect}`);
        }
        if (feasibility.rewardAnalysis.hourlyRate !== null && feasibility.rewardAnalysis.hourlyRate < 500) {
            warnings.push(`💰 Низкая ставка: ~${feasibility.rewardAnalysis.hourlyRate} ₽/час`);
        }
        return warnings;
    }
    generateOperatorNotes(job, feasibility) {
        const lines = [];
        lines.push(`📋 Категория: ${feasibility.category}`);
        lines.push(`⏱ Трудоёмкость: ~${feasibility.effortHours} часов (~${(feasibility.effortHours / 8).toFixed(1)} дней)`);
        lines.push(`🎯 Уверенность: ${(feasibility.confidence * 100).toFixed(0)}%`);
        lines.push(`💰 ${feasibility.rewardAnalysis.comment}`);
        if (feasibility.missingServices.length > 0) {
            lines.push('');
            lines.push('🔧 НЕОБХОДИМЫЕ СЕРВИСЫ:');
            for (const ms of feasibility.missingServices) {
                lines.push(`  [${ms.priority}] ${ms.serviceName}: ${ms.howToConnect}`);
            }
        }
        if (feasibility.blockers.length > 0) {
            lines.push('');
            lines.push('⚠️ БЛОКЕРЫ:');
            lines.push('techResearch: (строка) Какие библиотеки, фреймворки и архитектурные паттерны являются эталоном (best practices) для ее решения в 2026-2027 годах?');
            lines.push('apiPitfalls: (строка) Какие есть критические ограничения, лимиты API или "подводные камни" у этого стека?');
            for (const b of feasibility.blockers) {
                lines.push(`  [${b.severity}] ${b.description}`);
            }
        }
        return lines.join('\n');
    }
    // =========================================================
    // САМООБУЧЕНИЕ
    // =========================================================
    saveAnalysisPattern(job, feasibility) {
        const pattern = {
            date: new Date().toISOString(),
            category: feasibility.category,
            feasible: feasibility.feasible,
            effortHours: feasibility.effortHours,
            budgetAmount: feasibility.rewardAnalysis.budgetAmount,
            hourlyRate: feasibility.rewardAnalysis.hourlyRate,
            skillsUsed: job.skills || [],
            titleKeywords: job.title.toLowerCase().split(' ').filter(w => w.length > 3),
        };
        this.learnedPatterns.push(pattern);
        // Сохранить в проект
        this.saveLearnedPatterns(this.learnedPatterns);
        // Если накопилось достаточно паттернов — создать/обновить workflow
        if (this.learnedPatterns.length % 10 === 0) {
            this.generateSkillFile();
        }
    }
    generateSkillFile() {
        const skillsDir = path.join(this.projectRoot, '.agent', 'skills');
        fs.mkdirSync(skillsDir, { recursive: true });
        // Анализ паттернов: какие категории чаще всего успешны
        const categoryStats = {};
        for (const p of this.learnedPatterns) {
            if (!categoryStats[p.category]) {
                categoryStats[p.category] = { total: 0, feasible: 0, avgRate: 0 };
            }
            categoryStats[p.category].total++;
            if (p.feasible)
                categoryStats[p.category].feasible++;
            if (p.hourlyRate)
                categoryStats[p.category].avgRate += p.hourlyRate;
        }
        const skillContent = `---
name: task-analysis-patterns
description: Паттерны анализа задач, выведенные из ${this.learnedPatterns.length} проанализированных заданий
---

# Паттерны анализа задач

Обновлено: ${new Date().toISOString()}
Всего проанализировано: ${this.learnedPatterns.length} задач

## Статистика по категориям

${Object.entries(categoryStats).map(([cat, stats]) => {
            const feasibleRate = ((stats.feasible / stats.total) * 100).toFixed(0);
            const avgRate = stats.avgRate > 0 ? (stats.avgRate / stats.feasible).toFixed(0) : 'н/д';
            return `- **${cat}**: ${stats.total} задач, ${feasibleRate}% выполнимых, средняя ставка: ${avgRate} ₽/час`;
        }).join('\n')}

## Рекомендации

${Object.entries(categoryStats)
            .filter(([_, stats]) => stats.feasible / stats.total < 0.5)
            .map(([cat]) => `- ⚠️ Категория "${cat}" имеет низкий процент выполнимости — рассмотреть повышение навыков`)
            .join('\n') || '- Все категории показывают хорошую выполнимость'}
`;
        fs.writeFileSync(path.join(skillsDir, 'task-analysis-patterns.md'), skillContent);
    }
    // =========================================================
    // ЗАГРУЗКА / СОХРАНЕНИЕ
    // =========================================================
    loadAvailableServices() {
        const skillsPath = path.join(this.projectRoot, 'config', 'agent-skills.json');
        try {
            if (fs.existsSync(skillsPath)) {
                const data = JSON.parse(fs.readFileSync(skillsPath, 'utf-8'));
                const services = {};
                if (data.antigravity?.services) {
                    for (const [key, svc] of Object.entries(data.antigravity.services)) {
                        services[key] = {
                            name: svc.name || key,
                            purpose: svc.purpose || '',
                            enabled: svc.enabled || false,
                            capabilities: svc.capabilities || []
                        };
                    }
                }
                return services;
            }
        }
        catch (e) {
            console.error('Ошибка загрузки сервисов:', e);
        }
        return {};
    }
    loadLearnedPatterns() {
        const patternsPath = path.join(this.projectRoot, 'data', 'learning', 'analysis-patterns.json');
        try {
            if (fs.existsSync(patternsPath)) {
                return JSON.parse(fs.readFileSync(patternsPath, 'utf-8'));
            }
        }
        catch (e) {
            // Файл не существует или повреждён
        }
        return [];
    }
    saveLearnedPatterns(patterns) {
        const dir = path.join(this.projectRoot, 'data', 'learning');
        fs.mkdirSync(dir, { recursive: true });
        fs.writeFileSync(path.join(dir, 'analysis-patterns.json'), JSON.stringify(patterns, null, 2));
    }
    // =========================================================
    // УТИЛИТЫ
    // =========================================================
    matchesAny(text, keywords) {
        return keywords.some(kw => text.includes(kw));
    }
    checkSkillCoverage(job, category, specialist) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        const userSkills = Object.keys(this.profile.skills).map(s => s.toLowerCase());
        const synonyms = this.profile.skillSynonyms || {};
        // Расширить список навыков синонимами
        const allUserSkills = new Set(userSkills);
        for (const [canonical, syns] of Object.entries(synonyms)) {
            allUserSkills.add(canonical.toLowerCase());
            for (const syn of syns) {
                allUserSkills.add(syn.toLowerCase());
            }
        }
        // Подсчитать совпадения
        let matches = 0;
        for (const skill of allUserSkills) {
            if (text.includes(skill))
                matches++;
        }
        if (job.skills && job.skills.length > 0) {
            for (const jobSkill of job.skills) {
                if (allUserSkills.has(jobSkill.toLowerCase()))
                    matches++;
            }
        }
        if (specialist && specialist.supportedCategories.includes(category)) {
            matches += 2;
        }
        // Нормализация: 3-4 совпадения = 100%
        const finalScore = matches / 4;
        return Math.min(1, Math.max(0.05, finalScore));
    }
    isVagueDescription(text) {
        const vaguePatterns = [
            /сделать\s+(как-нибудь|красиво|хорошо)/,
            /нужн[оа]\s+(сделать|что-то)/,
            /подробности\s+(потом|позже|в\s+личке)/,
            /подумаем\s+по\s+ходу/,
        ];
        return vaguePatterns.some(p => p.test(text)) || text.length < 80;
    }
    calculateConfidence(job, blockers, skillCoverage) {
        let confidence = 0.5;
        // Описание
        if (job.description.length > 200)
            confidence += 0.15;
        if (job.description.length > 500)
            confidence += 0.1;
        // Навыки
        confidence += skillCoverage * 0.2;
        // Блокеры снижают уверенность
        confidence -= blockers.filter(b => b.severity === 'critical').length * 0.3;
        confidence -= blockers.filter(b => b.severity === 'major').length * 0.15;
        return Math.max(0, Math.min(1, confidence));
    }
    extractSpecificPlatform(text) {
        const platforms = ['1с', 'bitrix', 'битрикс', 'wordpress', 'shopify', 'wix', 'tilda', 'тильда'];
        for (const p of platforms) {
            if (text.includes(p))
                return p;
        }
        return null;
    }
    hasServiceFor(platform) {
        return Object.values(this.services).some(s => s.enabled && s.purpose.toLowerCase().includes(platform));
    }
    /**
     * Sherlock's Deep Deduction Skill: Многоэтапное исследование через Perplexity
     */
    async performDeepDeduction(job, category, specialist) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        // 1. Техническое исследование
        const techQuery = `Анализируй фриланс задачу: "${job.title}". Описание: ${job.description.slice(0, 500)}. 
      Какие библиотеки, фреймворки и архитектурные паттерны являются эталоном (best practices) для ее решения в 2026-2027 годах? 
      Укажи конкретные NPM пакеты или SDK. Будь краток.`;
        // 2. Анализ конкурентов и подводных камней
        const riskQuery = `Какие основные технические сложности, лимиты API или инфраструктурные барьеры могут возникнуть при реализации: "${job.title}"? 
      Также найди, как подобные задачи решаются конкурентами или в топовых open-source проектах.`;
        // 3. Анализ вложенных файлов (если есть) через Gemini
        let attachmentInsights = '';
        if (job.attachmentsContent) {
            const attachQuery = `Анализируй приложенные файлы к фриланс-задаче: "${job.title}".
      
      КОНТЕНТ ФАЙЛОВ:
      ${job.attachmentsContent.slice(0, 5000)}
      
      Твоя задача — извлечь специфические технические требования, архитектурные детали, ограничения или конкретный стек технологий, который требует заказчик в этих файлах. 
      Если файлы содержат код — объясни его суть. Если схему БД — опиши сущности.
      Сделай краткую, но ёмкую экспертную сводку.`;
            attachmentInsights = await (0, ai_1.generateWithGemini)(attachQuery, "Ты — ведущий системный архитектор. Твоя задача — извлекать скрытые требования и технические детали из вложений в ТЗ.");
        }
        // 3. Анализ вложения URL и техническая разведка (NEW)
        let siteTechStack = '';
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        const urls = text.match(urlRegex);
        if (urls && urls.length > 0 && this.browser) {
            siteTechStack = await this.performTechnicalRecon(urls[0]);
        }
        const [techResearch, risks] = await Promise.all([
            (0, ai_1.perplexitySearch)(techQuery),
            (0, ai_1.perplexitySearch)(riskQuery)
        ]);
        // 3. Анализ Win Probability (Шанс на победу)
        let winProb = 50; // Базовая вероятность
        // Коррекция на основе количества откликов
        const propCount = job.proposalsCount || 0;
        if (propCount < 5)
            winProb += 20;
        else if (propCount > 20)
            winProb -= 20;
        // Коррекция на основе соответствия навыкам (специалиста)
        const skillCoverage = this.checkSkillCoverage(job, category, specialist);
        winProb += (skillCoverage - 0.5) * 60; // От -30% до +30%
        // Коррекция на бюджет
        if (job.budget?.amount && job.budget.amount > 10000)
            winProb += 5;
        // 4. Идеи для допродажи (только релевантные)
        const upsellIdeas = [];
        if (category === 'web_frontend')
            upsellIdeas.push('Проработка адаптивной мобильной версии', 'Интеграция систем аналитики');
        if (category === 'telegram_bot')
            upsellIdeas.push('Настройка рассылок по сегментам', 'Интеграция с CRM');
        if (category === 'design_ui')
            upsellIdeas.push('Подготовка анимированных версий баннера', 'Разработка комплекта для разных соцсетей');
        if (category === 'marketing_ads')
            upsellIdeas.push('А/Б тестирование заголовков', 'Настройка ретаргетинга');
        return {
            techResearch: techResearch || 'Исследование временно недоступно.',
            competitorAnalysis: (risks || '').split('\n').filter(l => l.toLowerCase().includes('конкурент') || l.toLowerCase().includes('аналог')).join('\n') || 'Анализ конкурентов завершен.',
            apiPitfalls: risks || 'Специфических рисков не обнаружено.',
            winProbability: Math.min(Math.max(Math.round(winProb), 5), 98),
            upsellIdeas: upsellIdeas,
            attachmentInsights: attachmentInsights || undefined,
            siteTechStack: siteTechStack || undefined
        };
    }
    /**
     * Sherlock's Technical Recon: Анализ стека сайта через браузер
     */
    async performTechnicalRecon(url) {
        if (!this.browser)
            return 'Разведка недоступна';
        try {
            console.log(`🕵️‍♂️ [Sherlock] Разведка сайта: ${url}`);
            await this.browser.goto(url);
            const htmlText = await this.browser.extractText('body');
            const html = htmlText.toLowerCase();
            const tech = [];
            if (html.includes('wp-content'))
                tech.push('WordPress');
            if (html.includes('_next/static'))
                tech.push('Next.js');
            if (html.includes('react'))
                tech.push('React');
            if (html.includes('vue'))
                tech.push('Vue.js');
            if (html.includes('nuxt'))
                tech.push('Nuxt');
            if (html.includes('bitrix'))
                tech.push('1C-Bitrix');
            if (html.includes('jquery'))
                tech.push('jQuery');
            if (html.includes('tailwindcss'))
                tech.push('TailwindCSS');
            if (html.includes('bootstrap'))
                tech.push('Bootstrap');
            if (html.includes('gtm.js') || html.includes('googletagmanager'))
                tech.push('Google Tag Manager');
            return tech.length > 0
                ? `На сайте ${url} обнаружено: ${tech.join(', ')}`
                : `На сайте ${url} технологии не определены (возможно, статический HTML или кастомный стек)`;
        }
        catch (e) {
            return `Ошибка разведки ${url}: ${e?.message || e}`;
        }
    }
    /**
     * Логика Шерлока по расчету рейтинга задачи (0-100)
     */
    calculateTaskScore(feasibility, job, winProb = 50) {
        let score = 40; // База изменена
        // 1. Шанс на победу (новый фактор)
        if (winProb >= 80)
            score += 30;
        else if (winProb >= 60)
            score += 15;
        else if (winProb < 40)
            score -= 20;
        // 2. Деньги
        const rate = feasibility.rewardAnalysis.hourlyRate || 0;
        if (rate >= 2500)
            score += 30;
        else if (rate >= 1500)
            score += 15;
        else if (rate < 1000)
            score -= 30;
        // 3. Платформа (Кворк — лимитированный ресурс)
        if (job.platform === 'kwork') {
            if (rate >= 2000)
                score += 10;
        }
        // 4. Сложность (Шерлок любит четкие задачи)
        if (feasibility.blockers.length === 0)
            score += 10;
        return Math.max(0, Math.min(100, score));
    }
    /**
     * Обработка всех вложений к задаче через мультимодальный Gemini
     */
    async handleAttachments(job) {
        if (!job.attachmentUrls || !this.browser)
            return '';
        let combinedSummary = '--- АНАЛИЗ ВЛОЖЕНИЙ (Sherlock Multimodal) ---\n\n';
        let processedCount = 0;
        for (const url of job.attachmentUrls) {
            try {
                const buffer = await this.browser.downloadToBuffer(url);
                if (!buffer) {
                    console.warn(`⚠️ Не удалось скачать вложение: ${url}`);
                    continue;
                }
                // Определяем MIME-тип по расширению
                const ext = path.extname(url).toLowerCase();
                let mimeType = 'application/octet-stream';
                if (ext === '.pdf')
                    mimeType = 'application/pdf';
                else if (ext === '.png')
                    mimeType = 'image/png';
                else if (ext === '.jpg' || ext === '.jpeg')
                    mimeType = 'image/jpeg';
                else if (ext === '.webp')
                    mimeType = 'image/webp';
                else {
                    // Для других типов пробуем просто сгенерировать описание по имени, 
                    // но Gemini 1.5 хорошо кушает только PDF и картинки в base64
                    if (ext !== '.docx') { // docx в base64 не всегда работает без спец. обработки
                        console.log(`⏩ Пропускаю неподдерживаемый тип файла: ${ext}`);
                        continue;
                    }
                }
                const summary = await (0, ai_1.analyzeFileWithGemini)(buffer, mimeType, `Проанализируй этот файл, приложенный к фриланс-заказу "${job.title}". 
           Извлеки ключевые технические требования, функционал, ограничения или визуальные детали решения. 
           Если это скриншот — опиши структуру интерфейса. 
           Если это ТЗ — выдели критические моменты. 
           Дай краткую выжимку.`);
                if (summary) {
                    const fileName = path.basename(url);
                    combinedSummary += `📁 Файл [${fileName}]:\n${summary}\n\n`;
                    processedCount++;
                }
            }
            catch (error) {
                console.error(`Ошибка при обработке вложения ${url}:`, error);
            }
        }
        return processedCount > 0 ? combinedSummary : '';
    }
}
exports.ScoutAgent = ScoutAgent;
