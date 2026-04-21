import { Page } from 'playwright';
/**
 * Сервис для автоматической отправки откликов на биржах
 */
export declare class AutoBidService {
    private browser;
    private page;
    private readonly cookiesPath;
    constructor();
    /**
     * Запустить браузер
     */
    launch(headless?: boolean): Promise<void>;
    /**
     * Загрузить куки для платформы
     */
    loadCookies(platform: string): Promise<void>;
    /**
     * Сохранить куки для платформы
     */
    saveCookies(platform: string): Promise<void>;
    /**
     * Войти на Kwork
     */
    loginToKwork(email: string, password: string): Promise<boolean>;
    /**
     * Войти на Freelance.ru
     */
    loginToFreelance(email: string, password: string): Promise<boolean>;
    /**
     * Открыть страницу отклика на задачу
     */
    openBidPage(url: string): Promise<void>;
    /**
     * Вставить текст отклика в форму
     */
    pasteProposal(text: string): Promise<void>;
    /**
     * Отправить форму отклика
     */
    submitBid(): Promise<boolean>;
    /**
     * Закрыть браузер
     */
    close(): Promise<void>;
    /**
     * Получить страницу (для продвинутого использования)
     */
    getPage(): Page | null;
}
//# sourceMappingURL=auto-bid.d.ts.map