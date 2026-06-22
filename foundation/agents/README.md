# Foundation / Agents

Здесь хранятся фундаментальные агенты-роли:

| Агент | Роль |
|-------|------|
| `architect/` | Архитектура, дизайн систем |
| `researcher/` | Ресёрч, аналитика, поиск |
| `coder/` | Разработка, рефакторинг, тесты |
| `tester/` | Тестирование, QA |
| `project-manager/` | Планирование, хронология, декомпозиция |
| `igorek-core/` | Оркестратор |
| `kulibin-engineer/` | Инженер-оптимизатор |
| `marketer-strategist/` | CMO / маркетолог |
| `rembrandt-designer/` | Дизайнер |
| `shakespeare-editor/` | Редактор / копирайтер |
| `artemiy-frontend/` | Фронтенд-разработчик |
| `sherl-research/` | Исследователь рынка |
| `botman-creator/` | Создатель ботов |

## Структура одного агента

```text
foundation/agents/<agent-id>/
  agent.yaml    # роль, цели, ограничения
  prompt.md     # стиль, формат ответов
  skills.json   # какие foundation-скиллы подключать
```

## Использование в проекте

В `projects/<name>/config/agents.yaml`:

```yaml
agents:
  - id: coder
    foundation: foundation/agents/coder
    project_skills: [my-domain-skill]
```
