import { RawJob } from '../../models/job';
import { TaskCategory } from '../scout';
import { BaseSpecialist, TechStackRecommendation, PlanStep, PrototypeSpec, AgentCapability } from './base';
export declare class AdsSpecialist extends BaseSpecialist {
    readonly agentType = "ads";
    readonly agentName: string;
    readonly emoji = "\uD83C\uDFAF";
    readonly expertise: string;
    readonly supportedCategories: TaskCategory[];
    readonly capabilities: AgentCapability[];
    recommendTechStack(job: RawJob): TechStackRecommendation[];
    createPlan(job: RawJob, techStack: TechStackRecommendation[]): PlanStep[];
    generateQuestions(job: RawJob): string[];
    specifyPrototype(job: RawJob): PrototypeSpec | null;
    protected explainWhyMe(job: RawJob): string;
}
//# sourceMappingURL=ads.d.ts.map