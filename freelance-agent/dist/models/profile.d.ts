/**
 * Модель профиля пользователя
 */
export interface UserProfile {
    name: string;
    nickname: string;
    timezone: string;
    portfolio: {
        github?: string;
        website?: string;
        telegram?: string;
        [key: string]: string | undefined;
    };
}
export interface SkillSet {
    [skill: string]: number;
}
export interface SkillSynonyms {
    [canonicalSkill: string]: string[];
}
export interface Preferences {
    categories: string[];
    ignoreCategories: string[];
    ignoreKeywords: string[];
}
export interface MatchingConfig {
    skillMatchThreshold: number;
    clarityThreshold: number;
    maxTasksPerDay: number;
    minBudget: number;
    requirePaymentVerified: boolean;
    minClientRating: number;
    maxProposals: number;
}
export interface ScheduleConfig {
    enabled: boolean;
    timezone: string;
    runTime: string;
    daysOfWeek: number[];
}
export interface NotificationConfig {
    telegram?: {
        enabled: boolean;
        botToken: string;
        chatId: string;
    };
}
export interface ProtectionConfig {
    watermark: {
        enabled: boolean;
        text: string;
        position: string;
        opacity: number;
    };
    codeSnippets: {
        maxLines: number;
        hideCriticalParts: boolean;
    };
}
export interface ProfileConfig {
    user: UserProfile;
    skills: SkillSet;
    skillSynonyms: SkillSynonyms;
    preferences: Preferences;
    matching: MatchingConfig;
    schedule: ScheduleConfig;
    notifications: NotificationConfig;
    protection: ProtectionConfig;
}
//# sourceMappingURL=profile.d.ts.map