# Текущие задачи (обновлено 09.06.2026)

> **Архив завершённых/протухших задач:** `_archive/tasks/`

---

## 🔴 P0 — Сегодня

### 1. 📞 CSV-загрузка в TG → автодозвон Mango → отчёт в TG
- [ ] **Telegram handler**: команда `/call_csv` или приём CSV-файла с телефонами
- [ ] **Конвейер**: CSV → `mango_autocall.py` → обзвон → результаты
- [ ] **Отчёт**: результат обзвона в TG (кто подтвердил/отказал/не дозвонились)
- [ ] **Исходники**: `tg_bot.py` (новый handler) + `mango_autocall.py` (уже есть)

### 2. 🔧 Баги ночного аудита (26.05) — из `reports/night_audit_ai-eggs_2026-05-26.md`
- [ ] **`angelochka_core.py:78`** — `_CREATOR_TG_ID` без `.strip()` → 🔴 сброс прав владельца
- [ ] **`angelochka_core.py:72-86`** — `_has_phone_in_history` не видит телефон-контакт
- [ ] **`tg_bot.py:72`** — orphaned lock при SIGKILL → бот не стартует
- [ ] **`bitrix_scanner.py:519`** — `CLOSED_STAGES` не frozenset → race condition
- [ ] **`bitrix_intelligence.py:46`** — синхронный `requests` в асинхронном коде

---

## 🟠 P1 — Анжела: квалификация лидов (из Habr Velmi)

> Источник: https://habr.com/ru/articles/1045026/ — кейс +35% квалифицированных лидов, ответ 30 сек

### 6. ✅ `LeadQualification` Pydantic-модель в `angelochka_core.py` [DONE 09.06.2026]
- [x] Класс `LeadQualification` + `UrgencyLevel` enum (product, qty, city, date, name, phone, urgency, confidence)
- [x] `sales_step` property — заменяет _determine_sales_step()
- [x] `is_hot_lead` property — confidence ≥ 0.7 + urgency HOT/WARM
- [x] `to_crm_dict()` — готовый словарь для Битрикс24
- [x] `extract_lead_from_history()` — regex-парсинг без LLM, 3/3 тестов ✅

### 7. ✅ Redis debounce + lock против гонок вебхуков [DONE 09.06.2026]
- [x] Создан `debounce.py`: `MessageDebounce` + `ProcessLock`
- [x] Primary: Redis (`REDIS_URL`) | Fallback: JSON-файл с fcntl — выживает рестарты PM2
- [x] `msg_debounce.check_and_mark(msg_id)` в `bitrix_receiver.py`
- [x] `receiver_lock.acquire()` активирован — только один receiver одновременно
- [x] Тесты: 3/3 ✅

### 8. ✅ Few-shot срочности + confidence-валидатор [DONE 09.06.2026]
- [x] Few-shot примеры (12 кейсов: HOT/WARM/COLD) добавлены в промпт ROLE_CUSTOMER
- [x] Правило #9 в промпте: «ОДИН ВОПРОС в каждом сообщении»
- [x] Confidence validator: filled < 2 полей → max 0.40
- [x] COLD urgency → принудительно max 0.30 (даже с полными данными)
- [x] phone → минимум confidence 0.50 (железный маркер намерения)
- [x] COLD в текущем запросе перебивает WARM из истории (приоритет)
- [x] Тесты: 5/5 ✅

### 9. ✅ Loop-паттерн в `llm_planner.py` [DONE 09.06.2026]
- [x] `LoopIteration` dataclass: index, output, score, critique, converged, duration_s
- [x] `LoopResult` dataclass: best_output, best_score, converged, summary()
- [x] `LoopPlanner` класс: threshold, max_iterations, budget, verbose
- [x] ACT → JUDGE → CHECK → LIMIT цикл
- [x] `_judge()`: JSON-оценка quality | research convergence
- [x] task_type: "quality" | "research" | "binary"
- [x] CLI флаги: `--demo-loop`, `--loop`, `--threshold`
- [x] Синтаксис: 9/9 проверок ✅


> Источник: https://loops.elorm.xyz/loops — библиотека 40 петель для AI-агентов

- [ ] Добавить `TaskType.LOOP` в `model_router.py`
- [ ] В `llm_planner.py` реализовать loop-режим: `goal` + `max_iterations` + `check_cmd` + `exit_when`
- [ ] Агент сам итерирует: выполняет шаг → запускает `check_cmd` → читает вывод → продолжает если exit condition не выполнен
- [ ] Готовые петли для адаптации: `ship-pr-until-green`, `de-sloppify-pass` → под наш night_audit

### 10. ✅ DAG-карта зависимостей в `two-angelas-map.md` [DONE 09.06.2026]
- [x] Уровневая схема (0→4): Инфраструктура → Хранилища → Бизнес-логика → Ядро → Каналы
- [x] Mermaid-граф со стилями (CORE=красный, ENV=жёлтый, NEW=синий)
- [x] Таблица 15 компонентов: что ломается + критичность (FATAL/HIGH/MED/LOW)
- [x] Порядок деплоя при полном рестарте (8 шагов)
- [x] Таблица новых зависимостей: `debounce.py` + `LeadQualification`
- [x] `debounce.py` и `LeadQualification` отмечены как 🆕 в графе

---

### 11. 🧠 Mem0 — долгосрочная память клиентов для Анжелы
> Источник: https://github.com/Sumanth077/Hands-On-AI-Engineering/tree/main/ai_agents/ai_customer_support_agent
> Паттерн: CartMate — Mistral Small 4 + Mem0, помнит каждого клиента

- [ ] Изучить `pip install mem0ai` — документация и API
- [ ] Добавить `Mem0Client` в `angelochka_core.py`: сохранять факты о клиенте после каждого диалога
- [ ] Структура памяти: `lead_id` → `{name, budget, urgency, last_topics, decisions}`
- [ ] При новом сообщении: загружать память клиента → добавлять в системный промпт
- [ ] Интеграция с `LeadQualification` (#6): если клиент уже квалифицирован — не переспрашивать

### 12. 🔄 Self-Reflective RAG — валидация контекста перед ответом
> Источник: https://github.com/Sumanth077/Hands-On-AI-Engineering/tree/main/ai_agents/agentic_rag_system
> Паттерн: LangGraph → грейдит контекст → переписывает запрос если плохой → ответ только при валидном контексте

- [ ] Изучить LangGraph реализацию (Self-RAG pattern)
- [ ] Добавить в `rag_lite.py` шаг грейдинга: релевантен ли найденный чанк вопросу?
- [ ] Если грейд < 0.7 → переформулировать запрос → повторный поиск (max 2 итерации)
- [ ] Добавить метрику: логировать % случаев когда ответ был дан с первой / второй попытки
- [ ] Тест: вопросы на которые Анжела сейчас «плавает» → проверить улучшение

---

## 🟡 P2 — Средний приоритет


### 3. Контент-машина
- [ ] Яндекс.Дзен: статьи готовы, нужна публикация
- [ ] VK Канал А («ВезёмЦыплят»): группа не создана
- [ ] ОК: автопостинг готов, не запилен

---

## 🟢 P3 — По требованию (GEO/контент)

> Задачи не срочные. Выполнять после деплоя или по запросу.

### 4. GEO-видимость ai-bureau.pro
- [ ] Опубликовать 2 кейса на **VC.ru** с триплетами «AI Bureau → делает → AI-агентов»
- [ ] Добавить **Schema.org** (Organization + FAQPage) на ai-bureau.pro
- [ ] Добавить **FAQ-блоки** на страницы услуг
- [ ] Задеплоить **llms.txt** → `https://ai-bureau.pro/llms.txt` (файл создан в `public/`)

### 5. GEO-видимость vezemcip.ru
- [ ] Создать **llms.txt** в `vezemcip.ru/public/`
- [ ] Добавить **Schema.org** (LocalBusiness + Product) на vezemcip.ru
- [ ] FAQ-блоки: цены, породы, доставка
- [ ] Зарегистрировать в Яндекс Бизнес + 2GIS (карточки = вес в AI-выдаче)

### 6. GEO-монитор (инструмент готов)
- [ ] `python3 tools/geo_monitor.py --site vezemcip --dry-run` — первый замер VezemCip
- [ ] При запуске нового сайта → добавить в `SITES_CONFIG` в `tools/geo_monitor.py`
  - Шаблон: `name, domain, brand_patterns, queries (10-25 шт.)`
- [ ] **Правило Артемия**: каждый новый сайт → регистрация в GEO-мониторе ОБЯЗАТЕЛЬНА

---

## 🏗️ Архитектура автоматизации

### VPS (72.56.38.19) — 24/7
| Время MSK | Скрипт | Описание |
|-----------|--------|----------|
| */15 мин | watchdog_cron.sh | Мониторинг PM2 |
| 00:30 | call_learner.py | Обучение из звонков |
| 02:05 | night_audit_vps.sh | Код-аудит + Gemini ревью |
| 20:10 | daily_report.py | Ежедневный отчёт |
| 20:12 | call_quality_report.py | Отчёт по звонкам |

### Mac (launchd)
| Время | Скрипт | Описание |
|-------|--------|----------|
| 02:00 | night_audit.sh | Код-аудит (локальный) |
| 07:00 | morning_dream.sh | Анализ паттернов |
| 23:00 | finish_day_cron.sh | Бэкап + чистка + TG |
