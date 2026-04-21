# Детальный план реализации Freelance Agent MVP

> **Версия:** 2.0 (с учётом анализа open-source проектов)  
> **Дата:** 2026-03-23  
> **Основано на:** UpworkScraper, Upwork-Job-Scraper, job-scrapper, Upwork-Auto-Jobs-Applier, Proposal Generator

---

## Сводная таблица этапов

| Этап | Название | Длительность | Ссылка на open-source | Статус |
|------|----------|--------------|----------------------|--------|
| **MVP #1** | Базовый скрейпинг и фильтрация | 2-3 недели | UpworkScraper, Upwork-Job-Scraper | ⬜ Не начат |
| **MVP #2** | Умный матчинг и прототипы | 3-4 недели | job-scrapper, skill-matching | ⬜ Не начат |
| **MVP #3** | Авто-предложения и защита | 2-3 недели | Upwork-Auto-Jobs-Applier, Proposal Generator | ⬜ Не начат |

---

# MVP #1 — Базовый скрейпинг и фильтрация (2-3 недели)

## Цель
Минимально работающий продукт: авторизация на Upwork/FL.ru, сбор задач, простая фильтрация по ключевым словам, черновики писем.

---

## Неделя 1: Настройка проекта и инфраструктуры

### День 1-2: Структура проекта

**Задачи:**
- [ ] **1.1.1** Создать структуру папок проекта
```
freelance-agent/
├── .agent/
│   └── rules/
│       └── agent-guide.md          # Системный промпт агента
├── config/
│   ├── profile.json                # Профиль пользователя и навыки
│   ├── platforms.json              # Конфигурация площадок
│   └── search.json                 # Фильтры поиска (из calebmwelsh)
├── src/
│   ├── agents/
│   │   ├── scheduler.ts            # Scheduler-агент
│   │   ├── scraper.ts              # Scraper-агент
│   │   ├── matching.ts             # Matching-агент
│   │   ├── filter.ts               # Filter-агент
│   │   ├── solution.ts             # Solution-Draft-агент
│   │   ├── protection.ts           # Protection-агент
│   │   └── proposal.ts             # Proposal-агент
│   ├── adapters/
│   │   ├── base.ts                 # Базовый интерфейс PlatformAdapter
│   │   ├── upwork.ts               # Адаптер Upwork
│   │   ├── freelancer.ts           # Адаптер Freelancer
│   │   ├── flru.ts                 # Адаптер FL.ru
│   │   └── kwork.ts                # Адаптер Kwork
│   ├── services/
│   │   ├── browser.ts              # Browser Controller
│   │   ├── storage.ts              # Storage Service (JSON/SQLite)
│   │   ├── skills_extractor.ts     # Skills Extractor
│   │   └── notifications.ts        # Notifications Service
│   ├── models/
│   │   ├── job.ts                  # Job Model
│   │   ├── profile.ts              # Profile Model
│   │   └── proposal.ts             # Proposal Model
│   └── utils/
│       ├── logger.ts               # Логирование
│       ├── delays.ts               # Человеческие задержки
│       └── helpers.ts              # Вспомогательные функции
├── data/
│   ├── jobs/
│   │   └── raw/                    # Сырые данные по площадкам
│   ├── processed/                  # Отфильтрованные задачи
│   └── db/
│       └── freelance.db            # SQLite база (на выбор)
├── prototypes/                     # Прототипы по задачам
├── proposals/                      # Черновики предложений
├── logs/                           # Логи запусков
├── reports/                        # Отчёты
├── package.json
├── tsconfig.json
└── README.md
```

- [ ] **1.1.2** Инициализировать Node.js проект
```bash
npm init -y
npm install typescript @types/node ts-node --save-dev
npm install playwright --save
npm install better-sqlite3 --save  # опционально
```

- [ ] **1.1.3** Создать базовые конфиги
  - `tsconfig.json`
  - `.env.example`
  - `.gitignore`

---

### День 3-4: Конфигурация профиля

**Задачи:**
- [ ] **1.2.1** Создать `config/profile.json` (из OPEN_SOURCE_PATTERNS.md)
```json
{
  "user": {
    "name": "Иван Петров",
    "nickname": "ivan_dev",
    "timezone": "Europe/Moscow",
    "portfolio": {
      "github": "https://github.com/username",
      "website": "https://mysite.com",
      "linkedin": "https://linkedin.com/in/username"
    }
  },
  "skills": {
    "React": 0.9,
    "Next.js": 0.8,
    "TypeScript": 0.85,
    "Node.js": 0.7,
    "Python": 0.6
  },
  "skillSynonyms": {
    "React": ["React.js", "ReactJS", "React 18"],
    "Node.js": ["Node", "NodeJS", "Express", "NestJS"]
  },
  "preferences": {
    "categories": ["Web Development", "Full Stack"],
    "ignoreCategories": ["Writing", "SMM"],
    "ignoreKeywords": ["ботнет", "спам", "кардинг"]
  },
  "matching": {
    "skillMatchThreshold": 0.7,
    "clarityThreshold": 0.6,
    "maxTasksPerDay": 5,
    "minBudget": 500,
    "requirePaymentVerified": true
  }
}
```

- [ ] **1.2.2** Создать `config/platforms.json`
```json
{
  "platforms": [
    {
      "name": "upwork",
      "displayName": "Upwork",
      "url": "https://www.upwork.com/nx/search/jobs/",
      "loginUrl": "https://www.upwork.com/ab/account-security/login",
      "enabled": true,
      "priority": 1,
      "selectors": {
        "jobCard": ".job-tile",
        "title": "h2 a[data-test=\"job-title\"]",
        "description": ".job-description .tokenized-string",
        "budget": ".job-budget",
        "skills": ".job-skills li a",
        "clientInfo": ".client-info"
      },
      "delays": {
        "pageLoad": 2000,
        "scroll": 1500,
        "click": 500,
        "betweenRequests": 3000
      }
    },
    {
      "name": "fl.ru",
      "displayName": "FL.ru",
      "url": "https://www.fl.ru/projects/",
      "loginUrl": "https://www.fl.ru/login/",
      "enabled": true,
      "priority": 2
    }
  ]
}
```

- [ ] **1.2.3** Создать `config/search.json` (из calebmwelsh/Upwork-Job-Scraper)
```json
{
  "search": {
    "upwork": {
      "filters": {
        "jobType": ["hourly", "fixed"],
        "experienceLevel": ["intermediate", "expert"],
        "budget": { "min": 500, "max": null },
        "paymentVerified": true,
        "proposals": { "max": 20 }
      },
      "categories": [
        "531770282580668428",
        "531770282584862733"
      ],
      "sortBy": "date",
      "limit": 50
    }
  }
}
```

---

### День 5-7: Browser Controller

**Задачи:**
- [ ] **1.3.1** Создать `src/services/browser.ts`
```typescript
import { chromium, Browser, Page, BrowserContext } from 'playwright';

export class BrowserService {
  private browser: Browser | null = null;
  private context: BrowserContext | null = null;
  private page: Page | null = null;

  async launch(headless = false): Promise<void> {
    this.browser = await chromium.launch({
      headless,
      args: ['--disable-blink-features=AutomationControlled']
    });
    
    this.context = await this.browser.newContext({
      viewport: { width: 1920, height: 1080 },
      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...'
    });
    
    this.page = await this.context.newPage();
  }

  async goto(url: string): Promise<void> {
    await this.page?.goto(url, { waitUntil: 'networkidle' });
  }

  async type(selector: string, text: string): Promise<void> {
    await this.page?.type(selector, text, { delay: 50 });
  }

  async click(selector: string): Promise<void> {
    await this.page?.click(selector, { delay: 300 });
  }

  async scrollToEnd(): Promise<void> {
    await this.page?.evaluate(async () => {
      await new Promise<void>((resolve) => {
        let totalHeight = 0;
        const distance = 100;
        const timer = setInterval(() => {
          window.scrollBy(0, distance);
          totalHeight += distance;
          if (window.innerHeight + window.scrollY >= document.body.scrollHeight - 100) {
            clearInterval(timer);
            resolve();
          }
        }, 100);
      });
    });
  }

  async extractText(selector: string): Promise<string> {
    return await this.page?.textContent(selector) || '';
  }

  async extractAll(selector: string): Promise<Array<{ text: string; href?: string }>> {
    return await this.page?.$$eval(selector, elements => 
      elements.map(el => ({
        text: el.textContent?.trim() || '',
        href: (el as HTMLAnchorElement).href || undefined
      }))
    ) || [];
  }

  async saveCookies(path: string): Promise<void> {
    const cookies = await this.context?.cookies();
    // Сохранение в файл
  }

  async loadCookies(path: string): Promise<void> {
    // Загрузка из файла
  }

  async close(): Promise<void> {
    await this.browser?.close();
  }
}
```

- [ ] **1.3.2** Создать `src/utils/delays.ts` (человеческие задержки из Upwork-Job-Scraper)
```typescript
export function humanDelay(min: number, max: number): Promise<void> {
  const delay = Math.floor(Math.random() * (max - min + 1)) + min;
  return new Promise(resolve => setTimeout(resolve, delay));
}

export async function humanClick(page: Page, selector: string): Promise<void> {
  await humanDelay(300, 600);
  await page.click(selector);
  await humanDelay(200, 400);
}

export async function humanScroll(page: Page): Promise<void> {
  const scrollDelay = () => humanDelay(1000, 2000);
  
  await scrollDelay();
  await page.evaluate(() => window.scrollBy(0, 500));
  await scrollDelay();
  await page.evaluate(() => window.scrollBy(0, 500));
  await scrollDelay();
}
```

- [ ] **1.3.3** Создать `src/utils/logger.ts`
```typescript
import fs from 'fs';
import path from 'path';

export class Logger {
  private logFile: string;

  constructor(date: string = new Date().toISOString().split('T')[0]) {
    this.logFile = path.join(process.cwd(), 'logs', `agent-${date}.log`);
    fs.mkdirSync(path.dirname(this.logFile), { recursive: true });
  }

  log(action: string, result: string, details?: any): void {
    const entry = {
      timestamp: new Date().toISOString(),
      action,
      result,
      details
    };
    
    const line = JSON.stringify(entry) + '\n';
    fs.appendFileSync(this.logFile, line);
    
    console.log(`[${entry.timestamp}] ${action}: ${result}`);
  }

  error(action: string, error: Error, details?: any): void {
    this.log(action, `ERROR: ${error.message}`, { stack: error.stack, ...details });
  }
}
```

---

## Неделя 2: Адаптеры платформ и авторизация

### День 8-10: Базовый интерфейс адаптера

**Задачи:**
- [ ] **1.4.1** Создать `src/adapters/base.ts`
```typescript
import { BrowserService } from '../services/browser';
import { Logger } from '../utils/logger';

export interface Credentials {
  username: string;
  password: string;
  twoFactorCode?: string;
}

export interface AuthResult {
  success: boolean;
  requires2FA?: boolean;
  cookies?: any[];
}

export interface RawJob {
  platform: string;
  id?: string;
  url: string;
  title: string;
  description: string;
  budget?: {
    amount: number;
    currency: string;
    type: 'fixed' | 'hourly';
  };
  skills: string[];
  postedAt?: Date;
  client?: {
    name?: string;
    country?: string;
    rating?: number;
    paymentVerified: boolean;
  };
  proposalsCount?: number;
}

export interface PlatformSelectors {
  jobCard: string;
  title: string;
  description: string;
  budget: string;
  skills: string;
  clientInfo: string;
  postedAt: string;
  proposalsCount: string;
}

export interface PlatformDelays {
  pageLoad: number;
  scroll: number;
  click: number;
  betweenRequests: number;
}

export abstract class PlatformAdapter {
  abstract name: string;
  abstract baseUrl: string;
  abstract loginUrl: string;
  
  protected selectors: PlatformSelectors;
  protected delays: PlatformDelays;
  
  constructor(
    protected browser: BrowserService,
    protected logger: Logger
  ) {}

  abstract login(credentials: Credentials): Promise<AuthResult>;
  abstract isAuthenticated(): Promise<boolean>;
  abstract navigateToJobs(filters?: any): Promise<void>;
  abstract extractJobs(): Promise<RawJob[]>;
  
  protected async scrollToLoadMore(maxScrolls = 3): Promise<void> {
    let lastHeight = await this.browser.evaluate('() => document.body.scrollHeight');
    
    for (let i = 0; i < maxScrolls; i++) {
      await this.browser.scrollToEnd();
      await this.sleep(this.delays.scroll);
      
      const newHeight = await this.browser.evaluate('() => document.body.scrollHeight');
      if (newHeight === lastHeight) break;
      lastHeight = newHeight;
    }
  }

  protected sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

---

### День 11-14: Адаптер Upwork (из roperi/UpworkScraper)

**Задачи:**
- [ ] **1.5.1** Создать `src/adapters/upwork.ts`
```typescript
import { PlatformAdapter, Credentials, AuthResult, RawJob } from './base';
import { BrowserService } from '../services/browser';
import { Logger } from '../utils/logger';

export class UpworkAdapter extends PlatformAdapter {
  name = 'upwork';
  baseUrl = 'https://www.upwork.com';
  loginUrl = 'https://www.upwork.com/ab/account-security/login';
  
  protected selectors = {
    jobCard: '.job-tile',
    title: 'h2 a[data-test="job-title"]',
    description: '.job-description .tokenized-string',
    budget: '.job-budget',
    skills: '.job-skills li a',
    clientInfo: '.client-info',
    postedAt: 'time',
    proposalsCount: '.proposals-count'
  };
  
  protected delays = {
    pageLoad: 2000,
    scroll: 1500,
    click: 500,
    betweenRequests: 3000
  };

  constructor(browser: BrowserService, logger: Logger) {
    super(browser, logger);
  }

  async login(credentials: Credentials): Promise<AuthResult> {
    this.logger.log('UPWORK_LOGIN', 'Начало авторизации');
    
    try {
      // Открыть страницу логина
      await this.browser.goto(this.loginUrl);
      await this.sleep(this.delays.pageLoad);
      
      // Ввести логин
      await this.browser.type('#login_username', credentials.username);
      await this.sleep(500);
      
      // Ввести пароль
      await this.browser.type('#login_password', credentials.password);
      await this.sleep(500);
      
      // Кликнуть кнопку входа
      await this.browser.click('button[type="submit"]');
      await this.sleep(this.delays.pageLoad);
      
      // Проверка на 2FA
      const requires2FA = await this.browser.exists('.two-factor-input');
      if (requires2FA) {
        this.logger.log('UPWORK_LOGIN', 'Требуется 2FA');
        return { success: false, requires2FA: true };
      }
      
      // Проверка успешности
      const isLoggedIn = await this.browser.exists('.nav-user-menu');
      
      if (isLoggedIn) {
        this.logger.log('UPWORK_LOGIN', 'Успешная авторизация');
        await this.browser.saveCookies('data/cookies/upwork.json');
      } else {
        this.logger.log('UPWORK_LOGIN', 'Авторизация не удалась');
      }
      
      return {
        success: isLoggedIn,
        requires2FA: false,
        cookies: await this.browser.getCookies()
      };
    } catch (error) {
      this.logger.error('UPWORK_LOGIN', error as Error);
      return { success: false, requires2FA: false };
    }
  }

  async isAuthenticated(): Promise<boolean> {
    try {
      await this.browser.goto(`${this.baseUrl}/settings/notifications`);
      await this.sleep(this.delays.pageLoad);
      return await this.browser.exists('.nav-user-menu');
    } catch {
      return false;
    }
  }

  async navigateToJobs(filters?: any): Promise<void> {
    this.logger.log('UPWORK_NAVIGATE', 'Переход к поиску задач');
    
    let url = `${this.baseUrl}/nx/search/jobs/`;
    const params = new URLSearchParams();
    
    if (filters?.paymentVerified) {
      params.append('payment_verified', '1');
    }
    if (filters?.minBudget) {
      params.append('min_budget', filters.minBudget.toString());
    }
    if (filters?.jobType) {
      params.append('job_type', filters.jobType.join(','));
    }
    
    url += `?${params.toString()}`;
    await this.browser.goto(url);
    await this.sleep(this.delays.pageLoad);
    
    this.logger.log('UPWORK_NAVIGATE', `URL: ${url}`);
  }

  async extractJobs(): Promise<RawJob[]> {
    this.logger.log('UPWORK_EXTRACT', 'Начало извлечения задач');
    
    const jobs: RawJob[] = [];
    
    // Прокрутка для загрузки всех задач
    await this.scrollToLoadMore(3);
    await this.sleep(this.delays.betweenRequests);
    
    const jobCards = await this.browser.extractAll(this.selectors.jobCard);
    
    for (let i = 0; i < jobCards.length; i++) {
      try {
        const card = jobCards[i];
        const job: RawJob = {
          platform: this.name,
          url: card.href || '',
          title: await this.browser.extractText(`${this.selectors.jobCard}:nth-child(${i + 1}) ${this.selectors.title}`),
          description: await this.browser.extractText(`${this.selectors.jobCard}:nth-child(${i + 1}) ${this.selectors.description}`),
          budget: await this.extractBudget(i),
          skills: await this.extractSkills(i),
          client: await this.extractClientInfo(i)
        };
        
        jobs.push(job);
        this.logger.log('UPWORK_EXTRACT', `Извлечена задача #${i + 1}`, { title: job.title });
        
      } catch (error) {
        this.logger.error('UPWORK_EXTRACT', error as Error, { index: i });
      }
    }
    
    this.logger.log('UPWORK_EXTRACT', `Извлечено ${jobs.length} задач`);
    return jobs;
  }

  private async extractBudget(index: number): Promise<any> {
    const budgetText = await this.browser.extractText(
      `${this.selectors.jobCard}:nth-child(${index + 1}) ${this.selectors.budget}`
    );
    
    // Парсинг бюджета
    const fixedMatch = budgetText.match(/\$([\d,]+)(?:\s+(\w+))?/);
    const hourlyMatch = budgetText.match(/\$([\d,]+)-\$([\d,]+)\s*(?:\/\s*hr)?/);
    
    if (hourlyMatch) {
      return {
        type: 'hourly' as const,
        min: parseInt(hourlyMatch[1].replace(/,/g, '')),
        max: parseInt(hourlyMatch[2].replace(/,/g, '')),
        currency: hourlyMatch[3] || 'USD'
      };
    }
    
    if (fixedMatch) {
      return {
        type: 'fixed' as const,
        amount: parseInt(fixedMatch[1].replace(/,/g, '')),
        currency: fixedMatch[2] || 'USD'
      };
    }
    
    return undefined;
  }

  private async extractSkills(index: number): Promise<string[]> {
    const skills = await this.browser.extractAll(
      `${this.selectors.jobCard}:nth-child(${index + 1}) ${this.selectors.skills}`
    );
    return skills.map(s => s.text);
  }

  private async extractClientInfo(index: number): Promise<any> {
    const clientText = await this.browser.extractText(
      `${this.selectors.jobCard}:nth-child(${index + 1}) ${this.selectors.clientInfo}`
    );
    
    return {
      name: clientText,
      paymentVerified: clientText.includes('Verified') || clientText.includes('Payment verified')
    };
  }
}
```

---

### День 15-16: Адаптер FL.ru (для нишевых бирж)

**Задачи:**
- [ ] **1.6.1** Создать `src/adapters/flru.ts`
```typescript
import { PlatformAdapter, Credentials, AuthResult, RawJob } from './base';
import { BrowserService } from '../services/browser';
import { Logger } from '../utils/logger';

export class FLruAdapter extends PlatformAdapter {
  name = 'fl.ru';
  baseUrl = 'https://www.fl.ru';
  loginUrl = 'https://www.fl.ru/login/';
  
  protected selectors = {
    jobCard: '.project-card',
    title: '.project-card__title a',
    description: '.project-card__description',
    budget: '.project-card__budget',
    skills: '.project-card__skills .tag',
    clientInfo: '.project-card__client',
    postedAt: '.project-card__time',
    proposalsCount: '.project-card__proposals'
  };
  
  protected delays = {
    pageLoad: 2500,
    scroll: 2000,
    click: 600,
    betweenRequests: 4000
  };

  constructor(browser: BrowserService, logger: Logger) {
    super(browser, logger);
  }

  async login(credentials: Credentials): Promise<AuthResult> {
    this.logger.log('FLRU_LOGIN', 'Начало авторизации');
    
    await this.browser.goto(this.loginUrl);
    await this.sleep(this.delays.pageLoad);
    
    await this.browser.type('#email', credentials.username);
    await this.sleep(500);
    
    await this.browser.type('#password', credentials.password);
    await this.sleep(500);
    
    await this.browser.click('button.login-btn');
    await this.sleep(this.delays.pageLoad);
    
    const isLoggedIn = await this.browser.exists('.user-menu');
    
    if (isLoggedIn) {
      this.logger.log('FLRU_LOGIN', 'Успешная авторизация');
      await this.browser.saveCookies('data/cookies/flru.json');
    }
    
    return {
      success: isLoggedIn,
      requires2FA: false,
      cookies: await this.browser.getCookies()
    };
  }

  async isAuthenticated(): Promise<boolean> {
    await this.browser.goto(`${this.baseUrl}/user/`);
    return await this.browser.exists('.user-menu');
  }

  async navigateToJobs(filters?: any): Promise<void> {
    await this.browser.goto(`${this.baseUrl}/projects/`);
    await this.sleep(this.delays.pageLoad);
  }

  async extractJobs(): Promise<RawJob[]> {
    const jobs: RawJob[] = [];
    await this.scrollToLoadMore(3);
    
    const jobCards = await this.browser.extractAll(this.selectors.jobCard);
    
    for (let i = 0; i < jobCards.length; i++) {
      const job: RawJob = {
        platform: this.name,
        url: await this.browser.extractText(`${this.selectors.jobCard}:nth-child(${i + 1}) ${this.selectors.title}`),
        title: await this.browser.extractText(`${this.selectors.jobCard}:nth-child(${i + 1}) ${this.selectors.title}`),
        description: await this.browser.extractText(`${this.selectors.jobCard}:nth-child(${i + 1}) ${this.selectors.description}`),
        budget: await this.extractBudget(i),
        skills: await this.extractSkills(i),
        client: await this.extractClientInfo(i)
      };
      jobs.push(job);
    }
    
    return jobs;
  }

  private async extractBudget(index: number): Promise<any> {
    const text = await this.browser.extractText(
      `${this.selectors.jobCard}:nth-child(${index + 1}) ${this.selectors.budget}`
    );
    
    const match = text.match(/([\d,]+)\s*(₽|\$|€)/);
    if (match) {
      return {
        type: 'fixed' as const,
        amount: parseInt(match[1].replace(/,/g, '')),
        currency: match[2] === '₽' ? 'RUB' : match[2]
      };
    }
    return undefined;
  }

  private async extractSkills(index: number): Promise<string[]> {
    const skills = await this.browser.extractAll(
      `${this.selectors.jobCard}:nth-child(${index + 1}) ${this.selectors.skills}`
    );
    return skills.map(s => s.text);
  }

  private async extractClientInfo(index: number): Promise<any> {
    return { paymentVerified: false }; // FL.ru не всегда показывает
  }
}
```

---

## Неделя 3: Хранение данных и базовая фильтрация

### День 17-19: Storage Service

**Задачи:**
- [ ] **1.7.1** Создать `src/services/storage.ts`
```typescript
import fs from 'fs';
import path from 'path';
import { RawJob } from '../adapters/base';

export class StorageService {
  private baseDir: string;

  constructor() {
    this.baseDir = path.join(process.cwd(), 'data');
    fs.mkdirSync(this.baseDir, { recursive: true });
  }

  saveRawJobs(platform: string, date: string, jobs: RawJob[]): void {
    const dir = path.join(this.baseDir, 'jobs', 'raw', date);
    fs.mkdirSync(dir, { recursive: true });
    
    const filePath = path.join(dir, `${platform}-raw.json`);
    fs.writeFileSync(filePath, JSON.stringify(jobs, null, 2));
  }

  loadRawJobs(platform: string, date: string): RawJob[] {
    const filePath = path.join(this.baseDir, 'jobs', 'raw', date, `${platform}-raw.json`);
    if (!fs.existsSync(filePath)) return [];
    
    const content = fs.readFileSync(filePath, 'utf-8');
    return JSON.parse(content);
  }

  saveProcessed(date: string, jobs: any[]): void {
    const dir = path.join(this.baseDir, 'processed');
    fs.mkdirSync(dir, { recursive: true });
    
    const filePath = path.join(dir, `shortlist-${date}.json`);
    fs.writeFileSync(filePath, JSON.stringify(jobs, null, 2));
  }

  saveProposal(jobId: string, proposal: string): void {
    const dir = path.join(process.cwd(), 'proposals');
    fs.mkdirSync(dir, { recursive: true });
    
    const filePath = path.join(dir, `${jobId}-proposal.md`);
    fs.writeFileSync(filePath, proposal);
  }

  savePrototype(jobId: string, files: Map<string, string>): void {
    const dir = path.join(process.cwd(), 'prototypes', jobId);
    fs.mkdirSync(dir, { recursive: true });
    
    for (const [filename, content] of files.entries()) {
      fs.writeFileSync(path.join(dir, filename), content);
    }
  }
}
```

---

### День 20-21: Skills Extractor (из codebasics/job-scrapper)

**Задачи:**
- [ ] **1.8.1** Создать `src/services/skills_extractor.ts`
```typescript
export class SkillsExtractor {
  private readonly skillPatterns = {
    frontend: [
      'React', 'React.js', 'ReactJS', 'Vue', 'Vue.js', 'Angular',
      'Next.js', 'NextJS', 'Nuxt', 'TypeScript', 'JavaScript',
      'HTML5', 'CSS3', 'Tailwind', 'Bootstrap', 'Material-UI'
    ],
    backend: [
      'Node.js', 'NodeJS', 'Express', 'NestJS',
      'Python', 'Django', 'FastAPI', 'Flask',
      'PHP', 'Laravel', 'Java', 'Spring', 'Go', 'Ruby'
    ],
    database: [
      'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'SQLite'
    ],
    devops: [
      'Docker', 'Kubernetes', 'AWS', 'GCP', 'Azure', 'CI/CD'
    ],
    design: [
      'Figma', 'Sketch', 'Adobe XD', 'UI/UX', 'Prototyping'
    ]
  };

  extractSkills(description: string, tags: string[] = []): string[] {
    const text = (description + ' ' + tags.join(' ')).toLowerCase();
    const foundSkills = new Set<string>();

    for (const [category, skills] of Object.entries(this.skillPatterns)) {
      for (const skill of skills) {
        const regex = new RegExp(`\\b${this.escapeRegex(skill.toLowerCase())}\\b`, 'i');
        if (regex.test(text)) {
          foundSkills.add(this.normalizeSkillName(skill));
        }
      }
    }

    return Array.from(foundSkills);
  }

  private normalizeSkillName(skill: string): string {
    const normalizations: Record<string, string> = {
      'React.js': 'React',
      'ReactJS': 'React',
      'Vue.js': 'Vue',
      'NodeJS': 'Node.js'
    };
    return normalizations[skill] || skill;
  }

  private escapeRegex(string: string): string {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }
}
```

- [ ] **1.8.2** Создать простую фильтрацию по ключевым словам
```typescript
export class SimpleFilter {
  constructor(
    private ignoreKeywords: string[],
    private ignoreCategories: string[]
  ) {}

  shouldInclude(job: RawJob): boolean {
    const text = (job.title + ' ' + job.description).toLowerCase();
    
    // Проверка стоп-слов
    for (const keyword of this.ignoreKeywords) {
      if (text.includes(keyword.toLowerCase())) {
        return false;
      }
    }
    
    // Проверка категорий
    // (будет реализовано в Matching-агенте)
    
    return true;
  }
}
```

---

### День 22: Scheduler и запуск

**Задачи:**
- [ ] **1.9.1** Создать `src/agents/scheduler.ts`
```typescript
import { BrowserService } from '../services/browser';
import { StorageService } from '../services/storage';
import { Logger } from '../utils/logger';
import { UpworkAdapter } from '../adapters/upwork';
import { FLruAdapter } from '../adapters/flru';
import { SkillsExtractor } from '../services/skills_extractor';
import { SimpleFilter } from './filter';

export class SchedulerAgent {
  private browser: BrowserService;
  private storage: StorageService;
  private logger: Logger;
  private skillsExtractor: SkillsExtractor;
  private filter: SimpleFilter;

  constructor(config: any) {
    this.browser = new BrowserService();
    this.storage = new StorageService();
    this.logger = new Logger();
    this.skillsExtractor = new SkillsExtractor();
    this.filter = new SimpleFilter(
      config.preferences.ignoreKeywords,
      config.preferences.ignoreCategories
    );
  }

  async run(): Promise<void> {
    const today = new Date().toISOString().split('T')[0];
    this.logger.log('SCHEDULER', `Запуск агента ${today}`);
    
    try {
      await this.browser.launch(false); // headless = false для отладки
      
      // Загрузка куки если есть
      // await this.browser.loadCookies('data/cookies/upwork.json');
      
      // Авторизация
      const upworkAdapter = new UpworkAdapter(this.browser, this.logger);
      const authResult = await upworkAdapter.login({
        username: process.env.UPWORK_USERNAME!,
        password: process.env.UPWORK_PASSWORD!
      });
      
      if (!authResult.success) {
        this.logger.log('SCHEDULER', 'Авторизация не удалась, требуется ручное вмешательство');
        return;
      }
      
      // Навигация и сбор задач
      await upworkAdapter.navigateToJobs({
        paymentVerified: true,
        minBudget: 500
      });
      
      const jobs = await upworkAdapter.extractJobs();
      this.storage.saveRawJobs('upwork', today, jobs);
      
      // Простая фильтрация
      const filteredJobs = jobs.filter(job => this.filter.shouldInclude(job));
      this.storage.saveProcessed(today, filteredJobs);
      
      this.logger.log('SCHEDULER', `Собрано ${jobs.length}, отфильтровано ${filteredJobs.length}`);
      
    } catch (error) {
      this.logger.error('SCHEDULER', error as Error);
    } finally {
      await this.browser.close();
    }
  }
}
```

- [ ] **1.9.2** Создать `src/index.ts` для запуска
```typescript
import { SchedulerAgent } from './agents/scheduler';
import profileConfig from '../config/profile.json';

async function main() {
  const agent = new SchedulerAgent(profileConfig);
  await agent.run();
}

main().catch(console.error);
```

- [ ] **1.9.3** Добавить скрипт в `package.json`
```json
{
  "scripts": {
    "start": "ts-node src/index.ts",
    "dev": "ts-node src/index.ts",
    "build": "tsc"
  }
}
```

---

## Критерии готовности MVP #1

- [ ] Авторизация на Upwork работает
- [ ] Авторизация на FL.ru работает
- [ ] Сбор минимум 20 задач за сессию
- [ ] Сохранение в JSON файлы
- [ ] Простая фильтрация по стоп-словам
- [ ] Логирование всех действий
- [ ] Отчёт в конце сессии

---

# MVP #2 — Умный матчинг и прототипы (3-4 недели)

## Неделя 4-5: Skill Matcher (из job-matching / skill-matching)

**Задачи:**
- [ ] **2.1** Создать `src/services/skill_matcher.ts` (полный код из OPEN_SOURCE_PATTERNS.md)
- [ ] **2.2** Реализовать семантический поиск синонимов
- [ ] **2.3** Добавить расчёт `skill_match_score` ∈ [0, 1]
- [ ] **2.4** Интегрировать в Scheduler

---

## Неделя 6: Clarity Scorer

**Задачи:**
- [ ] **2.5** Создать `src/services/clarity_scorer.ts`
- [ ] **2.6** Реализовать эвристики (стек, референсы, сценарии, критерии)
- [ ] **2.7** Добавить детектор «плохих» ТЗ
- [ ] **2.8** Интегрировать двухэтапную фильтрацию

---

## Неделя 7-8: Solution Draft Agent

**Задачи:**
- [ ] **2.9** Создать генератор плана решения
- [ ] **2.10** Реализовать scaffold для Next.js проектов
- [ ] **2.11** Создать шаблоны для дизайн-задач
- [ ] **2.12** Интегрировать с Dashboard

---

# MVP #3 — Авто-предложения и защита (2-3 недели)

## Неделя 9-10: Proposal Generator (из DZone + client-proposal-generator-tool)

**Задачи:**
- [ ] **3.1** Создать `src/agents/proposal.ts`
- [ ] **3.2** Реализовать шаблонизатор писем
- [ ] **3.3** Добавить персонализацию
- [ ] **3.4** Создать детектор спам-триггеров

---

## Неделя 11: Protection Agent

**Задачи:**
- [ ] **3.5** Реализовать водяные знаки для изображений
- [ ] **3.6** Создать систему mock-слоя для критичных функций
- [ ] **3.7** Интегрировать деплой на Vercel/Netlify
- [ ] **3.8** Добавить юридические дисклеймеры

---

## Неделя 12: Dashboard и отчёты

**Задачи:**
- [ ] **3.9** Создать веб-Dashboard (React + Tailwind)
- [ ] **3.10** Реализовать систему отчётов
- [ ] **3.11** Добавить режим ручной проверки
- [ ] **3.12** Настроить Telegram/email уведомления

---

# Итоговый чеклист

## MVP #1 (Недели 1-3)
- [ ] Структура проекта создана
- [ ] Browser Controller работает
- [ ] Upwork адаптер готов
- [ ] FL.ru адаптер готов
- [ ] Storage Service работает
- [ ] Skills Extractor готов
- [ ] Simple Filter работает
- [ ] Scheduler запускается
- [ ] Логирование работает

## MVP #2 (Недели 4-8)
- [ ] Skill Matcher с семантикой
- [ ] Clarity Scorer с эвристиками
- [ ] Генератор планов решений
- [ ] Scaffold для веб-проектов
- [ ] Интеграция всех компонентов

## MVP #3 (Недели 9-12)
- [ ] Proposal Generator
- [ ] Protection механизмы
- [ ] Деплой на Vercel
- [ ] Веб-Dashboard
- [ ] Система отчётов

---

## Метрики успеха

| Метрика | MVP #1 | MVP #2 | MVP #3 |
|---------|--------|--------|--------|
| Точность матчинга | >60% | >80% | >85% |
| Скорость сбора 20 задач | <2 мин | <2 мин | <2 мин |
| Генерация прототипа | N/A | <5 мин | <3 мин |
| Конверсия в диалог | N/A | N/A | >30% |

---

## Бэклог — Post-MVP

### 🔖 Airweave (context retrieval layer)
- **Репозиторий:** [airweave-ai/airweave](https://github.com/airweave-ai/airweave) (⭐ 6.1k, MIT)
- **Что это:** Open-source unified retrieval layer для AI-агентов. Подключается к 50+ источникам (GitHub, Notion, Google Docs, Slack и др.), синхронизирует, индексирует данные и выставляет через единый поисковый API с семантическим поиском.
- **Техстек:** FastAPI + PostgreSQL + Vespa (векторы) + Temporal + Redis + Docker
- **SDK:** Python (`airweave-sdk`), TypeScript (`@airweave/sdk`), поддержка MCP
- **Оценка релевантности:** 4/10 для текущего MVP, **7/10 для пост-MVP фазы**
- **Почему не сейчас:**
  - Overengineering для MVP (~6 Docker-контейнеров)
  - Нет коннекторов к Upwork/FL.ru — скрейпинг всё равно свой
  - Решает другую задачу: retrieval по существующим данным, а не скрейпинг
- **Когда пригодится:**
  - [ ] Этап "Self-learning через базу знаний" — индексация GitHub-портфолио для персонализации proposals
  - [ ] Этап "Богатый контекст" — подтягивание документации фреймворков для прототипов
  - [ ] Этап "Масштабирование" — семантический поиск по 1000+ накопленных задач
- **Альтернативы для MVP:** ChromaDB/Qdrant (лёгкое векторное хранилище), LlamaIndex (RAG без инфраструктуры)

---

*Документ готов к реализации. Следующий шаг — начать с Недели 1, День 1.*
