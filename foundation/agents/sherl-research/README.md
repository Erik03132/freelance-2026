# 🔍 SHERL-RESEARCH AGENT

## Описание

**sherl-research** — это фундаментальный агент OpenCode для сбора и структурирования данных из внешнего мира. Используется для:

- **GEO-мониторинга** — проверка присутствия брендов в AI-выдаче (ChatGPT, Perplexity, Gemini)
- **Анализа конкурентов** — аудит сайтов, сравнение фич, отслеживание изменений
- **Market Intelligence** — сбор данных о ценах, партнёрствах, инвестициях

## 🚀 Последняя прокачка (Jun 29, 2026)

Добавлена интеграция **task-prioritizer** скил��а на основе паттернов из **ContentCombine**:

### Что изменилось

✅ **Приоритизация находок** — система скорит данные по триггерам, сущностям, комбинациям  
✅ **Детектирование трендов** — автоматическое группирование по типам находок  
✅ **Обучение на решениях** — система учится на том, что важно для вас  
✅ **Множитель свежести** — свежие находки весят больше  
✅ **Независимые сигналы** — тренд = ≥2 сигнала (не одна жалоба)

## 📊 Пример использования

```python
from task_prioritizer import TaskScorer

# Инициализация
scorer = TaskScorer(project_id="competitor-research")
scorer.load_niche_config("backend")

# Находки о конкурентах
findings = [
    {
        "title": "Competitor launched AI-powered search",
        "component": "competitor_x",
        "tags": ["feature_launch", "competitive_threat"],
        "created_at": "2026-06-29T10:00:00",
    },
    {
        "title": "Competitor's database down",
        "component": "competitor_x",
        "tags": ["outage", "production"],
        "created_at": "2026-06-29T09:00:00",
        "related_issues": 5,
    },
]

# Ранжируем по приоритету
ranked = scorer.rank_tasks(findings)
# Результат: outage (94) > feature_launch (45)
```

## 🎯 Скоринг: как это работает

### Триггеры (категории событий)

| Триггер | Вес | Примеры |
|---------|-----|---------|
| production_critical | 40 | outage, down, broken |
| data_loss | 45 | corruption, backup |
| security_issue | 35 | vulnerability, exploit |
| performance_issue | 30 | slow, timeout, crash |
| api_breaking | 28 | breaking change |
| feature_request | 15 | feature, enhancement |
| tech_debt | 12 | refactor, cleanup |

### Сущности (компоненты)

```
S-tier (30): database, auth, payment, api_gateway
A-tier (15): cache, queue, logging, monitoring
B-tier (8):  frontend, admin, dashboard
C-tier (3):  docs, examples, tests
```

### Комбинации (событие + компонент)

```
critical_component_issue:    production_critical + database → +25
security_in_auth:            security_issue + auth → +20
performance_in_database:     performance_issue + database → +18
```

### Свежесть (множитель)

```
< 1 часа:      ×1.0
1-6 часов:     ×0.95
6-24 часа:     ×0.85
1-3 дня:       ×0.7
3-7 дней:      ×0.5
> 7 дней:      ×0.3
```

## 🔗 Связанные скиллы

- **brand-voice** — копирайтинг, тональность
- **task-prioritizer** — приоритизация находок (новое!)
- **search-first** — методология поиска информации

## 📁 Структура

```
sherl-research/
├── agent.yaml           # конфиг агента
├── prompt.md            # промпт и инструкции
├── skills.json          # подключённые скиллы
├── README.md            # этот файл
└── IMPLEMENTATION_REPORT.md  # подробный отчёт о прокачке
```

## 🎓 Источник идей

Архитектура основана на паттернах из **ContentCombine** (мультинишевый агрегатор новостей):
- https://habr.com/ru/articles/1052928/
- https://github.com/staurus86/contentcombine-demo

## 🔄 Roadmap

- [ ] Health-monitoring для источников данных
- [ ] Circuit-breaker для внешних API
- [ ] Feedback loop (обучение на решениях)
- [ ] Дашборд для визуализации трендов
- [ ] Экспорт в Google Sheets

