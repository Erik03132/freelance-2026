"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DataAgent = void 0;
const base_1 = require("./base");
const team_1 = require("../../constants/team");
class DataAgent extends base_1.BaseSpecialist {
    agentType = 'data';
    agentName = team_1.TEAM_ROLES.SHERLOCK.NAME + ' (Data)';
    emoji = '📊';
    expertise = team_1.TEAM_ROLES.SHERLOCK.EXPERTISE;
    supportedCategories = [
        'parsing_scraping', 'data_science', 'web_backend'
    ];
    capabilities = [
        {
            name: 'Browser Automation',
            description: 'Управление браузером для сложного парсинга SPA',
            mcpServer: 'BrowserUse MCP',
            enabled: false, // TODO: подключить
        },
        {
            name: 'Local Database',
            description: 'Сбор и анализ данных в локальной БД',
            mcpServer: 'SQLite MCP',
            enabled: true,
        },
        {
            name: 'Jupyter Exploration',
            description: 'Анализ данных (EDA) и тестирование моделей',
            mcpServer: 'Jupyter MCP',
            enabled: false, // TODO: подключить
        }
    ];
    recommendTechStack(job) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        const stack = [];
        // Базовый язык
        stack.push({ name: 'Python 3.12+', reason: 'Индустриальный стандарт для скрейпинга и Data Science. Богатая экосистема библиотек.' });
        // Парсинг
        if (this.matchesAny(text, ['парс', 'scrape', 'сбор', 'parsing'])) {
            if (this.matchesAny(text, ['spa', 'react', 'js', 'динамич'])) {
                stack.push({ name: 'Playwright / Selenium', reason: 'Способен выполнять рендер JavaScript и обходить сложные капчи.' });
            }
            else if (this.matchesAny(text, ['быстр', 'масштаб', 'много', 'поток'])) {
                stack.push({ name: 'Scrapy + aiohttp', reason: 'Асинхронный и высокопроизводительный движок для быстрого сбора миллионов записей.' });
            }
            else {
                stack.push({ name: 'BeautifulSoup4 + requests', reason: 'Для простых, легко поддающихся парсингу страниц.' });
            }
        }
        // Data Science
        if (this.matchesAny(text, ['machine learning', 'ml', 'модель', 'предсказ', 'классификац', 'data science'])) {
            stack.push({ name: 'Pandas & NumPy', reason: 'Для быстрой очистки, аггрегации и манипуляций с данными.' });
            if (this.matchesAny(text, ['нейросет', 'глубок', 'компьютерное зрение', 'cv', 'nlp'])) {
                stack.push({ name: 'PyTorch / TensorFlow', reason: 'Мощный фреймворк для обучения и инференса нейросетей.' });
            }
            else {
                stack.push({ name: 'Scikit-Learn', reason: 'Классическое ML: решающие деревья, регрессии, базовый NLP.' });
            }
        }
        // Хранение результатов
        if (this.matchesAny(text, ['база', 'бд'])) {
            stack.push({ name: 'PostgreSQL', reason: 'Безопасное и структурное хранение собранных результатов.' });
        }
        else {
            stack.push({ name: 'MongoDB', reason: 'Отлично подходит для неструктурированных JSON-данных при скрейпинге.' });
        }
        return stack;
    }
    createPlan(job, techStack) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        const steps = [];
        let order = 1;
        if (this.matchesAny(text, ['парс', 'сбор', 'scrape'])) {
            // Скрейпинг план
            steps.push({
                order: order++,
                title: 'Анализ источника и обход защит',
                description: 'Анализ структуры DOM, запросов API ресурса, подбор прокси и анти-детект решений.',
                deliverable: 'PoC скрипт на получение первого элемента',
                estimatedHours: '2-4 часа',
                rationale: 'Источники часто меняют структуру данных или банят IP. Тестовый скрипт подтвердит принципиальную возможность.',
                canAutomate: true,
                automationTool: 'BrowserUse MCP',
            });
            steps.push({
                order: order++,
                title: 'Разработка парсера',
                description: 'Написание основной логики обхода пагинации, обработки ошибок, автоматической выгрузки.',
                deliverable: 'Рабочий скрипт парсинга',
                estimatedHours: '5-12 часов',
                rationale: 'Обработка edge cases гарантирует безостановочность парсинга.',
                canAutomate: true,
                automationTool: 'Antigravity Code Gen',
            });
            steps.push({
                order: order++,
                title: 'Очистка (Data Cleaning) и Экспорт',
                description: 'Нормализация данных, удаление дубликатов, приведение к нужному формату (JSON, CSV, БД).',
                deliverable: 'Итоговый дамп данных',
                estimatedHours: '2-4 часа',
                rationale: 'Клиенту нужны чистые данные готовые для аналитики, а не "сырой" мусор из HTML.',
                canAutomate: true,
            });
        }
        else {
            // ML план
            steps.push({
                order: order++,
                title: 'Разведочный анализ (EDA) и предобработка',
                description: 'Анализ распределений, работа с пропусками, генерация признаков (Feature Engineering).',
                deliverable: 'Jupyter Notebook с EDA',
                estimatedHours: '4-8 часов',
                rationale: '"Garbage in, garbage out" — качество данных напрямую определяет качество модели.',
                canAutomate: false,
            });
            steps.push({
                order: order++,
                title: 'Обучение и валидация моделей',
                description: 'Выбор архитектуры, кросс-валидация, подбор гиперпараметров (Grid/Optuna), оценка метрик.',
                deliverable: 'Обученная модель (.pkl, .onnx)',
                estimatedHours: '10-25 часов',
                rationale: 'Сравнение 2-3 подходов позволяет найти оптимальный tradeoff между скоростью и качеством.',
                canAutomate: true,
            });
            steps.push({
                order: order++,
                title: 'Упаковка в API (Инференс)',
                description: 'Создание FastAPI сервиса или Docker контейнера для удобного запроса предсказаний.',
                deliverable: 'Контейнер / API endpoints',
                estimatedHours: '4-6 часов',
                rationale: 'Модель в ноутбуке бесполезна для бизнеса. Требуется API-обертка для внедрения.',
                canAutomate: true,
            });
        }
        return steps;
    }
    generateQuestions(job) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        const questions = [];
        if (this.matchesAny(text, ['парс', 'scrape'])) {
            questions.push('Есть ли ограничения по скорости сбора? (Можем парсить в 100+ потоков, нужно ли это?)');
            questions.push('Требуется ли регулярный запуск парсера (например, раз в день), или это одноразовая выгрузка?');
            if (!this.matchesAny(text, ['база', 'бд'])) {
                questions.push('В каком формате удобнее получить результат (Excel/CSV, JSON, загрузка сразу к вам в БД)?');
            }
        }
        if (this.matchesAny(text, ['ml', 'модель'])) {
            questions.push('Предоставите ли вы исторические данные для обучения или требуется сначала собрать датасет?');
            questions.push('Какая метрика качества является для вас ключевой? (Например: критичнее не допускать ложно-положительных срабатываний?)');
            questions.push('Как планируете использовать модель в продакшене (встроить на сервер, локальный запуск, API для микросервисов)?');
        }
        return questions.slice(0, 5);
    }
    specifyPrototype(job) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        if (this.matchesAny(text, ['парс', 'scrape'])) {
            return {
                type: 'scraper_poc',
                files: new Map(),
                description: 'Тестовый парсинг первых 10-50 записей с целевого источника.',
                completionPercent: 30,
                whatIsImplemented: ['Запрос к сайту', 'Обход базовой защиты', 'Парсинг 2-3 ключевых полей'],
                whatIsLeft: ['Полный масштаб', 'Сохранение в Файл', 'Прокси-ротация'],
                demoInstructions: 'Предоставлю тестовый CSV файл с результатами для проверки структуры.'
            };
        }
        return null;
    }
    explainWhyMe(job) {
        return `🎯 Почему я подхожу:
• Знаю как обходить сложнейшие защиты от ботов (Cloudflare, reCAPTCHA, Datadome).
• Пишу масштабируемый код: скрипты не падают на 10-м часе работы.
• Отлично разбираюсь в алгоритмах и математике ML — строю модели не вслепую.`;
    }
}
exports.DataAgent = DataAgent;
