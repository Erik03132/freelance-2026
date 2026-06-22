# IDE Guide — freelance-2026

> Как работать в разных IDE со старыми и новыми проектами.

---

## Какие IDE используем

| IDE | Конфиг | Для чего |
|-----|--------|----------|
| **OpenCode** | `.opencode/opencode.json` | Основная IDE. Агентная работа, рефакторинг, разработка. |
| **Antigravity** | `.agent/rules/IRON_RULES.md` | Нативный AI-агент. Boot, finish-day, деплой. |
| **Cursor** | `.cursor/rules/` | Планируется. Правила уже готовы, но Cursor пока не активен. |
| **VS Code** | без спецконфига | Быстрые правки, когда агент не нужен. |

---

## Новый проект — создание с нуля

```bash
# 1. Создать каркас проекта
./tools/go.sh new project ai-sales-assistant

# ИЛИ напрямую:
./tools/new-project.sh ai-sales-assistant

# 2. Открыть проект в IDE
#    a) OpenCode — открой корень репозитория. Контекст подтянется из PROJECT_CONTEXT.md.
#    b) VS Code — code projects/ai-sales-assistant

# 3. Заполнить конфиг
#    projects/ai-sales-assistant/config/project.yaml     ← цели, стек, метрики
#    projects/ai-sales-assistant/docs/overview.md         ← описание проекта
#    projects/ai-sales-assistant/docs/architecture.md     ← архитектура

# 4. Добавить проектные скиллы (если нужны)
mkdir -p projects/ai-sales-assistant/project-skills/my-skill
cp -R templates/skill-skeleton/* projects/ai-sales-assistant/project-skills/my-skill/

# 5. Закоммитить
git add projects/ai-sales-assistant
git commit -m "chore: init project ai-sales-assistant"
```

---

## Старый проект — как открыть и начать работу

### OpenCode
1. Открой **корень** репозитория (`/Users/igorvasin/freelance-2026/`).
2. OpenCode прочитает `AGENTS.md` → `PROJECT_CONTEXT.md` → каскадная система из `~/.config/opencode/AGENTS.md`.
3. Скажи агенту: **«работаем над projects/<имя>»**.
4. Агент сам прочитает `projects/<имя>/AGENTS.md`, `config/project.yaml`, `docs/overview.md`.

### Antigravity
1. Запусти сессию командой: **«boot»** / **«старт»**.
2. Antigravity выполнит boot sequence из `IRON_RULES.md` §7.
3. Укажи проект: **«работаем над <имя>»**.

### VS Code
1. `code .` — открыть весь репозиторий.
2. Просмотри `projects/<имя>/docs/overview.md` и `config/project.yaml` вручную — контекст не инжектится автоматически.

---

## Быстрые команды

```bash
# Создать новый проект
./tools/go.sh new project <name>
# → projects/<name>/ со всей структурой

# Создать foundation-скилл
./tools/go.sh new skill <domain> <name>
# → foundation/skills/<domain>/<name>/

# Создать foundation-агента
./tools/go.sh new agent <agent-id>
# → foundation/agents/<agent-id>/

# Boot (проверка готовности)
./tools/go.sh boot
# → проверяет API, считает агентов, читает чекпоинт
```

---

## Где лежат скиллы и агенты

```
foundation/skills/<domain>/<skill>/    ← Foundation (2+ проекта используют)
foundation/agents/<agent>/              ← Foundation-агенты
projects/<name>/project-skills/<skill>/ ← Проектные скиллы (только для этого проекта)
projects/<name>/project-agents/<agent>/ ← Проектные агенты
~/.config/opencode/skills/              ← Глобальные OpenCode-скиллы
```

**Правило:** если скилл нужен в 2+ проектах → `foundation/`. Если только в одном → `projects/<name>/project-skills/`.

---

## Контекстные файлы (что читает агент при входе)

| Файл | Кто читает | Назначение |
|------|------------|------------|
| `AGENTS.md` | OpenCode, Antigravity | Карта репозитория и роадмап |
| `PROJECT_CONTEXT.md` | OpenCode, Cursor | Структурная карта для IDE |
| `projects/<name>/AGENTS.md` | Все агенты | Проектный контекст |
| `.agent/rules/IRON_RULES.md` | Antigravity | Железные правила |
| `foundation/skills/MANIFEST.md` | Все агенты | Каталог foundation-скиллов |
| `chp.md` | Antigravity | Чекпоинт текущего состояния |

---

## Отличия старого и нового подходов

| | Старый подход (до рефакторинга) | Новый подход (после Phase 6) |
|---|---|---|
| **Скиллы** | Дубли в каждом проекте | Foundation + проектные (без дублей) |
| **Агенты** | Разбросаны по проектам | Foundation + проектные |
| **Скрипты** | В корне репозитория | `tools/` |
| **Проект** | Вручную создаёшь папку | `./tools/go.sh new project <name>` |
| **Контекст** | Читать всё вручную | `PROJECT_CONTEXT.md` + автоинжект через `AGENTS.md` |
| **Конфиг** | Не было | `projects/<name>/config/{project,agents,skills}.yaml` |
