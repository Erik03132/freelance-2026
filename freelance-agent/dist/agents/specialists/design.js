"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DesignAgent = void 0;
const base_1 = require("./base");
const team_1 = require("../../constants/team");
class DesignAgent extends base_1.BaseSpecialist {
    agentType = 'design';
    agentName = team_1.TEAM_ROLES.REMBRANDT.NAME;
    emoji = '🎨';
    expertise = team_1.TEAM_ROLES.REMBRANDT.EXPERTISE;
    supportedCategories = [
        'design_ui', 'web_frontend', 'mobile_app'
    ];
    capabilities = [
        {
            name: 'SVG Logo Sourcing',
            description: 'Поиск и интеграция официальных SVG-логотипов (svglogo.dev, simpleicons)',
            enabled: true,
        },
        {
            name: 'Moodboard Search',
            description: 'Анализ конкурентов и подбор референсов через Behance/Dribbble API',
            enabled: true,
        },
        {
            name: 'Stitch UI Generation',
            description: 'Мгновенная генерация прототипов экранов и дизайн-систем через Stitch MCP',
            mcpServer: 'StitchMCP',
            enabled: true,
        }
    ];
    recommendTechStack(job) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        const isSmallTask = this.matchesAny(text, ['баннер', 'логотип', 'картинка', 'banner', 'logo', 'background', 'соцсет', 'linkedin', 'vk', 'превью']);
        const stack = [];
        if (isSmallTask) {
            stack.push({ name: 'Figma + SVGLogo.dev', reason: 'Для мгновенного доступа к качественным векторным ассетам.' });
            stack.push({ name: 'Moodboard Research', reason: 'Анализ лучших мировых кейсов для формирования уникального стиля.' });
        }
        else {
            stack.push({ name: 'Figma + Stitch MCP', reason: 'Отраслевой стандарт + AI-автоматизация для сборки интерфейсов.' });
            stack.push({ name: 'Atomic Design System', reason: 'Методология создания масштабируемых интерфейсов.' });
        }
        return stack;
    }
    createPlan(job, techStack) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        const isSmallTask = this.matchesAny(text, ['баннер', 'логотип', 'картинка', 'banner', 'logo', 'background', 'соцсет', 'linkedin', 'vk', 'превью']);
        const steps = [];
        let order = 1;
        if (isSmallTask) {
            steps.push({
                order: order++,
                title: 'Концепт и референсы',
                description: 'Подбор стилистики, поиск визуальных образов и создание 2-3 черновых набросков.',
                deliverable: 'Мудборд и эскизы',
                estimatedHours: '1-2',
                rationale: 'Позволяет быстро согласовать направление и не тратить время на ненужную детализацию.',
                canAutomate: true,
                automationTool: 'AI Research'
            });
            steps.push({
                order: order++,
                title: 'Финальная отрисовка',
                description: 'Чистовая работа над макетом, работа с типографикой, цветом и финальная ретушь.',
                deliverable: 'Готовый баннер/логотип в нужных форматах (SVG, PNG, JPG)',
                estimatedHours: '2-4',
                rationale: 'Создание качественного визуального продукта, готового к публикации.',
                canAutomate: false
            });
        }
        else {
            // План для серьезных интерфейсов
            steps.push({
                order: order++,
                title: 'UX-исследование и CJM',
                description: 'Анализ конкурентов, проектирование путей пользователя и логики переходов.',
                deliverable: 'CJM + UX-прототип',
                estimatedHours: '4-8',
                rationale: 'Гарантирует, что продукт будет удобным, а не просто красивым.',
                canAutomate: false
            });
            steps.push({
                order: order++,
                title: 'UI-дизайн и Система',
                description: 'Разработка визуального стиля и создание библиотеки компонентов в Figma.',
                deliverable: 'Дизайн-макеты + UI Kit',
                estimatedHours: '12-20',
                rationale: 'Создание консистентного и масштабируемого дизайна.',
                canAutomate: true,
                automationTool: 'Stitch MCP'
            });
            steps.push({
                order: order++,
                title: 'Интерактив и Передача',
                description: 'Сборка кликабельного прототипа и подготовка спецификаций для разработки.',
                deliverable: 'Интерактивный прототип + Handover',
                estimatedHours: '4-6',
                rationale: 'Упрощает реализацию и тестирование гипотез до написания кода.',
                canAutomate: true,
                automationTool: 'Stitch Prototypes'
            });
        }
        return steps;
    }
    generateQuestions(job) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        const questions = [];
        questions.push('Кто ваш основной конкурент и чем ваш продукт должен выделяться визуально?');
        if (!this.matchesAny(text, ['брендбук', 'логотип', 'цвета'])) {
            questions.push('Есть ли готовый брендбук или предпочтения по цветовой палитре?');
        }
        questions.push('Какое ключевое действие должен совершить пользователь на главном экране (Conversion Goal)?');
        if (!this.matchesAny(text, ['wcag', 'доступность', 'accessibility'])) {
            questions.push('Насколько критично соответствие стандартам доступности (WCAG 2.1) для вашего проекта?');
        }
        questions.push('В каком сервисе/стеке планируется верстка? (Интеграция с Tailwind/Styled Components)');
        return questions.slice(0, 5);
    }
    specifyPrototype(job) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        // CRM / Dashboard
        if (this.matchesAny(text, ['dashboard', 'админ', 'лк', 'crm', 'панел'])) {
            return {
                type: 'stitch_dashboard_prototype',
                files: new Map(),
                description: 'Интерактивный прототип CRM-системы в Stitch с настроенной дизайн-системой.',
                mcpActions: [
                    {
                        server: 'StitchMCP',
                        tool: 'create_project',
                        arguments: { title: `CRM Dashboard for ${job.title}` },
                        purpose: 'Создание рабочего пространства проекта в Stitch'
                    },
                    {
                        server: 'StitchMCP',
                        tool: 'generate_screen_from_text',
                        arguments: { prompt: `Modern dark-themed CRM dashboard for ${job.title} with sidebar navigation, stat cards, and data table. Premium aesthetics, glassmorphism.` },
                        purpose: 'Генерация главного экрана дашборда'
                    }
                ],
                completionPercent: 35,
                whatIsImplemented: ['Dashboard Home', 'Navigation Sidebar', 'User Profile State', 'Color Tokens', 'Typography System'],
                whatIsLeft: ['Таблицы данных', 'Графики (recharts)', 'Формы редактирования', 'Мобильная версия'],
                demoInstructions: 'Прототип доступен для просмотра в Stitch/Figma (ссылка по запросу)'
            };
        }
        // Landing / Promo
        if (this.matchesAny(text, ['лендинг', 'landing', 'сайт', 'одностранич', 'промо'])) {
            return {
                type: 'stitch_landing_concept',
                files: new Map(),
                description: 'Высокоуровневый концепт главного экрана + UI-Kit основных элементов.',
                mcpActions: [
                    {
                        server: 'StitchMCP',
                        tool: 'create_project',
                        arguments: { title: `Landing Page: ${job.title}` },
                        purpose: 'Инициализация дизайн-проекта лендинга'
                    },
                    {
                        server: 'StitchMCP',
                        tool: 'generate_screen_from_text',
                        arguments: { prompt: `High-converting modern landing page for "${job.title}". Features: Hero section with CTA, features grid, social proof. Clean, premium typography, vibrant accent colors.` },
                        purpose: 'Сборка концепта главного экрана (Hero section)'
                    }
                ],
                completionPercent: 40,
                whatIsImplemented: ['Hero Section', 'Header/Footer', 'Button System', 'Grid Layout', 'Concept Visuals via AI'],
                whatIsLeft: ['Блок отзывов', 'Ценовые таблицы', 'Форма захвата', 'Контентные блоки'],
                demoInstructions: 'Демонстрация концепта через Stitch Shared Link'
            };
        }
        // Mobile App
        if (this.matchesAny(text, ['мобильн', 'app', 'ios', 'android', 'приложен'])) {
            return {
                type: 'stitch_mobile_screens',
                files: new Map(),
                description: 'Набор из 3-х ключевых экранов мобильного приложения в темной и светлой темах.',
                mcpActions: [
                    {
                        server: 'StitchMCP',
                        tool: 'create_project',
                        arguments: { title: `Mobile App: ${job.title}` },
                        purpose: 'Создание мобильного дизайн-проекта'
                    },
                    {
                        server: 'StitchMCP',
                        tool: 'generate_screen_from_text',
                        arguments: { prompt: `Premium iOS application design for ${job.title}. Screen: Main Feed with tab bar. Apple human interface guidelines, smooth gradients, rounded corners.`, deviceType: 'MOBILE' },
                        purpose: 'Генерация базового экрана приложения'
                    }
                ],
                completionPercent: 30,
                whatIsImplemented: ['Onboarding', 'Login/Register', 'Main Feed', 'Bottom Navigation', 'Dark/Light themes'],
                whatIsLeft: ['Настройки профиля', 'Уведомления', 'Полный User Flow', 'Анимации переходов'],
                demoInstructions: 'Запуск через Stitch Mobile Preview'
            };
        }
        return null;
    }
    explainWhyMe(job) {
        return `🎯 Почему я подхожу:
• Проектирую на основе данных и User Research, а не просто "красиво".
• Внедряю дизайн-системы, которые экономят разработчикам до 40% времени на вёрстке.
• Использую Stitch MCP для мгновенной сборки прототипов, что позволяет вам увидеть результат уже в первый день.
• **Прагматичный подход:** не усложняю интерфейс лишними элементами, фиксирую только то, что решит вашу задачу сейчас. Никакого овер-инжиниринга.`;
    }
}
exports.DesignAgent = DesignAgent;
