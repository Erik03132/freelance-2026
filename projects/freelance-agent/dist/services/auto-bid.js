"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.AutoBidService = void 0;
const playwright_1 = require("playwright");
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
/**
 * Сервис для автоматической отправки откликов на биржах
 */
class AutoBidService {
    browser = null;
    page = null;
    cookiesPath;
    constructor() {
        this.cookiesPath = path.join(process.cwd(), 'data', 'cookies');
        fs.mkdirSync(this.cookiesPath, { recursive: true });
    }
    /**
     * Запустить браузер
     */
    async launch(headless = false) {
        this.browser = await playwright_1.chromium.launch({
            headless,
            args: [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        });
        this.page = await this.browser.newPage({
            viewport: { width: 1920, height: 1080 },
            userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        });
        // Скрыть флаг автоматизации
        await this.page.addInitScript(() => {
            // @ts-ignore
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        });
    }
    /**
     * Загрузить куки для платформы
     */
    async loadCookies(platform) {
        if (!this.browser)
            return;
        const cookieFile = path.join(this.cookiesPath, `${platform}.json`);
        if (!fs.existsSync(cookieFile))
            return;
        const cookiesData = fs.readFileSync(cookieFile, 'utf-8');
        const cookies = JSON.parse(cookiesData);
        await this.page?.context().addCookies(cookies);
    }
    /**
     * Сохранить куки для платформы
     */
    async saveCookies(platform) {
        if (!this.page)
            return;
        const cookies = await this.page.context().cookies();
        const cookieFile = path.join(this.cookiesPath, `${platform}.json`);
        fs.writeFileSync(cookieFile, JSON.stringify(cookies, null, 2));
    }
    /**
     * Войти на Kwork
     */
    async loginToKwork(email, password) {
        if (!this.page)
            throw new Error('Browser not launched');
        try {
            // Перейти на страницу входа
            await this.page.goto('https://kwork.ru/login', { waitUntil: 'networkidle' });
            await this.page.waitForTimeout(2000);
            // Проверить, уже ли авторизован
            const isLoggedIn = await this.page.isVisible('a[href="/profile"]');
            if (isLoggedIn) {
                console.log('Kwork: уже авторизован');
                return true;
            }
            // Ввести email
            await this.page.fill('input[name="login[email]"]', email);
            await this.page.waitForTimeout(500);
            // Ввести пароль
            await this.page.fill('input[name="login[password]"]', password);
            await this.page.waitForTimeout(500);
            // Нажать кнопку входа
            await this.page.click('button[type="submit"]');
            await this.page.waitForTimeout(3000);
            // Проверить успешность входа
            const success = await this.page.isVisible('a[href="/profile"]');
            if (success) {
                await this.saveCookies('kwork');
                console.log('Kwork: успешный вход');
            }
            else {
                console.log('Kwork: ошибка входа');
            }
            return success;
        }
        catch (error) {
            console.error('Kwork login error:', error);
            return false;
        }
    }
    /**
     * Войти на Freelance.ru
     */
    async loginToFreelance(email, password) {
        if (!this.page)
            throw new Error('Browser not launched');
        try {
            // Перейти на страницу входа
            await this.page.goto('https://freelance.ru/login', { waitUntil: 'networkidle' });
            await this.page.waitForTimeout(2000);
            // Проверить, уже ли авторизован
            const isLoggedIn = await this.page.isVisible('a[href="/user/"]');
            if (isLoggedIn) {
                console.log('Freelance.ru: уже авторизован');
                return true;
            }
            // Ввести email
            await this.page.fill('input[name="login"]', email);
            await this.page.waitForTimeout(500);
            // Ввести пароль
            await this.page.fill('input[name="password"]', password);
            await this.page.waitForTimeout(500);
            // Нажать кнопку входа
            await this.page.click('button[type="submit"]');
            await this.page.waitForTimeout(3000);
            // Проверить успешность входа
            const success = await this.page.isVisible('a[href="/user/"]');
            if (success) {
                await this.saveCookies('freelance');
                console.log('Freelance.ru: успешный вход');
            }
            else {
                console.log('Freelance.ru: ошибка входа');
            }
            return success;
        }
        catch (error) {
            console.error('Freelance login error:', error);
            return false;
        }
    }
    /**
     * Открыть страницу отклика на задачу
     */
    async openBidPage(url) {
        if (!this.page)
            throw new Error('Browser not launched');
        await this.page.goto(url, { waitUntil: 'networkidle' });
        await this.page.waitForTimeout(2000);
    }
    /**
     * Вставить текст отклика в форму
     */
    async pasteProposal(text) {
        if (!this.page)
            throw new Error('Browser not launched');
        // Найти текстовое поле (разные селекторы для разных бирж)
        const selectors = [
            'textarea[name="text"]',
            'textarea[name="message"]',
            'textarea[class*="comment"]',
            'div[contenteditable="true"]',
            '.ql-editor',
            'textarea'
        ];
        for (const selector of selectors) {
            try {
                const element = await this.page.$(selector);
                if (element) {
                    await element.focus();
                    await this.page.keyboard.press('Control+A');
                    await this.page.keyboard.press('Delete');
                    await this.page.type(selector, text, { delay: 50 });
                    console.log('Текст вставлен в форму');
                    return;
                }
            }
            catch (e) {
                // Продолжить поиск
            }
        }
        console.log('Форма не найдена, текст скопирован в буфер');
    }
    /**
     * Отправить форму отклика
     */
    async submitBid() {
        if (!this.page)
            throw new Error('Browser not launched');
        try {
            // Найти кнопку отправки
            const selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button[class*="send"]',
                'button[class*="submit"]'
            ];
            for (const selector of selectors) {
                try {
                    const element = await this.page.$(selector);
                    if (element) {
                        await element.click();
                        await this.page.waitForTimeout(3000);
                        console.log('Отклик отправлен');
                        return true;
                    }
                }
                catch (e) {
                    // Продолжить поиск
                }
            }
            return false;
        }
        catch (error) {
            console.error('Submit error:', error);
            return false;
        }
    }
    /**
     * Закрыть браузер
     */
    async close() {
        await this.browser?.close();
        this.browser = null;
        this.page = null;
    }
    /**
     * Получить страницу (для продвинутого использования)
     */
    getPage() {
        return this.page;
    }
}
exports.AutoBidService = AutoBidService;
