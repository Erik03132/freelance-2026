import { Page } from 'playwright';
import { Logger } from './logger';
/**
 * Результат навигации
 */
export interface NavigationResult {
    success: boolean;
    error?: string;
    errorCode?: string;
    suggestion?: string;
}
/**
 * Браузерный сервис на базе Playwright
 * Управляет браузером, навигацией и извлечением данных
 */
export declare class BrowserService {
    private browser;
    private context;
    private page;
    private readonly headless;
    private logger;
    constructor(headless?: boolean, logger?: Logger);
    /**
     * Запустить браузер
     */
    launch(): Promise<void>;
    /**
     * Перейти на страницу с обработкой ошибок
     */
    goto(url: string, timeout?: number): Promise<NavigationResult>;
    /**
     * Ввести текст в поле
     */
    type(selector: string, text: string): Promise<void>;
    /**
     * Кликнуть по элементу
     */
    click(selector: string): Promise<void>;
    /**
     * Проверить существование элемента
     */
    exists(selector: string): Promise<boolean>;
    /**
     * Извлечь текст из элемента
     */
    extractText(selector: string): Promise<string>;
    /**
     * Извлечь все элементы (текст + href)
     */
    extractAll(selector: string): Promise<Array<{
        text: string;
        href?: string;
    }>>;
    /**
     * Извлечь атрибут элемента
     */
    extractAttribute(selector: string, attribute: string): Promise<string>;
    /**
     * Прокрутить до конца страницы
     */
    scrollToEnd(): Promise<void>;
    /**
     * Сохранить куки в файл
     */
    saveCookies(filePath: string): Promise<void>;
    /**
     * Загрузить куки из файла
     */
    loadCookies(filePath: string): Promise<void>;
    /**
     * Получить текущий URL
     */
    getCurrentUrl(): Promise<string>;
    /**
     * Сделать скриншот
     */
    screenshot(filePath: string): Promise<void>;
    /**
     * Скачать файл в буфер (использует текущую сессию/куки)
     */
    downloadToBuffer(url: string): Promise<Buffer | null>;
    /**
     * Выполнить JavaScript в контексте страницы
     */
    evaluate<T = any>(pageFunction: string | ((...args: any[]) => T)): Promise<T>;
    /**
     * Закрыть браузер
     */
    close(): Promise<void>;
    /**
     * Получить страницу (для продвинутого использования)
     */
    getPage(): Page | null;
    /**
     * Рендеринг HTML-контента в буфер (PNG или PDF)
     * Используется для создания визуальных артефактов (30% CORE)
     */
    renderHtmlToBuffer(html: string, options?: {
        type?: 'png' | 'pdf';
        width?: number;
        height?: number;
    }): Promise<Buffer>;
}
//# sourceMappingURL=browser.d.ts.map