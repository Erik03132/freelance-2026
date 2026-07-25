---
name: governance
description: Document management — Single Source of Truth, Context Engineering, progressive disclosure, file organization, anti-patterns.
---

## Single Source of Truth (SSoT)
```
Каждой теме — ОДИН файл.
Нет файла по теме → создать.
Есть файл по теме → ДОПОЛНИТЬ, не создавать новый.
```

## Запрещённые паттерны
| ❌ Запрещено | ✅ Правильно |
|-------------|-------------|
| `*_V2.md`, `*_NEW.md` | Обновить оригинал |
| `TODO.md`, `STATUS.md` | Основной документ проекта |
| `PLAN_*.md` | ROADMAP проекта |

## Правила общения агента
- Общаться на русском языке
- Не повторять информацию, которую пользователь уже знает
- Не предлагать пользователю сделать то, что можно выполнить самому
- Быть кратким, по делу
- НЕ создавать документацию без явного запроса

## Progressive Disclosure
1. При старте: AGENTS.md + CHRONICLE.md
2. При задаче: загрузи нужный skill через tool → следуй
3. После задачи: контекст скилла не нужен

## Context Engineering
Иерархия: Rules/AGENTS.md → Spec → Source Code → Error Output → History
Цель: < 2000 строк focused контекста на задачу.

### Inline Planning Pattern
```
PLAN:
1. Сделать A
2. Сделать B
3. Сделать C
→ Выполняю, если не перенаправите.
```
