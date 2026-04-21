import { ScoutAgent } from './freelance-agent/src/agents/scout';
import { RawJob } from './freelance-agent/src/models/job';
import * as fs from 'fs';
import * as path from 'path';
import * as dotenv from 'dotenv';

// Load environment variables
dotenv.config({ path: path.join(__dirname, 'freelance-agent', '.env') });

async function run() {
    const profile = JSON.parse(fs.readFileSync(path.join(__dirname, 'freelance-agent', 'config', 'profile.json'), 'utf-8'));
    const scout = new ScoutAgent(profile, path.join(__dirname, 'freelance-agent'));

    const job: RawJob = {
        platform: 'kwork',
        url: 'https://kwork.ru/projects/selected',
        title: 'Верстка сайта (React, Next.js)',
        description: `Финтех-проект ищет фронтенд-разработчика для периодических задач на парт-тайм.
Что нужно делать:
— Верстать и дорабатывать страницы сайта (лендинг, саппорт, community и т.д.)
— Реализовывать дизайн-макеты в коде
— Иногда предлагать и реализовывать UI/UX улучшения

Стек:
— React / Next.js
— Базовое понимание Figma (забирать макеты)

Условия:
— Удалённо, парт-тайм
— Задачи приходят по мере необходимости (несколько раз в месяц)
— Оплата 1 000–5 000 ₽ за задачу, в зависимости от объёма
— Долгосрочное сотрудничество — ищем одного человека, с которым будет комфортно работать постоянно`,
        budget: {
            amount: 5000,
            currency: 'RUB',
            type: 'fixed'
        },
        skills: ['React', 'Next.js', 'TypeScript', 'Figma'],
        postedAt: new Date(),
        status: 'new'
    };

    console.log('🕵️‍♂️ Sherlock is investigating...');
    const result = await scout.analyzeAndProposeExpert(job);

    console.log('\n' + '='.repeat(80));
    console.log('  🤖 ЭКСПЕРТНОЕ ПРЕДЛОЖЕНИЕ');
    console.log('='.repeat(80) + '\n');
    console.log(result.proposal);

    console.log('\n' + '='.repeat(80));
    console.log('  🔍 ИНТЕЛЛЕКТ-ОТЧЕТ');
    console.log('='.repeat(80) + '\n');
    console.log(result.operatorNotes);
}

run().catch(console.error);
