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
        skills: { 'React': 1, 'TypeScript': 1, 'Node.js': 1, 'Next.js': 1, 'Svelte': 1 },
        skillSynonyms: { 'React': ['React.js', 'ReactJS'] }
    };
}
async function runTest() {
    const projectRoot = path.join(__dirname, '..');
    const profile = loadProfile();
    const scout = new scout_1.ScoutAgent(profile, projectRoot);
    // Тестовая задача с ВЛОЖЕНИЕМ (simulated)
    const sampleJob = {
        platform: 'fl.ru',
        url: 'https://fl.ru/projects/777',
        title: 'Разработка дэшборда для CRM системы',
        description: `Нужно разработать фронтенд для внутренней CRM. 
    Функционал: список клиентов, карточка клиента, графики продаж.
    Срок: 2 недели.
    Все подробности в приложенном ТЗ.`,
        skills: ['Web Development', 'Frontend'],
        budget: {
            amount: 60000,
            currency: 'RUB',
            type: 'fixed'
        },
        // Имитируем содержимое скачанного файла ТЗ
        attachmentsContent: `
    ТЕХНИЧЕСКОЕ ЗАДАНИЕ (ПРИЛОЖЕНИЕ №1)
    ----------------------------------
    1. ТЕХНОЛОГИЧЕСКИЙ СТЕК:
       - Фреймворк: SvelteKit (ОБЯЗАТЕЛЬНО, не React!)
       - База данных: PocketBase (уже развернута)
       - Стилизация: Tailwind CSS + специфические цвета бренда (#FF5500 - Primary)
    
    2. ОСОБЕННОСТИ:
       - Нужна интеграция с существующим API PocketBase через SDK.
       - Авторизация через встроенные механизмы PocketBase.
       - Графики на Chart.js или LayerChart.
    
    3. ДИЗАЙН:
       - Минимализм, темная тема.
    `
    };
    console.log('🚀 ЗАПУСК ТЕСТА: ШЕРЛОК (SCOUT) + GEMINI ATTACHMENT ANALYSIS');
    console.log('---------------------------------------------------------');
    console.log(`Заголовок задачи: ${sampleJob.title}`);
    console.log('Содержимое вложений (имитация): Присутствует');
    console.log('---------------------------------------------------------');
    try {
        const result = await scout.analyzeAndProposeExpert(sampleJob);
        console.log('\n🔍 ОЦЕНКА ВЫПОЛНИМОСТИ (FEASIBILITY):');
        console.log(`- Выполнимо: ${result.feasibility.feasible ? '✅ ДА' : '❌ НЕТ'}`);
        console.log(`- Категория: ${result.feasibility.category}`);
        if (result.deepDeduction?.attachmentInsights) {
            console.log('\n📑 ИНСАЙТЫ ИЗ ВЛОЖЕНИЙ (Найдены Gemini):');
            console.log(result.deepDeduction.attachmentInsights);
        }
        console.log('\n🤖 ГЕНЕРИРОВАННЫЙ ОТВЕТ (ДОЛЖЕН БЫТЬ СКОРРЕКТИРОВАН ПО ТЗ):');
        console.log('---------------------------------------------------------');
        console.log(result.proposal);
        console.log('---------------------------------------------------------');
        // Проверяем, упоминается ли SvelteKit (который был только во вложении)
        if (result.proposal.toLowerCase().includes('sveltekit')) {
            console.log('\n✅ УСПЕХ: Агент увидел SvelteKit во вложении и скорректировал оффер!');
        }
        else {
            console.log('\n❌ ОШИБКА: Агент проигнорировал требования из вложений.');
        }
    }
    catch (error) {
        console.error('❌ ОШИБКА В ТЕСТЕ:', error);
    }
}
runTest();
