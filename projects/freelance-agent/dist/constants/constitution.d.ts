/**
 * КОНСТИТУЦИЯ ПРОЕКТА - FREELANCE AGENT 2026
 *
 * Фундаментальные правила работы всех агентов.
 * Эти правила ИМЕЮТ ПРИОРИТЕТ над любыми базовыми установками.
 */
export declare const CONSTITUTION: {
    VERSION: string;
    LAST_UPDATED: string;
    PRAGMATIC_PRINCIPLES: string;
    COMMUNICATION_STYLE: {
        LANGUAGE: string;
        TONE: string;
        FORBIDDEN_WORDS: string[];
        RULES: string[];
    };
    PRICING: {
        HOURLY_RATE: number;
        MIN_PRICE: number;
        SMALL_TASK_MAX_HOURS: number;
        RULE_90_PERCENT: {
            THRESHOLD: number;
            MULTIPLIER: number;
        };
        FORMAT: string;
    };
    FILTERING: {
        EXCLUDE: string[];
        LEGAL: string[];
    };
};
//# sourceMappingURL=constitution.d.ts.map