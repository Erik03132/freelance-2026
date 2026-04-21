"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.AdsSpecialist = void 0;
const base_1 = require("./base");
const team_1 = require("../../constants/team");
class AdsSpecialist extends base_1.BaseSpecialist {
    agentType = 'ads';
    agentName = team_1.TEAM_ROLES.OSCAR.NAME;
    emoji = '🎯';
    expertise = team_1.TEAM_ROLES.OSCAR.EXPERTISE;
    supportedCategories = [
        'marketing_ads'
    ];
    capabilities = [
        {
            name: 'Ad Strategy Benchmarking',
            description: 'Анализ топовых креативов конкурентов через библиотеки рекламы',
            enabled: true,
        },
        {
            name: 'Conversion Optimization',
            description: 'Применение паттернов Growth Hacking для повышения конверсии',
            enabled: true,
        }
    ];
    recommendTechStack(job) {
        return [
            { name: 'Яндекс.Директ (Поиск + РСЯ)', reason: 'Основной канал для получения горячего спроса в RU сегменте.' },
            { name: 'VK Ads (Таргет)', reason: 'Эффективный инструмент для работы с интересами и базами конкурентов.' },
            { name: 'GTM + Яндекс.Метрика', reason: 'Для сквозной аналитики и отслеживания ROI/ROAS.' },
        ];
    }
    createPlan(job, techStack) {
        return [
            {
                order: 1,
                title: 'Бенчмаркинг и стратегия',
                description: 'Анализ рекламных стратегий конкурентов и подбор работающих креативных пар.',
                rationale: 'Мы не гадаем, а используем то, что уже приносит результат в вашей нише.',
                deliverable: 'Карта конкурентных преимуществ',
                estimatedHours: '3-4',
                canAutomate: true,
            },
            {
                order: 2,
                title: 'Настройка объявлений',
                description: 'Создание продающих текстов и баннеров для рекламных кабинетов.',
                rationale: 'Качественные креативы снижают стоимость клика (CPC).',
                deliverable: 'Готовые к запуску кампании',
                estimatedHours: '8-10',
                canAutomate: true,
            }
        ];
    }
    generateQuestions(job) {
        return [
            'Какой месячный бюджет планируете выделить на рекламу?',
            'Есть ли уже настроенная аналитика на сайте?',
            'На какие конкретно регионы планируется запуск?'
        ];
    }
    specifyPrototype(job) {
        return {
            type: 'ad_campaign_draft',
            files: new Map(),
            description: 'Проект рекламной кампании: 5 вариантов заголовков и текстов по AIDA.',
            completionPercent: 50,
            whatIsImplemented: ['Заголовки и офферы', 'Список ключевых фраз'],
            whatIsLeft: ['Настройка в кабинете', 'Модерация'],
        };
    }
    explainWhyMe(job) {
        return 'Я не просто настраиваю "кнопки", а выстраиваю систему, которая приносит заказы, а не просто клики. Работаю на результат (ROI).';
    }
}
exports.AdsSpecialist = AdsSpecialist;
