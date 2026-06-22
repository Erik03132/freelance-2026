"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const scout_1 = require("./agents/scout");
const constitution_1 = require("./constants/constitution");
async function testConstitution() {
    const scout = new scout_1.ScoutAgent({ user: { name: 'Эрик' } }, process.cwd());
    const illegalJob = {
        title: 'Сайт для казино',
        description: 'Нужно сделать сайт с игровыми автоматами и ставками.',
        budget: { amount: 100000, currency: 'RUB' }
    };
    console.log('--- ТЕСТ 1: ИЛЛЕГАЛЬНАЯ ЗАДАЧА ---');
    const result1 = await scout.analyzeAndProposeExpert(illegalJob);
    console.log('Выполнимо:', result1.feasibility.feasible);
    console.log('Причины:', result1.feasibility.reasons);
    console.log('Текст (фрагмент):', result1.proposal.substring(0, 100));
    const lowBudgetJob = {
        title: 'Лендинг',
        description: 'Простой сайт на реакте.',
        budget: { amount: 2000, currency: 'RUB' }
    };
    console.log('\n--- ТЕСТ 2: НИЗКИЙ БЮДЖЕТ ---');
    const result2 = await scout.analyzeAndProposeExpert(lowBudgetJob);
    console.log('Ставка за час:', result2.feasibility.rewardAnalysis.hourlyRate);
    console.log('Комментарий бюджета:', result2.feasibility.rewardAnalysis.comment);
    console.log('\n--- ПРОВЕРКА КОНСТИТУЦИИ: HOURLY_RATE ---');
    console.log('Конституция HOURLY_RATE:', constitution_1.CONSTITUTION.PRICING.HOURLY_RATE);
}
testConstitution().catch(console.error);
