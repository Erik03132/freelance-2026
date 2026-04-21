"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.humanDelay = humanDelay;
exports.humanClick = humanClick;
exports.humanScroll = humanScroll;
exports.beforeRequest = beforeRequest;
exports.afterRequest = afterRequest;
/**
 * Человеческая задержка (случайное время в диапазоне)
 */
function humanDelay(min, max) {
    const delay = Math.floor(Math.random() * (max - min + 1)) + min;
    return new Promise(resolve => setTimeout(resolve, delay));
}
/**
 * Человеческий клик с задержками
 */
async function humanClick(page, selector) {
    await humanDelay(300, 600);
    await page.click(selector);
    await humanDelay(200, 400);
}
/**
 * Человеческий скролл
 */
async function humanScroll(page) {
    const scrollDelay = () => humanDelay(1000, 2000);
    await scrollDelay();
    await page.evaluate(() => window.scrollBy(0, 500));
    await scrollDelay();
    await page.evaluate(() => window.scrollBy(0, 500));
    await scrollDelay();
    await page.evaluate(() => window.scrollBy(0, 500));
    await scrollDelay();
}
/**
 * Случайная задержка перед запросом
 */
async function beforeRequest() {
    await humanDelay(1000, 3000);
}
/**
 * Случайная задержка после запроса
 */
async function afterRequest() {
    await humanDelay(500, 1500);
}
