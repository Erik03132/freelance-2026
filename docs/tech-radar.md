# 🛰️ Tech Radar — Инструменты на вооружение

> SSoT-файл для отслеживания перспективных технологий и инструментов.
> Обновляется по мере обнаружения интересных решений.

**Последнее обновление:** 2026-05-11

---

## Статусы

| Статус | Значение |
|--------|----------|
| 🟢 **ADOPT** | Берём в работу, внедряем |
| 🟡 **TRIAL** | Тестируем, пилотируем |
| 🔵 **ASSESS** | Оценили, ждём момента |
| ⚪ **HOLD** | Интересно, но не сейчас |

---

## 📋 Radar

### 1. Blockify — Agentic Data Optimization for RAG

| Поле | Значение |
|------|----------|
| **Статус** | 🔵 ASSESS |
| **URL** | https://github.com/iternal-technologies-partners/blockify-agentic-data-optimization |
| **Компания** | Iternal Technologies, Inc. |
| **Лицензия** | ⚠️ Blockify Community License (кастомная EULA, НЕ open source). Revenue >$1M → Enterprise. Запрет на Competing Products и Managed Service. |
| **Что делает** | Замена naive chunking в RAG на структурированные IdeaBlocks (XML Q&A пары с метаданными). Pipeline: Ingest → Distill → Store. LLM конвертирует chunks в Q&A, потом дедуплицирует через LSH + embeddings. |
| **Заявленные метрики** | 78X accuracy aggregate, 2.29X vector search precision, 40X compression, 3.09X token efficiency |
| **Скоринг** | 54/80 — перспективная идея, vendor lock-in |
| **Дата оценки** | 2026-05-11 |
| **Полный обзор** | Артефакт `blockify_expert_review.md` (conversation 8ef15a4f) |

**Что берём:**
- Паттерн IdeaBlock (structured Q&A + metadata + dedup) → адаптируем для SmartFAQ Angelochka
- Semantic deduplication через FAISS + LSH
- Двухфазный pipeline (Ingest → Distill)

**Что НЕ берём:**
- SaaS-зависимость от Blockify API (core IP закрыт)
- Кастомную лицензию с ловушками

**Когда может понадобиться:**
- При масштабировании RAG для Angelochka (>500 документов в базе знаний)
- При создании SmartBlock формата для ВезёмЦыплят

---

### 2. OfficeCLI — Office Suite для AI-агентов

| Поле | Значение |
|------|----------|
| **Статус** | 🔵 ASSESS |
| **URL** | https://github.com/iOfficeAI/OfficeCLI |
| **Компания** | iOfficeAI |
| **Лицензия** | ✅ Apache-2.0 (настоящий open source) |
| **GitHub** | ⭐ 4K stars, 334 forks, 2743 коммитов, 8 issues, 7 PRs — зрелый проект |
| **Что делает** | CLI-утилита для создания/редактирования Word, Excel, PowerPoint файлов. Single binary (C#/.NET embedded), без установки Office. Специально спроектирован для AI-агентов. |
| **Дата оценки** | 2026-05-11 |

**Ключевые возможности:**
- **Один бинарник** — self-contained, .NET runtime встроен, zero dependencies
- **Word** — параграфы, таблицы, стили, headers/footers, TOC, формулы, watermarks, comments, i18n/RTL
- **Excel** — 150+ формул с автоэвалюацией, pivot tables, charts, conditional formatting, sparklines, CSV import
- **PowerPoint** — слайды, shapes, анимации, morph transitions, 3D модели (.glb), темы, видео/аудио
- **Rendering engine** — рендерит .docx/.xlsx/.pptx в HTML или PNG без Office. Агент видит результат
- **Template merge** — `{{key}}` плейсхолдеры, один шаблон → N заполненных документов
- **MCP Server** — встроенный, одна команда для Claude Code, Cursor, VS Code
- **Batch mode** — JSON-массив операций в одном вызове
- **Resident mode** — документ в памяти через named pipes, near-zero latency
- **Path-based addressing** — `/slide[1]/shape[2]`, агент не касается XML namespaces
- **Self-healing** — structured error codes, suggestions, valid ranges

**Установка:**
```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash

# MCP для Claude Code
officecli mcp claude
```

**Где может пригодиться:**
- 📊 **AutoReports для клиентов** — генерация отчётов (Excel/Word) из Bitrix24 данных через агента
- 📋 **Коммерческие предложения** — шаблонизация КП в .docx с динамическими данными из CRM
- 🎨 **Презентации** — автогенерация deck'ов для грантов/инвесторов
- 📄 **Договоры/счета** — merge-шаблоны с CRM-данными
- 🤖 **Angelochka** — формирование офисных документов по запросу клиента в TG-боте

**Когда внедрять:**
- Когда появится задача на автоматическую генерацию офисных документов
- Бесплатен, Apache-2.0, plug-and-play — можно начинать в любой момент

---

### 3. Waza — CLI/Framework для тестирования AI-скиллов (Microsoft)

| Поле | Значение |
|------|----------|
| **Статус** | 🟡 TRIAL |
| **URL** | https://github.com/microsoft/waza |
| **Компания** | Microsoft |
| **Лицензия** | ✅ MIT (настоящий open source) |
| **Язык** | Go (single binary, кросс-платформенный) |
| **Что делает** | CLI для создания, тестирования, измерения и улучшения качества AI-агентских скиллов. Scaffold eval suites, run benchmarks, compare results across models. |
| **Дата оценки** | 2026-05-11 |

**Ключевые возможности:**
- `waza init` — создание проекта с `skills/` + `evals/` структурой
- `waza new skill` — генерация скаффолда для нового скилла + eval suite
- `waza run` — запуск eval benchmarks с параллельными workers, кэшированием, retry
- `waza check` — проверка готовности скилла к продакшну (compliance, tokens, coverage)
- `waza quality` — LLM-as-Judge оценка по 5 осям (clarity, completeness, trigger precision, scope, anti-patterns)
- `waza suggest` — LLM генерирует eval artifacts из SKILL.md
- `waza compare` — сравнение результатов между моделями (delta per task, pass rate)
- `waza dev` — итеративное улучшение frontmatter скилла
- `waza tokens count/compare/suggest` — управление токен-бюджетом скиллов
- `waza serve` — dashboard для визуализации результатов
- `waza coverage` — матрица покрытия skills ↔ evals
- `waza grade` — отдельная прогонка graders без re-execution

**9 типов Graders:**
| Grader | Назначение |
|--------|-----------|
| `text` | Regex / substring matching в output |
| `code` | Python/JS assertions |
| `file` | Проверка существования и содержимого файлов |
| `diff` | Сравнение workspace с snapshot'ами |
| `behavior` | Ограничения (max tool calls, duration, tokens) |
| `action_sequence` | Валидация последовательности tool calls (F1 scoring) |
| `skill_invocation` | Проверка порядка вызова скиллов |
| `prompt` | LLM-as-judge с rubric'ой |
| `trigger_tests` | Точность trigger detection |

**CI/CD интеграция:**
- Exit codes: 0=success, 1=test failure, 2=config error
- JUnit XML reporter
- GitHub Actions workflow из коробки
- `--format github-comment` для PR комментариев
- Azure Blob Storage для истории результатов

**Установка:**
```bash
curl -fsSL https://raw.githubusercontent.com/microsoft/waza/main/install.sh | bash
```

**Почему TRIAL (а не ASSESS):**
- 🎯 **Прямой кейс**: у нас 28+ скиллов в `~/.gemini/antigravity/skills/` — Waza может измерить их качество
- 🏢 **Microsoft** — серьёзный бэкинг, MIT лицензия, zero risk
- 🔧 **Plug-and-play** — Go binary, zero dependencies, `curl | bash`
- 📐 **Совпадает с нашим SKILL.md форматом** — trigger hints, frontmatter, eval structure
- 🧪 **skill-creator skill** у нас уже есть — Waza дополняет его eval/quality стороной

**Где применяем:**
- 🧪 **Тестирование скиллов Antigravity** — автоматическая оценка quality/compliance всех 28 скиллов
- 📊 **Token budgeting** — `waza tokens count skills/` покажет раздутые скиллы
- 🔄 **CI gate** — `waza check` перед деплоем нового скилла на VPS
- 📈 **Сравнение моделей** — `waza run --model gpt-4o --model claude-sonnet` для выбора LLM
- 🎯 **Trigger accuracy** — `trigger_tests` grader покажет, правильно ли матчатся скиллы

**Когда внедрять:**
- Можно начинать СЕЙЧАС — бесплатно, MIT, идеально совпадает с нашей инфраструктурой скиллов

---

## 📝 Журнал изменений

| Дата | Действие |
|------|----------|
| 2026-05-11 | ✅ Waza v0.31.0 УСТАНОВЛЕН, waza-audit.sh создан, интеграция в finish-day.sh |
| 2026-05-11 | Waza → 🟢 ADOPT. Первый аудит: 168K токенов, 76 файлов, 41 скилл проверен |
| 2026-05-11 | Добавлен: Waza (TRIAL) — Microsoft CLI для тестирования AI-скиллов |
| 2026-05-11 | Добавлены: Blockify (ASSESS), OfficeCLI (ASSESS) |

