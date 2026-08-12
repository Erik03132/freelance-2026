# AGENTS.md — freelance-2026 (OpenCode + ZCode)

Единые правила работы с воркспейсом для обеих IDE (OpenCode и ZCode).

## Глобальные правила (обязательны)

**Прочитай и следуй каскадной системе:** `~/.config/opencode/AGENTS.md` —
полная каскадная система: автоматические паттерны (CONTEXT.md, ADR, Grill
Session, TDD, Two-axis Review, Handoff, eval suites, self-improvement),
политика прокси (ADR-002), графовый слой (ADR-003), каскад выбора моделей,
глобальные команды сессии.

- Отвечать всегда на русском.
- Не коммитить без явной просьбы пользователя.
- Не логировать и не коммитить секреты (.env, credentials).

## Файлы состояния проекта (общие для обеих IDE)

| Файл | Назначение |
|------|-----------|
| `ACTIVE_TASKS.md` | Активные задачи (чекбоксы). Читать при старте и обновлять по ходу |
| `SESSION_LATEST.md` | Итоги последней сессии (хвост — «что было вчера») |
| `chp.md` | Общий контекст проекта (первые строки — сводка) |
| `docs/adr/` | Architecture Decision Records |
| `CONTEXT.md` | Доменные термины проекта |

## Команды сессии

- `/start-day` → `tools/ops/start_day.sh` — начало сессии (контекст, серверы, порты, ключи)
- `/finish-day` → `tools/ops/finish_day.sh` — завершение (git-фиксация, лог сессии)

## Скиллы

Скиллы синхронизированы между `~/.config/opencode/skills/` (OpenCode) и
`~/.agents/skills/` (ZCode) через симлинки в обе стороны — физические папки и
симлинки дополняют друг друга, все актуальные версии видны в обеих IDE.
Дубли в `foundation/skills/` — устаревшая копия, НЕ использовать как источник
истины.

## Карта проектов (projectId для claude-mem)

| Проект | Путь | projectId |
|--------|------|-----------|
| Levitan (голосовые агенты) | `projects/levitan/` | `levitan` |
| AI-Scout | `projects/ai-scout/` | `ai-scout` |
| AI-Eggs (Angela) | `ai-eggs/` | `ai-eggs` |
| Angel-backend | `angel-backend/` | `angel-backend` |
| Freelance-agent | `freelance-agent/` | `freelance-agent` |
| HH AI Agent | `projects/hh-ai-agent/` | `hh-ai-agent` |
| Agent-lab | `agent-lab/` | `agent-lab` |
| AI Grant Portal | `ai-grant-portal-temp/` | `ai-grant-portal` |
| Dashboard | `dashboard/` | `dashboard` |
| Svo-start | `projects/svo-start/` | `svo-start` |
| My-project | `my-project/` | `my-project` |
| Sinergy | `projects/sinergy/` | `sinergy` |
| Глобальный/инфра | корень, `~/.config/opencode/` | `ai-bureau` |

## Архитектурные принципы

- Единый источник истины (SSoT): файлы состояния и скиллы не дублировать между IDE.
- Изменения конфигов обеих IDE синхронизировать; правки каскадной системы — только в `~/.config/opencode/AGENTS.md`.
