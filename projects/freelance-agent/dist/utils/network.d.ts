import { Logger } from '../services/logger';
/**
 * Проверка сетевого соединения
 */
export declare class NetworkChecker {
    private logger;
    constructor(logger: Logger);
    /**
     * Проверить доступность интернета
     */
    checkInternet(): Promise<{
        success: boolean;
        error?: string;
    }>;
    /**
     * Проверить доступность конкретной платформы
     */
    checkPlatform(url: string): Promise<{
        success: boolean;
        error?: string;
    }>;
}
//# sourceMappingURL=network.d.ts.map