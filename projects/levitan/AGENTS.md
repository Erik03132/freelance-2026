# Levitan Agents

Описание агентов проекта Levitan.

## Main Agent

**Роль:** Оркестратор  
**Описание:** Главный агент управления проектом, координирует работу других агентов и выполняет основные задачи.

---

## Команды сессии

### `start-day-ai-levitan` — Старт сессии

При вводе этой команды выполнить:

1. **Прочитать регламенты:** `AGENTS.md` + `chp.md` + последний `checkpoints/chp_*.md`
2. **claude-mem:** `memory_search("Levitan")` — подтянуть историю сессий
3. **Git:** `git status` — проверить незакоммиченные изменения
4. **.env:** проверить ключи Mango (`MANGO_VPBX_API_KEY`, `MANGO_VPBX_API_SALT`) — не пустые
5. **Handoff:** проверить `docs/handoff_*.json` — есть ли незавершённые задачи
6. **Скилл:** загрузить `bot-development`
7. Вывести краткую сводку: статус, блокеры, план на сегодня

### `finish-day-ai-levitan` — Завершение сессии

При вводе этой команды выполнить ПОСЛЕДОВАТЕЛЬНО:

1. **Обновить `chp.md`:** статус, что сделано, блокеры, план на завтра
2. **Копировать `chp.md`** → `checkpoints/chp_<YYYYMMDD_HHMM>.md`
3. **claude-mem:** `memory_add kind=session-summary` с итогами сессии
4. **Git:** `git add -A && git commit -m "..." && git push`
5. Сообщить пользователю: "Сессия завершена"

---

## Claude-mem: запись наблюдений

Записывать в claude-mem в течение сессии:

```
memory_add kind=session-summary title="Session YYYY-MM-DD — ..." content="..."
memory_add kind=decision title="..." content="..."
memory_add kind=bugfix title="..." content="..."
```

---

## Добавление навыка

1. Создайте папку в `agent/skills/<skill_name>/`
2. Добавьте `skill.py` с классом навыка
3. Зарегистрируйте в `main.py`