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
const scout_1 = require("./agents/scout");
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
// 1. Загрузка профиля
function loadProfile() {
    const profilePath = path.join(__dirname, '..', 'config', 'profile.json');
    if (fs.existsSync(profilePath)) {
        return JSON.parse(fs.readFileSync(profilePath, 'utf8'));
    }
    return {
        user: { name: 'Игорь' },
        skills: { 'React': 1, 'TypeScript': 1, 'Node.js': 1, 'Next.js': 1 },
        skillSynonyms: { 'React': ['React.js', 'ReactJS'] }
    };
}
async function runTest() {
    const projectRoot = path.join(__dirname, '..');
    const profile = loadProfile();
    const scout = new scout_1.ScoutAgent(profile, projectRoot);
    // Тестовая задача (Имитируем задачу с Kwork/FL)
    const sampleJob = {
        platform: 'kwork',
        url: 'https://kwork.ru/projects/12345',
        title: 'Разработка Telegram бота с интеграцией Stripe',
        description: `Нужен опытный разработчик для создания Telegram бота на Node.js. 
    Бот должен уметь:
    1. Показывать каталог товаров
    2. Принимать оплату через Stripe
    3. Сохранять заказы в базу данных (PostgreSQL или MongoDB)
    4. Иметь простую админ-панель для управления товарами.
    
    Срок выполнения: 7-10 дней. Бюджет обсуждается.`,
        skills: ['Node.js', 'Telegram API', 'Stripe', 'TypeScript', 'PostgreSQL'],
        budget: {
            amount: 45000,
            currency: 'RUB',
            type: 'fixed'
        }
    };
    console.log('🚀 ЗАПУСК ТЕСТА: ШЕРЛОК (SCOUT) + PERPLEXITY + СПЕЦИАЛИСТ');
    console.log('---------------------------------------------------------');
    console.log(`Заголовок задачи: ${sampleJob.title}`);
    console.log('---------------------------------------------------------');
    try {
        const result = await scout.analyzeAndProposeExpert(sampleJob);
        console.log('\n🔍 ОЦЕНКА ВЫПОЛНИМОСТИ (FEASIBILITY):');
        console.log(`- Выполнимо: ${result.feasibility.feasible ? '✅ ДА' : '❌ НЕТ'}`);
        console.log(`- Категория: ${result.feasibility.category}`);
        console.log(`- Оценка времени: ${result.feasibility.effortHours} часов`);
        console.log(`- ROI (Рейтинг): ${result.score}/100`);
        console.log('\n📋 ЗАМЕТКИ ОПЕРАТОРА (Включая Perplexity):');
        console.log(result.operatorNotes);
        console.log('\n🤖 ГЕНЕРИРОВАННЫЙ ОТВЕТ (ЭКСПЕРТНОЕ КП):');
        console.log('---------------------------------------------------------');
        console.log(result.proposal);
        console.log('---------------------------------------------------------');
        if (result.warnings.length > 0) {
            console.log('\n⚠️ ПРЕДУПРЕЖДЕНИЯ:');
            result.warnings.forEach(w => console.log(`- ${w}`));
        }
    }
    catch (error) {
        console.error('❌ ОШИБКА В ТЕСТЕ:', error);
    }
}
runTest();
