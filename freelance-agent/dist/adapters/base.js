"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.PlatformAdapter = void 0;
/**
 * Базовый интерфейс адаптера платформы
 * Работает с публичными данными (без авторизации)
 */
class PlatformAdapter {
    browser;
    logger;
    selectors;
    delays;
    filters;
    constructor(browser, logger) {
        this.browser = browser;
        this.logger = logger;
        this.selectors = {
            jobCard: '',
            title: '',
            description: '',
            budget: '',
            skills: '',
            clientInfo: '',
            postedAt: '',
            proposalsCount: ''
        };
        this.delays = {
            pageLoad: 2000,
            scroll: 1500,
            click: 500,
            betweenRequests: 3000
        };
        this.filters = {
            minBudget: 0,
            categories: [],
            ignoreKeywords: [],
            limit: 50
        };
    }
    // ═══════════════════════════════════════════════════════════
    // ██  ЧЁРНЫЙ СПИСОК ЗАДАНИЙ — НЕ БЕРЁМ В РАБОТУ           ██
    // ═══════════════════════════════════════════════════════════
    /** Ключевые слова в заголовке/описании → задание пропускается */
    static BLACKLIST_KEYWORDS = [
        // Динамические задания (на связи, звонки, SMS)
        'отвечать на звонки', 'отвечать на сообщения', 'отвечать на смс',
        'быть на связи', 'поддержка в чате', 'оператор на телефон',
        'принимать звонки', 'обзвон', 'холодные звонки', 'теплые звонки',
        'диспетчер', 'call-центр', 'колл-центр', 'call центр',
        'ответы на отзывы', 'модерация чата',
        // Маркетплейсы — карточки товаров
        'карточк', 'wildberries', 'вайлдберриз', 'wb ',
        'ozon', 'озон', 'маркетплейс',
        'инфографика для', 'рич-контент',
        'заполнение карточек', 'оформление карточек',
        // Спам / шаблонные задания
        'опубликовать похожий проект',
        // Прочее нерелевантное
        'набор текста', 'транскрибация', 'расшифровка аудио',
        'перевод с ', 'перевод на ',
    ];
    /**
     * Проверяет, нужно ли пропустить задание (чёрный список)
     * Вызывается ПОСЛЕ извлечения, ПЕРЕД сохранением в БД
     */
    shouldSkipJob(title, description) {
        const text = `${title} ${description}`.toLowerCase();
        for (const keyword of PlatformAdapter.BLACKLIST_KEYWORDS) {
            if (text.includes(keyword.toLowerCase())) {
                return { skip: true, reason: `Чёрный список: "${keyword}"` };
            }
        }
        return { skip: false };
    }
    /**
     * Отфильтровать задания из чёрного списка
     * Вызывать после extractJobs()
     */
    filterJobs(jobs) {
        const before = jobs.length;
        const filtered = jobs.filter(job => {
            const check = this.shouldSkipJob(job.title, job.description);
            if (check.skip) {
                this.logger.log('FILTER_SKIP', `⛔ Пропущено: "${job.title.slice(0, 60)}..." — ${check.reason}`);
            }
            return !check.skip;
        });
        if (before !== filtered.length) {
            this.logger.log('FILTER', `Отфильтровано: ${before - filtered.length} из ${before} заданий`);
        }
        return filtered;
    }
    /**
     * Извлечь детали задачи (при необходимости)
     */
    async extractJobDetails(url) {
        // По умолчанию возвращаем пустой объект
        // Можно переопределить в адаптере для детального парсинга
        return {};
    }
    /**
     * Прокрутка для загрузки контента
     */
    async scrollToLoadMore(maxScrolls = 3) {
        let lastHeight = await this.browser.evaluate('() => document.body.scrollHeight');
        for (let i = 0; i < maxScrolls; i++) {
            await this.browser.scrollToEnd();
            await this.sleep(this.delays.scroll);
            const newHeight = await this.browser.evaluate('() => document.body.scrollHeight');
            if (newHeight === lastHeight)
                break;
            lastHeight = newHeight;
        }
    }
    /**
     * Задержка
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    /**
     * Извлечь бюджет из текста
     */
    parseBudget(budgetText) {
        if (!budgetText)
            return undefined;
        // "Договорная" или "По договорённости"
        if (budgetText.toLowerCase().includes('договорн') || budgetText.toLowerCase().includes('по договор')) {
            return {
                type: 'fixed',
                amount: undefined,
                currency: 'RUB'
            };
        }
        // Почасовая оплата: "1000-2000 ₽/час"
        const hourlyMatch = budgetText.match(/([\d\s,]+)\s*[-–—]\s*([\d\s,]+)\s*(₽|\$|€|RUB|USD|EUR|руб|Rub|руб\.|RUR)?\s*(\/\s*час|\/hr|в\s*час)?/i);
        if (hourlyMatch) {
            return {
                type: 'hourly',
                min: parseInt(hourlyMatch[1].replace(/[\s,]/g, '')),
                max: parseInt(hourlyMatch[2].replace(/[\s,]/g, '')),
                currency: this.normalizeCurrency(hourlyMatch[3] || 'RUB')
            };
        }
        // Фиксированная: "50000 ₽" или "$500" или "60 000 Руб"
        const fixedMatch = budgetText.match(/([\d\s,]+)\s*(₽|\$|€|RUB|USD|EUR|руб|Rub|руб\.|RUR)/i);
        if (fixedMatch) {
            return {
                type: 'fixed',
                amount: parseInt(fixedMatch[1].replace(/[\s,]/g, '')),
                currency: this.normalizeCurrency(fixedMatch[2])
            };
        }
        return undefined;
    }
    /**
     * Нормализовать валюту
     */
    normalizeCurrency(symbol) {
        const mapping = {
            '₽': 'RUB',
            '$': 'USD',
            '€': 'EUR',
            'RUB': 'RUB',
            'USD': 'USD',
            'EUR': 'EUR',
            'руб': 'RUB',
            'Rub': 'RUB',
            'руб.': 'RUB',
            'RUR': 'RUB'
        };
        return mapping[symbol] || mapping[symbol.toUpperCase()] || symbol.toUpperCase();
    }
    /**
     * Извлечь навыки из текста
     */
    extractSkillsFromText(text) {
        if (!text)
            return [];
        // Разбить по запятым, точкам с запятой
        const skills = text
            .split(/[,;]/)
            .map(s => s.trim())
            .filter(s => s.length > 1 && s.length < 50);
        return skills;
    }
}
exports.PlatformAdapter = PlatformAdapter;
