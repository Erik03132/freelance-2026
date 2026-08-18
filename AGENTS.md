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
| Voice Agent Manager (AVM) | `projects/ai-bureau/ai-voice-manager/` | `avm` |
| Глобальный/инфра | корень, `~/.config/opencode/` | `ai-bureau` |

## Архитектурные принципы

- Единый источник истины (SSoT): файлы состояния и скиллы не дублировать между IDE.
- Изменения конфигов обеих IDE синхронизировать; правки каскадной системы — только в `~/.config/opencode/AGENTS.md`.

## Правила для обеих IDE (инфраструктура ZCode)

Файл `AGENTS.md` в корне воркспейса читают **обе** IDE (OpenCode и ZCode/Claude-стек).
Ниже — правила, которые должны действовать независимо от IDE.

### CLI для агентов — чек-лист (CP-1, из cursor/plugins `cli-for-agent`)

Любой скрипт/команда, которую вызывает агент (а не человек в терминале), обязан
удовлетворять чек-листу. Агент не читает README — он зовёт `--help` и смотрит на код выхода.

1. **Flags, не позиционные аргументы** — `script.py --file x --dry-run`, не `script.py x`.
2. **`--help` с примерами** — не только опции, но и 1-2 готовых примера (аргументы в кавычках).
3. **`--dry-run` всегда** — команда ничего не меняет без `--dry-run`; выводит, что сделала бы (для разрушающих операций — обязательно).
4. **Идемпотентность** — повторный запуск с тем же входом не ломает состояние и безопасен.
5. **Явные ошибки** — на сбой: причина в `stderr`, код выхода `!= 0`, без «пустого успеха».
6. **Pipeline-safe** — читает `stdin`/файл, пишет в `stdout`/файл, не интерактивен, работает под timeout.
7. **Путь к проекту** — не хардкодит `cwd`; принимает корень аргументом (агент запускает из `workdir`).

Проверка готова, когда агент может выполнить шаг по `--help` без чтения исходников.

### Worktree-per-Task (OR-2, паттерн из Orca ADE)

При параллельных/конкурентных задачах каждая идёт в **свой `git worktree`** —
агенты не конфликтуют за индекс, результат merge по победителю.

- Параллельные задачи → `git worktree add <path> -b <task-branch>` на задачу.
- Несколько кандидатов решения (A/B фикса, варианты лендинга) → N worktree → сравнить → merge лучший.
- Очистка после merge: `git worktree remove <path>`.
- В OpenCode есть нативные команды-обёртки (`/experimental/worktree`); в ZCode/Claude-стеке — нативные `git worktree`. Паттерн работает одинаково в обеих.
