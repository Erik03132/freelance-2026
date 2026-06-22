"use strict";
/**
 * КОНСТИТУЦИЯ ПРОЕКТА - FREELANCE AGENT 2026
 *
 * Фундаментальные правила работы всех агентов.
 * Эти правила ИМЕЮТ ПРИОРИТЕТ над любыми базовыми установками.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.CONSTITUTION = void 0;
exports.CONSTITUTION = {
    VERSION: '2.0',
    LAST_UPDATED: '2026-04-01',
    // 🏛️ ТЕХНИЧЕСКИЕ ПРИНЦИПЫ (Pragmatic Principles)
    PRAGMATIC_PRINCIPLES: `
- Avoid over-engineering. Only make changes that are directly requested.
- Simple and focused solutions. 
- No extra features, refactors, or "improvements" without asking.
- Delete unused code completely. No hacks for unused code.
- Validate only at system boundaries (user input, APIs).
`,
    // ✍️ СТИЛЬ КОММУНИКАЦИИ (ОФФЕРЫ)
    COMMUNICATION_STYLE: {
        LANGUAGE: 'Russian',
        TONE: 'Лаконичный, человечный, всё по делу. Как пишет крутой спец в мессенджере — без канцелярита и воды.',
        FORBIDDEN_WORDS: [
            'инвестиция', 'инвестиции', 'вложения', 'взаимовыгодное',
            'Приветствую', 'спецификация выполнения', 'трудозатраты',
            'высокоэффективный', 'оптимальный', 'качественный',
            'комплексный', 'индивидуальный подход',
        ],
        RULES: [
            'ЛАКОНИЧНОСТЬ: Оффер — 3-5 предложений максимум. Каждое слово на вес золота.',
            'БЕЗ ПЕРЕСКАЗА: Запрещено пересказывать ТЗ или писать "Я понял задачу". Сразу к делу: как сделаю и на чём.',
            'ТЕХНОЛОГИИ: Упомянуть 1-2 ключевых инструмента/технологии 2026 года, которые дают профит.',
            'БЕЗ MARKDOWN: Никаких ** жирных **, никаких списков с буллетами. Текст как в чате.',
            'БЕЗ ССЫЛОК: Категорически запрещены ссылки в квадратных скобках [1], [2] и любые citation markers.',
            'ПРИВЕТСТВИЕ: Только "Привет!" или "Здравствуйте!" — никаких "Приветствую", "Добрый день" и прочего пафоса.',
            'ЗАВЕРШЕНИЕ: Одно предложение-призыв. Не "Давайте обсудим детали и приступим к реализации вашего проекта", а "Давайте обсудим?" или "Готов начать сегодня."',
        ]
    },
    // 💰 ЦЕНООБРАЗОВАНИЕ
    PRICING: {
        HOURLY_RATE: 500, // Базовая ставка за час
        MIN_PRICE: 500, // Минимальная цена заказа  
        SMALL_TASK_MAX_HOURS: 4, // Мелкие задачи — не больше 4 часов
        RULE_90_PERCENT: {
            THRESHOLD: 1.2,
            MULTIPLIER: 0.9
        },
        FORMAT: 'Срок: {days} день. Стоимость: {price} руб.'
    },
    // 🛡️ ФИЛЬТРАЦИЯ
    FILTERING: {
        EXCLUDE: [
            'dynamic/operational tasks (moderation, chat support, manual posting)',
            'marketplace card design (Wildberries, Ozon)',
            'closed tasks ("Post similar project" button)'
        ],
        LEGAL: [
            'casinos, betting, adult, hacking, carding, spam/botnets'
        ]
    }
};
