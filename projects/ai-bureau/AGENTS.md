# AGENTS.md — AI Bureau

Скрипты и дистрибутивы для работы с AI API (Gemini, OpenRouter, Perplexity). Аудиты и отчёты.

---

## Команды сессии

### `start-day-ai-bureau` — Старт сессии

1. **Прочитать регламенты:** `AGENTS.md` + `chp.md` + последний `checkpoints/chp_*.md`
2. **claude-mem:** `memory_search("ai-bureau")` — подтянуть историю
3. **Git:** `git status`
4. **.env:** проверить `GEMINI_API_KEY`, `OPENROUTER_API_KEY`, `PERPLEXITY_API_KEY`
5. **Handoff:** проверить `docs/handoff_*.json`
6. Вывести краткую сводку

### `finish-day-ai-bureau` — Завершение сессии

1. **Обновить `chp.md`**
2. **Копировать** → `checkpoints/chp_<timestamp>.md`
3. **claude-mem:** `memory_add kind=session-summary`
4. **Git:** `git add -A && git commit -m "..." && git push`
5. Сообщить пользователю: "Сессия завершена"
