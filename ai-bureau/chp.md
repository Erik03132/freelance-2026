# 📌 Чекпоинт AI Bureau

## Последняя сессия
Рефакторинг системы скиллов (9ч назад):
- 8 скиллов из `.opencode/skills/` → глобальные `~/.config/opencode/skills/`
- Универсальная каскадная система в `~/.config/opencode/AGENTS.md` (4 тира, эскалация, учёт)
- Проектный `AGENTS.md` сокращён до контекста и ссылки на глобал
- SKILL.md приведены к формату с YAML frontmatter для авто-дискавери
- `night-audit: ruff --fix` (1 исправление)

## Состояние
- Сайт работает (frontend :3000, backend :3001), e2e тест пройден
- CHRONICLE.md не обновлён после рефакторинга скиллов
- `.opencode/opencode.json` — локальная конфигурация
- OpenRouter ключ рабочий, Gemini геозаблокирован

## Следующий шаг
1. Найти рабочий US/SOCKS5-прокси для Gemini
2. Добавить View Transitions API
3. CSP-метатег
4. Деплой на VPS/хостинг
