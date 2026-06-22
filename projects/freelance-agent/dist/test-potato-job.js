"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const scout_1 = require("./agents/scout");
async function analyzePotatoJob() {
    const scout = new scout_1.ScoutAgent({ user: { name: 'Эрик' } }, process.cwd());
    const potatoJob = {
        title: 'Разработка ПО для машины по сортировке картофеля (Computer Vision)',
        description: 'Нужна обученная модель для сортировки картофеля (брак/хороший). Есть фото-сет (хороший/плохой). В перспективе — масштабирование на другие культуры. Только софт и модель, электрику делать не надо. Нужна помощь в пусконаладке.',
        budget: { amount: 50000, currency: 'RUB' }
    };
    console.log('\n--- АНАЛИЗ ЗАДАЧИ ПО КАРТОФЕЛЮ (ШЕРЛОК) ---');
    const result = await scout.analyzeAndProposeExpert(potatoJob);
    console.log('\n--- ИТОГОВОЕ ПРЕДЛОЖЕНИЕ ---\n');
    console.log(result.proposal);
    console.log('\n--- ОТЧЕТ ДЛЯ ОПЕРАТОРА ---\n');
    console.log(result.operatorNotes);
}
analyzePotatoJob().catch(console.error);
