# PROJECT_CONTEXT — freelance-2026

> Этот файл — «карта репозитория» для IDE-агентов.
> Его должны читать Cursor, OpenCode и Antigravity при входе в проект.

## Что это за репозиторий

Монорепозиторий фриланс-проектов: AI-агенты, RAG, голосовой AI, веб-разработка, автоматизация.

Каскадная система, глобальные OpenCode-скиллы и правила эскалации: `~/.config/opencode/AGENTS.md`

## Структура (целевая)

```text
/freelance-2026/
├── foundation/                 # Универсальные скиллы и агенты
│   ├── skills/<domain>/<skill>/
│   ├── agents/<agent>/
│   └── libraries/
├── projects/                   # Активные проекты
│   └── <project-name>/
│       ├── config/
│       │   ├── project.yaml
│       │   ├── agents.yaml
│       │   └── skills.yaml
│       ├── project-skills/
│       ├── project-agents/
│       ├── src/
│       ├── docs/
│       │   ├── overview.md
│       │   ├── architecture.md
│       │   └── decisions.md
│       └── logs/
│           ├── timeline.md
│           └── sessions/
├── archive/                    # Закрытые/замороженные проекты
├── templates/
│   ├── project-skeleton/
│   ├── skill-skeleton/
│   └── agent-skeleton/
├── tools/                      # Глобальные скрипты
├── docs/                       # Глобальная документация
├── chronicles/                 # Глобальная хронология
└── AGENTS.md                   # Карта репозитория
```

## Быстрые команды

```bash
# Новый проект
./tools/new-project.sh <project-name>

# Новый foundation-скилл
./tools/new-skill.sh <domain> <skill-name>

# Новый foundation-агент
./tools/new-agent.sh <agent-id>
```

## Как работать с проектом

1. Открой `projects/<name>/AGENTS.md` — проектный контекст.
2. Прочитай `projects/<name>/config/project.yaml` — цели, стек, метрики.
3. Прочитай `projects/<name>/docs/overview.md` и `architecture.md`.
4. Вноси изменения.
5. Обнови `projects/<name>/docs/decisions.md` (ADR) и `logs/timeline.md`.

## Правила размещения

- **Foundation** (используется в 2+ проектах) → `foundation/`
- **Проектный код** → `projects/<name>/src/`
- **Проектные скиллы** → `projects/<name>/project-skills/`
- **Проектные агенты** → `projects/<name>/project-agents/`
- **Архив** → `archive/`
- **Глобальные скрипты** → `tools/`
- **Эксперименты** → `projects/agent-lab/`

## Статус миграции

- ✅ Phase 0 + Phase 1: создан каркас `foundation/`, `projects/`, `archive/`, `templates/`, `tools/new-project.sh`
- ✅ Phase 2: перенос существующих проектов из корня в `projects/`
- ✅ Phase 3: дедублицикация скиллов и перенос их в `foundation/skills/`
- ✅ Phase 4: создание `config/*.yaml` для каждого активного проекта
- ✅ Phase 5: перенос глобальных скриптов из корня в `tools/`
- ✅ Phase 6: обновление IDE-адаптеров (OpenCode + Antigravity; Cursor — пока нет)

## Для разных IDE

### Cursor
- Этот файл (`PROJECT_CONTEXT.md`) — главный контекст.
- Правила IDE: `.cursor/rules/global/` и `.cursor/rules/project/`
- При работе с проектом указывай файлы через `@projects/<name>/docs/overview.md`, `@projects/<name>/config/project.yaml`

### OpenCode
- Глобальные правила: `~/.config/opencode/AGENTS.md`
- Проектный контекст: `projects/<name>/AGENTS.md`
- Скиллы: `~/.config/opencode/skills/` (глобальные) + `foundation/skills/` (репо-уровень)

### Antigravity
- Глобальные правила: `.agent/rules/`
- Агенты: `foundation/agents/` + `projects/<name>/project-agents/`
- Скиллы: `foundation/skills/` + `projects/<name>/project-skills/`
