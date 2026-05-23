# 📋 MASTER BACKLOG — Antigravity Ecosystem
> **SSoT**: единственный источник правды по задачам эволюции агентов и технических улучшений.
> **Обновляется**: вручную при старте/финише задачи + автоматически через morning_dream.
> **Создан**: 23.05.2026 | Заменяет: AGENT_EVOLUTION_ROADMAP.md, AGENT_SKILL_ROADMAP.md, UNIFIED_ROADMAP.md

---

## 🔴 СРОЧНО — Сделать в ближайшие 1-2 дня

| # | Задача | Файл/контекст | Оценка |
|---|--------|--------------|--------|
| S1 | **Eval dataset для Анжелы-продавца** — 138 вопросов из транскриптов → проверить точность ответов | `eval_plan.md` на VPS | 2ч |
| S2 | **Eval RAG Recall@5** — создать 50 вопросов из PDF вручную, проверить поиск | `rag_improvements.py --quality` | 3ч |
| S3 | **Исходящий звонок через Mango** — Фаза 14.3 (baresip настроен, голос выбран) | `AGENT_EVOLUTION_ROADMAP.md` §14.3 | 1 день |
| **S4** | ~~⚠️ ДЕДЛАЙН 18 июня: Gemini CLI → Antigravity CLI~~ | ✅ **ВЫПОЛНЕНО 23.05** — обновлено `0.34 → 0.43`. Новое: `gemini skills`, `gemini hooks`, `--resume latest` | — |

---

## 🟠 ВАЖНО — Этот спринт (неделя)

| # | Задача | Описание | Оценка |
|---|--------|----------|--------|
| W1 | **Fine-tune локальной LLM** | Датасет из CRM + FAQ → LoRA → Ollama. Этап 7 эволюции. | 1 нед |
| W2 | **Авито-мультикабинет** | `avitolog.py` для 2+ кабинетов (Опт + Розница) + автоответы | 3 дня |
| W3 | **agentClient.js** — единая шина вызова агентов | Этап 1.1-1.4 эволюции | 2 дня |
| W4 | **book-to-skill** — PDF/EPUB → SKILL.md конвертер | Этап 13. Автоматическая прокачка из книг | 2 дня |
| W5 | **Анжела в MAX мессенджере** — Bot API `botapi.max.ru`, ~90 млн аудитория РФ, нет блокировок с VPS | `botman-creator` скилл §MAX | 1 день |
| W6 | **Автозакрытие активностей в Битриксе** — Анжела ответила клиенту → `crm.activity.update(COMPLETED=Y)` + комментарий в таймлайне сделки. Основа: `bitrix_receiver.py` | 30-50 строк кода | 2-3 часа |
| W7 | **Antigravity SDK** (Google I/O 2026) — программный доступ к agent harness. Возможно заменит `agentClient.js` (W3). Изучить API, оценить замену | Google I/O анонс | 1 день |

---

### 🐛 Kimi K2 Audit Fix Sprint (23.05.2026)
> Полный отчёт: [`reports/kimi_audit_2026-05-23.md`](reports/kimi_audit_2026-05-23.md)

| # | Баг/задача | Файл | Сложность |
|---|-----------|------|----------|
| **F1** | ~~🔴 Orphaned lock при SIGKILL~~ | ✅ **23.05** `atexit.register(_release_lock)` — `tg_bot.py:604` |
| **F2** | ~~🔴 Race condition CLOSED_STAGES~~ | ✅ **23.05** `frozenset({...})` — `bitrix_scanner.py:24` |
| **F3** | ~~🔴 ADMIN_TELEGRAM_ID без .strip()~~ | ✅ **23.05** `str(...).strip()` — `angelochka_core.py:31` |
| **F4** | ~~🟠 get_latest_scan() fallback при устаревании >2ч~~ | ✅ **УЖЕ БЫЛО** — `_is_scan_stale` + `_auto_run_scanner` в `daily_report.py:36-88` |
| **F5** | ~~🟠 Memory leak SmartFAQ~~ | ✅ **23.05** — `_dirty_count` батчинг: disk write каждые 5 track() + `atexit` flush — `angelochka_core.py:372` |
| **F6** | ~~🟠 VectorMemory race condition~~ | ✅ **23.05** — `threading.Lock()`: `add_texts()` (write) + `stats()` (read) — `vector_memory.py:83,165,261` |
| **F7** | 🟡 Вынести price-list в `config/prices.json` | `angelochka_core.py` | 1ч |
| **F8** | 🟡 Circuit-breaker OpenRouter (5 ошибок → Ollama fallback) | `angelochka_core.py` | 3ч |
| **F9** | 🟡 Унифицировать ID клиентов `tg_`/`vk_` через `uuid3` | `client_memory.py` | 2ч |


---

## 🟡 БЭКЛОГ — Следующие недели

### Инфраструктура агентов

| # | Задача | Этап | Приоритет |
|---|--------|------|-----------|
| B1 | `shared/event_log.jsonl` — файл-очередь / брокер событий | 1.2 | Высокий |
| B2 | `config/agents.yaml` — реестр всех агентов | 1.4 | Высокий |
| B3 | `tools/agctl.sh` — CLI-утилита управления агентами | 3.1 | Средний |
| B4 | Telegram-алерты при сбоях любого агента | 4.3 | Средний |
| B5 | `utils/skillLoader.js` — авторегистрация навыков | 5.1 | Средний |
| B6 | Google Calendar → задачи агентам (каждое событие = задача) | 6.2 | Низкий |

### Прокачка Анжелы

| # | Задача | Описание | Приоритет |
|---|--------|----------|-----------|
| A1 | **Re-indexing с chunk_size=800** | Сейчас 423 символа — мало для тех.руководств | Средний |
| A2 | **Multi-query expansion** | 3 варианта запроса вместо одного | Средний |
| A3 | **RAG для новых PDF** | Добавить новые руководства по птицеводству | Низкий |
| A4 | **Fallback Ollama** | Защита от блокировок Google/OpenRouter | Высокий |
| A5 | **Авито-чаты** | Анжела в Авито автоответы | Высокий |

### Прокачка скиллов агентов

| # | Скилл | Что добавить | Источник |
|---|-------|-------------|---------|
| SK1 | `rag-master` | Часть 2 от Честного знака (Advanced RAG) когда выйдет | Хабр |
| SK2 | `artemiy-frontend` | View Transitions API практика | MDN |
| SK3 | `rembrandt-designer` | Print Design (полиграфия, CMYK) | При 3+ заказах |
| SK4 | Новый скилл: `fine-tuning` | LoRA, датасеты, Unsloth, GGUF экспорт | После W1 |

### Стратегические / R&D

| # | Задача | Описание | Срок |
|---|--------|----------|------|
| R1 | **Self-Evolution** (Этап 9) | Агент сам предлагает улучшения своих скиллов | Q3 2026 |
| R2 | **DeepSec** (Этап 10) | AI-сканер уязвимостей кодовой базы | Q3 2026 |
| R3 | **GraphRAG** для Анжелы | Только если появятся межсущностные запросы | Условно |
| R4 | **Грант Старт-1** (4 млн ₽) | Документы, датасет, описание | Q2-Q3 2026 |

---

## ✅ СДЕЛАНО (архив)

| Дата | Задача |
|------|--------|
| 23.05.2026 | RAG audit: Advanced RAG (не GraphRAG) подтверждён, rerank добавлен |
| 23.05.2026 | code-review-and-quality v2.0 (thermo-nuclear rules из Cursor) |
| 23.05.2026 | rag-master v3.0 (3 источника, диагностика, GraphRAG секция) |
| 23.05.2026 | artemiy-frontend v2.0 (Chrome Modern Web Guidance) |
| 22.05.2026 | baresip watchdog через PM2 |
| 22.05.2026 | call_learner и morning_dream отключены (0 пользы, $0.05 экономия) |
| 10.05.2026 | curl.md CLI установлен и задеплоен на VPS |
| 08.05.2026 | call_learner.py + call_transcriber запущены |
| 08.05.2026 | night_audit починен + launchd на Mac |

---

## 🔔 Протокол напоминаний

**morning_dream.sh** читает этот файл каждый понедельник и выдаёт в Telegram:
```
📋 BACKLOG REVIEW:
🔴 Срочно: [S1, S2, S3]
🟠 Этот спринт: [W1, W2, W3]
💡 Напоминание: <случайный пункт из бэклога>
```

**Правило обновления (SSoT):**
- Задача появилась → сразу в MASTER_BACKLOG.md, не в отдельный файл
- Задача выполнена → перенести в секцию ✅ СДЕЛАНО
- Старые roadmap-файлы → заморозить (не удалять, там детали)

---

## 📁 Карта замороженных файлов (детали задач)

| Файл | Что внутри | Статус |
|------|-----------|--------|
| `AGENT_EVOLUTION_ROADMAP.md` | Детальная архитектура этапов 1-14 | 🧊 Заморожен, читать при необходимости |
| `AGENT_SKILL_ROADMAP.md` | Счётчик спроса по направлениям | 🧊 Заморожен |
| `ai-eggs/UNIFIED_ROADMAP.md` | Дорожная карта IncuBird 2.0 | 🧊 Заморожен |
| `ai-eggs/data/rag_knowledge/eval_plan.md` | Детали eval тестов | 🧊 VPS, актуален |
| `ACTIVE_TASKS.md` | Текущий статус боевой системы | ♻️ Обновлять по инфраструктуре |
