# 📑 INDEX: Все файлы прокачки Шерлока

## 📍 Основные файлы sherl-research

### 1. **agent.yaml** — конфиг агента
```
/Users/igorvasin/freelance-2026/foundation/agents/sherl-research/agent.yaml
```
- Описание агента
- Подключённые инструменты
- Список скилов

### 2. **prompt.md** — промпт и инструкции
```
/Users/igorvasin/freelance-2026/foundation/agents/sherl-research/prompt.md
```
- Цель агента
- Инструкции по использованию
- Constraints
- **НОВОЕ:** Описание task-prioritizer скилла

### 3. **skills.json** — подключённые скилы
```
/Users/igorvasin/freelance-2026/foundation/agents/sherl-research/skills.json
```
- **ОБНОВЛЕНО:** Добавлен `task-prioritizer`
- Список foundation skills
- Список project skills

### 4. **README.md** — документация
```
/Users/igorvasin/freelance-2026/foundation/agents/sherl-research/README.md
```
- Описание агента
- Примеры использования
- Скоринг система
- Roadmap

### 5. **IMPLEMENTATION_REPORT.md** — подробный отчёт
```
/Users/igorvasin/freelance-2026/foundation/agents/sherl-research/IMPLEMENTATION_REPORT.md
```
- Полный отчёт о прокачке
- Архитектура решения
- Боевые уроки из ContentCombine

---

## 🎯 Новый скилл: task-prioritizer

### 1. **SKILL.md** — полная документация
```
/Users/igorvasin/freelance-2026/foundation/skills/code/task-prioritizer/SKILL.md
```
- Когда использовать
- Быстрый старт
- Архитектура скоринга
- Примеры использования
- API Reference
- Боевые грабли

**Размер:** 180+ строк документации

---

## 💻 Python-библиотека

### 1. **task_prioritizer.py** — основной модуль
```
/Users/igorvasin/freelance-2026/foundation/libraries/task-prioritizer/task_prioritizer.py
```
- `TaskScorer` — основной класс
- `TriggerConfig`, `EntityConfig`, `ComboConfig` — конфиги
- `ScoringResult` — результат скоринга
- Методы: `score_task()`, `rank_tasks()`, `detect_trend()`, `record_decision()`

**Размер:** 500+ строк рабочего кода

### 2. **demo.py** — полная демонстрация
```
/Users/igorvasin/freelance-2026/foundation/libraries/task-prioritizer/demo.py
```
- DEMO 1: Базовый скоринг задач
- DEMO 2: Ранжирование по приоритету
- DEMO 3: Детектирование трендов
- DEMO 4: Исследование конкурентов (sherl-research use case)
- DEMO 5: Множитель свежести

**Размер:** 250+ строк

**Запуск:** `python3 demo.py`

### 3. **quickstart.py** — примеры использования
```
/Users/igorvasin/freelance-2026/foundation/libraries/task-prioritizer/quickstart.py
```
- ПРИМЕР 1: Базовое использование
- ПРИМЕР 2: Ранжирование списка задач
- ПРИМЕР 3: Использование в sherl-research
- ПРИМЕР 4: Детектирование трендов
- ПРИМЕР 5: Обучение на решениях

**Размер:** 200+ строк

**Запуск:** `python3 quickstart.py`

---

## 📊 Статистика

| Файл | Строк | Тип |
|------|-------|-----|
| SKILL.md | 180+ | Документация |
| task_prioritizer.py | 500+ | Python код |
| demo.py | 250+ | Примеры |
| quickstart.py | 200+ | Примеры |
| prompt.md | 30+ | Обновление |
| README.md | 80+ | Документация |
| IMPLEMENTATION_REPORT.md | 300+ | Отчёт |
| **ИТОГО** | **1540+** | - |

---

## 🚀 Как использовать

### Вариант 1: Импортировать в свой проект

```python
from task_prioritizer import TaskScorer

scorer = TaskScorer(project_id="my-project")
scorer.load_niche_config("backend")

score = scorer.score_task({...})
```

### Вариант 2: Запустить демонстрацию

```bash
cd /Users/igorvasin/freelance-2026/foundation/libraries/task-prioritizer
python3 demo.py
```

### Вариант 3: Запустить примеры

```bash
cd /Users/igorvasin/freelance-2026/foundation/libraries/task-prioritizer
python3 quickstart.py
```

---

## 🔗 Структура папок

```
foundation/
├── agents/
│   └── sherl-research/
│       ├── agent.yaml                    ✅ Обновлён
│       ├── prompt.md                     ✅ Обновлён
│       ├── skills.json                   ✅ Обновлён
│       ├── README.md                     ✅ Новый
│       ├── IMPLEMENTATION_REPORT.md      ✅ Новый
│       └── FILES_INDEX.md                ✅ Этот файл
│
├── skills/
│   └── code/
│       └── task-prioritizer/
│           └── SKILL.md                  ✅ Новый
│
└── libraries/
    └── task-prioritizer/
        ├── task_prioritizer.py           ✅ Новый
        ├── demo.py                       ✅ Новый
        └── quickstart.py                 ✅ Новый
```

---

## 📚 Источники

- **ContentCombine статья:** https://habr.com/ru/articles/1052928/
- **ContentCombine демо:** https://github.com/staurus86/contentcombine-demo
- **OpenCode документация:** https://opencode.ai/docs

---

## ✅ Чек-лист внедрения

- [x] Анализ ContentCombine
- [x] Проектирование архитектуры
- [x] Создание скилла task-prioritizer
- [x] Реализация Python-библиотеки
- [x] Обновление конфигов Шерлока
- [x] Написание документации
- [x] Создание демонстраций
- [x] Тестирование
- [ ] Health-monitoring (Tier 2)
- [ ] Circuit-breaker (Tier 2)
- [ ] Feedback loop (Tier 2)

---

## 🎓 Что дальше

После освоения task-prioritizer можно добавить:

1. **Health-monitoring** — отслеживание доступности источников
2. **Circuit-breaker** — обработка отказов внешних API
3. **Feedback loop** — обучение на решениях разработчика
4. **Дашборд** — визуализация трендов
5. **Экспорт** — выгрузка в Google Sheets

---

## 📞 Контакты

Вопросы по реализации? Смотри:
- IMPLEMENTATION_REPORT.md — полный отчёт
- SKILL.md — документация скилла
- demo.py — примеры работы

