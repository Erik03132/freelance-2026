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

### 4. DFlash — Block Diffusion для ускорения LLM-инференса (Z Lab)

| Поле | Значение |
|------|----------|
| **Статус** | 🔵 ASSESS |
| **URL** | https://github.com/z-lab/dflash |
| **Компания** | Z Lab (MIT, Zhijian Liu) |
| **Лицензия** | ✅ MIT (open source) |
| **Язык** | Python (PyTorch, MLX) |
| **Paper** | [arXiv:2602.06036](https://arxiv.org/abs/2602.06036) |
| **Что делает** | Speculative decoding через блочную диффузионную модель. Маленький «draft model» генерирует 16 токенов за один параллельный forward pass, большая LLM верифицирует. Результат: **2-6× lossless ускорение** инференса без потери качества. |
| **Дата оценки** | 2026-05-12 |

**Как это работает (ключевая идея):**
- Обычный speculative decoding (EAGLE-3): draft-модель генерирует токены последовательно → потолок 2-3×
- **DFlash**: draft-модель на основе block diffusion генерирует **все 16 токенов параллельно за 1 pass**
- Архитектура: Feature Fusion (скрытые слои target-модели) → KV Injection (каждый слой draft-модели) → Parallel Drafting
- Draft-модель переиспользует embedding и LM head от target → минимум параметров

**Заявленные результаты (Qwen3-8B):**
- До **6× lossless ускорение** (greedy decoding)
- **~4.5× ускорение** с sampling (temperature=1) и thinking mode
- **~2.5× быстрее** чем EAGLE-3 (предыдущий SOTA)

**Поддерживаемые модели (20+):**
- Qwen3/3.5/3.6 (4B — 122B), Qwen3-Coder
- Gemma-4 (26B, 31B)
- GPT-OSS (20B, 120B)
- Kimi-K2.5/K2.6, MiniMax-M2.5/M2.7
- Llama-3.1-8B
- DeepSeek-V4 (coming soon)

**Бэкенды:**
| Backend | Статус | Применимость |
|---------|--------|-------------|
| **vLLM** | ✅ v0.20.1+ | Production serving |
| **SGLang** | ✅ Полная | Production serving |
| **Transformers** | ✅ Qwen3/Llama | Эксперименты |
| **MLX (Apple Silicon)** | ✅ M-серия | Локальный инференс на Mac |

**Установка (MLX для нашего Mac):**
```bash
pip install -e ".[mlx]"
```

```python
from dflash.model_mlx import load, load_draft, stream_generate

model, tokenizer = load("Qwen/Qwen3.5-4B")
draft = load_draft("z-lab/Qwen3.5-4B-DFlash")

messages = [{"role": "user", "content": "Вопрос"}]
prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
for r in stream_generate(model, draft, tokenizer, prompt, block_size=16, max_tokens=2048):
    print(r.text, end="", flush=True)
```

**Почему ASSESS (а не TRIAL):**
- 🎯 Мы пока не хостим LLM сами — используем API (OpenRouter, Gemini)
- 🖥️ Для продакшн-сервинга нужны GPU (NVIDIA A100/H100)
- 🍎 MLX-бэкенд на Mac M-серии — интересно для локальных экспериментов
- 📊 Когда перейдём на self-hosted LLM (Ollama / vLLM) — DFlash станет критически важным

**Где может пригодиться:**
- 🔥 **Self-hosted LLM** — если развернём Qwen3 или DeepSeek на VPS с GPU → DFlash даст 3-6× ускорение бесплатно
- 🍎 **Локальный Mac инференс** — MLX + DFlash для быстрого Qwen3.5-4B на M5 Pro
- 🧪 **RAG-пайплайны** — ускорение генерации ответов из базы знаний
- 💰 **Cost reduction** — за ту же цену GPU обслуживаем в 3-6× больше запросов

**Когда внедрять:**
- При переходе на self-hosted LLM (запланирован в Q3 2026 roadmap)
- Или сейчас для локальных экспериментов с MLX на Mac

---

### 5. Open Design — Каталог AI-дизайн-скиллов (nexu-io)

| Поле | Значение |
|------|----------|
| **Статус** | 🟡 TRIAL |
| **URL** | https://github.com/nexu-io/open-design |
| **Компания** | nexu.io (open-source community) |
| **Лицензия** | ✅ Apache 2.0 |
| **Язык** | TypeScript |
| **GitHub** | ⭐ 37 670 stars · 4 280 forks · обновляется ежедневно |
| **Что делает** | Local-first open-source альтернатива Claude Design. 100+ скиллов, 71 дизайн-система. Генерация прототипов web/mobile/desktop, слайдов, видео, изображений с экспортом в HTML/PDF/PPTX/MP4. |
| **Совместимость** | ✅ Claude Code, Codex, Cursor, **Gemini**, Copilot, Qwen, Kimi CLI |
| **Дата оценки** | 2026-05-12 |

**Что внутри (100+ скиллов по категориям):**

| Категория | Примеры скиллов | Кол-во |
|-----------|----------------|--------|
| **Design Systems** | frontend-design, shadcn-ui, platform-design, apple-hig, brand-guidelines | ~15 |
| **Presentations** | slides, pptx-generator, nanobanana-ppt, html-ppt-retro | ~8 |
| **Image/Video Gen** | fal-generate, fal-video-edit, fal-3d, sora, replicate, imagen, imagegen | ~15 |
| **Marketing** | ad-creative, copywriting, marketing-psychology, screenshots-marketing | ~6 |
| **Animation** | gsap-core, gsap-react, gsap-scrolltrigger, threejs, remotion, shader-dev | ~8 |
| **Documents** | pdf, docx, minimax-pdf, minimax-docx, doc | ~5 |
| **UX/UI** | design-review, design-consultation, design-brief, ui-ux-pro-max, taste-skill | ~10 |
| **Figma** | figma-generate-design, figma-implement-design, figma-create-design-system-rules | ~7 |
| **Media** | venice-image-generate, venice-video, venice-audio-music, speech, ai-music-album | ~8 |
| **Прочие** | agent-browser, youtube-clipper, video-downloader, domain-name-brainstormer | ~10+ |

**Архитектура:**
- Каждый скилл — SKILL.md + assets (frames, templates, examples)
- Формат совместим с agentskills.io (тот же формат, что у нас!)
- Upstream-ссылки на оригинальные Anthropic skills
- `od:` метаданные для категоризации и discovery

**Пересечение с нашими скиллами:**
| Наш скилл | Open Design аналог | Что полезного |
|-----------|-------------------|---------------|
| `rembrandt-designer` | `frontend-design`, `design-review`, `ui-ux-pro-max` | Референсные дизайн-системы, паттерны ревью |
| `frontend-design` | `frontend-design`, `shadcn-ui`, `gsap-*` | GSAP-анимации, shadcn-компоненты |
| `copywriting` | `copywriting`, `ad-creative` | Шаблоны рекламных креативов |
| `marketing-psychology` | `marketing-psychology` | Альтернативная база паттернов |
| `brainstorming` | `brainstorming`, `design-brief` | Design brief + brainstorming workflow |
| `social-content` | `social-carousel` | Карусели для соцсетей |
| — (нет) | `fal-*` (15 скиллов!) | 🔥 Генерация изображений/видео через Fal.ai |
| — (нет) | `slides`, `pptx` | 🔥 Генерация презентаций |
| — (нет) | `figma-*` (7 скиллов) | 🔥 Прямая работа с Figma |

**Почему TRIAL:**
- ✅ Apache 2.0 — полная свобода использования
- ✅ 37K+ ⭐ — самый популярный open-source дизайн-каталог
- ✅ Совместимый формат скиллов (agentskills.io)
- ✅ Можно cherry-pick отдельные скиллы в нашу экосистему
- 🎯 Прямая польза: `fal-*` скиллы для генерации картинок/видео, `slides` для презентаций
- 🎯 Рембрандт может использовать их design systems как референсы

**Что попробовать первым:**
1. `fal-generate` — генерация изображений для постов ВК/ОК (замена стоковым фото)
2. `slides` / `pptx` — генерация презентаций для грантов (ai-grant-consalt)
3. `gsap-core` — анимации для лендингов

---

### 6. Vibeyard — IDE для AI-кодинг-агентов (elirantutia)

| Поле | Значение |
|------|----------|
| **Статус** | 🔵 ASSESS |
| **URL** | https://github.com/elirantutia/vibeyard |
| **Автор** | Eliran Tutia (indie dev) |
| **Лицензия** | ✅ MIT |
| **Язык** | TypeScript / Electron |
| **GitHub** | ⭐ 994 stars · 127 forks |
| **Платформы** | macOS (DMG), Linux (deb/AppImage), Windows (exe), npm |
| **Что делает** | Desktop IDE для управления несколькими AI-кодинг-агентами. Multi-session, parallel execution, cost tracking, kanban board, session resume. |
| **Дата оценки** | 2026-05-12 |

**Ключевые фичи:**
- 🖥️ **Multi-session** — несколько агент-сессий параллельно, каждая в своём PTY
- 📊 **Cost & context tracking** — расходы, токены, контекстное окно в реальном времени
- 📋 **Kanban board** — drag-and-drop задачи, каждая карточка → CLI-сессия одним кликом
- 🔄 **Session resume** — продолжение работы после перезапуска
- 🌐 **P2P session sharing** — шаринг терминала через WebRTC (read-only / read-write)
- 🔍 **Session inspector** — timeline, cost breakdown, tool usage stats (`Cmd+Shift+I`)
- 🤖 **AI Readiness Score** — оценка готовности проекта к AI-кодингу
- 🌐 **Embedded browser** — открытие localhost прямо в табе, click-to-inspect → AI-редактирование
- 🎨 **Swarm mode** — grid view всех сессий одновременно

**Поддерживаемые CLI:**
| Agent CLI | Статус |
|-----------|--------|
| Claude Code | ✅ |
| OpenAI Codex CLI | ✅ |
| Gemini CLI | ✅ |

**Установка:**
```bash
npm i -g vibeyard && vibeyard
# или скачать .dmg из Releases
```

**Почему ASSESS (а не TRIAL):**
- ⚠️ Мы уже используем **Antigravity** — наш основной IDE для AI-агентов
- ⚠️ 994 ⭐ — ещё молодой проект (создан 19.03.2026)
- ⚠️ Electron = тяжёлый (на M1 с 8 GB — лишняя нагрузка)
- ✅ Но: kanban + cost tracking + multi-session — интересные фичи
- ✅ P2P sharing — полезно для командной работы

**Что можно позаимствовать (идеи):**
- 💡 **AI Readiness Score** — можно реализовать как скилл для нашей экосистемы
- 💡 **Cost tracking dashboard** — встроить в finish-day или waza-audit
- 💡 **Embedded browser + click-to-inspect** — идея для лендинг-аудита

**Когда пересмотреть:**
- Если Antigravity не покроет multi-agent orchestration
- Если появится потребность в P2P session sharing для команды

---

## 📝 Журнал изменений

| Дата | Действие |
|------|----------|
| 2026-05-12 | Добавлен: Vibeyard (ASSESS) — IDE для AI-агентов, kanban + cost tracking |
| 2026-05-12 | Добавлен: Open Design (TRIAL) — 100+ AI-дизайн-скиллов, 71 design system, Apache 2.0 |
| 2026-05-12 | Добавлен: DFlash (ASSESS) — block diffusion для 2-6× ускорения LLM-инференса |
| 2026-05-11 | ✅ Waza v0.31.0 УСТАНОВЛЕН, waza-audit.sh создан, интеграция в finish-day.sh |
| 2026-05-11 | Waza → 🟢 ADOPT. Первый аудит: 168K токенов, 76 файлов, 41 скилл проверен |
| 2026-05-11 | Добавлен: Waza (TRIAL) — Microsoft CLI для тестирования AI-скиллов |
| 2026-05-11 | Добавлены: Blockify (ASSESS), OfficeCLI (ASSESS) |

