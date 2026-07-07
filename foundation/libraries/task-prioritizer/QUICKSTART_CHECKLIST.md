# 🚀 ЧЕКЛИСТ: Как внедрить в ТВОЙ проект за 30 минут

## Предусловие: Есть ли у тебя?
- [ ] Python 3.7+ установлен
- [ ] GitHub репозиторий с issues
- [ ] 30 минут свободного времени

---

## ВАРИАНТ A: Быстрый старт (без GitHub)

### Шаг 1: Скопировать файлы (2 мин)

```bash
# Скопировать библиотеку в твой проект
cp -r /Users/igorvasin/freelance-2026/foundation/libraries/task-prioritizer ~/my-project/

# Перейти в папку
cd ~/my-project/task-prioritizer
```

### Шаг 2: Запустить демо (1 мин)

```bash
python3 github_issues_example.py
```

**Что ты увидишь:**
```
🔴 КРИТИЧНО
1. GH-1001 (100/100) — Production database timeout
2. GH-1004 (100/100) — Security vulnerability

🟠 ВЫСОКИЙ
3. GH-1005 (73/100) — API endpoint returns 500 error
```

✅ **Готово!** Ты увидел, как это работает.

---

## ВАРИАНТ B: Подключить свой GitHub репо (15 мин)

### Шаг 1: Получить GitHub token (5 мин)

```bash
# Открыть: https://github.com/settings/tokens
# Создать новый token:
# - Name: "task-prioritizer"
# - Scopes: "repo" (read access)
# - Скопировать token

export GITHUB_TOKEN="ghp_xxx..."
```

### Шаг 2: Обновить скрипт (5 мин)

Отредактировать `github_issues_example.py`:

```python
# Найти эту строку:
# owner = "facebook"
# repo = "react"

# Изменить на:
owner = "YOUR_USERNAME"  # например "torvalds"
repo = "YOUR_REPO"       # например "linux"
github_token = os.getenv("GITHUB_TOKEN")  # твой token
```

### Шаг 3: Запустить (1 мин)

```bash
python3 github_issues_example.py
```

**Что ты увидишь:**
```
📥 Получаю issues из YOUR_USERNAME/YOUR_REPO...
✅ Получено 47 issues

🔄 Преобразую issues в формат task-prioritizer...
✅ Преобразовано 47 tasks

📊 Ранжирую issues по приоритету...

====================================================================================================
🎯 РЕЗУЛЬТАТЫ: TOP ISSUES ПО ПРИОРИТЕТУ
====================================================================================================

1. 🔴 КРИТИЧНО
   ID: GH-123
   Скор: 98/100
   Название: ...
```

✅ **Готово!** Ты видишь TOP issues своего проекта.

---

## ВАРИАНТ C: Автоматизация (10 мин)

### Шаг 1: Создать скрипт-обёртку

Создать файл `daily_prioritizer.sh`:

```bash
#!/bin/bash

export GITHUB_TOKEN="ghp_xxx..."

cd ~/my-project/task-prioritizer

# Запустить скрипт
python3 github_issues_example.py > /tmp/issues_priority.txt

# О��править в Slack (опционально)
curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
  -d @- << EOF
{
  "text": "📊 Daily Issue Priority Report",
  "attachments": [
    {
      "text": "$(cat /tmp/issues_priority.txt)"
    }
  ]
}
EOF
```

### Шаг 2: Добавить в cron (2 мин)

```bash
# Отредактировать crontab
crontab -e

# Добавить эту строку (запуск каждый день в 9:00)
0 9 * * * /path/to/daily_prioritizer.sh
```

### Шаг 3: Готово!

Каждый день в 9:00 ты будешь получать TOP issues в Slack.

---

## ВАРИАНТ D: Интеграция с Jira (20 мин)

### Шаг 1: Получить Jira token

```bash
# На Jira: Settings → API tokens
# Создать новый token
export JIRA_TOKEN="xxx..."
export JIRA_URL="https://your-company.atlassian.net"
```

### Шаг 2: Создать скрипт интеграции

Создать файл `jira_integration.py`:

```python
from task_prioritizer import TaskScorer
from jira import JIRA
import os

# Подключиться к Jira
jira = JIRA(
    os.getenv("JIRA_URL"),
    basic_auth=("email@example.com", os.getenv("JIRA_TOKEN"))
)

# Получить issues
issues = jira.search_issues("status = Open")

# Преобразовать в tasks
tasks = []
for issue in issues:
    tasks.append({
        "id": issue.key,
        "title": issue.fields.summary,
        "tags": [label for label in issue.fields.labels],
        "created_at": issue.fields.created,
    })

# Ранжировать
scorer = TaskScorer(project_id="jira-issues")
scorer.load_niche_config("backend")
ranked = scorer.rank_tasks(tasks)

# Обновить приоритет в Jira
for task in ranked[:10]:
    issue = jira.issue(task["id"])
    priority = "Highest" if task["priority_score"] > 80 else \
               "High" if task["priority_score"] > 60 else \
               "Medium" if task["priority_score"] > 30 else "Low"
    issue.update(priority={'name': priority})
    print(f"✅ {task['id']}: {priority}")
```

### Шаг 3: Запустить

```bash
python3 jira_integration.py
```

**Результат:** Приоритеты в Jira автоматически обновлены!

---

## ВАРИАНТ E: Собственный источник данных (15 мин)

Если у тебя данные не в GitHub/Jira, а в Slack/Email/Custom:

### Шаг 1: Создать функцию парсинга

```python
def get_tasks_from_slack():
    """Получить задачи из Slack"""
    client = slack_sdk.WebClient(token=SLACK_TOKEN)
    
    # Получить сообщения из канала
    result = client.conversations_history(channel="C123456")
    
    # Преобразовать в tasks
    tasks = []
    for msg in result["messages"]:
        if "bug" in msg["text"].lower() or "issue" in msg["text"].lower():
            tasks.append({
                "id": msg["ts"],
                "title": msg["text"][:100],
                "tags": extract_tags(msg["text"]),
                "created_at": msg["ts"],
                "reactions": len(msg.get("reactions", [])),
            })
    
    return tasks

# Использовать
tasks = get_tasks_from_slack()
scorer = TaskScorer(project_id="slack-issues")
ranked = scorer.rank_tasks(tasks)
```

---

## 📋 ЧЕКЛИСТ ВНЕДРЕНИЯ

### День 1: Setup (30 мин)
- [ ] Скопировать файлы
- [ ] Запустить демо
- [ ] Увидеть результаты
- [ ] Понять, как это работает

### День 2: Интеграция (1 час)
- [ ] Подключить свой GitHub/Jira
- [ ] Запустить на реальных данных
- [ ] Показать команде результаты
- [ ] Получить feedback

### День 3: Автоматизация (30 мин)
- [ ] Добавить в cron
- [ ] Настроить Slack notifications
- [ ] Готово к ежедневному использованию

### День 4+: Оптимизация
- [ ] Обновить конфиг на основе feedback
- [ ] Добавить новые триггеры/сущности
- [ ] Масштабировать на другие источники

---

## 🚨 Частые проблемы и решения

### Проблема 1: "ModuleNotFoundError: No module named 'task_prioritizer'"

**Решение:**
```bash
# Убедись, что путь правильный
export PYTHONPATH="/Users/igorvasin/freelance-2026/foundation/libraries:$PYTHONPATH"

# Или скопировать файл в текущую папку
cp /Users/igorvasin/freelance-2026/foundation/libraries/task-prioritizer/task_prioritizer.py .
```

### Проблема 2: "GitHub API rate limit exceeded"

**Решение:**
```bash
# Использовать token
export GITHUB_TOKEN="ghp_xxx..."

# Или уменьшить количество issues
# В скрипте изменить: per_page=100 → per_page=30
```

### Проблема 3: "Скор всех issues = 0"

**Решение:**
```python
# Проверить, что labels содержат нужные ключи
# Например, "bug" должен быть в labels

# Или обновить конфиг:
scorer.load_niche_config("backend")  # правильный конфиг

# Или добавить больше триггеров в конфиг
```

---

## ✅ КАК УЗНАТЬ, ЧТО ВСЁ РАБОТАЕТ?

### Признак 1: Видишь TOP issues

```
✅ Если видишь:
🔴 КРИТИЧНО
1. GH-1001 (100/100) — Production issue

❌ Если видишь:
Всё issues имеют скор 0
```

### Признак 2: Скоры разные

```
✅ Если видишь:
1. 100/100
2. 85/100
3. 50/100
4. 20/100
5. 0/100

❌ Если видишь:
1. 50/100
2. 50/100
3. 50/100 (все одинаковые)
```

### Признак 3: Анализ имеет смысл

```
✅ Если видишь:
"production_critical (40) + database (30) + critical_component_issue (25)"
└─ Имеет смысл: production + database = высокий приоритет

❌ Если видишь:
"No triggers or entities detected"
└─ Нужно обновить labels в GitHub
```

---

## 🎓 СЛЕДУЮЩИЕ ШАГИ

После успешного внедрения:

### Неделя 1: Наблюдение
- [ ] Запускать скрипт каждый день
- [ ] Смотреть на TOP issues
- [ ] Начинать с первого

### Неделя 2: Оптимизация
- [ ] Собрать feedback от команды
- [ ] Обновить триггеры/сущности
- [ ] Добавить новые labels в GitHub

### Неделя 3: Масштабирование
- [ ] Добавить второй источник (Sentry, Jira)
- [ ] Настроить автоматизацию (cron, Slack)
- [ ] Создать dashboard

### Неделя 4+: Production
- [ ] Полная автоматизация
- [ ] Интеграция со всеми источниками
- [ ] Обучение команды

---

## 📞 НУЖНА ПОМОЩЬ?

**Файлы для справки:**
- `GITHUB_ISSUES_EXPLAINED.md` — подробное объяснение
- `github_issues_example.py` — полный рабочий код
- `PRACTICAL_GUIDE.md` — 5 сценариев использования
- `APPLICATION_MATRIX.md` — матрица применения

**Команды для быстрого старта:**
```bash
# Демо
python3 github_issues_example.py

# С GitHub token
GITHUB_TOKEN="ghp_xxx" python3 github_issues_example.py

# С реальным репо
python3 github_issues_example.py --owner facebook --repo react
```

---

## ✨ ИТОГ

Ты можешь внедрить task-prioritizer за **30 минут** и сразу увидеть результаты.

Начни с Варианта A (демо) → Вариант B (свой GitHub) → Вариант C (автоматизация).

**Первый результат: TOP issues видны, хаос исчезает!** 🚀
