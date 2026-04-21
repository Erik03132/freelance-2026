/**
 * Интерфейс для сохранённого ответа
 */
export interface SavedProposal {
    id: string;
    jobId: number;
    jobTitle: string;
    jobType: 'lecture' | 'code' | 'text' | 'design' | 'data';
    responseText: string;
    sentAt: string;
    platform: string;
    status: 'sent' | 'accepted' | 'rejected';
    feedback?: string;
}
/**
 * Сервис для обучения агента на основе отправленных ответов
 */
export declare class AgentLearningService {
    private readonly historyPath;
    private readonly skillsPath;
    constructor();
    /**
     * Сохранить отправленный ответ в историю
     */
    saveProposal(proposal: Omit<SavedProposal, 'id' | 'sentAt' | 'status'>): void;
    /**
     * Получить историю ответов
     */
    getHistory(): SavedProposal[];
    /**
     * Сохранить историю
     */
    private saveHistory;
    /**
     * Обновить статистику по типам задач
     */
    private updateStats;
    /**
     * Получить конфигурацию скилов
     */
    private getSkillsConfig;
    /**
     * Сохранить конфигурацию скилов
     */
    private saveSkillsConfig;
    /**
     * Получить дефолтную конфигурацию
     */
    private getDefaultSkillsConfig;
    /**
     * Обновить уровень навыка
     */
    updateSkillLevel(skillName: string, increment?: number): void;
    /**
     * Получить лучшие паттерны ответов по типу задачи
     */
    getBestPatterns(jobType: string, limit?: number): SavedProposal[];
    /**
     * Обновить статус ответа (принят/отклонён)
     */
    updateProposalStatus(id: string, status: 'accepted' | 'rejected', feedback?: string): void;
    /**
     * Обновить скилы для типа задачи
     */
    private updateSkillLevelForJobType;
    /**
     * Сгенерировать ID
     */
    private generateId;
    /**
     * Получить статистику
     */
    getStats(): any;
}
//# sourceMappingURL=learning.d.ts.map