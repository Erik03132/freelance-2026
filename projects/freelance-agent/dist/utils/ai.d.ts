/**
 * Исследовательский поиск через Perplexity API
 */
export declare function perplexitySearch(query: string): Promise<string>;
/**
 * Генерация контента/кода через Gemini Pro
 */
export declare function generateWithGemini(prompt: string, systemPrompt?: string): Promise<string>;
/**
 * Анализ файла (изображение или PDF) через Gemini
 */
export declare function analyzeFileWithGemini(buffer: Buffer, mimeType: string, prompt: string): Promise<string>;
//# sourceMappingURL=ai.d.ts.map