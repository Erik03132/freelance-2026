"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FreelanceAdapter = void 0;
const base_1 = require("./base");
const scraper_1 = require("../services/scraper");
const helpers_1 = require("../utils/helpers");
/**
 * Адаптер для Freelance.ru (публичный доступ без авторизации)
 */
class FreelanceAdapter extends base_1.PlatformAdapter {
    name = 'freelance';
    baseUrl = 'https://freelance.ru';
    jobsUrl = 'https://freelance.ru/projects/';
    /**
     * 🏗 КОНСТИТУЦИЯ ОТБОРА ЛИДОВ (Sherlock Filter Rules)
     * Эти правила жестко запрещают попадание "мусорных" задач в воронку.
     */
    forbiddenBadges = [
        "Опубликовать похожий проект", // Фейки и дубликаты
        "Для теста", // Тестовые задания
        "Вакансия закрыта" // Неактуальные
    ];
    selectors = {
        jobCard: '.project-item-default-card',
        title: 'a[href*="/projects/"]',
        description: '.description, [class*="text"], .content',
        budget: '[class*="budget"], [class*="price"], .cost, [class*="sum"]',
        skills: '[class*="skill"], .tag',
        clientInfo: '[class*="author"], [class*="client"], [class*="name"], .project-owner',
        postedAt: 'time, [class*="time"], [class*="date"]',
        proposalsCount: '.post-card__proposals, [class*="response"], [class*="proposal"], [class*="bid"]'
    };
    delays = {
        pageLoad: 5000, // Freelance.ru медленнее загружается
        scroll: 2500,
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
        this.logger.log('FREELANCE_NAVIGATE', 'Переход к поиску задач');
        const url = this.jobsUrl;
        const result = await this.browser.goto(url);
        if (!result.success) {
            this.logger.warn('FREELANCE_NAVIGATE', `Браузер не смог открыть страницу (${result.error}). Переходим в режим прямого парсинга.`);
            this.useFallback = true;
            this.lastHtml = await this.scraper.fetchHtml(url);
            return !!this.lastHtml;
        }
        await this.sleep(this.delays.pageLoad);
        this.logger.log('FREELANCE_NAVIGATE', `URL: ${url}`);
        return true;
    }
    /**
     * Извлечь список задач
     */
    async extractJobs() {
        this.logger.log('FREELANCE_EXTRACT', 'Начало извлечения задач');
        if (this.useFallback) {
            return this.extractJobsDirect();
        }
        const jobs = [];
        try {
            // Прокрутка для загрузки всех задач
            await this.scrollToLoadMore(2);
            await this.sleep(this.delays.betweenRequests);
            // Получить все карточки задач
            const jobCards = await this.browser.extractAll(this.selectors.jobCard);
            this.logger.log('FREELANCE_EXTRACT', `Найдено карточек: ${jobCards.length}`);
            for (let i = 0; i < jobCards.length; i++) {
                try {
                    const cardIndex = i + 1;
                    const cardSelector = `${this.selectors.jobCard}:nth-child(${cardIndex})`;
                    // 🛡 ФИЛЬТР: Исключаем по "Конституции отбора"
                    const cardText = await this.browser.extractText(cardSelector);
                    if (this.forbiddenBadges.some(badge => cardText.includes(badge))) {
                        this.logger.log('FREELANCE_EXTRACT', `Пропущена задача по фильтру "Конституции"`);
                        continue;
                    }
                    // Извлечь заголовок
                    const titleElement = await this.browser.getPage()?.$(`${cardSelector} ${this.selectors.title}`);
                    if (!titleElement)
                        continue;
                    const title = await titleElement.textContent() || '';
                    const url = await titleElement.getAttribute('href') || '';
                    // Извлечь описание
                    const description = await this.browser.extractText(`${cardSelector} ${this.selectors.description}`);
                    // Извлечь бюджет
                    const budgetText = await this.browser.extractText(`${cardSelector} ${this.selectors.budget}`);
                    const budget = this.parseBudget(budgetText);
                    // Извлечь навыки
                    const skillsElements = await this.browser.extractAll(`${cardSelector} ${this.selectors.skills}`);
                    const skills = skillsElements.map(s => s.text).filter(Boolean);
                    // Извлечь информацию о клиенте
                    const clientName = await this.browser.extractText(`${cardSelector} ${this.selectors.clientInfo}`);
                    // Извлечь дату публикации
                    const postedAtText = await this.browser.extractText(`${cardSelector} ${this.selectors.postedAt}`);
                    const postedAt = postedAtText ? (0, helpers_1.parseRelativeTime)(postedAtText) : undefined;
                    // Извлечь количество откликов
                    const proposalsText = await this.browser.extractText(`${cardSelector} ${this.selectors.proposalsCount}`);
                    const proposalsCount = proposalsText ? parseInt(proposalsText.replace(/\D/g, '')) : undefined;
                    // Проверить наличие вложений
                    const hasAttachments = !!(await this.browser.getPage()?.$(`${cardSelector} .fa-paperclip, ${cardSelector} .attachments, ${cardSelector} [class*="file"]`));
                    const job = {
                        platform: this.name,
                        url: (0, helpers_1.normalizeUrl)(url, this.baseUrl),
                        title: title.trim(),
                        description: description.trim(),
                        budget,
                        skills,
                        client: {
                            name: clientName.trim() || undefined,
                            paymentVerified: false
                        },
                        proposalsCount,
                        postedAt,
                        hasAttachments,
                        status: 'new'
                    };
                    jobs.push(job);
                    this.logger.log('FREELANCE_EXTRACT', `Извлечена задача`, {
                        title: job.title,
                        budget: budget?.amount || budget?.min
                    });
                }
                catch (error) {
                    this.logger.error('FREELANCE_EXTRACT', error, { index: i });
                }
            }
            this.logger.log('FREELANCE_EXTRACT', `Извлечено ${jobs.length} задач`);
        }
        catch (error) {
            this.logger.error('FREELANCE_EXTRACT', error);
        }
        return jobs;
    }
    /**
     * Прямой парсинг через регулярные выражения
     */
    async extractJobsDirect() {
        if (!this.lastHtml) {
            this.lastHtml = await this.scraper.fetchHtml(this.jobsUrl);
        }
        if (!this.lastHtml)
            return [];
        this.logger.log('FREELANCE_EXTRACT_DIRECT', 'Парсинг HTML вручную (regex mode)');
        const jobs = [];
        // Ищем h2 с ссылками на проекты
        // <h2 class="title" title="...">
        //   <a href="/projects/nazvanie-proekta-12345.html" title="Разработка...">Название</a>
        // </h2>
        // На freelance.ru заголовок лежит в <h2> с ссылкой <a class="title"... или <h2 title=".."> <a ..>
        // Проще всего разбить по <div class="box-shadow" (каждая карточка)
        const blocks = this.lastHtml.split('class="box-shadow');
        blocks.shift(); // Убираем первую часть до карточек
        for (const block of blocks) {
            // 🛡 ФИЛЬТР: Исключаем по "Конституции отбора"
            if (this.forbiddenBadges.some(badge => block.includes(badge)))
                continue;
            // Ищем ссылку и название. Например: <a href="/projects/razrabotat-programmu-dlya-ucheta-1664751.html" ...
            // Или в markdown мы видели `[Разработать программу для учета](/projects/razrabotat-programmu-dlya-ucheta-1664751.html)`
            // Но мы парсим сырой HTML.
            const urlMatch = block.match(/href="(\/projects\/[^"']+\.html)"/);
            if (!urlMatch)
                continue;
            const url = urlMatch[1];
            // Ищем тайтл внутри этого a 
            const titleMatch = block.match(/href="[^"]+"[^>]*>([^<]+)<\/a>/is);
            const rawTitleMatch = block.match(/title="([^"]+)"/);
            const title = titleMatch ? titleMatch[1].trim() : (rawTitleMatch ? rawTitleMatch[1] : 'Без названия');
            // Описание обычно рядом, в div class="..."
            const descMatch = block.match(/href="[^"]+\.html"[^>]*>([^<]+)<\/a>(?:\s*<\/h2>)?\s*<[a-z][^>]*>([\s\S]+?)<\/(?:a|div|p)>/is);
            const descAttrMatch = block.match(/data-description="([^"]+)"/); // Иногда через аттрибуты
            // Альтернативный поиск описания (просто берем следующий кусок текста)
            const afterTitle = block.split(/<\/h2>|<\/a>/)[1] || '';
            const rawDescMatchStr = afterTitle.match(/<a[^>]*>(.+?)<\/a>/s) || afterTitle.match(/<div[^>]*>(.+?)<\/div>/s);
            let description = '';
            if (rawDescMatchStr) {
                description = rawDescMatchStr[1].replace(/<[^>]+>/g, '').trim();
            }
            else if (descMatch) {
                description = descMatch[2].replace(/<[^>]+>/g, '').trim();
            }
            if (!description && !title)
                continue;
            // Бюджет
            const budgetMatch = block.match(/cost[^>]*>([\s\S]+?)<\/div>/i) || block.match(/price[^>]*>([\s\S]+?)<\/div>/i) || block.match(/cost[^>]*>([\s\S]+?)<\/span>/i);
            const budgetText = budgetMatch ? budgetMatch[1].replace(/<[^>]+>/g, '').trim() : '';
            const job = {
                platform: this.name,
                url: (0, helpers_1.normalizeUrl)(url, this.baseUrl),
                title: title.trim(),
                description: description.substring(0, 1000).trim(), // Ограничим длину на всякий случай
                budget: this.parseBudget(budgetText),
                skills: [],
                client: { paymentVerified: false },
                proposalsCount: 0,
                status: 'new'
            };
            jobs.push(job);
        }
        this.logger.log('FREELANCE_EXTRACT_DIRECT', `Успешно распарсено ${jobs.length} карточек вручную`);
        return jobs;
    }
}
exports.FreelanceAdapter = FreelanceAdapter;
