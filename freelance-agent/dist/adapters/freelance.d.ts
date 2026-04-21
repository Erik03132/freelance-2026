import { PlatformAdapter, JobFilters, RawJob } from './base';
import { BrowserService } from '../services/browser';
import { Logger } from '../services/logger';
/**
 * Адаптер для Freelance.ru (публичный доступ без авторизации)
 */
export declare class FreelanceAdapter extends PlatformAdapter {
    name: string;
    baseUrl: string;
    jobsUrl: string;
    /**
     * 🏗 КОНСТИТУЦИЯ ОТБОРА ЛИДОВ (Sherlock Filter Rules)
     * Эти правила жестко запрещают попадание "мусорных" задач в воронку.
     */
    private forbiddenBadges;
    protected selectors: {
        jobCard: string;
        title: string;
        description: string;
        budget: string;
        skills: string;
        clientInfo: string;
        postedAt: string;
        proposalsCount: string;
    };
    protected delays: {
        pageLoad: number;
        scroll: number;
        click: number;
        betweenRequests: number;
    };
    private scraper;
    private lastHtml;
    private useFallback;
    constructor(browser: BrowserService, logger: Logger);
    /**
     * Перейти к поиску задач (публичная страница)
     */
    navigateToJobs(filters?: JobFilters): Promise<boolean>;
    /**
     * Извлечь список задач
     */
    extractJobs(): Promise<RawJob[]>;
    /**
     * Прямой парсинг через регулярные выражения
     */
    private extractJobsDirect;
}
//# sourceMappingURL=freelance.d.ts.map