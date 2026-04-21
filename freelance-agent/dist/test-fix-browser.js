"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const browser_1 = require("./services/browser");
const logger_1 = require("./services/logger");
async function test() {
    const logger = new logger_1.Logger();
    const browser = new browser_1.BrowserService(true, logger);
    try {
        console.log('Попытка запуска через BrowserService...');
        await browser.launch();
        console.log('✅ Успешный запуск!');
        const page = browser.getPage();
        if (page) {
            await page.goto('https://example.com');
            console.log('Заголовок страницы:', await page.title());
        }
        await browser.close();
    }
    catch (error) {
        console.error('❌ Ошибка:', error);
    }
}
test();
