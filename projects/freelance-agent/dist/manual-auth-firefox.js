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
const playwright_1 = require("playwright");
const logger_1 = require("./services/logger");
const path = __importStar(require("path"));
/**
 * Скрипт ручной авторизации на Kwork через Firefox
 */
async function manualAuthFirefox() {
    const logger = new logger_1.Logger();
    console.log('\n=== РУЧНАЯ АВТОРИЗАЦИЯ НА KWORK (Firefox) ===\n');
    console.log('1. Сейчас откроется браузер Firefox...');
    console.log('2. Войдите в аккаунт Kwork (введите email, пароль, пройдите капчу)');
    console.log('3. После успешного входа нажмите Enter в этом окне');
    console.log('4. Куки будут сохранены автоматически\n');
    console.log('Нажмите Ctrl+C для отмены в любой момент.\n');
    let browser = null;
    try {
        console.log('Запуск Firefox...');
        browser = await playwright_1.firefox.launch({
            headless: false,
            args: []
        });
        const context = await browser.newContext({
            viewport: { width: 1920, height: 1080 },
            userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            locale: 'ru-RU',
            timezoneId: 'Europe/Moscow',
            proxy: undefined
        });
        const page = await context.newPage();
        console.log('Браузер запущен. Открываю Kwork...\n');
        // Перейти на страницу входа с большим таймаутом
        await page.goto('https://kwork.ru/login', { waitUntil: 'domcontentloaded', timeout: 60000 });
        console.log('Страница входа открыта. Жду вашей авторизации...\n');
        // Ждать ввода пользователя
        await new Promise((resolve) => {
            process.stdin.once('data', () => {
                resolve();
            });
        });
        // Проверить авторизацию
        console.log('\nПроверка авторизации...');
        await page.goto('https://kwork.ru/user', { waitUntil: 'domcontentloaded', timeout: 60000 });
        const isLoggedIn = await page.$('.user-menu__link, .header-menu__user');
        if (isLoggedIn) {
            console.log('✅ Авторизация успешна!');
            // Сохранить куки
            const cookies = await context.cookies();
            const cookiesPath = path.join(process.cwd(), 'data', 'cookies', 'kwork.json');
            await import('fs').then(fs => {
                fs.mkdirSync(path.dirname(cookiesPath), { recursive: true });
                fs.writeFileSync(cookiesPath, JSON.stringify(cookies, null, 2));
            });
            console.log(`✅ Куки сохранены в: ${cookiesPath}`);
            console.log('\nТеперь агент может использовать сохранённые куки для автоматической работы!');
        }
        else {
            console.log('❌ Авторизация не удалась. Проверьте, что вы вошли в аккаунт.');
        }
    }
    catch (error) {
        logger.error('MANUAL_AUTH_FIREFOX', error);
        console.error('\n❌ Ошибка:', error);
    }
    finally {
        if (browser) {
            await browser.close();
            console.log('\nБраузер закрыт.');
        }
        process.exit(0);
    }
}
manualAuthFirefox();
