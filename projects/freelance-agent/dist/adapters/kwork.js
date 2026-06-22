"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.KworkAdapter = void 0;
const base_1 = require("./base");
const scraper_1 = require("../services/scraper");
const helpers_1 = require("../utils/helpers");
/**
 * Адаптер для Kwork.ru (публичный доступ без авторизации)
 */
class KworkAdapter extends base_1.PlatformAdapter {
    name = 'kwork';
    baseUrl = 'https://kwork.ru';
    jobsUrl = 'https://kwork.ru/projects';
    selectors = {
        jobCard: '.wants-card, .want-card',
        title: 'a[href*="/projects/"]',
        // Описание: основной селектор .wants-card__description-text, fallback на другие
        description: '.wants-card__description-text, [class*="text"], [class*="desc"]',
        budget: '[class*="price"], [class*="budget"], .cost, [class*="cost"]',
        skills: '[class*="skill"], .tags__item',
        clientInfo: '[class*="author"], [class*="client"], [class*="username"]',
        postedAt: 'time, [class*="time"], [class*="date"]',
        proposalsCount: '.wants-content__info-item, .wants-card__responses, .projects__responses'
    };
    delays = {
        pageLoad: 3000,
        scroll: 4000,
        click: 600,
        betweenRequests: 4000
    };
    scraper;
    lastHtml = null;
    useFallback = false;
    constructor(browser, logger) {
        super(browser, logger);
        this.scraper = new scraper_1.ScraperService(logger);
    }
    /**
     * Перейти к поиску задач (публичная страница)
     */
    async navigateToJobs(filters) {
        this.logger.log('KWORK_NAVIGATE', 'Переход к поиску задач');
        const url = this.jobsUrl;
        // 1. Попытка через браузер
        const result = await this.browser.goto(url);
        if (!result.success) {
            this.logger.warn('KWORK_NAVIGATE', `Браузер не смог открыть страницу (${result.error}). Переходим в режим прямого парсинга.`);
            this.useFallback = true;
            // Загружаем через ScraperService
            this.lastHtml = await this.scraper.fetchHtml(url);
            return !!this.lastHtml;
        }
        this.useFallback = false;
        await this.sleep(this.delays.pageLoad);
        this.logger.log('KWORK_NAVIGATE', `URL: ${url} (Browser mode)`);
        return true;
    }
    /**
     * Извлечь список задач
     *
     * КЛЮЧЕВОЕ РЕШЕНИЕ: Вместо клика по "Показать полностью" (который падает в цикле),
     * извлекаем textContent напрямую из скрытого div — textContent работает даже
     * для элементов с display:none. Это обходит проблему с перерисовкой DOM после клика.
     */
    async extractJobs() {
        this.logger.log('KWORK_EXTRACT', `Начало извлечения задач (${this.useFallback ? 'Fallback mode' : 'Browser mode'})`);
        if (this.useFallback) {
            return this.extractJobsDirect();
        }
        const jobs = [];
        const page = this.browser.getPage();
        if (!page) {
            this.logger.warn('KWORK_EXTRACT', 'Страница браузера не доступна, переходим на Fallback');
            this.useFallback = true;
            this.lastHtml = await this.scraper.fetchHtml(this.jobsUrl);
            return this.extractJobsDirect();
        }
        try {
            // Прокрутка для загрузки всех задач
            await this.scrollToLoadMore(2);
            await this.sleep(this.delays.betweenRequests);
            // Batch-извлечение всех карточек через page.$$eval — быстрее и надёжнее
            const rawCards = await page.$$eval(this.selectors.jobCard, (cards, selectors) => {
                return cards.map((card) => {
                    // Заголовок и URL
                    const titleEl = card.querySelector(selectors.title);
                    const title = titleEl?.textContent?.trim() || '';
                    const url = titleEl?.getAttribute('href') || '';
                    // Описание
                    const descEl = card.querySelector(selectors.description);
                    const description = descEl?.textContent?.trim() || '';
                    // Бюджет
                    const budgetEl = card.querySelector(selectors.budget);
                    const budgetText = budgetEl?.textContent?.trim() || '';
                    // Навыки/теги
                    const skillEls = card.querySelectorAll(selectors.skills);
                    const skills = Array.from(skillEls).map(el => el.textContent?.trim() || '').filter(Boolean);
                    // Клиент
                    const clientEl = card.querySelector(selectors.clientInfo);
                    const clientName = clientEl?.textContent?.trim() || '';
                    // Дата (на Kwork в списке часто нет даты, ищем любые индикаторы времени)
                    const timeEl = card.querySelector(selectors.postedAt) || card.querySelector('.project-card__time');
                    const postedAtText = timeEl?.textContent?.trim() || '';
                    // Отклики (сначала ищем по тексту "Предложений: N", т.к. классы меняются)
                    const fullText = card.textContent || '';
                    const pMatch = fullText.match(/(?:предложени|отклик).*?(\d+)/i);
                    let proposalsText = pMatch ? pMatch[1] : '';
                    if (!proposalsText) {
                        const proposalsEl = card.querySelector(selectors.proposalsCount);
                        proposalsText = proposalsEl?.parentElement?.textContent?.trim() || proposalsEl?.textContent?.trim() || '';
                    }
                    // Вложения
                    const attachmentEls = card.querySelectorAll('a[href*="download"], [class*="file"] a, [class*="attachment"] a');
                    const attachmentUrls = Array.from(attachmentEls)
                        .map(el => el.href)
                        .filter(href => href && (href.includes('download') || href.match(/\.(pdf|png|jpg|jpeg|docx)$/i)));
                    const hasAttachments = attachmentUrls.length > 0;
                    // Проверка на закрытость (наличие кнопки "Опубликовать похожий проект")
                    const isClosed = card.textContent?.includes('Опубликовать похожий проект') || false;
                    return { title, url, description, budgetText, skills, clientName, postedAtText, proposalsText, hasAttachments, attachmentUrls, isClosed };
                });
            }, this.selectors);
            return this.processRawJobs(rawCards.filter(c => !c.isClosed));
        }
        catch (error) {
            this.logger.error('KWORK_EXTRACT', error);
            return [];
        }
    }
    /**
     * Извлечение без внешних библиотек (через регулярки и split)
     */
    async extractJobsDirect() {
        if (!this.lastHtml) {
            this.lastHtml = await this.scraper.fetchHtml(this.jobsUrl);
        }
        if (!this.lastHtml)
            return [];
        try {
            this.logger.log('KWORK_EXTRACT_DIRECT', 'Парсинг HTML вручную');
            const rawCards = [];
            // Попытка извлечь данные из JSON (window.stateData) - самый надежный способ
            const stateDataMatch = this.lastHtml.match(/window\.stateData\s*=\s*({[\s\S]+?});/i);
            if (stateDataMatch) {
                try {
                    const state = JSON.parse(stateDataMatch[1]);
                    const data = state.wantsListData?.pagination?.data || state.wants || [];
                    if (Array.isArray(data) && data.length > 0) {
                        this.logger.log('KWORK_EXTRACT_DIRECT', `Найдено ${data.length} проектов через JSON`);
                        for (const item of data) {
                            rawCards.push({
                                title: item.name || item.title || '',
                                url: item.id ? `https://kwork.ru/projects/${item.id}` : '',
                                description: item.description || '',
                                budgetText: item.priceLimit || item.price || '',
                                skills: [], // В JSON навыки могут быть в другом месте, пока пусто
                                clientName: item.user?.username || 'Client',
                                postedAtText: item.date_create || '',
                                proposalsText: item.getWantsActiveCount || '0',
                                hasAttachments: (item.files && item.files.length > 0),
                                attachmentUrls: item.files?.map((f) => f.url) || [],
                                isClosed: item.status === 'closed'
                            });
                        }
                        return this.processRawJobs(rawCards.filter(c => !c.isClosed));
                    }
                }
                catch (jsonErr) {
                    this.logger.warn('KWORK_EXTRACT_DIRECT', 'Ошибка парсинга JSON window.stateData, перехожу к regex');
                }
            }
            this.logger.log('KWORK_EXTRACT_DIRECT', 'Переход к парсингу по регулярным выражениям');
            // Ищем блоки карточек (используем split по уникальному классу карточки)
            const parts = this.lastHtml.split('class="wants-card');
            parts.shift(); // Первый кусок до первой карточки
            for (const part of parts) {
                // Заголовок и ссылка
                const titleMatch = part.match(/wants-card__header-title[^>]*><a[^>]*href="([^"]+)"[^>]*>([^<]+)/i);
                const url = titleMatch ? titleMatch[1] : '';
                const title = titleMatch ? titleMatch[2].trim() : '';
                if (!title)
                    continue;
                // Описание
                const descMatch = part.match(/wants-card__description-text[^>]*>([\s\S]+?)<\/div>/i);
                let description = descMatch ? descMatch[1].replace(/<[^>]+>/g, '').trim() : '';
                // Бюджет
                const budgetMatch = part.match(/wants-card__price[^>]*>([\s\S]+?)<\/div>/i) || part.match(/wants-card__budget[^>]*>([\s\S]+?)<\/div>/i);
                const budgetText = budgetMatch ? budgetMatch[1].replace(/<[^>]+>/g, '').trim() : '';
                // Отклики (сначала текстовый поиск)
                const strippedPart = part.replace(/<[^>]+>/g, ' ');
                const pMatch = strippedPart.match(/(?:предложени|отклик).*?(\d+)/i);
                let proposalsText = pMatch ? pMatch[1] : '';
                if (!proposalsText) {
                    const proposalsMatch = part.match(/wants-card__responses[^>]*>([\s\S]+?)<\/div>/i) || part.match(/wants-content__info-item[^>]*>([\s\S]+?)<\/div>/i);
                    proposalsText = proposalsMatch ? proposalsMatch[1].replace(/<[^>]+>/g, '').trim() : '';
                }
                // Навыки (ищем все теги)
                const skills = [];
                const skillsPart = part.match(/tags[^>]*>([\s\S]+?)<\/div>/i);
                if (skillsPart) {
                    const individualSkills = skillsPart[1].match(/tags__item[^>]*>([^<]+)/gi);
                    if (individualSkills) {
                        individualSkills.forEach(s => {
                            const cleaned = s.replace(/<[^>]+>/g, '').trim();
                            if (cleaned)
                                skills.push(cleaned);
                        });
                    }
                }
                rawCards.push({
                    title,
                    url,
                    description,
                    budgetText,
                    skills,
                    clientName: 'Client',
                    postedAtText: 'Недавно',
                    proposalsText,
                    hasAttachments: part.includes('attachment'),
                    attachmentUrls: [],
                    isClosed: part.includes('Опубликовать похожий проект')
                });
            }
            this.logger.log('KWORK_EXTRACT_DIRECT', `Успешно распарсено ${rawCards.length} карточек вручную`);
            return this.processRawJobs(rawCards.filter(c => !c.isClosed));
        }
        catch (error) {
            this.logger.error('KWORK_EXTRACT_DIRECT', error);
            return [];
        }
    }
    /**
     * Общая логика обработки сырых данных
     */
    processRawJobs(rawCards) {
        const jobs = [];
        this.logger.log('KWORK_PROCESS', `Обработка ${rawCards.length} сырых карточек`);
        const dynamicKeywords = [
            'разместить на сайт', 'размещение контента', 'выкладывать товар', 'наполнять сайт',
            'отвечать в мессенджерах', 'общение с клиентами', 'оператор чата', 'менеджер чата',
            'регистрация на сайтах', 'регистрироваться', 'ходить по сайтам', 'пройти опрос',
            'модерация', 'обзвон', 'холодные звонки', 'заполнение карточек',
            'инфографика', 'wildberries', 'ozon', 'маркетплейс', 'карточки товаров', 'вб', 'озон'
        ];
        for (const raw of rawCards) {
            try {
                if (!raw.title)
                    continue;
                // Исключаем закрытые задачи
                if (raw.isClosed) {
                    this.logger.log('KWORK_SKIP', `Пропуск закрытого проекта: ${raw.title}`);
                    continue;
                }
                // Исключаем динамические/операционные задачи
                const text = `${raw.title} ${raw.description}`.toLowerCase();
                const isDynamic = dynamicKeywords.some(kw => text.includes(kw));
                if (isDynamic) {
                    this.logger.log('KWORK_SKIP', `Пропуск динамической задачи: ${raw.title}`);
                    continue;
                }
                let description = raw.description
                    .replace(/\s*Показать полностью\s*/g, ' ')
                    .replace(/\s*Скрыть\s*/g, ' ')
                    .replace(/&nbsp;/g, ' ')
                    .replace(/&quot;/g, '"')
                    .replace(/&amp;/g, '&')
                    .replace(/\s+/g, ' ')
                    .trim();
                const budget = this.parseBudget(raw.budgetText);
                const postedAt = raw.postedAtText ? (0, helpers_1.parseRelativeTime)(raw.postedAtText) : undefined;
                const proposalsMatch = raw.proposalsText?.match(/(\d+)/);
                const proposalsCount = proposalsMatch ? parseInt(proposalsMatch[1]) : undefined;
                const job = {
                    platform: this.name,
                    url: (0, helpers_1.normalizeUrl)(raw.url, this.baseUrl),
                    title: raw.title.trim(),
                    description,
                    budget,
                    skills: raw.skills,
                    client: {
                        name: raw.clientName || undefined,
                        paymentVerified: false
                    },
                    proposalsCount: proposalsCount,
                    postedAt,
                    hasAttachments: raw.hasAttachments,
                    attachmentUrls: raw.attachmentUrls.map((url) => (0, helpers_1.normalizeUrl)(url, this.baseUrl)),
                    status: 'new'
                };
                jobs.push(job);
            }
            catch (error) {
                this.logger.error('KWORK_PROCESS_ERROR', error);
            }
        }
        return jobs;
    }
}
exports.KworkAdapter = KworkAdapter;
