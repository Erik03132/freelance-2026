"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.MatcherService = void 0;
/**
 * Сервис для оценки соответствия задач профилю пользователя
 */
class MatcherService {
    profile;
    constructor(profile) {
        this.profile = profile;
    }
    /**
     * Оценить соответствие задачи навыкам пользователя (0-1)
     */
    calculateSkillMatch(job) {
        const userSkills = Object.keys(this.profile.skills);
        const skillSynonyms = this.profile.skillSynonyms || {};
        // Извлечь все навыки из описания задачи
        const jobSkills = this.extractJobSkills(job, userSkills, skillSynonyms);
        if (jobSkills.length === 0) {
            return 0;
        }
        // Рассчитать вес匹配
        let totalWeight = 0;
        let matchedWeight = 0;
        for (const jobSkill of jobSkills) {
            // Найти соответствующий навык в профиле
            const userSkill = this.findMatchingSkill(jobSkill, userSkills, skillSynonyms);
            if (userSkill) {
                const weight = this.profile.skills[userSkill] || 0.5;
                matchedWeight += weight;
            }
            totalWeight += 1;
        }
        // Нормализовать к [0, 1]
        const score = totalWeight > 0 ? matchedWeight / totalWeight : 0;
        return Math.round(score * 100) / 100;
    }
    /**
     * Оценить качество ТЗ (0-1)
     */
    calculateClarityScore(job) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        let score = 0;
        const maxScore = 20;
        // 1. Есть ли описание задачи (2 балла)
        if (job.description && job.description.length > 50) {
            score += 2;
        }
        // 2. Указана ли технология/стек (3 балла)
        const techKeywords = [
            'react', 'next', 'vue', 'angular', 'node', 'python', 'django',
            'flask', 'express', 'nest', 'postgresql', 'mysql', 'mongodb',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'redis',
            'typescript', 'javascript', 'php', 'laravel', 'rails',
            'flutter', 'react native', 'ios', 'android',
            'figma', 'photoshop', 'illustrator', 'api', 'rest', 'graphql'
        ];
        const foundTech = techKeywords.filter(keyword => text.includes(keyword));
        if (foundTech.length >= 1) {
            score += 3;
        }
        // 3. Есть ли конкретные требования (3 балла)
        const requirementPatterns = [
            /\b(должен|необходимо|требуется|нужно)\b/i,
            /\b(обязанност[ьи]|требован[ьи]я)\b/i,
            /\b(опыт|знание|умение)\b/i
        ];
        if (requirementPatterns.some(pattern => pattern.test(text))) {
            score += 3;
        }
        // 4. Есть ли примеры/референсы (2 балла)
        const referencePatterns = [
            /\b(пример|референс|аналог|как)\b/i,
            /\b(ссылк[аи]|url|http)\b/i,
            /\b(похожий|подобный)\b/i
        ];
        if (referencePatterns.some(pattern => pattern.test(text))) {
            score += 2;
        }
        // 5. Описан ли результат (2 балла)
        const resultPatterns = [
            /\b(результат|итог|получить|сделать|готов[ыйую])\b/i,
            /\b(функционал|возможност[ьи]|фич[аи])\b/i
        ];
        if (resultPatterns.some(pattern => pattern.test(text))) {
            score += 2;
        }
        // 6. Есть ли бюджет (2 балла)
        if (job.budget && (job.budget.amount || job.budget.min)) {
            score += 2;
        }
        // 7. Есть ли сроки (2 балла)
        const deadlinePatterns = [
            /\b(срок|дедлайн|время|день|недел[ьи]|месяц)\b/i,
            /\b(к|до)\s+\d+\s*(числа|месяца|недели)/i
        ];
        if (deadlinePatterns.some(pattern => pattern.test(text))) {
            score += 2;
        }
        // 8. Длина описания (4 балла максимум)
        const descriptionLength = job.description?.length || 0;
        if (descriptionLength >= 500) {
            score += 4;
        }
        else if (descriptionLength >= 200) {
            score += 3;
        }
        else if (descriptionLength >= 100) {
            score += 2;
        }
        else if (descriptionLength >= 50) {
            score += 1;
        }
        // Нормализовать к [0, 1]
        const normalizedScore = score / maxScore;
        return Math.round(normalizedScore * 100) / 100;
    }
    /**
     * Проверить, проходит ли задача пороги фильтрации
     */
    passesThresholds(job, skillMatchScore, clarityScore) {
        const { matching } = this.profile;
        // Проверка порога skill match (только если порог > 0)
        const skillThreshold = matching.skillMatchThreshold || 0;
        if (skillThreshold > 0 && skillMatchScore < skillThreshold) {
            return false;
        }
        // Проверка порога clarity (только если порог > 0)
        const clarityThreshold = matching.clarityThreshold || 0;
        if (clarityThreshold > 0 && clarityScore < clarityThreshold) {
            return false;
        }
        // Проверка минимального бюджета (только если порог > 0)
        if (matching.minBudget > 0 && job.budget) {
            const amount = job.budget.type === 'hourly'
                ? job.budget.min || 0
                : job.budget.amount;
            if (amount && amount < matching.minBudget) {
                return false;
            }
        }
        // Проверка игнорируемых категорий (только если категория задачи существует)
        if (job.category && this.profile.preferences.ignoreCategories?.some(cat => job.category.toLowerCase().includes(cat.toLowerCase()))) {
            return false;
        }
        // Проверка игнорируемых ключевых слов
        if (this.profile.preferences.ignoreKeywords?.some(word => job.title.toLowerCase().includes(word.toLowerCase()) ||
            job.description?.toLowerCase().includes(word.toLowerCase()))) {
            return false;
        }
        return true;
    }
    /**
     * Извлечь навыки из описания задачи
     */
    extractJobSkills(job, userSkills, skillSynonyms) {
        const text = `${job.title} ${job.description}`.toLowerCase();
        const foundSkills = [];
        // Проверить явные навыки из карточки
        if (job.skills) {
            for (const skill of job.skills) {
                const normalized = this.normalizeSkill(skill, userSkills, skillSynonyms);
                if (normalized && !foundSkills.includes(normalized)) {
                    foundSkills.push(normalized);
                }
            }
        }
        // Проверить текст описания на наличие навыков
        for (const [canonicalSkill, synonyms] of Object.entries(skillSynonyms)) {
            // Проверить каноническое название
            if (text.includes(canonicalSkill.toLowerCase()) && !foundSkills.includes(canonicalSkill)) {
                foundSkills.push(canonicalSkill);
                continue;
            }
            // Проверить синонимы
            for (const synonym of synonyms) {
                if (text.includes(synonym.toLowerCase()) && !foundSkills.includes(canonicalSkill)) {
                    foundSkills.push(canonicalSkill);
                    break;
                }
            }
        }
        // Проверить навыки, которые не имеют синонимов
        for (const skill of userSkills) {
            if (!skillSynonyms[skill] && text.includes(skill.toLowerCase())) {
                if (!foundSkills.includes(skill)) {
                    foundSkills.push(skill);
                }
            }
        }
        return foundSkills;
    }
    /**
     * Найти соответствующий навык в профиле пользователя
     */
    findMatchingSkill(jobSkill, userSkills, skillSynonyms) {
        // Точное совпадение
        if (userSkills.includes(jobSkill)) {
            return jobSkill;
        }
        // Поиск по синонимам
        for (const [canonicalSkill, synonyms] of Object.entries(skillSynonyms)) {
            if (synonyms.some(s => s.toLowerCase() === jobSkill.toLowerCase())) {
                return canonicalSkill;
            }
        }
        // Частичное совпадение
        for (const skill of userSkills) {
            if (skill.toLowerCase().includes(jobSkill.toLowerCase()) ||
                jobSkill.toLowerCase().includes(skill.toLowerCase())) {
                return skill;
            }
        }
        return null;
    }
    /**
     * Нормализовать название навыка
     */
    normalizeSkill(skill, userSkills, skillSynonyms) {
        // Точное совпадение
        if (userSkills.includes(skill)) {
            return skill;
        }
        // Поиск по синонимам
        for (const [canonicalSkill, synonyms] of Object.entries(skillSynonyms)) {
            if (synonyms.some(s => s.toLowerCase() === skill.toLowerCase())) {
                return canonicalSkill;
            }
        }
        return null;
    }
}
exports.MatcherService = MatcherService;
