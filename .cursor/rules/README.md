# .cursor/rules — Правила и скиллы Antigravity для Cursor

## Структура

```
.cursor/rules/
├── global/          ← Antigravity скиллы (НЕ РЕДАКТИРОВАТЬ вручную — перезапишутся!)
│   ├── 00_iron_rules.mdc      — Железные правила (SSH, SSoT, протоколы)
│   ├── 01_angela_map.mdc      — Карта агентов Анжела/Птенчикова
│   └── <skill-name>.mdc       — Все 41 скилл Antigravity
└── project/         ← Проектные правила (РЕДАКТИРОВАТЬ ЗДЕСЬ)
    ├── freelance_2026.mdc     — VPS, структура проекта, Битрикс
    └── <твой-новый-скилл>.mdc ← Создавай здесь новые скиллы
```

## Как работать в Cursor как в Antigravity

1. Открой папку `freelance-2026` в Cursor
2. Cursor автоматически подхватывает `.cursor/rules/` — все скиллы активны
3. `00_iron_rules.mdc` — `alwaysApply: true`, всегда в контексте
4. Остальные скиллы — `alwaysApply: false`, Cursor подключает по релевантности

## Синхронизация (Antigravity ↔ Cursor)

### Antigravity → Cursor (обновить после правки скиллов)
```bash
./tools/sync_cursor_rules.sh              # все скиллы
./tools/sync_cursor_rules.sh --skill rag-master  # один скилл
```
*Запускается автоматически при `finish_day.sh`*

### Cursor → Antigravity (создал новый скилл в Cursor)
```bash
# 1. Создай файл: .cursor/rules/project/my-new-skill.mdc
# 2. Импортируй:
./tools/import_cursor_skills.sh my-new-skill

# 3. Добавь в MANIFEST.md вручную:
open ~/.gemini/antigravity/skills/MANIFEST.md
```

## Создание нового скилла в Cursor

Создай файл `.cursor/rules/project/my-skill.mdc`:

```markdown
---
description: "Краткое описание скилла (для автоподключения Cursor)"
alwaysApply: false
---

---
name: my-skill
description: "Описание скилла"
---

# Название скилла

## Goal
Цель скилла.

## Когда активировать
- Список триггеров

## Инструкция
Детальные инструкции...
```

После создания запусти импорт в Antigravity (см. выше).

## Ограничения Cursor vs Antigravity

| Возможность | Antigravity | Cursor |
|------------|-------------|--------|
| Автозагрузка скиллов по boot | ✅ MANIFEST.md | ✅ .mdc автоподключение |
| Хроники / чекпоинты | ✅ Автоматически | ❌ Вручную |
| Параллельные агенты | ✅ Subagents | ❌ |
| SSH на VPS | ✅ run_command | ✅ Через терминал |
| Кодирование | ✅ | ✅✅ (Cursor сильнее) |
| Diff-интерфейс | Хуже | ✅ Нативный |
| Память между сессиями | ✅ Checkpoints | ❌ |
