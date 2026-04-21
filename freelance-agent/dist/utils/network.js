"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.NetworkChecker = void 0;
/**
 * Проверка сетевого соединения
 */
class NetworkChecker {
    logger;
    constructor(logger) {
        this.logger = logger;
    }
    /**
     * Проверить доступность интернета
     */
    async checkInternet() {
        const dns = await import('dns').then(m => m.default);
        const http = await import('http').then(m => m.default);
        return new Promise((resolve) => {
            // Попытка разрешить DNS
            dns.resolve('google.com', (err) => {
                if (err) {
                    this.logger.error('NETWORK_CHECK', err);
                    resolve({
                        success: false,
                        error: '❌ DNS не работает. Проверьте настройки сети.'
                    });
                    return;
                }
                // Попытка HTTP-запроса
                const req = http.get('http://google.com', { timeout: 5000 }, (res) => {
                    if (res.statusCode === 200 || res.statusCode === 301 || res.statusCode === 302) {
                        resolve({ success: true });
                    }
                    else {
                        resolve({
                            success: false,
                            error: `⚠️ HTTP-запрос вернул статус ${res.statusCode}`
                        });
                    }
                });
                req.on('error', (err) => {
                    this.logger.error('NETWORK_CHECK', err);
                    resolve({
                        success: false,
                        error: '❌ Нет доступа к интернету. Проверьте соединение.'
                    });
                });
                req.on('timeout', () => {
                    req.destroy();
                    resolve({
                        success: false,
                        error: '⏱ Таймаут соединения. Проверьте интернет.'
                    });
                });
            });
        });
    }
    /**
     * Проверить доступность конкретной платформы
     */
    async checkPlatform(url) {
        const https = await import('https').then(m => m.default);
        return new Promise((resolve) => {
            const req = https.get(url, { timeout: 10000 }, (res) => {
                if (res.statusCode === 200 || res.statusCode === 301 || res.statusCode === 302) {
                    resolve({ success: true });
                }
                else {
                    resolve({
                        success: false,
                        error: `⚠️ Сайт вернул статус ${res.statusCode}`
                    });
                }
            });
            req.on('error', (err) => {
                if (err.code === 'ENOTFOUND') {
                    resolve({
                        success: false,
                        error: `❌ Сайт ${url} недоступен (DNS ошибка)`
                    });
                }
                else if (err.code === 'ETIMEDOUT') {
                    resolve({
                        success: false,
                        error: `⏱ Таймаут при подключении к ${url}`
                    });
                }
                else if (err.code === 'ECONNREFUSED') {
                    resolve({
                        success: false,
                        error: `❌ Подключение отклонено ${url}`
                    });
                }
                else {
                    resolve({
                        success: false,
                        error: `❌ Ошибка: ${err.code || err.message}`
                    });
                }
            });
            req.on('timeout', () => {
                req.destroy();
                resolve({
                    success: false,
                    error: `⏱ Таймаут при подключении к ${url}`
                });
            });
        });
    }
}
exports.NetworkChecker = NetworkChecker;
