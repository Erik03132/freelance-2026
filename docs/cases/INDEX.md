# Cases — библиотека практических кейсов Hermes Agent

> Разборы реальных сценариев использования Hermes Agent из открытых источников: видео, статьи, блоги, Telegram-каналы практикующих авторов.

> **Не храним:** продающие разборы «экспертов» с обещаниями роста, общие обзоры без конкретики, разборы конкурирующих агентов.



## Формат кейса (1 страница)

```
## <slug> — <короткое название>
**Автор/источник:** <имя, ссылка, дата>
**Суть (2-3 строки):** что делает агент, на чём построено
**Стек:** модель, навыки, сервисы (только то, что упомянуто)
**Что применимо у нас:** [ДА / ЧАСТИЧНО / НЕТ] + почему
**Действие:** [ ] <конкретный шаг> → ACTIVE_TASKS
```

## Статусы

- `[ ]` — разобрать на следующей итерации (мониторинг)
- `[x]` — разобрано, зафиксировано
- `[skip]` — разобрано, не применимо (без ACTIVE_TASKS)


## Мониторинг

- Cron раз в неделю: `0 9 * * 1` (понедельник 9:00 МСК) — найти 3-5 свежих публичных кейсов Hermes Agent, разобрать.

- Источники: YouTube (фильтр «за неделю»), Telegram-каналы практиков (COMANDOS AI, Hermes-русскоязычное сообщество), GitHub `awesome-hermes` если появится, Reddit r/HermesAgent


- Разбор: скилл `expert-source-pipeline` (ADR-003 + правило «анти-авторитет»: проверять в открытых источниках, не принимать на веру).


---

## Кейсы

### ✅ Разобрано

- **[codegraph — локальный knowledge-graph для кода, MCP](./codegraph.md)** (17.08.2026, AI Stack Engineer) — парсит репо в SQLite-граф, отдаёт агенту через MCP как один tool. 67k★, активно поддерживает OpenCode + Hermes. **Закрывает наш ADR-003 (graph layer.** Пилот запланирован как ES-10.
- **[ivan-ilyich — ИИ-помощник по здоровью на Hermes](./ivan-ilyich.md)** (14.04.2026, Коновалов) — Claude Code + Telegram + 7 лет ЕМИАС. Локальная wiki-папки + семантический поиск + cron-напоминания + PDF-сводки для врача. **Референс для нашего Айболита(ES-11.**
- **[voice-live-pace — живой темп русского голосового разговора](./voice-live-pace.md)** (18.08.2026, Якимов/361.Robotics, Habr 1069312) — гибридный ASR+VAD-профиль, роутер команд на RU-эмбеддингах, ack-фразы, TTS-хигиена. **Бьёт в ветки Levitan/AVM/Angela(ES-12..ES-15.**
- **[knowledge-factory — модель знаний vs RAG, provenance, fact-check](./knowledge-factory.md)** (16.08.2026, Ланчев/ODS, Habr 1070832) — типизация сущностей, provenance-цепочка, контур факт-проверки. **Бьёт в Фемиду/SVO/Sinergy(ES-16..ES-18. Подтверждает HT-3/AG-3.**
- **[rag-production-patterns — препроцессинг запроса, семантический кэш, UPSERT](./rag-production-patterns.md)** (20.08.2026, SberDevices, Habr 1071570) — LLM-чистка RU-запроса перед retrieval, семант. кэш ~100x, idempotent UPSERT. **Бьёт в smart-rag/RAGFlow/Фемиду(ES-19..ES-21.**
- **[hermes-agent-feedback — агент как потребитель, не процессор](./hermes-agent-feedback.md)** (21.08.2026, Немировский/Альфа-Банк, Habr 1072770) — write-protect скиллов, явный failure у крона, вынос обработки в код. **Бьёт в skills/крон/Шерлок/sinergy( ES-22..ES-24. User-feedback по нашему Hermes Agent.**
- **[agent-security-trifecta — lethal trifecta, guardrails, red-teaming](./agent-security-trifecta.md)** (20.08.2026, Макрушин/Яндекс, Habr 1071908) — разрыв trifecta, runtime guardrail, непрерывный red-teaming. **Бьёт в ai-defender(ES-25..ES-27. Дефендер включён в Экспертную группу.**
- **[hermes-agent-audit — что есть, что не используется, что включить](./hermes-agent-audit.md)** (21.08.2026, аудит `hermes --help`)— 18 фич Hermes, не задействованных; приоритеты P0–P3. Роль «эксперта по Hermes» для пользователя.

- **[devbrain — Obsidian SSoT для мультиагентного кодинга](./2026-08-31_devbrain-obsidian-ssot.md)** (30.08.2026, DycandX, GitHub) — MCP-мост Obsidian↔агенты+Hermes/Claude/Antigravity/OpenCode, гибридный поиск FastEmbed/BM25, 7-папковая таксономия. **ES-29(общая база знаний, гибридный retrieval.**
- **[hermes-hq — control plane для команды Hermes-профилей](./2026-08-31_hermes-hq-control-plane.md)** (29.08.2026, smkamranqadri, GitHub) — SQLite-движок «одна сессия→задача», reviewer-gate, список «нужен ты». **ES-30(оркестрация команды 6 профилей. Early dev(★0.**
- **[hermes-snowflake — Hermes на Snowflake + прокси-совместимость провайдера](./2026-08-31_hermes-snowflake-provider-proxy.md)** (26.08.2026, Баттальери, GitHub) — каталог 5 несовместимостей OpenAI-протокола у Cortex + тонкий прокси-адаптер. **ES-31 (чинит наши провайдер-проблемы: opencode-zen 401, OmniRoute auto.**

### ⏸ В очереди

- **[hermes-companion — mobile-first control plane для Hermes](./2026-08-31_hermes-companion.md)** (30.08.2026, forcewake, GitHub) — Telegram Mini App + Web/PWA + бот с typed control plane, опц. local bridge. Дублирует наш TG-бот(@hermes03132_bot), но идея Mini App-поверхности новая — в очередь на оценку (не полный разбор).

.

### ❌ Пропущено

- **[2026-08-13 Дмитрий Попов / COMANDOS AI «9 кейсов»](https://www.youtube.com/watch?v=TCqlq4IB2Lg)** — продающее видео, размытые формулировки, продвигает внешний SaaS Multica. У нас всё уже покрыто(Игоёк/Ботман/Маркетолог, VPS + локальный Hermes.). Потенциальный сигнал: автор работает с РФ-малым бизнесом → возможный канал клиентов, не техническое.Title
- **[2026-08-18 Codedigipt «Hermes Bot Mode»](https://www.youtube.com/watch?v=lI0WMeTEwYQ)** — UI-обёртка Hermes Bots. Дублирует наши скиллы. См. ES-7 в ACTIVE_TASKS.

- **[2026-08-31 digital-employee-agent-gateway](https://github.com/erectsrhapsodesxx-max/digital-employee-agent-gateway)** (erectsrhapsodesxx-max) — корпоративный шлюз-«single middleware, 4-слойная маршрутизация» для Hermes (★0, китайский. **Дубль нашей шлюзовой инфраструктуры** (OmniRoute, кастомный дашборд `:8890`, gateway. Не применимо.
- **[2026-08-31 hermes-control-interface](https://github.com/x-cmd-install/hermes-control-interface)** (x-cmd-install) — self-hosted веб-dashboard:(browser terminal, file explorer, cron mgmt, metrics. **Дубль нашего дашборда `:8890`** + OmniRoute-дашборда. Пропущено.ор
- **[2026-08-31 titan-agent-dashboard](https://github.com/Rockerik36812/titan-agent-dashboard)** (Rockerik36812) — real-time multi-agent monitoring для Hermes. **Дубль dashboards**(см. выше. Пропущено 3иото


---

## Связанные

- `docs/solutions/` — технические one-pager'ы по инструментам (отдельный слой..
- `ACTIVE_TASKS.md` секция «🧠 Эксперт-сессия» — задачи из разборов.