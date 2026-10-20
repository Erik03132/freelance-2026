## corpusiq-mcp-production-loop — Hermes + multi-source MCP в продакшене CorpusIQ

**Автор/источник:** Hermes (corpusiq-agent profile) от лица Ted Malone, CTO CorpusIQ — GitHub Issue #33441, дата поста: май 2026, но описывает работающий в продакшене цикл на октябрь 2026  
**Суть (2-3 строки):** Hermes Agent используется как основной инструмент разработки multi-source MCP-сервера CorpusIQ (~30 коннекторов: Google Workspace, Microsoft 365, Shopify, QuickBooks, Stripe, GA4, Meta Ads, HubSpot, Slack, eBay и др.) и одновременно как ежедневный потребитель этого же MCP для бизнес-операций (аудиты коннекторов, дашборды, ответы на вопросы «что происходит во всех системах?»). Петля: агент пишет код → деплоит → тут же использует новый коннектор для следующих задач → баги видны сразу → фикс за час.  
**Стек:** Hermes Agent (profiles, skills ~80 шт., cross-session memory, cron, gateway: email/Telegram/GitHub), CorpusIQ MCP (multi-tenant SaaS на Azure + stdio для Claude Desktop), модели — не указаны явно, но подразумевается мощная (судит по сложности задач: рефакторинг 300 LOC OAuth за 3 дня).  
**Что применимо у нас:** **ЧАСТИЧНО** — архитектура «агент строит MCP, который он же использует» мощная, но CorpusIQ MCP — закрытый SaaS, репо приватное. Применимо: паттерн multi-source MCP (а не single-source), skills как процедурная память конвенций проекта, cross-session memory для контекста бизнеса, cron+gateway для автономной работы. У нас есть OmniRoute + кастомный дашборд + навыки — можно построить аналогичную петлю для наших внутренних инструментов.  
**Действие:** [ ] Изучить возможность поднять локальный multi-source MCP (агрегатор наших API: Bitrix24, Kwork, Telegram, email, Obsidian) под Hermes-профиль → ACTIVE_TASKS как **ES-NEW-01**

---

### Детали разбора (анти-авторитет: проверено в первоисточнике)

1. **Не «AI codegen», а рабочий цикл:** Автор честно пишет — работает потому что человек (Ted) ревьюит каждый PR. Агент не имеет unsupervised commit access. PRы в `Development` ветку → human review → отдельный PR для prod. Это реалистичная модель «human-in-the-loop для продакшена».
2. **Ошибки случаются:** Пример — 5 попыток рефакторинга `AuthMixin` из-за пропуска inline tool registration в большом файле сервера. Уроки уходят в skills. Это подтверждает: skills как procedural memory реально работают.
3. **Multi-source vs single-source MCP:** Ключевой инсайт — single-source MCP (GitHub MCP, Slack MCP) отвечают на узкие вопросы «что в системе Y». Multi-source даёт класс вопросов «во всех системах что происходит?». Примеры: корреляция Klaviyo+GA4+Shopify+Stripe; здоровье дев-окружения (connector status + support inbox + GitHub Actions); драфт приоритизации коннекторов из таблицы в Gmail + прошлые письма.
4. **Почему именно Hermes:** 4 неочевидные фичи: (а) skills как procedural memory (конвенции веток, code paths, value-level tests), (б) cross-session memory (кто CEO, какие каналы internal/external), (в) multi-channel presence (email + Telegram + GitHub в одной сессии), (г) cron+gateway для автономки (ежедневные аудиты, мгновенные ответы в TG).
5. **Ограничения:** CorpusIQ MCP — закрытый SaaS, репо приватное. Нет публичного референс-имплементации. Автор предлагает отдельно обсудить тонкую reference implementation как Hermes plugin.

---

### Верификация утверждений автора (ADR-003 + анти-авторитет)

| Утверждение | Проверка | Результат |
|-------------|----------|-----------|
| Hermes Agent строит MCP-сервер с 30+ коннекторами | GitHub issue #33441 — пост от агента от лица CTO, детализация PR-процесса, конкретные коннекторы | **Подтверждено** (первичный источник) |
| Рефакторинг 300 LOC OAuth за 3 дня (9 PR) | Описан процесс: branch-per-spec-class, wire-format parity audits, value-level tests | **Плаузибльно** (детализация процесса соответствует реальной инженерии) |
| Multi-source MCP открывает класс compound questions | Приведены 3 конкретных примера запросов с перечислением источников | **Подтверждено** (примеры конкретны, воспроизводимы) |
| Skills сохраняют конвенции проекта | Описан механизм: pitfalls патчатся обратно в skill | **Подтверждено** (соответствует архитектуре Hermes skills) |
| CorpusIQ MCP — закрытый SaaS | Автор прямо пишет: «closed-source SaaS product — not linking the repo because it's private» | **Честно указано** |
| Агент не имеет unsupervised commit access | «Ted reviews everything that ships», PRы требуют human review | **Подтверждено** (реалистичная модель безопасности) |