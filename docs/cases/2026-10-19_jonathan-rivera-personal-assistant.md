# jonathan-rivera-personal-assistant — 24/7 личный ассистент на Qwen 3.5-35B local + OpenRouter fallback

**Автор/источник:** Jonathan_Rivera (Reddit r/HermesAgent, 12.10.2026, [s4qhl2](https://www.reddit.com/r/hermesagent/comments/1s4qhl2/hermes_agent_personal_assistant_in_development/))

**Суть (2-3 строки):** Разработчик запускает Hermes Agent 24/7 на Windows PC с локальной Qwen 3.5-35B через LM Studio (fast, private, no cloud) + OpenRouter fallback. Mac M3 16GB доступен, но пока не в пайплайне. Основной интерфейс — Discord. Интеграции: Google Calendar, Gmail, Obsidian vault (PKM), Todoist, Apple Health (в разработке), файлы/PDF, терминал (git, builds, scripts), cron, background processes, iMessage, Telegram. Domain-skills: финансовый трекинг (stocks, options), domain intelligence/recon. Всё логгируется в общий Obsidian vault (SSoT). Ключевой workflow: pull calendar+Gmail+Todoist → analyze what's due → delegate coding to Claude Code → track progress → update vault. Есть dedicated Claude Code Skill для оптимизации Hermes — каждая ошибка/фикс логируется в shared doc.

**Стек:**
- Hardware: Windows PC (main) + Mac M3 16GB (available, not yet in pipeline)
- Local LLM: Qwen 3.5-35B via LM Studio (primary inference)
- Fallback: OpenRouter (when other models needed)
- Hermes: 24/7 alongside Claude Code
- Communication: Discord (primary), iMessage, Telegram
- Integrations: Google Calendar, Gmail, Obsidian vault, Todoist (custom labels: waiting-approval, in-progress, follow-up), Apple Health (WIP), file ops, PDF handling
- Execution: Terminal access, file ops, cron job mgmt, background process mgmt
- Domain skills: Financial tracking (stock prices, options positions), Domain intelligence & reconnaissance
- Memory: Persistent across sessions (learns preferences, workflows, domain knowledge)
- SSoT: Personal Obsidian vault

**Что применимо у нас:** [ДА] — несколько сильных совпадений с нашей архитектурой:
1. **Локальная Qwen 3.5-35B** — валидация ES-NEW-03 (Qwen local для профилей, напр. marketer). У нас Mac M3/M4 — нужно проверить MLX/llama.cpp кванты Qwen 3.5-35B.
2. **Multi-channel gateway** (Discord + iMessage + Telegram) — у нас TG-бот @hermes03132_bot + VPS профили + Discord fail-closed (ES-NEW-02). Паттерн «один агент, много каналов» — наш курс.
3. **Obsidian как SSoT + персистентная память** — у нас vault `~/freelance-2026/vault/` + 7-папковая таксономия. Подтверждает подход.
4. **Workflow chain: data → analysis → Claude Code delegation → track → update vault** — ровно наш паттерн Sherlock→Batrak→Chief + expert-session.
5. **Dedicated skill для оптимизации самого Hermes** (Claude Code Skill) — идея «агент улучшает агента» — в духе self-evolution (awesome-hermes-usecases: Self-Evolution).

**Действие:**
- [x] Создать запись в `docs/cases/`
- [ ] **ES-NEW-03 расширение**: Валидация Qwen 3.5-35B MLX/llama.cpp на Mac M3/M4 для профиля marketer (анализ каналов) → ACTIVE_TASKS
- [ ] Изучить dedicated «Hermes-optimizer» skill pattern (агент пишет/фиксит свои скиллы через Claude Code) → ACTIVE_TASKS как **ES-NEW-05**
- [ ] Проверить: как у автора реализован bridge к Apple Health / iMessage — у нас есть `apple-reminders`, `apple-notes`, `imessage` скиллы

**Цифры/бенчмарки (из источника):**
- Qwen 3.5-35B local: «fast, private inference without cloud reliance»
- 24/7 uptime на consumer hardware
- Shared context doc с Claude Code: «invaluable for developing new skills and debugging»

**Trade-off (автор признаёт):**
- Mac M3 пока не в inference pipeline (потенциал не использован)
- Apple Health — в разработке (не готово)
- OpenRouter fallback = все равно зависимость от облака для сложных задач

**Подводные камни (из источника):**
- Локальная 35B модель требует достаточного RAM (35B ~20GB+ квантованная) — Windows PC автора, вероятно, 32-64GB
- LM Studio как inference server — отдельный компонент для управления
- Memory persistence across sessions — нужно правильно настроить Hermes memory provider
- iMessage/Telegram integration — может требовать отдельные настройки авторизации

**Когда НЕ применять:** Если нет железа для локальной 35B (минимум 24GB RAM для 4-bit); если приватность не критична и дешевле cloud; если нужна только простая автоматизация без персистентной памяти.