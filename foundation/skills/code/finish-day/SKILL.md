---
name: finish-day
description: Завершение рабочей сессии — фиксация изменений Git, запись лога сессии, отчёт о проделанной работе. Вызывать по окончании работы в ZCode или Open Code.
---

# Finish Day

## When to Use
- Завершение рабочей сессии в ZCode или Open Code
- Перед закрытием проекта или сменой контекста
- Нужно зафиксировать текущие изменения и записать что было сделано

## Action
Выполнить скрипт завершения дня:
```bash
bash /Users/igorvasin/freelance-2026/tools/ops/finish_day.sh
```

## What It Does
- Фиксирует все изменения в Git (add + commit)
- Обновляет журнал сессий
- Записывает сводку того, что было сделано
- Выполняет cleanup временных файлов

## Integration
- Git status → фиксация изменений
- AGENTS.md / SESSION_LATEST.md → обновление контекста
- Работает в обеих средах: ZCode и Open Code

## Commands
- `skill("finish-day")` — активировать скилл завершения сессии
- «Заверши день» — выполнить finish_day.sh вручную
