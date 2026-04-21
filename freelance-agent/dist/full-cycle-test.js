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
const kwork_1 = require("./adapters/kwork");
const browser_1 = require("./services/browser");
const logger_1 = require("./services/logger");
const scout_1 = require("./agents/scout");
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
async function runFullCycle() {
    const logger = new logger_1.Logger();
    const browser = new browser_1.BrowserService(false, logger);
    const kwork = new kwork_1.KworkAdapter(browser, logger);
    // 1. Загрузка профиля
    const profilePath = path.join(__dirname, '..', 'config', 'profile.json');
    const profile = JSON.parse(fs.readFileSync(profilePath, 'utf8'));
    const scout = new scout_1.ScoutAgent(profile, path.join(__dirname, '..'));
    console.log('🚀 ЗАПУСК ПОЛНОГО ЦИКЛА: ПАРСИНГ -> ШЕРЛОК -> КП');
    console.log('------------------------------------------------');
    try {
        await browser.launch();
        console.log('✅ Браузер запущен. Иду на Kwork...');
        await kwork.navigateToJobs();
        const jobs = await kwork.extractJobs();
        console.log(`✅ Нашел ${jobs.length} задач на Kwork.`);
        // Берем 2 самые свежие/подходящие задачи для теста
        const testJobs = jobs.slice(0, 2);
        for (const job of testJobs) {
            console.log('\n' + '='.repeat(50));
            console.log(`🔍 ОБРАБОТКА ЗАДАЧИ: ${job.title}`);
            console.log('URL:', job.url);
            console.log('='.repeat(50));
            console.log('🕵️‍♂️ Шерлок анализирует задачу через Perplexity...');
            const result = await scout.analyzeAndProposeExpert(job);
            console.log('\n📊 ИТОГИ АНАЛИЗА:');
            console.log(`- Категория: ${result.feasibility.category}`);
            console.log(`- Выполнимо: ${result.feasibility.feasible ? '✅' : '❌'}`);
            console.log(`- Оценка ROI: ${result.score}/100`);
            console.log(`- Агент-исполнитель: ${result.agentUsed}`);
            console.log('\n📜 СГЕНЕРИРОВАННОЕ ПРЕДЛОЖЕНИЕ:');
            console.log('------------------------------------------------');
            console.log(result.proposal);
            console.log('------------------------------------------------');
            console.log('\n🔍 ИНСАЙТЫ ОТ PERPLEXITY:');
            // Инсайты лежат в operatorNotes
            const insights = result.operatorNotes.split('🔍 ИНСАЙТЫ ОТ PERPLEXITY:')[1] || 'Нет данных';
            console.log(insights.trim());
        }
    }
    catch (error) {
        console.error('❌ ОШИБКА ЦИКЛА:', error);
    }
    finally {
        await browser.close();
    }
}
runFullCycle();
