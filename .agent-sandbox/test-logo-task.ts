
import { ScoutAgent } from '../freelance-agent/src/agents/scout';
import { RawJob } from '../freelance-agent/src/models/job';
import fs from 'fs';
import path from 'path';

async function runTest() {
    console.log('--- ТЕСТ: ШЕРЛОК + РЕМБРАНДТ (ЛОГОТИП) ---');

    const job: RawJob = {
        platform: 'kwork',
        url: 'https://kwork.ru/projects/logo-test',
        title: 'Нужен новый логотип для платформы Внешка',
        description: 'Добрый день! Нужно создать новый логотип для нашей "платформы Внешка", можете изучить вложение, там есть детали по цветам. Мы хотим премиальный, современный вид для фрилансеров.',
        budget: { amount: 8000, currency: 'RUB', type: 'fixed' },
        skills: ['Дизайн логотипов', 'Figma', 'Брендинг'],
        hasAttachments: true,
        // Имитируем, что Шерлок уже прочитал вложение (SvelteKit/Web3/etc)
        attachmentsContent: 'ЦВЕТА: Глубокий синий #0f172a, Неоновый голубой #38bdf8. СТИЛЬ: Минимализм, геометрические формы. Стек платформы: SvelteKit + Tailwind.'
    };

    const scout = new ScoutAgent();
    // Инициализация (может потребоваться для доступа к профилю)
    
    console.log('🕵️‍♂️ Шерлок начинает дедукцию...');
    const result = await scout.analyzeAndProposeExpert(job);

    console.log('\n--- ОЦЕНКА ---');
    console.log(`Score: ${result.score}%`);
    console.log(`Prob: ${result.winProbability}%`);
    
    console.log('\n--- ТЕКСТ ПРЕДЛОЖЕНИЯ (БЕЗ ** СИМВОЛОВ) ---');
    console.log(result.expertProposal?.fullText);

    // Сохраним в файл для проверки
    fs.writeFileSync('logo-offer.txt', result.expertProposal?.fullText || '');
}

runTest().catch(console.error);
