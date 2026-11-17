---
type: article-digest
tags: [cua, computer-use, sandbox, opencode, claude-code, handoff, изоляция-агентов, worktree-per-task]
status: done
updated: 2026-10-25
---

# Cua Spaces SDK — компьютеры для агентов на своих машинах (2026-10-20)
Источник: дроп ТГ 25.10.2026 → верифицировано: [[source]] (cua.ai/docs/spaces, docs/cua-sdk, spaces.cua.ai, GitHub trycua/cua, TechCityAuthority 20.10.2026). Связано: ACTIVE_TASKS секция 🐨 CUA (разбор 21.10.2026: trycua/cua 30k★, sample cua-bots-macos, FSL-1.1-MIT, ⏰ блокировка до апгрейда железа 15.11).

## Главный вывод
**Computer as a primitive for agents.** Spaces SDK — открытый слой «даю каждому агенту свой рабочий стол на машине, которую я контролирую»: ноут, Mac mini, свой облако-аккаунт (AWS/GCP/Azure/Modal). Cua ничего не рентует — relay/координация, не хостинг. Альтернатива облачным агентам: сам выбираешь где исполняется, какие модели, какой доступ.

## Как работает (паттерны для переноса)
1. **Space = один рабочий стол под задачу**: VM/контейнер с экраном и приложениями; агент работает в нём, ты смотришь тот же экран и можешь взять управление (take-over).
2. **`sandbox.agents()`** — запуск кодинг-харнесса (Claude Code, Codex, Gemini CLI, **OpenCode**, Goose) в песочнице: харнесс ставится из pinned+checksum-verified источников, управление через **Agent Client Protocol**, выход нормализован в события.
3. **Run переживает процесс**: state в `~/.cua/agents/<run>`, любой клиент может реттачнуться позже → солидный отклик на наш handoff-пейн (агент умер — работа продолжается).
4. **`cua` CLI**: `agent run / create / ls / logs / send / interrupt` — CP-1 стиль: флаги, follow/queue, interrupt не рвёт сессию.
5. **Multiplayer/teleport**: несколько курсоров на одном десктопе, шаринг Space по аккаунту.
6. **Изоляция vs Worktree-per-Task (OR-2, AGENTS.md):** worktree изолирует только индекс/код, Space изолирует весь compute (ФС, сеть, приложения, GUI) — уровень выше.
7. **~10 строк** старт: пример `examples/agents-in-sandboxes/tour.py`.

## Умолчания дропа (проверить при внедрении)
- Песочницы **E2B/Daytona** — в доках только «sandbox service», явного списка E2B/Daytona в результатах поиска не увидели — перепроверить при внедрении.
- **OpenCode — официальный харнесс** Cua (наш основной стек) — прямая связка.
- Hosted relay бесплатен в early access — после него, вероятно, платно (pricing не опубликован).
- Лицензии: driver MIT, Spaces app FSL-1.1-MIT (source-available, запрет конкурирующих продуктов 2 года — для внутреннего использования ок).
- ⚠️ ai-defender-граница: правила исполнения «инструкции, не enforcement» — Space сам апрувит свои служебные permissions внутри VM; host-доступ НЕ давать.

## Маппинг на наш стек
- **Изоляция handoff-агентов** (AGENTS.md, claude-handoff): реттач + Space-изоляция закрывают 2 главные боли — умерший процесс и доступ секретов.
- OpenCode в списке харнессов — пробовать `cua agent run` (CLI-путь, без Swift-сборки CuaBots) как лёгкую точку входа на CUA-1.
- Мак-сторона: держать VM (Lume) на Mac можно, но пока 8 ГБ RAM мало; блокировка до 15.11.2026.
- Паттерн маркеров `[[ask]]/[[notify]]/[[done]]` (из прошлого кандидата CUA) по-прежнему переносим в наши handoff-агенты — независимо от Spaces.

## Task-и
ACTIVE_TASKS 🐨 CUA: вердикт «кандидат/эксперимент» сохранён; CUA-1 при смоук-тесте сначала `cua agent run` (легче, чем Swift-build), потом CuaBots. OpenCode-in-Space — вариант при перепроектировании handoff-инфраструктуры.
