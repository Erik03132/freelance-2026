import { PlatformAdapter, JobFilters, RawJob } from './base';
import { BrowserService } from '../services/browser';
import { Logger } from '../services/logger';
/**
 * Адаптер для Kwork.ru (публичный доступ без авторизации)
 */
export declare class KworkAdapter extends PlatformAdapter {
    name: string;
    baseUrl: string;
    jobsUrl: string;
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
     *
     * КЛЮЧЕВОЕ РЕШЕНИЕ: Вместо клика по "Показать полностью" (который падает в цикле),
     * извлекаем textContent напрямую из скрытого div — textContent работает даже
     * для элементов с display:none. Это обходит проблему с перерисовкой DOM после клика.
     */
    extractJobs(): Promise<RawJob[]>;
    /**
     * Извлечение без внешних библиотек (через регулярки и split)
     */
    private extractJobsDirect;
    /**
     * Общая логика обработки сырых данных
     */
    private processRawJobs;
}
//# sourceMappingURL=kwork.d.ts.map