# ai-levitan — AI-агент для автообзвона сельхозпроизводителей

> **Голосовой агент Levitan для Global Fields Export (GFE)**
> Автоматический обзвон базы контактов, квалификация лидов, CRM.

## Быстрый старт

```bash
cd /Users/igorvasin/freelance-2026/projects/levitan
source .venv/bin/activate
python3 scripts/dialer_bot.py
```

## Команды Telegram-бота

| Команда | Действие |
|---------|----------|
| `начать обзвон` | Запуск цикла обзвона |
| `следующий` | Перейти к следующему контакту |
| `пропустить` | Пропустить текущий |
| `конец обзвона` / `стоп` | Остановить обзвон |
| `статус` | Статистика |

## Архитектура

```
Telegram Bot (dialer_bot.py)
    │
    ├── Mango API (commands/callback)
    │   ├── ext 22 → Zoiper (оператор)
    │   └── ext 23 → baresip (робот-приветствие, WIP)
    │
    ├── STT (faster-whisper) → транскрипт разговора
    ├── LLM (DeepSeek/OpenRouter) → извлечение CRM-данных
    └── CRM (CSV + JSON) → data/call_results/
```

## Документация

| Документ | Содержание |
|----------|-----------|
| [COMPANY.md](COMPANY.md) | Карточка компании GFE |
| [ACCOUNTS.md](ACCOUNTS.md) | Аккаунты и доступы |
| [STATUS.md](STATUS.md) | Текущий статус проекта |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Архитектура системы |

## Структура проекта

```
ai-levitan/
├── README.md           # Этот файл
├── COMPANY.md          # GFE — карточка компании
├── ACCOUNTS.md         # Все аккаунты и креды
├── STATUS.md           # Текущий статус
├── ARCHITECTURE.md     # Архитектура
├── docs/               # Дополнительные документы
├── scripts/ → ../levitan/scripts/          # Симлинк: скрипты
├── greeting_bridge/ → ../levitan/greeting_bridge/  # Симлинк: baresip
└── data/ → ../levitan/data/               # Симлинк: данные
```
