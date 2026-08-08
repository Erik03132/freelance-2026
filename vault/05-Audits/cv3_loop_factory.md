# CV-3: junior-to-senior и loop-factory — оценка (08.08.2026)

## Статус репозиториев
- **loop-factory** (JuliusBrussee) — клонирован (depth 1), изучен.
- **junior-to-senior** — НЕ найден (`repository not found`). Пропускаем; вместо него оценён loop-factory.

## loop-factory — суть
Спека-файл (markdown) → три папки состояния:
```
inbox/ (идеи) → active/ (агент работает) → archive/ (проверено, принято)
```
Цикл: spec → dispatch (агент строит) → verify (тесты из спеки) → review (проход) → archive / ещё пасс → backpropagate (уроки пишутся обратно в docs).

**Философия:** «автоматизируй печать и проверку, а НЕ решение что строить». Агент никогда не решает направление продукта.

## Оценка vs наши паттерны

| Критерий | loop-factory | У нас | Вердикт |
|----------|-------------|-------|---------|
| Задача как спека | ✅ spec.md | ✅ writing-plans, PRD | Дубль |
| Состояние = папка | inbox/active/archive | ⚠️ чекпоинты, handoff | Можно взять идею |
| Verify перед review | ✅ тесты из спеки | ✅ verification-before-completion, eval | Совпадает |
| Review-pass/перепроход | ✅ review agent | ✅ two-axis review, Проверяла | Совпадает |
| Backpropagate уроков | ✅ пишутся в docs | ✅ self_improve_log, ce-compound | Совпадает |
| Агент НЕ решает направление | ✅ жёстко | ✅ человек финалит | Совпадает |

## Вывод (CV-3)

**НЕ внедрять как систему** — 90% паттернов уже есть (writing-plans + verification-before-completion + two-axis review + Проверяла + ce-compound). 

**Забрать 1 идею:** «состояние задачи = папка» (inbox/active/archive) — простое и видимое. Для наших фоновых агентов/рункан-канона это даёт on-ramp без БД. Частично уже реализовано в `run_canon.py` (runs/step-N-name/) — расширить на inbox/active/archive как обёртку.

**junior-to-senior:** не найден публично — пропускаем.

**Статус:** CV-3 закрыт оценкой. `docs/solutions/2026-08-08_nonblocking_subagents.md` + этот файл в docs/audits/.