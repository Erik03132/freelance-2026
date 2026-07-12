## 🏁 2026-07-07 — CRM доработки (Levitan)

**Статус:** Сессия завершена. Исправлена логика «Сегодня» и счётчик звонков.

**Сделано в сессии:**
1. Исправлена логика страницы "📞 Сегодня": показывает напоминания с дедлайном сегодня/просроченные
2. Кнопка «На сегодня» создаёт напоминание на сегодняшнюю дату
3. Исправлен счётчик «Звонков сегодня» — считает по timestamp, а не по created_at
4. Обновлён шаблон today.html
5. Завершена сессия по протоколу finish-day

**Проблемы:** VPS недоступны, Whisper STT плохой, claude-mem 403 на projectId

**План на завтра:**
- Дождаться 25 июля для теста автопоявления напоминаний
- Восстановить VPS или сменить хостинг

---

## 🌙 2026-07-08 (ночь) — Global Session: Levitan + Agents Upgrade

**Статус:** Сессия завершена.

### Сделано

**1. Levitan — Ralph Phase-1 (Production Readiness) — ВСЁ ГОТОВО**
- US-001: ruff linting (445→0 ошибок)
- US-002: `normalize_phone()` в utils.py
- US-003: `crm_enricher.py` (provider pattern + MockCrmProvider)
- US-004: CRM enrichment в dialer_bot.py
- US-005: duration_sec + operator в save_to_crm
- US-006: ConfigDict замена (0 pydantic warnings)
- US-007: campaign_runner.py (100-call baseline)
- Тесты: 25 → 41, все проходят

**2. Поиск глобальных агентов (Antigravity)**
- Найдены в `freelance-agent/.agent/agents/`: Артемий, Ботмэн, Игорёк, Кулибин, Маркетолог, Рембрандт, Шекспир, Шерлок
- Skills: `~/.agents/skills/sherlock-deduction/`, `sherlock-bidding/`, `brigadier-router/`
- Фелини — только в gemini brain, отдельного профиля нет

**3. Rembrandt (ai-eggs) — апгрейд до Universal Designer Agent**
- Modules: brand_system, image_generator, design_generator, component_generator
- CLI: `python3 agent/rembrandt.py --design/--component/--prompt`
- Agent profile `rembrandt-designer.md` обновлён
- IncuBird brand JSON добавлен
- 7 коммитов в angel-sales repo

**4. HH.ru** — Ralph setup создан, НО deprioritized (пользователь выбрал Levitan как приоритет)

### Архитектурные решения
- OpenCode (не Claude Code CLI) — пользователь через OpenRouter в IDE
- Ralph default tool → `opencode`
- Levitan приоритетнее HH.ru

### Проблемы
- claude-mem binary недоступен (создан SESSION_SUMMARY markdown вместо)
- ai-levitan repo accidentally staged docs/superpowers from root — исправлено

### План на завтра
- Запустить реальный 100-call обзвон через campaign_runner (Levitan)
- Проанализировать метрики
- Прокачать других агентов (Артемий, Кулибин, Шерлок) по аналогии с Рембрандтом
- Рассмотреть Refero MCP интеграцию для Рембрандта

---

## 🌞 2026-07-09 — Agent Ecosystem: Full upgrade (Memory + Model Routing + Tests)

**Статус:** Сессия завершена.

### Сделано

**1. Починка TG бота @Angella26bot** — заблокированный токен заменён в 6 файлах, бот работает.

**2. Agent Ecosystem — финальный апгрейд всех 4 агентов**
- `rembrandt/component_generator.py` + `design_generator.py`: `requests.post` → `call_llm` (model routing, graceful fallback, cleaned unused `_find_env`/`import os`/`import requests`)
- `sherl/llm_client.py`: добавлен `ROUTE` dict (simple→deepseek, complex→sonnet) + fenced block stripping + `_compress`
- `memory/enrich_context()`: обёртка `recall + merge` в `memory/__init__.py`
- Все 4 CLI (`artemiy`, `kulibin`, `sherl`, `rembrandt`): `import memory` с graceful fallback + `enrich_context()` во все LLM-ветки
- Исправлен `DESIGN_SYSTEM_PROMPT` (экранированы JSON-фигурные скобки для `.format()`)
- Docstrings в копиях `llm_client.py` исправлены (кулибин/рембрандт)

**3. Тесты для всех агентов (40 total, 100% pass)**
- `artemiy/tests/test_component_gen.py` — 8 тестов (типы, фреймворки, fallback без ключа, invalid type)
- `kulibin/tests/test_basic.py` — 11 тестов (языки, анализатор, scout/evaluate без ключа, security)
- `sherl/tests/test_sherl.py` — 10 тестов (провайдеры, geo scan, research без ключа, форматирование)
- `rembrandt/tests/` — 11 тестов (были до, все проходят)

**4. Профили агентов + Handoff**
- `artemiy-frontend.md`, `kulibin-engineer.md`, `sherl-research.md`, `rembrandt-designer.md`: добавлены секции Memory Tree + Model Routing
- `docs/handoff_session_final.json` — финальная передача (контекст, файлы, next steps)
- `docs/adr/ADR-001..004` — архитектурные решения (LLM-CLI, Self-Learning, Security, Memory)

### План на завтра
- Levitan: запустить 100-call обзвон
- Angela: eval для Generator (LLM-as-judge, HD5)
- LLM Wiki: перестроить KB Angela по паттерну Карпатого (HD1)
- Agent Ecosystem: протестировать model routing с реальным ключом, кросс-агентный recall

---

## 🌞 2026-07-09 (2-я сессия) — Levitan Realtime Migration + Global Commands

**Статус:** Сессия завершена.

### Сделано

**Levitan — Real-time миграция (планирование + DRAFT)**
- Habr-кейс 1057176: Яндекс Realtime побеждает для РФ (330мс, родной русский, без VPN, рубли).
- ADR-001 (`docs/adr/ADR-001-yandex-realtime.md`): архитектура прокси (baresip→FastAPI WS→Яндекс Realtime WS), 5 этапов миграции, риски.
- `deploy/levitan_turnbased.py`: класс `RealtimeDialog` (DRAFT, GA-форма сессии, `gpt-realtime-2.1-mini`).
- `docs/active_tasks.md` — обновлено с блокомером Яндекс Cloud ключа.
- `docs/adr/ADR-001-yandex-realtime.md` + `checkpoints/chp_20260709_1006.md`.

**Global AGENTS.md — новые команды**
- `/goal` — декларативный цикл до измеримого результата (метрика+target→baseline→итерировать TDD→стоп/эскалация→`memory_add kind=decision`).
- `/code-review` — выделенный Two-axis Review: `git status/diff`→полное чтение файлов+вызовы→Standards+Spec→список рисков→не коммитить без подтверждения→`memory_add kind=bugfix` при блокере.

### Блокеры
- **Яндекс Cloud аккаунт/ключ** — сервисный аккаунт с 4 ролями (`ai.speechkit-stt.user`, `ai.speechkit-tts.user`, `ai.languageModels.user`, `ai.models.user`) + `YC_API_KEY`/`YC_FOLDER_ID`. Нет аккаунта — задача на след. сессию.

### План на завтра
1. Создать Яндекс Cloud аккаунт + сервисный аккаунт с 4 ролями → выдать ключ → в `.env`.
2. `deploy/levitan_realtime.py` (FastAPI WS-прокси, TDD) + `tests/test_realtime_proxy.py`.
3. `greeting_bridge` baresip: PCM FIFO + `auresamp` 8k↔24k + `echoCancellation`.
4. `SYSTEM_PROMPT` под голос (убрать JSON, роль/факты/цены/запреты, tool `save_lead`).
5. Function calling `save_lead` → CRM API.
6. Тест: latency <500мс, barge-in, эхо, лид в CRM. Трёхзвенка — fallback.

---

## 🌞 2026-07-09 (3-я сессия) — Habr Digests + Evals + GPT-Live vs Realtime

**Статус:** Сессия завершена.

### Сделано

**1. Обработка дайджестов**
- 🔑 **TG токен @Angella26bot**: найден заблокированный (401), заменён на рабочий в 6 файлах (`~/.env`, `watchdog.py`, `send_report_today.py`, `projects/ai-eggs/.env`, `projects/agent-lab/.env`, `projects/angel-backend/.env`). Бот ожил.
- 📡 **ABR INTELLIGENCE 02.07**: SkillSpector (NVIDIA, 12K stars) — `uv tool install skillspector`. Просканированы 14 скиллов — 0 находок. Добавлен в архитектурные заметки ACTIVE_TASKS.md.
- 📖 **HABR DIGEST 01.07**: LLM Wiki (Карпатый) — перестроить KB Angela по паттерну raw/wiki/index/ingest/query/lint. Добавлен в план (HD1).
- 📖 **Статья "Claude-агент без LangChain"** — сравнить с архитектурой Angela (ABR4).

**2. Статья "RAG на кончиках пальцев" (22.06 → `angela_agents.py`)**
- `faq_synonyms.json` — 27 negative synonyms (бройлеры ↔ утки, корм ↔ аптечка, москва ↔ краснодар и др.)
- `faq_aliases.json` — 40 записей морфологических алиасов (утка/уток/уточки, справка/справки и др.)
- `lookup_faq()` переписан: fingerprint + aliases + negative synonyms с penalty 2x при score ≥ 0.83
- Починены Router keywords: `опрос`→pro, `пород`→breeds, `налич`→availability, `функционал`→dev, `сколько сто`→pricing
- Шумовые слова: `расскажи`, `привезите` добавлены в noise filter

**3. Статья "Evals" (23.06 → глобальный CI-слой)**
- `tests/eval_angela.py` — 47 тестов: Router regression (9) + capability (11) + FAQ точность (7) + aliases (12) + negative (3) + nomatch (4). 100% pass.
- Pre-commit hook — авто-прогон при изменении `angela_agents.py` или `faq_*`
- `scripts/install-eval-hook.sh` — универсальный установщик для любого проекта
- `AGENTS.md` (глобальный): пункт 9 — Eval-driven development (каждый проект → eval suite, прогон перед изменениями)
- AGENTS.md ai-eggs: добавлена строка про eval suite в блок LLM каскада

**4. Сравнение GPT-Live vs Яндекс Realtime для Levitan**
- GPT-Live (gpt-realtime-2.1): $4/мин audio → ~$240/час. Из РФ — через VPN. Качество диалога выше.
- Яндекс Realtime: бесплатные кредиты, РФ без прокси, <500ms, родной русский.
- **Вердикт:** Яндекс Realtime — единственный реалистичный вариант для Levitan сейчас. GPT-Live рассматривать только после починки VPS и стабильной инфраструктуры.

### Архитектурные решения
- Eval-driven development — для всех проектов, текущих и будущих
- FAQ matching: fingerprint + aliases + negative synonyms (статья IgMamont)
- Eval suite как CI-слой AI-систем (статья artarasov)

### Блокеры
- VPS 185.39.206.145 — не отвечает (100% packet loss)
- SIP audio на Mac — тишина (Mango employee 22 timeout ~0 сек)
- Яндекс Cloud ключ — нет аккаунта для Realtime

### План на завтра
1. Создать Яндекс Cloud аккаунт + сервисный аккаунт с ролями STT/TTS/LLM → ключ в `.env`
2. `deploy/levitan_realtime.py` (FastAPI WS-прокси, TDD)
3. Angela: eval для Generator (LLM-as-judge, HD5)
4. LLM Wiki: перестроить KB Angela по паттерну Карпатого (HD1)
