# Заимствованные паттерны из open-source проектов

> Версия: 1.0  
> Дата: 2026-03-23  
> Источник: Анализ проектов UpworkScraper, Upwork-Job-Scraper, job-scrapper и др.

---

## Обзор заимствований

| Источник | Что заимствуем | Куда применяем | Приоритет |
|----------|----------------|----------------|-----------|
| UpworkScraper | Авторизация + навигация | Scraper-агент | 🔴 Высокий |
| Upwork-Job-Scraper | Структура данных вакансий | Data Model | 🔴 Высокий |
| Upwork-Job-Scraper | Конфиг поиска с фильтрами | config/profile.json | 🔴 Высокий |
| job-scrapper | Извлечение навыков (regex) | Matching-агент | 🔴 Высокий |
| job-scrapper | Архитектура scraping→parsing→storage | Общая архитектура | 🔴 Высокий |
| job-matching | Расчёт skill_match_score | Matching-агент | 🟡 Средний |
| skill-matching | Профиль skill→weight | config/profile.json | 🔴 Высокий |
| Upwork-Auto-Jobs-Applier | Continuous scanning | Scheduler-агент | 🟡 Средний |
| Upwork-Auto-Jobs-Applier | Smart classification pipeline | Matching-агент | 🟡 Средний |
| Proposal Generator | Шаблонный подход к письмам | Proposal-агент | 🔴 Высокий |

---

## 1. Структуры данных

### 1.1 Job Model (из Upwork-Job-Scraper)

```typescript
interface Job {
  // Основная информация
  id: string;                    // Уникальный ID задачи
  platform: string;              // 'upwork' | 'fiverr' | 'freelancer' | 'fl.ru' | 'kwork'
  url: string;                   // Ссылка на задачу
  
  // Контент
  title: string;                 // Заголовок задачи
  description: string;           // Полное описание
  descriptionHtml?: string;      // HTML версия (если есть)
  
  // Финансы
  budget?: {
    amount: number;
    currency: string;            // 'USD' | 'EUR' | 'RUB' | 'GBP'
    type: 'fixed' | 'hourly';
  };
  hourlyRate?: {
    min: number;
    max: number;
    currency: string;
  };
  
  // Метаданные
  postedAt: Date;                // Дата публикации
  category: string;              // Категория (Web Dev, Design, etc.)
  subcategory?: string;          // Подкатегория
  
  // Навыки и теги
  skills: string[];              // Извлечённые навыки
  
  // Клиент
  client?: {
    id: string;
    name?: string;
    country?: string;
    rating?: number;
    reviewsCount?: number;
    jobsPosted?: number;
    hireRate?: number;           // Процент найма
    paymentVerified: boolean;    // Платёж верифицирован
    totalSpent?: number;
  };
  
  // Статистика
  proposalsCount?: number;       // Количество откликов
  interviewsCount?: number;      // Количество интервью
  viewsCount?: number;           // Количество просмотров
  
  // Дополнительно
  duration?: string;             // 'Less than 1 week', '1-3 months', etc.
  experienceLevel?: string;      // 'Entry', 'Intermediate', 'Expert'
  projectType?: string;          // 'One-time', 'Ongoing'
  remote?: boolean;              // Удалённая работа
  
  // Локальные метрики
  skillMatchScore?: number;      // 0-1, рассчитывается Matching-агентом
  clarityScore?: number;         // 0-1, рассчитывается Filter-агентом
  status?: JobStatus;
}

type JobStatus = 
  | 'new'
  | 'filtered_out_skills'
  | 'filtered_out_clarity'
  | 'shortlisted'
  | 'prototype_ready'
  | 'proposal_sent'
  | 'in_negotiation'
  | 'closed'
  | 'ignored';
```

### 1.2 Profile Config (из skill-matching + Upwork-Auto-Jobs-Applier)

```json
{
  "user": {
    "name": "Иван Петров",
    "nickname": "ivan_dev",
    "timezone": "Europe/Moscow",
    "portfolio": {
      "github": "https://github.com/username",
      "website": "https://mysite.com",
      "linkedin": "https://linkedin.com/in/username",
      "dribbble": "https://dribbble.com/username"
    }
  },
  
  "skills": {
    "React": 0.9,
    "Next.js": 0.8,
    "TypeScript": 0.85,
    "Node.js": 0.7,
    "Python": 0.6,
    "PostgreSQL": 0.75,
    "MongoDB": 0.65,
    "Docker": 0.7,
    "AWS": 0.5,
    "UI/UX": 0.6,
    "Figma": 0.55
  },
  
  "skillSynonyms": {
    "React": ["React.js", "ReactJS", "React 18"],
    "Next.js": ["NextJS", "Next 14"],
    "TypeScript": ["TS", "TypeScript 5"],
    "Node.js": ["Node", "NodeJS", "Express", "NestJS"],
    "Python": ["Python 3", "Django", "FastAPI"],
    "PostgreSQL": ["Postgres", "PSQL"],
    "MongoDB": ["Mongo", "Mongoose"],
    "Docker": ["Docker Compose", "Kubernetes"],
    "AWS": ["Amazon Web Services", "EC2", "S3", "Lambda"],
    "UI/UX": ["User Interface", "User Experience", "Material Design"],
    "Figma": ["FigJam", "Design Systems"]
  },
  
  "preferences": {
    "categories": [
      "Web Development",
      "Full Stack Development",
      "Backend Development",
      "Frontend Development",
      "API Development",
      "Database Design"
    ],
    "ignoreCategories": [
      "Writing & Translation",
      "Social Media Marketing",
      "SEO",
      "Data Entry"
    ],
    "ignoreKeywords": [
      "ботнет",
      "кардинг",
      "спам",
      "накрутка",
      "взлом",
      "crack",
      "spam",
      "botnet"
    ]
  },
  
  "matching": {
    "skillMatchThreshold": 0.7,
    "clarityThreshold": 0.6,
    "maxTasksPerDay": 5,
    "minBudget": 500,
    "requirePaymentVerified": true,
    "minClientRating": 4.0,
    "maxProposals": 20
  },
  
  "platforms": [
    {
      "name": "upwork",
      "displayName": "Upwork",
      "url": "https://www.upwork.com/nx/search/jobs/",
      "loginUrl": "https://www.upwork.com/ab/account-security/login",
      "enabled": true,
      "priority": 1,
      "config": {
        "filters": {
          "jobType": ["hourly", "fixed"],
          "experienceLevel": ["intermediate", "expert"],
          "paymentVerified": true,
          "minBudget": 500,
          "maxProposals": 20
        },
        "selectors": {
          "jobCard": ".job-tile",
          "title": "h2 a",
          "description": ".job-description",
          "budget": ".job-budget",
          "skills": ".job-skills li",
          "clientInfo": ".client-info"
        }
      }
    },
    {
      "name": "freelancer",
      "displayName": "Freelancer.com",
      "url": "https://www.freelancer.com/jobs/",
      "enabled": true,
      "priority": 2
    },
    {
      "name": "fl.ru",
      "displayName": "FL.ru",
      "url": "https://www.fl.ru/projects/",
      "enabled": true,
      "priority": 3
    },
    {
      "name": "kwork",
      "displayName": "Kwork",
      "url": "https://kwork.ru/projects",
      "enabled": true,
      "priority": 4
    }
  ],
  
  "schedule": {
    "enabled": true,
    "timezone": "Europe/Moscow",
    "runTime": "09:00",
    "daysOfWeek": [1, 2, 3, 4, 5]
  },
  
  "notifications": {
    "telegram": {
      "enabled": false,
      "botToken": "",
      "chatId": ""
    },
    "email": {
      "enabled": false,
      "smtpHost": "",
      "smtpPort": 587,
      "username": "",
      "password": ""
    }
  },
  
  "protection": {
    "watermark": {
      "enabled": true,
      "text": "© {nickname} - Demo Only",
      "position": "center",
      "opacity": 0.3
    },
    "demoHosting": {
      "provider": "vercel",
      "domain": "demo.myportfolio.com"
    },
    "codeSnippets": {
      "maxLines": 50,
      "hideCriticalParts": true
    }
  }
}
```

---

## 2. Архитектурные паттерны

### 2.1 Scraper Pipeline (из job-scrapper)

```
┌─────────────────────────────────────────────────────────────┐
│                     Scheduler Agent                          │
│                  (запускает по расписанию)                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Browser Controller                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Authorizer │→ │   Navigator │→ │    Content Reader   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Platform Adapters                         │
│  ┌──────────┐ ┌────────────┐ ┌─────────┐ ┌──────────────┐   │
│  │  Upwork  │ │ Freelancer │ │ FL.ru   │ │    Kwork     │   │
│  │ Adapter  │ │  Adapter   │ │ Adapter │ │   Adapter    │   │
│  └──────────┘ └────────────┘ └─────────┘ └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Raw Job Storage                            │
│              tasks/raw/{platform}-{date}.json                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Skills Extractor                           │
│         (regex + keyword matching + NLP)                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Matching Agent                             │
│  ┌────────────────────┐  ┌────────────────────────────┐     │
│  │  Skill Matching    │→ │  Clarity Scoring           │     │
│  │  (score 0-1)       │  │  (score 0-1)               │     │
│  └────────────────────┘  └────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Filter & Shortlist                          │
│         (применяет пороги, лимиты, приоритеты)               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Solution Draft Agent                            │
│  ┌────────────────────┐  ┌────────────────────────────┐     │
│  │  Plan Generator    │→ │  Prototype Scaffold        │     │
│  └────────────────────┘  └────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Proposal Agent                              │
│  ┌────────────────────┐  ┌────────────────────────────┐     │
│  │  Letter Template   │→ │  Protection Disclaimer     │     │
│  └────────────────────┘  └────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Dashboard / Report                        │
│              (отчёт пользователю)                            │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Skills Extraction Module (из codebasics/job-scrapper)

```typescript
class SkillsExtractor {
  // Предопределённые списки технологий
  private readonly skillPatterns = {
    frontend: [
      'React', 'React.js', 'ReactJS',
      'Vue', 'Vue.js', 'VueJS',
      'Angular',
      'Next.js', 'NextJS', 'Nuxt',
      'TypeScript', 'JavaScript', 'ES6',
      'HTML5', 'CSS3', 'SASS', 'LESS',
      'Tailwind', 'Bootstrap', 'Material-UI'
    ],
    backend: [
      'Node.js', 'NodeJS', 'Express', 'NestJS',
      'Python', 'Django', 'FastAPI', 'Flask',
      'PHP', 'Laravel', 'Symfony',
      'Java', 'Spring', 'Spring Boot',
      'Go', 'Golang',
      'Ruby', 'Rails'
    ],
    database: [
      'PostgreSQL', 'MySQL', 'MongoDB', 'Redis',
      'SQLite', 'MariaDB', 'Elasticsearch'
    ],
    devops: [
      'Docker', 'Kubernetes', 'AWS', 'GCP', 'Azure',
      'CI/CD', 'GitHub Actions', 'GitLab CI', 'Jenkins'
    ],
    design: [
      'Figma', 'Sketch', 'Adobe XD', 'Photoshop',
      'UI/UX', 'Prototyping', 'Wireframing'
    ]
  };

  extractSkills(description: string, tags: string[] = []): string[] {
    const text = (description + ' ' + tags.join(' ')).toLowerCase();
    const foundSkills = new Set<string>();

    // Поиск по паттернам
    for (const [category, skills] of Object.entries(this.skillPatterns)) {
      for (const skill of skills) {
        const regex = new RegExp(`\\b${this.escapeRegex(skill.toLowerCase())}\\b`, 'i');
        if (regex.test(text)) {
          foundSkills.add(this.normalizeSkillName(skill));
        }
      }
    }

    // Дополнительно: извлечение из CSS-классов, data-атрибутов
    // (если есть доступ к HTML)

    return Array.from(foundSkills);
  }

  private normalizeSkillName(skill: string): string {
    // Приведение к каноническому виду
    const normalizations: Record<string, string> = {
      'React.js': 'React',
      'ReactJS': 'React',
      'Vue.js': 'Vue',
      'VueJS': 'Vue',
      'Next.js': 'Next.js',
      'NodeJS': 'Node.js',
      'TypeScript': 'TypeScript',
      'PostgreSQL': 'PostgreSQL',
      'MongoDB': 'MongoDB'
    };
    return normalizations[skill] || skill;
  }

  private escapeRegex(string: string): string {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }
}
```

### 2.3 Skill Matching Algorithm (из job-matching / skill-matching)

```typescript
class SkillMatcher {
  constructor(
    private userSkills: Map<string, number>, // skill → weight (0-1)
    private skillSynonyms: Record<string, string[]>
  ) {}

  calculateMatchScore(jobSkills: string[]): number {
    if (jobSkills.length === 0) return 0;

    let totalScore = 0;
    let matchedCount = 0;

    for (const jobSkill of jobSkills) {
      const match = this.findBestMatch(jobSkill);
      if (match) {
        totalScore += match.weight;
        matchedCount++;
      }
    }

    // Нормализация: средневзвешенное покрытие
    const coverageRatio = matchedCount / jobSkills.length;
    const avgWeight = totalScore / (matchedCount || 1);
    
    // Формула: покрытие * средний вес * коэффициент полноты
    return coverageRatio * avgWeight * this.completenessFactor(jobSkills.length);
  }

  private findBestMatch(jobSkill: string): { skill: string; weight: number } | null {
    const normalizedJobSkill = this.normalize(jobSkill);
    
    // Прямое совпадение
    if (this.userSkills.has(normalizedJobSkill)) {
      return {
        skill: normalizedJobSkill,
        weight: this.userSkills.get(normalizedJobSkill)!
      };
    }

    // Поиск по синонимам
    for (const [canonicalSkill, synonyms] of Object.entries(this.skillSynonyms)) {
      if (synonyms.some(s => this.normalize(s) === normalizedJobSkill)) {
        if (this.userSkills.has(canonicalSkill)) {
          return {
            skill: canonicalSkill,
            weight: this.userSkills.get(canonicalSkill)! * 0.9 // Коэффициент за синоним
          };
        }
      }
    }

    // Семантическая близость (можно расширить)
    const semanticMatch = this.findSemanticMatch(jobSkill);
    if (semanticMatch) {
      return {
        skill: semanticMatch.skill,
        weight: semanticMatch.weight * 0.7 // Коэффициент за семантику
      };
    }

    return null;
  }

  private findSemanticMatch(jobSkill: string): { skill: string; weight: number } | null {
    // Упрощённая эвристика: частичное совпадение
    const jobSkillLower = jobSkill.toLowerCase();
    
    for (const [userSkill, weight] of this.userSkills.entries()) {
      const userSkillLower = userSkill.toLowerCase();
      
      // Один содержит другой
      if (userSkillLower.includes(jobSkillLower) || jobSkillLower.includes(userSkillLower)) {
        return { skill: userSkill, weight: weight * 0.8 };
      }
      
      // Расстояние Левенштейна для близких названий
      if (this.levenshteinDistance(userSkillLower, jobSkillLower) <= 2) {
        return { skill: userSkill, weight: weight * 0.75 };
      }
    }

    return null;
  }

  private completenessFactor(skillCount: number): number {
    // Штраф за слишком мало навыков в задаче
    if (skillCount < 3) return 0.8;
    if (skillCount < 5) return 0.9;
    return 1.0;
  }

  private normalize(skill: string): string {
    return skill.trim().toLowerCase();
  }

  private levenshteinDistance(a: string, b: string): number {
    const matrix: number[][] = [];
    
    for (let i = 0; i <= b.length; i++) matrix[i] = [i];
    for (let j = 0; j <= a.length; j++) matrix[0][j] = j;
    
    for (let i = 1; i <= b.length; i++) {
      for (let j = 1; j <= a.length; j++) {
        if (b.charAt(i - 1) === a.charAt(j - 1)) {
          matrix[i][j] = matrix[i - 1][j - 1];
        } else {
          matrix[i][j] = Math.min(
            matrix[i - 1][j - 1] + 1,
            matrix[i][j - 1] + 1,
            matrix[i - 1][j] + 1
          );
        }
      }
    }
    
    return matrix[b.length][a.length];
  }
}
```

### 2.4 Clarity Scoring (эвристики из spec)

```typescript
class ClarityScorer {
  score(job: Job): number {
    let score = 0;
    const description = job.description || '';
    const wordCount = description.split(/\s+/).length;

    // 1. Наличие стека технологий (+0.2)
    if (job.skills && job.skills.length > 0) {
      score += 0.2;
    }

    // 2. Наличие референсов/примеров (+0.2)
    if (this.hasReferences(description)) {
      score += 0.2;
    }

    // 3. Описание пользовательских сценариев (+0.2)
    if (this.hasUserScenarios(description)) {
      score += 0.2;
    }

    // 4. Acceptance criteria (+0.2)
    if (this.hasAcceptanceCriteria(description)) {
      score += 0.2;
    }

    // 5. Детальное описание (+0.2)
    if (wordCount >= 150) {
      score += 0.2;
    } else if (wordCount >= 80) {
      score += 0.1;
    }

    // Штрафы
    // 1. Стоп-фразы неопределённости
    if (this.hasVaguePhrases(description)) {
      score -= 0.15;
    }

    // 2. Слишком короткое
    if (wordCount < 50) {
      score -= 0.2;
    }

    // Нормализация к [0, 1]
    return Math.max(0, Math.min(1, score));
  }

  private hasReferences(text: string): boolean {
    const patterns = [
      /пример[аы]?[:\s]/i,
      /референс[аы]?[:\s]/i,
      /похож[ие][ий]/i,
      /как\s+(в|на)/i,
      /https?:\/\//i,
      /figma\.com/i,
      /dribbble\.com/i,
      /behance\.net/i
    ];
    return patterns.some(p => p.test(text));
  }

  private hasUserScenarios(text: string): boolean {
    const patterns = [
      /пользователь\s+(должен|может|будет)/i,
      /user\s+(story|flow|journey)/i,
      /когда\s+.*\s+то/i,
      /сценарий/i,
      /workflow/i
    ];
    return patterns.some(p => p.test(text));
  }

  private hasAcceptanceCriteria(text: string): boolean {
    const patterns = [
      /критерий/i,
      /acceptance\s+criteria/i,
      /definition\s+of\s+done/i,
      /должен\s+(быть|делать|работать)/i,
      /требование/i,
      /must\s+have/i
    ];
    return patterns.some(p => p.test(text));
  }

  private hasVaguePhrases(text: string): boolean {
    const patterns = [
      /как-нибудь/i,
      /красиво/i,
      /подумаем\s+по\s+ходу/i,
      /сделать\s+хорошо/i,
      /whatever/i,
      /make\s+it\s+pretty/i,
      /figure\s+it\s+out/i
    ];
    return patterns.some(p => p.test(text));
  }
}
```

---

## 3. Шаблоны предложений (из Proposal Generator)

### 3.1 Структура шаблона письма

```markdown
# Proposal Template v1.0

## Subject
{{#if job.budget}}
Разработка {{job.category}} для {{job.client.name || 'вашего проекта'}} — бюджет {{job.budget.amount}} {{job.budget.currency}}
{{else}}
Разработка {{job.category}} для {{job.client.name || 'вашего проекта'}}
{{/if}}

## Body

Здравствуйте{{#if job.client.name}}, {{job.client.name}}{{else}}{{/if}}!

### Понимание задачи
{{proposal.taskSummary}}

Я внимательно изучил ваше описание и понимаю, что вам нужно:
{{#each proposal.requirements}}
- {{this}}
{{/each}}

### Почему я подхожу
{{#each proposal.matchedSkills}}
- **{{this.skill}}** (уровень {{this.level}}) — {{this.relevance}}
{{/each}}

{{#if proposal.similarProjects}}
Похожие проекты в портфолио:
{{#each proposal.similarProjects}}
- [{{this.title}}]({{this.url}})
{{/each}}
{{/if}}

### План решения
{{proposal.solutionPlan}}

### Демонстрация
{{#if proposal.demoUrl}}
Я уже подготовил предварительный прототип, чтобы вы могли оценить подход:
👉 {{proposal.demoUrl}}

{{/if}}
{{#if proposal.codeSnippet}}
Ключевой фрагмент решения:
```{{proposal.codeSnippet.language}}
{{proposal.codeSnippet.code}}
```

{{/if}}

### Важное примечание
> Данное демо предоставлено исключительно в ознакомительных целях. 
> Права на решение и исходный код передаются только после оплаты и заключения договора.

### Следующие шаги
Готов обсудить детали и ответить на вопросы:
- 📅 Предложу удобное время для созвона
- 📝 Предоставлю детальную оценку сроков и стоимости
- 💬 Отвечу на технические вопросы

{{#if user.portfolio.website}}
Портфолио: {{user.portfolio.website}}
{{/if}}
{{#if user.portfolio.github}}
GitHub: {{user.portfolio.github}}
{{/if}}

С уважением,
{{user.name}}
{{user.nickname}}
```

### 3.2 Генератор предложений

```typescript
interface ProposalData {
  taskSummary: string;
  requirements: string[];
  matchedSkills: Array<{ skill: string; level: number; relevance: string }>;
  similarProjects?: Array<{ title: string; url: string }>;
  solutionPlan: string;
  demoUrl?: string;
  codeSnippet?: { language: string; code: string };
}

class ProposalGenerator {
  constructor(
    private userProfile: UserProfile,
    private template: string
  ) {}

  async generate(job: Job, proposalData: ProposalData): Promise<string> {
    // 1. Заполняем шаблон данными
    let letter = this.template;
    
    // Замена переменных {{variable}}
    letter = this.interpolate(letter, {
      job,
      user: this.userProfile,
      proposal: proposalData
    });
    
    // 2. Добавляем персонализацию
    letter = await this.personalize(letter, job);
    
    // 3. Проверяем на спам-триггеры
    letter = this.removeSpamTriggers(letter);
    
    return letter;
  }

  private interpolate(template: string, data: Record<string, any>): string {
    return template.replace(/\{\{([^}]+)\}\}/g, (match, path) => {
      const value = this.getNestedValue(data, path.trim());
      return value !== undefined ? String(value) : '';
    });
  }

  private async personalize(letter: string, job: Job): Promise<string> {
    // Здесь можно использовать LLM для улучшения тона
    // или добавления конкретных деталей из описания задачи
    return letter;
  }

  private removeSpamTriggers(letter: string): string {
    // Удаление шаблонных фраз, которые выглядят как спам
    const spamPhrases = [
      'Dear Sir/Madam',
      'I am writing to express',
      'Please consider me'
    ];
    
    let result = letter;
    for (const phrase of spamPhrases) {
      result = result.replace(new RegExp(phrase, 'gi'), '');
    }
    
    return result;
  }

  private getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((acc, key) => acc?.[key], obj);
  }
}
```

---

## 4. Адаптеры для платформ

### 4.1 Базовый интерфейс адаптера

```typescript
interface PlatformAdapter {
  name: string;
  baseUrl: string;
  loginUrl: string;
  
  // Авторизация
  login(credentials: Credentials): Promise<AuthResult>;
  isAuthenticated(): Promise<boolean>;
  
  // Навигация
  navigateToJobs(filters?: JobFilters): Promise<void>;
  scrollToLoadMore(): Promise<void>;
  
  // Парсинг
  extractJobs(): Promise<RawJob[]>;
  extractJobDetails(url: string): Promise<JobDetails>;
  
  // Утилиты
  getSelectors(): PlatformSelectors;
  getDelays(): PlatformDelays;
}

interface PlatformSelectors {
  jobCard: string;
  title: string;
  description: string;
  budget: string;
  skills: string;
  clientInfo: string;
  postedAt: string;
  proposalsCount: string;
}

interface PlatformDelays {
  pageLoad: number;      // ms
  scroll: number;        // ms
  click: number;         // ms
  betweenRequests: number; // ms
}
```

### 4.2 Адаптер для Upwork

```typescript
class UpworkAdapter implements PlatformAdapter {
  name = 'upwork';
  baseUrl = 'https://www.upwork.com';
  loginUrl = 'https://www.upwork.com/ab/account-security/login';
  
  private selectors: PlatformSelectors = {
    jobCard: '.job-tile',
    title: 'h2 a[data-test="job-title"]',
    description: '.job-description .tokenized-string',
    budget: '.job-budget',
    skills: '.job-skills li a',
    clientInfo: '.client-info',
    postedAt: 'time',
    proposalsCount: '.proposals-count'
  };
  
  private delays: PlatformDelays = {
    pageLoad: 2000,
    scroll: 1500,
    click: 500,
    betweenRequests: 3000
  };

  async login(credentials: Credentials): Promise<AuthResult> {
    // 1. Открыть страницу логина
    await browser.goto(this.loginUrl);
    await sleep(this.delays.pageLoad);
    
    // 2. Ввести логин
    await browser.type('#login_username', credentials.username);
    await sleep(500);
    
    // 3. Ввести пароль
    await browser.type('#login_password', credentials.password);
    await sleep(500);
    
    // 4. Кликнуть кнопку входа
    await browser.click('button[type="submit"]');
    await sleep(this.delays.pageLoad);
    
    // 5. Проверить успешность
    const isLoggedIn = await browser.exists('.nav-user-menu');
    
    return {
      success: isLoggedIn,
      requires2FA: await browser.exists('.two-factor-input'),
      cookies: await browser.getCookies()
    };
  }

  async navigateToJobs(filters?: JobFilters): Promise<void> {
    let url = `${this.baseUrl}/nx/search/jobs/`;
    const params = new URLSearchParams();
    
    if (filters?.category) {
      params.append('category', filters.category);
    }
    if (filters?.minBudget) {
      params.append('min_budget', filters.minBudget.toString());
    }
    if (filters?.paymentVerified) {
      params.append('payment_verified', '1');
    }
    
    url += `?${params.toString()}`;
    await browser.goto(url);
    await sleep(this.delays.pageLoad);
  }

  async extractJobs(): Promise<RawJob[]> {
    const jobs: RawJob[] = [];
    
    // Прокрутка для загрузки
    await this.scrollToLoadMore();
    
    const jobCards = await browser.querySelectorAll(this.selectors.jobCard);
    
    for (const card of jobCards) {
      try {
        const job = {
          platform: this.name,
          title: await card.$eval(this.selectors.title, el => el.textContent),
          url: await card.$eval(this.selectors.title, el => el.href),
          description: await card.$eval(this.selectors.description, el => el.textContent),
          budget: await this.extractBudget(card),
          skills: await this.extractSkills(card),
          postedAt: await this.extractPostedAt(card),
          client: await this.extractClientInfo(card)
        };
        
        jobs.push(job);
      } catch (e) {
        console.error('Error extracting job:', e);
      }
    }
    
    return jobs;
  }

  private async scrollToLoadMore(): Promise<void> {
    let lastHeight = await browser.evaluate('() => document.body.scrollHeight');
    
    for (let i = 0; i < 3; i++) { // Максимум 3 скролла
      await browser.evaluate('window.scrollTo(0, document.body.scrollHeight)');
      await sleep(this.delays.scroll);
      
      const newHeight = await browser.evaluate('() => document.body.scrollHeight');
      if (newHeight === lastHeight) break;
      lastHeight = newHeight;
    }
  }
}
```

### 4.3 Адаптер для FL.ru

```typescript
class FLruAdapter implements PlatformAdapter {
  name = 'fl.ru';
  baseUrl = 'https://www.fl.ru';
  loginUrl = 'https://www.fl.ru/login/';
  
  private selectors: PlatformSelectors = {
    jobCard: '.project-card',
    title: '.project-card__title a',
    description: '.project-card__description',
    budget: '.project-card__budget',
    skills: '.project-card__skills .tag',
    clientInfo: '.project-card__client',
    postedAt: '.project-card__time',
    proposalsCount: '.project-card__proposals'
  };
  
  private delays: PlatformDelays = {
    pageLoad: 2500,
    scroll: 2000,
    click: 600,
    betweenRequests: 4000
  };

  async login(credentials: Credentials): Promise<AuthResult> {
    await browser.goto(this.loginUrl);
    await sleep(this.delays.pageLoad);
    
    await browser.type('#email', credentials.username);
    await sleep(500);
    
    await browser.type('#password', credentials.password);
    await sleep(500);
    
    await browser.click('button.login-btn');
    await sleep(this.delays.pageLoad);
    
    const isLoggedIn = await browser.exists('.user-menu');
    
    return {
      success: isLoggedIn,
      requires2FA: false, // FL.ru не имеет 2FA
      cookies: await browser.getCookies()
    };
  }

  async navigateToJobs(filters?: JobFilters): Promise<void> {
    const url = `${this.baseUrl}/projects/`;
    await browser.goto(url);
    await sleep(this.delays.pageLoad);
  }

  async extractJobs(): Promise<RawJob[]> {
    // Аналогично Upwork, но с другими селекторами
    const jobs: RawJob[] = [];
    const jobCards = await browser.querySelectorAll(this.selectors.jobCard);
    
    for (const card of jobCards) {
      const job = {
        platform: this.name,
        title: await card.$eval(this.selectors.title, el => el.textContent?.trim()),
        url: await card.$eval(this.selectors.title, el => el.href),
        description: await card.$eval(this.selectors.description, el => el.textContent?.trim()),
        budget: await this.extractBudget(card),
        skills: await this.extractSkills(card),
        postedAt: await this.extractPostedAt(card),
        client: await this.extractClientInfo(card)
      };
      
      jobs.push(job);
    }
    
    return jobs;
  }
}
```

---

## 5. Хранение данных

### 5.1 Структура SQLite (из UpworkScraper)

```sql
-- Таблица задач
CREATE TABLE jobs (
    id TEXT PRIMARY KEY,
    platform TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    budget_amount REAL,
    budget_currency TEXT,
    budget_type TEXT,
    hourly_min REAL,
    hourly_max REAL,
    category TEXT,
    subcategory TEXT,
    posted_at DATETIME,
    duration TEXT,
    experience_level TEXT,
    project_type TEXT,
    remote BOOLEAN,
    
    -- Клиент
    client_id TEXT,
    client_name TEXT,
    client_country TEXT,
    client_rating REAL,
    client_reviews_count INTEGER,
    client_jobs_posted INTEGER,
    client_hire_rate REAL,
    client_payment_verified BOOLEAN,
    client_total_spent REAL,
    
    -- Статистика
    proposals_count INTEGER,
    interviews_count INTEGER,
    views_count INTEGER,
    
    -- Метрики
    skill_match_score REAL,
    clarity_score REAL,
    
    -- Статус
    status TEXT DEFAULT 'new',
    
    -- Метаданные
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    scraped_at DATETIME
);

-- Таблица навыков
CREATE TABLE skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    category TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Связь задач и навыков
CREATE TABLE job_skills (
    job_id TEXT NOT NULL,
    skill_id INTEGER NOT NULL,
    PRIMARY KEY (job_id, skill_id),
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

-- Таблица откликов
CREATE TABLE proposals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL,
    status TEXT DEFAULT 'draft',
    letter_text TEXT,
    demo_url TEXT,
    sent_at DATETIME,
    response_at DATETIME,
    response_status TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- Таблица пользовательских действий (для обучения)
CREATE TABLE user_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL,
    action_type TEXT NOT NULL, -- 'interested', 'ignored', 'applied'
    action_data TEXT, -- JSON с дополнительными данными
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- Индексы для производительности
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_posted_at ON jobs(posted_at);
CREATE INDEX idx_jobs_skill_match ON jobs(skill_match_score);
CREATE INDEX idx_jobs_platform ON jobs(platform);
CREATE INDEX idx_proposals_status ON proposals(status);
```

### 5.2 JSON-хранилище (для MVP)

```
project-root/
├── data/
│   ├── jobs/
│   │   ├── 2026-03-23/
│   │   │   ├── upwork-raw.json
│   │   │   ├── freelancer-raw.json
│   │   │   └── fl.ru-raw.json
│   │   └── 2026-03-24/
│   └── processed/
│       └── shortlist-2026-03-23.json
├── prototypes/
│   └── {job-id}/
│       ├── README.md
│       ├── plan.md
│       └── demo/
└── proposals/
    └── {job-id}-proposal.md
```

---

## 6. Конфигурация поиска (из calebmwelsh/Upwork-Job-Scraper)

```json
{
  "search": {
    "upwork": {
      "query": "",
      "filters": {
        "jobType": ["hourly", "fixed"],
        "experienceLevel": ["intermediate", "expert"],
        "budget": {
          "min": 500,
          "max": null
        },
        "hourlyRate": {
          "min": 25,
          "max": null
        },
        "paymentVerified": true,
        "clientCountry": [],
        "proposals": {
          "max": 20
        },
        "includeWords": [],
        "excludeWords": ["spam", "bot", "scraping"]
      },
      "categories": [
        "531770282580668428", // Web Development
        "531770282584862733", // Full Stack Development
        "531770282584862734"  // Backend Development
      ],
      "sortBy": "date",
      "limit": 50
    },
    "freelancer": {
      "filters": {
        "projectType": ["hourly", "fixed"],
        "budget": {
          "min": 500
        },
        "verifiedPayment": true,
        "skills": []
      },
      "limit": 50
    }
  }
}
```

---

## 7. Checklist реализации

### MVP #1 — Базовый функционал

- [ ] **7.1** Создать структуру проекта с папками
- [ ] **7.2** Реализовать базовый Browser Controller
- [ ] **7.3** Создать адаптер для Upwork
  - [ ] Авторизация
  - [ ] Навигация к задачам
  - [ ] Извлечение задач
  - [ ] Сохранение в JSON
- [ ] **7.4** Создать адаптер для FL.ru
- [ ] **7.5** Реализовать Skills Extractor
- [ ] **7.6** Реализовать простой Matching (точное совпадение)
- [ ] **7.7** Создать генератор черновиков предложений
- [ ] **7.8** Создать базовый Dashboard (CLI/Markdown)

### MVP #2 — Умный матчинг

- [ ] **7.9** Реализовать семантический Skill Matcher
- [ ] **7.10** Реализовать Clarity Scorer
- [ ] **7.11** Создать генератор планов решений
- [ ] **7.12** Реализовать scaffold для веб-проектов
- [ ] **7.13** Интегрировать с Dashboard

### MVP #3 — Защита и масштабирование

- [ ] **7.14** Реализовать водяные знаки
- [ ] **7.15** Создать систему деплоя на Vercel/Netlify
- [ ] **7.16** Добавить адаптеры для Kwork, Freelancer
- [ ] **7.17** Создать веб-Dashboard
- [ ] **7.18** Реализовать систему отчётов

---

*Документ будет дополняться по мере разработки*
