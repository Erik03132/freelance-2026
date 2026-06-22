/**
 * Router Agent — Диспетчер задач
 *
 * Определяет, какому специализированному агенту передать задачу.
 * Для комплексных задач создаёт оркестрацию нескольких агентов.
 */
import { RawJob } from '../../models/job';
import { TaskCategory } from '../scout';
export type AgentType = 'webdev' | 'bot' | 'design' | 'data' | 'content' | 'devops' | 'architecture' | 'ads';
export interface RoutingDecision {
    primaryAgent: AgentType;
    supportAgents: AgentType[];
    mode: 'single' | 'sequential' | 'parallel';
    rationale: string;
    category: TaskCategory;
}
/**
 * Маршрутизация задачи к специализированному агенту
 */
export declare function routeTask(job: RawJob, category: TaskCategory): RoutingDecision;
//# sourceMappingURL=router.d.ts.map