---
name: shrelock-research
description: 8-фазный исследовательский пайплайн Шерлока (Scope→Plan→Retrieve→Triangulate→Synthesize→Critique→Refine→Package) + competitive-intelligence фреймворк. Адаптирован из Auto-Company `.claude/skills/deep-research/` + `competitive-intelligence-analyst/`. Для профиля sherlock: поиск вакансий, исследования рынка, competitor-матрицы, pricing intel.
argument-hint: "[исследовательский вопрос + режим quick|standard|deep|ultradeep]"
disable-model-invocation: true
---

# Shrelock Research — мозг Шерлока

Адаптированный исследовательский пайплайн из Auto-Company (MaxMiksa, 2563★).
Объединяет deep-research (8-фазный pipeline) + competitive-intelligence (competitor-матрицы, gap analysis).

## Зачем

Шерлок = поисковый разведчик. Ему нужна методология для:
- Поиска вакансий (HH.ru, Kwork) с анализом рынка
- Исследований конкурентов (feature matrix, pricing, positioning)
- Разбора технологий/подходов (compare X vs Y)
- Проверки фактов (2+ источника на утверждение)

## Триггер

- «Исследуй [тема]» / «разбери [тема]» / «compare X vs Y»
- «Найди вакансии по [направление]» + анализ рынка
- «Кто конкуренты [продукт]?» / «pricing intel [сегмент]»
- «Проверь факт [утверждение]»
- Входной параметр `$ARGUMENTS` — описание вопроса

## Режимы

| Режим | Фазы | Время | Источники | Когда |
|---|---|---|---|---|
| **Quick** | 3 | 2-5 мин | 5-10 | Экспресс-обзор, срочно |
| **Standard** | 6 | 5-10 мин | 15-30 | Большинство задач [DEFAULT] |
| **Deep** | 8 | 10-20 мин | 30-50 | Важное решение, проверка |
| **UltraDeep** | 8+ | 20-45 мин | 50+ | Критический анализ |

## 8-фазный пайплайн (адаптирован из Auto-Company)

### Фаза 1. SCOPE — границы
1. Разобрать `$ARGUMENTS` на подвопросы
2. Определить режим (quick/standard/deep/ultradeep)
3. Указать: что входит в скоуп, что НТ

### Фаза 2. PLAN — стратегия
1. Декомпозировать на 5-10 углов поиска
2. Выбрать источники (см. «Наши источники»)
3. Определить параллельные задачи для субагентов

### Фаза 3. RETRIEVE — параллельный сбор
**Обязательно параллельно:**
1. Разложить запрос на 5-10 независимых поисковых углов
2. Запустить ВСЕ поиски в одном сообщении (web_search + web_extract)
3. Качественный порог: track source count + credibility
4. Spawn 3-5 субагентов через `delegate_task` для глубоких копаний

**Наши источники (в порядке приоритета):**
| Источник | Когда | Как |
|---|---|---|
| **web_search** | Общий поиск | `web_search(query, limit=10)` |
| **web_extract** | Детальный разбор URL | `web_extract([urls])` |
| **browser_exec** | SPA (Kwork, HH), JS-рендер | `browser_exec(code)` |
| **HH API** | Вакансии на hh.ru | `web_search("site:hh.ru ...")` + browser_exec |
| **Kwork** | Фриланс-биржа | Playwright headless (см. `cron_jobs/kwork_finder.py`) |
| **arXiv** | Академические исследования | `web_search("arxiv [topic]")` + arxiv skill |
| **GitHub** | Код, лицензии, stars | `gh search repos [query]` |
| **Supabase** | Наша БД ai-scout | Через REST API (если нужно) |

### Фаза 4. TRIANGULATE — верификация
1. 3+ источника на каждое ключевое утверждение
2. Различать FACTS (из источников) vs SYNTHESIS (анализ)
3. Маркировать: «According to [1]...» / «[1] reports...»
4. Нет источников → «No sources found for X» (НЕ фабриковать)

### Фаза 4.5 OUTLINE REFINEMENT — адаптация структуры
На основе найденного скорректировать план отчёта (WebWeaver 2025).

### Фаза 5. SYNTHESIZE — инсайты
1. Генерировать новое знание, а не пересказывать источники
2. Паттерны, тренды, неочевидные связи
3. Конкурентные матрицы (если применимо)

### Фаза 6. CRITIQUE — красная команда (Deep+)
1. Контраргументы, контрдоказательства
2. Слабые места методологии
3. Альтернативные интерпретации

### Фаза 7. REFINE — доработка (Deep+)
1. Закрыть пробелы
2. Усилить слабые утверждения
3. Проверить цитаты

### Фаза 8. PACKAGE — упаковка

**Формат вывода (markdown):**
```markdown
## Executive Summary (2-3 абзаца, 50-250 слов)

## Introduction (вопрос, скооп, методология)

## Main Analysis (4-8 findings, каждый 300-500 слов + цитаты [1],[2],[3])

## Competitive Landscape (если применимо)
### Feature Comparison Matrix
### Pricing Intelligence
### Positioning Analysis

## Synthesis & Insights (паттерны, инсайты)

## Limitations & Caveats (пробелы, неопределённость)

## Recommendations (действия, следующие шаги)

## Bibliography (ВСЕ цитаты [1]..[N], без пропусков)

## Methodology Appendix (процесс, источники, верификация)
```

**Требования к bibliography (строго):**
- ВСЕ цитаты [N] из тела отчёта → полные записи
- Формат: `[N] Author/Org (Year). "Title". Publication. URL`
- НЕТ пропусков: `[1-50]` — НЕПРАВИЛЬНО
- НЕТ плейсхолдеров: "Additional citations" — НЕПРАВИЛЬНО

**Куда писать:**
- Основной вывод: прямо в чат (инлайн)
- Файл: `~/freelance-2026/projects/hh-ai-agent/docs/outbox/research_<slug>_<YYYYMMDD>.md`
- НЕ писать в `~/.claude/research_output/` — у нас этого нет

## Competitive Intelligence Framework (из Auto-Company)

Для задач «кто конкуренты» / «pricing» / «market gaps»:

### Competitor Deep Dive
Для каждого конкурента:
- Компания: название, URL, год основания, размер
- Продукт: ключевые фичи, positioning
- Pricing: тиры, модель (freemium/subscription)
- Сильные/слабые стороны
- Последние движения (фичи, раунды, партнёрства)

### Feature Comparison Matrix
```
| Feature | Мы | Comp A | Comp B | Comp C |
|---------|-----|--------|--------|--------|
| Feature 1 | Y/N/P | Y/N/P | Y/N/P | Y/N/P |
```

### Pricing Intelligence
```
| Tier | Мы | Comp A | Comp B | Market Avg |
|------|-----|--------|--------|------------|
| Entry | $X | $X | $X | $X |
```

### Gap Analysis
| Gap Type | Как искать | Пример |
|----------|------------|--------|
| Feature gaps | Нет ни у кого | No API, no integrations |
| Customer gaps | Underserved segment | Small teams ignored |
| Pricing gaps | Нет на ценовом промежутке | Nothing between free and $100/mo |
| Experience gaps | UX/complaints | All competitors have bad UX |

### Win/Loss Patterns
| Pattern | Action |
|---------|--------|
| Lose on price | Value messaging или lower tier |
| Lose on features | Roadmap priority |
| Win on ease of use | Double down on simplicity |

## Валидация (scripts/)

Адаптировано под наш формат `brief.md`:
- `scripts/validate_report.py` — 8 проверок качества
- `scripts/citation_manager.py` — трекинг цитат
- `scripts/source_evaluator.py` — credibility scoring (0-100)

Запуск:
```bash
python3 skills/shrelock-research/scripts/validate_report.py --report <path>
```

## Anti-Hallucination Protocol (КРИТИЧНО)

- **Source grounding**: Каждый факт → цитата [N] в том же предложении
- **Clear boundaries**: FACTS vs SYNTHESIS — явно маркировать
- **No speculation without labeling**: «This suggests...» ≠ «Research shows...»
- **Verify before citing**: Не уверен → НЕ цитируй
- **When uncertain**: «No sources found for X» (НЕ выдумывать)

## Формат вывода (обязательный)

```
## Состав исследования
- Режим: [quick/standard/deep/ultradeep]
- Источников: N
- Время: ~X мин

## Вердикт
[ГОПРОСТЬ/НЕТ-ГОПРОСТЬ] + одно предложение.

## Риски
- ...

## Документы
- projects/hh-ai-agent/docs/outbox/research_<slug>_<date>.md
```

## Привязка к задачам

- **T-03** (регистратор): Шерлок берёт этот скилл для поисковых задач
- **ES-N** (экспертные боты): паттерн ложится на многоагентную дискуссию
- **AI-Scout expert analysis**: 8-фазный pipeline как fallback для `expert_analysis`
- **Ночной конвейер Kwork**: исследование рынка + competitor-матрица

## Примечания

- Названия агентов — наши профили (`sherlock/femida/defender/marketer/financier/health`), **не** `.claude/agents/*` из Auto-Company
- Выход: `projects/hh-ai-agent/docs/outbox/`, не `~/.claude/research_output/`
- Структура `SKILL.md` — по канону Hermes (`---` frontmatter + `name`/`description` + `argument-hint` + `disable-model-invocation`)
- Китайский текст из оригинала убран; нотация адаптирована под ru
- Ссылки на `generating-pdf` skill убраны — используем наш `pdf` skill
- Ссылки на `Task tool` / `general-purpose agent` → `delegate_task` / `subagent_type: general-purpose`
