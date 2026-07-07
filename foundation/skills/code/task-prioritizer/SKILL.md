---
name: task-prioritizer
description: Система приоритизации задач разработки на основе ContentCombine-паттернов. Скоринг триггерами, сущностями, весами и свежестью. Для sherl-research и других агентов.
tags: [sherl-research, prioritization, scoring, automation]
---

## Когда использовать

- Нужно приоритизировать задачи разработки (bug vs feature vs tech-debt)
- Хочешь оценить критичность проблемы (production-critical vs low-priority)
- Требуется автоматический score для задач на основе множественных факторов
- Нужна система для отслеживания тренда (много задач одного типа = тренд)
- Хочешь обучать систему на решениях разработчика (feedback loop)

## Философия

Адаптация паттернов из **ContentCombine** (агрегатор новостей) для приоритизации задач разработки:

```
ContentCombine: новость → триггеры + сущности + свежесть → скор → тренд
Task Prioritizer: задача → типы + компоненты + urgency → скор → приоритет
```

Система считает не "сколько задач", а "сколько независимых сигналов" указывают на важность.

## Быстрый старт

### 1. Инициализация скорера

```python
from task_prioritizer import TaskScorer, TaskTrigger, Entity

# Создаём скорер для проекта
scorer = TaskScorer(
    project_id="my-project",
    niche="backend",  # или "frontend", "devops", etc.
)

# Загружаем конфиг ниши (триггеры, сущности, веса)
scorer.load_niche_config("backend")
```

### 2. Скоринг задачи

```python
task = {
    "id": "TASK-123",
    "title": "Production database connection drops under load",
    "description": "PostgreSQL connections timeout after 100 concurrent users",
    "component": "database",
    "tags": ["production", "urgent", "bug"],
    "created_at": "2026-06-29T10:00:00",
    "related_issues": 3,  # сколько других задач связано
}

score = scorer.score_task(task)
print(score)
# Output: {
#   "total": 92,
#   "triggers": {"production_critical": 40, "performance": 30},
#   "entities": {"postgresql": 15},
#   "combos": {"critical_component": 25},
#   "freshness": 1.0,
#   "independent_signals": 4,
#   "breakdown": "Production bug + DB component + Performance issue + 3 related tasks"
# }
```

### 3. Приоритизация ленты задач

```python
tasks = [
    {"id": "T1", "title": "Fix typo in README", ...},
    {"id": "T2", "title": "Database crashes on load", ...},
    {"id": "T3", "title": "Add dark mode toggle", ...},
]

ranked = scorer.rank_tasks(tasks)
# Результат отсортирован по score (выше = важнее)
# T2 (92) → T3 (45) → T1 (5)
```

## Архитектура скоринга

### Компоненты

```
Task → Trigger Detection → Entity Extraction → Combo Matching → Freshness Decay → Final Score
         (категории)         (компоненты)      (события)        (время)
```

### 1. Trigger Detection (Триггеры)

Триггер — это категория события с весом. Примеры для backend:

| Триггер | Вес | Примеры ключей |
|---------|-----|----------------|
| production_critical | 40 | "production", "prod", "critical", "outage", "down" |
| performance_issue | 30 | "slow", "timeout", "crash", "memory leak", "CPU" |
| security_issue | 35 | "vulnerability", "exploit", "security", "auth", "XSS" |
| data_loss | 45 | "data loss", "corruption", "backup", "recovery" |
| api_breaking | 28 | "breaking change", "API", "deprecation", "migration" |
| tech_debt | 12 | "refactor", "cleanup", "technical debt", "legacy" |
| feature_request | 15 | "feature", "enhancement", "new", "add support" |
| documentation | 5 | "docs", "README", "comment", "docstring" |

**Дедупликация по категории:** Если задача содержит несколько триггеров из одной категории (например, "production" и "prod"), берётся только самый весомый.

### 2. Entity Extraction (Сущности)

Сущность — это компонент/сервис с тиром важности:

```yaml
entities:
  S-tier:  # критичные компоненты (+30)
    - database
    - auth
    - payment
    - api-gateway
  A-tier:  # важные (+15)
    - cache
    - queue
    - logging
    - monitoring
  B-tier:  # обычные (+8)
    - frontend
    - admin-panel
    - dashboard
  C-tier:  # низкий приоритет (+3)
    - docs
    - examples
    - tests
```

### 3. Combo Matching (Комбинации)

Пара "событие + компонент" считается отдельно, потому что вместе они значат больше:

```yaml
combos:
  - name: "critical_component_issue"
    triggers: ["production_critical", "data_loss"]
    entities: ["S-tier"]
    bonus: 25  # дополнительный скор

  - name: "security_in_auth"
    triggers: ["security_issue"]
    entities: ["auth"]
    bonus: 20

  - name: "performance_in_database"
    triggers: ["performance_issue"]
    entities: ["database"]
    bonus: 18
```

### 4. Freshness Decay (Свежесть как множитель)

Старые задачи теряют актуальность. Множитель:

```
< 1 часа:      ×1.0   (полный вес)
1-6 часов:     ×0.95
6-24 часа:     ×0.85
1-3 дня:       ×0.7
3-7 дней:      ×0.5
> 7 дней:      ×0.3
```

Старая критичная задача может быть решена, поэтому не стоит её переоценивать.

### 5. Independent Signals (Независимые сигналы)

Тренд = ≥2 независимых сигнала (как в ContentCombine). Сигналы:

1. Задача помечена тегом `production`
2. Задача содержит триггер `critical`
3. Компонент в S-tier
4. Есть связанные задачи (≥2)
5. Много реакций/комментариев (≥5)

Если ≥2 сигнала совпадают → это реальный приоритет, а не одинокая жалоба.

## Примеры использования

### Пример 1: Простой баг

```python
task = {
    "title": "Fix typo in error message",
    "component": "frontend",
    "tags": ["bug", "low-priority"],
    "created_at": "2026-06-29T14:00:00",
}

score = scorer.score_task(task)
# Output: {"total": 8, "breakdown": "Bug (5) + Frontend component (3)"}
```

### Пример 2: Production outage

```python
task = {
    "title": "Database connection pool exhausted - API down",
    "description": "PostgreSQL connections timeout. Affects all users.",
    "component": "database",
    "tags": ["production", "critical", "urgent"],
    "created_at": "2026-06-29T10:00:00",
    "related_issues": 5,  # много связанных задач
    "reactions": 12,  # много реакций от команды
}

score = scorer.score_task(task)
# Output: {
#   "total": 94,
#   "triggers": {
#     "production_critical": 40,
#     "performance_issue": 30
#   },
#   "entities": {"database": 30},  # S-tier component
#   "combos": {"critical_component_issue": 25},
#   "independent_signals": 5,
#   "breakdown": "Production + Performance + DB (S-tier) + 5 related + High engagement"
# }
```

### Пример 3: Security vulnerability

```python
task = {
    "title": "XSS vulnerability in user input validation",
    "component": "auth",
    "tags": ["security", "vulnerability"],
    "created_at": "2026-06-29T09:30:00",
}

score = scorer.score_task(task)
# Output: {
#   "total": 85,
#   "triggers": {"security_issue": 35},
#   "entities": {"auth": 30},  # S-tier
#   "combos": {"security_in_auth": 20},
#   "independent_signals": 3,
# }
```

## Конфигурирование под нишу

Каждый проект/язык имеет свой конфиг. Пример для `backend.yaml`:

```yaml
niche: backend

triggers:
  production_critical:
    weight: 40
    keys: ["production", "prod", "critical", "outage", "down", "broken"]
  
  performance_issue:
    weight: 30
    keys: ["slow", "timeout", "crash", "memory leak", "CPU spike"]
  
  security_issue:
    weight: 35
    keys: ["vulnerability", "exploit", "security", "auth", "XSS", "injection"]

entities:
  database:
    tier: S
    boost: 30
  
  auth:
    tier: S
    boost: 30
  
  cache:
    tier: A
    boost: 15
  
  frontend:
    tier: B
    boost: 8

combos:
  - name: "critical_component_issue"
    triggers: ["production_critical", "data_loss"]
    entities: ["database", "auth"]
    bonus: 25

min_signals_for_trend: 2
max_score: 100
```

## Обучение на решениях (Feedback Loop)

Система может обучаться на решениях разработчика:

```python
# Разработчик решил задачу
scorer.record_decision(
    task_id="TASK-123",
    action="resolved",  # или "postponed", "rejected"
    time_to_resolution=3600,  # секунды
    difficulty="high",  # субъективная оценка
)

# Система пересчитывает веса источников
# Если разработчик часто решает задачи с определённым триггером → вес растёт
# Если часто откладывает → вес падает
```

## API Reference

### TaskScorer

```python
class TaskScorer:
    def __init__(self, project_id: str, niche: str)
    
    def load_niche_config(self, niche: str) -> None
    
    def score_task(self, task: dict) -> dict
        # Returns: {"total": int, "triggers": dict, "entities": dict, ...}
    
    def rank_tasks(self, tasks: list[dict]) -> list[dict]
        # Returns: tasks отсортированные по score
    
    def detect_trend(self, tasks: list[dict]) -> list[dict]
        # Returns: сгруппированные задачи по триггерам/компонентам
    
    def record_decision(self, task_id: str, action: str, **kwargs) -> None
        # Обучение на решениях
    
    def get_source_health(self) -> dict
        # Статистика по каждому триггеру/компоненту
```

## Интеграция с sherl-research

Шерлок использует этот скилл для приоритизации находок:

```python
# В sherl-research агенте
findings = search_competitors()  # находим данные о конкурентах

# Скорим каждую находку
for finding in findings:
    score = scorer.score_task({
        "title": finding["title"],
        "component": finding["competitor"],
        "tags": finding["types"],  # "price_change", "new_feature", etc.
        "created_at": finding["date"],
    })
    
    finding["priority_score"] = score["total"]

# Возвращаем отсортированные по приоритету
ranked = sorted(findings, key=lambda x: x["priority_score"], reverse=True)
```

## Боевые грабли из ContentCombine

Автор статьи столкнулся с этими проблемами и их решениями:

### 1. Гипер-частые сущности слипаются в блоб

**Проблема:** Google, ChatGPT, "нейросети" встречаются в половине задач → всё склеивается в один сюжет.

**Решение:** Выкинуть из пересечения сущности, которые встречаются >10% пачки.

```python
def filter_common_entities(entities, task_list, threshold=0.1):
    frequency = {e: 0 for e in entities}
    for task in task_list:
        for e in task.get("entities", []):
            if e in frequency:
                frequency[e] += 1
    
    # Выкидываем частые (>10%)
    return [e for e in entities if frequency[e] / len(task_list) < threshold]
```

### 2. Тренд = независимые сигналы, не похожие названия

**Проблема:** Две абсолютно несвязанные задачи имеют одно слово → система их склеивает.

**Решение:** Требуется лексическое совпадение + сущность только усиливает, не создаёт с нуля.

### 3. Проверь тупые константы

**Проблема:** `LIMIT 500` в БД → 2/3 материалов не участвуют в анализе.

**Решение:** Регулярно проверяй логи и метрики.

## Что дальше

- [ ] Добавить health-monitoring для источников (как в ContentCombine)
- [ ] Реализовать circuit-breaker для внешних API
- [ ] Интегрировать с claude-mem для обучения на истории
- [ ] Создать дашборд для визуализации трендов
- [ ] Добавить экспорт в Google Sheets для ручного ревью
