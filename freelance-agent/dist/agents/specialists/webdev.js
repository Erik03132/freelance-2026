"use strict";
/**
 * 💻 WebDev Agent — Специалист по веб-разработке
 *
 * Full-stack разработчик с экспертизой в:
 * - Mobile: Flutter, Dart, React Native (planned)
 * - Frontend: React 19, Next.js 15, Vue 3, Tailwind CSS, shadcn/ui
 * - Backend: FastAPI, NestJS, Express, Prisma, Drizzle
 * - Database: PostgreSQL, MongoDB, Redis, SQLite, Supabase
 * - Deploy: Vercel, Railway, Docker, Nginx
 *
 * Прокачан знаниями из:
 * - bulletproof-react (архитектура React)
 * - fastapi-best-practices (паттерны FastAPI)
 * - create-t3-app (T3 stack)
 * - realworld spec (эталон CRUD API)
 *
 * MCP-сервисы:
 * - Stitch MCP: генерация UI-экранов
 * - GitHub MCP: хранение кода прототипов (planned)
 * - Supabase MCP: мгновенная БД (planned)
 * - Vercel MCP: деплой прототипов (planned)
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.WebDevAgent = void 0;
const base_1 = require("./base");
const team_1 = require("../../constants/team");
class WebDevAgent extends base_1.BaseSpecialist {
    agentType = 'webdev';
    agentName = team_1.TEAM_ROLES.BRIGADIER.NAME;
    emoji = '👷‍♂️';
    expertise = team_1.TEAM_ROLES.BRIGADIER.EXPERTISE;
    supportedCategories = [
        'web_fullstack', 'web_frontend', 'web_backend',
        'chrome_extension', 'mobile_app', 'desktop_app',
    ];
    capabilities = [
        {
            name: 'Bulletproof Architecture',
            description: 'Применение эталонных паттернов структуры проекта (React/Next.js)',
            enabled: true,
        },
        {
            name: 'High-Fi UI Synthesis',
            description: 'Сборка интерфейсов из премиальных блоков shadcn/ui и Magic UI',
            enabled: true,
        },
        {
            name: 'GitHub Integration',
            description: 'Push кода прототипа, чтение репозиториев и создание Pull Requests',
            mcpServer: 'GitHub MCP',
            enabled: true,
        },
        {
            name: 'Neon Serverless Postgres',
            description: 'Мгновенная Serverless PostgreSQL БД для прототипов',
            mcpServer: 'Neon MCP',
            enabled: true,
        },
        {
            name: 'Stitch UI Generation',
            description: 'Мгновенная генерация фронтенд прототипов',
            mcpServer: 'StitchMCP',
            enabled: true,
        },
        {
            name: 'Vercel Deploy',
            description: 'Мгновенный деплой прототипов',
            mcpServer: 'Vercel MCP',
            enabled: false, // TODO: подключить
        },
    ];
    // =========================================================
    // СТЕК ТЕХНОЛОГИЙ (с обоснованием)
    // =========================================================
    recommendTechStack(job) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        const stack = [];
        // --- Mobile (Flutter/React Native) ---
        const isMobile = this.matchesAny(text, ['flutter', 'dart', 'мобильн', 'ios', 'android', 'приложен', 'mobile']);
        if (isMobile) {
            if (this.matchesAny(text, ['flutter', 'dart'])) {
                stack.push({ name: 'Flutter 3.x (Stable)', reason: 'Кроссплатформенная разработка с одним кодовым фундаментом (Impeller).' });
                stack.push({ name: 'Dart', reason: 'Типизированный, быстрый язык с поддержкой асинхронности.' });
                stack.push({ name: 'Riverpod', reason: 'Стейт-менеджмент нового поколения: безопасен и тестируем.' });
                stack.push({ name: 'Dio + Retrofit', reason: 'Стандарт индустрии для работы с REST API во Flutter.' });
            }
            else if (this.matchesAny(text, ['react native'])) {
                stack.push({ name: 'React Native + Expo', reason: 'Быстрая разработка на JS/React с доступом к нативным функциям.' });
            }
            else {
                stack.push({ name: 'Flutter', reason: 'Оптимальный выбор для MVP: быстрее и дешевле нативной разработки.' });
            }
        }
        // --- Frontend (Browser) ---
        if (this.needsFrontend(text) && !isMobile) {
            // React vs Vue vs Angular
            if (this.matchesAny(text, ['vue', 'vuetify', 'quasar'])) {
                stack.push({ name: 'Vue 3 + Composition API', reason: 'Указан в ТЗ. Composition API обеспечивает лучшую типизацию и переиспользование логики' });
            }
            else if (this.matchesAny(text, ['angular'])) {
                stack.push({ name: 'Angular 17+', reason: 'Указан в ТЗ. Signals API + standalone components упрощают разработку' });
            }
            else {
                // React — по умолчанию
                if (this.matchesAny(text, ['seo', 'ssr', 'ssg', 'блог', 'landing', 'лендинг', 'next'])) {
                    stack.push({ name: 'Next.js 15 (App Router)', reason: 'Актуальный стандарт 2026 года для SEO и масштабируемости.' });
                    stack.push({ name: 'Bulletproof React Pattern', reason: 'Для масштабируемой архитектуры, которую легко поддерживать.' });
                }
                else {
                    stack.push({ name: 'React 19 + Vite', reason: 'Быстрая сборка, React Compiler и нативные Actions для веб-приложений.' });
                }
            }
            // TypeScript — всегда
            stack.push({ name: 'TypeScript', reason: 'Type safety снижает баги на 15-20% (исследования Microsoft). Autocompletion ускоряет разработку' });
            // Стилизация
            if (this.matchesAny(text, ['material', 'mui'])) {
                stack.push({ name: 'Material UI v5', reason: 'Указан в ТЗ. Готовые компоненты ускоряют разработку в 2-3 раза' });
            }
            else if (this.matchesAny(text, ['bootstrap'])) {
                stack.push({ name: 'Bootstrap 5', reason: 'Указан в ТЗ. Широкая экосистема и документация' });
            }
            else {
                stack.push({ name: 'Tailwind CSS + shadcn/ui', reason: 'Utility-first подход = быстрая вёрстка. shadcn/ui — красивые, доступные компоненты без зависимостей' });
            }
            // State management
            if (this.matchesAny(text, ['state', 'redux', 'store', 'хранилищ', 'глобальн'])) {
                stack.push({ name: 'Zustand', reason: 'Легче Redux (2KB vs 40KB), но такой же мощный. Минимальный boilerplate' });
            }
        }
        // --- Backend ---
        if (this.needsBackend(text)) {
            if (this.matchesAny(text, ['python', 'fastapi', 'django', 'flask'])) {
                if (this.matchesAny(text, ['django'])) {
                    stack.push({ name: 'Django 5 + DRF', reason: 'Указан в ТЗ. Батарейки включены: ORM, Auth, Admin из коробки' });
                }
                else {
                    stack.push({ name: 'FastAPI', reason: 'Async из коробки = высокая производительность. Автоматическая OpenAPI документация. Pydantic v2 для валидации' });
                    stack.push({ name: 'Pydantic v2', reason: 'Валидация данных в 5-50x быстрее v1. Type-safe сериализация' });
                }
            }
            else if (this.matchesAny(text, ['nestjs', 'nest'])) {
                stack.push({ name: 'NestJS', reason: 'Указан в ТЗ. Enterprise-grade: DI, Guards, Interceptors, модульность' });
            }
            else if (this.matchesAny(text, ['express'])) {
                stack.push({ name: 'Express.js', reason: 'Указан в ТЗ. Минималистичный, огромная экосистема middleware' });
            }
            else {
                // По умолчанию — выбираем по контексту
                if (this.matchesAny(text, ['node', 'javascript', 'typescript', 'js', 'ts'])) {
                    stack.push({ name: 'NestJS', reason: 'TypeScript фреймворк с DI и модулями — масштабируемая архитектура из коробки' });
                }
                else {
                    stack.push({ name: 'FastAPI', reason: 'Лучше Express по производительности в 3-5x. Автодокументация API через Swagger' });
                }
            }
        }
        // --- Database ---
        if (this.needsDatabase(text)) {
            if (this.matchesAny(text, ['mongodb', 'mongo', 'nosql'])) {
                stack.push({ name: 'MongoDB + Mongoose', reason: 'Указан в ТЗ. Гибкая схема для быстро меняющихся данных' });
            }
            else if (this.matchesAny(text, ['supabase'])) {
                stack.push({ name: 'Supabase (PostgreSQL + Auth + Storage)', reason: 'БД + авторизация + файловое хранилище в одном сервисе. Бесплатный tier для MVP' });
            }
            else {
                stack.push({ name: 'PostgreSQL', reason: 'Надёжная, ACID-совместимая БД. JSON-поддержка, full-text search из коробки' });
            }
            // ORM
            if (this.matchesAny(text, ['prisma'])) {
                stack.push({ name: 'Prisma ORM', reason: 'Type-safe запросы, автомиграции, визуальный GUI' });
            }
            else if (this.matchesAny(text, ['python', 'fastapi', 'django'])) {
                stack.push({ name: 'SQLAlchemy 2.0', reason: 'Стандарт ORM для Python. Async поддержка, мощный query builder' });
            }
            else {
                stack.push({ name: 'Drizzle ORM', reason: 'Лёгкий (6KB), SQL-like синтаксис, отличная TypeScript интеграция. Быстрее Prisma в runtime' });
            }
        }
        // --- Auth ---
        if (this.matchesAny(text, ['авториз', 'auth', 'jwt', 'login', 'регистрац', 'oauth'])) {
            if (this.matchesAny(text, ['next', 'nextjs'])) {
                stack.push({ name: 'NextAuth.js v5', reason: 'OAuth из коробки (Google, GitHub, etc.). Session management встроен в Next.js' });
            }
            else if (this.matchesAny(text, ['python', 'fastapi'])) {
                stack.push({ name: 'JWT (python-jose) + passlib', reason: 'Стандарт для FastAPI. Stateless авторизация — масштабируется без сервера сессий' });
            }
            else {
                stack.push({ name: 'JWT авторизация', reason: 'Stateless — масштабируется горизонтально. Стандарт для REST API' });
            }
        }
        // Fallback
        if (stack.length === 0) {
            stack.push({ name: 'TypeScript', reason: 'Универсальный язык для frontend и backend' });
            stack.push({ name: 'React 18 + Vite', reason: 'Самый популярный UI-фреймворк, огромная экосистема' });
        }
        return stack;
    }
    // =========================================================
    // ПЛАН РЕАЛИЗАЦИИ (с обоснованиями)
    // =========================================================
    createPlan(job, techStack) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        const steps = [];
        let order = 1;
        const isSmallFix = this.matchesAny(text, ['исправить', 'поправить', 'баг', 'кнопка', 'форма', 'скрипт', 'ошибка', 'fix', 'bug', 'small']);
        // --- Этап 1: Проектирование или Анализ ---
        if (isSmallFix) {
            steps.push({
                order: order++,
                title: 'Анализ и локализация',
                description: 'Изучение текущего кода, поиск причин ошибки и определение оптимального способа исправления без вреда для общего функционала.',
                deliverable: 'План исправления',
                estimatedHours: '1-2',
                rationale: 'Быстрый анализ позволяет устранить причину, а не следствие ошибки.',
                canAutomate: false,
            });
        }
        else {
            steps.push({
                order: order++,
                title: 'Проектирование архитектуры',
                description: 'Структура данных (ERD), API-контракты, wireframes основных экранов.',
                deliverable: 'Схема архитектуры + ERD + API spec',
                estimatedHours: '3-5',
                rationale: 'Без чёткой архитектуры код будет переписываться 2-3 раза. Проектирование экономит 30-40% времени разработки.',
                canAutomate: false,
            });
        }
        if (isSmallFix) {
            steps.push({
                order: order++,
                title: 'Реализация и проверка',
                description: 'Внесение необходимых правок в код, функциональное тестирование и проверка кроссбраузерности.',
                deliverable: 'Исправленный функционал',
                estimatedHours: '2-4',
                rationale: 'Гарантия того, что правка работает и не создала новых проблем в других частях системы.',
                canAutomate: true,
            });
            return steps; // Для правок этого достаточно
        }
        // --- Backend ---
        if (this.needsBackend(text)) {
            steps.push({
                order: order++,
                title: 'Настройка проекта и моделей данных',
                description: `Инициализация ${techStack[0]?.name || 'проекта'}, структура папок, модели данных, миграции.`,
                deliverable: 'Рабочий scaffold с моделями и первой миграцией',
                estimatedHours: '2-4 часа',
                rationale: 'Начинаем с данных, потому что API и UI строятся поверх модели данных. Все зависит от правильной структуры.',
                canAutomate: true,
                automationTool: 'Antigravity code generation',
            });
            steps.push({
                order: order++,
                title: 'Реализация API endpoints',
                description: 'CRUD операции, валидация входных данных, обработка ошибок, пагинация.',
                deliverable: 'Рабочее API с Swagger-документацией',
                estimatedHours: '6-10 часов',
                rationale: 'API-first подход: фронтенд сразу работает с реальными данными, а не моками.',
                canAutomate: true,
                automationTool: 'Antigravity + Swagger автогенерация',
            });
            if (this.matchesAny(text, ['авториз', 'auth', 'jwt', 'login', 'регистрац'])) {
                steps.push({
                    order: order++,
                    title: 'Система авторизации',
                    description: 'Регистрация, логин, JWT токены (access + refresh), защита endpoints, роли.',
                    deliverable: 'Полная auth-система с тестами',
                    estimatedHours: '4-6 часов',
                    rationale: 'Авторизация — фундамент безопасности. Лучше сделать правильно сразу, чем переделывать.',
                    canAutomate: true,
                    automationTool: 'Antigravity (boilerplate auth)',
                });
            }
        }
        // --- Frontend ---
        if (this.needsFrontend(text)) {
            steps.push({
                order: order++,
                title: 'UI-компоненты и дизайн-система',
                description: 'Базовые компоненты (Button, Input, Card, Modal), цветовая палитра, typography.',
                deliverable: 'Библиотека UI-компонентов',
                estimatedHours: '3-5 часов',
                rationale: 'Переиспользуемые компоненты ускоряют дальнейшую разработку в 3-4 раза и гарантируют единый стиль.',
                canAutomate: true,
                automationTool: 'Stitch MCP (дизайн-система) + shadcn/ui',
            });
            steps.push({
                order: order++,
                title: 'Реализация страниц и навигации',
                description: 'Основные экраны, роутинг, лейауты, responsive вёрстка.',
                deliverable: 'Рабочий UI со всеми страницами',
                estimatedHours: '6-10 часов',
                rationale: 'Страницы строим на готовых компонентах — быстрая сборка из проверенных блоков.',
                canAutomate: true,
                automationTool: 'Stitch MCP (генерация экранов)',
            });
            if (this.needsBackend(text)) {
                steps.push({
                    order: order++,
                    title: 'Интеграция Frontend ↔ Backend',
                    description: 'API-клиент, обработка loading/error/empty состояний, кэширование запросов.',
                    deliverable: 'Полностью рабочее приложение',
                    estimatedHours: '4-6 часов',
                    rationale: 'Отдельный этап, потому что UX зависит от правильной обработки крайних случаев (loading, error, empty, offline).',
                    canAutomate: false,
                });
            }
        }
        // --- Mobile Apps ---
        if (this.matchesAny(text, ['flutter', 'dart', 'мобильн', 'mobile'])) {
            steps.push({
                order: order++,
                title: 'Архитектура мобильного приложения',
                description: 'Настройка Clean Architecture, слои Data/Domain/Presentation, инициализация DI (get_it/riverpod).',
                deliverable: 'Scaffold проекта с настроенной архитектурой',
                estimatedHours: '4-6 часов',
                rationale: 'Без чёткого разделения слоёв мобильное приложение становится невозможно поддерживать при росте фич.',
                canAutomate: true,
            });
            steps.push({
                order: order++,
                title: 'Разработка UI-кита и экранов',
                description: 'Вёрстка виджетов по макетам, настройка темы (Material 3), адаптация под разные размеры экранов.',
                deliverable: 'Набор готовых экранов с навигацией',
                estimatedHours: '10-20 часов',
                rationale: 'UI в мобилках — это 70% успеха. Используем нативные паттерны (iOS/Android) для лучшего UX.',
                canAutomate: false,
            });
            if (this.needsBackend(text)) {
                steps.push({
                    order: order++,
                    title: 'Интеграция с API и кэширование',
                    description: 'Реализация репозиториев, маппинг JSON в Dart-объекты, локальное хранилище (Hive/Isar) для оффлайн-режима.',
                    deliverable: 'Рабочая бизнес-логика с сетевыми запросами',
                    estimatedHours: '8-12 часов',
                    rationale: 'В мобильных приложениях критично обрабатывать отсутствие интернета и кэшировать данные для скорости.',
                    canAutomate: true,
                });
            }
            steps.push({
                order: order++,
                title: 'Сборка и публикация (TestFlight/App Distribution)',
                description: 'Настройка сертификатов, иконок, сплеш-скринов, сборка APK/AAB и IPA для тестирования.',
                deliverable: 'Ссылка на билд в TestFlight / Firebase App Distribution',
                estimatedHours: '4-6 часов',
                rationale: 'Клиент должен как можно раньше потрогать продукт на реальном устройстве.',
                canAutomate: true,
            });
        }
        // --- Chrome Extension ---
        if (this.matchesAny(text, ['chrome extension', 'расширение', 'manifest'])) {
            steps.push({
                order: order++,
                title: 'Manifest V3 и архитектура',
                description: 'manifest.json, permissions, content scripts, service worker.',
                deliverable: 'Рабочий scaffold расширения',
                estimatedHours: '2-3 часа',
                rationale: 'Manifest V3 — новый стандарт Chrome, имеет ограничения vs V2 (background → service worker), лучше учесть сразу.',
                canAutomate: true,
                automationTool: 'Antigravity code generation',
            });
        }
        // --- Тестирование ---
        steps.push({
            order: order++,
            title: 'Тестирование и баг-фикс',
            description: 'Функциональное тестирование, edge cases, кроссбраузерная проверка.',
            deliverable: 'Стабильная версия',
            estimatedHours: '3-5 часов',
            rationale: 'Тестирование на ранней стадии дешевле в 5-10 раз, чем фикс багов после релиза.',
            canAutomate: true,
            automationTool: 'Playwright (E2E тесты)',
        });
        // --- Документация ---
        steps.push({
            order: order++,
            title: 'Документация и передача',
            description: 'README с инструкцией по запуску, .env.example, комментарии в коде.',
            deliverable: 'Проект с полной документацией',
            estimatedHours: '2-3 часа',
            rationale: 'Хорошая документация = заказчик может самостоятельно поддерживать проект. Повышает доверие и ведёт к повторным заказам.',
            canAutomate: true,
            automationTool: 'Antigravity (README generation)',
        });
        return steps;
    }
    // =========================================================
    // УТОЧНЯЮЩИЕ ВОПРОСЫ (экспертные)
    // =========================================================
    generateQuestions(job) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        const questions = [];
        // Дизайн
        if (!this.matchesAny(text, ['figma', 'макет', 'дизайн', 'xd', 'sketch'])) {
            questions.push('Есть ли готовый дизайн/макет? Если нет — могу подготовить мокапы для согласования перед разработкой.');
        }
        // Хостинг/деплой
        if (!this.matchesAny(text, ['деплой', 'хостинг', 'сервер', 'vercel', 'aws', 'docker'])) {
            questions.push('Где планируется размещение? Могу задеплоить на Vercel (бесплатный tier) или подготовить Docker для вашего сервера.');
        }
        // Интеграции
        if (this.matchesAny(text, ['интеграци', 'api', 'внешн'])) {
            if (!this.matchesAny(text, ['документаци', 'api doc', 'swagger'])) {
                questions.push('Есть ли документация по внешним API, с которыми нужна интеграция?');
            }
        }
        // Мобильная адаптация
        if (!this.matchesAny(text, ['мобильн', 'адаптив', 'responsive', 'mobile'])) {
            if (this.needsFrontend(text)) {
                questions.push('Нужна ли мобильная адаптация (responsive)? Рекомендую — 60%+ трафика сейчас с мобильных устройств.');
            }
        }
        // SEO
        if (this.matchesAny(text, ['лендинг', 'сайт', 'landing', 'блог'])) {
            if (!this.matchesAny(text, ['seo'])) {
                questions.push('Нужна ли SEO-оптимизация? Если да — рекомендую SSR (Next.js) вместо SPA для лучшей индексации.');
            }
        }
        // Deadline
        if (!this.matchesAny(text, ['срок', 'дедлайн', 'deadline'])) {
            questions.push('Есть ли жёсткий дедлайн? Это поможет правильно расставить приоритеты в плане.');
        }
        questions.push('Остались ли требования, не отражённые в описании?');
        return questions.slice(0, 5);
    }
    // =========================================================
    // ПРОТОТИП
    // =========================================================
    specifyPrototype(job) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        // Лендинг
        if (this.matchesAny(text, ['лендинг', 'landing', 'промо', 'одностранич'])) {
            return {
                type: 'landing',
                files: new Map(),
                description: 'Next.js лендинг с hero-секцией, блоком преимуществ, CTA и футером. Адаптивный, с анимациями.',
                completionPercent: 35,
                whatIsImplemented: ['Hero секция', 'Блок преимуществ (3 карточки)', 'CTA кнопка', 'Responsive вёрстка', 'Базовые анимации'],
                whatIsLeft: ['Контент из ТЗ', 'Формы обратной связи', 'Аналитика', 'SEO мета-теги'],
                demoInstructions: 'Демо будет доступно по ссылке после запуска',
            };
        }
        // Dashboard / Админка
        if (this.matchesAny(text, ['dashboard', 'админ', 'панел', 'crm', 'cms'])) {
            return {
                type: 'dashboard',
                files: new Map(),
                description: 'React dashboard с sidebar-навигацией, карточками статистики, таблицей данных и графиками.',
                mcpActions: [
                    {
                        server: 'mcp-server-neon',
                        tool: 'create_project',
                        arguments: { name: `db-${job.title}`.replace(/[^a-z0-9]/gi, '-').toLowerCase() },
                        purpose: 'Подготовка облачной базы данных Neon (Postgres)'
                    },
                    {
                        server: 'StitchMCP',
                        tool: 'generate_screen_from_text',
                        arguments: { prompt: `React Dashboard component with sidebar for ${job.title}. Tailwind CSS integration.` },
                        purpose: 'Генерация фронтенд-интерфейса дашборда'
                    }
                ],
                completionPercent: 30,
                whatIsImplemented: ['Sidebar с навигацией', 'Header + поиск', '4 stat-карточки', 'Таблица с пагинацией', 'Мок-данные'],
                whatIsLeft: ['Реальные данные из API', 'Графики', 'Фильтрация', 'Экспорт', 'Авторизация'],
                demoInstructions: 'Демо будет доступно по ссылке после запуска',
            };
        }
        // API
        if (this.matchesAny(text, ['api', 'backend', 'бэкенд', 'fastapi', 'rest'])) {
            return {
                type: 'api',
                files: new Map(),
                description: 'FastAPI приложение с 5 CRUD endpoints, Swagger-документацией и Docker.',
                completionPercent: 30,
                whatIsImplemented: ['Структура проекта', '5 CRUD endpoints', 'Pydantic модели', 'Swagger UI', 'Docker Compose'],
                whatIsLeft: ['Авторизация', 'Бизнес-логика', 'Тесты', 'Продакшн-конфиг'],
                demoInstructions: 'Swagger UI доступен по /docs',
            };
        }
        // E-commerce
        if (this.matchesAny(text, ['магазин', 'shop', 'e-commerce', 'ecommerce', 'каталог', 'корзин'])) {
            return {
                type: 'ecommerce',
                files: new Map(),
                description: 'Next.js магазин с каталогом товаров, фильтрами, карточкой товара и корзиной.',
                completionPercent: 25,
                whatIsImplemented: ['Каталог (grid)', '3 тестовых товара', 'Карточка товара', 'Корзина (localStorage)', 'Responsive'],
                whatIsLeft: ['Оплата', 'Личный кабинет', 'Admin-панель', 'Реальная БД', 'Поиск и фильтры'],
                demoInstructions: 'Демо будет доступно по ссылке после запуска',
            };
        }
        return null;
    }
    // =========================================================
    // WHY ME
    // =========================================================
    explainWhyMe(job) {
        return [
            '🎯 Почему я подхожу:',
            '• **Keep It Simple:** делаю ровно то, что просили, без лишних абстракций и овер-инжиниринга.',
            '• **Скорость:** использую стэки с мощной автоматизацией (FastAPI, Next.js), что дает быстрый результат.',
            '• **Надежность:** строгая валидация (Zod/Pydantic) только на входах в систему.',
            '• **Чистый результат:** если код не нужен для текущей задачи — его не будет в проекте. Без "планов на будущее".'
        ].join('\n');
    }
    // =========================================================
    // ВСПОМОГАТЕЛЬНЫЕ
    // =========================================================
    needsFrontend(text) {
        return this.matchesAny(text, [
            'react', 'vue', 'angular', 'next', 'nuxt', 'frontend', 'фронтенд',
            'интерфейс', 'лендинг', 'landing', 'сайт', 'страниц', 'компонент',
            'верстк', 'dashboard', 'ui', 'приложен',
        ]);
    }
    needsBackend(text) {
        return this.matchesAny(text, [
            'api', 'backend', 'бэкенд', 'бекенд', 'сервер', 'fastapi',
            'express', 'nestjs', 'django', 'flask', 'rest', 'graphql',
            'базу данных', 'бд', 'database', 'авториз', 'auth',
            'crud', 'endpoint', 'webhook',
        ]);
    }
    needsDatabase(text) {
        return this.matchesAny(text, [
            'postgresql', 'postgres', 'mysql', 'mongodb', 'mongo', 'sqlite',
            'database', 'бд', 'базу данных', 'хранени', 'crud', 'supabase',
            'firebase', 'prisma', 'orm',
        ]) || this.needsBackend(text);
    }
}
exports.WebDevAgent = WebDevAgent;
