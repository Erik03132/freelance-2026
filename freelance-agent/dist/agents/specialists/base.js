"use strict";
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
Object.defineProperty(exports, "__esModule", { value: true });
exports.BaseSpecialist = exports.PRAGMATIC_PRINCIPLES = void 0;
const ai_1 = require("../../utils/ai");
const constitution_1 = require("../../constants/constitution");
/**
 * Прагматичные принципы разработки (Pragmatic Principles)
 * Применяются ко всем агентам для исключения овер-инжиниринга.
 */
exports.PRAGMATIC_PRINCIPLES = constitution_1.CONSTITUTION.PRAGMATIC_PRINCIPLES;
// =========================================================
// BASE SPECIALIST
// =========================================================
class BaseSpecialist {
    /**
     * Переформулировать задачу своими словами (показать понимание)
     */
    reformulateTask(job) {
        const desc = job.description || '';
        const sentences = desc.split(/[.!?]/).filter(s => s.trim().length > 15);
        if (sentences.length >= 2) {
            return `Понятно, что нужно: ${sentences[0].trim().toLowerCase()}. ${sentences[1].trim()}.`;
        }
        if (sentences.length === 1) {
            return `Понятно, что нужно: ${sentences[0].trim().toLowerCase()}.`;
        }
        return `Вижу задачу: ${job.title.toLowerCase()}.`;
    }
    /**
     * Сгенерировать полное предложение с учетом инсайтов от Perplexity и приложенных файлов
     */
    async generateProposal(job, userName = 'Ваш исполнитель', insights) {
        const techStack = this.recommendTechStack(job);
        const plan = this.createPlan(job, techStack);
        const questions = this.generateQuestions(job);
        const prototype = this.specifyPrototype(job);
        const understanding = this.reformulateTask(job);
        const whyMe = this.explainWhyMe(job);
        // 1. Определение сложности
        const text = `${job.title} ${job.description}`.toLowerCase();
        const isSmallTask = this.matchesAny(text, [
            'баннер', 'логотип', 'иконк', 'картинк', 'превью', 'обложк',
            'простой', 'быстро', 'небольшой', 'маленький', 'легкий',
            'исправить', 'поправить', 'баг', 'кнопка', 'форма', 'скрипт',
            'banner', 'logo', 'fix', 'bug', 'small',
        ]);
        // 2. Подсчёт часов с жёстким ограничением для мелких задач
        let totalHours = plan.reduce((sum, step) => {
            const match = step.estimatedHours.match(/(\d+)-?(\d+)?/);
            if (match) {
                const min = parseInt(match[1]);
                const max = match[2] ? parseInt(match[2]) : min;
                return sum + (min + max) / 2;
            }
            return sum;
        }, 0);
        // Мелкие задачи — не больше 4 часов (КОНСТИТУЦИЯ v2)
        const pricing = constitution_1.CONSTITUTION.PRICING;
        if (isSmallTask) {
            totalHours = Math.min(totalHours, pricing.SMALL_TASK_MAX_HOURS || 4);
        }
        totalHours = Math.round(totalHours);
        // Дни: мелкие задачи — 1 день, крупные — расчёт
        const totalDays = isSmallTask ? '1' : Math.max(1, Math.ceil(totalHours / 8)).toString();
        // 3. Адекватное ценообразование
        let basePrice = Math.round(totalHours * pricing.HOURLY_RATE);
        basePrice = Math.max(basePrice, pricing.MIN_PRICE || 500);
        let roundedPrice = Math.ceil(basePrice / 100) * 100;
        const clientBudget = job.budget?.amount || 0;
        // Если клиент указал бюджет и он адекватен — не превышаем его
        if (clientBudget > 0 && clientBudget >= roundedPrice * 0.5) {
            roundedPrice = Math.min(roundedPrice, Math.round(clientBudget * 0.9));
            roundedPrice = Math.max(roundedPrice, pricing.MIN_PRICE || 500);
        }
        const finalPriceText = pricing.FORMAT
            .replace('{days}', totalDays)
            .replace('{price}', roundedPrice.toString());
        // 4. Очистка инсайтов от ссылок Perplexity [1][2][3]
        const cleanInsights = (str) => {
            if (!str)
                return '';
            return str.replace(/\[\d+\]/g, '').replace(/\s{2,}/g, ' ').trim();
        };
        // 5. AI-генерация оффера — ЖЁСТКИЙ промпт на лаконичность
        const techNames = techStack.slice(0, 2).map(t => t.name).join(' + ');
        const refinementPrompt = `
ТЫ — ${this.agentName}, элитный эксперт. Твоя экспертиза: ${this.expertise}. Напиши ОФФЕР на заказ.

ЗАДАЧА КЛИЕНТА: "${job.title}"

ТВОЯ АВТОРСКАЯ ПОЗИЦИЯ: ${whyMe}
ТВОЙ СТЕК: ${techNames}
СРОК И ЦЕНА: ${finalPriceText}

ЖЁСТКИЕ ПРАВИЛА (СТИЛЬ ИГОРЯ):
- МАКСИМУМ 3-8 предложений. Больше = провал.
- Начни с персонального приветствия: "Здравствуйте!" (НЕ используй "Приветствую"). Если из задачи можно понять имя клиента — обязательно используй его.
- Сразу скажи КАК сделаешь (1-2 технологии/решения) и ПОЧЕМУ это круто, опираясь на свою авторскую позицию.
- Отрази свою уникальную личность (${this.agentName}), но без кринжа и пафоса, только через профессионализм.
- В конце ОДНОЙ СТРОКОЙ укажи цену и сроки: "${finalPriceText}"
- После цены обязательно задай 2-3 конкретных, экспертных технических вопроса по ТЗ клиента.
- ЗАПРЕЩЕНО: пересказывать ТЗ, писать "Я понял задачу", использовать ** жирный **, ставить [1][2] ссылки, использовать хештеги (#).
- ЗАПРЕЩЕНО: слова "инвестиция", "трудозатраты", "спецификация", "Приветствую", "высокоэффективный".
- ЗАПРЕЩЕНО: списки с буллетами/номерами. Пиши сплошным текстом как в мессенджере (вопросы можно вынести отдельными абзацами).
- Самая последняя строчка документа ВСЕГДА ДОЛЖНА БЫТЬ: "С уважением, Игорь" (с новой строки). Без дополнительных призывов.

${cleanInsights(insights?.techResearch) ? `ИНСАЙТ (используй если релевантно): ${cleanInsights(insights?.techResearch)}` : ''}

Верни ТОЛЬКО текст оффера. Ничего больше.`;
        const capabilitiesList = this.capabilities.filter(c => c.enabled).map(c => c.name).join(', ');
        const systemPrompt = `Ты — элитный фрилансер по имени ${this.agentName}. 
Твоя экспертиза: ${this.expertise}. 
Твои супер-способности (инструменты автоматизации): ${capabilitiesList || 'Стандартные инструменты'}.
Пиши коротко, по делу, без воды, используя свой уникальный профессиональный стиль общения. Строго соблюдай все лимиты предложений (максимум 5).`;
        const finalTextFromAI = await (0, ai_1.generateWithGemini)(refinementPrompt, systemPrompt);
        // 6. Финальная очистка: убираем маркдаун, [ссылки], лишние пробелы
        let cleanedText = (finalTextFromAI || '')
            .replace(/\*\*/g, '') // убираем жирный
            .replace(/\[\d+\]/g, '') // убираем [1][2][3]
            .replace(/^[-•]\s*/gm, '') // убираем буллеты
            .replace(/^\d+\.\s*/gm, '') // убираем нумерацию
            .replace(/\s{2,}/g, ' ') // убираем двойные пробелы
            .trim();
        // Заменяем "Приветствую" если AI всё-таки вставил
        cleanedText = cleanedText
            .replace(/^Приветствую[.!]?\s*/i, 'Привет! ')
            .replace(/^Добрый день[.!]?\s*/i, 'Привет! ');
        return {
            greeting: 'Привет!',
            understanding,
            whyMe,
            techStack,
            plan,
            questions,
            prototype: prototype || undefined,
            totalHours,
            totalDays,
            fullText: cleanedText || `Привет! Сделаю на ${techNames}. ${finalPriceText}. Готов начать сегодня.`,
        };
    }
    // Вспомогательные
    matchesAny(text, keywords) {
        return keywords.some(keyword => text.toLowerCase().includes(keyword));
    }
    extractFromText(text, patterns) {
        const found = [];
        for (const [name, keywords] of Object.entries(patterns)) {
            if (keywords.some(k => text.toLowerCase().includes(k))) {
                found.push(name);
            }
        }
        return found;
    }
}
exports.BaseSpecialist = BaseSpecialist;
