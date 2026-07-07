# Levitan - Голосовой агент для обзвона сельхозпроизводителей

## Быстрый старт

### 1. Установка зависимостей

```bash
cd /Users/igorvasin/freelance-2026/projects/levitan
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Настройка окружения

```bash
cp config/.env.example .env
# Заполни .env реальными значениями
```

### 3. Конвертация базы данных

```bash
python3 scripts/convert_excel.py
```

### 4. Запуск

```bash
# Веб-сервер
python3 main.py

# Или запуск кампании
python3 scripts/run_campaign.py rostov data/campaigns/csv/Ростовская область 2026.csv
```

## Структура проекта

```
projects/levitan/
├── src/levitan/
│   ├── __init__.py
│   ├── config.py              # Настройки
│   ├── prompts.py             # System prompts
│   ├── mango_client.py        # Mango Office API
│   ├── webhook_server.py      # FastAPI webhook
│   ├── call_session.py        # Управление звонком
│   ├── stt_engine.py          # Speech-to-Text
│   ├── tts_engine.py          # Text-to-Speech
│   ├── llm_client.py          # OpenRouter LLM
│   ├── knowledge_base.py      # RAG + FAQ
│   ├── campaign_manager.py    # Управление кампаниями
│   ├── lead_storage.py        # Хранение лидов
│   ├── post_call.py           # Анализ звонков
│   └── telegram_reporter.py   # Отчеты в Telegram
├── data/
│   ├── knowledge_base.json    # База знаний
│   ├── campaigns/             # CSV базы по регионам
│   └── transcripts/           # Транскрипты звонков
├── scripts/
│   ├── convert_excel.py       # Конвертация Excel → CSV
│   └── run_campaign.py        # Запуск кампании
├── docs/
│   └── PLAN_FOR_PARTNERS.md   # План для партнеров
└── main.py                    # Основной файл
```

## Компоненты

| Компонент | Назначение |
|-----------|------------|
| Mango Client | Инициация звонков, воспроизведение аудио |
| Webhook Server | Обработка событий Mango |
| Call Session | Управление диалогом |
| STT Engine | Распознавание речи (faster-whisper) |
| TTS Engine | Синтез речи (edge-tts) |
| LLM Client | Генерация ответов (OpenRouter) |
| Knowledge Base | Поиск по базе знаний (RAG) |
| Campaign Manager | Управление кампаниями обзвона |
| Lead Storage | Хранение лидов (SQLite) |
| Post Call | Анализ завершенных звонков |
| Telegram Reporter | Отчеты в Telegram |

## База данных

- **Регионы:** Ростовская, Волгоградская, Брянская, Оренбургская, Тульская, Мордовия, Башкортостан, Ставропольский край
- **Всего контактов:** ~16 000
- **Формат:** Excel → CSV

## Настройка

### Mango Office

1. Получи API ключ и соль в [ЛК Mango](https://lk.mango-office.ru/)
2. Настрой SIP-аккаунт для бота
3. Укажи URL webhook: `https://your-server.com/mango/webhook`

### OpenRouter

1. Зарегистрируйся на [OpenRouter](https://openrouter.ai/)
2. Создай API ключ
3. Укажи модель: `deepseek/deepseek-chat-v3-0324`

### Telegram

1. Создай бота через [@BotFather](https://t.me/BotFather)
2. Получи токен
3. Узнай chat_id (отправь сообщение боту и проверь `/getUpdates`)

## Стоимость

| Статья | Стоимость |
|--------|-----------|
| Mango Office (звонки) | ~3-15 руб./мин |
| OpenRouter (LLM) | ~5-20 руб./день |
| edge-tts (TTS) | Бесплатно |
| faster-whisper (STT) | Бесплатно |

**Итого на 100 звонков:** ~1 000 - 3 000 руб./день
