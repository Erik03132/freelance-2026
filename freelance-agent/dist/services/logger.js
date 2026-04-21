"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.Logger = void 0;
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
/**
 * Сервис логирования
 * Пишет логи в файлы и консоль
 */
class Logger {
    logFile;
    constructor(date = new Date().toISOString().split('T')[0]) {
        this.logFile = path_1.default.join(process.cwd(), 'logs', `agent-${date}.log`);
        fs_1.default.mkdirSync(path_1.default.dirname(this.logFile), { recursive: true });
    }
    /**
     * Записать лог
     */
    log(action, result, details) {
        const entry = {
            timestamp: new Date().toISOString(),
            action,
            result,
            details
        };
        const line = JSON.stringify(entry) + '\n';
        fs_1.default.appendFileSync(this.logFile, line);
        console.log(`[${entry.timestamp}] ${action}: ${result}`);
    }
    /**
     * Записать ошибку
     */
    error(action, error, details) {
        const entry = {
            timestamp: new Date().toISOString(),
            action,
            result: `ERROR: ${error.message}`,
            details: {
                stack: error.stack,
                ...details
            }
        };
        const line = JSON.stringify(entry) + '\n';
        fs_1.default.appendFileSync(this.logFile, line);
        console.error(`[${entry.timestamp}] ${action}: ERROR - ${error.message}`);
    }
    /**
     * Записать предупреждение
     */
    warn(action, message, details) {
        const entry = {
            timestamp: new Date().toISOString(),
            action,
            result: `WARN: ${message}`,
            details
        };
        const line = JSON.stringify(entry) + '\n';
        fs_1.default.appendFileSync(this.logFile, line);
        console.warn(`[${entry.timestamp}] ${action}: WARN - ${message}`);
    }
    /**
     * Записать информацию о задаче
     */
    job(message, jobData) {
        this.log(message, jobData.title, {
            platform: jobData.platform,
            url: jobData.url
        });
    }
    /**
     * Получить путь к файлу логов
     */
    getLogFile() {
        return this.logFile;
    }
}
exports.Logger = Logger;
