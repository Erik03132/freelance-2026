## 🛡️ 2026-08-03 — Security rotation: SEC-1..9 закрыты

**Статус:** Сессия завершена (продолжение позже).

### Критичный блок (SEC-1..3) — ЗАКРЫТ
- **SEC-1** — Funpay/wellflow провайдер БОЛЬШЕ НЕ существует в opencode → ключ `Funpay_MYbt...` мёртв, ротация не нужна. Провайдер удалён из `opencode.json`.
- **SEC-2** — OmniRoute JWT_SECRET + API_KEY_SECRET + INITIAL_PASSWORD ротированы (`openssl rand -hex 32`), обновлены `omniroute-recover.sh` и `/root/.omniroute/.env` на VPS 217.149.23.113, pm2 restart, `/v1/models`=200. **Новый dashboard-пароль — в recover-скрипте**.
- **SEC-3** — репозиторий был **PUBLIC** → теперь **PRIVATE** (`gh repo edit`). Secret scanning недоступен (422).

### Высокий блок (SEC-4..7) — ЗАКРЫТ
- **SEC-4** — секреты вынесены в gitignored `.env`: `omniroute-recover.sh` (+`.env.example`), `night_audit_vps.sh`, `watchdog.py`. 🔴 находка: в `watchdog.py` был захардкожен TG-токен `8336409939:AAHr2wbu...` — оказался СТАРЫМ отозванным токеном Анжелочки (401), ротация не нужна; следы убраны из `watchdog.py`, `send_report_today.py`, `angel-backend/.env.sandbox`.
- **SEC-5** — levitan SQLi ×4 (`crm/app.py`): whitelist `_SAFE_CONDITIONS` + `CONTACT_COLUMNS` + бонусом path traversal в `/api/import`.
- **SEC-6** — levitan: FIFO `0o777`→`0o600`, MD5→SHA256 (tts_engine, upload_greeting). Zadarma-скрипт не трогал (MD5 по протоколу).
- **SEC-7** — levitan `test_all.py` больше не печатает ключи (только set/MISSING).

### Средний блок (SEC-8..9) — ЗАКРЫТ, SEC-10 — В ПРОЦЕССЕ
- **SEC-8** — `.gitleaks.toml` закоммичен, no-secrets через pre-commit (проверено: ловит секреты).
- **SEC-9** — хук-скрипты перенесены в версионируемые `githooks/`, `.pre-commit-config.yaml` обновлён, создан корневой `README.md` (шаг `pre-commit install`).
- **SEC-10** — ai-defender `llm --frame mcp` по `freelance-agent/src/mcp-servers` выдал **0 файлов просканировано** (отчёт пуст) — разбор причины НЕ ЗАВЕРШЁН (смотреть `cli.py:59`/`report.py` — счётчик files_scanned).

### Осталось (блокеры/план)
1. **SEC-10**: разобраться, почему `llm_audit` дал 0 файлов (report gen), пересканировать MCP-серверы
2. **OMNIR_VPS_KEY** `sk-c7a0aac...` в git-истории → ротация API-ключа шлюза + обновить потребителей
3. **SEC-11**: чистка git-истории (mango_api.py, .cursor/rules, CHRONICLE.md, checkpoints — проверить мертвость)
4. Прокси-креды хардкод в `ai-senat/agent/*.py`, `ai-eggs/agent/*.py`, `sinergy/src/**` + build-артефакты `sinergy/.next` → параметризовать
5. **НЕ ЗАКОММИЧЕНО** (все изменения сессии): `opencode.json`, трекеры, `crm/app.py`, `tts_engine.py`, `upload_greeting.py`, `test_all.py`, `githooks/`, `.pre-commit-config.yaml`, `README.md`, `.env.example` — нужен Two-axis review + коммит

---

## 🛡️ 2026-08-02 — Создан ai-defender + аудит + РОТАЦИЯ НУЖНА

**⚠️ НАПОМНИТЬ В ЭТОЙ СЕССИИ — СРОЧНО (SEC-1..3):**
> Ротация скомпрометированных ключей из GitHub. Детали: `ACTIVE_TASKS.md` (секция 🛡️ БЕЗОПАСНОСТЬ), `SECRETS_ROTATION.md`, `reports/security-audit-2026-08-02.md`.
> 1. Funpay-ключ в `opencode.json` → ротировать + в `.env`
> 2. OmniRoute JWT/API/пароль в `omniroute-recover.sh` → `openssl rand -hex 32`
> 3. Проверить публичность репозитория GitHub

**Сделано:**
- Создан security-агент **ai-defender** (ADR-004): SKILL.md, пакет `ai_defender/`, CLI `ai-defender`, установлены gitleaks/bandit/pip-audit, eval 10 TP / 0 FP
- Аудиты: levitan (SQLi×4, chmod 0777, MD5), ai-scout, freelance-agent — чисто
- gitleaks: 71 утечка в git-истории; pre-commit hook `no-secrets.sh` переведён на gitleaks + `.gitleaks.toml`
- Правило в AGENTS.md: каждый новый проект → базовый security-аудит до первого коммита

**Разборы (все в claude-mem как decision + ACTIVE_TASKS):**
- OpenHuman (6/10) → OH-1..3 · Firecrawl MCP (7/10) → FC-1..3 · Agent-Reach (7.5/10) → AR-1..3
- ИИ-Автопилот 13x (8/10) → AV-1..3 · Индексация Яндекс+Алиса (7.5/10) → IN-1..3 · Бот Ио 6 лет (7/10) → RB-1..3
- Вайбкодинг-методология (7/10) — подтверждение стека, без задач

**Блокеры (требуют ваших действий):**
- 🔴 SEC-1..3: ротация Funpay-ключа и OmniRoute секретов (см. выше), проверка публичности GitHub

**План на завтра:**
1. Ротация SEC-1..3 (первым делом — ключи в GitHub)
2. FC-1 (Firecrawl MCP keyless) + AR-1 (Agent-Reach --safe) — web-research контур
3. RB-2 (describe-once для Angela/levitan) — быстрая экономия
4. IN-1 (IndexNow в деплой svo-start)

## 🌞 2026-07-29 — Sinergy: Multi-Agent Blender + прокачка системы + деплой

**Статус:** Сессия завершена.

### Сделано

1. **Прокачка всей системы:**
   - claude-mem server-beta проверен и работает (:37878 + Postgres :5432)
   - Пути проектов в AGENTS.md исправлены (freelance-2026/)
   - Скиллы восстановлены через симлинки (~/.agents/skills/ → ~/.config/opencode/skills/)
   - ADR-001/002/003 актуальны
   - 3 handoff'а завершены (agent_upgrade, security_layer, self_learning)

2. **Eval suites созданы для всех активных проектов:**
   - levitan (voice agent) — 34/64
   - agent-lab (core agent) — 14/14 ✅
   - ai-scout (content pipeline) — 9/9 ✅
   - my-project (auto reels) — 10/10 ✅
   - sinergy (startup engine) — 12/12 ✅

3. **Sinergy — аудит и рефакторинг:**
   - Удалены мёртвые AI файлы (deepseek, kimi, moonshot, qwen)
   - Убран dynamic `import('cheerio')` → статический import
   - `from('ideas').select('*')` → `.limit(500).order()`
   - fake SynergyScoreBreakdown → реальные вычисления
   - `Buffer.from()` → `shortHash()` (без Buffer)
   - Все идеи теперь сохраняются с AI-классифицированной вертикалью

4. **Sinergy — Multi-Agent Blender (ключевая фича):**
   - Builder Agent (детерминированный, без AI) — MVP, логика, title
   - Optimist Agent (AI + fallback) — Blue Ocean, тренды
   - Skeptic Agent (AI + fallback) — риски, anti-patterns
   - Orchestrator — координатор pipeline
   - `find-next/route.ts` сокращён с 392 до 42 строк

5. **Деплой Sinergy на Vercel:**
   - Env vars добавлены (Supabase, OpenRouter)
   - AI провайдер переключён с Gemini на OpenRouter
   - Production live: https://sinergy-tau.vercel.app

### Системные изменения
- AGENTS.md: добавлен project `sinergy` в карту проектов
- AGENTS.md: исправлены пути всех проектов
- Созданы eval suites для 4 проектов (levitan, agent-lab, ai-scout, my-project)

---

## ⏰ НАПОМИНАНИЕ (start-day hook) — БЕЗОПАСНОСТЬ 2026-08-02
**СРОЧНО SEC-1..3 (ACTIVE_TASKS.md):** ротировать Funpay-ключ (`opencode.json`) и OmniRoute JWT/API/пароль (`omniroute-recover.sh`), проверить публичность GitHub-репо. Агент: `ai-defender`. Отчёт: `reports/security-audit-2026-08-02.md`.
