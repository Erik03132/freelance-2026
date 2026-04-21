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
const scout_1 = require("./agents/scout");
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const storage_1 = require("./services/storage");
async function analyzeTgBot() {
    // 1. Setup Environment
    const projectRoot = path.join(__dirname, '..');
    const envContent = fs.readFileSync(path.join(projectRoot, '.env'), 'utf-8');
    const geminiMatch = envContent.match(/GEMINI_API_KEY=(.*)/);
    const pplxMatch = envContent.match(/PERPLEXITY_API_KEY=(.*)/);
    if (geminiMatch)
        process.env.GEMINI_API_KEY = geminiMatch[1].trim();
    if (pplxMatch)
        process.env.PERPLEXITY_API_KEY = pplxMatch[1].trim();
    const profilePath = path.join(projectRoot, 'config', 'profile.json');
    const dbPath = 'freelance.db'; // StorageService handles the path
    const profile = JSON.parse(fs.readFileSync(profilePath, 'utf-8'));
    const scout = new scout_1.ScoutAgent(profile, projectRoot);
    const storage = new storage_1.StorageService(dbPath);
    storage.init();
    const job = {
        platform: 'kwork',
        url: 'https://kwork.ru/projects/tg-bot-stats-custom',
        title: 'Telegram Бот для сбора статистики и рассылки',
        description: 'Бот должен собирать статистику с каналов (просмотры, реакции, пересылки) и делать рассылки по пользователям. Также нужна админ-панель для управления.',
        budget: { amount: 15000, currency: 'RUB', type: 'fixed' },
        skills: ['Telegram Bot', 'Python', 'Node.js'],
        postedAt: new Date(),
        status: 'new'
    };
    console.log('🕵️‍♂️ Sherlock is investigating (Task #5)...');
    // Perform detailed analysis
    const result = await scout.analyzeAndProposeExpert(job);
    // Map analysis to DB fields
    const enrichedJob = {
        ...job,
        expert_proposal: result.proposal,
        sherlock_score: result.score || 0,
        analysis_report: result.operatorNotes,
        status: 'analyzed'
    };
    await storage.saveJob(enrichedJob);
    console.log('\n' + '='.repeat(80));
    console.log('  🤖 ЭКСПЕРТНОЕ ПРЕДЛОЖЕНИЕ (PROPOSAL)');
    console.log('='.repeat(80) + '\n');
    console.log(result.proposal);
    console.log('\n' + '='.repeat(80));
    console.log('  🔍 ИНТЕЛЛЕКТ-ОТЧЕТ (INTELLIGENCE REPORT)');
    console.log('='.repeat(80) + '\n');
    console.log(result.operatorNotes);
    console.log('\n' + '='.repeat(80));
}
analyzeTgBot().catch(console.error);
