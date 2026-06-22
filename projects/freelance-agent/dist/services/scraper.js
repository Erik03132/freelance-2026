"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ScraperService = void 0;
const logger_1 = require("./logger");
/**
 * Простое решение для скачивания HTML без браузера
 * (Используем нативный fetch из Node.js 18+)
 */
class ScraperService {
    logger;
    userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';
    constructor(logger) {
        this.logger = logger || new logger_1.Logger();
    }
    /**
     * Получить HTML-страницу
     */
    async fetchHtml(url) {
        try {
            this.logger.log('SCRAPER_FETCH', `Загрузка через native fetch: ${url}`);
            const response = await fetch(url, {
                headers: {
                    'User-Agent': this.userAgent,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
                }
            });
            if (response.ok) {
                return await response.text();
            }
            return null;
        }
        catch (error) {
            this.logger.error('SCRAPER_FETCH', error, { url });
            return null;
        }
    }
}
exports.ScraperService = ScraperService;
