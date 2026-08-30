# Solutions — единый указатель фич/инструментов/решений

> Собрано из разбросанных папок vault/ (06-Library, 05-Audits, 04-Decisions, 03-Lessons) и docs/solutions/. ОРИГИНАЛЫ В VAULT НЕТРОНУТЫ — это копии.

Всего заметок: 29

## Категории

### Решения / tools (свежие, hand-written) (5)

- [auto-company — автономная AI-компания 24/7 на 14 агентах + Dashboard + daemon](./auto-company.md)  _(экспертный разбор)_
- [macos-harness — computer-use бэкенд для Mac](./macos-harness.md)  _(оригинал: vault)_
- [Ornith-1.5 — локальный агентный «мозг» (LLM, не замена macos-harness)](./ornith_1_5.md)  _(оригинал: vault)_
- [Qwen3.8-27B-Uncensored-MLX — локальная без-цензуры LLM на Mac](./qwen3_8_uncensored_mlx.md)  _(оригинал: vault)_
- [Vercel fx — ультралёгкий coding-агент (один бинарь, Zig)](./vercel-fx.md)  _(оригинал: vault)_
- [Claude Code session efficiency — выжимка стоимости токенов](./claude-code-session-efficiency.md)  _(оригинал: vault)_
- [razbor-servisa — реверс сервиса без API → CLI для агента](./razbor-servisa.md)
- [watermarks-remover — гигиена AI-провенанса, skill/service split как эталон для CP-1](./watermarks-remover.md)

### Library/books — digest (инструменты/статьи) (8)

- [20260808_About Python_trade_ _ Python.org](./lib__20260808_about-python_trade_-_-pythonorg.md)  _(оригинал: vault)_
- [20260808_GitHub - jacob-bd_gemini-notebook-mcp-cli_ Programmatic access to Gemini Notebook - via command-line interface (CLI)_ Mo](./lib__20260808_github---jacob-bd_gemini-notebook-mcp-cli_-programmatic-access-to-gemini-notebook---via-command-line-interface-cli_-mo.md)  _(оригинал: vault)_
- [20260808_notebooklm-mcp _ PyPI](./lib__20260808_notebooklm-mcp-_-pypi.md)  _(оригинал: vault)_
- [20260809_llms.txt _ кто его реально читает и нужен ли он вашему сайту __x2F_ Хабр](./lib__20260809_llmstxt-_-----------__x2f_-.md)  _(оригинал: vault)_
- [20260813_BSS перевела _Речевую аналитику_ на рельсы автономных ИИ-агентов_ вышел новый релиз 2.15](./lib__20260813_bss--_-_-----_----215.md)  _(оригинал: vault)_
- [20260814_This 12-Year-Old Created an AI Receptionist to Help Small Businesses - Business Insider](./lib__20260814_this-12-year-old-created-an-ai-receptionist-to-help-small-businesses---business-insider.md)  _(оригинал: vault)_
- [Ключевые тезисы](./lib__llms-txt-habr.md)  _(оригинал: vault)_
- [Agentic AI Guide (NotebookLM)](./lib__nblm-agentic-ai-guide.md)  _(оригинал: vault)_

### Audits (аудиты инструментов/кода) (15)

- [AN-1: Бенчмарк AnyDoc (firecrawl) — локальный DOCX → Markdown (08.08.2026)](./audit__an1_anydoc_benchmark.md)  _(оригинал: vault)_
- [AN-1: Бенчмарк AnyDoc vs MinerU — ЧАСТИЧНО, блокер: диск + прокси](./audit__an1_anydoc_vs_mineru.md)  _(оригинал: vault)_
- [AR-1: Agent-Reach — НЕ ПРИМЕНИМ в исходной формулировке](./audit__ar1_agent_reach.md)  _(оригинал: vault)_
- [CE-2/CE-3: Изучение ce-plan/ce-code-review/lfg + вывод](./audit__ce_cv_review.md)  _(оригинал: vault)_
- [CV-1: Caveman-компрессия AGENTS.md / CLAUDE.md — эксперимент (07.08.2026)](./audit__cv1_caveman_compress.md)  _(оригинал: vault)_
- [CV-3: junior-to-senior и loop-factory — оценка (08.08.2026)](./audit__cv3_loop_factory.md)  _(оригинал: vault)_
- [HT-1: Инвентаризация правил «НИКОГДА» — кандидаты на перевод в код](./audit__ht1_rules_inventory.md)  _(оригинал: vault)_
- [HT-2: Тулсет-аудит — вес скиллов в системном промпте](./audit__ht2_toolset_audit.md)  _(оригинал: vault)_
- [K4: Контракты AI-Scout (Collector/Analyst/Curator) — проверка 08.08.2026](./audit__k4_aiscout_contracts.md)  _(оригинал: vault)_
- [LV-3: Аудит веса промптов (levitan autopilot)](./audit__lv3_prompts_audit.md)  _(оригинал: vault)_
- [PF-3: Аудит «функции над данными»](./audit__pf3_functions_over_data.md)  _(оригинал: vault)_
- [RB-1: Память-факты vs сырая векторизация (сверка)](./audit__rb1_facts_over_rag.md)  _(оригинал: vault)_
- [RB-3: Self-hosted эмбеддинги для smart-rag (08.08.2026)](./audit__rb3_selfhosted_embeddings.md)  _(оригинал: vault)_
- [RW-1: Пилот repowise — ЧАСТИЧНО, блокер: облачная авторизация](./audit__rw1_repowise_pilot.md)  _(оригинал: vault)_
- [SA-3: «Дешёвое доказательство» — инвентаризация верификации](./audit__sa3_cheap_proofs.md)  _(оригинал: vault)_

### Decisions (ADR) (1)

- [RW-4: Решение по лицензии AGPL-3.0 (repowise)](./dec__RW-4-agpl-repowise.md)  _(оригинал: vault)_

### Lessons (уроки) (2)

- [Юр-разбор: Чек-лист подачи на Грант «Старт-1»](./lesson__2026-08-08_femida_grant_checklist_report.md)  _(оригинал: vault)_
- [PF-1: Неблокирующие субагенты (Prime Agent паттерн)](./lesson__2026-08-08_nonblocking_subagents.md)  _(оригинал: vault)_

## Источники (оригиналы в vault, не трогали)

- `vault/06-Library/books/` — digest+source по инструментам/статьям
- `vault/05-Audits/` — аудиты
- `vault/04-Decisions/` — ADR
- `vault/03-Lessons/` — уроки

---
_Сгенерировано автоматически, 2026-08-19. Копии, не оригиналы._ls ~/freelance-2026/docs/solutions/
