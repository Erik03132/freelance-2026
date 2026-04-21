# Адаптированный план реализации Freelance Agent MVP

> **Версия:** 3.0 (с учётом вашего стека)  
> **Дата:** 2026-03-23  
> **Стек:** TypeScript + Playwright + Gemini Pro + Neon PostgreSQL + Telegram Bot + Vercel

---

## Ваш стек инструментов

| Компонент | Технология | Назначение |
|-----------|------------|------------|
| **LLM** | Gemini Pro API | Генерация предложений, семантический матчинг, планы решений |
| **База данных** | Neon PostgreSQL + MCP | Хранение задач, профиля, откликов, логов |
| **Уведомления** | Telegram Bot API | Алёрты о задачах, отчёты, подтверждение отправки |
| **Браузер** | Antigravity MCP + Playwright | Скрейпинг бирж, авторизация |
| **Email** | SendPost | Email-уведомления, отчёты |
| **Язык** | TypeScript | Единый код для всех компонентов |
| **Деплой** | Vercel Serverless Functions | Запуск по расписанию (cron) |
| **Прототипы** | Vercel/Netlify | Деплои демо-проектов |
| **Код** | GitHub | Хранение прототипов, версионирование |

---

## Обновлённая архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                    Vercel Serverless Functions                   │
│                         (cron: 09:00 daily)                      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Scheduler Agent (TypeScript)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Antigravity│→ │    Gemini    │→ │    Neon PostgreSQL   │  │
│  │   MCP Browser│  │    Pro API   │  │    (via MCP)         │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
        ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
        │   Telegram   │ │   SendPost   │ │    Vercel    │
        │     Bot      │ │    Email     │ │   Deploy     │
        └──────────────┘ └──────────────┘ └──────────────┘
```

---

## Схема базы данных (Neon PostgreSQL)

```sql
-- Профиль пользователя
CREATE TABLE user_profile (
    id SERIAL PRIMARY KEY,
    name TEXT,
    nickname TEXT,
    timezone TEXT DEFAULT 'Europe/Moscow',
    portfolio_github TEXT,
    portfolio_website TEXT,
    portfolio_linkedin TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Навыки пользователя
CREATE TABLE user_skills (
    id SERIAL PRIMARY KEY,
    skill_name TEXT UNIQUE NOT NULL,
    skill_level REAL CHECK (skill_level >= 0 AND skill_level <= 1),
    category TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Синонимы навыков
CREATE TABLE skill_synonyms (
    id SERIAL PRIMARY KEY,
    canonical_skill TEXT REFERENCES user_skills(skill_name) ON DELETE CASCADE,
    synonym TEXT NOT NULL,
    UNIQUE (canonical_skill, synonym)
);

-- Задачи (jobs)
CREATE TABLE jobs (
    id TEXT PRIMARY KEY,
    platform TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    budget_amount REAL,
    budget_currency TEXT,
    budget_type TEXT CHECK (budget_type IN ('fixed', 'hourly')),
    hourly_min REAL,
    hourly_max REAL,
    category TEXT,
    skills_extracted TEXT[],
    posted_at TIMESTAMPTZ,
    
    -- Клиент
    client_name TEXT,
    client_country TEXT,
    client_rating REAL,
    client_payment_verified BOOLEAN DEFAULT FALSE,
    
    -- Статистика
    proposals_count INTEGER,
    
    -- Метрики
    skill_match_score REAL,
    clarity_score REAL,
    
    -- Статус
    status TEXT DEFAULT 'new' CHECK (status IN (
        'new', 'filtered_out_skills', 'filtered_out_clarity',
        'shortlisted', 'prototype_ready', 'proposal_sent',
        'in_negotiation', 'closed', 'ignored'
    )),
    
    -- Метаданные
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    scraped_at TIMESTAMPTZ DEFAULT NOW()
);

-- Отклики (proposals)
CREATE TABLE proposals (
    id SERIAL PRIMARY KEY,
    job_id TEXT REFERENCES jobs(id) ON DELETE CASCADE,
    letter_text TEXT,
    demo_url TEXT,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'sent', 'rejected', 'accepted')),
    sent_at TIMESTAMPTZ,
    response_at TIMESTAMPTZ,
    response_status TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Пользовательские действия (для обучения)
CREATE TABLE user_actions (
    id SERIAL PRIMARY KEY,
    job_id TEXT REFERENCES jobs(id) ON DELETE CASCADE,
    action_type TEXT NOT NULL,
    action_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Логи запусков
CREATE TABLE run_logs (
    id SERIAL PRIMARY KEY,
    run_date DATE DEFAULT CURRENT_DATE,
    run_time TIMESTAMPTZ DEFAULT NOW(),
    platform TEXT,
    jobs_scraped INTEGER,
    jobs_filtered INTEGER,
    jobs_shortlisted INTEGER,
    prototypes_generated INTEGER,
    proposals_generated INTEGER,
    errors TEXT[],
    duration_seconds INTEGER
);

-- Индексы
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_posted_at ON jobs(posted_at);
CREATE INDEX idx_jobs_skill_match ON jobs(skill_match_score DESC);
CREATE INDEX idx_jobs_platform ON jobs(platform);
CREATE INDEX idx_proposals_status ON proposals(status);
CREATE INDEX idx_user_actions_job ON user_actions(job_id);
```

---

# MVP #1 — Базовый скрейпинг и фильтрация (2 недели)

## Неделя 1: Настройка инфраструктуры

### День 1-2: Инициализация проекта

**Задачи:**
- [ ] **1.1.1** Создать структуру проекта
```
freelance-agent/
├── .vercel/
│   └── project.json
├── api/
│   ├── cron/
│   │   └── run-agent.ts          # Serverless function для cron
│   ├── telegram/
│   │   └── webhook.ts            # Telegram webhook
│   └── health.ts                 # Health check endpoint
├── src/
│   ├── agents/
│   │   ├── scheduler.ts
│   │   ├── scraper.ts
│   │   ├── matching.ts
│   │   └── proposal.ts
│   ├── adapters/
│   │   ├── base.ts
│   │   ├── upwork.ts
│   │   └── flru.ts
│   ├── services/
│   │   ├── database.ts           # Neon PostgreSQL client
│   │   ├── gemini.ts             # Gemini Pro API client
│   │   ├── telegram.ts           # Telegram Bot client
│   │   └── email.ts              # SendPost client
│   ├── models/
│   │   ├── job.ts
│   │   └── profile.ts
│   └── utils/
│       ├── logger.ts
│       └── delays.ts
├── config/
│   └── profile.json
├── vercel.json                     # Vercel config + cron
├── package.json
└── tsconfig.json
```

- [ ] **1.1.2** Инициализировать проект
```bash
npm init -y
npm install typescript @types/node ts-node --save-dev
npm install playwright --save
npm install @google/generative-ai --save
npm install node-telegram-bot-api --save
npm install @vercel/postgres --save
npm install vercel --save-dev
```

- [ ] **1.1.3** Создать `vercel.json` с cron
```json
{
  "version": 2,
  "functions": {
    "api/cron/run-agent.ts": {
      "schedule": "0 9 * * 1-5"
    }
  },
  "env": {
    "GEMINI_API_KEY": "@gemini-api-key",
    "TELEGRAM_BOT_TOKEN": "@telegram-bot-token",
    "TELEGRAM_CHAT_ID": "@telegram-chat-id",
    "POSTGRES_URL": "@neon-postgres-url",
    "SENDPOST_API_KEY": "@sendpost-api-key"
  }
}
```

---

### День 3-4: Подключение Neon PostgreSQL через MCP

**Задачи:**
- [ ] **1.2.1** Создать `src/services/database.ts`
```typescript
import { sql } from '@vercel/postgres';

export class DatabaseService {
  // Профиль
  async getProfile() {
    const result = await sql`SELECT * FROM user_profile LIMIT 1`;
    return result.rows[0];
  }

  async updateProfile(profile: any) {
    await sql`
      INSERT INTO user_profile (name, nickname, portfolio_github, portfolio_website)
      VALUES (${profile.name}, ${profile.nickname}, ${profile.github}, ${profile.website})
      ON CONFLICT (id) DO UPDATE SET
        name = EXCLUDED.name,
        nickname = EXCLUDED.nickname,
        updated_at = NOW()
    `;
  }

  // Навыки
  async getSkills(): Promise<Map<string, number>> {
    const result = await sql`SELECT skill_name, skill_level FROM user_skills`;
    return new Map(result.rows.map(r => [r.skill_name, r.skill_level]));
  }

  async getSkillSynonyms(): Promise<Record<string, string[]>> {
    const result = await sql`SELECT canonical_skill, synonym FROM skill_synonyms`;
    const synonyms: Record<string, string[]> = {};
    for (const row of result.rows) {
      if (!synonyms[row.canonical_skill]) {
        synonyms[row.canonical_skill] = [];
      }
      synonyms[row.canonical_skill].push(row.synonym);
    }
    return synonyms;
  }

  // Задачи
  async saveJob(job: any): Promise<void> {
    await sql`
      INSERT INTO jobs (
        id, platform, url, title, description, budget_amount,
        budget_currency, budget_type, skills_extracted, posted_at,
        client_name, client_payment_verified, scraped_at
      ) VALUES (
        ${job.id}, ${job.platform}, ${job.url}, ${job.title},
        ${job.description}, ${job.budget?.amount}, ${job.budget?.currency},
        ${job.budget?.type}, ${job.skills}, ${job.postedAt},
        ${job.client?.name}, ${job.client?.paymentVerified}, NOW()
      )
      ON CONFLICT (id) DO UPDATE SET
        title = EXCLUDED.title,
        updated_at = NOW()
    `;
  }

  async getJobsByStatus(status: string, limit = 50) {
    const result = await sql`
      SELECT * FROM jobs 
      WHERE status = ${status} 
      ORDER BY posted_at DESC 
      LIMIT ${limit}
    `;
    return result.rows;
  }

  async updateJobStatus(jobId: string, status: string, metrics?: any) {
    await sql`
      UPDATE jobs SET 
        status = ${status},
        skill_match_score = ${metrics?.skillMatchScore || null},
        clarity_score = ${metrics?.clarityScore || null},
        updated_at = NOW()
      WHERE id = ${jobId}
    `;
  }

  // Предложения
  async saveProposal(jobId: string, proposal: any) {
    await sql`
      INSERT INTO proposals (job_id, letter_text, demo_url, status)
      VALUES (${jobId}, ${proposal.letter}, ${proposal.demoUrl}, 'draft')
    `;
  }

  // Логи
  async logRun(stats: any) {
    await sql`
      INSERT INTO run_logs (
        jobs_scraped, jobs_filtered, jobs_shortlisted,
        prototypes_generated, proposals_generated, errors, duration_seconds
      ) VALUES (
        ${stats.scraped}, ${stats.filtered}, ${stats.shortlisted},
        ${stats.prototypes}, ${stats.proposals}, ${stats.errors}, ${stats.duration}
      )
    `;
  }
}
```

- [ ] **1.2.2** Настроить подключение Neon через MCP
```bash
# В Antigravity настроить MCP-сервер для PostgreSQL
# Добавить POSTGRES_URL из Neon dashboard
```

---

### День 5-7: Gemini Pro + Telegram Bot

**Задачи:**
- [ ] **1.3.1** Создать `src/services/gemini.ts`
```typescript
import { GoogleGenerativeAI } from '@google/generative-ai';

export class GeminiService {
  private genAI: GoogleGenerativeAI;
  private model: any;

  constructor(apiKey: string) {
    this.genAI = new GoogleGenerativeAI(apiKey);
    this.model = this.genAI.getGenerativeModel({ model: 'gemini-pro' });
  }

  async generateProposal(job: any, profile: any): Promise<string> {
    const prompt = `
Создай персонализированное предложение для фриланс-задачи.

ЗАДАЧА:
Заголовок: ${job.title}
Описание: ${job.description}
Бюджет: ${job.budget?.amount || 'не указан'} ${job.budget?.currency || ''}
Навыки: ${job.skills_extracted?.join(', ')}

ПРОФИЛЬ ФРИЛАНСЕРА:
Имя: ${profile.name}
Навыки: ${JSON.stringify(profile.skills)}
Портфолио: ${profile.portfolio_website}

Требования:
1. Краткое приветствие
2. Показать понимание задачи
3. Объяснить почему подхожу
4. Предложить план решения
5. Призыв к действию

Тон: профессиональный, дружелюбный, без шаблонных фраз.
`;

    const result = await this.model.generateContent(prompt);
    return result.response.text();
  }

  async calculateSkillMatch(jobSkills: string[], userSkills: Map<string, number>): Promise<number> {
    const prompt = `
Рассчитай процент совпадения навыков (0-1).

Навыки задачи: ${jobSkills.join(', ')}
Навыки пользователя: ${Array.from(userSkills.entries()).map(([s, l]) => `${s}:${l}`).join(', ')}

Верни только число от 0 до 1 с точностью 2 знака.
`;

    const result = await this.model.generateContent(prompt);
    const score = parseFloat(result.response.text());
    return Math.max(0, Math.min(1, score));
  }

  async assessClarity(description: string): Promise<number> {
    const prompt = `
Оцени понятность ТЗ от 0 до 1.

Описание задачи:
${description}

Критерии:
- Наличие стека технологий
- Есть примеры/референсы
- Описаны пользовательские сценарии
- Есть acceptance criteria
- Детальное описание (>100 слов)

Верни только число от 0 до 1 с точностью 2 знака.
`;

    const result = await this.model.generateContent(prompt);
    const score = parseFloat(result.response.text());
    return Math.max(0, Math.min(1, score));
  }

  async generateSolutionPlan(job: any): Promise<string> {
    const prompt = `
Создай структурированный план решения задачи.

ЗАДАЧА:
${job.title}
${job.description}

Формат:
1. Краткая переформулировка задачи
2. Основная идея архитектуры/дизайна
3. Основные шаги реализации
4. Возможные риски и вопросы к заказчику

Объём: ~300 слов.
`;

    const result = await this.model.generateContent(prompt);
    return result.response.text();
  }
}
```

- [ ] **1.3.2** Создать `src/services/telegram.ts`
```typescript
import TelegramBot from 'node-telegram-bot-api';

export class TelegramService {
  private bot: TelegramBot;
  private chatId: string;

  constructor(token: string, chatId: string) {
    this.bot = new TelegramBot(token, { polling: false });
    this.chatId = chatId;
  }

  async sendNewJobAlert(job: any): Promise<void> {
    const message = `
🔔 **Новая подходящая задача**

**Платформа:** ${job.platform}
**Заголовок:** ${job.title}
**Бюджет:** ${job.budget?.amount || 'N/A'} ${job.budget?.currency || ''}
**Совпадение:** ${(job.skill_match_score * 100).toFixed(0)}%
**ТЗ:** ${(job.clarity_score * 100).toFixed(0)}%

[Открыть задачу](${job.url})
    `;

    await this.bot.sendMessage(this.chatId, message, {
      parse_mode: 'Markdown',
      reply_markup: {
        inline_keyboard: [
          [{ text: '👍 Интересно', callback_data: `like_${job.id}` }],
          [{ text: '👎 Не интересно', callback_data: `dislike_${job.id}` }],
          [{ text: '📝 Открыть черновик', callback_data: `draft_${job.id}` }]
        ]
      }
    });
  }

  async sendDailyReport(stats: any): Promise<void> {
    const message = `
📊 **Ежедневный отчёт**

📥 Задач найдено: ${stats.scraped}
❌ Отфильтровано: ${stats.filtered}
✅ В коротком списке: ${stats.shortlisted}
🛠 Прототипов: ${stats.prototypes}
📝 Предложений: ${stats.proposals}

Время выполнения: ${stats.duration}с
    `;

    await this.bot.sendMessage(this.chatId, message, { parse_mode: 'Markdown' });
  }

  async sendErrorAlert(error: string): Promise<void> {
    await this.bot.sendMessage(this.chatId, `❌ **Ошибка агента:**\n${error}`, {
      parse_mode: 'Markdown'
    });
  }

  setupCallbacks(handlers: any): void {
    this.bot.on('callback_query', async (query) => {
      const [action, jobId] = query.data?.split('_') || [];
      
      if (action === 'like') {
        await handlers.onInterested(jobId);
        await this.bot.answerCallbackQuery(query.id, { text: '✓ Помечено как интересное' });
      } else if (action === 'dislike') {
        await handlers.onNotInterested(jobId);
        await this.bot.answerCallbackQuery(query.id, { text: '✓ Помечено как неинтересное' });
      } else if (action === 'draft') {
        await handlers.onViewDraft(jobId);
      }
    });
  }
}
```

- [ ] **1.3.3** Создать `src/services/email.ts` (SendPost)
```typescript
import axios from 'axios';

export class EmailService {
  private apiKey: string;
  private baseUrl = 'https://api.sendpost.io/v1';

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  async sendWeeklyReport(email: string, stats: any): Promise<void> {
    await axios.post(
      `${this.baseUrl}/send`,
      {
        from: { email: 'noreply@yourdomain.com', name: 'Freelance Agent' },
        to: [{ email }],
        subject: `Еженедельный отчёт: ${stats.totalJobs} задач, ${stats.proposals} откликов`,
        html: this.generateWeeklyReportHTML(stats)
      },
      {
        headers: { 'Authorization': `Bearer ${this.apiKey}` }
      }
    );
  }

  private generateWeeklyReportHTML(stats: any): string {
    return `
      <h1>Еженедельный отчёт</h1>
      <p>Задач найдено: ${stats.totalJobs}</p>
      <p>Откликов отправлено: ${stats.proposals}</p>
      <p>Диалогов начато: ${stats.dialogues}</p>
    `;
  }
}
```

---

## Неделя 2: Адаптеры и скрейпинг

### День 8-10: Адаптер Upwork

**Задачи:**
- [ ] **1.4.1** Создать `src/adapters/upwork.ts` (используем код из DETAILED_IMPLEMENTATION_PLAN.md с интеграцией в Neon)

### День 11-12: Адаптер FL.ru

**Задачи:**
- [ ] **1.5.1** Создать `src/adapters/flru.ts`

### День 13-14: Scheduler Agent

**Задачи:**
- [ ] **1.6.1** Создать `src/agents/scheduler.ts` с полной интеграцией
- [ ] **1.6.2** Создать `api/cron/run-agent.ts` для Vercel cron
- [ ] **1.6.3** Протестировать запуск

---

# MVP #2 — Умный матчинг (2 недели)

## Неделя 3: Gemini для матчинга

**Задачи:**
- [ ] **2.1** Интегрировать `GeminiService.calculateSkillMatch()`
- [ ] **2.2** Интегрировать `GeminiService.assessClarity()`
- [ ] **2.3** Сохранение метрик в Neon
- [ ] **2.4** Telegram-алёрты для задач с score > threshold

---

## Неделя 4: Генерация предложений

**Задачи:**
- [ ] **2.5** Интегрировать `GeminiService.generateProposal()`
- [ ] **2.6** Сохранение черновиков в базу
- [ ] **2.7** Telegram-кнопки для подтверждения отправки
- [ ] **2.8** Update статуса в базе

---

# MVP #3 — Прототипы и защита (2 недели)

## Неделя 5: Vercel Deploy API

**Задачи:**
- [ ] **3.1** Интеграция с Vercel Deploy API
- [ ] **3.2** Создание scaffold Next.js проектов
- [ ] **3.3** Авто-деплой прототипов
- [ ] **3.4** Сохранение demo_url в базу

---

## Неделя 6: Dashboard и отчёты

**Задачи:**
- [ ] **3.5** Telegram-команды: /status, /jobs, /stats
- [ ] **3.6** Еженедельные email-отчёты через SendPost
- [ ] **3.7** Health check endpoint `/api/health`
- [ ] **3.8** Логирование ошибок и мониторинг

---

## Итоговый чеклист

### Инфраструктура
- [ ] Vercel проект создан
- [ ] Neon PostgreSQL подключён через MCP
- [ ] Gemini Pro API ключ настроен
- [ ] Telegram Bot создан и настроен
- [ ] SendPost API ключ настроен
- [ ] Vercel cron настроен (0 9 * * 1-5)

### MVP #1
- [ ] Адаптер Upwork работает
- [ ] Адаптер FL.ru работает
- [ ] Задачи сохраняются в Neon
- [ ] Telegram-алёрты приходят
- [ ] Cron запускается по расписанию

### MVP #2
- [ ] Gemini считает skill_match_score
- [ ] Gemini считает clarity_score
- [ ] Предложения генерируются
- [ ] Telegram-кнопки работают

### MVP #3
- [ ] Прототипы деплоятся на Vercel
- [ ] Demo URL сохраняется в базу
- [ ] Еженедельные отчёты отправляются

---

## Следующий шаг

Начинаем с **Недели 1, День 1** — инициализация проекта. Готов приступить!
