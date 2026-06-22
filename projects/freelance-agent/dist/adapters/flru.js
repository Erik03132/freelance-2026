"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FLruAdapter = void 0;
const base_1 = require("./base");
const helpers_1 = require("../utils/helpers");
/**
 * Адаптер для FL.ru (публичный доступ без авторизации)
 */
class FLruAdapter extends base_1.PlatformAdapter {
    name = 'flru';
    baseUrl = 'https://www.fl.ru';
    jobsUrl = 'https://www.fl.ru/projects/';
    selectors = {
        jobCard: '.project-card, .vacancy-card',
        title: '.project-card__title a, .vacancy-card__title a',
        description: '.project-card__description, .vacancy-card__description',
        budget: '.project-card__budget, .vacancy-card__budget',
        skills: '.project-card__skills .tag, .vacancy-card__skills .tag',
        clientInfo: '.project-card__client, .vacancy-card__client',
        postedAt: '.project-card__time, .vacancy-card__time',
        proposalsCount: '.project-item__stats-item, .project-card__proposals, [class*="response"], [class*="proposal"]'
    };
    delays = {
        pageLoad: 3000, // FL.ru медленнее загружается
        scroll: 2500,
        click: 800,
        betweenRequests: 5000
    };
    constructor(browser, logger) {
        super(browser, logger);
    }
    /**
     * Перейти к поиску задач (публичная страница)
     */
    async navigateToJobs(filters) {
        this.logger.log('FLRU_NAVIGATE', 'Переход к поиску задач');
        const url = this.jobsUrl;
        const result = await this.browser.goto(url);
        if (!result.success) {
            this.logger.error('FLRU_NAVIGATE', new Error(result.error || 'Неизвестная ошибка'));
            if (result.suggestion) {
                console.log('\n' + result.suggestion + '\n');
            }
            return false;
        }
        await this.sleep(this.delays.pageLoad);
        this.logger.log('FLRU_NAVIGATE', `URL: ${url}`);
        return true;
    }
    /**
     * Извлечь список задач
     */
    async extractJobs() {
        this.logger.log('FLRU_EXTRACT', 'Начало извлечения задач');
        const jobs = [];
        try {
            // Прокрутка для загрузки всех задач
            await this.scrollToLoadMore(2);
            await this.sleep(this.delays.betweenRequests);
            // Получить все карточки задач
            const jobCards = await this.browser.extractAll(this.selectors.jobCard);
            this.logger.log('FLRU_EXTRACT', `Найдено карточек: ${jobCards.length}`);
            for (let i = 0; i < jobCards.length; i++) {
                try {
                    const cardIndex = i + 1;
                    const cardSelector = `${this.selectors.jobCard}:nth-child(${cardIndex})`;
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
                    // Извлечь количество откликов (через текст всей карточки)
                    const cardText = await this.browser.extractText(cardSelector);
                    let proposalsCount = undefined;
                    if (cardText) {
                        const match = cardText.match(/(?:отклик|предложени).*?(\d+)/i);
                        if (match)
                            proposalsCount = parseInt(match[1]);
                    }
                    if (proposalsCount === undefined) {
                        const proposalsText = await this.browser.extractText(`${cardSelector} ${this.selectors.proposalsCount}`);
                        if (proposalsText) {
                            const parsed = parseInt(proposalsText.replace(/\D/g, ''));
                            if (!isNaN(parsed))
                                proposalsCount = parsed;
                        }
                    }
                    if (proposalsCount !== undefined) {
                        this.logger.log('FLRU_EXTRACT', `Количество откликов: ${proposalsCount}`);
                    }
                    const job = {
                        platform: this.name,
                        url: (0, helpers_1.normalizeUrl)(url, this.baseUrl),
                        title: title.trim(),
                        description: description.trim(),
                        budget,
                        skills,
                        client: {
                            name: clientName.trim() || undefined,
                            paymentVerified: false // Без авторизации не видно
                        },
                        proposalsCount,
                        postedAt,
                        status: 'new'
                    };
                    jobs.push(job);
                    this.logger.log('FLRU_EXTRACT', `Извлечена задача`, {
                        title: job.title,
                        budget: budget?.amount || budget?.min
                    });
                }
                catch (error) {
                    this.logger.error('FLRU_EXTRACT', error, { index: i });
                }
            }
            this.logger.log('FLRU_EXTRACT', `Извлечено ${jobs.length} задач`);
        }
        catch (error) {
            this.logger.error('FLRU_EXTRACT', error);
        }
        return jobs;
    }
}
exports.FLruAdapter = FLruAdapter;
