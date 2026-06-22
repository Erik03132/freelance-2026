/**
 * Base Specialist Agent — Базовый класс для специализированных агентов
 *
 * Каждый специалист:
 * 1. Имеет системный промпт (экспертиза)
 * 2. Знает свой стек технологий
 * 3. Имеет шаблоны прототипов
 * 4. Генерирует экспертные предложения
 * 5. Создаёт прототипы (30% задачи)
 */
import { RawJob } from '../../models/job';
import { TaskCategory } from '../scout';
/**
 * Прагматичные принципы разработки (Pragmatic Principles)
 * Применяются ко всем агентам для исключения овер-инжиниринга.
 */
export declare const PRAGMATIC_PRINCIPLES: string;
export interface TechStackRecommendation {
    name: string;
    reason: string;
}
export interface PlanStep {
    order: number;
    title: string;
    description: string;
    deliverable: string;
    estimatedHours: string;
    rationale: string;
    canAutomate: boolean;
    automationTool?: string;
}
export interface MCPAction {
    server: string;
    tool: string;
    arguments: any;
    purpose: string;
}
export interface PrototypeSpec {
    type: string;
    files: Map<string, string>;
    mcpActions?: MCPAction[];
    description: string;
    completionPercent: number;
    whatIsImplemented: string[];
    whatIsLeft: string[];
    demoInstructions?: string;
}
/**
 * Результаты глубокого исследования задачи (Perplexity)
 */
export interface DeepDeductionResult {
    techResearch: string;
    competitorAnalysis: string;
    apiPitfalls: string;
    winProbability: number;
    upsellIdeas: string[];
    attachmentInsights?: string;
    siteTechStack?: string;
}
export interface ExpertProposal {
    greeting: string;
    understanding: string;
    whyMe: string;
    techStack: TechStackRecommendation[];
    plan: PlanStep[];
    questions: string[];
    prototype?: PrototypeSpec;
    totalHours: number;
    totalDays: string;
    fullText: string;
}
export interface AgentCapability {
    name: string;
    description: string;
    mcpServer?: string;
    sdk?: string;
    enabled: boolean;
}
export declare abstract class BaseSpecialist {
    abstract readonly agentType: string;
    abstract readonly agentName: string;
    abstract readonly emoji: string;
    abstract readonly expertise: string;
    abstract readonly capabilities: AgentCapability[];
    abstract readonly supportedCategories: TaskCategory[];
    /**
     * Определить стек технологий для задачи
     * С обоснованием каждого выбора
     */
    abstract recommendTechStack(job: RawJob): TechStackRecommendation[];
    /**
     * Создать детальный план реализации
     * С обоснованием «почему» для каждого шага
     */
    abstract createPlan(job: RawJob, techStack: TechStackRecommendation[]): PlanStep[];
    /**
     * Сгенерировать список уточняющих вопросов
     * Контекстных, экспертных — не шаблонных
     */
    abstract generateQuestions(job: RawJob): string[];
    /**
     * Определить, какой прототип создать для этой задачи
     */
    abstract specifyPrototype(job: RawJob): PrototypeSpec | null;
    /**
     * Переформулировать задачу своими словами (показать понимание)
     */
    protected reformulateTask(job: RawJob): string;
    /**
     * Объяснить, почему именно я подхожу для этой задачи
     */
    protected abstract explainWhyMe(job: RawJob): string;
    /**
     * Сгенерировать полное предложение с учетом инсайтов от Perplexity и приложенных файлов
     */
    generateProposal(job: RawJob, userName?: string, insights?: DeepDeductionResult): Promise<ExpertProposal>;
    protected matchesAny(text: string, keywords: string[]): boolean;
    protected extractFromText(text: string, patterns: Record<string, string[]>): string[];
}
//# sourceMappingURL=base.d.ts.map