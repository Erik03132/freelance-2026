import { Logger } from './logger';
/**
 * Простое решение для скачивания HTML без браузера
 * (Используем нативный fetch из Node.js 18+)
 */
export declare class ScraperService {
    private logger;
    private userAgent;
    constructor(logger?: Logger);
    /**
     * Получить HTML-страницу
     */
    fetchHtml(url: string): Promise<string | null>;
}
//# sourceMappingURL=scraper.d.ts.map