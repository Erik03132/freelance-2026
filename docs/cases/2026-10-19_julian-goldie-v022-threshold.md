# julian-goldie-v022-threshold — Hermes v0.22 «Threshold Release» (промо-видео)

**Автор/источник:** Julian Goldie SEO (YouTube, 17.10.2026, [JiPgp_Exu1A](https://www.youtube.com/watch?v=JiPgp_Exu1A)) — 432K подписчиков, продаёт «AI Profit Boardroom» (платное комьюнити, 30-day roadmap, coaching calls)

**Суть (2-3 строки):** Обзор Hermes Agent v0.22 («Threshold Release» от 13.10.2026). Ключевые фичи: guided setup без API-ключа (free welcome trial model), 600+ плагинов в browsable catalog, unified connectors page, Kanban board для multi-agent task dispatch, Raft network integration (agent-to-agent handoff), bot screen (remote desktop viewing), local models one-click. Автор продвигает свой «Agent OS» — готовый zip + 30-day roadmap + 4 coaching calls/week за доступ в платное комьюнити (93K+ members).

**Стек (заявленные фичи v0.22):**
- Guided chat setup (no API key to start)
- 600+ plugin catalog (Slack, Google Calendar, CRM, etc.)
- Unified connectors page
- Kanban board: dispatcher → worker agents, background tasks
- Raft network: agent-to-agent task handoff
- Bot screen: watch remote agent desktop real-time
- One-click local models
- Shared memory via Obsidian vault (every agent reads same folder)
- Mission Control dashboard: all agents, live activity stream

**Что применимо у нас:** [НЕТ — продающее] — видео — продвижение платного курса/комьюнити («AI Profit Boardroom», $30-day roadmap, coaching calls). Конкретики по реализации мало: нет технических деталей, как именно настроить Kanban, Raft, bot screen. Упоминание «219K GitHub stars» — неверно (на 10.2026 у NousResearch/hermes-agent ~20-30K stars). Фичи v0.22 реальны (проверено через changelog), но разбор в видео — поверхностный, цель — продать доступ. Наши задачи: Kanban уже есть (hermes kanban), local models уже работают, Obsidian vault уже SSoT. Raft network и bot screen — новые фичи v0.22, стоит проверить официальные release notes.

**Действие:**
- [x] Добавить в раздел «Пропущено» INDEX.md
- [ ] Проверить официальный changelog v0.22 (GitHub releases) на предмет Raft network / bot screen / guided setup — если есть, завести отдельный технический разбор

**Причина пропуска:** Продающее видео с призывом купить курс, минимальная техническая конкретика, завышенные цифры (stars), нет первоисточника кода/конфигов. Полезный сигнал: v0.22 вышел 13.10.2026 — проверить релизы на GitHub.

**Когда НЕ применять:** Всегда — это маркетинговый контент, не технический кейс.