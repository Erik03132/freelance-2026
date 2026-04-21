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
const dotenv = __importStar(require("dotenv"));
dotenv.config();
// 1. Загрузка профиля
function loadProfile() {
    const profilePath = path.join(__dirname, '..', 'config', 'profile.json');
    if (fs.existsSync(profilePath)) {
        return JSON.parse(fs.readFileSync(profilePath, 'utf8'));
    }
    return {
        user: { name: 'Игорь' },
        skills: { 'Flutter': 1, 'Dart': 1, 'Node.js': 1, 'REST API': 1 },
        skillSynonyms: { 'Flutter': ['Dart'] }
    };
}
async function runTest() {
    const projectRoot = path.join(__dirname, '..');
    const profile = loadProfile();
    const scout = new scout_1.ScoutAgent(profile, projectRoot);
    const sampleJob = {
        platform: 'kwork',
        url: 'https://kwork.ru/projects/3139368',
        title: 'REST API / Flutter / APK',
        description: `Приветствую тебя S.T.A.L.K.E.R Не знаю, на кой чёрт тебе этот KWORK сдался! Но я в чужие дела не лезу. Зашёл, значит есть зачем. Что нужно сделать Приложение для знакомств. пробное! Техно-демо! 3 страницы! 1) самая важная (знакомства) 2) заглушка (сообщения) 3) заглушка (профиль) На данном этапе не нужна страница авторизации и регистрации. Просто делаете обращение к странице, она возвращает JSON с данными. Эти данные выводим на главной странице. Дизайна нет. Есть похожее приложение! На первый раз позаимствуем их оформление.`,
        skills: ['Flutter', 'REST API', 'JSON', 'Dart', 'Mobile app'],
        budget: {
            amount: 4000,
            currency: 'RUB',
            type: 'fixed'
        }
    };
    console.log('🚀 АНАЛИЗ ЗАДАЧИ: REST API / Flutter / APK');
    console.log('---------------------------------------------------------');
    try {
        const result = await scout.analyzeAndProposeExpert(sampleJob);
        console.log('\n🔍 ОЦЕНКА ВЫПОЛНИМОСТИ (FEASIBILITY):');
        console.log(`- Выполнимо: ${result.feasibility.feasible ? '✅ ДА' : '❌ НЕТ'}`);
        console.log(`- Категория: ${result.feasibility.category}`);
        console.log(`- Оценка времени: ${result.feasibility.effortHours} часов`);
        console.log(`- ROI (Рейтинг): ${result.score}/100`);
        console.log('\n📋 ЗАМЕТКИ ОПЕРАТОРА (Sherlock Intelligence):');
        console.log(result.operatorNotes);
        console.log('\n🤖 ГЕНЕРИРОВАННЫЙ ОТВЕТ (ЭКСПЕРТНОЕ КП):');
        console.log('---------------------------------------------------------');
        console.log(result.proposal);
        console.log('---------------------------------------------------------');
        if (result.executionPlan) {
            console.log('\n🗺️ ПЛАН ИСПОЛНЕНИЯ (EXECUTION PLAN):');
            console.log(JSON.stringify(result.executionPlan, null, 2));
        }
    }
    catch (error) {
        console.error('❌ ОШИБКА:', error);
    }
}
runTest();
