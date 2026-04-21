/**
 * 💻 WebDev Agent — Специалист по веб-разработке
 *
 * Full-stack разработчик с экспертизой в:
 * - Mobile: Flutter, Dart, React Native (planned)
 * - Frontend: React 19, Next.js 15, Vue 3, Tailwind CSS, shadcn/ui
 * - Backend: FastAPI, NestJS, Express, Prisma, Drizzle
 * - Database: PostgreSQL, MongoDB, Redis, SQLite, Supabase
 * - Deploy: Vercel, Railway, Docker, Nginx
 *
 * Прокачан знаниями из:
 * - bulletproof-react (архитектура React)
 * - fastapi-best-practices (паттерны FastAPI)
 * - create-t3-app (T3 stack)
 * - realworld spec (эталон CRUD API)
 *
 * MCP-сервисы:
 * - Stitch MCP: генерация UI-экранов
 * - GitHub MCP: хранение кода прототипов (planned)
 * - Supabase MCP: мгновенная БД (planned)
 * - Vercel MCP: деплой прототипов (planned)
 */
import { RawJob } from '../../models/job';
import { TaskCategory } from '../scout';
import { BaseSpecialist, TechStackRecommendation, PlanStep, PrototypeSpec, AgentCapability } from './base';
export declare class WebDevAgent extends BaseSpecialist {
    readonly agentType = "webdev";
    readonly agentName: string;
    readonly emoji = "\uD83D\uDC77\u200D\u2642\uFE0F";
    readonly expertise: string;
    readonly supportedCategories: TaskCategory[];
    readonly capabilities: AgentCapability[];
    recommendTechStack(job: RawJob): TechStackRecommendation[];
    createPlan(job: RawJob, techStack: TechStackRecommendation[]): PlanStep[];
    generateQuestions(job: RawJob): string[];
    specifyPrototype(job: RawJob): PrototypeSpec | null;
    protected explainWhyMe(job: RawJob): string;
    private needsFrontend;
    private needsBackend;
    private needsDatabase;
}
//# sourceMappingURL=webdev.d.ts.map