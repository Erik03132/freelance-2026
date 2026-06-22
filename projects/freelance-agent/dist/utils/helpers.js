"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.extractSkills = extractSkills;
exports.stripHtml = stripHtml;
exports.truncate = truncate;
exports.normalizeUrl = normalizeUrl;
exports.containsStopWords = containsStopWords;
exports.generateId = generateId;
exports.formatDate = formatDate;
exports.parseRelativeTime = parseRelativeTime;
/**
 * Извлечь навыки из описания задачи
 */
function extractSkills(text, knownSkills) {
    if (!text)
        return [];
    const textLower = text.toLowerCase();
    const foundSkills = [];
    for (const skill of knownSkills) {
        const skillLower = skill.toLowerCase();
        const regex = new RegExp(`\\b${escapeRegex(skillLower)}\\b`, 'i');
        if (regex.test(textLower)) {
            foundSkills.push(skill);
        }
    }
    return foundSkills;
}
/**
 * Экранировать спецсимволы для regex
 */
function escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
/**
 * Очистить текст от HTML-тегов
 */
function stripHtml(html) {
    if (!html)
        return '';
    return html.replace(/<[^>]*>/g, '');
}
/**
 * Обрезать текст до указанной длины
 */
function truncate(text, maxLength) {
    if (!text)
        return '';
    if (text.length <= maxLength)
        return text;
    return text.slice(0, maxLength) + '...';
}
/**
 * Нормализовать URL
 */
function normalizeUrl(url, baseUrl) {
    if (url.startsWith('http')) {
        return url;
    }
    if (url.startsWith('//')) {
        return 'https:' + url;
    }
    return baseUrl + (url.startsWith('/') ? '' : '/') + url;
}
/**
 * Проверить, содержит ли текст стоп-слова
 */
function containsStopWords(text, stopWords) {
    if (!text || stopWords.length === 0)
        return false;
    const textLower = text.toLowerCase();
    return stopWords.some(word => textLower.includes(word.toLowerCase()));
}
/**
 * Сгенерировать уникальный ID
 */
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}
/**
 * Форматировать дату
 */
function formatDate(date) {
    return date.toISOString().split('T')[0];
}
/**
 * Форматировать относительное время (например, "2 часа назад")
 */
function parseRelativeTime(relativeText, baseDate = new Date()) {
    if (!relativeText)
        return undefined;
    const text = relativeText.toLowerCase().trim();
    // "только что"
    if (text.includes('только что') || text.includes('just now')) {
        return new Date();
    }
    // Обработка Kwork "Осталось: ..."
    // Обычно на Kwork дают 24 часа. Если осталось 23 часа, значит запостили час назад.
    if (text.includes('осталось') || text.includes('left')) {
        const hoursMatch = text.match(/(\d+)\s*ч/i);
        const daysMatch = text.match(/(\d+)\s*д/i);
        if (daysMatch) {
            // Если осталось больше суток, вероятно это старый заказ или длинный аукцион
            const daysLeft = parseInt(daysMatch[1]);
            if (daysLeft >= 3)
                return new Date(baseDate.getTime() - 7 * 24 * 60 * 60 * 1000); // Считаем старым
            return new Date(baseDate.getTime() - (3 - daysLeft) * 24 * 60 * 60 * 1000);
        }
        if (hoursMatch) {
            const hoursLeft = parseInt(hoursMatch[1]);
            // Если осталось 23 часа, значит запостили 1 час назад (при лимите в 24 часа)
            const hoursAgo = Math.max(0, 24 - hoursLeft);
            return new Date(baseDate.getTime() - hoursAgo * 60 * 60 * 1000);
        }
        return baseDate; // По умолчанию считаем свежим
    }
    // "X минут назад"
    const minutesMatch = text.match(/(\d+)\s*(минут[ыы]|minute[s]?)/i);
    if (minutesMatch) {
        const minutes = parseInt(minutesMatch[1]);
        return new Date(baseDate.getTime() - minutes * 60 * 1000);
    }
    // "X часов назад"
    const hoursMatch = text.match(/(\d+)\s*(час[аов]|hour[s]?)/i);
    if (hoursMatch) {
        const hours = parseInt(hoursMatch[1]);
        return new Date(baseDate.getTime() - hours * 60 * 60 * 1000);
    }
    // "X дней назад"
    const daysMatch = text.match(/(\d+)\s*(дн[яей]|day[s]?|дня)/i);
    if (daysMatch) {
        const days = parseInt(daysMatch[1]);
        return new Date(baseDate.getTime() - days * 24 * 60 * 60 * 1000);
    }
    // "X недель назад"
    const weeksMatch = text.match(/(\d+)\s*(недел[ьи]|week[s]?)/i);
    if (weeksMatch) {
        const weeks = parseInt(weeksMatch[1]);
        return new Date(baseDate.getTime() - weeks * 7 * 24 * 60 * 60 * 1000);
    }
    // Если не распознали, пробуем распарсить как обычную дату
    const parsed = new Date(relativeText);
    if (!isNaN(parsed.getTime())) {
        return parsed;
    }
    return undefined;
}
