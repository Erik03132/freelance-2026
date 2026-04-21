import { Page } from 'playwright';
/**
 * Человеческая задержка (случайное время в диапазоне)
 */
export declare function humanDelay(min: number, max: number): Promise<void>;
/**
 * Человеческий клик с задержками
 */
export declare function humanClick(page: Page, selector: string): Promise<void>;
/**
 * Человеческий скролл
 */
export declare function humanScroll(page: Page): Promise<void>;
/**
 * Случайная задержка перед запросом
 */
export declare function beforeRequest(): Promise<void>;
/**
 * Случайная задержка после запроса
 */
export declare function afterRequest(): Promise<void>;
//# sourceMappingURL=delays.d.ts.map