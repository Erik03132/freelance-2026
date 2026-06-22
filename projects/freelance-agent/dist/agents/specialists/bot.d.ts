/**
 * 🤖 Bot Agent — Специалист по Telegram/Discord ботам
 *
 * Эксперт по:
 * - Telegram: aiogram 3.x, python-telegram-bot, Telegraf.js, grammY
 * - Discord: discord.py, discord.js
 * - Архитектура: FSM (конечные автоматы), inline keyboards, payments
 * - Паттерны: handlers → filters → middlewares → database
 *
 * Прокачан знаниями из:
 * - aiogram 3.x examples (50+ примеров)
 * - aiogram_dialog (FSM-диалоги)
 * - tgbot_template (продакшн структура)
 * - Telegram Bot API documentation
 */
import { RawJob } from '../../models/job';
import { TaskCategory } from '../scout';
import { BaseSpecialist, TechStackRecommendation, PlanStep, PrototypeSpec, AgentCapability } from './base';
export declare class BotAgent extends BaseSpecialist {
    readonly agentType = "bot";
    readonly agentName: string;
    readonly emoji = "\uD83E\uDD16";
    readonly expertise: string;
    readonly supportedCategories: TaskCategory[];
    readonly capabilities: AgentCapability[];
    recommendTechStack(job: RawJob): TechStackRecommendation[];
    createPlan(job: RawJob, techStack: TechStackRecommendation[]): PlanStep[];
    generateQuestions(job: RawJob): string[];
    specifyPrototype(job: RawJob): PrototypeSpec | null;
    protected explainWhyMe(job: RawJob): string;
}
//# sourceMappingURL=bot.d.ts.map