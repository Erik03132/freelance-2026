---
type: wiki
tags: [cua, sandbox, computer-use, opencode, handoff, изоляция-агентов, worktree]
status: done
updated: 2026-11-17
sources: [06-Library/cua-spaces-sdk-2026/digest.md]
---

# Cua Spaces: компьютер на задачу для агента

Источник: `06-Library/cua-spaces-sdk-2026/digest.md` (2026-10-25), верифицировано по cua.ai/docs/spaces, docs/cua-sdk, spaces.cua.ai, GitHub trycua/cua, TechCityAuthority 20.10.2026. Репозиторий ~30k★.

## Идея

Computer as a primitive for agents: каждому агенту — свой рабочий стол на машине, которую контролируешь (ноут, Mac mini, свой облачный аккаунт AWS/GCP/Azure/Modal). Cua не рентует compute, только relay и координация.

## Как устроено

1. **Space = один рабочий стол под задачу**: VM/контейнер с экраном и приложениями; агент работает в нём, человек смотрит тот же экран и может взять управление.
2. **`sandbox.agents()`** запускает кодинг-харнесс (Claude Code, Codex, Gemini CLI, OpenCode, Goose) в песочнице. Харнесс ставится из pinned + checksum-verified источников, управление через Agent Client Protocol, выход нормализован в события.
3. **Run переживает процесс**: состояние в `~/.cua/agents/<run>`, любой клиент может реттачнуться позже. Это прямой ответ на боль handoff: агент умер — работа продолжается.
4. **CLI `cua`**: `agent run / create / ls / logs / send / interrupt`. Флаги, follow/queue, interrupt не рвёт сессию (соответствует нашему CP-1).
5. **Multiplayer/teleport**: несколько курсоров на одном десктопе, шаринг Space по аккаунту.
6. **Старт — ~10 строк**: пример `examples/agents-in-sandboxes/tour.py`.

## Изоляция: Space против worktree

Worktree-per-Task изолирует только индекс и код. Space изолирует весь compute: файловую систему, сеть, приложения, GUI. Уровень выше, цена — сложнее делиться результатом.

## Границы и риски

- Лицензии: driver — MIT, Spaces app — FSL-1.1-MIT (source-available, запрет конкурирующих продуктов 2 года). Для внутреннего использования ок, для клиентского сетевого продукта — проверять.
- **OpenCode — официальный харнесс Cua**, прямая связка с нашим стеком.
- Hosted relay бесплатен в early access, pricing не опубликован.
- Песочницы E2B/Daytona: в доках только «sandbox service», явного подтверждения нет — перепроверить при внедрении.
- Правила Space — «инструкции, не enforcement»: Space сам апрувит свои служебные permissions внутри VM. Host-доступ не давать.

## Куда применять

Изоляция handoff-агентов: реттач плюс Space закрывают две боли — умерший процесс и доступ к секретам хоста. Лёгкая точка входа — `cua agent run` (CLI, без сборки Swift-приложения CuaBots). В дайджесте (2026-10-25) внедрение значилось заблокированным до апгрейда железа 15.11.2026; актуальный статус — в `ACTIVE_TASKS`, секция CUA.
