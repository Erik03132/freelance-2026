# 🏛️ AI-SENAT (Мустай) — Спецификация проекта

> **AI-помощник сенатора от Башкортостана**  
> Последнее обновление: 2026-04-19  
> Статус: **MVP — Фаза 1 (в процессе)**

---

## 📋 ЧЕКЛИСТ ПРОЕКТА

### Фаза 0: Инфраструктура
- [x] Создать структуру проекта `/Users/igorvasin/freelance-2026/ai-senat/`
- [x] `.env` с реальными ключами (Gemini, OpenRouter, Neon DB)
- [x] `.env.example` (шаблон без секретов)
- [x] `.gitignore`
- [x] `requirements.txt`
- [x] Python venv с установленными зависимостями
- [x] `manage_mustai.sh` — скрипт управления (start/stop/status/pipeline)
- [ ] Git-репозиторий инициализирован (`git init`)
- [ ] README.md с описанием для внешних

### Фаза 1: Ядро (MVP)
#### LLM Каскад (`agent/llm_cascade.py`)
- [x] Gemini Direct API
- [x] OpenRouter (3 модели с фоллбэком)
- [x] Ollama offline
- [x] `call_llm()` — общий вызов
- [x] `call_llm_structured()` — вызов с system prompt

#### RSS-сканер (`agent/scanner/rss_monitor.py`)
- [x] RSS-парсинг через feedparser
- [x] Дедупликация (hash-based)
- [x] Сохранение сырых данных в `data/raw_feed/`
- [x] Автоочистка старых хешей (>7 дней)
- [x] **Работающие источники:**
  - [x] Правительство РФ ✅
  - [x] ТАСС ✅
  - [x] РБК ✅
  - [x] Коммерсантъ ✅
  - [x] Интерфакс ✅
  - [ ] Парламентская газета (pnp.ru — connection error)
  - [ ] БашИнформ (bashinform.ru — HTML, не XML)
  - [ ] Гарант (garant.ru — не well-formed)
  - [ ] Кремлин (kremlin.ru — syntax error)
- [ ] Добавить скрейпинг HTML-страниц для источников без RSS
- [ ] Мониторинг СОЗД ГД (sozd.duma.gov.ru) — законопроекты
- [ ] Telegram-каналы мониторинг (telethon/pyrogram)

#### Веб-поиск (`agent/scanner/deep_search.py` + `web_search.py`)
- [x] DuckDuckGo HTML-поиск (бесплатно, без ключей)
- [x] DDG как фоллбэк в deep_search
- [ ] Perplexity API (ключ не задан)
- [ ] Tavily API (ключ не задан)
- [ ] Парсинг содержимого найденных страниц (readability)

#### Генератор инициатив (`agent/generator/initiative_gen.py`)
- [x] Системный промпт с шаблоном инициативы
- [x] Загрузка KB Башкортостана
- [x] Загрузка профиля сенатора
- [x] Антидубли (проверка по истории)
- [x] Сохранение в `initiatives_history.json`
- [x] Генерация по конкретной теме (`generate_on_topic`)
- [ ] Оценка качества инициативы (самопроверка LLM)
- [ ] Автоматическая категоризация инициатив

#### Ядро агента (`agent/senator_core.py`)
- [x] `get_answer()` — обработка сообщений с маршрутизацией
- [x] `run_daily_pipeline()` — полный ежедневный цикл
- [x] Маршрутизация по типу запроса (инициатива/поиск/сравнение/общий)
- [x] Загрузка KB при старте
- [x] Фокусная тема (set/get/clear)
- [ ] Кеширование ответов (SmartFAQ паттерн из ai-eggs)
- [ ] Логирование запросов в traces.json

#### Telegram-бот (`agent/tg_bot.py`)
- [x] Создан бот @mustaybot
- [x] Токен: 8610936135:AAE... (в .env)
- [x] Lock-файл защита (один экземпляр)
- [x] Retry с backoff при конфликтах
- [x] **Команды:**
  - [x] `/start` — приветствие
  - [x] `/initiative` — инициатива дня
  - [x] `/search [тема]` — глубокий поиск
  - [x] `/global [тема]` — мировой опыт
  - [x] `/compare [регион]` — сравнение регионов
  - [x] `/focus [тема]` — фокусная тема
  - [x] `/history` — архив инициатив
  - [x] `/digest` — дайджест дня
  - [x] `/pipeline` — ручной запуск цикла
  - [x] `/status` — статус системы
- [x] Свободный диалог (произвольные сообщения)
- [x] История диалогов в памяти (последние 20)
- [ ] Inline-кнопки для навигации
- [ ] Меню бота (сейчас ошибка "chat not found" — нужен первый /start)

#### Планировщик (`agent/scheduler.py`)
- [x] Ежедневный pipeline в 07:00
- [x] Доставка инициативы в 10:00
- [x] Логирование в `scheduler.log`
- [x] Очистка кеша задач в полночь
- [ ] Запуск через systemd/launchd (автостарт после ребута)
- [ ] Мониторинг здоровья (heartbeat)

### Фаза 2: База знаний и RAG
#### База знаний Башкортостана (`data/bashkortostan_kb/`)
- [x] `economy.md` — экономика, отрасли, бюджет
- [x] `demographics.md` — население, города, образование
- [x] `challenges.md` — проблемы и точки роста
- [ ] `legislation.md` — действующее региональное законодательство
- [ ] `committees.md` — комитеты СФ и их повестка
- [ ] `competitors.md` — сравнение с Татарстаном, Свердловской обл.
- [ ] `history_initiatives.md` — ранее принятые инициативы от РБ

#### Профиль сенатора (`data/senator_profile.md`)
- [x] Базовый профиль (регион, направления)
- [ ] Конкретные комитеты
- [ ] Приоритетные темы от сенатора
- [ ] Политические ограничения

#### RAG (Vector Search)
- [ ] Подключение pgvector (Neon DB)
- [ ] Embeddings (sentence-transformers)
- [ ] Гибридный поиск (BM25 + Vector)
- [ ] Индексинг KB и истории инициатив
- [ ] Автоматическое обновление индекса при поступлении новых данных

### Фаза 3: Продвинутые функции
- [ ] Auto-learner (самообучение на обратной связи сенатора)
- [ ] Мониторинг Telegram-каналов (парсинг каналов депутатов/СМИ)
- [ ] Парсинг СОЗД ГД (tracking законопроектов)
- [ ] Email-рассылка дайджеста (альтернатива Telegram)
- [ ] Веб-дашборд для просмотра аналитики
- [ ] Мультиязычность (башкирский язык)

### Фаза 4: Deployment
- [ ] Деплой на VPS (Timeweb/Railway)
- [ ] systemd/supervisor для автозапуска
- [ ] Мониторинг (uptime, ошибки, расход токенов)
- [ ] Бэкап данных (автоматический)
- [ ] CI/CD (GitHub Actions)

---

## 🏗️ ТЕКУЩАЯ АРХИТЕКТУРА

```
ai-senat/
├── .env                      # API ключи (Gemini✅, OpenRouter✅, Bot✅, Neon✅)
├── .env.example
├── .gitignore
├── requirements.txt
├── manage_mustai.sh          # bash start/stop/status/pipeline
├── PROJECT_SPEC.md           # ← ВЫ ЗДЕСЬ
│
├── agent/
│   ├── llm_cascade.py        # Каскадный LLM (Gemini → OpenRouter → Ollama)
│   ├── senator_core.py       # Ядро: pipeline + маршрутизация + диалог
│   ├── tg_bot.py             # Telegram-бот @mustaybot (10 команд)
│   ├── scheduler.py          # Планировщик (07:00 pipeline → 10:00 доставка)
│   ├── scanner/
│   │   ├── rss_monitor.py    # RSS (9 источников, 5 работают стабильно)
│   │   ├── deep_search.py    # Perplexity + Tavily + DDG fallback
│   │   └── web_search.py     # Бесплатный DDG поиск (без API ключей)
│   └── generator/
│       └── initiative_gen.py # Генератор инициатив с шаблоном
│
├── data/
│   ├── senator_profile.md     # Профиль сенатора
│   ├── bashkortostan_kb/      # База знаний (3 файла)
│   │   ├── economy.md
│   │   ├── demographics.md
│   │   └── challenges.md
│   ├── raw_feed/              # Сырые RSS-данные (по дням)
│   ├── daily_digests/         # Ежедневные дайджесты
│   └── initiatives_history.json  # Архив инициатив
│
└── venv/                      # Python 3.9 виртуальное окружение
```

## 🔑 КЛЮЧИ И ДОСТУПЫ

| Сервис | Переменная | Статус |
|--------|-----------|--------|
| Gemini AI | `GEMINI_API_KEY` | ✅ Подключен (из ai-eggs) |
| OpenRouter | `OPENROUTER_API_KEY` | ✅ Подключен (из ai-eggs) |
| Telegram Bot | `SENATOR_BOT_TOKEN` | ✅ @mustaybot |
| Admin ID | `SENATOR_ADMIN_ID` | ✅ 176203333 |
| Neon PostgreSQL | `NEON_DATABASE_URL` | ✅ Подключен (из ai-eggs) |
| Perplexity | `PERPLEXITY_API_KEY` | ❌ Не задан |
| Tavily | `TAVILY_API_KEY` | ❌ Не задан |
| Ollama | `OLLAMA_URL` | ⏸️ Опционально |

## 📊 ТЕСТЫ И ВАЛИДАЦИЯ

| Тест | Результат | Дата |
|------|----------|------|
| Импорт всех модулей | ✅ Все 5 модулей | 19.04.2026 |
| RSS-сканирование | ✅ 75 записей (5 источников) | 19.04.2026 |
| DDG веб-поиск | ✅ 5 результатов | 19.04.2026 |
| Telegram-бот polling | ✅ Работает (PID 92892) | 19.04.2026 |
| /status команда | ✅ Ответил корректно | 19.04.2026 |
| /pipeline полный цикл | ⏳ Не тестирован (ждёт перезапуска) |
| Генерация инициативы | ⏳ Не тестирована вживую |

## 🚀 СЛЕДУЮЩИЙ СЕАНС — ПРИОРИТЕТЫ

1. **Перезапустить бота** и протестировать `/pipeline` (полный цикл)
2. **Протестировать генерацию инициативы** — убедиться что LLM отвечает по шаблону
3. **Добавить комитеты сенатора** в профиль (данные от клиента)
4. **Починить RSS-источники** — добавить скрейпинг HTML для БашИнформ и pnp.ru
5. **Запустить scheduler** на постоянной основе (launchd или nohup)
6. **Git init + первый коммит** — зафиксировать MVP

## ⚠️ ИЗВЕСТНЫЕ ПРОБЛЕМЫ

1. **Zombie-процессы в sandbox** — при запуске бота из Antigravity sandbox, процессы не умирают через kill. Запускать ТОЛЬКО из терминала пользователя.
2. **Telegram conflict** — если бот не останавливается корректно, нужно ждать 35с перед перезапуском (Telegram кеширует polling).
3. **Меню бота "chat not found"** — зарегистрируется после первого `/start` от пользователя.
4. **Python 3.9** — некоторые пакеты (duckduckgo-search) не установились из-за timeout pip. Используем свой DDG-парсер.
