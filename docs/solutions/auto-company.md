# Auto Company — полностью автономная AI-компания 24/7

**Что:** репозиторий `MaxMiksa/Auto-Company`. 2 563★ / 401 форк / 8 открытых issue / 502 коммита от 1 автора (Max Kong), создан 12.02.2026, последнее пуш 20.05.2026 — архитектура зрелая, активность затухает (нет коммитов с мая). Реальные файлы: `CLAUDE.md`, `PROMPT.md`, `Makefile`, `scripts/core/auto-loop.sh`, `.claude/agents/*.md` (14 файлов), `.claude/skills/team/SKILL.md`, `dashboard/server.py`, `tests/test_dashboard_server.py`, `projects/snapog/`. Лицензия: MIT (указана в README и `package.json`), но **в корне нет LICENSE-файла** (GitHub API `/license` вернул null) — для корпоративного использования требует прояснения (см. риски).

**Суть (метод за 1 минуту):** автономная AI-компания, которая будит LLM-CLI (Claude Code или Codex CLI) по кругу каждые ~30 сек, читает `memories/consensus.md` как «батон» между циклами, набирает 3–5 агентам из 14 персонажей (Бізнес, Продакт, Інжинірінг, Бізнес, Розвідка) и шипить: досліджуй → пиши → деплой → маркет → оновлюй консенсус → спи → повтори. Кожен цикл — один CLI-визов, стан зберігається лише в `consensus.md` + `.auto-loop-state`. Має дашборд (Python stdlib `http.server`), macOS launchd / WSL systemd --user daemon, Windows PowerShell-оркестратор, 30+ навушків під дослідження/бізнес/інжинір/маркетинг/безпеку. Головний продукт у репо — `projects/snapog` (генератор Open Graph зображень на Cloudflare Workers + D1 + R2, `$0/$19/$49` тарифи).

**Вес (диск):** ~2.5 МБ репо (без `projects/snapog/node_modules`), зависимости: Python 3 (dashboard), Node.js 18+ (snapog, skill-creator), wrangler CLI, make, jq. Для Мака — нативно, на VPS — контейнер (Docker не фіксований явно, но WSL-орієнтован). Потребує quota Claude Code / Codex CLI щоразу коли працює.

**Когда юзать у нас:**
| Слой / Сценарій | У нас применимо для |
|---|---|
| Стратегічний цикл (CEO/CTO/Critic) | Шерлок (пріоритизація, PR/FAQ), Angela (мета-аналіз рішень) |
| Дослідження + критичне мислення | AI-Scout (competitive-intelligence, deep-research pipeline) |
| Автономне тестування + QA | Ботман (QA-боты), кворки для МСБ |
| Дашборд + daemon оркестрация | Інфра (как образец моніторингу loop-агентів) |
| Snapog (OG-images API) | Маркетинг-агенти, контент-платформи — як приклад ship-демо |
| Скилли (deep-research, financial-unit-economics, security-audit) | Бібліотека промптів/скилів, що можна адаптувати під наші агентів |

**Конкретные правки в нашей системе:**
1. **Шерлок** — добавить `scripts/core/auto-loop.sh` как эталон паттерна «autonomous daemon loop» в каталог `docs/patterns/`; позичити `consensus.md`-релей для наших автономних агентів (file: `shuttle/AGENTS.md` → секція cross-cycle state).
2. **Кулибин** — підхопити `.claude/agents/ceo-bezos.md`, `critic-munger.md` як рольові промпти для наших продуктових агентів; файли `.claude/agents/*.md` — ready-to-use, треба адаптувати під наш контекст без прямої копії.
3. **Angela** — інтегрувати `.claude/skills/team/SKILL.md` як шаблон команди (spawn 3–5 subagents, `docs/<role>/` outputs, consensus baton) — це вже майже наш пайплайн "паралельних експертів".
4. **Ботман** — взяти `tests/test_dashboard_server.py` (unittest-покриття dashboard server) як еталон TDD для наших серверних компонентів; покрити її модулі подібними тестами.
5. **Агент-браузер** — `agent-browser/SKILL.md` + шаблони `capture-workflow.sh`/`form-automation.sh` — забрати як готовий скриптовий інструментарій для парсингу/автоматизації (без Docker, чистий shell+curl).

**Риски/ограничения (экспертиза, авг-2026):**
1. **Лицензия — «не указана явно».** README говорит MIT, но в корне нет `LICENSE` файла (curl LICENSE → 404). SPDX:license identifier в `package.json` есть (`"license": "MIT"`), но для корпоративного использования требует прояснения — сперва добавить LICENSE-файл в копию или договориться с Max Miksa.
2. **Автономность без «kill switch» на уровне агента.** `CLAUDE_PERMISSION_MODE=bypassPermissions` + правила «не жди человека» — мощно, но опасно. Без ручного апрува на destructive действия (gh repo delete, wrangler delete, rm -rf) любой баг в промпте может навредить. Наше правило «авто=бан» (см. memory) напрямую конфликтует с философией репо — адаптировать нужно с нашей блокировкой на критичные операции.
3. **Единая точка отказа — consensus.md.** Всё состояние компании в одном файле. Нет транзакционности, нет roll-back на уровне БД. Конфликт циклов маловероятен (один CLI-вызов за раз), но при повреждении `consensus.md` теряется весь прогресс. Добавить версионирование/бэкап (auto-loop.sh уже делает `consensus.md.bak`, но это хрупко).
4. **Монолит-промпт, не true microservices.** `.claude/skills/deep-research/SKILL.md` — 33 KB монолит + 14 справочников по 6–18 KB; `security-audit/SKILL.md` — 2.7 KB без бинарника. Навуши «симпатичные», но тяжёлые для холодного старта агента.
5. **Активность затухает.** Последний коммит май 2026, 1 автор, открытых issue 8 — проект в maintenance-режиме. Некоторые скиллы (например, `deep-research/SKILL.md` с references) могут быть не синхронизированы с последними практиками 2026.
6. **Cloudflare-зависимость snapog.** `projects/snapog` жёстко привязан к Workers/D1/R2 — для нашей инфраструктуры (VPS, TimeWeb) это не прямой путь без переписывания на наш стек.
7. **Безопасность скиллов.** `security-audit/SKILL.md` ссылается на `agents: [yokay-security-scanner]` — агентов нет в репо (не установлен); остальные скиллы не имеют автономного бинарника — это промпт-ориентиры, не автономные инструменты.

**Статус:** кандидат на адаптацию (не инлайн как есть). Лучшее применение — как набор паттернов, промптов и скиллов, а не как скопированный продукт. Snapog отдельно — готовый к ship продукт.

**Следующие шаги (предлагаю, не делаю без команды):**
1. Добавить LICENSE в копию репо или зафиксировать решение «MIT без файла — договорённость с мейнтейнером».
2. **ПИЛОТ (рекомендуется начать здесь):**
   - **Файл #1 ✅ ДОСТАВЛЕН** — `.claude/skills/team/SKILL.md` → `skills/expert-council-adapter/SKILL.md` (spawn 3–5 субагентов, `docs/<role>/`, consensus baton). Зарегистрирован в Hermes + `skill-router.md`.
   - **Файл #2** — `.claude/skills/deep-research/SKILL.md` + `.claude/skills/competitive-intelligence-analyst/SKILL.md` → «мозг» Шерлока: 8-фазный исследовательский пайплайн с citation tracking.
   - **Файл #3** — `.claude/skills/financial-unit-economics/SKILL.md` + `.claude/agents/cfo-campbell.md` → финансовая гигиена Маркетолога/Финансиста (LTV:CAC, ценовая модель,拉面盈利).
3. Пробежаться по `tests/test_dashboard_server.py` как шаблону — накидать покрытие на наш `dashboard/server.py`-аналог.
4. Оценить `snapog` как демонстрационный кейс ship (если нужен пример продукта для клиентов Kwork).
5. Запустить `make dashboard` на Маке и посмотреть дашборд вживую (порт 8787 по умолчанию) — чтобы решить, брать ли сервер как есть.

**Что я НЕ буду делать без явного «да»:**
- Клонировать/форкать репо локально и запускать `make start` / `make install` — это потребует quota Claude/Codex и запускает фоновый daemon; репо сам по себе не знает о нашем «авто=бан».
- Редактировать `.claude/agents/*.md` или `CLAUDE.md` в оригинальном репо (запись в чужой репо без ветки/PR — стирает историю).
- Устанавливать `@anthropic-ai/claude-code`, `@openai/codex`, `wrangler` глобально — это подписки/квоты, которые должны быть явно утверждены.
- Привязывать `projects/snapog` к нашему VPS без переписывания на наш стек (Cloudflare Workers ≠ TimeWeb).
- Адаптировать `bypassPermissions` и autonomous-loop философию под нашу инфраструктуру без установки наших guardrails (нет auto-approve на destructive operations).
- Писать новые скиллы по паттерну репо без проверки на вес — `.claude/skills/deep-research/SKILL.md` = 33 KB, один скилл съест много контекста агента.
