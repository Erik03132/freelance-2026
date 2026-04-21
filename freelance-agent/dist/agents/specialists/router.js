"use strict";
/**
 * Router Agent — Диспетчер задач
 *
 * Определяет, какому специализированному агенту передать задачу.
 * Для комплексных задач создаёт оркестрацию нескольких агентов.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.routeTask = routeTask;
/**
 * Маршрутизация задачи к специализированному агенту
 */
function routeTask(job, category) {
    const text = `${job.title} ${job.description}`.toLowerCase();
    // Маппинг категорий → основной агент
    const categoryToAgent = {
        'web_fullstack': 'webdev',
        'web_frontend': 'webdev',
        'web_backend': 'webdev',
        'telegram_bot': 'bot',
        'chrome_extension': 'webdev',
        'parsing_scraping': 'data',
        'mobile_app': 'webdev',
        'desktop_app': 'webdev',
        'devops': 'devops',
        'data_science': 'data',
        'design_ui': 'design',
        'marketing_ads': 'ads',
        'lecture_education': 'content',
        'text_content': 'content',
        'engineering_drafting': 'architecture',
        'operational_manual': 'content',
        'other': 'webdev',
    };
    const primaryAgent = categoryToAgent[category] || 'webdev';
    const supportAgents = [];
    let mode = 'single';
    const rationales = [];
    // Определяем, нужны ли дополнительные агенты
    // Веб-задача + дизайн
    if (['web_fullstack', 'web_frontend'].includes(category)) {
        if (matchesAny(text, ['дизайн', 'макет', 'figma', 'ui', 'ux', 'красивый', 'современный'])) {
            supportAgents.push('design');
            mode = 'sequential';
            rationales.push('Задача включает дизайн — подключаем Design Agent для мокапов');
        }
    }
    // Веб-задача + деплой
    if (['web_fullstack', 'web_backend'].includes(category)) {
        if (matchesAny(text, ['деплой', 'deploy', 'docker', 'ci/cd', 'сервер', 'хостинг', 'production'])) {
            supportAgents.push('devops');
            mode = 'sequential';
            rationales.push('Задача включает деплой — подключаем DevOps Agent');
        }
    }
    // Бот + веб-панель
    if (category === 'telegram_bot') {
        if (matchesAny(text, ['admin', 'панел', 'dashboard', 'веб', 'сайт', 'лендинг'])) {
            supportAgents.push('webdev');
            mode = 'sequential';
            rationales.push('Бот + веб-панель — подключаем WebDev Agent для админки');
        }
    }
    // Парсинг + визуализация
    if (category === 'parsing_scraping') {
        if (matchesAny(text, ['dashboard', 'визуализ', 'сайт', 'дашборд', 'отчёт', 'график'])) {
            supportAgents.push('webdev');
            mode = 'sequential';
            rationales.push('Парсинг + дашборд — подключаем WebDev Agent для визуализации');
        }
    }
    // Контент + дизайн
    if (category === 'text_content') {
        if (matchesAny(text, ['визуал', 'картинк', 'баннер', 'дизайн', 'инфографик'])) {
            supportAgents.push('design');
            mode = 'parallel';
            rationales.push('Контент + визуал — Design Agent работает параллельно');
        }
    }
    const rationale = rationales.length > 0
        ? rationales.join('. ')
        : `Задача "${category}" полностью обрабатывается ${primaryAgent} Agent`;
    return { primaryAgent, supportAgents, mode, rationale, category };
}
function matchesAny(text, keywords) {
    return keywords.some(keyword => text.includes(keyword));
}
