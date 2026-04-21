"use strict";
/**
 * 🤖 Bot Agent — Специалист по Telegram/Discord ботам
 *
 * Эксперт по:
 * - Telegram: aiogram 3.x, python-telegram-bot, Telegraf.js, grammY
 * - Discord: discord.py, discord.js
 * - Архитектура: FSM (конечные автоматы), inline keyboards, payments
 * - Паттерны: handlers → filters → middlewares → database
 *
 * Прокачан знаниями из:
 * - aiogram 3.x examples (50+ примеров)
 * - aiogram_dialog (FSM-диалоги)
 * - tgbot_template (продакшн структура)
 * - Telegram Bot API documentation
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.BotAgent = void 0;
const base_1 = require("./base");
const team_1 = require("../../constants/team");
class BotAgent extends base_1.BaseSpecialist {
    agentType = 'bot';
    agentName = team_1.TEAM_ROLES.BOTMAN.NAME;
    emoji = '🤖';
    expertise = team_1.TEAM_ROLES.BOTMAN.EXPERTISE;
    supportedCategories = ['telegram_bot'];
    capabilities = [
        {
            name: 'SDK Discovery',
            description: 'Поиск специализированных библиотек для API (Payment SDKs, CRM adapters)',
            enabled: true,
        },
        {
            name: 'Flow Mapping',
            description: 'Проектирование логики диалогов через FSM или State-машины',
            enabled: true,
        },
        {
            name: 'GitHub Integration',
            description: 'Push кода бота на GitHub',
            mcpServer: 'GitHub MCP',
            enabled: true,
        },
        {
            name: 'Neon Serverless Postgres',
            description: 'БД для хранения данных бота',
            mcpServer: 'Neon MCP',
            enabled: true,
        },
    ];
    // =========================================================
    // СТЕК ТЕХНОЛОГИЙ
    // =========================================================
    recommendTechStack(job) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        const stack = [];
        // Framework
        if (this.matchesAny(text, ['telegraf', 'node', 'javascript', 'js', 'typescript', 'ts'])) {
            stack.push({
                name: 'grammY (TypeScript)',
                reason: 'Type-safe Telegram framework. Лучше Telegraf: активнее разработка, лучше TypeScript поддержка, встроенные плагины'
            });
            stack.push({ name: 'TypeScript', reason: 'Type-safe обработка callback queries и FSM — меньше runtime ошибок' });
        }
        else {
            stack.push({
                name: 'aiogram 3.x',
                reason: 'Самый популярный async Telegram-фреймворк для Python. 10K+ звёзд, активная разработка, поддержка Bot API 7.x'
            });
            stack.push({ name: 'Python 3.12+', reason: 'Async/await, type hints, огромная экосистема' });
        }
        // FSM для сложных сценариев
        if (this.matchesAny(text, ['сценари', 'диалог', 'шаг', 'этап', 'анкет', 'опрос', 'форм'])) {
            stack.push({
                name: 'FSM (конечный автомат)',
                reason: 'Для сложных диалогов: пользователь проходит шаги (выбор → ввод → подтверждение). Aiogram FSM или aiogram-dialog для визуальных окон'
            });
        }
        // Database
        if (this.matchesAny(text, ['сохран', 'данн', 'пользовател', 'заказ', 'товар', 'каталог', 'подписк', 'статистик'])) {
            if (this.matchesAny(text, ['много пользовател', 'масштаб', 'production'])) {
                stack.push({ name: 'PostgreSQL + SQLAlchemy', reason: 'Для 1000+ пользователей нужна полноценная БД с индексами и транзакциями' });
            }
            else {
                stack.push({ name: 'SQLite + aiosqlite', reason: 'Для MVP: zero-config, файловая БД, легко мигрировать на PostgreSQL позже' });
            }
        }
        // Payments
        if (this.matchesAny(text, ['оплат', 'платёж', 'payment', 'купить', 'подписк', 'план'])) {
            if (this.matchesAny(text, ['yookassa', 'юкасса', 'юмани'])) {
                stack.push({ name: 'YooKassa SDK', reason: 'Указан в ТЗ. Стандарт для платежей в РФ, поддерживает карты/ЮMoney/SBP' });
            }
            else {
                stack.push({ name: 'Telegram Payments API', reason: 'Встроенные платежи прямо в боте — удобный UX, нативная интеграция' });
            }
        }
        // Scheduling
        if (this.matchesAny(text, ['рассылк', 'расписани', 'напоминани', 'schedule', 'cron', 'периодичес'])) {
            stack.push({ name: 'APScheduler', reason: 'Гибкий планировщик задач: cron-like расписания для рассылок и напоминаний' });
        }
        // Web App (Mini App)
        if (this.matchesAny(text, ['web app', 'mini app', 'webapp', 'веб-приложени'])) {
            stack.push({ name: 'Telegram Mini App (React)', reason: 'Полноценный UI внутри Telegram. React + Telegram Web App SDK для доступа к данным пользователя' });
        }
        // Deploy
        stack.push({ name: 'Webhook (aiohttp)', reason: 'Webhook режим для production — надёжнее polling, мгновенная реакция на сообщения' });
        return stack;
    }
    // =========================================================
    // ПЛАН РЕАЛИЗАЦИИ
    // =========================================================
    createPlan(job, techStack) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        const steps = [];
        let order = 1;
        steps.push({
            order: order++,
            title: 'SDK Discovery & Сценарии',
            description: 'Подбор лучших библиотек для интеграций и проектирование FSM states.',
            deliverable: 'Технический стек интеграций + карта диалогов',
            estimatedHours: '2-3 часа',
            rationale: 'Правильный выбор SDK на старте экономит 50% времени на отладку. Карта сценариев исключает тупиковые ветки.',
            canAutomate: true,
        });
        steps.push({
            order: order++,
            title: 'Архитектура проекта',
            description: 'Структура папок (handlers/keyboards/database/config), базовый бот с /start и /help.',
            deliverable: 'Рабочий бот с 2 командами',
            estimatedHours: '2-3 часа',
            rationale: 'Правильная структура с первого дня: handler per file, разделение логики и представления. По паттерну tgbot_template.',
            canAutomate: true,
            automationTool: 'Antigravity code generation',
        });
        // Основная логика
        if (this.matchesAny(text, ['каталог', 'товар', 'магазин', 'shop', 'корзин'])) {
            steps.push({
                order: order++,
                title: 'Каталог и корзина',
                description: 'Inline-каталог с пагинацией, добавление в корзину, просмотр корзины, очистка.',
                deliverable: 'Рабочий каталог с inline-кнопками',
                estimatedHours: '5-8 часов',
                rationale: 'Inline-кнопки удобнее reply-кнопок для каталога: не засоряют чат и позволяют вернуться к любому товару.',
                canAutomate: true,
                automationTool: 'Antigravity code generation',
            });
        }
        if (this.matchesAny(text, ['оплат', 'платёж', 'payment', 'купить'])) {
            steps.push({
                order: order++,
                title: 'Интеграция оплаты',
                description: 'Подключение платёжного провайдера, генерация инвойсов, обработка successful_payment.',
                deliverable: 'Рабочая оплата в тестовом режиме',
                estimatedHours: '3-5 часов',
                rationale: 'Telegram Payments + pre_checkout_query гарантируют, что оплата не пройдёт если товар недоступен.',
                canAutomate: false,
            });
        }
        if (this.matchesAny(text, ['рассылк', 'уведомлени', 'broadcast'])) {
            steps.push({
                order: order++,
                title: 'Система рассылок',
                description: 'Массовая рассылка с anti-flood (30 сообщений/сек), фильтрация по сегментам.',
                deliverable: 'Рассылка с прогрессом и статистикой',
                estimatedHours: '3-4 часа',
                rationale: 'Telegram лимитирует 30 msg/sec — нужна очередь с задержками, иначе бот получит Flood Wait.',
                canAutomate: true,
                automationTool: 'Antigravity code generation',
            });
        }
        if (this.matchesAny(text, ['admin', 'администр', 'управлен', 'модерац'])) {
            steps.push({
                order: order++,
                title: 'Админ-панель в боте',
                description: 'Статистика пользователей, управление контентом, бан/разбан, ручная рассылка.',
                deliverable: 'Набор админ-команд с inline-меню',
                estimatedHours: '3-5 часов',
                rationale: 'Админка в самом боте — не нужен отдельный сайт. Быстро реагировать с телефона.',
                canAutomate: true,
                automationTool: 'Antigravity code generation',
            });
        }
        // AI в боте
        if (this.matchesAny(text, ['ai', 'chatgpt', 'gpt', 'нейросет', 'умный', 'gemini'])) {
            steps.push({
                order: order++,
                title: 'Интеграция AI',
                description: 'Подключение Gemini/OpenAI для генерации ответов, контекст диалога, настройка промптов.',
                deliverable: 'Бот с AI-ответами',
                estimatedHours: '4-6 часов',
                rationale: 'Gemini Pro — бесплатный tier достаточен для MVP. Контекст-менеджер хранит историю диалога для естественных ответов.',
                canAutomate: false,
            });
        }
        // Тестирование
        steps.push({
            order: order++,
            title: 'Тестирование и деплой',
            description: 'Тестирование всех сценариев, edge cases, настройка webhook, .env конфиг.',
            deliverable: 'Стабильный бот + инструкция по деплою',
            estimatedHours: '2-4 часа',
            rationale: 'Webhook надёжнее polling: мгновенная реакция, не пропускает сообщения при перезапуске.',
            canAutomate: false,
        });
        steps.push({
            order: order++,
            title: 'Документация',
            description: 'README, список команд, .env.example, инструкция для BotFather.',
            deliverable: 'Полная документация',
            estimatedHours: '1-2 часа',
            rationale: 'Заказчик должен уметь перенастроить бота без моей помощи.',
            canAutomate: true,
            automationTool: 'Antigravity (README generation)',
        });
        return steps;
    }
    // =========================================================
    // ВОПРОСЫ
    // =========================================================
    generateQuestions(job) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        const questions = [];
        if (!this.matchesAny(text, ['botfather', 'token', 'токен'])) {
            questions.push('Бот уже создан через @BotFather? Если нет — создам и настрою.');
        }
        if (this.matchesAny(text, ['каталог', 'товар', 'магазин'])) {
            questions.push('Откуда брать данные о товарах? Есть Excel/CSV или нужна админка для ручного добавления?');
        }
        if (this.matchesAny(text, ['оплат', 'платёж'])) {
            questions.push('Какой платёжный провайдер предпочитаете? (ЮKassa, Stripe, или встроенные Telegram Payments)');
        }
        if (!this.matchesAny(text, ['сервер', 'хостинг', 'vps'])) {
            questions.push('Есть ли сервер для размещения бота? Если нет — могу задеплоить на Railway (бесплатный tier).');
        }
        if (!this.matchesAny(text, ['язык', 'python', 'node', 'typescript'])) {
            questions.push('Есть ли предпочтения по языку? Рекомендую Python (aiogram) — самая большая экосистема для Telegram-ботов.');
        }
        questions.push('Планируется ли рост числа пользователей? Это повлияет на выбор БД и архитектуру.');
        return questions.slice(0, 5);
    }
    // =========================================================
    // ПРОТОТИП
    // =========================================================
    specifyPrototype(job) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        if (this.matchesAny(text, ['каталог', 'товар', 'магазин', 'shop'])) {
            return {
                type: 'shop-bot',
                files: new Map(),
                description: 'Telegram-бот магазина на aiogram 3.x с каталогом из 3 товаров, корзиной и inline-кнопками.',
                completionPercent: 30,
                whatIsImplemented: ['/start + приветствие', 'Каталог (3 товара) с inline-кнопками', 'Добавление в корзину', 'Просмотр корзины', '/help'],
                whatIsLeft: ['Оплата', 'Админ-панель', 'Реальная БД', 'Рассылки', 'Статистика'],
                demoInstructions: 'Бот запущен в тестовом режиме: @demo_shop_bot',
            };
        }
        if (this.matchesAny(text, ['помощник', 'faq', 'поддержк', 'support'])) {
            return {
                type: 'helper-bot',
                files: new Map(),
                description: 'Telegram-бот помощник на aiogram 3.x с FAQ, тикетами и автоответами.',
                completionPercent: 30,
                whatIsImplemented: ['/start', '/help', 'FAQ inline-меню (5 вопросов)', 'Создание тикета', 'Команда /status'],
                whatIsLeft: ['AI-ответы', 'База знаний', 'Интеграция с CRM', 'Статистика тикетов'],
            };
        }
        // Дефолтный прототип для любого бота
        return {
            type: 'generic-bot',
            files: new Map(),
            description: 'Базовый Telegram-бот на aiogram 3.x с продакшн-структурой и 3 рабочими командами.',
            completionPercent: 25,
            whatIsImplemented: ['/start с приветствием', '/help с inline-кнопками', 'Базовая FSM-структура', 'Продакшн-структура проекта'],
            whatIsLeft: ['Основная бизнес-логика', 'БД', 'Деплой', 'Документация'],
        };
    }
    // =========================================================
    // WHY ME
    // =========================================================
    explainWhyMe(job) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        const points = [];
        points.push('Опыт разработки 10+ Telegram-ботов (магазины, CRM, парсеры, AI-ассистенты)');
        if (this.matchesAny(text, ['aiogram'])) {
            points.push('Работаю с aiogram 3.x с момента релиза, знаю все нюансы FSM и middleware');
        }
        if (this.matchesAny(text, ['оплат', 'платёж'])) {
            points.push('Опыт интеграции Telegram Payments + ЮKassa — знаю подводные камни с pre_checkout_query');
        }
        points.push('Использую AI-инструменты для ускорения — базовая структура генерируется автоматически');
        return `🎯 Почему я подхожу:\n${points.map(p => `• ${p}`).join('\n')}`;
    }
}
exports.BotAgent = BotAgent;
