import { BrowserService } from '../services/browser';
import { Logger } from '../services/logger';
import { RawJob } from '../models/job';
export { RawJob };
/**
 * Задача с оценками соответствия
 */
export interface ScoredJob {
    job: RawJob;
    skillMatchScore: number;
    clarityScore: number;
    overallScore: number;
}
/**
 * Селекторы платформы
 */
export interface PlatformSelectors {
    jobCard: string;
    title: string;
    description: string;
    budget: string;
    skills: string;
    clientInfo: string;
    postedAt: string;
    proposalsCount: string;
}
/**
 * Задержки платформы (человеческое поведение)
 */
export interface PlatformDelays {
    pageLoad: number;
    scroll: number;
    click: number;
    betweenRequests: number;
}
/**
 * Фильтры для поиска задач
 */
export interface JobFilters {
    minBudget?: number;
    categories?: string[];
    ignoreKeywords?: string[];
    limit?: number;
}
/**
 * Базовый интерфейс адаптера платформы
 * Работает с публичными данными (без авторизации)
 */
export declare abstract class PlatformAdapter {
    protected browser: BrowserService;
    protected logger: Logger;
    abstract name: string;
    abstract baseUrl: string;
    abstract jobsUrl: string;
    protected selectors: PlatformSelectors;
    protected delays: PlatformDelays;
    protected filters: JobFilters;
    constructor(browser: BrowserService, logger: Logger);
    /** Ключевые слова в заголовке/описании → задание пропускается */
    private static readonly BLACKLIST_KEYWORDS;
    /**
     * Проверяет, нужно ли пропустить задание (чёрный список)
     * Вызывается ПОСЛЕ извлечения, ПЕРЕД сохранением в БД
     */
    shouldSkipJob(title: string, description: string): {
        skip: boolean;
        reason?: string;
    };
    /**
     * Отфильтровать задания из чёрного списка
     * Вызывать после extractJobs()
     */
    filterJobs(jobs: RawJob[]): RawJob[];
    /**
     * Перейти к поиску задач (публичная страница)
     * @returns true если успешно, false если ошибка
     */
    abstract navigateToJobs(filters?: JobFilters): Promise<boolean>;
    /**
     * Извлечь список задач
     */
    abstract extractJobs(): Promise<RawJob[]>;
    /**
     * Извлечь детали задачи (при необходимости)
     */
    extractJobDetails(url: string): Promise<Partial<RawJob>>;
    /**
     * Прокрутка для загрузки контента
     */
    protected scrollToLoadMore(maxScrolls?: number): Promise<void>;
    /**
     * Задержка
     */
    protected sleep(ms: number): Promise<void>;
    /**
     * Извлечь бюджет из текста
     */
    protected parseBudget(budgetText: string): {
        amount?: number;
        min?: number;
        max?: number;
        currency: string;
        type: 'fixed' | 'hourly';
    } | undefined;
    /**
     * Нормализовать валюту
     */
    private normalizeCurrency;
    /**
     * Извлечь навыки из текста
     */
    protected extractSkillsFromText(text: string): string[];
}
//# sourceMappingURL=base.d.ts.map