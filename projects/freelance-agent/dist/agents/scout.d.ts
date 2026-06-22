/**
 * Sherlock Agent (Агент-Шерлок, ранее Скаут)
 *
 * Элитный агент-аналитик. Его задача — найти «жемчужины» среди сотен задач.
 * 1. Глубокий анализ ТЗ (дедукция)
 * 2. Оценка выгодности (ROI): только те задачи, где ₽/час > 1000
 * 3. Приоритизация (Скоринг): выбор лучших 30 задач в день для Кворка
 * 4. Мульти-агентная маршрутизация (передача спецам)
 */
import { RawJob, ExecutionPlan } from '../models/job';
import { ProfileConfig } from '../models/profile';
import { RoutingDecision, ExpertProposal, DeepDeductionResult } from './specialists';
import { BrowserService } from '../services/browser';
export interface MCPService {
    name: string;
    purpose: string;
    enabled: boolean;
    capabilities: string[];
}
export interface AvailableServices {
    [key: string]: MCPService;
}
export interface FeasibilityResult {
    feasible: boolean;
    confidence: number;
    reasons: string[];
    blockers: FeasibilityBlocker[];
    missingServices: MissingService[];
    effortHours: number;
    rewardAnalysis: RewardAnalysis;
    category: TaskCategory;
}
export interface FeasibilityBlocker {
    type: 'credentials_required' | 'specific_site_access' | 'hardware' | 'legal' | 'skill_gap' | 'unclear_requirements' | 'too_complex';
    description: string;
    severity: 'critical' | 'major' | 'minor';
}
export interface MissingService {
    serviceName: string;
    serviceType: 'mcp' | 'api' | 'tool';
    purpose: string;
    howToConnect: string;
    priority: 'required' | 'recommended' | 'optional';
}
export interface RewardAnalysis {
    budgetAmount: number | null;
    budgetCurrency: string;
    hourlyRate: number | null;
    worthIt: boolean;
    comment: string;
}
export interface ProposalResult {
    proposal: string;
    feasibility: FeasibilityResult;
    warnings: string[];
    operatorNotes: string;
    routing?: RoutingDecision;
    expertProposal?: ExpertProposal;
    agentUsed?: string;
    score?: number;
    deepDeduction?: DeepDeductionResult;
    taskNature?: TaskNature;
    executionPlan?: ExecutionPlan;
}
export type TaskCategory = 'web_fullstack' | 'web_frontend' | 'web_backend' | 'telegram_bot' | 'chrome_extension' | 'parsing_scraping' | 'mobile_app' | 'desktop_app' | 'devops' | 'data_science' | 'design_ui' | 'lecture_education' | 'marketing_ads' | 'text_content' | 'engineering_drafting' | 'operational_manual' | 'other';
/**
 * Характер задачи:
 * - static: Создание продукта (код, дизайн, текст)
 * - dynamic: Операционные действия (размещение, общение, модерация)
 */
export type TaskNature = 'static' | 'dynamic';
export declare class ScoutAgent {
    private profile;
    private services;
    private learnedPatterns;
    private projectRoot;
    private browser?;
    readonly agentName: string;
    readonly agentRole: string;
    readonly expertise: string;
    constructor(profile: ProfileConfig, projectRoot: string, browser?: BrowserService);
    /**
     * [LEGACY] Анализирует задачу шаблонным методом.
     * Используйте analyzeAndProposeExpert() для мульти-агентной системы.
     */
    analyzeAndPropose(job: RawJob): ProposalResult;
    /**
     * Анализирует задачу и делегирует генерацию предложения
     * специализированному агенту через Router.
     *
     * Пайплайн:
     * 1. Категоризация задачи
     * 2. Оценка выполнимости (feasibility)
     * 3. Маршрутизация → специализированный агент
     * 4. Генерация экспертного предложения с обоснованиями
     * 5. Самообучение
     */
    analyzeAndProposeExpert(job: RawJob): Promise<ProposalResult>;
    /**
     * Генерация детального плана исполнения (Execution Plan)
     * по методологии "Суперагента" (Best Practices 2026).
     */
    private generateExecutionPlan;
    private detectCategory;
    private assessFeasibility;
    private checkRequiredServices;
    private estimateEffort;
    private analyzeReward;
    private generateProposal;
    private createUnderstanding;
    private determineTechStack;
    private createImplementationPlan;
    private generateClarifyingQuestions;
    private generateWarnings;
    private generateOperatorNotes;
    private saveAnalysisPattern;
    private generateSkillFile;
    private loadAvailableServices;
    private loadLearnedPatterns;
    private saveLearnedPatterns;
    private matchesAny;
    private checkSkillCoverage;
    private isVagueDescription;
    private calculateConfidence;
    private extractSpecificPlatform;
    private hasServiceFor;
    /**
     * Sherlock's Deep Deduction Skill: Многоэтапное исследование через Perplexity
     */
    private performDeepDeduction;
    /**
     * Sherlock's Technical Recon: Анализ стека сайта через браузер
     */
    private performTechnicalRecon;
    /**
     * Логика Шерлока по расчету рейтинга задачи (0-100)
     */
    private calculateTaskScore;
    /**
     * Обработка всех вложений к задаче через мультимодальный Gemini
     */
    private handleAttachments;
}
//# sourceMappingURL=scout.d.ts.map