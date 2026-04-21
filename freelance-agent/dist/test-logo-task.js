"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const scout_1 = require("./agents/scout");
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
async function runTest() {
    console.log('--- ТЕСТ: ШЕРЛОК + РЕМБРАНДТ (ЛОГОТИП) ---');
    const job = {
        platform: 'kwork',
        url: 'https://kwork.ru/projects/logo-test',
        title: 'Нужен новый логотип для платформы Внешка',
        description: 'Добрый день! Нужно создать новый логотип для нашей "платформы Внешка", можете изучить вложение, там есть детали по цветам. Мы хотим премиальный, современный вид для фрилансеров.',
        budget: { amount: 8000, currency: 'RUB', type: 'fixed' },
        skills: ['Дизайн логотипов', 'Figma', 'Брендинг'],
        hasAttachments: true,
        // Имитируем, что Шерлок уже прочитал вложение
        attachmentsContent: 'ЦВЕТА: Глубокий синий #0f172a, Неоновый голубой #38bdf8. СТИЛЬ: Минимализм, геометрические формы. Стек платформы: SvelteKit + Tailwind.'
    };
    const profilePath = path_1.default.join(__dirname, '../config/profile.json');
    const profile = JSON.parse(fs_1.default.readFileSync(profilePath, 'utf-8'));
    const scout = new scout_1.ScoutAgent(profile, process.cwd());
    console.log('🕵️‍♂️ Шерлок начинает дедукцию...');
    const result = await scout.analyzeAndProposeExpert(job);
    console.log('\n--- ОЦЕНКА ---');
    console.log(`Score: ${result.score}%`);
    console.log(`Prob: ${result.score}%`);
    console.log('\n--- ТЕКСТ ПРЕДЛОЖЕНИЯ (БЕЗ ** СИМВОЛОВ) ---');
    console.log(result.expertProposal?.fullText);
    // Сохраним в файл для проверки
    const outputPath = path_1.default.join(process.cwd(), 'logo-offer.txt');
    fs_1.default.writeFileSync(outputPath, result.expertProposal?.fullText || '');
    console.log(`\n📄 Оффер сохранен в: ${outputPath}`);
}
runTest().catch(console.error);
