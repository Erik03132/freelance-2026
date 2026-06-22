import { RawJob } from '../models/job';
/**
 * Сервис хранения данных на базе SQLite
 */
export declare class StorageService {
    private db;
    private readonly dbPath;
    constructor(dbName?: string);
    /**
     * Инициализировать базу данных
     */
    init(): void;
    /**
     * Обновить оценки задачи
     */
    updateJobScores(jobId: number, skillMatchScore: number, clarityScore: number): void;
    /**
     * Сохранить задачу
     */
    saveJob(job: RawJob): void;
    /**
     * Сохранить несколько задач
     */
    saveJobs(jobs: RawJob[]): void;
    /**
     * Получить задачи по фильтру
     */
    getJobs(filters?: {
        platform?: string;
        status?: string;
        minSkillMatch?: number;
        url?: string;
        limit?: number;
    }): RawJob[];
    /**
     * Обновить статус задачи
     */
    updateJobStatus(url: string, status: string, extraData?: Partial<RawJob>): void;
    /**
     * Начать сессию
     */
    startSession(platform: string): number;
    /**
     * Завершить сессию
     */
    completeSession(sessionId: number, jobsFound: number, jobsFiltered: number): void;
    /**
     * Преобразовать строку БД в Job
     */
    private rowToJob;
    /**
     * Добавить колонку в таблицу, если она отсутствует
     */
    private addColIfNotExists;
    /**
     * Закрыть соединение с БД
     */
    close(): void;
    /**
     * Получить путь к БД
     */
    getDbPath(): string;
}
//# sourceMappingURL=storage.d.ts.map