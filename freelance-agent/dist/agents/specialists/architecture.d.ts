import { RawJob } from '../../models/job';
import { TaskCategory } from '../scout';
import { BaseSpecialist, TechStackRecommendation, PlanStep, PrototypeSpec, AgentCapability } from './base';
export declare class ArchitectureAgent extends BaseSpecialist {
    readonly agentType = "architecture";
    readonly agentName = "\u041A\u0443\u043B\u0438\u0431\u0438\u043D (\u0418\u043D\u0436\u0435\u043D\u0435\u0440-\u041A\u043E\u043D\u0441\u0442\u0440\u0443\u043A\u0442\u043E\u0440)";
    readonly emoji = "\uD83D\uDCD0";
    readonly expertise = "\u0418\u043D\u0436\u0435\u043D\u0435\u0440-\u043A\u043E\u043D\u0441\u0442\u0440\u0443\u043A\u0442\u043E\u0440 \u0441 \u043E\u043F\u044B\u0442\u043E\u043C \u0432 \u043F\u0440\u043E\u043C\u044B\u0448\u043B\u0435\u043D\u043D\u043E\u043C \u0434\u0438\u0437\u0430\u0439\u043D\u0435 \u0438 \u043C\u0435\u0431\u0435\u043B\u044C\u043D\u043E\u043C \u043F\u0440\u043E\u0438\u0437\u0432\u043E\u0434\u0441\u0442\u0432\u0435. \u041F\u0440\u043E\u0435\u043A\u0442\u0438\u0440\u043E\u0432\u0430\u043D\u0438\u0435 \u0447\u0435\u0440\u0442\u0435\u0436\u0435\u0439 \u043F\u043E \u0413\u041E\u0421\u0422/ISO, \u0440\u0430\u0441\u0447\u0435\u0442 \u043D\u0430\u0433\u0440\u0443\u0437\u043E\u043A \u0438 \u0441\u043F\u0435\u0446\u0438\u0444\u0438\u043A\u0430\u0446\u0438\u0439 \u043C\u0430\u0442\u0435\u0440\u0438\u0430\u043B\u043E\u0432.";
    readonly supportedCategories: TaskCategory[];
    readonly capabilities: AgentCapability[];
    recommendTechStack(job: RawJob): TechStackRecommendation[];
    createPlan(job: RawJob, techStack: TechStackRecommendation[]): PlanStep[];
    generateQuestions(job: RawJob): string[];
    specifyPrototype(job: RawJob): PrototypeSpec | null;
    protected explainWhyMe(job: RawJob): string;
}
//# sourceMappingURL=architecture.d.ts.map