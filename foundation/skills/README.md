# Foundation / Skills

Здесь хранятся фундаментальные (универсальные) навыки, которые переиспользуются в 2+ проектах.

## Структура

```text
foundation/skills/<domain>/<skill-name>/
  skill.yaml    # описание навыка
  prompt.md     # основной промпт
  examples.md   # примеры использования
  tests/        # тестовые сценарии
  README.md     # 10–20 строк: что делает, когда применять
```

## Домены

| Домен | Назначение |
|-------|------------|
| `text/` | Работа с текстом: суммаризация, классификация, перевод |
| `code/` | Программирование: рефакторинг, генерация тестов, архитектурный обзор |
| `productivity/` | Планирование, заметки, исследования |
| `business/` | Бизнес-специфичные навыки: интеграции, деплой, голос бренда |

## Текущие foundation-скиллы

| Скилл | Домен | Где используется |
|-------|-------|------------------|
| `angelochka-sales` | business | ai-eggs, angel-backend |
| `bitrix-integration` | business | ai-eggs, ai-grant-consalt |
| `brand-voice` | business | все проекты |
| `deployment-procedures` | business | все проекты |
| `geo-fundamentals` | business | ai-eggs, ai-grant-consalt |
| `telegram-bot-patterns` | business | ai-eggs, ai-grant-consalt |
| `react-patterns` | code | все frontend-проекты |

## Как добавить новый скилл

```bash
./tools/new-skill.sh <domain> <skill-name>
```

> Если такого скрипта ещё нет — скопируй `templates/skill-skeleton/` в нужный домен.
