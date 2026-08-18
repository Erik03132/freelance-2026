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

### 🐍 Pi Coding Agent (YouTube AI Stack Engineer, 11.08.2026, оценка 7.5/10)

### 🤖 AI Voice Manager (AVM) — AI-голосовой менеджер (NEW 11.08.2026)
> **Проект:** `/ai-bureau/ai-voice-manager` (в составе AI-bureau). 
> **Суть:** Локальный AI-голосовой менеджер для малого бизнеса РФ. 
> **Стек:** Levitan (Mango + livekit-sip, нестабилен), TTS (Яндекс Realtime), CRM (Bitrix24), LLM (OmniRoute), Telegram bot. 
> **Статус:** pre-product. Голосовой агент ещё не стабилен (бесплатные модели, нестабильный стек). 
> **Продукт не продаётся клиентам до прохождения гейта стабильности** (голосовой агент стабильно отвечает на входящие без «немых» звонков). 
> **Название по-русски:** AI-голосовой менеджер (автомат). 
> **Цифры:** рекуррентная подписка 7-60К₽/мес, маржа ~70%. 
> **Гейт продажи:** AVM-0 (стабильность голосового агента). 
> **Критический**: Голосовой агент в Levitan нестабилен, пока не готов. Настроить гейт стабильности и приступить к пилоту (10-20 клиентов). 
> **Оценка:** 5/10 — пока концепция.
> Источник: https://www.youtube.com/watch?v=9AfjQf-6fHQ (Pi — минимальный терминальный агент от Марио Ценера,
> автор libGDX, ~86K звёзд; OpenClaw работает на Pi как harness). Видео 10:27, транскрипт извлечён (yt-dlp).
> **Суть:** ядро из 7 тулов (read, bash, edit, write, grep, find, ls) + системный промпт <1000 токенов.
> Ничего больше в ядре: нет MCP, субагентов, plan mode, todo, фонового bash, permission-поп-апов.
> Всё остальное — скиллы (Open Agent Skills), промпт-темплейты, TypeScript-расширения, npm-пакеты.
> Правило Ценера: «если ему не нужно — не попадает в ядро; растёт твой сетап, а не инструмент».
> Сравнение (прямая цитата): «Claude Code — полированный и закрытый. OpenCode даёт automatic LSP и
> multi-agent из коробки. Pi делает меньше намеренно и отдаёт тебе хуки».
> Безопасность: Pi запускается с правами пользователя без песочницы (документация честно предупреждает,
> указывает на 3 опции контейнеризации: Gondolin/microVM, Docker, OpenShell sandbox).
> Ключ API можно задать shell-командой (`!cmd` → 1Password/keychain), не храня сырой ключ на диске.
> Сессии = дерево (не плоский лог), ветки с /fork, /clone, /compact, саммари брошенной ветки.
> /model + thinking level прямо в имени (sonnet:high). Provider-лист ~30 (включая DeepSeek, Groq, Ollama).

- [ ] **PI-1.** Применить правило Ценера к AGENTS.md/HT-2: ядро opencode-сетапа не растёт — фичи
      (MCP, субагенты, todo) живут как скиллы/расширения за триггером. Уже частично сделано выносом
      в skills-lib ✅ 11.08: правила HT-2 + skills-lib подтверждены этим видео (тот же паттерн).
- [ ] **PI-2.** Проверить секрет-паттерн «ключ = shell-команда» (OP/keychain) для .env-прокси в AGENTS.md
      — сейчас ключи в .env, сырой формат; shell-подстановка `!cmd` снижает риск утечки файла.
- [ ] **PI-3.** Взять идею «саммари брошенной ветки сессии» в claude-mem/handoff: при смене ветки
      (snapshot-переход) подвешивать саммари пройденного пути к новой позиции — аналог нашего handoff.

### 📸 Сколько токенов в скриншоте — таблица vision-тарифов (BotHub, 11.08.2026, оценка 7/10)
> Источник: https://habr.com/ru/companies/bothub/articles/1068866/ (BotHub, ELF19, 10.08.2026).
> **Суть:** один скриншот 1920×1080 стоит по-разному: GPT-5.5 = 2040 токенов (сетка 32×32,
> ceil(w/32)×ceil(h/32), режим high/original, до 2048px по длинной стороне), Claude Opus 4.8 = 2691
> (патчи 28×28, повышенное разрешение), Gemini 3.1 = до 1120 (media_resolution: low 280 / medium 560 /
> high 1120 / ultra_high 2240 — бюджет, не сетка). Обрезка 1920×1080 → 960×540: GPT 510 (в 4x меньше),
> Claude 700; сжатие JPEG/PNG НЕ влияет на счёт (только размеры). Паттерн «2 изображения» (экран +
> увеличенный фрагмент) = +25% к запросу, но лучше OCR мелкого текста. Рекомендации: убрать панель
> задач/вкладки, не склеивать экраны, для кодов/артикулов использовать high/оригинал и перепроверять.
> Генерация картинок: GPT Image 2 1024×1024 = 4160 выходных токенов; Nano Banana 2 ≈ 67 200 CAPS (~14.5₽).
> **Применимость:** у нас vision-кода в стеке НЕТ (проверено: projects/, levitan, avito — пусто), но
> это справочная таблица для будущих GUI-агентов и скриншот-проверок (screenshot опции в firecrawl,
> верификация UI). Модель для vision-задач: Gemini 3.1 (1120) в 2.4x дешевле Claude (2691) по визуалу.

- [ ] **VS-1.** Зафиксировать таблицу vision-тарифов в справку для агентов (памятка: 1920×1080 =
      GPT 2040 / Claude 2691 / Gemini до 1120 токенов; обрезка = -75% у GPT, ~-75% у Claude;
      сжатие не экономит) ✅ 11.08: ACTIVE_TASKS секция VS (эта запись — сам справочник).
- [ ] **VS-2.** При появлении vision-задачи (GUI-агент, скриншот-верификация, OCR кода) —
      выбирать Gemini 3.1 (high/ultra_high) вместо Claude: -60% визуальных токенов при том же качестве.
- [ ] **VS-3.** Шаблон скриншот-проверки для верификации: если нужен код ошибки/артикул — паттерн
      «2 изображения» (полный экран + фрагмент 960×540), иначе обрезка до области + контекст словами.

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

### 🎯 Model or Harness — локализация отказов агентов по edge·fault (NEW 11.08.2026, оценка 9/10)
> Источник: https://arxiv.org/abs/2607.28802 (Scale AI, 30.07.2026). Таксономия 41 failure mode: каждый отказ = `компонент1—компонент2 · fault: сторона` (8 компонентов: Model/Owner/Grader/Third-party/Context/Memory/Tool/Env). Ключевое: (1) **repair-assignment** — один видимый отказ требует разных интервенций (post-training vs harness vs environment vs benchmark), outcome-метки их сливают; (2) **правило атрибуции** — модель виновата, если более способная модель при тех же условиях избежала бы отказа → 36/41 model-side; (3) **root cause** — метка на первое событие, из которого исполнение не восстановилось (не симптомы); (4) **selective voting** — панель 4 судей + abstain: 3/4 согласны = precision 0.83 @ 90% coverage, единогласие = 0.96 @ 68% (GPT-5.5 κ=0.76 vs люди).
> Применимо: наш HT-3 «у отказа должно быть имя» называет отказ, но не локализует сторону. Формат `edge·fault` + fault_side в trajectory_eval + подтверждает self_improve_log (scaffold-апдейт = harness-сторона).
- [ ] **MH-1.** Формат локализации в отчётах агентов (closeout/handoff): к имени отказа добавить `edge·fault` (напр. «API 429 → environment» vs «модель сдалась после 1×429 → tool—model · fault: model») — обновить шаблон Handoff Summary + verification-before-completion
- [ ] **MH-2.** fault_side в trajectory_eval: при реопене/closeout классифицировать провал по edge·fault, детект «модель сдалась после транзиентной ошибки» (Tool Recovery Failure) — расширить `tools/trajectory_eval.py`
- [ ] **MH-3.** Selective voting в cross_check: панель судей + abstain (воздержание при расхождении вместо одиночного судьи) — порог согласия как параметр
- [ ] **MH-4.** Связать с self_improve_log (Target B): scaffold-фикс по harness-стороне отказов (после 2+ fault: harness) — дописать в self-improvement skill

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
- [ ] **DR-1.** Интервью-режим в sinergy: перед вердиктом — 3-5 уточняющих вопросов (аудитория/гео/монетизация/конкуренты), вердикт только после ответов ✅ 08.08: `src/app/api/sinergy/interview/route.ts` (gemini-генерация вопросов + 4 fallback-вопроса), TS-чистый. ✅ 10.08 (код): UI-гейт в `add/page.tsx` (2-шаговый флоу: форма → вопросы → сохранение), `classify` принимает `interview_answers` (в промпт Gemini), типы `InterviewQuestion/InterviewAnswers`. Build OK, eval 12/12. ⏳ Осталось: коммит, деплой на Vercel, smoke-тест в проде (handoff: `projects/sinergy/docs/handoff_dr1_interview.json`)
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
- [ ] **MP-5.** Аудит наших скиллов по методологии Pocock `writing-for-agents` (два бюджета: context/cognitive load; pointer = 1 триггер на ветку; позитив вместо negation; оговорки в тело; progressive disclosure против sprawl) ✅ 11.08: **Fixed** — description 4 скиллов: `ponytail` 111→71 слов (−36%), `beautify-github-readme` 99→70 (−29%), `femida` 78→69, `action-first` (убраны дубли-синонимы отчёт/report, negation→позитив). **Осталось:** (1) sprawl `vk-integration` (462 стр), `levitan-voice-agent` (369), `seo-local` (315), `seo-geo` (314) — прогрессивное раскрытие референса за pointer; (2) SEO-семейство 14 скиллов `seo-*` — SSoT-дублирование; (3) `levitan-voice-agent`/`bitrix-integration` restate environment (конфиги/команды дублируют проект → кэши, устаревают)

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
- [ ] **HT-2.** Тулсет-аудит: посчитать реальный вес скиллов/инструментов в системном промпте opencode (кто платит токены) → кандидаты на сокращение описаний или вынос за триггеры ✅ 06.08: отчёт vault/05-Audits/ht2_toolset_audit.md (36 скиллов = 43.7K токенов, топ vk-integration 20K); ✅ 11.08: реальные вызовы из opencode.db (77 всего, ядро: bot-development 12, brainstorming 7, mango-autocall 6, levitan-voice-agent 5; половина скиллов 0-1 вызов → вынос в skills-lib/) ✅ 11.08: 12 скиллов (0 вызовов, 115KB) вынесены в ~/.config/opencode/skills-lib/ (seo-* ×8, beautify-github-readme, svo-veteran-support, wizard, to-questionnaire); экономия ~268 токенов/запрос + no false-trigger; возврат через mv (README.md); уточнение: постоянная цена = описания, не файлы ✅ 12.08: HT-2 остаток — дедупликация deployment/bot-семейств: `deployment-procedures` (90% дубликат `deployment`) вынесен в skills-lib, полезное (`pm2 monit`, `[ ]` чек-лист) слито в `deployment`; bot-family (`bot-development`+`telegram-bot-patterns`+`agents/botman`) и `workflow` — НЕ дубликаты (слои), оставлены; удалён битый симлинк `~/.agents/skills/deployment-procedures`; skills-lib/README.md + ht2_toolset_audit.md обновлены
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
- [ ] **LV-6.** (опц.) Grok Voice Think Fast 2.0 (xAI) как альтернатива для Levitan — АЛЬТЕРНАТИВНЫЙ ВАРИАНТ, отложено (NEW 11.08.2026). Конвергентный стек (STT+LLM+TTS+tool-calling в одной модели): первый звук 0.7s (vs ~1.5-3s сейчас), STT в 1.5-2x точнее Deepgram Nova 3 (в шуме до 10x), tool-calling до конца фразы, короткие ответы, $0.08/мин (текущий стек ~$0.03-0.05/мин), русский есть. Artificial Analysis 82.9 vs GPT Realtime 2.1 (79.1) vs Gemini 3.1 Flash (69.5). ⚠️ Блокеры: РФ-блокировка xAI (реалтайм-аудио через прокси = латентность+риск обрывов), self-hosted pipecat → облако, в бою не проверен. Тестировать только A/B на 10-20 звонках (TTFT, успешность, обрывы, $/мин), не мигрировать рабочий Levitan. Связано: X1-X4 (x.ai Voice Agent пилот)

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

### 🧠 RAGFlow (infiniflow/ragflow) — вердикт: принят к рассмотрению, ждёт триггер (NEW 13.08.2026)
> [проверено (src) → ПРИНЯТО С ОГОВОРКОЙ] Enterprise-RAG движок (87.9K⭐, Apache-2.0, v0.26.4 от 07.07.2026, активен: обновлён 13.08). «Контекст-слой для LLM»: DeepDoc-парсинг сложных/сканированных документов, template chunking, тиражируемые цитаты-источники (grounded citations, меньше галлюцинаций), recall+fusing+re-ranking, agentic workflow + MCP + gVisor code-executor, коннекторы (Confluence/S3/Notion/Discord/Google Drive/Feishu/Telegram), DeepSeek v4/Gemini 3 Pro/GPT-5. ТРЕБОВАНИЯ: CPU≥4 / RAM≥16GB / Disk≥50GB / Docker / Python≥3.13 / только x86 (официальных ARM64-образов НЕТ). Технологически сильнее нашего smart-rag (sentence-transformers) в deep-doc/citations/агентных пайплайнах.
- [ ] **RG-1.** ⚠️ НЕ внедрять сейчас (YAGNI): нет документо-тяжёлых задач; наш VPS 217.149.23.113 (рядом с levitan/ai-eggs) минимум 16GB RAM + Docker, x86 — отдельный инстанс. Для голосовых агентов levitan не релевантен (вызов/STT/TTS, не корпоративный RAG).
- [ ] **RG-2.** 🔑 ТРИГГЕР внедрения: документо-тяжёлая задача (базы договоров/статей/нормативки, контент-корпус, AI-Scout-проект с качественным RAG) → поднять RAGFlow (docker compose, CPU-образ) на отдельном инстансе или VPS с ≥16GB RAM; для ARM64 — сборка образа.
- [ ] **RG-3.** Сверка с существующим стеком при триггере: smart-rag (лёгкий, embedded) vs RAGFlow (тяжёлый, enterprise) — критерий выбора по объёму/сложности данных и latency-требованиям; RAGFlow НЕ заменяет claude-mem/факт-память (RB-1: факты с весами > сырая векторизация).

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

### Qwen-MM-Plugins — мультимодальность для харнесса (NEW — GitHub)
> Источник: https://github.com/QwenLM/Qwen-MM-Plugins
> Суть: официальный QwenLM репозиторий (1.9K★, Apache-2.0). Делает любой harness мультимодальным: каждая capability = skill (модель знает о тулах) + MCP-сервер (uvx, на лету). Поддерживает opencode напрямую («Other harnesses: Gemini CLI · opencode · pi — register skill + MCP yourself»).
> Capabilities: core (локальное чтение img/video/docs в динамическом разрешении — БЕЗ ключа), api (DashScope: vision_chat, OCR, grounding, Omni A/V с таймстампами/ASR/диаризацией/event counting), search (Serper: web + reverse-image), video-memory (QA по длинным видео), video-edit, blender, freecad, edu-agent.
> Оценка: 7.5/10. Закрывает наш главный gap — vision-кода в стеке нет (см. VS-1). core бесплатен; api/search упираются в отсутствие ключей DashScope/Serper.

- [ ] **MM-1.** Поставить core-капсибилити (локальное чтение изображений/видео, без ключа) — регистрация скилла + MCP в конфиге opencode ✅ 11.08: репозиторий изучен, интеграция = manual register skill+MCP (installer не покрывает opencode); ждёт появления реальной vision-задачи
- [ ] **MM-2.** Qwen Omni A/V (api) — потенциальное усиление video-clipper: event counting / temporal grounding вместо LLM-эвристик по транскрипту (video_clipper.py: find_highlights_llm). Блокер: нужен DASHSCOPE_API_KEY (Alibaba Cloud)
- [ ] **MM-3.** Завести DASHSCOPE_API_KEY (Alibaba Cloud DashScope) + SERPER_API_KEY, если появится мультимодальная задача (OCR чеков/скринов, верификация скриншотов, видео-аналитика). ✅ 13.08: по решению пользователя — ОТЛОЖЕНО (не критично), держать в статусе, ключи завести при появлении реальной vision/поиск-задачи

### Herdr — рантайм для кодинг-агентов (NEW — GitHub)
> Источник: https://github.com/herdrdev/herdr (27.5K★, 1.9K forks, Apache-2.0, создан 27.03.2026, активен). Пост: нейробизнес.
> Суть: терминальный workspace-менеджер (Rust, один бинарник, tmux-подобный) как фоновый сервер. Агенты живут в панелях, работают при закрытой крышке/без сети. Распознаёт 19 агентов: Pi, Claude Code, Codex, Cursor Agent CLI, Gemini CLI, **opencode** (lifecycle-интеграция v5, session restore через `opencode --session`), Grok CLI, Copilot CLI, Devin, Kimi, Qoder, Hermes, Antigravity CLI, Kilo, MastraCode и др. Статусы working/blocked/idle (lifecycle hooks для opencode/Pi/Kimi/MastraCode/Kilo; screen manifests для остальных).
> Agent-native: CLI + socket API — агент может `herdr agent prompt <target> <text> --wait --until idle/blocked`, `agent wait`, `agent read`, `agent send-keys`, спавнить панели и пропмтить ДРУГОЙ харнесс (Codex → Claude Code → ответ). Без общего протокола/MCP — просто управление терминалами.
> Оценка: 8/10. Это НЕ замена opencode — это инфраструктура для фоновых/параллельных мульти-харнесс-сессий. Рекламный посыл поста (anthropic-анонс «сессии Claude общаются» + Herdr) преувеличен: механизм — терминальный ввод/вывод, не структурированный протокол. Ключевая ценность для нас: фоновые долгие сессии + мульти-модельная верификация (связь с MH).

- [ ] **HR-1.** Herdr как альтернатива/надстройка handoff.sh + `claude --bg`: фоновые панели с opencode/Claude Code, детач `ctrl+b q`, опрос `herdr agent list` / `agent wait --until blocked` вместо пинг-понга по логов. ⚠️ Изоляция worktree per session — обязательна: YouTube Zuevich/k1qVs60he7E (~Why Next «Как общая папка ломает ИИ Агента»): `git checkout` в session A сажает коммит session B → в MH параллельные харнессы в shared чекауте дают ложное selective voting. Herdr ≠ git-изоляция (он — tmux). → добавить `git worktree` per panel через ce-worktree, re-verify branch перед коммитом, scoped check до changed-files. Ставить, только когда появится реальная потребность в параллельных долгих сессиях разных харнессов
- [ ] **HR-2.** Мульти-модельная верификация (связка с MH-1..4, selective voting): верификатор-ревизор на Claude Code/Codex в панели Herdr, ожидание `blocked`/`idle`, чтение ответа через `agent read`. Усиливает Fable 5 Advisor-режим. Требует worktree-isolation (см. HR-1) — иначе конфликт репо → ложное голосование
- [ ] **HR-3.** Проверить интеграцию opencode v5: lifecycle-плагин для статусов + session restore — как открывается `herdr integration install opencode` и что даёт по сравнению с текущим фоновым запуском

### ManuAGI дайджест 20 проектов (NEW — YouTube St3wKHJwF60)
> Источник: https://www.youtube.com/watch?v=St3wKHJwF60 (ManuAGI, 11.08.2026, 18:36, 528 просмотров). Обзор 20 AI-проектов за неделю.
> Суть: рекламный дайджест (аффилейты), оценка 5/10. Отобрал 4 релевантных нам:
> **Toolport** — локальный open-source MCP-шлюз: все MCP-серверы за одним портом, per-task включение тулов (резак токенов), ключи в keychain, audit-трейл. Работает с claude, codex, cursor, codeex, VS Code; Mac/Linux/Windows. → агрегация наших 4 MCP (claude-mem, firecrawl, notebooklm, geekneural) + экономия контекста.
> **AgentConnect** — self-hostable слой: ACP-агенты (Claude Code, Codex, Gemini CLI) подключаются в Slack/Discord/**Telegram**/GitHub с ролями, памятью и scoped permissions; control plane хранит только конфиг, не транскрипты/код. → паттерн для наших Telegram-ботов (Angela, HH) и будущих коллаборативных агентов.
> **BrowserOS neo** — локальный браузер для агентов: параллельные сессии, снапшоты каждого шага, меньше токенов (web-агент читает снапшоты), импорт логина из Chrome, Linux/Windows. → закрывает gap GUI-задач для vision (см. VS-1..3, MM-1).
> **Prompt Bridge** — Chrome-расширение: перенос полного контекста чата между GPT/Claude/Grok/Gemini/DeepSeek с конденсацией в токен-экономные саммари, авто-инжект в поле ввода. → паттерн для каскада моделей (ND-1: перенос контекста между тирами без переплаты).
> Справочно (не наше): Omniwork, Solop OS, Argos, Coldtea.ai, Troop, Lightfield, Stepshot, Nitro 4.0, Rindler, Soup CLI (нужен GPU), Basedash Subscriptions, Bevel (= наш ADR-003), Firecrawl (= уже есть задача).

- [ ] **MA-1.** ✅ 13.08: Toolport изучен и ОТКЛОНЁН по YAGNI (не внедряем сейчас). Проверено (п.13): `tsouth89/toolport` — 160⭐, MIT, активна (обновлён 13.08), gateway (stdio/HTTP) + десктоп Tauri, lazy discovery (4 мета-тула вместо каталога → 96% меньше tool-defs, 91% меньше total tokens; BENCHMARK.md), tool-integrity (rug-pull/poisoning), per-agent scoping, OpenCode поддержан (`opencode.json mcp`). ПОЧЕМУ НЕТ: после MA-1.2 у нас 3 MCP (claude-mem/geekneural/transcribe, ~30 тулов ≈ 3-4K токенов) — экономия уже получена отключением серверов; Toolport = слой (Tauri-приложение + gateway-бинарник + зависимость от active-development проекта) ради малого остаточного выигрыша. Возврат к оценке при ЛЮБОМ из: (1) >10 MCP-серверов, (2) нужен OAuth в каждом, (3) мульти-клиент (Claude+Codex+openCode в одном registry), (4) понадобится tool-integrity-защита
- [x] **MA-2.** AgentConnect против нашего бота-стека ✅ 12.08: НЕ внедряем (YAGNI). AgentConnect = self-hostable слой для ACP-агентов (Claude Code/Codex/Gemini CLI) в Slack/Discord/Telegram/GitHub с ролями + scoped permissions + native вызовы друг друга. Наш `botman`-стек (aiogram/ptb + FSM + RAG + Smart Fallback + `igorek`-оркестрация) уже покрывает нужды. AgentConnect = опция, если позже понадобится мульти-харнесс-мульти-агентность в канале (связь с MH-1..4: верификатор-ревизор на Codex рядом с Claude Code-агентом в том же Telegram)
- [ ] **MA-3.** BrowserOS neo — статус «предложено автором, НЕ проверено» (13.08: `gh search repos "browseros neo"` → OSS-проект не найден, только конфиг-кит 1⭐). Не как решение, только гипотеза. Актуализировать верификацию (video/docs/web) при появлении реальной GUI-задачи: «верификация скриншотов/UI-тесты» → тогда выбирать между ним и Qwen-MM (MM-1) по принципу «меньше кода»
- [x] **MA-4.** Prompt Bridge — РЕАЛИЗОВАН ✅ 12.08: создан `tools/context_bridge.py` (CLI, не MCP — не платит токенами в system prompt). Перенос контекста между моделями каскада с LLM-конденсацией (~89% сжатие). Эндпоинт: локальный OmniRoute `http://127.0.0.1:20128/v1/chat/completions` (как в opencode.jsonc), модель `auto/fast`, ключ опционален (OMNI_API_KEY). CLI: `python3 tools/context_bridge.py -i session.txt -o summary.txt -m auto/fast`. Связь с ND-1 (cache-aware): решает обнуление prompt cache при смене модели через сжатие контекста. ТЕСТ ЗАБЛОКИРОВАН: провайдеры OmniRoute упали (503), OpenRouter 403/таймаут — инфраструктурная недоступность, не баг скрипта. Проверить позже, когда провайдеры поднимутся. Решение изменено: вместо «отложить» — реализовано (пользователь выбрал п.2)

### Google Cloud: DMi Partners — agentic AI для маркетинга (NEW — YouTube 5S1wIiS5LQo)
> Источник: https://www.youtube.com/watch?v=5S1wIiS5LQo (Google Cloud, 12.08.2026). Транскрипт извлечён yt-dlp (en auto-sub, 8.5K символов).
> Суть: DMi Partners (маркетинг-агентство) строит self-service платформу на Google Cloud: Looker (semantic layer) + BigQuery → Orion by Gravity (agentic interpretation, proactive insights) → DMi (экспертиза в training). Агентства, строящие лучших агентов, процветают. Бренды не знают «как перейти от разговоров об AI к стратегии» → low-cost self-service модель.
> 🔑 Ключевой паттерн: **изоляция tenant-данных** — per-brand projects + Looker access level filters (один бренд не видит данные другого). + proactive prompts («какие вопросы задавать» — агент ведёт пользователя к инсайтам).
> Оценка: 6/10 (маркетинг Google Cloud, но паттерн изоляции tenant ценен для наших multi-client агентов).

- [ ] **DM-1.** Мульти-тенантная изоляция для наших агентов: применить паттерн DMi (per-project + access filters) к `ai-scout` (разные клиенты) и `angel-backend` (разные бренды). Уже есть `claude-mem` projectId — расширить на уровень RAG/данных (не только memory). Связь с HR-1 (worktree) + RB Tech «4 слоя workspace»
- [ ] **DM-2.** Proactive prompts («какие вопросы задавать»): добавить в GEO/agent-паттерн — агент сам ведёт пользователя к инсайтам через starter prompts (как в DMi интерфейсе). Связь с GEO-оптимизацией (Шекспир)
- [ ] **DM-3.** Self-service слой для клиентов: если делаем агента для клиента (ai-scout/angel) — дать self-service интерфейс (как DMi через Marketplace), а не только полное управление. Оценить, нужно ли для наших проектов

### Habr 1069180 — SEO-маркетинг 90/10, zero-click, GEO (NEW — Habr)
> Источник: https://habr.com/ru/articles/1069180/ (Вадим Мамонтов, эксперт по нейросайтам/GEO, 12.08.2026).
> Суть: классическое SEO = 10% (техничка/тайтлы), 90% — ценность для живого человека. Zero-click уже случился: ~69% поисков без перехода на сайт (Similarweb 2026), ~26% сессий заканчиваются на выдаче (Pew 2025), B2B 85% выбирают из «списка первого дня» (Bain 2025). Нейровыдача учит покупателя — переход уже произошёл. Коммерческие запросы («заказать», «рассчитать») всё ещё ведут на сайт; бренды в нейроответах +35% органики (Seer 2025). SEO 360: релевантность + поведенческие + E-E-A-T + коммерческие + интерактив разом.
> 🔑 ИИ-агент для отзывов: кластеризация возражений/болей через LLM (отсекает накрученные по формулировкам, не метаданным). Карта смыслов: ценность из 3 источников (собственник / менеджеры продаж / записи звонков + отзывы). Статусная аналитика: ClientID → CRM → offline-конверсии (метрика сделки, не клика). Кейс: завод теплиц, конверсия 0,35%→1,3% за 9 мес без накруток.
> Оценка: 8/10. Прямо в тему нашего GEO (Шекспир/geo-strategy): zero-click, нейровыдача, E-E-A-T, коммерческие запросы.

- [ ] **HB-1.** GEO под zero-click: адаптировать контент-стратегию (Шекспир) под нейровыдачу — фокус на коммерческие запросы («заказать/под ключ/рассчитать»), E-E-A-T (портфолио/кейсы/экспертность), попадание в нейроответ (Seer: +35% кликов). Связь с GEO-оптимизация (строка 653) + geo-strategy скилл
- [ ] **HB-2.** ИИ-агент для отзывов: кластеризация возражений/болей через LLM (как в статье — отсев накрученных по формулировкам). Добавить в ai-scout или angel-backend как модуль анализа отзывов клиентов. Связь с bot-development (Smart Fallback)
- [ ] **HB-3.** Карта смыслов: методика сбора ценности из 3 источников (собственник / менеджеры / звонки+отзывы) — внедрить в контент-маркетинг (Шекспир) для клиентских сайтов. Закрывает потребность, а не «рассказ о себе»
- [ ] **HB-4.** Статусная аналитика: ClientID → CRM → offline-конверсии (метрика сделки, не клика). Оценить для ai-scout/angel-backend — нужен ли захват ClientID + триггер статуса в Метрику. Связь с VC-1 (аналитика)

### Habr 1069372 — GEO-плейбук: 2 кейса (AUTOPRO +168%, Бананашоу +40%) (NEW — Habr)
> Источник: https://habr.com/ru/articles/1069372/ (Женя Ванжула, AdsON + ГЕОранк, 12.08.2026). Суть: практический GEO (продвижение в нейровыдаче). Кейсы: автоподбор AUTOPRO (переходы +168%, заявки 4→13) и детские праздники Бананашоу (заявки +40%). Техники: пул промптов (30-50 разговорных, по интентам), доля голоса (share of voice), повторные замеры; публикации в подборках/рейтингах (DTF/VC); отзывы (Яндекс Карты); Schema.org; llms.txt (автор сам оговорил «влияние нужно проверять»); конкретные факты/цифры вместо «быстро и качественно»; экспертность вне сайта.
> Оценка после ВЕРИФИКАЦИИ (AGENTS.md п.13): 9/10 — совпадает с проверенными GEO-практиками. llms.txt VERIFIED как маргинальный (Google не использует, 97% не читаются, SE Ranking нет корреляции). Schema.org JSON-LD VERIFIED как высокоценный.

- [ ] **HG-1.** [проверено src → ПРИНЯТО] Факты/цифры на сайте вместо общих фраз («подбор 5-9 дней, 170 пунктов проверки» → цитируемо). VERIFIED: Princeton GEO (arXiv:2311.09735) — statistics +32%, quotations +41% к видимости. Связь с HB-1 (value-first), Шекспир GEO-секция. Перенести в контент-стратегию клиентских сайтов
- [ ] **HG-2.** [проверено src → ПРИНЯТО] Schema.org JSON-LD: Article/Organization/Person + FAQPage/Product где уместно. VERIFIED (SEJ, CrawlSense, arXiv:2603.10700): LLM retrieval читает JSON-LD; принцип «less is more» (3 корректных > 12 битых), DOM-consistency критична. Применить на наших сайтах (ai-eggs/angel/ai-scout) как техничку
- [ ] **HG-3.** [проверено src → ПРИНЯТО] Сторонние упоминания/отзывы/подборки/карты = ГЛАВНЫЙ рычаг GEO (не свой сайт). VERIFIED: brand mentions corr 0.664 с AI-цитатами vs backlinks 0.218 (Zyppy meta-analysis). Для локальных ниш (РФ): Яндекс Карты, profi.ru, отзовики. Связь с HB-1 (внешние площадки)
- [ ] **HG-4.** [проверено src → НЕ приоритет] llms.txt: VERIFIED маргинален (Google не использует для AI Overviews; Ahrefs 97% файлов не читаются; SE Ranking 300K доменов — нулевая корреляция с цитатами; Attrifast тест — лифт только Perplexity +10pp, ноль ChatGPT/Gemini). Автор Habr сам оговорил. Можно ставить как дешёвый hedge (30 мин, 0 downside), НЕ делать ставку. Не путать с HG-2 (Schema.org)
- [ ] **HG-5.** [проверено src → ПРИНЯТО] Методика измерения GEO: пул 30-50 разговорных промптов по интентам (выбор/сравнение/стоимость/локал/услуга), стартовый замер → повторные по расписанию, метрики (доля упоминаний/ссылок/тональность/доля голоса). VERIFIED подход (ГЕОранк/Profound/Otterly). Применять, если делаем GEO-заказ для клиентов (angel/ai-scout)

### TG neurobussines (3011 + окрестности) — Skill-Guide, 80% дешевле, OpenMontage (NEW — Telegram)
> Источник: https://t.me/s/neurobussines/3011 (канал «НейроБаза», 65.5K подп, 12.08.2026). Окрестные посты 2972-3022.
> NB-3011 (Skill-Guide): сканирует установленные скиллы, раскладывает по полочкам (категория, описание на RU, под какую модель, GitHub-источник), **считает реальные вызовы**. Автор: «половину ни разу не открывал, только память занимают». NB-2973: Claude+Codex «на 80% дешевле токенов без потери качества». NB-3010: `github.com/calesthio/OpenMontage` — автомонтаж видео словами, кадры из бесплатных стоков, бесплатно. NB-3005/3008: бригада субагентов-монтажёров (транскрибатор/резчик пауз/плашки) — паттерн нашей multi-agent архитектуры.
> Оценка: 8/10 (NB-3011 прямо к HT-2; NB-2973 валидирует cost-cascade; NB-3010/3005 — ref для video-clipper/agent-архитектуры).

- [ ] **NB-1.** Skill-Guide → адаптировать skills-lib: добавить в README.md счётчик реальных вызовов скиллов (как HT-2 метрику). Подтверждает: половина не используется → кандидаты на вынос в skills-lib. Связь с HT-2 (skills-lib/README.md)
- [ ] **NB-2.** 80% дешевле токенов (NB-2973) → ЗАПИСАТЬ как валидацию нашего cost-cascade (Tier 0/1 + RTK+Caveman ~89% сжатие OmniRoute). Не внедрять (уже есть). Связь с каскадом моделей в AGENTS.md
- [ ] **NB-3.** OpenMontage (`github.com/calesthio/OpenMontage`) → reference для video-clipper скилла: автомонтаж словами, кадры из открытых стоков, бесплатно. Добавить ссылку в video-clipper SKILL.md как альтернативу/дополнение
- [ ] **NB-4.** Бригада субагентов-монтажёров (NB-3005/3008) → паттерн совпадает с нашей архитектурой (transcribe→cut→overlay). Зафиксировать как подтверждение паттерна, не менять

### YouTube 3afX6vZ3zaM — Obsidian как «второй мозг» для агентов (NEW — YouTube)
> Источник: https://www.youtube.com/watch?v=3afX6vZ3zaM (12.08.2026). Суть: Obsidian vault = единая БЗ для нескольких агентов (Codex/Code/Hermes/Antigravity) на разных серверах. Агенты создают/редактируют заметки, общаются через них. Ключ: просить агента добавить YAML-свойства (frontmatter) в заметки или предложить, как дополнить материалы свойствами → «перестаёт тупить» в навигации. Иерархия: inbox (свалка/мок) = вход → карта → заметки = документация.
> У нас уже есть: Obsidian подключён (AGENTS.md 0.1 — агенты читают ТОЛЬКО md из vault/06-Library/** и ~/Library/Mobile Documents/.../КНИГИ/), claude-mem server-beta как persistent БЗ, CONTEXT.md/ACTIVE_TASKS как иерархия.
> Оценка: 7/10. Подтверждает архитектуру; НОВОЕ: structured YAML frontmatter в vault-заметках для навигации агента (gap у нас).

- [ ] **OB-1.** ✅ 13.08: внедрено минимально. [проверено (src) → ПРИНЯТО, с оговоркой] YAML frontmatter в vault-заметках (минимум: `type`, `tags`, `status`, `updated`). Сделано: (1) `vault/CLAUDE.md` (rulebook) — правила frontmatter + иерархия + правило-исключение для 00-Inbox; (2) `book_digest.py` пишет `type: book-digest`/`tags`/`updated`/`status: read`; (3) AGENTS.md 0.1 ссылается на vault/CLAUDE.md. ОГОВОРКА: rulebook без MCP-retrieval — фильтрация по frontmatter вручную/через grep; MCP-obsidian при масштабировании. Просить агента самого предлагать свойства — правило зафиксировано в vault/CLAUDE.md
- [ ] **OB-2.** ✅ 13.08: инбокс есть и работает — `vault/00-Inbox/` + ночная раскладка (night_reader Фаза 1b: NFC-нормализация имён, мусор удаляется, сырьё → 06-Library/КНИГИ). Флоу: TG/VPS-мост (fetch_url+tg_bot) → 00-Inbox → night_reader → 06-Library; СЫРЬЁ никогда не попадает в ACTIVE_TASKS напрямую. 13.08: фикс «❌ Не удалось скачать: exit 1» — `fetch_url.py` получил retry×3 на транзиентные сбои (сеть/5xx/429/Timeout), задеплоен на VPS, рабочая share.google-ссылка OK. ✅ РИСК ПРОКСИ РЕШЁН 13.08: angela-bot переведён на прямое соединение (VPS за пределами РФ — прямого доступа к api.telegram.org достаточно, getMe 3x ok ~0.15s); `_make_session` в tg_bot.py инвертирован: прямое первым, SOCKS5 fallback. После рестарта ProxyTimeoutError/ProxyConnectionError (60s) исчезли
- [ ] **OB-3.** Паттерн «несколько агентов + одна Obsidian vault, общение через заметки» — УЖЕ покрыто claude-mem server-beta (multi-project, projectId). Зафиксировать как подтверждение архитектуры, не менять

### Habr 1069782 (simpleone/СФТ) — agentic-разработка, агент-критик (NEW — Habr)
> Источник: https://habr.com/ru/companies/simpleone/articles/1069782/ (simpleone — вендор no-code BPM/CФТ, 12.08.2026).
> Суть: agentic-разработка = оркестрация ролей (product owner / архитектор / разработчик / QA), агент-критик (пара «создатель + критик»: критик заворачивает ~58% черновиков создателя → итерация до прохождения), нужен фундамент ДО агентов (доска задач / IDE / runtime / data / MCP), low-code как среда исполнения (про erStudio фирмы).
> ВЕРИФИКАЦИЯ (п.13, анти-авторитет): паттерн «парный агент-критик» подтверждён OSS/наукой — PairCoder (ACL 2026, 91% pass@1, +20.3% над single-agent, −40-70% токенов против multi-agent бригад), DebateCoder (ACL 2025, дебаты критика/создателя). Вендорский low-code-питч (erStudio) — реклама, НЕ принимать.
> Оценка: 7/10 (паттерн критика ценный и подтверждён; статья наполовину реклама своего no-code).

- [ ] **SM-1.** [проверено src → ПРИНЯТО] Агент-критик/верификатор: пара «создатель+критик» как штатный режим для ответственных задач (код/контент/промпты). VERIFIED: PairCoder (ACL 2026: 91% pass@1, +20.3% к single, −40-70% токенов vs multi-agent), DebateCoder (ACL 2025). Ложить на уже имеющееся: Two-axis Review (/code-review), Fable 5 Advisor, validation-layer @validated, судьи в MH (selective voting). Не заводить новый инструмент — усилить существующие шаги критиком
- [ ] **SM-2.** ✅ 13.08: сопоставление подтверждено. Наша модель: PO = ACTIVE_TASKS/бэклог (igorek-приоритизация), архитектор = kulibin (+Fable 5 Tier 3 на стратегию), разработчик = кодеры (я + субагенты general/explore), QA = процессные шаги: /code-review (Two-axis Review), eval_gate.sh (eval suite), verification-before-completion, ai-defender (security-аудит), критик (SM-1) = Fable 5 Advisor + @validated + судьи MH. ⚠️ Gap: QA не выделен отдельным субагентом — роли критика/QA реализованы как шаги типового флоу, не как сторона-ревизор. Отдельный субагент-верификатор — только при частых реопенах (сейчас не частые)
- [ ] **SM-3.** ✅ 13.08: стека достаточно, gap нет. Доска: ACTIVE_TASKS.md; IDE: OpenCode+ZCode; runtime: VPS/pm2 217.149.23.113 (временно недоступен, watchdog держит) + локальный OmniRoute :8123; data: claude-mem server-beta (Postgres); MCP: claude-mem+geekneural+transcribe (firecrawl/notebooklm отключены MA-1.2, ~105→мало тулов). low-code erStudio отклонён как вендорский питч
### 🧩 DeepSeek Harness (dsh) — «Everything is a Plugin» (NEW 14.08.2026, оценка 9/10 — взять паттерны)
> Источник: https://github.com/deepseek-ai/deepseek-harness (v0.1 developer preview, 2026-08-13, MIT, 94k★).
> Ядро: [Cordis](https://github.com/cordiverse/cordis) — мета-фреймворк «spatiotemporal composability». Формула: `Agent = Model + Harness`.
> 9 категорий плагинов (все заменяемы через конфиг без правки core): модели, инструменты, навыки (skills),
> сессии, песочницы, storage/FS, loops, scheduling, UI. Провайдеры моделей агностичны (Anthropic/OpenAI/Bedrock/Azure/Gemini).
> **Seam** (шов заменяемости) = 3 роли: Service Definition (интерфейс) + Service Provider (реализация) + Consumer (инжект).
> **Append-only Session Log** как source of truth: жёсткое правило «всё, что видит модель, реконструируется из лога» → resume/fork/replay/telemetry на одном event-stream.
> Event lifecycle как точки расширения: `turn/start → claim input → agent/pre-step → assemble prompt+tools → agent/request → llm/stream → assistant/message → tool/call → tools/pre-execute → tools/execute → tools/post-execute → tool/result → step/end → turn/end`.
> 4 runtime-мода (одно ядро): Standard / Code (модель пишет TS-прогон против тулов) / Minimal (bash+str_replace_editor) / Creator.
> Композиция: Profile (именованная сборка) + Bundle (группа плагинов) + Patch layer (row-based оверлей конфига).
> Песочница строгая: Linux Landlock / macOS Seatbelt / Windows restricted-token ACL.
> Сравнение с нашим стеком: skills≈skills, OmniRoute≈models-plugin, claude-mem≈sessions-plugin, но у нас НЕТ единого типизированного kernel и строгого model-visible⇒logged лога.

- [ ] **DSH-1.** [предложено автором] Оформить ADR: адаптация паттернов DeepSeek Harness к нашему стеку (seam Definition/Provider/Consumer + append-only event-log как source of truth для claude-mem/отчётов агентов). VERIFY: нужно сопоставить с Cordis paper и нашим AGENTS-каскадом перед принятием.
- [ ] **DSH-2.** Применить seam-паттерн к OmniRoute и скиллам: явно выделять интерфейс / провайдер / потребитель, чтобы менять backend без правки продукта (расширить `tools/omni-auto-router` + скилл-загрузчик).
- [ ] **DSH-3.** Правило «model-visible ⇒ logged»: довести claude-mem до строгого append-only лога, из которого реконструируется контекст модели (fork/replay/resume). Сейчас observations хранятся, но контекст модели не всегда реконструируем из одного стрима.
- [ ] **DSH-4.** Изучить Cordis paper («A Programming Paradigm for Spatiotemporal Composability», cordiverse/paper) — оценить, стоит ли брать kernel целиком под OpenCode/ZCode вместо децентрализованных текстовых правил AGENTS.
- [ ] **DSH-5.** Runtime-моды как паттерн: выделить Minimal-режим (стабильная tool-поверхность) для чистых бенчмарков моделей (аналог нашего использования eval suite + FREE_MODELS). Code-mode SDK — кандидат на упаковку многоходовочных операций агента в один прогон.

### 🔌 Anthropic Knowledge Work Plugins (KWP) — вертикальные плагины ролей (NEW 14.08.2026, оценка 8.5/10 — взять манифест+commands)
> Источник: https://github.com/anthropics/knowledge-work-plugins (Apache-2.0, 23.5k★, 11 плагинов). Для Claude Cowork/Claude Code.
> Суть: плагины превращают Claude в специалиста роли/команды/компании. 11 доменов: sales, legal, finance, data,
> product-management, marketing, customer-support, bio-research, enterprise-search, productivity, hr (+ cowork-plugin-management).
> Структура file-based (без кода): `.claude-plugin/plugin.json` (манифест) + `.mcp.json` (коннекторы/MCP) + `commands/` (slash-команды) + `skills/` (доменная экспертиза, авто-подгрузка).
> Коннекторы = MCP-серверы (Slack, HubSpot, Snowflake, Jira, Notion…). Установка: `claude plugin marketplace add anthropics/knowledge-work-plugins` → `claude plugin install sales@knowledge-work-plugins`.
> ОТЛИЧИЕ ОТ DSH: Anthropic KWP — ВЕРТИКАЛЬНЫЕ (роли/домены), DeepSeek Harness — ГОРИЗОНТАЛЬНЫЕ (runtime-слои: models/tools/sandbox/loop).
> KWP не имеет runtime-плуггиабилити (seam, append-only лог) и жёстко привязан к Claude. Но индустрия сошлась на «skills + plugins + MCP» как единице — и Anthropic, и DeepSeek независимо.
> НАШ СТЕК УЖЕ СОГЛАСЕН: `skills/`(SKILL.md/AgentSkills) ≈ KWP skills/, наш MCP (claude-mem/geekneural) ≈ KWP `.mcp.json` коннекторы, AGENTS-каскад ≈ манифест/процессы.

- [ ] **KWP-1.** [предложено автором] Адаптировать `plugin.json`-манifest (`.claude-plugin/plugin.json`) к нашим скиллам: каждый скилл/группа скиллов получает манифест SSoT (имя, триггеры, зависимости, MCP-коннекторы). VERIFY: сопоставить с нашим AGENTS-каскадом и форматом SKILL.md перед принятием.
- [ ] **KWP-2.** Выделить `commands/` (slash-команды для явного вызова) аналогично нашим skill-вызовам — пакетировать часто используемые скиллы (start-day/finish-day/goal/code-review) как явные команды с именем `plugin:command`.
- [ ] **KWP-3.** Изучить структуру 2-3 плагинов (sales, data, finance) на предмет best-practice skill-файлов и `.mcp.json` коннекторов — взять паттерны в наши скиллы (botman/marketer/kulibin), не копируя доменное содержимое.
- [ ] **KWP-4.** Сопоставить KWP vs DSH: наш стек покрывает оба направления? Вертикаль (роли) = скиллы ✅; горизонталь (runtime) = DSH-1..4 (seam/kernel). Закрыть gap marketplace-концепта (установка плагинов по имени) — нужен ли нам, или достаточно симлинков скиллов.

### 🛡️ Claude-BugHunter — эталонный security-бандл на Agent Skills (NEW 14.08.2026, оценка 8/10 — референс-архитектура, НЕ деплоить оффенсив)
> Источник: https://github.com/elementalsouls/Claude-BugHunter (Sachin Sharma/ElementalSoul, 3.6k★, MIT+CC-BY-4.0, authorization-гейты).
> Суть: skill-бандл для bug-hunting и ВНЕШНЕГО red-team (авторизованного). 82 скилла, 15 slash-команд,
> 681 паттерн из реальных HackerOne-репортов, 24 класса уязвимостей + enterprise-матрицы (M365/Entra, Okta, vCenter, SSL-VPN).
> КРИТИЧНО: написан на той же спец. Agent Skills (SKILL.md), что грузят Claude Code · OpenCode · Codex CLI · Hermes Agent.
> Установка `--all` копирует в ~/.claude/skills, ~/.agents/skills, ~/.hermes/skills — а ~/.agents/skills = наше место симлинков скиллов.
> Структура (эталон большого бандла): skills/ (hunt-*, auth-*, recon-* — авто-триггер) + commands/ (/hunt,/recon,/report)
> + engine/ (детерминированный engagement-оркестратор map→route→skill) + eval/ (eval-сьют навыков) + scripts/install.sh --all --burp-mcp.
> Discipline: 5-фазный workflow + 7-Question Gate перед сабмитом (Q3=в scope, Q2=allowed-impact) + evidence-hygiene (редактирование PII/cookies).
> ОТНОШЕНИЕ К ТРИАДЕ: DSH=горизонталь runtime, KWP=вертикаль роли, BugHunter=вертикаль домен (security). Наш ai-defender=defensive, BugHunter=offensive/authorized → КОМПЛЕМЕНТАРНЫ.
> ДОКАЗЫВАЕТ: SKILL.md-экосистема кросс-харнессная, наши скиллы уже совместимы с OpenCode; engine/+eval/ = наши /goal + eval_gate.sh в зрелом виде (референс-архитектура).
> ⚠️ ОФФЕНСИВ-ИНСТРУМЕНТ: применимость у нас СТРОГО defensive (аудит своих репо как ai-defender, CTF, авторизованный пентест). Не направлять на чужие ассеты без письменного разрешения. Учитывать Anthropic CVP-ограничения.

- [ ] **BH-1.** [предложено автором] Изучить структуру бандла (skills/ + engine/ + eval/) как РЕФЕРЕНС для наших бандлов — забрать паттерн engagement-оркестратора (map→route→skill) и eval/ навыков. VERIFY: не копировать оффенсив-содержимое, только архитектуру пакетирования.
- [ ] **BH-2.** Сопоставить с нашим `ai-defender` (defensive): что из discipline-слоя BugHunter переносимо в ai-defender (7-Question Gate, evidence-hygiene, per-class чек-листы OWASP) без оффенсив-части.
- [ ] **BH-3.** Проверить кросс-харнесс совместимость: наши скиллы (symlink в ~/.agents/skills) грузятся тем же движком, что BugHunter — подтвердить, что формат SKILL.md у нас валиден для OpenCode (регресс-тест при обновлении скиллов).
- [ ] **BH-4.** [ГРАНИЦА] НЕ деплоить оффенсив-скиллы (hunt-*, redteam-*) в рабочий стек без явной задачи авторизованного пентеста. При необходимости — изолированный клон + только defensive-применение (аудит своих репо).

### ⚠️ Heretic — авто-снятие safety-alignment с локальных LLM (NEW 14.08.2026, оценка 7/10 — НАБЛЮДЕНИЕ, НЕ ВНЕДРЯТЬ)
> Источник: https://github.com/p-e-w/heretic (Philipp Emanuel Weidmann, 27.6k★, AGPL-3.0). ВНЕ ТЕМЫ триады (DSH/KWP/BugHunter): не harness/плагины, а инструмент УРОВНЯ МОДЕЛИ.
> Суть: автоматическое «decensoring» transformer-моделей локально без дообучения. Метод = directional ablation (abliteration, Arditi 2024)
> + TPE-оптимизатор (Optuna), минимизирует refusals + KL-дивергенцию. 20-30 мин на RTX 3090; >5000 моделей в HF. Research: визуализация residual-векторов (PaCMAP).
> ЛИЦЕНЗИЯ AGPL-3.0 (copyleft) — форк/использование в сервисе обяжет раскрывать исходники.
> ОТНОШЕНИЕ К СТЕКУ: трогает Model в `Agent = Model + Harness`. Наш стек = легитимные провайдеры (OmniRoute→OpenRouter/DeepSeek/Anthropic), безопасные агенты.
> ⚠️ ЖЁСТКАЯ ГРАНИЦА: НЕ использовать для обхода safeguards провайдеров, для клиентских продуктов (AVM/Angela/боты) или запрещённого контента — нарушает ToS и политику ai-defender.
> ЛЕГИТИМНО ТОЛЬКО КАК: (1) research-контекст для ai-defender (model-security awareness: как модель можно развыровнять), (2) интерпретируемость/abliteration как НИОКР изолированно, на СВОИХ моделях, не для деплоя.

- [ ] **HTC-1.** [НАБЛЮДЕНИЕ] Не внедрять в рабочий стек. Засветить как reference в ai-defender: понимать вектор «развыравнивания» моделей (model-security), чтобы детектить/учитывать в аудитах. VERIFY: не копировать код (AGPL — заражает наш репо при линковке).
- [ ] **HTC-2.** [ГРАНИЦА] Если понадобится НИОКР по интерпретируемости (residual directions, abliteration) — только изолированный клон вне freelance-2026, на своих моделях, без деплоя и без снятия guardrails у моделей в проде. Запрет на uncensored-модели в клиентских агентах.

### 🌐 Agent-Reach — capability layer доступа агента к интернету (NEW 14.08.2026, оценка 8.5/10 — взять паттерн fallback + соц-листенинг)
> Источник: https://github.com/Panniantong/Agent-Reach (Panniantong, 71.7k★, MIT). ВОЗВРАТ К ТЕМЕ плагинов/скиллов (после тангенса Heretic).
> Суть: «capability layer, not another tool» — one-click доступ агента к соц/нишевым платформам (Twitter/X, Reddit, YouTube,
> Bilibili, XiaoHongShu, LinkedIn, Facebook, IG, RSS, GitHub, web, search). Делает selection+install+health-check+routing, не чтение.
> КЛЮЧЕВОЙ ПАТТЕРН: ordered backend list (primary + fallbacks) на канал: `twitter.py → twitter-cli ▸ OpenCLI ▸ bird`;
> переключение = переупорядочить список, не переписывать код. `agent-reach doctor` показывает активный backend; бэкенды РЕАЛЬНО прозваниваются.
> КРОСС-ХАРНЕСС: ставится как Skill (`npx skills add Panniantong/Agent-Reach@agent-reach` → SKILL.md), Claude Code/OpenClaw/Cursor/Windsurf.
> MIT, cookies локально, open source, `doctor` = встроенная диагностика. Прокси только для заблокированных сетей ($1/мес).
> ОТНОШЕНИЕ К СТЕКУ: (1) ordered-backend-list+fallback = НАШ PT-1/PT-2 (TwoLayerExtractor HTTP→Playwright) и DSH seam (hot-swap backend);
> (2) SKILL.md кросс-харнесс = наши скиллы; (3) `doctor` = аналог нашего eval_gate.sh; (4) marketplace-ссылка (Agent Skills Hub, 133k security-graded) → закрывает KWP-4 (gap marketplace).
> ВЫИГРЫШ: расширяет соц-листенинг для Sherlock (GEO/конкурент) — Twitter/Reddit/YouTube/XHS, что Firecrawl/MCP не покрывают.
> ⚠️ Внешний Python-пакет с shell-exec + cookie-экспортом → перед установкой аудит ai-defender (зависимости, запись на диск), ADR-002 (прокси только для РФ-заблокированного).

- [ ] **AR-1.** [проверено src → ПРИНЯТО паттерн] Изучить как эталон «capability layer + ordered backend fallback»: валидирует наш PT-1/PT-2 (TwoLayerExtractor) и DSH seam (hot-swap backend). Зафиксировать: переупорядочивание списка бэкендов вместо переписывания кода = наш паттерн рецепт+фолбэк.
- [ ] **AR-2.** Оценить установку как Skill для наших агентов (Sherlock/GEO-соц-листенинг: Twitter/Reddit/YouTube/XHS). VERIFY: аудит ai-defender зависимостей + ADR-002 прокси ДО установки; cookies локально (OK), но проверить что пакет не пишет вне ~/.agent-reach.
- [ ] **AR-3.** Agent Skills Hub (133k security-graded скиллов/MCP) — вход для KWP-4 (marketplace-концепт): оценить как источник проверенных скиллов вместо самописного marketplace.
- [ ] **AR-4.** Перенести идею `doctor` (health-check активных бэкендов) в наш eval_gate.sh / Firecrawl-MCP: явный статус доступности каждого канала перед вызовом (аналог trajectory/verification-before-completion).

### 🎙️ Meetily — privacy-first local meeting assistant (NEW 14.08.2026, оценка 7/10 — референс: local STT+diarization + seam-паттерн)
> Источник: https://github.com/Zackriya-Solutions/meetily (Zackriya-Solutions, 29.1k★, MIT, pre-release). Ракурс: локальное GUI-приложение (не harness).
> Суть: privacy-first AI meeting assistant. Tauri (Rust backend) + Next.js. Локальная транскрипция Parakeet/Whisper (4x быстрее),
> diarization (sortformer), суммаризация на Ollama. 100% local, no cloud, GDPR-by-design.
> КЛЮЧЕВОЕ: model-agnostic provider support = Ollama ▸ Claude ▸ Groq ▸ OpenRouter ▸ custom OpenAI-compatible → DSH seam НА УРОВНЕ ПРИЛОЖЕНИЯ.
> ОТНОШЕНИЕ К СТЕКУ: (1) seam-паттерн = наш OmniRoute (роутинг+fallback) уже реализует; (2) local STT + diarization =
> кандидат на апгрейд голосового пайплайна (Levitan/AVM/Angela); (3) privacy-by-design = ADR-002 + ai-defender (локально для чувствит. аудио).
> ⚠️ Pre-release, GUI-приложение (не агент-инфра), macOS/Win/Linux. Ценно как референс моделей/паттерна, не как готовый компонент.

- [ ] **ME-1.** [проверено src → ПРИНЯТО паттерн] Model-agnostic provider (Ollama/Claude/Groq/OpenRouter/custom) = конкретный DSH seam на уровне приложения. Подтверждает: наш OmniRoute (роутинг+fallback) — правильный seam; зафиксировать как эталон provider-abstraction.
- [ ] **ME-2.** Оценить local STT (Parakeet/Whisper, 4x) + diarization (sortformer) для голосового пайплайна (Levitan/AVM/Angela): транскрипция+диаризация звонков hr-agent/Angela. VERIFY: pre-release зрелость, macOS-build, сравнить с текущим STT (Mango/Whisper). Не деплоить GUI-приложение целиком — только модели/паттерн.
- [ ] **ME-3.** Privacy-by-design (local processing чувствительного аудио) — вынести в ADR-002/ai-defender: аудио звонков клиентов обрабатывать локально, не отправлять в облако (согласно нашей политике прокси/приватности).

### 📚 BookTrans — конвейер LLM-перевода книг (Habr/ruVDS, 14.08.2026, оценка 9/10 — ВЗЯТЬ паттерны интегрити/контекста/инъекций)
> Источник: https://habr.com/ru/companies/ruvds/articles/1070088/ (автор Сергей Каменев) + проект https://github.com/sukamenev/booktrans (PyPI: booktrans).
> Кейс: конвейер перевода книг целиком (EPUB→FB2/PDF) на LLM. ~2 недели разработки с ИИ (Claude Code Opus → AGY Gemini Pro при лимитах).
> 3 агента (claude/codex/agy) через VPS RUVDS. Архитектура = детерминированные python-скрипты + LLM-агенты (роли разделены).
> ПАТТЕРНЫ (прямо проецируются на наш стек):
> 1) ЦЕЛОСТНОСТЬ: стабильный ID + хеш каждого абзаца, ответ обязан вернуть тот же набор → ловит пропуски/склейки/галлюцинации; при несовпадении повтор, после 3 неудач — резервная модель, иначе стоп. = НАШ HT-3 + verification-before-completion + eval_gate.
> 2) СЛОИСТЫЙ КОНТЕКСТ (5 слоёв): мир/стиль(глоссарий) · сюжет(накопит. конспект + периодич. сжатие) · стык(2-3 посл. абзаца) · взгляд вперёд(начало след. фрагмента) · работа. = НАШ claude-mem context injection + trajectory + сжатие.
> 3) НЕДОВЕРЕННЫЕ ДАННЫЕ=ИНЪЕКЦИЯ: текст книги сканируется в разведке на prompt-injection; при находке — стоп до ручной проверки (--force-injected). Защита: Claude --tools "" без MCP, AGY --sandbox, Codex --sandbox read-only + web_search disabled. = ИДЕАЛЬНЫЙ КЕЙС ДЛЯ ai-defender.
> 4) ПРОФИЛИ МОДЕЛЕЙ С ФОЛБЭКОМ НА ЗАДАЧУ: translator/editor/scout/formatter — списки моделей с резервом через разные агенты (Gemini→Claude→GPT). = DSH seam + каскад OmniRoute.
> 5) РАЗДЕЛЕНИЕ РОЛЕЙ (редактор не видит оригинал → нет калек) = Two-axis Review / Fable 5 Advisor. 6) Resumable checkpoints (фрагмент отдельно, рестарт продолжает) = handoff / session resume.
> ПРОВЕРЕНО: читал оригинал статьи, цифры реальные (Bostrom Optimal Timing переведён за $0.00 на подписке, 379 блоков, 3 замечания).

- [x] **BK-1.** [проверено src → ПРИНЯТО] Перенести паттерн целостности (стабильный ID+хеш блока, ответ обязан вернуть тот же набор, auto-retry→резерв.модель→стоп) в наш eval_gate.sh / verification-before-completion. ✅ Verified 14.08: в `tools/trajectory_eval.py` добавлены `seal()` (стабильный block_id b0000.. + sha256-хеш блока) и `verify_integrity()` (replay НЕ проходит, если хеш/длина изменились — детект drift/тамперинга). Тесты в `tests/eval_trajectory.py` PASSED (идентичный replay OK, drift аргумента/длина → FAIL). Эталон HT-3 «у отказа имя + доказательство» соблюдён.
- [x] **BK-2.** Слоистый контекст (5 слоёв с периодич. сжатием накопит. конспекта) — применить к долгим агентам (claude-mem context injection, trajectory_eval): явные слои мир/сюжет/стык/вперёд/работа вместо плоского дампа. ✅ Verified 14.08: `tools/context_layers.py` (LAYERS=[world,story,seam,forward,work], `LayeredContext` с add/compact/auto-compact по threshold + render), eval `tools/tests/eval_context_layers.py` PASSED, добавлен в eval_gate KNOWN_EVALS.
- [x] **BK-3.** [ВЫСОКИЙ приоритет] Untrusted-data injection defense из BookTrans → добавить в ai-defender как шаблон обработки недоверенного внешнего контента (Agent-Reach соц-данные, скрапинг PT, загрузки пользователя): (a) скан на инъекцию в фазе разведки, (b) запуск агента с --tools "" / --sandbox / web_search disabled при обработке недоверенного текста. ✅ Verified 14.08: добавлен плейбук `untrusted_data.md` + смелл `untrusted_to_llm` (MEDIUM) в scan.py; eval PASSED (11 TP, 0 FP), CLI-смоук `agent.run(web_fetch())` → MEDIUM.
- [x] **BK-4.** Per-task model profiles с cross-agent фолбэком (translator/editor/scout/formatter lists) — формализовать в OmniRoute профилях: назначать резервные модели на задачу, а не глобальный каскад (расширить DSH-1 seam + наш FREE_MODELS cascade). ✅ Verified 14.08: `tools/model_profiles.py` (MODEL_PROFILES: translate/edit/scout/format/reason + GLOBAL_FALLBACK, `select_model`/`select_chain` с per-task фолбэком), eval `tools/tests/eval_model_profiles.py` PASSED, добавлен в eval_gate KNOWN_EVALS.

### 🗺️ Harness-ландшафт (Habr-обзор) — синтез + ВАЛИДАЦИЯ нашего стека (NEW 14.08.2026, оценка 9/10 — ПОДТВЕРЖДАЕТ стек)
> Источник: https://habr.com/ru/articles/1070296/ (Данила Поддубный / danyathewriter, 13.08.2026). Обзор категории agent-harness (≈35 живых CLI-агентов на июль 2026).
> КЛЮЧЕВЫЕ ТЕЗИСЫ + ОТНОШЕНИЕ К НАМ:
> 1) Цифра агентного бенчмарка = model+harness, не свойство модели. Честное сравнение = mini-SWE-agent «Bash Only» (только bash, одинаковый промпт). = НАШ DSH-5 Minimal-mode / PT-бейзлайн (изолировать вклад обвязки).
> 2) OpenCode — MIT, ~182k★, 75+ провайдеров, client-server — ЛИДЕР model-agnostic лагеря, прямо назван самым зазвёзженным агентом GitHub. **ЭТО НАШ ОСНОВНОЙ IDE** → выбор подтверждён. ZCode (Z.ai, GLM-5.2) в таблице = НАША ВТОРАЯ IDE из AGENTS.md.
> 3) Hermes Agent (Nous): персистентная память успехов/провалов → генерирует ПЕРЕИСПОЛЬЗУЕМЫЕ СКИЛЛЫ («agent that grows with you»). = ТОЧНОЕ ОПИСАНИЕ НАШЕГО self-improvement / Target B / self_improve_log / claude-mem. ВНЕШНЯЯ ВАЛИДАЦИЯ подхода.
> 4) OpenClaw (Steinberger): «бизнес-модель твоей зависимости = твоя бизнес-модель» — оптимизировал под Anthropic, те за сутки отключили. = НАША ADR-002 (независимость от вендора, прокси, model-agnostic OmniRoute). Открытость MIT = страховка от «выключения письмом».
> 5) ТАЙПСКВОТТИНГ: PyPI `deepseek-harness` от постороннего (совпадает имя `dsh`) — официальный только npm `@deepseek-ai/dsh`. = В ai-defender (supply-chain: проверять источник пакета до установки).
> 6) Code mode / Programmatic Tool Calling (модель пишет программу, в контекст — только print) = наш DSH Code-mode. 7) Omnigent (Databricks) мета-харнесс оркестрирует Claude Code/Codex/OpenCode/Hermes = наша оркестрация (Agent-lab, /goal).
> ТАБЛИЦА ЛАБ: Anthropic Claude Code, OpenAI Codex CLI, Google Antigravity CLI, MS Copilot CLI, xAI Grok Build, Mistral Vibe, Moonshot Kimi Code, Z.ai ZCode, Alibaba Qwen, Amazon Kiro, Tencent CodeBuddy, Nous Hermes, Meta Muse Code, DeepSeek Harness. Model-agnostic: OpenCode/Pi/Goose/Cline/OpenHands/Aider/Kilo/Omp + mini-SWE-agent.

- [x] **HZ-1.** [проверено src → ПОДТВЕРЖДЕНО] OpenCode (наш IDE) = лидер model-agnostic (182k★, 75+ провайдеров); ZCode (Z.ai GLM-5.2) = вторая IDE из AGENTS.md. ✅ Verified 14.08: выбор IDE/харнесса валиден рынком (обзор Habr #1070296). Код-действий не требует; зафиксировано как подтверждённое арх-решение (см. ADR-002 п.2).
- [x] **HZ-2.** Hermes self-improvement (память успехов/провалов → переиспользуемые скиллы) = внешняя валидация нашего self-improvement/Target B/self_improve_log. ✅ Verified 14.08: в SKILL.md self-improvement добавлен раздел «Skill synthesis from observations (HZ-2)» — процедура агрегации рекуррентных паттернов (learning context + claude-mem) → синтез SKILL.md при capability (≥3 задач), фиксация в self_improve_log. Аналог ce-compound (ЦЕ-1).
- [x] **HZ-3.** OpenClaw-урок (выключение подписки Anthropic за сутки) → закрепить в ADR-002: model-agnostic OmniRoute + прокси-независимость = защита от vendor-lock. ✅ Verified 14.08: создан `docs/adr/ADR-002-proxy-policy-russian-services.md` (п.2 «Независимость от вендора»: тезис «бизнес-модель зависимости = твоя бизнес-модель» + model-agnostic OmniRoute + MIT как страховка от kill-switch). Файл материализует ранее упомянутый в AGENTS.md ADR-002.
- [x] **HZ-4.** [ВЫСОКИЙ] Тайпсквоттинг (PyPI deepseek-harness vs npm @deepseek-ai/dsh) → добавить в ai-defender supply-chain чек-лист: проверять официальный источник/организацию пакета ДО установки (npm-орг vs PyPI-дубликат), особенно при совпадении имён команд. Сверить с install-гигиеной (githooks/no-secrets). ✅ Verified 14.08: `scan_typosquat` в deps_scan.py (KNOWN_PACKAGE_SOURCES + edit-distance≤2 к популярным пакетам), вшит в `scan_all`/`--deps`; eval PASSED — PyPI `deepseek-harness`→HIGH, офиц. `@deepseek-ai/dsh`→0 FP; CLI-смоук подтвердил HIGH.
- [x] **HZ-5.** mini-SWE-agent «Bash Only» (честное сравнение моделей) → формализовать DSH-5 Minimal-mode как наш стандарт бенчмарка моделей: один и тот же минимальный tool-набор для сравнения моделей вне вклада обвязки (связать с eval_gate + FREE_MODELS). ✅ Verified 14.08: `tools/model_bench.py` (контракт bash-only + детерминир. верификатор + compare_models), офлайн `--selftest`, eval `tools/tests/eval_model_bench.py` PASSED, добавлен в eval_gate KNOWN_EVALS. Лайв-режим `--live` через OmniRoute (OPENAI_BASE_URL+KEY).

### 📄 llms.txt — валидатор + реальный спрос ботов (Habr #1070334, оценка 8.5/10 — ПОЛЕЗНО, корректирует GEO-приоритеты)
> Источник: https://habr.com/ru/articles/1070334/ (Игорь Новиков / ig_novvv, 23ч назад). Валидатор+генератор llms.txt на 64 тестах + замер реального спроса ИИ-ботов.
> КЛЮЧЕВОЕ (что бьёт в нас):
> 1) **Спрос ботов на llms.txt статистически неразличим**: 408 запросов из 515 млн событий (Limy.ai, май 2026). GPTBot/ClaudeBot/PerplexityBot читают HTML и уважают robots.txt, но файл-карту целенаправленно НЕ запрашивают. Яндекс не заявлял поддержку (ни Алиса AI, ни нейропоиск). = llms.txt = ДЕШЁВАЯ СТРАХОВКА, не primary-рычаг GEO.
> 2) Спецификация (llmstxt.org, Дж. Ховард): H1 первой значимой строкой (ровно 1) → `> Описание` цитатой сразу под заголовком → `## Секции` с буллетами `- [Name](url): пояснение`. `llms-full.txt` — ВНЕ спека, реализации расходятся (не полагаться).
> 3) Архитектура валидатора: `parseLlmsTxt` (парсер, сохраняет ПОРЯДОК — нарушается чаще всего) отдельно от `validateLlmsTxt` (правила). Сеть НЕ трогается — валидируется структура текста, не доступность ссылок.
> 4) Оценка весами: `SEVERITY_WEIGHT={critical:40, high:25, medium:12, low:5}`, score=100−Σвесов. critical=пусто/нет H1; high=описание до заголовка/два H1; medium=битый буллет/посторонний текст в секции; low=http:// вместо https://.
> 5) 22 теста на llms.txt (+64 с микроразметкой/прокси), 43ms. Чек-лист публикации: H1 первый/один, описание цитатой, только буллеты в секциях, ВСЕ ссылки https://, отдаётся как text/plain БЕЗ редиректа (проверка `curl -I`).
> ИТОГ автора: ставить как страховку, НЕ как путь в ответы нейросетей — туда ведёт органика + содержание страниц. Нарушают спеку почти все.

- [x] **LL-1.** [ВЫСОКИЙ] Детерминированный валидатор llms.txt (как наши тулзы, ponytail): `parse_llms_txt(text)` (парсер: title/description/sections/malformed/stray + порядок) отдельно от `validate_llms_txt(text)` (правила со SEVERITY_WEIGHT, score=100−Σ). НЕ трогать сеть. ✅ Verified 14.08: `tools/llms_txt_validator.py` (parse/validate, critical→score 0 по спеке Habr), eval `tools/tests/eval_llms_txt.py` PASSED (edge: пусто/пробелы/CRFL/два H1/описание до заголовка/не-цитата/битый буллет/посторонний текст/http://), в eval_gate KNOWN_EVALS. CLI-смоук: валидный → 100/100, http:// → 95/100 + LOW.
- [ ] **LL-2.** Чек-лист публикации llms.txt для наших проектов (dashboard, freelance-2026 и др. с GEO-фокусом): H1 первый/один, `> Описание` цитатой, только буллеты в секциях, https://, отдача text/plain без редиректа (curl -I). + убедиться, что боты читают HTML и robots.txt (уже ок).
- [ ] **LL-3.** GEO-приоритет: llms.txt = дёшевая страховка, НЕ primary-рычаг. Скорректировать geo-strategy/ai-seo: фокус на органике + содержании страниц + структурир. разметке, llms.txt — опционально и только валидный. Не переинвестировать.
- [ ] **LL-4.** [НИЗКИЙ] `llms-full.txt` — НЕ стандарт, реализации расходуется; не полагаться на него в GEO-паутине наших сайтов. Если делаем — только как опциональный дамп контента, отдельно от llms.txt.

### 🧠 RAG с нуля (Habr #1070662, оценка 8/10 — ПОЛЕЗНО, усиливает smart-rag/claude-mem)
> Источник: https://habr.com/ru/articles/1070662/ (Илья / Darg_vet, 4ч назад). RAG без фреймворков (LangChain/LlamaIndex): Loader→Chunker→Embedder→VectorStore→Retriever→Reranker→LLM.
> КЛЮЧЕВОЕ (что бьёт в наш стек — smart-rag, claude-mem, bot-development):
> 1) **Ретривал = bi-encoder (быстрый top-k) → cross-encoder reranker → финал**. `top_k_retrieve`=30-50 (пул для reranker, НЕ в промпт), `top_k_final`=3-5 (в промпт). Cross-encoder точнее, но не кешируется → только на отобранных кандидатах.
> 2) **Асимметричные префиксы эмбеддинга**: `search_query:` / `search_document:` для nomic-embed-text — трюк точности семантического поиска (запрос и док-т кодируются по-разному).
> 3) **Local-first стек через Ollama**: nomic-embed-text (bi) + ms-marco-MiniLM (cross-encoder) + llama3.1:8b (генерация) = наш ADR-002 (приватность, локальный inference) + OmniRoute (роутинг embed/rerank/generate на локальный Ollama).
> 4) Chunking: fixed (N+overlap) / recursive (separators \n\n,\n,. ,space) + `merge_small_chunks` склейка мелочи до целевого размера — применимо к claude-mem / долгому контексту (BK-2).
> 5) Генерация: инструкция «опирайся только на контекст» снижает галлюцинации = контекст как данные, не инструкции (связь BK-3/untrusted_data).
> 6) VectorStore: in-memory + numpy cosine + pickle + фильтр по metadata.
> Нарушений границ НЕТ (легитный туториал).

- [x] **RAG-1.** [ВЫСОКИЙ] Reranker-стадия в нашем ретривале — `tools/rag_retrieval.py`: `VectorStore` (cosine + metadata-фильтр + pickle) + `rag_retrieve()` (bi-encoder top_k_retrieve → cross-encoder rerank → top_k_final). Eval `tools/tests/eval_rag_retrieval.py` PASSED. **Verified.** (Локальный cross-encoder ms-marco-MiniLM подключается как reranker_fn; см. RAG-3.)
- [x] **RAG-2.** [СРЕДНИЙ] Асимметричные префиксы `search_query:` / `search_document:` — встроены в `embed_query()` / `embed_document()` (`tools/rag_retrieval.py`). Eval TP-6 PASSED. **Verified.**
- [x] **RAG-3.** [СРЕДНИЙ] Local-first RAG-стек зафиксирован как эталонная архитектура — `docs/adr/ADR-004-rag-local-first.md`. Принцип (bi+rerank, асимметричные префиксы, local-first) + модельный выбор (Ollama nomic-embed-text/cross-encoder/llama **ИЛИ** sentence-transformers), согласован с ADR-002 (приватность) и OmniRoute (роутинг/fallback). embed/rerank плагинны. **Verified** (арх. решение, обосновано анти-авторитетной проверкой).
- [x] **RAG-4.** [НИЗКИЙ] Chunking-стратегии — `tools/chunking.py`: `fixed_chunk` (+overlap), `recursive_chunk` (по разделителям \n\n,\n,. ,space + hard-split), с `merge_small_chunks` (склейка до target). Eval `tools/tests/eval_chunking.py` PASSED, добавлен в `eval_gate.sh`. **Verified.** Применять к ingestion claude-mem / долгому контексту.
- [x] **RAG-5.** [СРЕДНИЙ] Инструкция «опирайся только на контекст» — `build_prompt()` в `tools/rag_retrieval.py` с GROUNDING. Eval TP-7 PASSED. **Verified.** Связать с BK-3 (контекст = данные, не инструкции).

### 🧿 LFM2.5-VL-3B — локальная vision-модель (Liquid AI, оценка 9/10 — ПОЛЕЗНО для 8ГБ Mac)
> Источник: https://www.liquid.ai/blog/lfm2-5-vl-3b (Liquid AI, 12.08.2026). 3.1B VLM, SigLIP2 NaFlex 400M, контекст 32K, лицензия LFM Open License v1.0 (open-weight, бесплатно коммерчески до $10M выручки).
> КЛЮЧЕВОЕ (8ГБ Mac): единственная из рассмотренных, что реально влезает локально (~3ГБ RAM, MLX/Apple Silicon). Наши Qwen2.5-7B+0.5B — текст-only, эта ДОБАВЛЯЕТ on-device vision. Не замена, а дополнение.
> Сильна: screen/UI-понимание, grounding (bounding box по NL), function calling (vision+tools), document/OCR с layout, 16 яз. (RU есть). Non-reasoning → низкая латентность, НЕ для сложного рассуждения/long-context (туда 7B/облако). Бенчмарки вендорские.
> ⏸ **ПАУЗА (решение 2026-08-15):** локально модель работает (проверка через `python -m mlx_vlm.generate` CLI). Интеграция в OpenCode (плагин `opencode-image-comprehension` auto-routing) **отложена** — нет текущей необходимости. Рабочий путь: ручное переключение в меню на 👁️ LFM2.5-VL-3B (local vision) либо прямой CLI. Сервер `tools/lfm_vl_server.py` + провайдер `lfm-vl` в `opencode.jsonc` готовы, но не задействованы.

- [x] **LFM-1.** [ВЫСОКИЙ] Локальная vision-модель на 8ГБ Mac — коннектор `tools/vision_local.py` + **OpenAI-совместимый сервер `tools/lfm_vl_server.py`** (MLX ~3ГБ, zero-dep, ленивый mlx_vlm). Провайдер `lfm-vl` добавлен в `~/.config/opencode/opencode.jsonc` → модель **👁️ LFM2.5-VL-3B (local vision)** появляется в меню выбора OpenCode (рядом с Ollama Qwen). ДОПОЛНЕНИЕ, не замена. Eval `tools/tests/eval_vision_local.py` + `tools/tests/eval_lfm_vl_server.py` PASSED. **Verified** (логика; модель прогоняется на Mac, LFM-4). ~3ГБ RAM влезает в 8ГБ с запасом.
- [x] **LFM-2.** [СРЕДНИЙ] Vision-узел для агентов — **авто-маршрутизация скриншотов**: плагин `opencode-image-comprehension` (прописан в `opencode.jsonc`) перехватывает картинку и отдаёт локальной LFM2.5-VL-3B через `lfm_vl_server.py` (бэкенд `omlx` на :8000). Агент остаётся на умной модели, переключать ничего не надо; зрение — локально (ADR-002). Конфиг `~/.config/opencode/opencode-image-comprehension.json` создан. Плюс прямой API `tools/vision_local.py` (`understand`/`detect_objects`). **Verified** (конфиг + сервер-логика). Финал — прогон на живом Mac (LFM-4).
- [x] **LFM-3.** [НИЗКИЙ] Лицензия LFM1.0 подтверждена (web-верификация): open-weight, бесплатно коммерчески до $10M выручки; не Apache. Перед коммерч. деплоем >$10M — вскрыть LICENSE файл. Зафиксировано в `tools/vision_local.py` docstring. **Verified** (web).
- [ ] **LFM-4.** [СРЕДНИЙ] Eval на Mac: прогнать vision-задачи (документ/OCR, screen understanding) на LFM2.5-VL-3B (MLX) → измерить качество/латентность. **Готово:** команда `python -m mlx_vlm.generate --model LiquidAI/LFM2.5-VL-3B-MLX-8bit --image <img> --prompt "..."`; прогон на Mac пользователя. (Требует установки mlx-vlm + веса ~3ГБ — в CI не качаем.)

### 📊 RAG eval set — «честная» оценка retrieval (Habr #1070534, 14.08.2026, оценка 9/10 — КЛЮЧЕВОЙ сиквел к RAG-1..5)
> Источник: https://habr.com/ru/articles/1070534/ (photonchikk, 14.08.2026, туториал, 5.8K, пост серии про RAG). Вердикт: **проверено src → принято**.
> Суть: без своего eval set мы меняем chunking/embedder/reranker вслепую (то, что только что внедрили как RAG-1..5). Три РАЗДЕЛЬНЫХ набора: smoke (20-50, у CI) / ручной eval (100-300, выбирает конфиги) / train (свой holdout — иначе «экзаменационные билеты»). До разметки — 8 срезов-решений (exact entity, перефраз, длинные разделы, таблицы, версии-конфликты, НЕТ ответа, плохая формулировка, чувствительный сценарий). Метрики retrieval (Recall@k, MRR@k, nDCG@k) — ОТДЕЛЬНО от ответа (groundedness/completeness/relevance/correct abstention).
> Схема кейса JSONL: `expected_document_ids` + `gold_evidence` (relevance 0-2) по стабильному document_id/section_id (НЕ chunk_id — chunking меняется и ломает gold), `answerability` (явно хранит «нет ответа»), `expected_facts` (для LLM-as-judge). Порог: 1-2 кейса из 120 = шум (SE ±7.4pp) → парный McNemar/bootstrap, смотреть по КЕЙСАМ и критичным срезам, не по среднему. Runner пишет per-case trace (index_version, retrieved, latency, prompt_version) — иначе метрика бесполезна. ACL/tenant isolation — часть eval-сценариев.
> Маппинг: валидирует и усиливает наш eval-driven подход (AGENTS §9) — текущие `tests/eval_*.py` это smoke-уровень; следующий уровень — ручной eval set по срезам для нашего RAG. Связано: RAG-1..5, ADR-004, validation-layer @validated, OmniRoute (LLM-as-judge).
> Границы: нарушений НЕТ (легитная методология оценки).

- [x] **REV-1.** [ВЫСОКИЙ] Метрики retrieval stdlib-модулем — `tools/rag_metrics.py`: Recall@k, MRR@k, nDCG@k + abstention для среза «нет ответа». Eval `tools/tests/eval_rag_metrics.py` PASSED, в `eval_gate.sh`. **Verified** (независимые эталоны, вручную посчитаны).
- [x] **REV-2.** [ВЫСОКИЙ] Формат кейса JSONL (id, query, scenario, answerability, expected_document_ids, gold_evidence по document_id/section_id, relevance 0-2, expected_facts, source, reviewed_by, dataset_version) + загрузчик-схема `tools/rag_evalset.py` (dataclass EvalCase/GoldEvidence, load_eval_set, validate_case/validate_eval_set, relevance_map). Eval `tools/tests/eval_rag_evalset.py` PASSED, в `eval_gate.sh`. **Verified**.
- [x] **REV-3.** [СРЕДНИЙ] Runner с per-case trace — `tools/rag_evalrunner.py`: `run_eval` (retrieve_fn/answer_fn, trace: case_id, config_id, index_version, retrieved[{id,rank,score}], answer, latency_ms, prompt_version), `summarize` (Recall@k/MRR@k/nDCG@k по срезам + abstention), `check_gates` (порог критичного среза отдельно), `write_report` (JSONL). Eval `tools/tests/eval_rag_evalrunner.py` PASSED, в `eval_gate.sh`. **Verified**.
- [ ] **REV-4.** [СРЕДНИЙ] Baseline smoke-набор (20-50) из реальных проектов (Levitan/ai-scout/claude-mem) + матрица срезов (exact_entity, paraphrase, long_section, tables, versions, no_answer) с квотой ≥10-15 на срез; критичный срез — отдельный порог, НЕ растворён в среднем. **(требует данных из реальных проектов)**
- [ ] **REV-5.** [НИЗКИЙ] Метрики ответа (groundedness/completeness/relevance/abstention) — связать с validation-layer `@validated` и LLM-as-judge (OmniRoute); судью проверить на ручной подвыборке до автооценки.

### 🧰 Claude Code Tips — статус-лайн с токенами (GitHub ykdojo, 15.08.2026, оценка 7/10 — ПРОВЕРЕНО, частично применимо)
> Источник: https://github.com/ykdojo/claude-code-tips (Tip 0: customize status line). Вердикт: **проверено src → принято (паттерн), реализация — через OpenCode-плагины, НЕ скрипт для Claude Code**.

> Суть: скрипт `context-bar.sh` читает session-метаданные из stdin (model, cwd, `context_window.total_input_tokens/output_tokens/window_size`). Для нас ценно: **визуальный контроль расхода контекста/токенов** (цель $20/мес, Tier-каскад).
> Маппинг: OpenCode-аналоги (верифицировано аднтивой): плагин `opencode-statusline` (MIT, sidebar: git-branch/git-diff/custom, конфиг `~/.config/opencode/sidebar.json`) и `opencode-subagent-statusline` (token/context usage субагентов, TUI-plugin). Сигнал: наш стек уже контролирует токены (claude-mem, eval_gate, OmniRoute), статус-лайн добавит **видимость на лету**.
> Границы: нарушений НЕТ (обычные утилиты).

- [ ] **CCT-1.** [СРЕДНИЙ] Прогресс-бар токенов/контекста на лету в OpenCode — подключить `opencode-subagent-statusline` (token/context usage) в `tui.json`, конфиг-minimal; цель — видеть расход контекста в сессии без `/context`. Верифицировать, что токены реально видны (plugin 1.x уже поддерживает).
- [ ] **CCT-2.** [НИЗКИЙ] Sidebar git-статус (ветка/дифф) — плагин `opencode-statusline` + `~/.config/opencode/sidebar.json` (git-branch, git-diff, custom). Взять, если хочется видно ветку/дифф на лету.
- [ ] **CCT-3.** [НИЗКИЙ] Вторая строка «последнее сообщение» — у нас уже есть (chp.md, claude-mem context) — НЕ внедрять, только средствами плагинов.

### 🐝 Buzz — workspace людей+агентов на self-hosted Nostr relay (GitHub block/buzz, 15.08.2026, оценка 8/10 — ВАЛИДИРУЕТ ai-bureau)
> Источник: https://github.com/block/buzz (Block, Inc., Apache-2.0, Rust, 27.5K★, активен). Вердикт: **проверено src → принято (паттерны), развёртывание relay = гипотеза**.
> Суть: self-hosted workspace (Nostr relay), где люди и AI-агенты в одних комнатах. Всё — подписанные события в единый лог: сообщения, патчи (NIP-34), CI, ревью, workflow, git. Агенты = МЕМБЕРЫ с собственными ключами/членствами/аудит-логом (scoped by identity, не permission-флагами). `buzz-cli` (JSON in/out, под LLM tools) + `buzz-acp` (ACP-харнес: Goose/Codex/Claude Code) + YAML-workflows (message/reaction/schedule/webhook). Аудит — hash-chain, FTS-поиск (Postgres). «Вопрос проекту → ответ с ресиптами по 6 мес истории» = агент ищет по своей истории и постит треды.
> Маппинг (ПОДТВЕРЖДАЕТ наш стек): (1) агенты-члены по identity — наш субагент-стек + ai-defender + claude-mem; (2) единый event log + FTS — наш SSoT (ACTIVE_TASKS/chp.md/claude-mem); (3) «ответ с ресиптами по истории» — claude-mem поиск по прошлым сессиям; (4) ACP-харнес — в opencode уже есть ACP Support. Инфра (relay+Postgres+Redis+S3+Docker, Rust) для разворота у нас избыточна → реализация не в приоритете.
> Границы: нарушений НЕТ (Apache-2.0, open-source; ключи агента — паттерн безопасности, усиливающий ai-defender).

- [ ] **BUZ-1.** [СРЕДНИЙ] Паттерн «identity-scoped агенты» в наш ai-bureau: задокументировать правило — каждый агент/субагент с собственным контекстом доступа и аудит-логом своих действий (связать с claude-mem субагентов и ai-defender). Результат — правило в AGENTS/CLAUDE.md + проверка, что subagents уже следуют этому.
- [ ] **BUZ-2.** [НИЗКИЙ] «Ответ с ресиптами»: уточнить конвенцию для агентов — при ответе по истории claude-mem давать источники (id наблюдений), не «гадание». Проверить/усилить инструкции AI-агентов.
- [ ] **BUZ-3.** [НИЗКИЙ] Разворот self-hosted relay как «общей комнаты» ai-bureau — ГИПОТЕЗА: требует relay+Postgres+Redis+S3+Docker. Не внедряем сейчас (избыточно); пересмотреть при нужде в общем рабочем пространстве >1 агента с общим аудит-логом в реальном времени.

### 🎋 Bonsai-27B — extreme-quantized 27B на 8ГБ Mac (Prism ML, 16.08.2026, оценка 6/10 — ГИПОТЕЗА, принято только на гейт-тест)
> Источник: материалы Prism ML / Bonsai (1-bit binary + ternary 2-bit квант, база Qwen3.6-27B). Вердикт: **предложено автором (вендорские бенчи) → принято на ГЕЙТ-ТЕСТ, замена вслепую ОТКЛОНЕНА**.
> Расклад по RAM (пик = веса + KV + буферы, 8ГБ Mac): **1-bit MLX** — веса 4.21ГБ, пик ~5.9ГБ @4K ctx / 6.3ГБ @10K, при 4-bit KV ниже → **влезает впритык** (своп на длинных сессиях). **Ternary MLX** — диск 8.49ГБ, пик **9.2ГБ @4K** → **НЕ влезает в 8ГБ** (граница).
> Сильные стороны (1-bit): math 91.7 / coding 81.9 / LiveCodeBench 76.4 / IFEval 79.1 / BFCL v3 70.7 — заявленный уровень выше нашего Qwen2.5-7B. Δ: reasoning 27B-класса в ~6ГБ.
> КРАСНЫЕ ФЛАГИ: (1) агентное кодирование (long-horizon run-test-repair) — в limitations явно указано как слабое место → code-агентам оставить OmniRoute; (2) tool calling (BFCL 70.7) ниже ternary (74.4) и ниже облака — проверять на РЕАЛЬНЫХ агентных сценариях; (3) бенчи ВЕНДОРСКИЕ (Prism ML); (4) нужен КАСТОМНЫЙ MLX-форк Prism ML (не стандартный mlx-lm) — совместимость с нашей интеграцией (по образцу `lfm_vl_server.py`) проверить; (5) русский язык — тестировать.
> Границы: замена только ЛОКАЛЬНОЙ текстовой Qwen2.5-7B на reasoning-задачи; НЕ для кодинг-агента, НЕ для tool-heavy без реального прогона. Облачный контур (OmniRoute) не трогаем.
> PDF/binary официальной модели не читается по правилу 0.1 — только md/статьи/web + реальные прогоны.

- [ ] **BN-1.** [СРЕДНИЙ] Гейт-тест на Mac: поставить MLX-форк Prism ML, скачать 1-bit MLX (~5.1ГБ), поднять OpenAI-совместимый сервер (по образцу `lfm_vl_server.py`), измерить tok/s + пик RAM (4K/10K ctx) + русский + краткий tool-calling сценарий (BFCL-light). Критерий принятия: пик <7ГБ при 10K ctx и RU tool-колл реально работает. Вендорские бенчи НЕ считать подтверждением без этого прогона.
- [ ] **BN-2.** [СРЕДНИЙ] Если гейт прошёл: замена Qwen2.5-7B на Bonsai 1-bit в локальном слое для reasoning-задач (обзвон/суммари/извлечение). Откат на Qwen2.5-7B при регрессии eval (`eval_gate.sh`). Кодинг-агенты и tool-heavy остаются на облаке.
- [ ] **BN-3.** [НИЗКИЙ] Ternary-вариант — граница: пик 9.2ГБ > 8ГБ RAM. НЕ внедряем на текущем железе; пересмотреть при машине ≥12ГБ или после BN-1, если качество 1-bit не хватит (тогда поднять бюджет RAM, не модель).

### 🎞 GitHub Weekly #283 — digest 5 OSS-проектов (видео AI Agents Studio, 16.08.2026, оценка 7/10)
> Источник: https://www.youtube.com/watch?v=8V348y_VYZ4 (видео-обзор, ID #283). Вердикты по каскаду ADR-003 (каждый факт верифицирован по GitHub/сайтам, НЕ из видео): **Needle 2 → принято (паттерн)**; **Cursor Plugins → принято (валидация стека + паттерн cli-for-agent)**; **Orca → принято (инструмент, гипотеза)**; **RustDesk → граница**; **PartMode → граница**.
> Суть (кратко): (1) **Needle 2** — cactus-compute/needle, 5.8K★, MIT, `pip install cactus-needle`: 45M-параметров, 14MB-бинарь (CQ2-bit), ~28MB RAM на сессию, tool calling + structured extraction, byte-level grammar по JSON-схемам, confidence-gated (порог → эскалация), tool retrieval (топ-5 инструментов/ход), sliding window 256 токенов (KV sinks). Live BFCL v4 (офиц. скорер): overall 61.7 vs FunctionGemma-270M 60.8 / Apple FM 46.1, well-formed 95.0. Папір: Simple Attention Network (arXiv:2607.18363). Focus: <$200 девайсы без GPU/NPU — нашим Mac он не нужен по мощности, но как **дешёвый локальный слой для извлечения структур** (инвойсы, сущности, поля) — реальный кандидат: себестоимость ~0, приватность локально.
> (2) **Cursor Plugins** — cursor/plugins, 2.9K★, MIT: официальная спека: plugin = директория с `.cursor-plugin/plugin.json` + `skills/`(SKILL.md) + `rules/`(.mdc) + `mcp.json`. **Валидирует наш OpenCode-стек** (мы уже так живём). Ценные плагины-паттерны: `cli-for-agent` (CLI, который агент надёжно вызывает: flags, help-с-примерами, pipelines, errors, idempotency, dry-run), `thermos` (branch review: security-аудит + параллельные сабагенты), `orchestrate` (fan-out на параллельные облачные агенты с planners/workers/verifiers/handoffs — у нас это субагенты + Handoff), `continual-learning` (incremental transcript → AGENTS.md — у нас claude-mem), `pr-review-canvas`.
> (3) **Orca** — stablyai/orca, 45.7K★, MIT, YC-backed: «The worktree IDE for AI coding agents» (ADE). Изолированные **git worktrees на задачу**, параллельные агенты (Claude Code/Codex/**OpenCode**/Gemini и др.) рядом, терминал Ghostty-класса (WebGL, splits, restore on restart), Design Mode (встроенный Chromium: клик по UI-элементу → HTML/CSS/скриншот в агента), GitHub/Linear native, remote worktrees по SSH, мобильный компаньон (iOS/Android), CLI + MCP/hooks/skills. **Поддерживает OpenCode напрямую**.
> (4) **RustDesk** — 120K★, AGPL-3.0, Rust: self-hosted remote desktop (NAT traversal, codecs, шифрование). Для нас **граница**: доступ к VPS по SSH, GUI-удалённый рабочий стол не нужен; AGPL (не смешивать с закрытым кодом).
> (5) **PartMode** — BOMWiki/partmode, GNU AGPL v3: local-first параметрический **browser CAD**. Граница: CAD-задач в нашем стеке нет.
> Маппинг: Needle 2 → бесплатный локальный слой извлечения вместо облачных вызовов (Tier-каскад); Cursor plugins → наши AGENTS/openagent скиллы; Orca → вкладка «мультиагент» поверх OpenCode (worktree-изоляция); RustDesk/PartMode — без внедрения.
> Границы: реализацию только после «да»; Orca = обёртка поверх нашего стека, НЕ замена; RustDesk/PartMode не трогаем.

- [ ] **ND-1.** [СРЕДНИЙ] Needle 2 как локальный слой извлечения структур — `pip install cactus-needle` (14MB, ~28MB RAM, `needle playground` :7860 или `agent.run`/`extract`), прогнать против FREE-моделей и Qwen2.5-0.5B на extraction-срезе (JSON-поля из текста; взять куски из REV-4-данных, когда будут). Критерий принятия: структурная точность ≥ наших облачных на срезе И себестоимость ≈0 локально → встраиваем в рутинные extraction (спам-парсинг, сущности из текстов).
> **ℹ️ РЕЗУЛЬТАТ ГЕЙТА (16.08.2026): НЕ ПРОЙДЕН — отказ называется.** Артефакт `tools/tests/eval_needle_extraction.py` (6 кейсов: invoice/contact/order, RU/EN). Needle 2+Literal-enum — **75%** (12/16), без enum — 69%; **Qwen2.5-0.5B (baseline) — 81% (13/16)** — наш текущий локальный слой стабильнее. Провалы RU: `vendor`≈«от ООО», `name` тянет должность, `phone»/«тел», дата-нормализация в ISO. Enum констрейнт (Literal) работает и возвращает `status` корректно. Вердикт: на текущем срезе Needle НЕ заменяет Qwen2.5-0.5B для RU-extraction. В `eval_gate.sh` НЕ вшит (гейт красный). Eval оставлен как артефакт для повторных прогонов; повторная оценка — если появится REV-4-данные или обновится модель.
- [x] **CP-1.** [НИЗКИЙ] Паттерн `cli-for-agent` (cursor/plugins) → наш чек-лист для скриптов, которые вызывает агент: flags, `--help`-с-примерами, pipelines, явные ошибки, идемпотентность, dry-run. Результат — раздел в AGENTS.md или в `workflow`-скилл. (У нас частично есть; формализовать.)
> **ℹ️ РЕЗУЛЬТАТ (16.08.2026): ЗАКРЫТО Verified (исправленная запись).** Чек-лист `## CLI для агентов (CP-1)` добавлен в **проектный** `AGENTS.md` (корень воркспейса, читается и OpenCode, и ZCode/Claude-стеком) — 7 пунктов (flags, --help-с-примерами, --dry-run, идемпотентность, явные ошибки, pipeline-safe, путь к проекту). SSoT: правило действует там, а не только в OpenCode-конфиге; SLOT для обеих IDE. Ранеешнюю запись «уже внедрено в ~/.config/opencode/AGENTS.md» отменяю — в глобальном файле чек-листа не было (ошибка верификации).
- [x] **CP-2.** [НИЗКИЙ] `continual-learning` (transcript→memory) — проверить, что наш claude-mem покрывает; доп. правило не нужно = **валидация** (закрыть без работы, если по критерию совпадает).
> **ℹ️ РЕЗУЛЬТАТ (16.08.2026): ЗАКРЫТО Verified — claude-mem подключён к ОБЕИМ IDE.** Проверено: плагин `claude-mem@thedotmack` 13.3.0 активен в ZCode (`~/.claude/settings.json` → `enabledPlugins: true`), marketplace-каталог на месте, hooks (Setup/SessionStart/UserPromptSubmit) зарегистрированы, `CLAUDE_MEM_RUNTIME=server-beta` в `~/.claude-mem/settings.json` → ZCode пишет в тот же Postgres-бэкенд (:37878), что и OpenCode. В ZCode MCP подключается через плагин, а не через `mcpServers` `.claude.json` (поэтому там пусто — норма). Ранеешняя пометка «MCP только в opencode.jsonc» — ОШИБКА, снята.
- [ ] **OR-1.** [СРЕДНИЙ] Orca — ГИПОТЕЗА: поставить и попробовать fan-out одной задачи на параллельные сессии OpenCode/Codex в изолированных worktrees (Design Mode + моб.компаньон как бонус). ВНИМАНИЕ: 8ГБ Mac — проверить RAM-профиль; не менять наш основной стек (OpenCode + claude-mem + OmniRoute остаются SSoT), Orca = опциональная обёртка для мультиагента.
> **ℹ️ УТОЧНЕНИЕ (16.08.2026): ценность снижена.** OpenCode уже имеет нативные `/experimental/worktree` (create/list/reset/remove) — изоляция worktree-per-task доступна без Orca (реализовано в OR-2). Orca остаётся опциональной обёрткой: ценность = GUI (Design Mode, моб.компаньон) и мульти-CLI-харнес (Claude Code + Codex + OpenCode рядом). Решать только при реальной нужде в GUI-мультиагентности; RAM-гейт 8ГБ обязателен.
- [x] **OR-2.** [НИЗКИЙ] Перенести core-паттерн worktree-per-task в наш ручной workflow — правило, когда фан-аут по git worktrees выгоднее последовательных субагентов одного сеанса (большие параллельные ветки: промпт → 2-3 worktree → merge победителя).
> **ℹ️ РЕЗУЛЬТАТ (16.08.2026): ЗАКРЫТО Verified.** Правило «Worktree-per-Task (OR-2)» добавлено в **проектный** `AGENTS.md` (видят обе IDE) — раздел с нативным `git worktree add/remove` + упоминание OpenCode-обёртки `/experimental/worktree`; звено Handoff сохранено. Для ZCode/Claude-стека работает через нативный `git worktree`, для OpenCode — через `/experimental/worktree`.
- [ ] **RD-1.** [НИЗКИЙ] RustDesk — **граница**: self-hosted remote desktop не нужен (SSH + OmniRoute); AGPL. НЕ внедряем. Закрыто как вердикт.
- [ ] **PM-1.** [НИЗКИЙ] PartMode (browser CAD) — **граница**: CAD-задач нет. НЕ внедряем. Закрыто как вердикт.

---

- *"Продолжаем! Давай деплоить мультиагентную систему Angela"*
- *"Погнали тестировать A/B промпты"*
- *"Запусти SQLite логирование"*
- *"Настрой HH.ru бота и запусти автопоиск"*
- *"Покажи статистику HH.ru агента"*
- *"Запусти пилот x.ai Voice Agent"*
- *"Сравни baresip vs x.ai на 10 звонках"*

Отдыхай, система сохранена! 🛠️
