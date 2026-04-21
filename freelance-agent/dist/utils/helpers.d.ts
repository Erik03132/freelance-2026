/**
 * Извлечь навыки из описания задачи
 */
export declare function extractSkills(text: string, knownSkills: string[]): string[];
/**
 * Очистить текст от HTML-тегов
 */
export declare function stripHtml(html: string): string;
/**
 * Обрезать текст до указанной длины
 */
export declare function truncate(text: string, maxLength: number): string;
/**
 * Нормализовать URL
 */
export declare function normalizeUrl(url: string, baseUrl: string): string;
/**
 * Проверить, содержит ли текст стоп-слова
 */
export declare function containsStopWords(text: string, stopWords: string[]): boolean;
/**
 * Сгенерировать уникальный ID
 */
export declare function generateId(): string;
/**
 * Форматировать дату
 */
export declare function formatDate(date: Date): string;
/**
 * Форматировать относительное время (например, "2 часа назад")
 */
export declare function parseRelativeTime(relativeText: string, baseDate?: Date): Date | undefined;
//# sourceMappingURL=helpers.d.ts.map