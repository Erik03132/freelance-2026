/**
 * Специализированные агенты-исполнители
 *
 * Экспорт всех агентов и Router для маршрутизации задач.
 */
export { BaseSpecialist } from './base';
export type { TechStackRecommendation, PlanStep, PrototypeSpec, ExpertProposal, AgentCapability, DeepDeductionResult, } from './base';
export { routeTask } from './router';
export type { RoutingDecision, AgentType } from './router';
export { WebDevAgent } from './webdev';
export { BotAgent } from './bot';
export { DesignAgent } from './design';
export { DataAgent } from './data';
export { ContentAgent } from './content';
export { DevOpsAgent } from './devops';
export { ArchitectureAgent } from './architecture';
export { AdsSpecialist } from './ads';
import { BaseSpecialist } from './base';
import { AgentType } from './router';
/**
 * Получить экземпляр специализированного агента по типу
 */
export declare function getAgent(type: AgentType): BaseSpecialist;
/**
 * Получить список доступных агентов
 */
export declare function getAvailableAgents(): {
    type: string;
    name: string;
    emoji: string;
}[];
//# sourceMappingURL=index.d.ts.map