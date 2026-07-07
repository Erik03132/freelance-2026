# AGENTS.md — Agent Lab

Python ML/embedding пайплайн: LLM2Vec, нормализация, validation layer, интеграция с Bitrix и Photo API.

---

## Команды сессии

### `start-day-agent-lab` — Старт сессии

1. **Прочитать регламенты:** `AGENTS.md` + `chp.md` + последний `checkpoints/chp_*.md`
2. **claude-mem:** `memory_search("agent-lab")` — подтянуть историю
3. **Git:** `git status`
4. **.env:** проверить `OPENROUTER_API_KEY`, `GEMINI_API_KEY`, `LEONARDO_API_KEY`, `NEON_DATABASE_URL`
5. **Handoff:** проверить `docs/handoff_*.json`
6. **Скилл:** загрузить `bot-development` (Python)
7. Вывести краткую сводку

### `finish-day-agent-lab` — Завершение сессии

1. **Обновить `chp.md`**
2. **Копировать** → `checkpoints/chp_<timestamp>.md`
3. **claude-mem:** `memory_add kind=session-summary`
4. **Git:** `git add -A && git commit -m "..." && git push`
5. Сообщить пользователю: "Сессия завершена"
