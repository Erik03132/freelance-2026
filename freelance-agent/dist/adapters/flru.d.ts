import { PlatformAdapter, JobFilters, RawJob } from './base';
import { BrowserService } from '../services/browser';
import { Logger } from '../services/logger';
/**
 * Адаптер для FL.ru (публичный доступ без авторизации)
 */
export declare class FLruAdapter extends PlatformAdapter {
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
    constructor(browser: BrowserService, logger: Logger);
    /**
     * Перейти к поиску задач (публичная страница)
     */
    navigateToJobs(filters?: JobFilters): Promise<boolean>;
    /**
     * Извлечь список задач
     */
    extractJobs(): Promise<RawJob[]>;
}
//# sourceMappingURL=flru.d.ts.map