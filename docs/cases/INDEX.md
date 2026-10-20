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
- Источники: YouTube (фильтр "за неделю"), Telegram-каналы практиков (COMANDOS AI, Hermes-русскоязычное сообщество), GitHub `awesome-hermes` если появится, Reddit r/HermesAgent

- Разбор: скилл `expert-source-pipeline` (ADR-003 + правило "анти-авторитет": проверять в открытых источниках, не принимать на веру).

---

## Сводка за 13–19 октября 2026

**Найдено:** 3 кейса (2 Reddit r/hermesagent + 1 YouTube)
**Пропущено:** 1 (продающее видео v0.22)  
**Новые задачи в ACTIVE_TASKS:** ES-NEW-03, ES-NEW-04, ES-NEW-05

---

## Кейсы

### ✅ Разобрано

- **[codegraph — локальный knowledge-graph для кода, MCP](./codegraph.md)** (17.08.2026, AI Stack Engineer) — парсит репо в SQLite-граф, отдаёт агенту через MCP как один tool. 67k★, активно поддерживает OpenCode + Hermes. **Закрывает наш ADR-003 (graph layer).** Пилот запланирован как ES-10.

- **[ivan-ilyich — ИИ-помощник по здоровью на Hermes](./ivan-ilyich.md)** (14.04.2026, Коновалов) — Claude Code + Telegram + 7 лет ЕМИАС. Локальная wiki-папки + семантический поиск + cron-напоминания + PDF-сводки для врача. **ES-12..ES-15 → ACTIVE_TASKS.**

- **[knowledge-factory — AI-компаньон для freelance бизнеса](./knowledge-factory.md)** (11.04.2026) — Hermes + Claude Code как компаньон: авто-деплой лендингов, cron-аудит NLP-моделей, 24/7 мониторинг, тикеты. **ES-16..ES-18 → ACTIVE_TASKS.**

- **[voice-live-pace — локальный голосовой стек для AI-агентов](./voice-live-pace.md)** (18.08.2026, Александр Левитан) — Whisper MLX + VAD-профиль + артефакт-блеклист, локальная генерация речи MLX, TTS через Siri/Neural. **ES-12..ES-15 → ACTIVE_TASKS.**

- **[rag-production-patterns — RAG-пайплайн для финансистов](https://github.com/nousresearch/hermes-agent/blob/main/hermes-already-has-routines.md)** (системный docs, актуально 2026) — Hermes + Ollama embeddings через MCP, RAG pipeline: data ingestion, embedding, retrieval, agent orchestration, feedback loop. **ES-19..ES-21 → ACTIVE_TASKS.**

- **[agent-security-trifecta — сценарии атак на AI-агентскую инфраструктуру](./agent-security-trifecta.md)** (07.09.2026, AI Security Report) — 3 класса атак: prompt injection через MCP, memory poisoning, gateway bypass. Hermes уязвим к context injection, backdoor в shared memory. **ES-25..ES-27 → ACTIVE_TASKS.**

- **[hermes-agent-feedback — обратная связь и улучшения через диалог](./hermes-agent-feedback.md)** (08.09.2026, Nous Research Blog) — feedback channel, rating system, self-improving prompts, agent-to-agent task routing. **ES-22..ES-24 → ACTIVE_TASKS.**

- **[always-on-personal-assistant — Hermes Agent как 24/7 фоновый оператор личных сервисов](./2026-10-12_always-on-personal-assistant.md)** (12.10.2026, u/recmend, Reddit r/hermesagent) — Qwen 3.5-35B local (LM Studio) + OpenRouter fallback, 24/7 на Mac M3. Интеграции: Calendar, Gmail, Obsidian, Todoist, iMessage, Telegram, WhatsApp, Discord, Signal. Workflow chain: data→analysis→Claude Code delegation→track→update vault. Local voice via Faster Whisper. Agent-to-agent messaging через profile system. **ES-NEW-03(валидация Qwen local + multi-channel gateway + voice для профилей.**

- **[rasmus-hermes-windows-discord — личный рабочий процесс Hermes на Windows + Discord](./2026-10-19_rasmus-hermes-windows-discord.md)** (05.10.2026, Rasmus Wulff Jensen, YouTube) — 3 месяца 24/7 на Windows, Discord multi-channel (meal prep, morning status, notifications, YouTube, email, calendar), интеграции: RSS, X, Gmail, Calendar, Todoist, файлы, терминал, cron. Ключевой инсайт: Discord каналы = контекстные инструкции на домен. **ES-NEW-04(Telegram Topics как замена Discord-каналов для профилей.**

- **[jonathan-rivera-personal-assistant — 24/7 личный ассистент на Qwen 3.5-35B local + OpenRouter](./2026-10-19_jonathan-rivera-personal-assistant.md)** (12.10.2026, Jonathan_Rivera, Reddit r/HermesAgent) — Windows PC + Qwen 3.5-35B (LM Studio) + OpenRouter fallback, Mac M3 доступен но не в пайплайне. Discord + iMessage + Telegram, Obsidian vault SSoT, Google Calendar/Gmail/Todoist/Apple Health, terminal/cron/background, financial tracking, domain recon. Workflow: data→analysis→Claude Code delegation→track→vault. Dedicated skill для оптимизации Hermes. **ES-NEW-03(валидация Qwen 35B MLX на Mac M3), ES-NEW-05(Hermes-optimizer skill pattern).**

### ⏸ В очереди

- **[corpusiq-mcp-production-loop — Hermes + multi-source MCP в продакшене CorpusIQ](./2026-10-11_corpusiq-mcp-production-loop.md)** (11.10.2026, Hermes/Ted Malone CTO, GitHub #33441) — агент строит multi-source MCP (30+ коннекторов: Google, MS365, Shopify, Stripe, GA4, Meta Ads, HubSpot, Slack, eBay) и одновременно использует его для бизнес-операций: аудиты, дашборды, compound queries. Петля: PR→deploy→использование→баг→фикс за час. **ES-NEW-01(локальный multi-source MCP для наших API: Bitrix24/Kwork/email/Obsidian.**

- **[discord-failclosed-permission — Hermes Agent Discord развёртывание с fail-closed политикой](./2026-10-11_discord-failclosed-permission.md)** (11.10.2026, Hermes Team, официальный блог) — официальный гайд настройки Discord gateway с 2026 fail-closed политикой: token alone не достаточно, нужен explicit allowlist (users/roles/channels), thread sessions, FlyHermes option. **ES-NEW-02(обновить Discord-gateway конфиг в профилях до fail-closed.**

---

### ❌ Пропущено

- **[2026-10-17 Julian Goldie «NEW Hermes Agent Update is ABSOLUTELY INSANE!»](https://www.youtube.com/watch?v=JiPgp_Exu1A)** — промо-видео v0.22 «Threshold Release» для продажи «AI Profit Boardroom» (платное комьюнити, 30-day roadmap, coaching). Завышенные цифры (219K stars vs реальных ~25K), нет технической конкретики, цель — конверсия в платный доступ. Фичи v0.22 реальны (guided setup, 600+ plugins, Kanban, Raft, bot screen) — проверить в официальном changelog.