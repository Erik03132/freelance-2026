"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.BrowserService = void 0;
const playwright_1 = require("playwright");
const logger_1 = require("./logger");
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
/**
 * Браузерный сервис на базе Playwright
 * Управляет браузером, навигацией и извлечением данных
 */
class BrowserService {
    browser = null;
    context = null;
    page = null;
    headless;
    logger;
    constructor(headless = true, logger) {
        this.headless = headless;
        this.logger = logger || new logger_1.Logger();
    }
    /**
     * Запустить браузер
     */
    async launch() {
        try {
            const dataDir = path_1.default.join(process.cwd(), '.browser-data');
            if (!fs_1.default.existsSync(dataDir)) {
                fs_1.default.mkdirSync(dataDir, { recursive: true });
            }
            this.logger.log('BROWSER_LAUNCH', 'Запуск WebKit для обхода проблем с MachPort Chromium...');
            this.browser = await playwright_1.firefox.launch({
                headless: this.headless
            });
            this.context = await this.browser.newContext({
                viewport: { width: 1920, height: 1080 },
                userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
                locale: 'ru-RU',
                timezoneId: 'Europe/Moscow',
                extraHTTPHeaders: {
                    'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
                }
            });
            this.page = this.context.pages()[0] || await this.context.newPage();
            // Скрыть флаг автоматизации
            await this.page.addInitScript(() => {
                // @ts-ignore
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            });
            this.logger.log('BROWSER_LAUNCH', 'Браузер успешно запущен');
        }
        catch (error) {
            this.logger.warn('BROWSER_LAUNCH', `Браузер не запущен: ${error.message}. Переходим в режим Direct Scraper.`);
            this.browser = null;
        }
    }
    /**
     * Перейти на страницу с обработкой ошибок
     */
    async goto(url, timeout = 30000) {
        if (!this.page) {
            return {
                success: false,
                error: 'Браузер не запущен',
                suggestion: 'Вызовите browser.launch() перед навигацией'
            };
        }
        try {
            await this.page.goto(url, { waitUntil: 'networkidle', timeout });
            return { success: true };
        }
        catch (error) {
            const err = error;
            const errorCode = err.code || 'UNKNOWN';
            // Определить тип ошибки и дать рекомендацию
            let suggestion = '';
            if (errorCode.includes('SOCKS') || errorCode.includes('PROXY') || err.message.includes('SOCKS')) {
                suggestion = '❌ Ошибка прокси. Проверьте настройки сети:\n' +
                    '   • Отключите VPN/прокси в системе (Системные настройки → Сеть)\n' +
                    '   • Проверьте, не включён ли прокси в терминале (export http_proxy)\n' +
                    '   • Перезапустите терминал и попробуйте снова';
            }
            else if (errorCode.includes('TIMEOUT') || errorCode.includes('ETIMEDOUT')) {
                suggestion = '⏱ Таймаут соединения. Проверьте:\n' +
                    '   • Доступность интернета\n' +
                    '   • Блокировку сайта (Роскомнадзор)\n' +
                    '   • Попробуйте позже';
            }
            else if (errorCode.includes('ENOTFOUND') || errorCode.includes('ECONNREFUSED')) {
                suggestion = '🌐 Сайт недоступен. Проверьте:\n' +
                    '   • Правильность URL\n' +
                    '   • Доступность сайта в браузере\n' +
                    '   • DNS-настройки';
            }
            else if (errorCode.includes('CERT')) {
                suggestion = '🔒 Ошибка SSL-сертификата. Попробуйте:\n' +
                    '   • Открыть сайт в браузере и принять сертификат\n' +
                    '   • Проверить дату на компьютере';
            }
            else {
                suggestion = `Ошибка сети: ${errorCode}.\n` +
                    `Сообщение: ${err.message}\n\n` +
                    `Возможные причины:\n` +
                    `   • Прокси/VPN в системе\n` +
                    `   • Блокировка сайта\n` +
                    `   • Временная недоступность`;
            }
            this.logger.error('BROWSER_NAVIGATION', err, { url, errorCode });
            return {
                success: false,
                error: err.message,
                errorCode,
                suggestion
            };
        }
    }
    /**
     * Ввести текст в поле
     */
    async type(selector, text) {
        if (!this.page) {
            throw new Error('Browser not launched');
        }
        await this.page.type(selector, text, { delay: 50 });
    }
    /**
     * Кликнуть по элементу
     */
    async click(selector) {
        if (!this.page) {
            throw new Error('Browser not launched');
        }
        await this.page.click(selector, { delay: 300 });
    }
    /**
     * Проверить существование элемента
     */
    async exists(selector) {
        if (!this.page) {
            throw new Error('Browser not launched');
        }
        try {
            await this.page.waitForSelector(selector, { timeout: 2000 });
            return true;
        }
        catch {
            return false;
        }
    }
    /**
     * Извлечь текст из элемента
     */
    async extractText(selector) {
        if (!this.page) {
            throw new Error('Browser not launched');
        }
        try {
            const element = await this.page.$(selector);
            if (!element)
                return '';
            const text = await element.textContent();
            return text?.trim() || '';
        }
        catch {
            return '';
        }
    }
    /**
     * Извлечь все элементы (текст + href)
     */
    async extractAll(selector) {
        if (!this.page) {
            throw new Error('Browser not launched');
        }
        try {
            return await this.page.$$eval(selector, elements => elements.map(el => ({
                text: el.textContent?.trim() || '',
                href: el.href || undefined
            })));
        }
        catch {
            return [];
        }
    }
    /**
     * Извлечь атрибут элемента
     */
    async extractAttribute(selector, attribute) {
        if (!this.page) {
            throw new Error('Browser not launched');
        }
        try {
            const element = await this.page.$(selector);
            if (!element)
                return '';
            const value = await element.getAttribute(attribute);
            return value || '';
        }
        catch {
            return '';
        }
    }
    /**
     * Прокрутить до конца страницы
     */
    async scrollToEnd() {
        if (!this.page) {
            throw new Error('Browser not launched');
        }
        await this.page.evaluate(async () => {
            await new Promise((resolve) => {
                let totalHeight = 0;
                const distance = 100;
                const timer = setInterval(() => {
                    window.scrollBy(0, distance);
                    totalHeight += distance;
                    if (window.innerHeight + window.scrollY >= document.body.scrollHeight - 100) {
                        clearInterval(timer);
                        resolve();
                    }
                }, 100);
            });
        });
    }
    /**
     * Сохранить куки в файл
     */
    async saveCookies(filePath) {
        if (!this.context) {
            throw new Error('Context not created');
        }
        const cookies = await this.context.cookies();
        const dir = path_1.default.dirname(filePath);
        fs_1.default.mkdirSync(dir, { recursive: true });
        fs_1.default.writeFileSync(filePath, JSON.stringify(cookies, null, 2));
    }
    /**
     * Загрузить куки из файла
     */
    async loadCookies(filePath) {
        if (!this.context) {
            throw new Error('Context not created');
        }
        if (!fs_1.default.existsSync(filePath)) {
            return;
        }
        const cookiesData = fs_1.default.readFileSync(filePath, 'utf-8');
        const cookies = JSON.parse(cookiesData);
        await this.context.addCookies(cookies);
    }
    /**
     * Получить текущий URL
     */
    async getCurrentUrl() {
        if (!this.page) {
            throw new Error('Browser not launched');
        }
        return this.page.url();
    }
    /**
     * Сделать скриншот
     */
    async screenshot(filePath) {
        if (!this.page) {
            throw new Error('Browser not launched');
        }
        await this.page.screenshot({ path: filePath, fullPage: true });
    }
    /**
     * Скачать файл в буфер (использует текущую сессию/куки)
     */
    async downloadToBuffer(url) {
        if (!this.context) {
            throw new Error('Browser not launched');
        }
        try {
            const response = await this.context.request.get(url);
            if (response.status() === 200) {
                return await response.body();
            }
            this.logger.error('BROWSER_DOWNLOAD', new Error(`Failed to download: ${response.status()}`), { url });
            return null;
        }
        catch (error) {
            this.logger.error('BROWSER_DOWNLOAD', error, { url });
            return null;
        }
    }
    /**
     * Выполнить JavaScript в контексте страницы
     */
    async evaluate(pageFunction) {
        if (!this.page) {
            throw new Error('Browser not launched');
        }
        return await this.page.evaluate(pageFunction);
    }
    /**
     * Закрыть браузер
     */
    async close() {
        await this.browser?.close();
        this.browser = null;
        this.context = null;
        this.page = null;
    }
    /**
     * Получить страницу (для продвинутого использования)
     */
    getPage() {
        return this.page;
    }
    /**
     * Рендеринг HTML-контента в буфер (PNG или PDF)
     * Используется для создания визуальных артефактов (30% CORE)
     */
    async renderHtmlToBuffer(html, options = {}) {
        const { type = 'png', width = 1200, height = 800 } = options;
        if (!this.context) {
            await this.launch();
        }
        const renderPage = await this.context.newPage();
        try {
            await renderPage.setViewportSize({ width, height });
            // Оборачиваем в базовые стили, если это просто фрагмент
            const fullHtml = html.includes('<html') ? html : `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <style>
            body { 
              font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
              margin: 0; padding: 40px; background: #0f172a; color: #f8fafc;
              line-height: 1.6;
            }
            .container { max-width: 1000px; margin: 0 auto; }
            pre { background: #1e293b; padding: 20px; border-radius: 8px; overflow: auto; border: 1px solid #334155; }
            h1, h2, h3 { color: #38bdf8; }
            code { color: #f472b6; }
          </style>
        </head>
        <body>
          <div class="container">${html}</div>
        </body>
        </html>
      `;
            await renderPage.setContent(fullHtml, { waitUntil: 'networkidle' });
            if (type === 'pdf') {
                return await renderPage.pdf({ format: 'A4', printBackground: true });
            }
            else {
                // Скриншот всей страницы
                return await renderPage.screenshot({ fullPage: true, type: 'png' });
            }
        }
        finally {
            await renderPage.close();
        }
    }
}
exports.BrowserService = BrowserService;
