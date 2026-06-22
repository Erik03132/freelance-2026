export interface LogEntry {
    timestamp: string;
    action: string;
    result: string;
    details?: any;
}
/**
 * Сервис логирования
 * Пишет логи в файлы и консоль
 */
export declare class Logger {
    private logFile;
    constructor(date?: string);
    /**
     * Записать лог
     */
    log(action: string, result: string, details?: any): void;
    /**
     * Записать ошибку
     */
    error(action: string, error: Error, details?: any): void;
    /**
     * Записать предупреждение
     */
    warn(action: string, message: string, details?: any): void;
    /**
     * Записать информацию о задаче
     */
    job(message: string, jobData: {
        title: string;
        platform: string;
        url?: string;
    }): void;
    /**
     * Получить путь к файлу логов
     */
    getLogFile(): string;
}
//# sourceMappingURL=logger.d.ts.map