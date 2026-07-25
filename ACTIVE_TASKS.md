# Текущий статус проекта (обновлено 04.07.2026 - 18:00)

---

## 🎯 ГЛАВНОЕ: Мультиагентная система Angela (ГОТОВО)

> Статья: https://habr.com/ru/companies/alpinadigital/articles/1054436/
> Принцип: **70% workflow, 30% автономные агенты**

### 3 Агента Angela

| Агент | Тип | Доля | Функция |
|-------|-----|------|---------|
| **Router** | Workflow | 70% | Определение роли, темы, сложности |
| **KnowledgeBase** | Workflow | 70% | FAQ, товары, контекст, память |
| **Generator** | Autonomous | 30% | LLM с маршрутизацией по тирам |

### Как включить
```bash
# Добавить в .env
USE_MULTI_AGENT=true
```

### Ожидаемый эффект
| Метрика | До | После |
|---------|-----|-------|
| Стоимость API | ~$600/мес | ~$60/мес (-90%) |
| Качество | 70% | 90% (+29%) |
| Предсказуемость | Низкая | Высокая |

---

## 📋 ВЫПОЛНЕННОЕ (02.07.2026)

### Angela
- [x] FAQ-эталоны (8-10 эталонных ответов на роль)
- [x] Prompt caching (`cache_control: ephemeral`)
- [x] Мультиагентная архитектура: Router + KnowledgeBase + Generator
- [x] Аналитика статьи 1054436: 70/30 workflow/autonomy

### ContentCombine (ai-scout)
- [x] Pexels интеграция для визуалов в Telegram
- [x] Автопоиск фото по тегам статьи
- [x] Чипсы вместо select в форме добавления инструмента
- [x] HTML to Markdown конвертер (BeautifulSoup, очистка Habr/Medium)

### Sherl-Research
- [x] Оптимизация system prompt (28 → 131 строка)
- [x] Search-First Protocol, GEO-Scan, Competitor Audit
- [x] Шаблоны вывода (GEO-отчёт, анализ конкурента)

### HH.ru AI Agent (04.07.2026)
> Статья: https://habr.com/ru/articles/1055530/
> Стек: Python, Playwright, Ollama, Aiogram, SQLite
> Репо: https://github.com/fikstt2/hh-ai-agent

| Фича | Коммит | Статус |
|------|--------|--------|
| Analytics Database Schema | `c20b354` | ✅ |
| A/B Prompt Testing | `aaa9624` | ✅ |
| Multi-Resume Support | `461150e` | ✅ |
| Rate Limiting | `897edef` | ✅ |
| Analytics Dashboard (/stats) | `3a43c88` | ✅ |

**Что сделано:**
- [x] Таблицы `analytics_events`, `conversion_metrics` для трекинга конверсии
- [x] Два промпта: v1 (классический) + v2 (hook/match/proof, 150 слов)
- [x] 3 резюме: backend, fullstack, CV — авто-выбор по ключевым словам
- [x] Rate limiter: 20 откликов/час, 30 сек между откликами
- [x] Команды `/stats` (дашборд) и `/prompt` (версия промпта)
- [x] 18 тестов, все проходят

**Архитектура:**
```
main.py (asyncio.gather)
├── tg_bot.py (aiogram) → /stats, /prompt
├── hh_client.py (playwright) → search_and_apply, check_chats
├── ai_analyzer.py (ollama) → A/B prompts, YES/NO фильтр
├── analytics.py → conversion tracking
└── database.py (SQLite) → applied_jobs, analytics_events
```

### Архитектура
- [x] Multi-agent architecture для ai-scout (Collector/Analyst/Curator)
- [x] Angela architecture plan (Router/KB/Generator)

---

## 📚 ПРИМЕНЕНИЕ: Claude Code Prompt Library + Matt Pocock Skills

> Источники:
> - https://code.claude.com/docs/en/prompt-library
> - https://github.com/mattpocock/skills (156k stars)
> Статус: ✅ Проанализировано, применяется

### Ключевые паттерны

#### 1. CONTEXT.md — Shared Language
Создать CONTEXT.md для каждого проекта с доменными терминами.
**Применено:** `ai-eggs/CONTEXT.md`, `ai-scout/CONTEXT.md`

#### 2. ADR — Architecture Decision Records
Фиксировать архитектурные решения с контекстом и последствиями.
**Применено:** `ai-eggs/docs/adr/001-multi-agent-architecture.md`

#### 3. Grill Session — Interview Before Building
Интервью перед построением для уточнения требований.
**Применение:** Перед каждым крупным изменением проводить grill session.

#### 4. Vertical Slices — Independent Issues
Разбивать план на независимые задачи.
**Применение:** ACTIVE_TASKS.md разбит на горизонтальные слайсы.

#### 5. Two-axis Code Review — Standards + Spec
Двухосевой обзор: стандарты + спецификация.
**Применение:** Добавить в CLAUDE.md для каждого проекта.

#### 6. TDD — Red-Green-Refactor
Test-Driven Development с циклом красный-зелёный-рефакторинг.
**Применение:** Добавить в CLAUDE.md для Angela.

#### 7. Claude Handoff — Background Agents
Передача задач фоновым агентам через handoff summary.
**Применено:**
- Шаблон в AGENTS.md (пункт 7)
- Глобальный CLAUDE.md (`~/CLAUDE.md`)
- Alias: `handoff "задача"` или `ho "задача"`
- Скрипт: `~/.config/opencode/handoff.sh`
- Skill: `~/.config/opencode/skills/claude-handoff/SKILL.md`
**Сценарии:**
- Долгие задачи (>10 мин) → `ho "название" "описание"`
- Параллельная работа → несколько `ho`
- Эскалация → `escalation: true`
**Примеры:** `docs/handoff-examples.md`

#### 8. Prompt Optimization (Article 1053516)
Оптимизация промптов для снижения галлюцинаций.
**Проблемы:**
- Lost in the Middle (30-40% потеря внимания)
- Contextual Distraction (до 80% падение точности)
- Few-Shot Overrated (примеры не учат)
**Решения:**
- Убрать примеры из промптов
- Убрать повторы и нерелевантные термины
- Сократить системный промпт до <500 токенов
**Результат:** -69% токенов (1933→603), +20% внимание
**Гайд:** `docs/prompt-optimization-guide.md`
**Файлы:** `ai-eggs/agent/prompts_optimized.py`, `test_prompts.py`

---

## 📋 ПЛАН НА НЕДЕЛЮ 1 (02.07 - 09.07.2026)

### ai-levitan: Mango Речевая аналитика 🔴 NEW
> Документ: `ai-levitan/docs/MANGO_SPEECH_ANALYTICS_RECOMMENDATIONS.md`
> Дедлайн: 12.07.2026 (демо-режим истекает через 7 дней)
> **Подход: Сначала 100 звонков → анализ записей → потом настройка Mango**

**Этап 1: Обзвон (сейчас)**
- [ ] **M1.** Провести 100 звонков через текущий пайплайн
- [ ] **M2.** Собрать записи разговоров
- [ ] **M3.** Расшифровать через faster-whisper

**Этап 2: Анализ (после 100 звонков)**
- [ ] **M4.** Прослушать 20-30 записей → выявить паттерны
- [ ] **M5.** Определить топ-10 возражений
- [ ] **M6.** Определить топ-10 вопросов
- [ ] **M7.** Составить список ключевых слов

**Этап 3: Настройка Mango (на основе данных)**
- [ ] **M10.** Подключить Mango демо (только после анализа!)
- [ ] **M11.** Настроить ИИ Помощника с реальным промптом
- [ ] **M12.** Создать тематики с реальными ключевыми словами
- [ ] **M13.** Протестировать на 10 звонках

**Этап 4: Решение (12.07.2026)**
- [ ] **M15.** Сравнить: Mango vs ручной анализ vs DeepSeek
- [ ] **M16.** Решение: платный тариф или свой пайплайн

### Angela
- [ ] **A1.** Замерить реальную экономию после prompt caching (log usage)
- [ ] **A2.** Протестировать FAQ-эталоны на 10-20 диалогах
- [ ] **A3.** Настроить логирование прерванных диалогов (drop-off)

### Claude Code Prompt Library
- [ ] **P1.** Применить "Plan before code" к Angela (планирование перед генерацией)
- [ ] **P2.** Применить "Follow existing patterns" к ai-scout (копировать паттерны)
- [ ] **P3.** Применить "Turn corrections into rules" (создать CLAUDE.md для проектов)

### HH.ru AI Agent
- [ ] **H1.** Настроить `.env` (TG_BOT_TOKEN, TG_USER_ID, OLLAMA_URL)
- [ ] **H2.** Первый запуск: авторизация на HH.ru, сохранение `state.json`
- [ ] **H3.** Протестировать A/B промпты (собирать статистику 1-2 недели)
- [ ] **H4.** Проанализировать конверсию через `/stats`

### x.ai Voice Agent (Пилот)
- [ ] **X1.** Получить API ключ x.ai ($25 кредит для пилота)
- [ ] **X2.** Создать `xai_voice_agent.py` — WebSocket клиент
- [ ] **X3.** Создать `auto_call_pilot.py` — сравнение baresip vs x.ai
- [ ] **X4.** Запустить 10 звонков через x.ai, собрать результаты
- [ ] **X5.** Проанализировать: конверсия, стоимость, качество диалога

### Prompt Optimization
- [x] **PO1.** Оптимизировать промпт Angela (Router: 2000→500 токенов) ✅ -69%
- [ ] **PO2.** Оптимизировать промпт HH.ru bot (Cover Letter: 600→150 токенов)
- [ ] **PO3.** Протестировать на 10 диалогах, сравнить качество
- [ ] **PO4.** Обновить CLAUDE.md / AGENTS.md (убрать примеры)

### Инфраструктура
- [ ] **I1.** Деплой мультиагентной системы Angela на VPS
- [ ] **I2.** SQLite логирование для Angela

---

## 📋 ПЛАН НА НЕДЕЛЮ 2 (09.07 - 16.07.2026)

### ai-levitan: Mango Analytics (результаты демо)
> **12.07.2026:** Демо Mango истекает → РЕШЕНИЕ: платный тариф или свой пайплайн

- [ ] **M7.** Проанализировать результаты демо (10 звонков)
- [ ] **M8.** Сравнить: Mango ИИ Помощник vs DeepSeek LLM
- [ ] **M9.** Принять решение: миграция или возврат
- [ ] **M10.** Если Mango → интегрировать с Telegram ботом

### Angela
- [ ] **A4.** A/B тестирование промптов (сравнение конверсии)
- [ ] **A5.** Мониторинг качества после мультиагентного перехода

### ai-scout
- [ ] **S1.** Разделить на 3 компонента (Collector/Analyst/Curator)
- [ ] **S2.** Добавить метрики для каждого компонента

### Sherl-Research
- [ ] **R1.** Добавить агента-консультанта для вопросов по конкурентам
- [ ] **R2.** Интегрировать с task-prioritizer для скоринга находок

---

## 📋 ПЛАН НА НЕДЕЛЮ 3 (16.07 - 23.07.2026)

### Тестирование
- [ ] **T1.** Запустить Angela в фоновом режиме (2 недели)
- [ ] **T2.** Собрать фидбэк от пользователей
- [ ] **T3.** Оценить точность vs ручной мониторинг

### Оптимизация
- [ ] **O1.** Оптимизировать стоимость API (цель: <$60/мес)
- [ ] **O2.** Оптимизировать качество ответов (цель: >90%)

---

## 📈 Ожидаемый ROI

| Проект | Метрика | До | После | Экономия |
|--------|---------|-----|-------|----------|
| Angela | Стоимость API | ~$600/мес | ~$60/мес | -90% |
| Angela | Качество ответов | 70% | 90% | +29% |
| Angela | Предсказуемость | Низкая | Высокая | — |
| ContentCombine | Визуалы в Telegram | 0 | 100% | — |
| ai-scout | Заполняемость форм | 30% | 75% | +150% |
| HH.ru Agent | Стоимость откликов | 3-5к/мес | 0 | -100% |
| HH.ru Agent | Конверсия откликов | ~2% | ~5% | +150% |
| HH.ru Agent | Время на отклик | 10 мин | 0 мин | -100% |
| x.ai Voice | Качество диалога | Фиксированный | Адаптивный | +200% |
| x.ai Voice | Конверсия звонков | ~15% | ~35% | +130% |
| x.ai Voice | Стоимость звонка | $0 | $0.02-0.05 | +$0.05 |
| Prompt Opt | Галлюцинации | 30% | 10% | -67% |
| Prompt Opt | Токены в промпте | 1933 | 603 | -69% |
| Prompt Opt | Качество ответов | 70% | 85% | +21% |

---

## 🤖 Наша ИИ-Команда (Роли)

- **Босс (Антигравити / Я)** — Архитектор системы, стратег, пишу ядро интеграций.
- **Роботяга (Я)** — Выполняет тяжелые рутинные задачи, парсинг, интеграцию API.
- **Шерлок (Scout/Analyst)** — Ищет и оценивает заказы (Perplexity).
- **Анжела (Sales/Support)** — AI-менеджер по продажам (мультиагентная система).
- **Рембрандт (Designer)** — Генерирует дизайн-токены, UI-компоненты.
- **Кулибин (Engineer)** — Пишет код, работает с БД и деплоит.
- **Хант (HH.ru Bot)** — Автопоиск вакансий, A/B тесты, конверсия откликов.
- **Голос (x.ai Voice)** — Адаптивные голосовые звонки через Mango.

---

## 📋 OmniRoute — Полная настройка AI-шлюза 🔴 NEW

> **Что сделано (25.07.2026):**
> - OmniRoute VPS (217.149.23.113:20128) — установлен, работает
> - OpenRouter провайдер — подключён с API-ключом
> - Компрессия RTK + Caveman (stacked) — включена
> - Semantic cache — включён
> - API-ключ `sk-c7a0aac...` — создан, используется omni-auto и VPS-сервисами
> - omni-auto v3 — VPS → fallback прямой OpenRouter через US-прокси
> - 7 неработающих моделей удалены из списка

### O1. Добавить прямых провайдеров (OpenAI, Anthropic) для fallback
> Сейчас все запросы идут через OpenRouter. Если OpenRouter недоступен — полная остановка.
- [ ] **O1.1.** Найти/создать API-ключи OpenAI и Anthropic
- [ ] **O1.2.** Добавить провайдеры в дашборд OmniRoute
- [ ] **O1.3.** Создать Combo-модели с fallback-цепочкой: OpenRouter → OpenAI → Anthropic
- [ ] **O1.4.** Протестировать fallback: заблокировать OpenRouter → проверить переключение

### O2. Настроить семантический кеш для экономии токенов
> Кеш включён, но пуст. Нужно настроить агрессивное кеширование повторяющихся запросов.
- [ ] **O2.1.** Изучить параметры semantic cache (TTL, max entries, bypass headers)
- [ ] **O2.2.** Настроить агрессивный режим (TTL 30+ мин, большой лимит записей)
- [ ] **O2.3.** Включить idempotency layer (дедупликация одинаковых запросов)
- [ ] **O2.4.** Внедрить cache warming для частых промптов
- [ ] **O2.5.** Настроить мониторинг cache hit rate

### O3. Включить Caveman Output Mode (сжатие ответов)
> Сейчас сжимаются только входящие запросы. Исходящие ответы — без сжатия.
- [ ] **O3.1.** Включить `cavemanOutputMode.enabled = true`
- [ ] **O3.2.** Настроить `autoClarity` — авто-восстановление читаемости после сжатия
- [ ] **O3.3.** Выставить интенсивность `full` для максимальной экономии

### O4. Настроить облачную синхронизацию конфигурации
- [ ] **O4.1.** Включить `cloudEnabled` с Cloudflare Workers
- [ ] **O4.2.** Настроить бэкап конфигурации OmniRoute
- [ ] **O4.3.** Настроить автовосстановление после переустановки VPS

### O5. Мониторинг и алертинг
- [ ] **O5.1.** Настроить сбор метрик: токены/день, cost/день, cache hit rate
- [ ] **O5.2.** Настроить алерт при падении OmniRoute (TG-бот?)
- [ ] **O5.3.** Включить детальное логирование pipeline (compress/decompress)
- [ ] **O5.4.** Создать дашборд экономии (сколько сэкономили на компрессии)

### O6. Распределение по OpenCode
- [ ] **O6.1.** Настроить несколько провайдеров в opencode.jsonc:
  - `omniroute-vps` — через VPS (OmniRoute)
  - `omniroute-fallback` — напрямую OpenRouter через US-прокси
  - `omniroute-free` — только бесплатные модели
- [ ] **O6.2.** Добавить авто-выбор провайдера в opencode.jsonc
- [ ] **O6.3.** Настроить размножение моделей через filter/transform

### O7. Оптимизация стоимости
> Цель: <$20/мес на все AI-API (сейчас $19.61 потрачено из $20 лимита OpenRouter)
- [ ] **O7.1.** Анализ расхода по моделям: что жрёт бюджет
- [ ] **O7.2.** Ограничить Tier 3 модели (Fable 5, Opus 4.8) — только по явному указанию
- [ ] **O7.3.** Добавить бюджетные лимиты в OmniRoute (max spend per day/week)
- [ ] **O7.4.** Максимально использовать free модели (Nemotron Ultra, Ling 3.0, Gemma 4)

### O8. VPS: зафиксировать настройки в конфиге
- [ ] **O8.1.** Создать `server_deploy.sh` — полная установка OmniRoute с нуля
- [ ] **O8.2.** Закоммитить конфигурацию провайдеров в репо (без ключей!)
- [ ] **O8.3.** Создать playbook восстановления после сбоя VPS

---

## 📋 HABR ABR INTELLIGENCE Digest — Новые задачи (NEW)

> Источник: ABR INTELLIGENCE от 25.07.2026 (Habr digest)

### H1. Harness Pipeline Factory — Фабрика пайплайнов
> *Harness engineering — превращает CI/CD в фабрику: declarative pipelines, template library, automated governance, cost optimization.*

**Проекты:** ai-eggs, ai-bureau, ai-scout, agent-lab
- [ ] **H1.1.** Изучить Harness Pipeline Templates — библиотека готовых пайплайнов
- [ ] **H1.2.** Настроить декларативные пайплайны вместо скриптов (YAML + variables)
- [ ] **H1.3.** Template Library — общие шаблоны для всех проектов (build, test, deploy, security scan)
- [ ] **H1.4.** Automated Governance — policy-as-code для security/compliance gates
- [ ] **H1.5.** Cost Optimization — tracking cost per pipeline, per service, per environment
- [ ] **H1.6.** Интеграция с существующими GitHub Actions / GitLab CI (миграция поэтапно)

### H2. Local RAG на Go + PostgreSQL + Ollama
> *Полностью локальный RAG без внешних API: Go-библиотека, pgvector в PostgreSQL, эмбеддинги через Ollama (mxbai-embed-large / nomic-embed-text).*

**Проекты:** ai-bureau, agent-lab
- [ ] **H2.1.** Поднять PostgreSQL + pgvector на VPS / локально
- [ ] **H2.2.** Настроить Ollama с моделями эмбеддингов (mxbai-embed-large, nomic-embed-text)
- [ ] **H2.3.** Go-библиотека: chunking (semantic / fixed), embedding, upsert в pgvector
- [ ] **H2.4.** Hybrid search: vector similarity + BM25 (full-text) + rerank
- [ ] **H2.5.** API: /ingest (documents), /search (query + filters), /chat (RAG + LLM через Ollama)
- [ ] **H2.6.** Eval suite: retrieval accuracy (recall@k), generation quality, latency
- [ ] **H2.7.** Интеграция в ai-bureau (knowledge base для агентов) и agent-lab (local research tool)

---

## 📋 Context Engineering Cleanup (NEW — Anthropic Best Practices)

> Статья: https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models
> Принцип: **убрали 80% системного промпта** — модели теперь сами решают, как писать код, какую плотность комментариев держать, когда создавать доки.

### CE1. Запустить `/doctor` в Claude Code
- [ ] **CE1.1.** Запустить `claude doctor` — получить список перегруженных скиллов/CLAUDE.md
- [ ] **CE1.2.** Применить рекомендации авто-очистки

### CE2. CLAUDE.md — оставить только "gotchas"
- [ ] **CE2.1.** Убрать очевидное (структура репо, как запускать тесты, стандартные паттерны)
- [ ] **CE2.2.** Оставить только нюансы: нестандартные места, где модель ошибётся без подсказки
- [ ] **CE2.3.** Добавить ссылки на скиллы вместо инлайн-инструкций (прогрессивное раскрытие)

### CE3. Скиллы — прогрессивное раскрытие
- [ ] **CE3.1.** Разбить длинные скиллы на мелкие файлы
- [ ] **CE3.2.** Убрать примеры использования — оставить только дизайн интерфейсов (параметры тулов)
- [ ] **CE3.3.** Перевести жёсткие правила в рекомендации (model judgement)

### CE4. Системные промпты / AGENTS.md / IRON_RULES.md
- [ ] **CE4.1.** Удалить повторы: инструкции в системном промпте + в тулах + в CLAUDE.md
- [ ] **CE4.2.** Убрать "не делай X" — заменить на "пиши как окружающий код"
- [ ] **CE4.3.** Убрать примеры — оставить только описание параметров тулов

### CE5. Референсы вместо спеков
- [ ] **CE5.1.** Где есть markdown-спеки — добавить HTML-артефакты / тестовые наборы / рубрики для верификаторов
- [ ] **CE5.2.** Использовать код как референс (тесты, существующие реализации)

### CE6. Auto-memory
- [ ] **CE6.1.** Убрать ручные #hotkey инструкции — модель теперь сама сохраняет память

---

Шеф, напиши Роботяге:
- *"Продолжаем! Давай деплоить мультиагентную систему Angela"*
- *"Погнали тестировать A/B промпты"*
- *"Запусти SQLite логирование"*
- *"Настрой HH.ru бота и запусти автопоиск"*
- *"Покажи статистику HH.ru агента"*
- *"Запусти пилот x.ai Voice Agent"*
- *"Сравни baresip vs x.ai на 10 звонках"*

Отдыхай, система сохранена! 🛠️
