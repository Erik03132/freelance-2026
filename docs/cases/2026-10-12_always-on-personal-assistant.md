## always-on-personal-assistant — Hermes Agent как 24/7 фоновый оператор личных сервисов

**Автор/источник:** u/recmend — Reddit r/hermesagent, 5 апреля 2026 (материал пересматривался и репостился в октябре 2026), исходный пост: https://www.reddit.com/r/hermesagent/comments/1sd3bwf/  
**Суть (2-3 строки):** Пользователь запустил Hermes Agent 24/7 на Mac M3 с Qwen 3.5-35B (LM Studio) + OpenRouter fallback. Агент соединяет Google Calendar, Gmail, Obsidian, Todoist, iMessage и Telegram. Календарь+Gmail+Todoist → анализ → делегирование задач в Claude Code → треккинг прогресса → обновление Obsidian vault. Цепочка workflow вместо чата.  
**Стек:** Qwen 3.5-35B (локальная) + OpenRouter (fallback), LM Studio, Hermes profiles (отдельные конфиги/API keys/memory/gateway), cross-channel (WhatsApp/Telegram/Discord/Signal), Faster Whisper (локальный voice), skills как self-improving system.  
**Что применимо у нас:** **ЧАСТИЧНО** — архитектура always-on + multi-channel + local LLM + Claude Code delegation уже близка к нашей. Мы используем профили, Telegram, cron, skills, но Qwen локально пока не пробовали. Применимо: multi-channel presence (WhatsApp/Signal добавить), локальный voice режим (Faster Whisper), cross-profile communication (agent-to-agent).  
**Действие:** [ ] Валидация Qwen 3.5-35B в local LLM для одного из профилей (например, marketer для анализа каналов) + тест multi-channel gateway → ACTIVE_TASKS как **ES-NEW-03**

---

### Детали разбора (анти-авторитет: проверено в первоисточнике)

1. **Не Chatbot, а Background Operator:** Ключевая фраза — «It's not a chatbot; it's a background operator». Это согласуется с нашей архитектурой (Sherman как cron-based, а не reactive).
2. **Multi-channel presence:** Подключены WhatsApp, Telegram, Discord, Signal одновременно — несколько поверхностей в одной сессии. Это соответствует нашему multi-profile gateway подходу.
3. **Local voice:** Voice mode runs locally с Faster Whisper — не через cloud. Актуально для Shield/voice-профилей если будем делать voice команды.
4. **Agent-to-agent communication:** Пример — Hermes одного пользователя автономно послал сообщение Hermes бизнес-партнёра для координации. Profile system allows this: каждый профиль = отдельный config/API keys/memory/gateway.
5. **Self-improving skills:** «The skill system that builds and improves itself over time is unique» — автор считает это ключевым отличием от Claude Code/OpenClaw.
6. **Qwen local vs OpenRouter fallback:** Схема: локальная модель для обыденных задач, OpenRouter fallback для сложного. Соответствует нашей cascade: Nous API → OpenRouter.

---

### Верификация утверждений автора (ADR-003 + анти-авторитет)

| Утверждение | Проверка | Результат |
|-------------|----------|-----------|
| 24/7 always-on personal assistant на Mac M3 | Частный пост пользователя с описанием setup | **Верифицируемо черехов** (описание техническое, без чужих claim) |
| Qwen 3.5-35B local + OpenRouter fallback | Упомянуто конкретно: LM Studio + OpenRouter как fallback | **Плаузибельно** (соответствует известности Qwen + OpenRouter) |
| multi-channel: WhatsApp/Telegram/Discord/Signal | Список каналов согласуется с Hermes gateway docs | **Подтверждено** |
| agent-to-agent messaging между профилями | Описан механизм: profile system, отдельные gateway | **Плаузибельно** (соответствует Hermes architecture) |
| local voice с Faster Whisper | Упомянуто как особенность setup | **Плаузибельно** (Faster Whisper is стандарт для локального ASR) |
| skills self-improving | «The skill system that builds and improves itself over time is unique» — opinion, но опирается на Hermes features | **Частично** (соответствует Hermes skills system, но claim о uniqueness не проверен) |
| Не заменяет Claude Code, а complement | «I’m probably not replacing my Claude Code setup, but running Hermes alongside it» | **Честно указано** (реалистичный вывод пользователя)