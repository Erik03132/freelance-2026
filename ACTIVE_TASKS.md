# Текущие задачи (обновлено 09.06.2026)

> **Архив завершённых/протухших задач:** `_archive/tasks/`

---

## 🔴 P0 — 16.06.2026 (завтра)

### 14. 📞 Автодозвон «Доставка 18 июня» — УТРО 16.06
> 24 заказа (39 уникальных номеров), маршрут Азовское-Керчь. WAV готов, CSV готов.

- [ ] Загрузить `confirm_june18_8k.wav` в ЛК Mango → получить `audio_id`
- [ ] Подменить WAV на VPS (`/tmp/mango_play.wav`) или прописать новый `audio_id`
- [ ] Запустить обзвон: `python3 /opt/data/mango/run_batch.py /opt/data/mango/delivery_june18.csv`
- [ ] При ДА/DTMF-1 → Битрикс: сделка «Новый заказ» → «Подтверждено» (уточнить `STAGE_ID`)
- [ ] При НЕТ → ничего не меняем, менеджеры перезвонят вручную по списку
- [ ] Отчёт: сводка по 39 номерам в TG

### 15. 📞 Автодозвон «Доставка [ДАТА 2]» — 16.06
> Вторая дата от заказчика — будет утром 16.06. Создать WAV + CSV + запуск.

- [ ] Получить дату и список телефонов
- [ ] Сгенерировать WAV с новой датой
- [ ] Нарезать CSV + запуск обзвона

### 16. 🧠 Улучшение STT-распознавания ответов — ВЕЧЕР 16.06
> 335 «unclear» за день 15.06 — система не распознаёт «Ага», «Давай», «Ну да» как ДА. Нужен fuzzy-matching + расширение словаря.

- [ ] Расширить словарь YES/NO в `dtmf_monitor.py` (добавить «ага», «давай», «конечно», «ладно», «угу»)
- [ ] Добавить Levenshtein-расстояние для fuzzy-match (порог ≤ 2)
- [ ] Тест на записях из `call_results.csv` — замер precision/recall

### 13. 📞 Recall по потенциальным ДА — ВЕЧЕР 16.06
> Из утренних пакетов #13–#16 (200 звонков) — 166 «unclear», среди них ~40-50 человек слышали скрипт целиком (звонок > 20 сек). Горячая аудитория!

- [ ] Отфильтровать из `call_results.csv` все `unclear` где длительность звонка > 20 сек (через Mango CDR API или лог)
- [ ] Нарезать recall-пакет: короткий WAV *«Вы не успели ответить — вам интересна доставка 24 июля? Нажмите 1 или скажите ДА»* (10-15 сек)
- [ ] Запустить recall вечером 16.06 в 19:00 MSK (лучший слот по A/B тесту)
- [ ] Ожидаемый результат: +15-25 подтверждений сверху

### 1. 📞 CSV-загрузка в TG → автодозвон Mango → отчёт в TG
- [ ] **Telegram handler**: команда `/call_csv` или приём CSV-файла с телефонами
- [ ] **Конвейер**: CSV → `mango_autocall.py` → обзвон → результаты
- [ ] **Отчёт**: результат обзвона в TG (кто подтвердил/отказал/не дозвонились)
- [ ] **Исходники**: `tg_bot.py` (новый handler) + `mango_autocall.py` (уже есть)

### 2. 🔧 Баги ночного аудита — ЗАКРЫТО ✅
- [x] **14.06** `angelochka_core.py` — fail-closed при битом roles_config.json
- [x] **14.06** `tg_bot.py` — race condition в is_silent_mode() (try/except OSError)
- [x] **14.06** `angelochka_core.py` — path traversal (realpath + проверка границ)
- [x] **14.06** `bitrix_intelligence.py` — SSL verify=True явно
- [x] **14.06** `angelochka_core.py` — _CREATOR_TG_ID .strip()
- [x] **15.06** `angelochka_core.py:4` — дублирующий `import re as _re_core` убран
- [x] **15.06** `bitrix_intelligence.py:26` — EnvironmentError при пустом BITRIX_URL
- [x] **15.06** `bitrix_intelligence.py:40-48` — bx_post: логирование HTTP 502/504 + API error
- [x] **15.06** `bitrix_intelligence.py:59-62` — bx_get_all: защита от не-list при {"error":...}

---

## 🎙️ P0 — Voice Angela (голосовой ассистент) — 17.06.2026

> Создана 16.06.2026. Тестовый звонок утром 17.06 в 09:00 MSK.
> Документация: `ai-eggs/AGENTS.md`, `docs/superpowers/specs/2026-06-16-realtime-voice-angela.md`

### 20. 🎯 Тестовый звонок — утро 17.06 09:00 MSK
> Mango не звонит ночью. Первый тест — через исходящий callback на +79687896924.

- [ ] Запустить: `bash agent/start_voice_test.sh` на VPS
- [ ] Ответить на звонок, проверить: Kore голос, Angela отвечает по ценам/породам
- [ ] Проверить STT: распознаёт ли русскую речь?
- [ ] Проверить Bitrix24 lookup: находит ли контакт по номеру?
- [ ] Проверить перевод на оператора (команда "ПЕРЕКЛЮЧАЮ_ОПЕРАТОРА")
- [ ] Если OK → настроить inbound routing в Mango Office

### 21. 🛠 Диагностика baresip регистрации (P1)
> baresip не посылает REGISTER на Mango SIP. Нужно понять почему — проверено: DNS резолвится, порт открыт.

- [ ] Проверить формат accounts файла
- [ ] Проверить digest auth (пароль с & и !)
- [ ] Попробовать обновить baresip до свежей версии

### 22. 🚀 Production voice-angela (P2)
- [ ] Предзагрузить greeting audio_id для быстрого старта
- [ ] GStreamer для streaming (замена file-based)
- [ ] Silero VAD для лучшей детекции речи
- [ ] Dashboard метрик: звонки, длительность, latency

---

## 🔵 P1 — RAG & Eval (из статьи Bitrix24)

> Источник: https://habr.com/ru/companies/bitrix/articles/1046512/

### 17. 🎯 LLM as a judge — авто-валидация ответов агентов
> Оценка 9/10. Bitrix24: eval-пайплайн для RAG-помощника через LLM-судью.
> Применение: Шекспир (контент) + ai-eggs — автоматическая проверка качества ответов без ручной разметки.

- [ ] Создать `llm_judge.py` в `agent-lab/`: принимает (вопрос, ответ, контекст) → оценка relevance + correctness + helpfulness
- [ ] Интегрировать с ai-eggs: после каждого ответа Шекспира — прогонять через LLM-судью, логировать оценку
- [ ] Настроить алерт: если оценка < 6/10 — уведомление в TG с цитатой плохого ответа
- [ ] Добавить чеклисты (checklist items) для каждой роли агента — судья проверяет не только качество, но и соответствие роли

### 18. 📊 RAGAS — метрики качества RAG-систем (P2)
> Оценка 8/10. Универсальный инструмент для валидации retrieval-эффективности.

- [ ] `pip install ragas` в agent-lab
- [ ] Протестировать на датасете ai-bureau: замерить faithfulness, answer relevancy, context precision
- [ ] Добавить в CRON раз в день: `ragas_eval.py` → отчёт в TG с динамикой метрик
- [ ] Агент: Кулибин

### 19. 🔍 Recall@K / Hit Rate@K — метрики поиска (P2)
> Оценка 7/10. Стандартизация оценки retrieval в RAG-пайплайне.

- [ ] Добавить в ai-scout расчёт Recall@K и Hit Rate@K для поиска по TG-сообщениям
- [ ] Калибровать threshold под GEO-запросы (Маркетолог)
- [ ] Экспортировать метрики в дашборд (лог-файл + TG-нотификация раз в неделю)
- [ ] Агент: Маркетолог

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
