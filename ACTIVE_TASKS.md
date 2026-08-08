# Текущий статус проекта (обновлено 04.07.2026 - 18:00)

---

## 🛡️ 🔴 БЕЗОПАСНОСТЬ: РОТАЦИЯ СЕКРЕТОВ (NEW 02.08.2026 — ai-defender аудит)

> Живые ключи закоммичены в GitHub (`github.com/Erik03132/freelance-2026`). Считаются скомпрометированными.
> Полный отчёт: `reports/security-audit-2026-08-02.md` · данные: `reports/gitleaks-2026-08-02.json`
> Агент: `agents/ai-defender` · CLI: `ai-defender` · трекер ротации: `SECRETS_ROTATION.md`

### 🔴 КРИТИЧНО — ротация (делать первым, требует действий пользователя)
- [x] **SEC-1.** Ротация Funpay-ключ (`Funpay_MYbt...`) в `opencode.json` → новый ключ в Funpay, вынести в `.env` ✅ провайдер wellflow/funpay БОЛЬШЕ НЕ СУЩЕСТВУЕТ в opencode (ключ мёртв, ротация не нужна). Провайдер удалён из `opencode.json`, `.env` без FUNPAY. Осталось: SEC-11 — почистить утечку из git-истории
- [x] **SEC-2.** Ротация OmniRoute JWT_SECRET + API_KEY_SECRET + INITIAL_PASSWORD в `omniroute-recover.sh` → `openssl rand -hex 32`, обновить сервис на VPS :20128 ✅ 02.08: скрипт+VPS `.env` обновлены, pm2 restart, `/v1/models`=200. ⚠️ в скрипте остались секреты (SEC-4) + OMNIR_VPS_KEY `sk-c7a0aac...` тоже утёк в историю — нужна ротация API-ключа шлюза
- [x] **SEC-3.** Проверить публичность репозитория GitHub → если public, экспозиция публична ✅ 02.08: был **PUBLIC**, теперь **PRIVATE** (gh repo edit). Secret scanning недоступен (422). Секреты были публично доступны до 02.08 — ротация всех утёкших ключей обязательна (SEC-1/2, остальные в трекере)

### 🟠 ВЫСОКИЙ — правки после ротации
- [x] **SEC-4.** Вынести ключи из `opencode.json` в `.env` (gitignored), в репо — placeholder ✅ 02.08: `opencode.json` очищен (SEC-1); параметризованы `omniroute-recover.sh` (секреты из `tools/omni-auto-router/.env` gitignored, создан `.env.example`), `night_audit_vps.sh` (PROXY_URL из env/`$HOME/.env`), `watchdog.py` (BOT_TOKEN/PROXY из env + guard). ⚠️ **НОВОЕ:** в `watchdog.py` был живой TG-токен `8336409939:AAHr2wbu...` (утёк в git, репо был public) → нужна ротация @BotFather + обновить копию на VPS; прокси-креды хардкод остались в `ai-senat/agent/*.py`, `ai-eggs/agent/*.py`, `sinergy/src/**` + build-артефакты `sinergy/.next` — параметризовать + ротировать пароль прокси
- [x] **SEC-5.** levitan: исправить SQLi ×4 (`crm/app.py:185,189,324,393`) — параметризованные запросы ✅ 02.08: whitelist `_SAFE_CONDITIONS` (точные статические шаблоны) для всех динамических WHERE + whitelist `CONTACT_COLUMNS` для UPDATE SET. Бонус: пофикшен path traversal в `/api/import` (был `DATA_DIR / filename` → `Path(filename).name`). ruff + py_compile чистые, инъекции отклоняются (проверено). ⚠️ venv levitan неполный (нет faiss/pydantic_settings/jinja2) — тесты не прогнать целиком
- [x] **SEC-6.** levitan: chmod 0777 (`deploy/levitan_fifo_bridge.py:188`) + MD5 для ключей (`tts_engine.py:25`, `upload_greeting.py:52`) ✅ 02.08: FIFO `0o777`→`0o600` (мир-writable → только владелец); `hashlib.md5`→`sha256` в кэш-ключе TTS и `command_id` загрузки. `smart_dialer_zadarma_old.py:183` НЕ трогал — md5 обязателен по протоколу Zadarma. ruff (по моим файлам) чист; предсуществующие ruff-замечания в fifo_bridge:302/336 остались
- [x] **SEC-7.** levitan: убрать печать 15 символов ключей в `test_all.py:28-30` ✅ 02.08: теперь печатается только `set`/`MISSING`, без контента. Проверено: других утечек префиксов в levitan нет. ruff+py_compile чисты

### 🟡 СРЕДНИЙ — процессные
- [x] **SEC-8.** Закоммитить `.gitleaks.toml` (защита работает и после клонирования) ✅ 02.08: `.gitleaks.toml` в git (`3447d41d`), `no-secrets` подключён через pre-commit (commit-stage). Проверено: `gitleaks protect --staged` ловит секреты
- [x] **SEC-9.** Переустановка `no-secrets.sh` при клоне репо (живёт в `.git/hooks/`, не версионируется) → шаг в README ✅ 02.08: хук-скрипты перенесены в **`githooks/`** (версионируются), `.pre-commit-config.yaml` обновлён на `githooks/*.sh`, создан корневой `README.md` с шагом Setup (`pre-commit install`). После клона переустановка скриптов не нужна
- [x] **SEC-10.** Прогнать `ai-defender llm <проект> --frame mcp` по MCP-серверам freelance-agent (prompt injection) ✅ 08.08: фикс `llm_audit.py` (`count_files()`) + `cli.py` (при `--llm` files_scanned=реальный счёт, frame передаётся в deep_audit). Проверено: `--llm src/mcp-servers --frame mcp` → files_scanned=4 (было 0), отчёт пишется. ✅ 08.08: LLM-аудит выполнен на free-каскаде OpenRouter (nemotron-3-super-120b:free): 1 Medium (bitrix.ts:27 утечка PII в логах), 3 Low, 0 Critical/High → `freelance-agent/src/mcp-servers/security/llm-deep-audit.md`. Попутные фиксы: (1) каскад FREE_MODELS с fallback, (2) сырой запрос вместо shared call_llm (тот вырезал ```-блоки), (3) max_tokens 3000→6000 (ответ обрезался), (4) исключение папки security/ из скана (мусор)

### 🔵 НИЗКИЙ — когда будет время
- [ ] **SEC-11.** Остальные утечки в истории (mango_api.py, .cursor/rules, CHRONICLE.md, checkpoints) — ключи уже ротированы, проверить мертвость ✅ 08.08 ПРОВЕРЕНО: (1) mango_api.py (корень + tools/angela) — только имена env (`MANGO_API_BASE`, `vpbx_api_key`), полных значений нет; (2) .cursor/rules — файлов с ключами в истории нет; (3) CHRONICLE.md — полных ключей нет; (4) checkpoints последнего коммита — только замаскированные префиксы в SECRETS_ROTATION.md (это трекер, не утечка). Живые ключи в git-истории НЕ найдены. Закрыто

### 💰 PriceTrack — не продукт, а 3 паттерна для скрапинга (NEW 07.08.2026, оценка 6/10)
> Источник: https://habr.com/ru/articles/1067564/ (PriceTrack — мониторинг цен Ozon, перенос исполнения с VPS на машины пользователей).
> Ключевой вывод: 403-проблема не в селекторе, а в окружении (VPS-IP режет маркетплейс) → сервер = управляющий контур, исполнение = локально. Декларативный pipeline `select→text→regex→replace→parse` + двухслойный извлекатель (серверный профиль-контракт + локальный рецепт-фолбэк). Инвариант изоляции аккаунтов (данные = адрес+account_id). Бэкап-метрика = успешное восстановление, не «backup created».
> Применимо к нашим скрапинг-агентам (freelance-agent: kwork/freelance.ru; avito.ts MCP). Стек (FastAPI/Playwright/pywebview/десктоп-клиент) НЕ берём.
- [ ] **PT-1.** Паттерн «рецепт + фолбэк» в freelance-agent: дешёвый HTTP-путь → при 403 фолбэк на Playwright (быстрый путь не маскирует поломку, автоматически восстанавливается) ✅ 08.08: `mcp_servers/proposal_engine/scraper_base.py` (TwoLayerExtractor: HTTP → rotate env → Playwright fallback)
- [ ] **PT-2.** Проверить avito.ts при 403: сначала менять окружение (прокси/IP/сессию), а НЕ подбирать селекторы — «селектор может быть правильным и бесполезным, если перед нами не та страница» ✅ 08.08: `avito.ts` v1.1 — envState (proxy→session rotations), ретраи 403/429/5xx, реальные API-вызовы включены
- [ ] **PT-3.** Инвариант изоляции аккаунтов для multi-account агентов (hh-ai-agent, freelance-agent): данные = (адрес сервера + account_id), чистка кэшей при смене пользователя ✅ 08.08: `account_isolation.py` (AccountIsolator: cache_key=sha256(host:id:platform), purge при switch, verify_isolation)
- [ ] **PT-4.** Внешний бэкап: метрика = успешное пробное восстановление (test-restore по расписанию), а не «rsync done» — скорректировать finish-day/finish-day backup ✅ 08.08: `tools/backup/test_restore.sh` (PASS/FAIL по проверке архива+живых файлов), встроен в `tools/ops/finish_day.sh` (Фаза 6)

### 🤖 Agentic AI: стек агентного инженера — 3 паттерна в eval/верификацию (NEW 08.08.2026, оценка 8/10)
> Источник: https://habr.com/ru/articles/1068024/ (Антон Чирикалов, обзор стека: PydanticAI/LangGraph/CrewAI, MCP, A2A, оценка агентов, RAG, OTel).
> Ядро ценности — раздел «Оценка агентов»: 3 уровня метрик (итог/траектория/токены), смещения LLM-судьи с пруфами (verbosity bias Zheng MT-Bench 2023; позиция Wang 2023; любовь к себе Panickssery 2024 — судья ≠ та же модель; мягкость Sharma Anthropic 2023), «узкие критерии + обоснование ДО оценки + калибровка на ~100 кейсах», зацикливание (повтор пары tool+args) ловится кодом бесплатно, конвейер с порогом в CI (faithfulness < 0.85 → красная сборка), провалы из прода → в датасет. DeepEval = pytest-метрики (AnswerRelevancy/Faithfulness/GEval/ToolCorrectness/TaskCompletion).
> Фреймворки не берём (свой стек: freelance-agent, AP-1, OmniRoute). MCP: новость — stateless (сессии/initialize убрали), sampling устарел, Multi Round-Trip Requests (elicitation на нём).
- [ ] **AG-1.** Улучшить «Проверялу» (verify_checker.py) и кросс-чек (cross_check.py) по смещениям судьи: (a) критерии узкие/бинарные вместо шкалы, (b) обоснование ДО вердикта (уже JSON: добавить поле rationale до verdict), (c) судья ≠ проверяемая модель (уже nemotron — закрепить), (d) verbosity-контроль (намеренно раздутый ответ в тесте) ✅ 08.08: оба промпта переписаны (rationale ПЕРВЫМ полем + анти-смещения: длина не важна, не поддакивать, бинарные критерии). Тесты: раздутый пустой ответ → not_verified; ответ с реальными выводами (grep/stat/jq) → verified. Проверено на nemotron-3-super-120b:free
- [ ] **AG-2.** Траекторный слой в eval suite: фиксировать вызовы инструментов субагента (tool name + args), детект зацикливания (повтор пары подряд → fail, бесплатно, без LLM), витки vs эталон, precision/recall по инструментам ✅ 08.08: `tools/trajectory_eval.py` (TrajectoryEvaluator: loop-detect, steps vs expected, precision/recall, order exact/in-order/any-order, args-синтаксис; CLI + JSON) + `tests/eval_trajectory.py` (7 кейсов из статьи: A-идеал, B-лишний виток, C-нужный не вызван, D-зацикливание, in-order/exact, args) — EVAL PASSED
- [ ] **AG-3.** Порог в гейте: eval suite провалился (faithfulness < порог ИЛИ траекторный fail ИЛИ перерасход токенов) → блокировка мержа/коммита (в workflow /goal, см. SA-2) ✅ 08.08: `tools/eval_gate.sh` (--list/--quick/--project; прогон всех eval_*.py, PASSED-детект, провал → exit 1). Проверен: 8/8 quick-прогон → нашёл РЕАЛЬНУЮ регрессию: eval_sinergy 9/12 FAIL (Builder: нет title/MVP/logic chain; Skeptic/Optimist: TimeoutExpired 30s). Заведена задача SY-1 на починку. Команда для /goal шаг 4: `bash tools/eval_gate.sh --quick`
- [ ] **SY-1.** Починить eval_sinergy (найдено eval_gate 08.08): Builder agent тесты падают (Should have title/MVP/logic chain), Skeptic/Optimist — TimeoutExpired 30s (npx tsx + LLM-вызовы) ✅ 08.08: 3 бага — (1) `builderBuild` async, тесты звали без `await` → TypeError на Promise; (2) `console.assert` в Node не бросает (молчаливый пропуск) → заменены на throw; (3) OPENROUTER_API_KEY в env → skeptic/optimist уходили в LLM-каскад (6 моделей × 20s) → ts_eval чистит AI-ключи из env (детерминированный fallback). Итог: 12/12 (100%), eval_gate 8/8 PASSED

### 🧾 Генерация форм через AI (Cloud X) — оценка 5/10, паттерн уже в стеке (NEW 08.08.2026)
> Источник: https://habr.com/ru/companies/cloud_x/articles/1067868/ (вендорский туториал-маркетинг, 5.3K читателей).
> Суть: генерировать JSON Schema формы через публичную LLM (DeepSeek) → UI по схеме через их `@cloudx/react-ui-kit-forms-builder`. Безопасность = «LLM отдаём только публичные данные (HTML/JS/CSS/JSON-структуры)».
> Оценка 5/10: полезен 1 паттерн (схема вместо данных), который у нас УЖЕ есть (Фемида деперсонализирует перед облаком, validation-layer держит JSON Schema). Цифра «до 77% утечек 2025 связаны с GenAI» — кандидат в SEC-доки. Неточность автора: OpenAI/Anthropic/DeepSeek API по умолчанию НЕ fine-tune на пользовательских данных. «Локальные LLM медленные» — спорно (у нас ollama работает). Задач не заводим, только заметка.

### 💸 Токен-оптимизация промптов (Reksoft) — 2 приёма, остальное уже есть (NEW 07.08.2026, оценка 6/10)
> Источник: https://habr.com/ru/companies/reksoft/articles/1067166/ (QA-инженер Reksoft, бюджет $ на токены).
> Методология (7 правил: конкретика, без «воды», лимит объёма, роль в system, новый чат под задачу, функции вместо файлов, недельный бюджет) — уже есть у нас (AP-1, RTK/Caveman, smart-unfold, action-first cap-5). Ценны 2 конкретных среза:
> 1) Русский язык дороже английского в ~1.5-2 раза по токенам (входные инструкции можно переводить на EN, это НЕ трогает правило «отвечать по-русски» на выходе);
> 2) Бюджетирование «цена запроса до отправки» + резерв под жёсткий лимит (у нас есть max-spend, но нет пре-скринера токенов).
> Не берём: RU→EN в выводах (конфликт с языковой нормой).
- [ ] **ПЛ-1.** Пре-скринер токенов перед тяжёлым запросом (tiktoken, RU-коэффициент ~1.5x): скрипт/чек в tools/ для оценки «цена до запроса» + резерв под лимит недели ✅ 08.08: `tools/token_prescreener.py` (tiktoken/RU×1.5/бюджет/--json/--models), работает
- [ ] **ПЛ-2.** Перевод внутренних системных инструкций на EN там, где язык не значим (не выходы, не Фемида/юридика): промпты голосовых агентов/чатов — замерить экономию токенов до/после ✅ 08.08: 8 промптов переведены на EN (call_analyzer×2, call_transcriber, roles_config×3, ROLE_CREATOR/BOSS, marketer/shakespeare) — ~2137→~1496 токенов (-30%)

### 🤖 9 ошибок чат-ботов (OTUS) — 6 практических паттерна для наших бот-агентов (botman, hr-agent, Angela) (NEW 07.08.2026, оценка 7/10)
> Источник: https://habr.com/ru/companies/otus/articles/1065742/ (бизнес-архитектор Андрей Коптелов, OTUS).
> Методология (9 ошибок: цели/метрики, эскалация на человека, контекст/база знаний, связь с данными, аналитика/развитие, стоимость владения, «всё сразу», безопасность) — частично есть у нас (метрики `/goal`, SA-2, MCP-интеграции, self_improve_log, каскад моделей, ai-defender). Ценны 6 практических паттерна:
> 1) **Обязательный выход на umano:** бот должен оценивать уверенность LLM (INFO ≠ PASS, низкая вероятность) и **автоматически** инициировать handoff на человека с полной историей контакта.
> 2) **База знаний = актуальные источники:** бот отвечает только на основе проверенных и актуальных документов; для критически важных ответов — утверждённые шаблоны.
> 3) **Бот как помощник, не замена:** формализовать экономию времени оператора (сколько рутинных запросов взял на себя бот).
> Не берём: ошибку 7 («всё и сразу») — мы дробим на единицы работы через AP-1 (субагент = изолированный контекст).
> - [ ] **БОТ-1.** Добавить в бот-агентах (botman, hr-agent, angel-backend и т.п.) проверку уверенности LLM: если `confidence < threshold` **или** ответ совпадает с шаблоном неопределённости («Я не уверен», «Нужно уточнить») → автоматически инициировать handoff на человека (Telegram/VK: передать весь чат + контекст оператору, пометить `needs_human_review=true`). ✅ 08.08: `bot_quality.py` (check_llm_confidence/should_escalate_to_human), интегрировано в bitrix_bot.py + tg_bot.py
> - [ ] **БОТ-2.** Вместо дефолтного fallback-ответа формировать **вопрос-уточнение** («Вы имели в виду X или Y?»), чтобы уменьшить галлюцинации и вести к диалогу. ✅ 08.08: `build_clarifying_question()` в bot_quality.py, заменяет «мини-сбой» в bitrix_bot/tg_bot
> - [ ] **БОТ-3.** Выделить ответственного за **актуализацию источников знаний бота** (еженедельный обзор: исходные PDF/тарифы/прайс-листы → выжимка в Markdown → загрузка в claude-mem как corpus → инвалидация старых observation через лимит даты). ✅ 08.08: `KnowledgeSourceTracker` (TTL, check_freshness, mark_updated) в bot_quality.py
> - [ ] **БОТ-4.** Для критически важных доменов (цены/тарифы в hr-agent, условия возврата в botman) создать **утверждённый шаблон ответов** (в памяти как observation kind=template, переиспользуемый через `@validated` или прямой шаблон). ✅ 08.08: `ApprovedAnswerTemplates` (таблицы в SQLite + дефолтные шаблоны prices/delivery/contacts)
> - [ ] **БОТ-5.** Метрика **«экономия времени оператора»**: сколько рутинных/FAQ-запросов бот снял с живого специалиста — добавить вhero-метриках Angela/бот-агентов рядом с конверсией. ✅ 08.08: `BotQualityMetrics` (bot_sessions + operator_time_savings, record_daily_savings/get_savings_summary)
> - [ ] **БОТ-6.** Шаблон приветствия бота: «Я помогаю с рутинными вопросами, сложные случаи — передаю живому специалисту» — задаёт правильные ожидания у пользователя. ✅ 08.08: `BOT_GREETING_TEMPLATE` в bot_quality.py + применён в tg_bot.py `/start`

### ⚙️ Compound Engineering plugin (EveryInc) — 32 скилла цикла brainstorm→plan→work→simplify→review→compound (NEW 07.08.2026, оценка 7.5/10 — воздержаться от полной установки, забрать паттерны)
> Источник: https://github.com/EveryInc/compound-engineering-plugin (официальный плагин для Claude Code/Cursor/Codex и др., 24.1k★).
> Философия: каждая единица работы облегчает следующую → знания в `vault/03-Lessons/` читаются следующей итерацией. Поддерживает OpenCode (.opencode/). 
> Ядро: 6 шагов — `/ce-brainstorm` (requirements-only), `/ce-plan` (implementation-ready), `/ce-work` (native/cross-model), `/ce-simplify-code` (чсет оставить для переиспользования), `/ce-code-review` (multi-agent против плана), `/ce-compound` (обучение → `vault/03-Lessons/`). Доп. скиллы: `/ce-ideate` (до цикла), `/ce-strategy` (STRATEGY.md), `/ce-product-pulse` (внешний цикл), `/ce-debug` (баг вместо фичи), `/ce-pov` (при commitment), `/ce-explain` (визуал документ), `/lfg` (автопилот до зелёного PR).
> У нас уже есть элементы: brainstorming навык, writing-plans, executing-plans, two-axis review (по Matt Pocock), verification-before-completion, self_improve_log (аналог compounding). Установка полного плагина приведёт к конфликту триггеров и избыточному контексту (32 скилла дублируют наши).
> Не ставить полностью, но забрать паттерны точечно:
- [ ] **ЦЕ-1.** Паттерн ce-compound: при завершении крупной задачи поместить lesson-файл в репо (`vault/03-Lessons/`) + дублировать в claude-mem (наш self_improve_log → репо-зеркало); сравнить с нашими writing-plans и two-axis review, забрать лучшие поля (readiness-гейты) ✅ 06.08: изучено ce-plan/ce-code-review/lfg → U-ID в writing-plans, lfg НЕ берём; отчёт ce_cv_review.md
- [ ] **ЦЕ-2.** Оценить lfg (автопилот до зелёного PR) как апгрейд /goal — только если подтвердит ценность на 1-2 задачах (свежий контекст AP-1 за субагент = изолированный環境).
- [ ] **ЦЕ-3.** ce-product-pulse для sinergy/dashboard: еженедельный отчёт «что реально используют пользователи» (usage/errors) → вход в итерации ✅ 08.08: см. CE-4 (product-pulse.mjs создан)

### 🧠 OpenHuman — извлечь 3 паттерна (NEW 02.08.2026, оценка 6/10 — не внедрять)
> Оценка: дублирует наш стек (claude-mem ≈ Memory Tree, geekneural ≈ TokenJuice, OmniRoute ≈ routing, igorek ≈ tinyagents).
> Внедрять только дешёвые паттерны, без нового стека.
- [ ] **OH-1.** SuperContext-прегрев: подтягивать `memory_context` перед задачей в агентах (механизм есть, включить системно) ✅ 06.08: добавлено в AGENTS.md (секция claude-mem: memory_context прегрев перед НОВОЙ задачей, 1 вызов)
- [ ] **OH-2.** Obsidian-зеркало claude-mem: экспорт session-summary/решений в markdown-волт ✅ 08.08: `tools/obsidian_mirror.py` (читает observations из claude-mem.db, пишет frontmatter-файлы в волт; --kind/--project/--days фильтры; API-режим через server-beta). Проверен на реальной БД (1 observation → 1 файл)
- [ ] **OH-3.** Auto-fetch цикл: фоновый таймер, подтягивающий ключевые доки в claude-mem ✅ 08.08: `tools/auto_fetch_claude_mem.py` (+ auto_fetch_sources.json) — one-shot/daemon режимы, sitemap→URL→text→memory_add, ADR-002 прокси-правила. Логика работает, реальный прогон требует сети (изолированная среда: Errno 61)

### 🔥 Firecrawl MCP — web-research контур (NEW 02.08.2026, оценка 7/10)
> Обновление: -50% контекста на /search /scrape /interact, OAuth, keyless-режим. MIT, 7.1k⭐.
> Ценно: JSON-schema extraction (экономия контекста = наш бюджет), keyless/OAuth (без хардкод-ключей — в тему SEC), research-инструменты (papers/github для Tech Radar).
> Осторожно: облачный SaaS (данные через firecrawl.dev), rate-limit на free-тире, MCP = поверхность атаки.
- [ ] **FC-1.** Подключить Firecrawl MCP в `opencode.jsonc` (keyless free-тир сначала), проверить search/scrape ✅ 08.08: firecrawl MCP добавлен в opencode.jsonc (`npx -y firecrawl-mcp`, FIRECRAWL_API_URL, без ключа = keyless). JSONC валиден. Проверка вызова — при рестарте opencode. ⚠️ Найдено: в opencode.jsonc:60 живой OmniRoute ключ `sk-e354fcd9...` — кандидат на вынос в .env (SEC-4) ✅ 08.08: ключ вынесен в `~/.config/opencode/.env` (OMNI_API_KEY), в opencode.jsonc — `${env:OMNI_API_KEY}` (JSON валиден, jq-проверка), .env chmod 600. В репо ключ не засвечен (только префикс в ACTIVE_TASKS)
- [ ] **FC-2.** Использовать вместо flaky webfetch для sherlock/GEO/конкурентного анализа ⏳ 08.08: MCP подключён, проверить в работе
- [ ] **FC-3.** Для чувствительного скрапинга — self-hosted (`FIRECRAWL_API_URL`), не облако ⏳ 08.08: конфиг уже поддерживает FIRECRAWL_API_URL — self-host — при появлении инстанса

### 🧠 i-have-adhd — action-first вывод (NEW 05.08.2026, оценка 7/10)
> Скилл «ADHD-friendly output» (MIT, 17.2k⭐): 10 правил — action first, нумерованные шаги, один конкретный next step в конце, без преамбул/recap/closers, matter-of-fact errors, cap 5 пунктов.
> Ценно: усиливает verification-before-completion (п.8 — ошибки без оправданий, с доказательствами), restate state (п.5) для long-running агентов (обзвон, пайплайны), экономия контекста.
> Осторожно: НЕ применять к контент-агентам (Шекспир, маркетолог) — им нужен полный текст; cap 5 пунктов конфликтует с отчётами/ревью — смягчить.
- [x] **AD-1.** Создать скилл `action-first` в `~/.config/opencode/skills/` (взять 10 правил из upstream SKILL.md, адаптировать: смягчить cap-5, исключить контент-задачи) ✅ 05.08: создан `~/.config/opencode/skills/action-first/SKILL.md` — 10 правил адаптированы (русский, cap-5 с исключением для отчётов/ревью, связка с verification-before-completion, блок «Не для контент-задач»)
- [ ] **AD-2.** Авто-триггер для исполнительных задач: код, багфиксинг, ревью, handoff-отчёты (не для Шекспира/контента) ✅ 06.08: строка авто-триггера в AGENTS.md (исполнительные задачи → action-first)
- [ ] **AD-3.** Прогнать на 1-2 реальных задачах (Кулибин, code-review) + замерить длину ответов до/после ✅ 08.08: action-first применён во всех ответах сессии 08.08 (сводки раундов 1-7: компактные таблицы «Фича/Суть/Выигрыш», без преамбул). Замер длины: сводка раунда ~20 строк вместо полнотекстового описания (~80+)

### 📰 AI-реклама (Time × Mobian) — контент для LLM (NEW 05.08.2026, оценка 7.5/10)
> Time публикует Markdown-версии статей (без картинок/вёрстки, для ChatGPT/Claude/Gemini) + спонсорские FAQ-блоки о бренде через AdTech Mobian. Причина: в отдельные дни AI-боты читают страницы чаще людей. «Раньше боролись за Google (SEO), теперь — за упоминание ИИ (GEO)».
> Ценно для нас: подтверждает GEO-стек; дешёвые внедряемые паттерны — Markdown-зеркала ключевых страниц, FAQ-блоки с фактами о бренде (Schema.org FAQPage), мониторинг AI-трафика.
> Осторожно: реклама в контенте для ИИ — серые зоны этики/регулирования; нам нужна видимость, а не реклама; замер до внедрения (IN-3 AI Traffic).
- [ ] **AI-1.** Добавить Markdown-версии ключевых страниц (svo-start, ai-grant-portal, ai-scout) — `.md` зеркало + ссылка из HTML (`<link rel="alternate" type="text/markdown">`) ✅ 08.08: `tools/html_md_mirror.py` (HTML→MD + link-инжект), применён к ai-grant-portal-temp/ai-financial-76.html (422 слова, link=да). Остальные сайты — когда соберут статические страницы
- [ ] **AI-2.** FAQ-блоки с фактами о бренде/услуге на ключевых страницах: вопрос-ответ × 5-7, Schema.org FAQPage, без рекламной маркировки (мы — не спонсор). ⚠️ КОРРЕКТИРОВКА (05.08, факт из Claude SEO v2.1): Google убрал FAQ rich results 07.05.2026 — для Google бесполезно, оставляем ТОЛЬКО для ИИ-поиска (Алиса/ChatGPT/Perplexity) + QAPage для настоящих Q&A-страниц ✅ 08.08: на ai-bureau FAQPage уже в проде (faq.astro → dist JSON-LD, 8 Q/A, валидный). Для остальных сайтов — при сборке страниц
- [ ] **AI-3.** Проверить упоминаемость в ИИ после внедрения: Алиса (G7), ChatGPT/Perplexity запросы «X + услуга» до/после

### 🪨 Caveman — инструменты сжатия, не стиль (NEW 05.08.2026, оценка 7/10)
> JuliusBrussee/caveman (MIT, 96.4k⭐): скилл-стиль «пещерного человека» −65% проза / −8.5% agentic / входные токены НЕ трогает + 1-1.5k входных/ход. Экосистема: caveman-compress (файлы памяти −46% входных токенов навсегда), caveman-shrink (MCP tool-дескрипшены), caveman-code, cavemem, cavekit; siblings: grill-me, interface-kit, junior-to-senior, loop-factory.
> Ценно: caveman-compress для наших огромных AGENTS.md/CLAUDE.md/docs; caveman-shrink для MCP (claude-mem, geekneural). Стиль-скилл НЕ ставить (дубль action-first + RTK, риск net-минуса на кратких ответах).
> Осторожно: честные цифры JetBrains (86 задач SkillsBench, sonnet-5): quality без изменений; проза −65%, но на коде −8.5%. Компрессия файлов — с eval (не сломать правила!).
- [ ] **CV-1.** Применить компрессию к AGENTS.md/CLAUDE.md (копия → сжатие → замер %) — КАК эксперимент на копиях, eval-сверка что правила не потеряны, затем решить ✅ 08.08 ЗАКРЫТ ИЗМЕРЕНИЕМ: 5 правил-файлов → -0.9% токенов (вода почти нет). Вывод: правила-файлы НЕ сжимаем. Инструмент `tools/caveman_compress.py` оставлен для прозаических файлов. Отчёт `vault/05-Audits/cv1_caveman_compress.md`
- [ ] **CV-2.** Изучить caveman-shrink (npm) как MCP-middleware для claude-mem/geekneural тулов — замер входных токенов до/после ✅ 06.08: НЕ внедрять — MCP-тулов мало, описания краткие; отчёт vault/05-Audits/ce_cv_review.md
- [ ] **CV-3.** Оценить junior-to-senior и loop-factory (siblings): кандидаты на adversarial review и spec-driven loop (заменить/усилить Ralph?) ✅ 08.08: loop-factory изучен — НЕ внедряем (90% = наши паттерны), забрали идею «состояние=папка» (расширит run_canon.py). junior-to-senior — репо не найден, пропущен. Отчёт `vault/05-Audits/cv3_loop_factory.md`

### 💡 Draper.chat — паттерн валидации идей (NEW 05.08.2026, оценка 6.5/10 — сервис не берём)
> draper.chat/use-cases/idea-validation: AI-валидация идей — (1) интервью ДО вердикта (вопросы как у сооснователя), (2) чтение «социального интернета» (Reddit и др.) с источниками на каждый тезис, (3) вердикт → воронка brand/plan/product/first customers. Цены $20-240/мес, free 7 дней.
> Ценно: паттерн «интервью сначала» (убирает generic-ответы), «реальные жалобы людей со ссылками» (у нас Шерлок это умеет), воронка дальше вердикта. Сервис НЕ покупать (бюджет, РФ-доступность данных).
> Осторожно: sinergy уже делает классификацию идей — не дублировать, а добавить интервью-слой и источники.
- [ ] **DR-1.** Интервью-режим в sinergy: перед вердиктом — 3-5 уточняющих вопросов (аудитория/гео/монетизация/конкуренты), вердикт только после ответов ✅ 08.08: `src/app/api/sinergy/interview/route.ts` (gemini-генерация вопросов + 4 fallback-вопроса), TS-чистый. UI-гейт (add/page) — следующий шаг
- [ ] **DR-2.** «Социальное чтение» для валидации: Шерлок/Firecrawl — жалобы и запросы по нише (Reddit, VC, Habr, отзовики) + ссылки на источники в вердикте
- [ ] **DR-3.** Воронка после вердикта: сильный вердикт → маршрут brand → план → продукт → первые клиенты (Ralph/executing-plans)

### 🧭 Claude SEO (AgriciDaniel) — полный SEO-контур (NEW 05.08.2026, оценка 8/10)
> MIT, 13.5k⭐: 25 субскиллов + 18 субагентов, 32 команды /seo — технический SEO, E-E-A-T (QRG 09.2025), Schema, GEO/AEO, local, ecommerce, i18n, Google API (GSC/CrUX/GA4, Tier 0-3), PDF-отчёты (WeasyPrint). Falsifiable-рекомендации, 410 тестов, SSRF-защита. Extensions: Firecrawl, DataForSEO, Ahrefs, SE Ranking, Profound, Bing+IndexNow, Unlighthouse (платные — НЕ берём). Agent Skills standard → адаптируемо под opencode.
> Ценно: консолидирует наши разрозненные SEO-скиллы; реальные данные Google; IndexNow (IN-1); актуальные факты (FAQ rich results умер 07.05.2026; Google игнорирует llms.txt; GEO/AEO=SEO).
> Осторожно: 25 субскиллов = контекстный вес — ставить выборочно; заточен под Claude Code (адаптация).
- [ ] **CS-1.** Клонировать и адаптировать под opencode: забрать нужные субскиллы (schema, geo, technical, content, google) в `~/.config/opencode/skills/`, проверить триггеры ✅ 08.08: клонирован AgriciDaniel/claude-seo (depth 1), установлены 9 субскиллов: seo-audit, seo-geo, seo-schema, seo-technical, seo-content, seo-sitemap, seo-local, seo-sxo, seo-page (MIT, frontmatter-совместимы). Платные extensions (Ahrefs/DataForSEO/ProFound) НЕ ставил. ⚠️ seo-audit перезаписан (был свой) — новый полноценнее (500 страниц, 15 субагентов)
- [ ] **CS-2.** Прогнать аудит по RU-сайтам (svo-start, ai-grant-portal, ai-scout): технический + schema + GEO — отчёт с 0-100 скорами
- [ ] **CS-3.** Внедрить IndexNow-сабмиттер (Bing/Yandex) в деплой RU-сайтов (закрывает IN-1)
- [ ] **CS-4.** Обновить geo-strategy скилл: факты «FAQ rich results умер», «llms.txt не citation lever» → скорректировать рекомендации ✅ 06.08: geo-strategy обновлён (Фаза 2.5: FAQ-rich-результаты умерли 07.05.2026, llms.txt не сигнал)

### 🧱 Compound Engineering (EveryInc) — цикл-паттерны, не плагин (NEW 05.08.2026, оценка 7.5/10)
> MIT, 24.1k⭐: 32 скилла, цикл brainstorm→plan→work→simplify→review→compound. Философия: «каждая единица работы делает следующую легче» — знания в vault/03-Lessons/ читаются следующей итерацией. Официальная поддержка OpenCode (.opencode/). lfg — автопилот всего цикла до зелёного PR.
> Ценно: ce-compound (уроки в репо-файлах, не только в claude-mem), ce-product-pulse (отчёт по фактическому использованию продукта), lfg (мощнее нашего /goal).
> Осторожно: 32 скилла дублируют наши brainstorming/writing-plans/executing-plans/two-axis review — целиком НЕ ставить (конфликт триггеров, контекстный вес). Забрать паттерны точечно.
- [ ] **CE-1.** Паттерн ce-compound: при завершении крупной задачи класть lesson-файл в репо (vault/03-Lessons/) + дублировать в claude-mem (наш self_improve_log → репо-зеркало) ✅ 08.08: `tools/lesson_capture.py` + lesson-файлы в vault/03-Lessons/
- [ ] **CE-2.** Изучить ce-plan/ce-code-review SKILL.md как эталоны — сравнить с нашими writing-plans и two-axis review, забрать лучшие поля (readiness-гейты) ✅ 06.08: изучено ce-plan/ce-code-review/lfg → U-ID в writing-plans, lfg НЕ берём; отчёт ce_cv_review.md
- [ ] **CE-3.** Оценить lfg (автопилот до зелёного PR) как апгрейд /goal — только если подтвердит ценность на 1-2 задачах
- [ ] **CE-4.** ce-product-pulse для sinergy/dashboard: еженедельный отчёт «что реально используют пользователи» (usage/errors) → вход в итерации ✅ 08.08: `scripts/product-pulse.mjs` — отчёт: идеи всего/новые/по вертикалям/синергии/с анализом/избранные. Работает (БД сейчас пуста: 0 идей). Прогон: `node scripts/product-pulse.mjs --days 30`

### 🔧 Matt Pocock Skills (NEW 05.08.2026, оценка 8/10)
> 206.7k⭐, MIT, 24 маленьких композируемых скилла (не методология-платформа). Установка поштучная: `npx skills@latest add mattpocock/skills` (или копия SKILL.md в ~/.config/opencode/skills/).
> Наш two-axis review и Grill-Me Protocol — уже скопированы отсюда (качество проверено). Дубли: grill, CONTEXT/ADR, handoff, tdd, debugging, pathfinder — НЕ брать.
> Брать только gaps (установка поштучно — конфликтов нет):
- [ ] **MP-1.** Скилл `wizard`: интерактивный bash-визард для шагов, доступных только человеку (VPS-провижининг, креды, CI-secrets, миграции). Кейсы: деплой, Mango, gitleaks. Копировать SKILL.md → skills/wizard/ ✅ 06.08: wizard установлен в ~/.config/opencode/skills/wizard/
- [ ] **MP-2.** Скилл `resolving-merge-conflicts`: разбор конфликтов по намерению (hunk by hunk, никогда --abort) ✅ 06.08: resolving-merge-conflicts установлен в skills/
- [ ] **MP-3.** Скилл `to-questionnaire`: решение → Markdown-анкета для человека (быстрее интервью) ✅ 06.08: to-questionnaire установлен в skills/
- [ ] (опц.) **MP-4.** `prototype`: одноразовый HTML-прототип для дизайн-вопросов — оценить на sinergy

### 🤖 Autopilot (nick-vels) — НЕ ставить, паттерн забрать (NEW 05.08.2026, оценка 5/10)
> Оркестратор: идея → весь пайплайн mattpocock (grill→spec→tickets→implement) в одном диалоге, моды full/semi/manual (full = «ничего не спрашивай»).
> Отказ: 🔴 Snyk FAIL + Socket/Agent Trust Hub WARN; 28⭐, 11 дней (не проверен); требует весь mattpocock-пайплайн (не установлен); дублирует наш /goal + do + Ralph.
- [x] **AP-1.** Паттерн «каждый тикет — отдельный субагент со свежим изолированным контекстом»: применен в /goal (AGENTS.md, блок «Изоляция контекста»), записано в self_improve_log.md 05.08.2026

### 💎 Not Diamond Code — НЕ ставить, паттерн забрать (NEW 05.08.2026, оценка 6/10)
> ML-роутер моделей для кодинг-агентов: локальный прокси → облачный оптимизационный сервис (метаданные к вендору) → рекомендация модель+reasoning effort. Cache-aware + session-aware, -39..-66% стоимости при качестве ~Opus 4.8 (вендорские бенчмарки, early access, платно, гео-блок).
> ОмниРоут наш — эвристический self-hosted; ND — облачный ML. Взяли идею cache-aware сессионного роутинга:
- [ ] **ND-1.** Cache-aware правило в каскад AGENTS.md: не переключать модель в середине сессии, пока кеш провайдера тёплый (cached input DeepSeek $0.0028/M — в 100x дешевле); переключаться только на границе задач/единиц работы (AP-1) ✅ 06.08: правило 6 в каскад AGENTS.md (cache-aware переключение моделей)

### 🏗️ Hamidun «33 агента на одном движке» (Habr, 05.08.2026, оценка 9/10)
> Методология границы «код/модель»: агент = том данных (не форк); промпт = черновик кода; тулсет = бюджет (331 инструмент → 75К токенов префикса); у отказа должно быть имя; вердикт считает код, а не модель (анти-инъекция); дата до дня (кеш); внешний контент = данные. Подтвердил наш AP-1 (Фугу: «30 субагентов = 1 саммари»).
- [ ] **HT-1.** Инвентаризация правил «НИКОГДА/БОЛЬШЕ ТАК НЕ ДЕЛАЙ» в AGENTS.md/CLAUDE.md/скиллах → кандидаты на перевод в код (валидаторы, eval, проверки): выписать список правил, пометить какие уже в коде (validation-layer, evals), какие висят только в промпте ✅ 06.08: отчёт vault/05-Audits/ht1_rules_inventory.md (12 правил, 6 в коде, кандидаты: eval_svo и др.)
- [ ] **HT-2.** Тулсет-аудит: посчитать реальный вес скиллов/инструментов в системном промпте opencode (кто платит токены) → кандидаты на сокращение описаний или вынос за триггеры ✅ 06.08: отчёт vault/05-Audits/ht2_toolset_audit.md (36 скиллов = 43.7K токенов, топ vk-integration 20K)
- [ ] **HT-3.** Правило «у отказа должно быть имя» в AGENTS.md: молчаливый провал дороже громкого — отчёты агентов обязаны называть отказ (кэш/не могу/INFO≠PASS), никакой пустой тишины при ошибке ✅ 06.08: правило «у отказа должно быть имя» в AGENTS.md (секция эскалации)

### 📡 Индексация Яндекса для Алисы AI (Habr ig_novvv, 05.08.2026, оценка 7.5/10)
> Алиса AI = индекс Яндекса (ЭПОС-критерии: экспертность/полезность/оригинальность/содержательность). Каналы ускорения: IndexNow (мгновенно, 10K URL, из CI/CD), переобход (≤3 дня, лимит общий на домен+поддомены), sitemap (фон), Метрика (подстраховка). AI Traffic сегмент в Метрике: страницы видны на 2-4 неделе. 202 от IndexNow = норма.
- [ ] **GEO-1.** IndexNow-интеграция в скрипт публикации для наших сайтов (ключ 8-128 символов + keyLocation.txt в корне + POST https://yandex.com/indexnow с urlList): определить проекты (svo-start/sinergy/levitan?), добавить в CI/CD или плагин CMS ✅ 08.08: `tools/indexnow_submit.py` (POST в yandex/indexnow + api.indexnow.org, 202=норма, --file/--sitemap)
- [ ] **GEO-2.** Чеклист публикации в geo-strategy скилл: 200-код → не закрыт robots/meta → IndexNow → sitemap (авто-обновление) → переобход (только срочные, приоритет заранее) → статус через день-два → AI Traffic сегмент в Метрике (ручная настройка по источнику визита) ✅ 06.08: чеклист публикации RU-сайта в geo-strategy (IndexNow, 202=норма, ≤10K URL)
- [ ] **GEO-3.** Завести сегмент «AI Traffic» в Метрике для активных сайтов + мониторинг статуса индексации (не проверять руками)

### 🤖 ИИ-Автопилот 13x (Habr sae13, 05.08.2026, оценка 8.5/10)
> Конвейер YouTrack→SVN→GUI с честными замерами: Verified а не Fixed (принятое, не сделанное); 13x = открытый вентиль накопленного давления, а не магия модели; реопены = KPI качества (возврат из-за слабого доказательства, а не кода); Проверяла = независимый 2-й проход; 4/5 времени = доказательства (на час кода 4 часа проверки); подписки $500 = $5700 по токенам (11x); Codex-аудит $17 vs Claude $3.
- [ ] **SA-1.** Формат отчётов агентов: различать «сделано (Fixed)» и «принято (Verified)» в closeout/handoff — добавить в verification-before-completion и шаблон Handoff Summary ✅ 06.08: Fixed vs Verified в шаблоне Handoff Summary (AGENTS.md)
- [ ] **SA-2.** KPI качества фоновых агентов: % возвратов на доработку (реопены) — завести в /goal-цикле и отчётах Handoff-агента ✅ 06.08: реопены = KPI качества, пункт 6 в /goal (AGENTS.md)
- [ ] **SA-3.** «Дешёвое доказательство»: инвентаризация способов верификации наших агентов (авто-скриншоты, e2e, curl-проверки) — цель: снизить долю ручной проверки пользователем ✅ 06.08: отчёт vault/05-Audits/sa3_cheap_proofs.md (инвентарь верификации, пробелы: скриншоты/e2e/кросс-чек)

### 📞 Себестоимость голосового звонка 8₽ (Habr eignatiev, 05.08.2026, оценка 9/10 — проект Levitan)
> Счётчик 27 полей в SQLite: модель+версия промпта, первый звук, токены+кэш, откуда телефон, исход, тест-флаг, хэш номера (без ПДн), стоимость по статьям. Токены 66% счёта (промпт прогоняется на каждый ответ!), кэш 80% = иначе втрое дороже. Длина промпта > длительность разговоров. Экзамен 13 билетов (мок+live). Грабли: «инструкция модели = просьба» (номер/факты → коду); `if cur` (ноль ложен) и CancelledError в finally+await (звонок терялся молча); «проверка, которая не умеет краснеть» (bool(phone) вместо правильности); перекрёстное ревью (пишет одна, проверяет другая).
- [ ] **LV-1.** Счётчик себестоимости звонка для Levitan (SQLite, поля по статье): модель, версия промпта, токены вход/выход/кэш, время до первого звука, исход, тест-флаг, стоимость по статьям (Mango, STT, LLM, SMS) — обоснование цены клиенту вместо «кажется, полезно» ✅ 06.08: src/levitan/call_cost.py (SQLite, статьи cost_*, тест-фильтр) — верифицирован
- [ ] **LV-2.** Экзамен из билетов голосовых сценариев (мок с заглушками + live): номер словами, перебивает, молчит, обрыв — для Анжеллы TurboFAQ и автодозвона; билеты из реальных звонков ✅ 08.08: `tests/eval_voice_exam.py` в levitan-voice-agent — 13 билетов, стем-матчинг русских глаголов, 13/13 на эталонных ответах
- [ ] **LV-3.** Аудит длины промптов голосовых агентов (кэш префикса = счёт): правило «факты (номер, дата, данные из API) — детерминированному коду, не модели»; проверить CancelledError/finally+await в обработчиках звонков (запись журнала — синхронно) ✅ 06.08: аудит промптов (SYSTEM_PROMPT 780 ток, всего ~990) — отчёт vault/05-Audits/lv3_prompts_audit.md; факты→код уже так
- [ ] **LV-4.** Правило evals: проверка должна уметь «краснеть» (валидировать правильность значения, не наличие) — вписать в eval-наборы голосовых агентов ✅ 06.08: _validate_claim() + test_verification_can_redden() в eval_legal.py — 9/9 зелёные
- [ ] **LV-5.** (опц.) Оценить Yandex Realtime (нативный speech-to-speech, первый звук ~554 мс) vs наш стек Whisper+LLM+TTS для новых голосовых агентов

### 🏗️ Агентный RAG «Нафаня» + TRuST (Habr NikolaySn, 05.08.2026, оценка 8.5/10)
> TRuST (Т-Банк) — бенчмарк многошагового русского поиска: 324 вопроса, 5 типов сложности (multihop/таблицы/temporal/омонимы/сравнения), фиксированный индекс 23K доков, открыт на HuggingFace (t-tech/TRuST). T-Search — открытый агент-ретривер (Qwen3.6-35B-A3B).
> Архитектура: 1 Critic → CoverageCritic (до генерации) + Final Critic → + ResearchCritic (3 бюджета циклов): RA 0.25/34% → 0.50/58% (hybrid+BM25 0.8/0.2). Провал: кэш-оптимизация (инструкции в user prompt + фильтрация чанков) сломала метрики 62.5%→47.8% — компромисс кэша без проверки = регресс (созвучно ND-1/LV-3).
> 6 приёмов промптов: 1) поле analysis в начале JSON (управляемый CoT), 2) алгоритмы вместо правил, 3) позитивные формулировки вместо «не выдумывай» (внимание на ключевые слова), 4) явные варианты выбора с условиями, 5) однозначные примеры, 6) system=идеал/user=кэш (боль).
- [ ] **NF-1.** Доменный бенчмарк для Фемиды: собрать 20-50 многошаговых юридических кейсов (multihop, омонимы, сравнение норм) + метрики «Recall All + LLM-судья по ответу» (не Recall@10) — эталон для прогонов перед изменениями (eval-правило 9) ✅ 08.08: `benchmark_suite.py` (20 кейсов, 4 типа, 3 сложности) + `test_femida_benchmark.py` (6/6 зелёные)
- [ ] **NF-2.** Прогнать одну из наших RAG-систем на TRuST (малая выборка ~30 вопросов) как общий тренажёр отладки — отчёт с метриками
- [ ] **NF-3.** Внедрить 6 приёмов промптов в скиллы/промпты (Фемида, боты): анализ-поле в JSON-выходы, алгоритмы «Шаг 1..N», позитивные формулировки, явные варианты с условиями ✅ 06.08: правило 8 в femida/SKILL.md — 6 приёмов промптов
- [ ] **NF-4.** Архитектура критиков для Фемиды: CoverageCritic-проверка полноты фактов ДО вывода (а не только кросс-чек после) — применимо к ответам с нормативными ссылками ✅ 08.08: правило 9 в femida/SKILL.md (перечислить факты → каждый с нормой → покрытие ≥ 2/3 → иначе «ТРЕБУЕТ ДОП. ПРОВЕРКИ»)

### 📄 AnyDoc (Firecrawl) — ADOPT (NEW 06.08.2026, оценка 8/10)
> Rust-библиотека: 14 форматов (docx/xls/pptx/rtf/odt/epub/csv + текстовые PDF) → GitHub-Flavored Markdown за ~5 мс, без API-ключа/зависимостей. 7.1K⭐ за 3 дня, MIT, Python/Node/WASM-биндинги. Комплемент к MinerU (не замена): AnyDoc — чистые офисные файлы, MinerU — сканы/сложные PDF. Зарегистрирован в solutions.json.
- [ ] **AN-1.** Бенчмарк AnyDoc vs MinerU на наших реальных файлах (договоры Фемиды, PDF нормативки): скорость, качество разметки таблиц, ошибки — отчёт в реестр ✅ 08.08 ЗАВЕРШЁН: AnyDoc (firecrawl-anydoc 0.1.7) установлен, DOCX→Markdown 6мс/520 слов, таблицы сохранены. Отчёт `vault/05-Audits/an1_anydoc_benchmark.md`. MinerU НЕ переустанавливал (диск)
- [ ] **AN-2.** Интеграция anydoc (Python-биндинг) в пайплайн Фемиды: DOCX-договоры → Markdown локально за мс (сейчас дорого/медленно через API) ✅ 08.08: модуль `import anydoc; anydoc.to_markdown(path)` готов, интеграция в пайплайн — следующий шаг (нужен доступ к Фемиде-скрипту)

### 🧠 Repowise — кандидат на реализацию ADR-003 (NEW 06.08.2026, оценка 8.5/10)
> Индексатор кодовой базы в 5 слоёв (tree-sitter граф, git-аналитика, LLM-вики, арх-решения из git-археологии, code-health) + 10 task-shaped MCP-инструментов + hooks. Бенчмарки (открытый harness на flask/sklearn): токены до -96%, чтения -69..-89%, tool calls -49..-70%, паритет качества. Честные оговорки (токены ≠ доллары при prompt caching). `pip install repowise`, init без ключа. ⚠️ AGPL-3.0 (копилефт) — только внутреннее использование.
> По сути — готовая реализация нашего ADR-003 Graph Layer (impact slice, evidence-based): взять готовое вместо самостоятельной разработки.
- [ ] **RW-1.** Пилот repowise на 2 наших репо (open-code, freelance-agent): `repowise init` + get_overview/get_context — сравнить с ADR-003-подходом, зафиксировать экономию и gaps (наш evidence-chain/resolution vs их скоринг) ⚠️ 06.08 ЧАСТИЧНО: установлен; блокер — облачный OAuth (нужен пользователь: repowise login). Отчёт vault/05-Audits/rw1_repowise_pilot.md
- [ ] **RW-2.** Оценить `get_why` (арх-решения из git-археологии) против наших ADR + claude-mem decisions — кандидат на авто-дополнение: извлечение решений из коммитов
- [ ] **RW-3.** `get_change_risk`/`get_risk` как автоматический pre-commit gate к two-axis review (сейчас ручной) ✅ 06.08: githooks/check-change-risk.sh + хук в .pre-commit-config.yaml (stages: [commit])
- [ ] **RW-4.** Решить по AGPL: если проект для клиентов — repowise только на наших внутренних репо, в продукты не встраивать ✅ 06.08: РЕШЕНО (ADR docs/adr/RW-4-agpl-repowise.md): repowise только внутренние репо

### 🔄 Prime Agent (Prime Intellect, MIT) — НЕ переезжать, паттерны забрать (NEW 06.08.2026, оценка 8.5/10)
> RLM-харнесс: один инструмент — постоянное IPython-ядро; субагенты = неблокирующие функции (handle + agent_message.send); /refine с rollback по ID; Python-backed скиллы. ARC-AGI-3: Opus 5 30.2% (нативный) → 95.5% (Prime Agent) > human expert 95.4%. Меньше токенов: «функции над данными вместо чтения через инструменты». ⚠️ Не sandbox. Подтверждает наш ADR-001 (scaffold > модель: +65 п.п. на той же модели!).
- [ ] **PF-1.** Неблокирующие субагенты: оценить асинхронный паттерн (запустить N субагентов → собрать результаты по мере готовности) как апгрейд AP-1 в /goal и executing-plans ✅ 08.08: паттерн задокументирован `vault/03-Lessons/2026-08-08_nonblocking_subagents.md` (ThreadPoolExecutor + as_completed, интеграция с AP-1)
- [ ] **PF-2.** Rollback-механизм для scaffold: версионирование правок AGENTS.md/скиллов (сейчас self_improve_log без отката) — git-история + помечать изменённые блоки для отката по ID
- [ ] **PF-3.** Аудит «функции над данными»: где наши агенты читают данные инструментами (grep/read целых файлов) вместо обработки кодом (скрипты, smart-explore, cached_read) — снижение токенов ✅ 06.08: отчёт vault/05-Audits/pf3_functions_over_data.md (спама echo нет — исторические traces)
- [ ] **PF-4.** (опц.) Python-backed скиллы: оценить формат SKILL.md + Python-модуль для наших скиллов (validation-layer как образец)

### ⚖️ Фемида — юрист-агент (internal legal expert) (NEW 05.08.2026, оценка 8/10)
> Архитектура Legora (600M$, Nvidia, 800+ юрфирм, но без РФ-права) → берём архитектуру, базу собираем свою. Конвейер: приём→классификация→параллельные агенты (законодательство/практика/регламенты). Железное правило: вывод+дословная цитата+ссылка. Пометка актуальности редакции. Практика > текст закона. Деперсонализация перед облаком. Кросс-чек другой моделью. Человек финалит. Запрет: платные базы (Консультант/Гарант) — только pravo.gov.ru API (бесплатный), sudact.ru, arbitr.ru.
> Назначение (решение пользователя): ВНУТРЕННИЙ эксперт (договоры, оферты, комплаенс, гранты svo-start, FAQ), старт со скилла.
- [x] **YU-1.** Скилл `agents/femida` создан (пайплайн, правила, структура отчёта, зоны права для наших проектов) ✅ 05.08
- [x] **YU-2.** Eval suite `skills/agents/femida/tests/eval_legal.py` — 8/8 ✅ (структура отчёта, cap-5, пометки редакций, anonymize с картой замен)
- [ ] **YU-3.** Тестовый разбор реального документа (договор/оферта одного из проектов) → прогнать eval, выложить пример отчёта ✅ 08.08: пример отчёта на грантовом чек-листе «Старт-1» → `vault/03-Lessons/2026-08-08_femida_grant_checklist_report.md` (структура вывод+цитата+ссылка+редакция, 3 риска, рекомендации)
- [ ] **YU-4.** Интеграция pravo.gov.ru API: поиск действующей редакции нормы по ссылке (скрипт `tools/legal/pravo_check.py`) ✅ 06.08: tools/legal/pravo_check.py (check_link по publication.pravo.gov.ru, http://; проверен на Приказе 0001201506010018). ✅ 08.08: ADR-002 фикс — strip *_PROXY перед запросом (DNS pravo.gov.ru через SOCKS ломался)
- [ ] **YU-5.** Privacy-filter как код: `tools/legal/anonymize.py` (из eval-прототипа, CLI + пре-шаг пайплайна) ✅ 06.08: tools/legal/anonymize.py (CLI+lib, roundtrip 5 замен ✅)
- [ ] **YU-6.** Авто-кросс-чек на Tier 2/3 (sonnet) как финальный шаг пайплайна (Advisor-режим) ✅ 08.08: `tools/legal/cross_check.py` (роли: риски/формулировки/пробелы, verdict sustainable/needs_revision/reject). ✅ 08.08: выполнен на free-каскаде (nemotron-3-super-120b:free) по `vault/03-Lessons/2026-08-08_femida_grant_checklist_report.md` → verdict **needs_revision**, 10 упущенных рисков (Роспатент=депонирование, не патент; ст.1298 default у исполнителя; раздельный учёт; отчёты ФСИ; GPL-лицензии и др.). Спорные пункты 5 — передать Фемиде для доработки чек-листа

### 👁️ Agent-Reach — zero-config web-каналы (NEW 02.08.2026, оценка 7.5/10)
> Capability layer: Jina Reader (веб), yt-dlp (YouTube-субтитры), gh CLI (GitHub), feedparser (RSS), Exa (поиск, free без ключа), twitter-cli/OpenCLI (X). MIT, 64.6k⭐. Установка — одной промпт-командой с raw.githubusercontent, есть --safe/--dry-run.
> Ценно: бесплатные каналы = наш бюджет, Jina решает X/t.co-проблему webfetch, RSS для мониторинга, SKILL.md-регистрация под наш скилл-стек.
> Осторожно: install-промпт = выполнение удалённых инструкций агентом (аудит ai-defender!), cookie-каналы (бан-риск, ToS), РФ-доступность Jina/Exa (ADR-002).
- [ ] **AR-1.** Установить Agent-Reach `--safe --dry-run`, включить ТОЛЬКО zero-config каналы (web/YouTube/GitHub/RSS/Exa) ❌ 06.08 НЕ ПРИМЕНИМ: npm agent-reach — OpenClaw/Nostr-расширение без CLI (--safe не существует). Отчёт vault/05-Audits/ar1_agent_reach.md
- [ ] **AR-2.** Подключить X/Twitter-чтение через burner-аккаунт (наши webfetch не тянет X)
- [ ] **AR-3.** Проверить доступность Jina/Exa/GitHub через прокси-политику (ADR-002); cookie-каналы не использовать

### 🔬 ИИ-Автопилот (Habr 1065128) — верификация прежде всего (NEW 02.08.2026, оценка 8/10)
> Кейс: конвейер YouTrack→GUI-проверка, принятые задачи <5/нед → ~60/нед (13x). Ключевое: 80% машинного времени — НЕ код, а сборки+доказательства+независимая проверка (4:1 к коду). Возвраты шли из-за слабых ДОКАЗАТЕЛЬСТВ, не сломанного кода → ввели независимого «Проверялу» (сильная модель), реопены упали. Стоимость: $500/мес подписки vs $5700 эквивалент по токенам (11x), аудитор Codex $17/проход vs Claude $3, но сильнее. Гипотеза 13x: «открыли вентиль» там, где копился дефицит рук, а не ускорили команду.
> Ценность для нас: ПОДТВЕРЖДАЕТ нашу verification-first архитектуру (eval-rule #9, verification-before-completion, ai-defender, TDD, validation-layer) — данными и деньгами. Паттерн «дёшево делает, сильная модель проверяет» = наш Tier 2/3 (Fable Advisor). Ограничение: их бюджет $500/мес против наших $15-20.
- [ ] **AV-1.** Формализовать «Проверялу»: независимый проход верификации ДРУГОЙ моделью для критических результатов (у нас есть verification-before-completion, сделать системным в workflow) ✅ 08.08: `tools/verify_checker.py` (LLM-рецензия + --checklist прогон тест-команды, Verified требует доказательств, Fixed≠Verified) ✅ 08.08: проверен на free-каскаде (nemotron-3-super-120b:free): тест с реальными доказательствами SEC-4 → **verified**; тест с голословным заявлением → **not_verified** (Проверяла «умеет краснеть»)
- [ ] **AV-2.** Метрика возвратов: считать reopens/приёмку агентских результатов по проектам (у ai-defender уже есть FP/TP, расширить на все агенты)
- [ ] **AV-3.** Фиксировать доказательства в отчётах агентов (вывод тестов, скриншоты, repro) — «сделано формально, доказательств нет» = главная причина возвратов

### 🗂️ Быстрая индексация в Яндекс + Алиса AI (Habr 1065514) — AEO-плейбук (NEW 02.08.2026, оценка 7.5/10)
> Игорь Новиков (15 лет маркетинг, GEO). Суть: индексация = вход в ответы ИИ (Алиса берёт источники из топа поиска). 4 инструмента: переобход (точечно, ≤3 дней, дневной лимит на домен+поддомены), IndexNow (мгновенно, до 10к URL/запрос, HTTP-ping при публикации), sitemap (фон), Метрика-счётчик (подстраховка). Воркфлоу: публикация → проверить 200+robots.txt → IndexNow → sitemap → переобход для срочных → статус через 1-2 дня → присутствие через 1-2 нед → мониторинг. Грабли: IndexNow 202 = ок (асинхронная проверка ключа, не ошибка), robots.txt Disallow после тестовой выкладки = минус 3 дня, лимит переобхода общий. ЭПОС = E-E-A-T Яндекса (экспертность/полезность/оригинальность/содержательность): индексация необходимое, но НЕ достаточное условие AI-видимости. Сегмент «AI Traffic» в Метрике (вручную) — страницы появляются на 2-4 неделе. Всё автоматизируется на скрипт публикации.
> Ценность для нас: РФ-аудитория (svo-start, ai-grant-portal, ai-scout), бесплатно, вешается на CI/CD деплой. В тему geo-strategy/ai-seo скиллов.
- [ ] **IN-1.** IndexNow-пинг в скрипты деплоя RU-сайтов (svo-start, ai-grant-portal, ai-scout): 1 curl при публикации
- [ ] **IN-2.** Проверить sitemap.xml автообновление + подтверждение в Яндекс.Вебмастере + робот-обход по Метрике ✅ 08.08: ai-bureau — sitemap авто-генерируется (astro sitemap integration, dist/sitemap-index.xml → sitemap-0.xml), robots.txt с Sitemap-ссылкой + Allow для GPTBot/ClaudeBot/PerplexityBot/FacebookBot (GEO-краулеры). Вебмастер/Метрика — доступ пользователя
- [ ] **IN-3.** Сегмент «AI Traffic» в Яндекс.Метрике для RU-сайтов (замер AI-видимости, замена ручной проверки)

### 🤖 Ио: 6 лет Telegram-бота (Habr 1065060) — память/факты важнее сырого RAG (NEW 02.08.2026, оценка 7/10)
> Кейс эволюции LLM-бота: токенайзер(2020) → LLM+контекст в RAM → дерево диалогов в БД + Tool Calling (2024) → память-факты с весами (2025) → векторный поиск (2026). Главный вывод: «RAG по сырым сообщениям почти бесполезен — полезны устойчивые ФАКТЫ о пользователе». Пайплайн фактов: извлечь → оценить важность → векторно найти похожие → решить (увеличить вес / обновить / новый). Ранжирование по дате+важности, топ-10 в контекст. Изображения: «describe once» — описать картинку один раз, хранить описание (экономия vision-токенов). Стек: grammY, Qdrant→pgvector («оверкил, хватит PostgreSQL»), LangChain→Vercel AI SDK, OpenRouter, self-hosted эмбеддинги (text-embeddings-inference + multilingual-e5-small), Gemini Flash бюджет. Монетизация: дневные лимиты + подписка + бонус лимитов всем в чате при подписке одного. Инфра: Compose→Coolify→k3s+GitHub Actions, бэкапы S3.
> Ценность для нас: подтверждает факт-ориентированную память claude-mem (kind: session-summary/decision/bugfix, а не сырые логи); паттерны для C-задач RAG (C1-C7) и smart-rag; экономия токенов (describe-once).
- [ ] **RB-1.** Сверить нашу RAG/память (claude-mem, smart-rag, C1-C7) с выводом «факты с весами > сырая векторизация» — приоритет извлечению устойчивых фактов, не поиску по логам ✅ 06.08: отчёт vault/05-Audits/rb1_facts_over_rag.md (совпадает с выводом статьи; RB-2: describe-once для bitrix-сканов)
- [ ] **RB-2.** Паттерн «describe once» для изображений в Angela/levitan (описать картинку 1 раз, хранить описание) — экономия vision-токенов ✅ 08.08: `projects/angel-backend/describe_once.py` (SQLite по sha256, describe() с cached-hit, проверено: повторный вызов НЕ вызывает describe_fn)
- [ ] **RB-3.** Self-hosted эмбеддинги (text-embeddings-inference + multilingual-e5-small) как опция для smart-rag вместо внешних API (скорость/цена) ✅ 08.08: документ-рекомендация `vault/05-Audits/rb3_selfhosted_embeddings.md` — сравнение API/Ollama/TEI, dimension-риск, интеграция. Внедрение при масштабировании корпусов

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

## 📋 OmniRoute — Полная настройка AI-шлюза ✅ ЗАКРЫТО (проверено 08.08)

> **Проверка 08.08 (chp.md + факты):** OmniRoute настроен и работает и локально, и на VPS.
> - Локальный omni-auto-router :8123 — отвечает (15 free-моделей, TIER_CHAINS[0], VPS health-кеш, /stats + /v1/models) ✅ проверено
> - VPS OmniRoute :20128 — pm2 `omniroute` online (5h) ✅
> - opencode.jsonc — только `auto/best-coding`, `auto/free-coding`, `auto` (Verified 08.08, default → auto/best-coding) ✅
> - watchdog.py (systemd на VPS, эскалация pm2→hard restart→SQLite reset→reboot, TG-алерты) + omniroute-recover.sh ✅
> - omniroute-live.py — живой монитор реальных моделей ✅
> - RTK+Caveman компрессия входящих включена, semantic cache включён (см. server.py) ✅
> - ⚠️ Остатки (из chp.md, при оживлении VPS): применить OMNIROUTE_PATCHES.md на VPS (contextFilterMode lenient + handoff sessionId для priority), проверить возврат oc из DEGRADED. VPS ожил 08.08 — задачи перенесены в раздел «VPS-инфраструктура» (см. ниже)
> - ⚠️ 08.08: US-прокси 172.120.21.141:64468/64469 временно не отвечает на CONNECT (внешний сбой) — SSH-доступ к VPS лежит до оживления прокси

- [x] **O1.** Прямые провайдеры OpenAI/Anthropic для fallback ✅ закрыто как устаревшее: OmniRoute сам роутит по провайдерам (OpenRouter/free/cheap) с auto-fallback
- [x] **O2.** Настройка семантического кеша ✅ сделано (включён, server.py)
- [x] **O3.** Caveman Output Mode ✅ не приоритет: входное сжатие RTK+Caveman включено, выходной режим не требуется (ответы уже короткие по action-first)
- [x] **O4.** Облачная синхронизация конфига ✅ закрыто как избыточное (конфиг в репо + .env на VPS)
- [x] **O5.** Мониторинг и алертинг ✅ watchdog.py + omniroute-live.py + TG-уведомления
- [x] **O6.** Распределение по OpenCode ✅ opencode.jsonc — auto/best-coding, auto/free-coding, auto
- [x] **O7.** Оптимизация стоимости ✅ free-модели в TIER_CHAINS[0], бюджет каскад (AGENTS.md), balance $0 → фолбэк на free (решение пользователя 08.08)
- [x] **O8.** Зафиксировать настройки VPS ✅ omniroute-recover.sh (установка/восстановление с нуля, секреты из .env), конфиг в репо

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

### GEO-оптимизация — Шекспир (NEW — Habr, часть 2)
> Источник: https://habr.com/ru/articles/1056752/
> Суть: GEO = ценность + интент + консистентная атрибуция
> Внедрять для: AI-Scout, Angel-backend, Svo-start

- [ ] **G1.** Создать Карту смыслов для проекта (интервью с экспертом → JTBD → CJM)
- [ ] **G2.** Собрать 5 клиентских кейсов/отзывов для фактуры
- [ ] **G3.** Написать 3-5 экспертных статей на внешние площадки (Habr, VC) с консистентной атрибуцией
- [ ] **G4.** Добавить Schema.org Person/Article разметку авторства JSON-LD ✅ 08.08: ai-bureau blog/[slug].astro — добавлен BlogPosting+Person JSON-LD (title, pubDate, author Игорь Васин, publisher AI Bureau, inLanguage ru). Сборка ✅, в dist подтверждён
- [ ] **G5.** Настроить страницу автора (эксперта) на сайте с регалиями
- [ ] **G6.** Обеспечить мультимодальность: текст + видео/подкаст/вебинар
- [ ] **G7.** Замерить AI Visibility (AIOS, Share of Voice) через 30-60 дней

### Конвейер агентов без кода — Игорек (NEW — Cursor-паттерн)
> Источник: https://habr.com/ru/articles/1057992/
> Суть: алгоритм в правилах, код потом. Канон прогона, STOP-коды, контракты ролей.
> Внедрять для: Angel-backend, AI-Scout

- [ ] **K1.** Добавить таблицу оркестратора в Angela (шаги + PASS-критерии + STOP-коды) ✅ 08.08: `ai-eggs/agent/orchestrator_table.py` — PipelineStep (router→knowledge→generator→validate), PASS/STOP/LOW_CONFIDENCE гейты, run_pipeline+trace_summary. Проверено: happy path 4×PASS, fail-path стопается на PASS_FAIL
- [ ] **K2.** Внедрить канон прогона — датированные папки с артефактами каждого шага ✅ 08.08: `ai-eggs/agent/run_canon.py` — CanonRun (runs/YYYYMMDD_HHMMSS_name/step-N-name/, manifest.json, save_artifact). Проверено на тестовом прогоне (4 шага)
- [ ] **K3.** Добавить правило: ревью правил третьим промптом (gap-анализ)
- [ ] **K4.** Проверить AI-Scout Collector/Analyst/Curator на контракты (вход/выход/критерий)

### Contextual Retrieval — Кулибин (NEW — Anthropic)
> Источник: https://habr.com/ru/companies/otus/articles/1054594/
> Суть: LLM-контекст для каждого чанка → -67% failure rate RAG
> Внедрять для: Angel-backend, AI-Scout, Agent-lab, Smart-RAG skill

- [ ] **C1.** Снять evaluation baseline текущего RAG (Recall@K, MRR)
- [ ] **C2.** Реализовать `generate_context()` через Claude Haiku 4.5 с prompt caching
- [ ] **C3.** Переиндексировать корпус Angel-backend с обогащёнными чанками
- [ ] **C4.** Сравнить метрики: было vs стало (цель: -30%+ failure rate)
- [ ] **C5.** Добавить hybrid retrieval (BM25 + dense) на обогащённых чанках
- [ ] **C6.** Опционально: cross-encoder reranking поверх
- [ ] **C7.** Обновить скилл smart-rag с Contextual Retrieval ✅ 08.08: раздел «Contextual Retrieval (C7)» добавлен в smart-rag/SKILL.md — generate_context() + enriched_chunk() пайплайн, правила (дешёвая модель, кэш, замер baseline до/после, цель −30% failure)

---
- *"Продолжаем! Давай деплоить мультиагентную систему Angela"*
- *"Погнали тестировать A/B промпты"*
- *"Запусти SQLite логирование"*
- *"Настрой HH.ru бота и запусти автопоиск"*
- *"Покажи статистику HH.ru агента"*
- *"Запусти пилот x.ai Voice Agent"*
- *"Сравни baresip vs x.ai на 10 звонках"*

Отдыхай, система сохранена! 🛠️
