## 🧬 2026-07-14 — soul.md: самоуправляемая конституция агентов (Chen pattern)

**Статус:** Сессия завершена.

### Источник
Видео Шен Шон Чена (@vibecoding_tg/3475) о self-improving агентах. 5 механик: soul.md · smart RAG · self-terminating loop · self-healing prompt · memory compaction. Выбрана к внедрению **soul.md**.

### Сделано
**Новый модуль `soul/` (freelance-agent/.agent/agents/soul/)** — pure stdlib, graceful fallback:
- `store.py`: read/write/scaffold/replace_auto_zone. Формат soul.md = 2 зоны: `## Constitution` (human-owned) + `## Evolving Lessons` с маркерами `<!-- SOUL:AUTO:BEGIN/END -->` (machine-owned).
- `__init__.py`: `load_soul` · `soul_context(max_chars)` · `ensure_soul` (идемпотентно) · `evolve_soul(lessons)` (self-edit только AUTO-зоны).
- `tests/test_soul.py` — **10 тестов, 100% pass** (TDD): scaffold, идемпотентность, evolve замыкается только на AUTO-зону, замена прошлых lessons, no-op на пустое, max_chars.

**4 soul.md с распиленными конституциями:** artemiy · kulibin · sherl · rembrandt (Role + Hard rules из профилей).

**Проводка в CLI (4 агента):** wrapper над `build_learned_context` инжектит `soul_context` во ВСЕ call-sites без правки каждого; `ensure_soul` на старте; при `--feedback` accepted/edited/rejected → `evolve_soul` сворачивает свежие learned-lessons в soul.md (замкнут self-improving цикл: signals → learning → soul).

### Проверка
- soul: 10/10 · sherl: 10/10 · все 4 CLI smoke OK (`--list-*`).
- ⚠️ artemiy/kulibin/rembrandt tests виснут на pre-existing тесте `*_empty_api_key` (реальный сетевой вызов без таймаута) — НЕ связано с soul.

### Архитектурные решения
- soul.md = единый живой файл governance: статичная конституция (человек) + эволюционирующие уроки (машина). Заменяет разрозненность profile.md / memory.jsonl / learning.
- evolve_soul трогает только AUTO-зону — конституция человека неприкосновенна.

### Продолжение (та же сессия) — механики Чена #4, #5 + фикс тестов

**1. Фикс pre-existing сетевого хэнга в тестах**
- Корень: `key = api_key or load_openrouter_key()` — пустая строка `""` (тестовый «нет ключа») falsy → подхватывался реальный ключ из `.env` → реальный сетевой вызов 60с.
- Фикс во всех 4 llm_client.py: `key = api_key if api_key is not None else load_openrouter_key()` — `None` = взять из env, `""` = явно без ключа. Тесты стали герметичны.

**2. Механика #4 — self-healing prompt (`healing/`)**
- `run_with_healing(prompt, generate, validate, max_retries)` — detect error → patch prompt корректирующими директивами → re-run → self-terminate на чистой валидации ИЛИ по исчерпании бюджета (совмещает #4 + #3 self-terminating loop).
- `heal_prompt(prompt, issues)` + dataclass `HealResult(output, ok, attempts, issues)`. Валидатор-исключения контейнеризованы (не роняют цикл).
- Проводка в artemiy: `_validate_frontend` (пусто/лики/наличие markup) оборачивает генерацию компонента, max_retries=1.
- `tests/test_healing.py` — **7 тестов, 100% pass**.

**3. Механика #5 — memory compaction (`memory.compact`)**
- Дедуп идентичных фактов (norm-текст, хранит новейший ts) + обрезка до `keep` новейших; атомарная перезапись jsonl. Возвращает `{before, after, removed}`.
- Авто-триггер в feedback-хендлере всех 4 CLI (момент самооптимизации) с выводом `🗜️ Memory compacted`.
- `memory/tests/test_compact.py` — **5 тестов, 100% pass**.

### Итог по тестам
Полный прогон: **62 passed за 33s, без хэнга** (было 50). soul 10 + healing 7 + memory compact 5 + прежние 40.

**4. Механика #2 — smart RAG top-K (`memory.recall_scored`)**
- Найден баг: `enrich_context` вызывал `recall()` (возвращает строку), но итерировал как список dict'ов → память **никогда** не инжектилась.
- `recall_scored(agent, query, top_k, min_score)` — ранжированные dict'ы {fact, score, ...} по Jaccard-overlap, порог + top-K. `recall()` переписан поверх (backward-compat строка).
- `enrich_context` починен: реально инжектит top-K релевантных фактов.
- `memory/tests/test_smart_rag.py` — **8 тестов, 100% pass** (ранжирование, top-K, min_score, реальная инъекция в enrich_context).

### Самоулучшающийся цикл (замкнут)
generate → **validate/heal** (#4) → **smart-RAG recall** (#2) → signals → learning → **soul.md evolve** (#1) → **memory compact** (#5). Из 5 механик Чена внедрены **все**: #1, #2, #3 (внутри #4), #4, #5.

### Итог по тестам (финал)
Полный прогон: **70 passed за 27s, без хэнга** (было 50). +soul 10 +healing 7 +compact 5 +smart_rag 8.

---

## 🌞 2026-07-12 — VPS диагностика + обновление credentials

**Статус:** Сессия в процессе.

**Сделано:**
1. Диагностика VPS: 72.56.38.19 — пинг есть, SSH не пускает (host key changed, пароль не подходит). 185.39.206.145 — мёртв
2. Выяснена причина молчания @Angella26bot — VPS переустановлен, все PM2 процессы удалены
3. Найдены Timeweb credentials в .env (ai-eggs)
4. Обновлены Timeweb логин/пароль во всех проектах: ai-eggs, ai-levitan, levitan, angel-backend, agent-lab
5. Новые данные: лог `Vezemcip@yandex.com`, пасс `Azamat123`

**Блокеры:** ❌ VPS недоступен (ждём сброс пароля от Timeweb панели)

**План:**
- Зайти в my.timeweb.ru → сбросить root-пароль
- SSH → восстановить сервисы (Angela, боты, VezemCip)

---

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

---

## 🔧 2026-07-12 — P1 cleanup + GeekNeural token-dedup

**Статус:** Сессия завершена.

### Сделано

**1. P1 — приведение кода в порядок (4 сабмодуля + root)**
- `ai-grant-portal-temp` (`685aad3`): AGENTS.md, config, лендинг.
- `ai-scout` (`133ab1e`): скилл `extruct-api` → `project-skills/`, +content-pipeline, video_clipper.
- `ai-eggs` (`76f828a`): удалены 4 генератора + тесты; +eval suite (**47/47 passed**).
- `angel-backend` (`72d35f8`): agentic RAG, mem0, autodial, call-quality monitor; `.gitignore` пополнен артефактами.
- root (`4aa79c7e`,`a3415565`,`5387c294`): bump указателей, chp.md 07-09, extract/enrich adygea leads, gitignore PII.
- Безопасность: секреты не попали (`.env` игнорируются; `adygea_leads/` PII → gitignore). Дубликат-чекпоинт удалён.

**2. GeekNeural — движок дедупликации контекста (4 уровня)**
- Одно и то же содержимое в сессии передаётся модели **один раз**; повтор → короткая ссылка `gn:<hash>`.
- Единое ядро `tools/geekneural/core/dedup.py` (чистый stdlib, без зависимостей).
- Уровни:
  - 1. shell-hook `shell/hook.sh` (`gn read|cat|stats|clear`, bash+zsh) — **работает**;
  - 2. MCP-сервер `mcp_server/server.py` (stdio JSON-RPC, чистый stdlib) — **зарегистрирован в `opencode.jsonc`**;
  - 3. браузерное расширение MV3 `browser/extension/` (дедуп вставок в ChatGPT/Claude/Gemini);
  - 4. IDE-плагин VS Code `ide/vscode/` (команда «копировать файл в чат (дедуп)»).
- volatile/real-time (`*.log`, `/tmp/`, runtime-JSON) сознательно **не дедуплицируются**.
- Тесты: unit (6) + MCP-интеграция — оба green.
- Коммит: `5b4d3273`. ADR-001 + README.

### Демо (реальные цифры)
- 5 чтений 11 КБ-файла → **79.9%** экономии (~11 059 токенов).
- Сценарий агента (3 файла проекта + 2 перечитывания): 257 630 байт → 132 024, **48.8%** (~31 401 токенов).
- На стабильном контексте — до **~92%**.

### Архитектурные решения
- MCP на чистом stdlib JSON-RPC (без `mcp` SDK) — переносимо, без сети/установки.
- Кеш сессии в `~/.geekneural/cache.db` (локально, **без телеметрии**).
- Дедуп через content-addressed sha256; статистика персистентна в БД между процессами.

### Блокеры (ждут пользователя)
- VPS `185.39.206.145` лежит (100% packet loss) → боты оффлайн.
- Ключ SSH отвергнут на `72.56.38.19` → добавить `id_ed25519.pub` в `authorized_keys`.

### План на завтра
1. **Перезапустить OpenCode** → подхватит MCP `geekneural` (`cached_read`).
2. Восстановить VPS / сменить хостинг; добавить SSH-ключ на `72.56.38.19`.
3. Задеплоить накопленные изменения сабмодулей на живой VPS.
4. (опц.) Загрузить браузерное расширение и VS Code-плагин.
