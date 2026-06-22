import { ProfileConfig } from '../models/profile';
import { RawJob } from '../adapters/base';
/**
 * Сервис для оценки соответствия задач профилю пользователя
 */
export declare class MatcherService {
    private profile;
    constructor(profile: ProfileConfig);
    /**
     * Оценить соответствие задачи навыкам пользователя (0-1)
     */
    calculateSkillMatch(job: RawJob): number;
    /**
     * Оценить качество ТЗ (0-1)
     */
    calculateClarityScore(job: RawJob): number;
    /**
     * Проверить, проходит ли задача пороги фильтрации
     */
    passesThresholds(job: RawJob, skillMatchScore: number, clarityScore: number): boolean;
    /**
     * Извлечь навыки из описания задачи
     */
    private extractJobSkills;
    /**
     * Найти соответствующий навык в профиле пользователя
     */
    private findMatchingSkill;
    /**
     * Нормализовать название навыка
     */
    private normalizeSkill;
}
//# sourceMappingURL=matcher.d.ts.map