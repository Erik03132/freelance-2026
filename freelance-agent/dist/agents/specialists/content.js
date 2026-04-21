"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ContentAgent = void 0;
const base_1 = require("./base");
const team_1 = require("../../constants/team");
class ContentAgent extends base_1.BaseSpecialist {
    agentType = 'content';
    agentName = team_1.TEAM_ROLES.SHAKESPEARE.NAME;
    emoji = '✍️';
    expertise = team_1.TEAM_ROLES.SHAKESPEARE.EXPERTISE;
    supportedCategories = [
        'text_content', 'lecture_education'
    ];
    capabilities = [
        {
            name: 'Content Generation',
            description: 'Генерация профессиональных и выверенных текстов через Gemini MCP',
            mcpServer: 'Gemini',
            enabled: true,
        },
        {
            name: 'Notion Integration',
            description: 'Построение базы знаний и курсов в Notion',
            mcpServer: 'Notion MCP',
            enabled: false, // TODO: подключить
        }
    ];
    recommendTechStack(job) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        const stack = [];
        if (this.matchesAny(text, ['лекц', 'обучен', 'курс', 'education'])) {
            stack.push({ name: 'Google Slides / Miro / Notion', reason: 'Инструменты для визуализации лекций и структуры материалов.' });
            stack.push({ name: 'Интерактивные задачи', reason: 'Использование платформы (LMS) для контроля знаний аудитории.' });
        }
        else {
            stack.push({ name: 'Markdown / HTML', reason: 'Чистый формат текста для правильной дистрибьюции.' });
            if (this.matchesAny(text, ['seo', 'поиск'])) {
                stack.push({ name: 'SEO стандарты (Ahrefs guidelines)', reason: 'Соблюдение LSI и ключевых слов для поднятия текста в поисковиках.' });
            }
        }
        return stack;
    }
    createPlan(job, techStack) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        const steps = [];
        let order = 1;
        steps.push({
            order: order++,
            title: 'Анализ аудитории и сбор семантики',
            description: 'Исследование ЦА, понимание болей, сбор tone-of-voice и ключевых слов.',
            deliverable: 'Структура, глоссарий и tone of voice',
            estimatedHours: '2-3 часа',
            rationale: 'Любой контент пишется под конкретного читателя или слушателя. Это основа.',
            canAutomate: true,
        });
        steps.push({
            order: order++,
            title: 'Создание драфтов (Черновиков)',
            description: 'Написание основной структуры (Outline) и первых разделов для согласования стиля.',
            deliverable: 'Драфт документации/статьи',
            estimatedHours: '4-8 часов',
            rationale: 'Сверяемся по стилю до написания всего массива текста.',
            canAutomate: true,
            automationTool: 'Gemini AI drafting'
        });
        steps.push({
            order: order++,
            title: 'Доводка, редактура и публикация',
            description: 'Финальная полировка текста, проверка уникальности (антиплагиат), верстка таблиц/графиков/иллюстраций.',
            deliverable: 'Готовый материал',
            estimatedHours: '3-6 часов',
            rationale: 'Текст должен легко читаться и быть без ошибок. Вычитка (Proofreading).',
            canAutomate: true,
        });
        return steps;
    }
    generateQuestions(job) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        const questions = [];
        questions.push('Есть ли зафиксированный Tone of Voice (например: формальный, дружеский, экспертный)?');
        questions.push('Каков ожидаемый средний объем текста / продолжительность курса?');
        if (this.matchesAny(text, ['текст', 'стать', 'seo', 'копирайт'])) {
            questions.push('Есть ли конкретные SEO ключи, которые обязательно должны быть в статье?');
        }
        return questions.slice(0, 5);
    }
    specifyPrototype(job) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        if (this.matchesAny(text, ['текст', 'стать', 'seo', 'копирайт'])) {
            return {
                type: 'article_draft',
                files: new Map(),
                description: 'Структура статьи (h1-h2-h3) и написанное Введение (Intro) для проверки слога.',
                completionPercent: 20,
                whatIsImplemented: ['Заголовочный каркас', 'Введение (1 абзац)', 'Мокап визуалов'],
                whatIsLeft: ['Пишем весь материал', 'Редактируем', 'Иллюстрации'],
                demoInstructions: 'Заберу на 15 минут, скину в Google Docs.'
            };
        }
        return null;
    }
    explainWhyMe(job) {
        return `🎯 Почему я подхожу:
• Создаю тексты, контент и лекции без "воды", 100% информативности.
• Понимаю, как работают поисковики - текст будет работать для SEO.
• Имею технический бэкграунд: могу писать грамотно о сложнейших ИТ продуктах.`;
    }
}
exports.ContentAgent = ContentAgent;
