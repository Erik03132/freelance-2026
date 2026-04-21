# 🚀 Freelance Agent — Быстрый старт

## ⚡ Утром начать работу (Соблюдая Ритуал):

```bash
# 1. СВЯЩЕННЫЙ РИТУАЛ №1: Проверить системы (Sherlock Start)
cd /Users/igorvasin/freelance-2026/freelance-agent && npm run sherlock-start

# 2. ЗАПУСК МОНИТОРИНГА: Начать фоновый сбор заказов
cd /Users/igorvasin/freelance-2026/freelance-agent && npm run agents-start

# 3. ЦЕНТР УПРАВЛЕНИЯ: Запустить Дашборд (на порту 3010)
cd /Users/igorvasin/freelance-2026/dashboard && PORT=3010 npm run dev
```

**Полный список процедур:** см. `RITUALS.md` в корне проекта.


---

## 🆕 Персонализированные предложения

### Настройка НЕ требуется!

Генератор создаёт **уникальный план выполнения** под каждую задачу.

### Использование:

1. Откройте http://localhost:3010
2. Выберите задачу
3. Нажмите **"🪄 Сгенерировать через AI"**
4. Получите персонализированное предложение

**Что делает генератор:**
- ✅ Анализирует тип задачи (8 категорий)
- ✅ Распознаёт технологии в ТЗ
- ✅ Создаёт детальный план по этапам
- ✅ Подбирает стек технологий
- ✅ Считает сроки и бюджет
- ✅ Генерирует уточняющие вопросы

**Пример ответа:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💻 РАЗРАБОТКА

🛠 СТЕК ТЕХНОЛОГИЙ
• Python 3.11+
• FastAPI
• Pydantic
• SQLAlchemy / Tortoise ORM

📋 ПЛАН РЕАЛИЗАЦИИ
Этап 1: Анализ ТЗ и проектирование
Этап 2: Настройка проекта
Этап 3: Реализация API endpoints
Этап 4: Система авторизации
...

⏱️ ОБЩИЕ СРОКИ: 6 этапов, ~2.9 дней
```

**Подробности:** `dashboard/PERSONALIZED_PROPOSALS.md`

---

## 📊 Что где находится:

| Что | Где | Зачем |
|-----|-----|-------|
| **Веб-интерфейс** | http://localhost:3010 | Просмотр задач, генерация ответов |
| **Задачи (база)** | `freelance-agent/data/db/freelance.db` | Все найденные задачи |
| **История ответов** | `freelance-agent/data/learning/history.json` | Обучение агента |
| **Скилы агента** | `freelance-agent/config/agent-skills.json` | Навыки и статистика |
| **Логи** | `freelance-agent/logs/agent-YYYY-MM-DD.log` | Логи запусков |

---

## 🎯 Как работать:

### 1. Сканирование задач
```bash
cd /Users/igorvasin/freelance-2026/freelance-agent
npm run dev:kwork        # Только Kwork
npm run dev:freelance    # Только Freelance.ru
npm run dev              # Все платформы
```

### 2. Просмотр задач
- Откройте http://localhost:3010
- Выберите задачу из списка
- Изучите персонализированный ответ

### 3. Отправка ответа
- Нажмите **"Отправить"**
- Выберите:
  - **OK** — откроет браузер + вставит текст
  - **Отмена** — скопирует в буфер
- Вставьте в форму на бирже

### 4. Выполнение работы
- Откройте задачу на бирже
- Выполните через Antigravity IDE
- Отправьте прототип заказчику

---

## 🔧 Настройки:

### Изменить навыки агента:
```bash
code /Users/igorvasin/freelance-2026/freelance-agent/config/agent-skills.json
```

### Изменить пороги фильтрации:
```bash
code /Users/igorvasin/freelance-2026/freelance-agent/config/profile.json
```

### Посмотреть историю:
```bash
cat /Users/igorvasin/freelance-2026/freelance-agent/data/learning/history.json | jq
```

---

## 📊 Проверка статуса:

```bash
# Сколько задач в базе
sqlite3 /Users/igorvasin/freelance-2026/freelance-agent/data/db/freelance.db "SELECT COUNT(*) FROM jobs;"

# Сколько отправлено
sqlite3 /Users/igorvasin/freelance-2026/freelance-agent/data/db/freelance.db "SELECT COUNT(*) FROM proposals;"

# Статистика скилов
cat /Users/igorvasin/freelance-2026/freelance-agent/config/agent-skills.json | python3 -c "import sys,json; d=json.load(sys.stdin); print('Проектов:', d.get('statistics',{}).get('totalProjects',0))"
```

---

## ⚠️ Известные проблемы:

### 1. Не видно количество откликов
**Решение:** Парсеры не извлекают `proposals_count`. Нужно обновить адаптеры.

### 2. Автоотправка не работает
**Решение:** Требуется `.env` с логинами/паролями и скомпилированный `auto-bid.ts`.

### 3. История обучения пустая
**Решение:** Проверить, что `LearningService` импортируется в `dashboard/src/app/api/proposals/route.ts`.

---

## 📚 Документация:

- **Полная:** `STATUS_2026-03-24.md` — детальное описание всего проекта
- **Автоотправка:** `dashboard/AUTO_SEND.md` — как работает автоотправка
- **Обучение:** `freelance-agent/LEARNING.md` — система самообучения агента
- **Проблемы:** `dashboard/TROUBLESHOOTING.md` — решение проблем с сетью

---

## 💡 Советы:

1. **Запускайте сканирование утром** — свежие задачи имеют меньше конкуренции
2. **Используйте фильтр "Свежие (≤2ч)"** — больше шансов на ответ
3. **Редактируйте ответы** — добавляйте детали под конкретного заказчика
4. **Сохраняйте сессию** — куки сохраняются, вход автоматический
5. **Проверяйте статистику** — какие типы задач конвертят лучше

---

*Шпаргалка для быстрого старта. Полная документация в `STATUS_2026-03-24.md`*
