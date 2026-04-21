"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.AgentLearningService = void 0;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
/**
 * Сервис для обучения агента на основе отправленных ответов
 */
class AgentLearningService {
    historyPath;
    skillsPath;
    constructor() {
        this.historyPath = path.join(process.cwd(), 'data', 'learning', 'history.json');
        this.skillsPath = path.join(process.cwd(), 'config', 'agent-skills.json');
        // Создать директорию если не существует
        fs.mkdirSync(path.dirname(this.historyPath), { recursive: true });
    }
    /**
     * Сохранить отправленный ответ в историю
     */
    saveProposal(proposal) {
        const history = this.getHistory();
        const newEntry = {
            ...proposal,
            id: this.generateId(),
            sentAt: new Date().toISOString(),
            status: 'sent'
        };
        history.push(newEntry);
        this.saveHistory(history);
        // Обновить статистику по типам задач
        this.updateStats(proposal.jobType);
    }
    /**
     * Получить историю ответов
     */
    getHistory() {
        if (!fs.existsSync(this.historyPath)) {
            return [];
        }
        const data = fs.readFileSync(this.historyPath, 'utf-8');
        return JSON.parse(data);
    }
    /**
     * Сохранить историю
     */
    saveHistory(history) {
        fs.writeFileSync(this.historyPath, JSON.stringify(history, null, 2));
    }
    /**
     * Обновить статистику по типам задач
     */
    updateStats(jobType) {
        const skillsConfig = this.getSkillsConfig();
        // Увеличить счётчик выполненных задач по типу
        if (!skillsConfig.statistics.byType) {
            skillsConfig.statistics.byType = {};
        }
        skillsConfig.statistics.byType[jobType] = (skillsConfig.statistics.byType[jobType] || 0) + 1;
        skillsConfig.statistics.totalProjects = (skillsConfig.statistics.totalProjects || 0) + 1;
        this.saveSkillsConfig(skillsConfig);
    }
    /**
     * Получить конфигурацию скилов
     */
    getSkillsConfig() {
        if (!fs.existsSync(this.skillsPath)) {
            return this.getDefaultSkillsConfig();
        }
        const data = fs.readFileSync(this.skillsPath, 'utf-8');
        return JSON.parse(data);
    }
    /**
     * Сохранить конфигурацию скилов
     */
    saveSkillsConfig(config) {
        fs.writeFileSync(this.skillsPath, JSON.stringify(config, null, 2));
    }
    /**
     * Получить дефолтную конфигурацию
     */
    getDefaultSkillsConfig() {
        return {
            version: "1.0",
            updatedAt: new Date().toISOString(),
            skills: {
                technical: {},
                soft: {}
            },
            antigravity: {
                enabled: true,
                services: {}
            },
            preferences: {},
            statistics: {
                totalProjects: 0,
                byType: {}
            }
        };
    }
    /**
     * Обновить уровень навыка
     */
    updateSkillLevel(skillName, increment = 0.05) {
        const config = this.getSkillsConfig();
        if (config.skills.technical[skillName]) {
            const currentLevel = config.skills.technical[skillName].level || 0.5;
            const newLevel = Math.min(1.0, currentLevel + increment);
            config.skills.technical[skillName].level = newLevel;
            config.skills.technical[skillName].lastUsed = new Date().toISOString();
            config.skills.technical[skillName].projectsCompleted =
                (config.skills.technical[skillName].projectsCompleted || 0) + 1;
            // Повысить confidence при достижении порогов
            if (newLevel >= 0.8 && config.skills.technical[skillName].confidence === 'medium') {
                config.skills.technical[skillName].confidence = 'high';
            }
            else if (newLevel >= 0.5 && config.skills.technical[skillName].confidence === 'low') {
                config.skills.technical[skillName].confidence = 'medium';
            }
        }
        this.saveSkillsConfig(config);
    }
    /**
     * Получить лучшие паттерны ответов по типу задачи
     */
    getBestPatterns(jobType, limit = 3) {
        const history = this.getHistory();
        // Фильтровать по типу и статусу
        const filtered = history.filter(p => p.jobType === jobType &&
            (p.status === 'accepted' || p.status === 'sent'));
        // Сортировать по дате (новые первые)
        filtered.sort((a, b) => new Date(b.sentAt).getTime() - new Date(a.sentAt).getTime());
        return filtered.slice(0, limit);
    }
    /**
     * Обновить статус ответа (принят/отклонён)
     */
    updateProposalStatus(id, status, feedback) {
        const history = this.getHistory();
        const proposal = history.find(p => p.id === id);
        if (proposal) {
            proposal.status = status;
            proposal.feedback = feedback;
            // Если принят — обновить скилы
            if (status === 'accepted') {
                this.updateSkillLevelForJobType(proposal.jobType);
            }
            this.saveHistory(history);
        }
    }
    /**
     * Обновить скилы для типа задачи
     */
    updateSkillLevelForJobType(jobType) {
        const skillMapping = {
            'lecture': ['technicalWriting', 'communication'],
            'code': ['programming', 'architecture'],
            'text': ['technicalWriting', 'copywriting'],
            'design': ['design', 'creativity'],
            'data': ['dataProcessing', 'automation']
        };
        const skills = skillMapping[jobType] || [];
        for (const skill of skills) {
            this.updateSkillLevel(skill, 0.02);
        }
    }
    /**
     * Сгенерировать ID
     */
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }
    /**
     * Получить статистику
     */
    getStats() {
        const config = this.getSkillsConfig();
        const history = this.getHistory();
        return {
            totalProjects: config.statistics.totalProjects || 0,
            byType: config.statistics.byType || {},
            accepted: history.filter(p => p.status === 'accepted').length,
            rejected: history.filter(p => p.status === 'rejected').length,
            pending: history.filter(p => p.status === 'sent').length
        };
    }
}
exports.AgentLearningService = AgentLearningService;
