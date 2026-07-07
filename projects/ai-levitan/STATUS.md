# ai-levitan — Статус проекта

## Текущий статус: 🟡 Callback ext 22 работает, приветствие в разработке

## Прогресс

- [x] Структура проекта создана (13 модулей)
- [x] База 15 965 контактов сконвертирована
- [x] VPS: webhook + форвардинг событий
- [x] Mango callback работает
- [x] Записи разговоров приходят (recording_added)
- [x] Скачивание записей через Mango API
- [x] STT (faster-whisper) на VPS
- [x] LLM извлечение данных из транскрипта
- [x] Smart Dialer: автодозвон + авто-CRM
- [x] Шпаргалка-скрипт разговора
- [x] Telegram бот @levitan_dialer_bot (новый, создан сегодня)
- [x] SIP: Zoiper подключён (v1000@vpbx400374818.mangosip.ru, ext 22)
- [x] Баг wait_for_recording исправлен (отсутствовал аргумент phone)
- [x] Mango callback → полная цепочка: Zoiper → клиент
- [ ] Ручной обзвон 100 контактов (проверка гипотезы)
- [ ] Real-time диалог (после подтверждения конверсии)

## Архитектура (текущая)

```
Smart Dialer (локально):
  ├── Загружает базу → фильтрует зерновые/масличные/бобовые (11 240 контактов)
  ├── Mango callback → ты говоришь с клиентом
  ├── После звонка → ищет recording_id на VPS
  ├── Скачивает запись → STT (faster-whisper, VPS)
  ├── LLM (DeepSeek) → извлекает структурированные данные
  ├── Сохраняет в CRM (CSV + JSON)
  └── Telegram уведомление с саммари

VPS (72.56.38.19):
  ├── mango-webhook (8085) — события Mango
  ├── levitan-webhook (8087) — форвард событий
  └── faster-whisper base — STT
```

## Сессия 2026-07-04 (предыдущая)

### Что сделано
1. **Новый Telegram бот** — `@levitan_dialer_bot` (старый `@Angella26bot` чужой)
   - Токен: `8776258870:AAEvEAQNRL4N8sLmn0eUnARQ8-6BOl6rEM8`
   - Chat ID: `176203333`
2. **SIP-телефон** — переключились с Telephone.app на **Zoiper**
   - Пользователь: `user4`
   - Домен: `vpbx400161137.mangosip.ru`
   - Пароль: `k8&HR5z!aZ62G`
   - Транспорт: UDP
3. **Исправлен баг** — `wait_for_recording()` не получал аргумент `phone`
4. **Первый тест звонка** — Mango callback вернул `result=1000` (успешно)
   - Клиент: `79611061981`
   - Клиент не ответил → звонок в Zoiper не дошёл (нормально)

### Проблемы и решения
| Проблема | Решение |
|----------|---------|
| Telephone.app не регистрируется | Переключились на Zoiper |
| Бот `@Angella26bot` чужой | Создали нового `@levitan_dialer_bot` |
| `wait_for_recording()` missing arg | Добавлен аргумент `phone` |
| Клиент не ответил → нет звонка в Zoiper | Нормальное поведение callback |

### Команды бота
| Команда | Действие |
|---------|----------|
| `/start` | Приветствие + инструкция |
| `начать обзвон` | Запуск обзвона |
| `следующий` | Следующий клиент |
| `стоп` | Остановить обзвон |
| `статус` | Статистика звонков |

### Следующие шаги
1. **Протестировать звонок** — когда клиент ответит, проверить что приветствие играет
2. **Проверить CRM** — сохранение результатов в CSV/JSON
3. **Ручной обзвон** — 100 контактов за день
4. **Анализ результатов** — конверсия, скрипт, возражения

## Сессия 2026-07-05

### Что сделано
1. **Починен callback** — Zoiper был подключён к чужой АТС (vpbx400161137). Сотрудник с extension 22 живёт на vpbx400374818. Переключили Zoiper: user4→v1000, другой домен, новый пароль.
2. **Полная цепочка пройдена** — callback → Zoiper (Mac) → тестовый телефон (+79687896924). Оба звонка пришли.
3. **Оценён x.ai Voice план** — продакшен-готовность 10%. Для Levitan преждевременно, пока базовая механика не работает.

### Обнаружено
- Callback: `from.extension` звонит агенту ПЕРВЫМ. Только когда агент поднимает трубку — Mango звонит клиенту.
- Приветствие не проигрывается автоматически — callback просто соединяет линии.
- **Критично:** Mango требует SIP URI = username (user1), НЕ extension number (23). `sip:23@...` → 403, `sip:user1@...` → 200 OK.
- Частые 403 блокируют IP. Сброс через Wi-Fi отключение/подключение.
- Mango API: `commands/call`, `commands/group`, `config/users`, `media/*` — все возвращают 3128 (нет прав).

### Greeting Bridge (baresip)
- ✅ Baresip установлен локально (brew, v4.9.0)
- ✅ Extension 23 (user1) регистрируется: `sip:user1@vpbx400374818.mangosip.ru`
- ✅ SIP password: `25!vsnzQ6m6H`
- ⚠️ Конфиг: `greeting_bridge/config` + `accounts`
- ⚠️ Баг: ctrl_tcp не загружается в daemon-режиме — нужно починить модуль
- ⏳ Контроллер: `greeting_bridge/controller.py` — написан, не протестирован
- ⏳ Полный цикл: callback ext 23 → baresip → приветствие → transfer ext 22

### Данные Greeting Bridge
| Параметр | Значение |
|----------|----------|
| Baresip ext | 23 (SIP: user1@vpbx400374818.mangosip.ru) |
| SIP password | `25!vsnzQ6m6H` |
| ctrl_tcp port | 4446 |
| SIP listen port | 5081 |
| Greeting WAV | `scripts/tts_cache/globalfields_greeting_default.wav` |
| Transfer target | `sip:22@vpbx400374818.mangosip.ru` |
| Mango audio file ID | `1000556744` |

### Следующий запуск
1. Починить ctrl_tcp в конфиге baresip
2. Протестировать контроллер greeting_bridge.py
3. Полный цикл с тестовым звонком
4. Ручной обзвон 100 контактов

## Скрипты

| Скрипт | Назначение | Запуск |
|--------|-----------|--------|
| `scripts/dialer_bot.py` | Telegram бот + Mango callback + CRM | `python3 scripts/dialer_bot.py` |
| `scripts/smart_dialer.py` | Автодозвон + авто-CRM через запись | `python3 scripts/smart_dialer.py` |
| `scripts/manual_dialer.py` | Простой автодозвон + ручной ввод | `python3 scripts/manual_dialer.py` |
| `scripts/smart_dialer_greeting.py` | TTS приветствие (DmitryNeural) | — |
| `scripts/CALL_SCRIPT.txt` | Шпаргалка для печати | — |
| `deploy/levitan_turnbased.py` | Turn-based AI-диалог (заготовка) | На VPS |

## Запуск

```bash
cd /Users/igorvasin/freelance-2026/projects/levitan
source .venv/bin/activate
python3 scripts/dialer_bot.py
```

## Данные для подключения

| Сервис | Данные |
|--------|--------|
| Mango API Key | `k0ockrwsafuf7tfpuk7fkqtps4nl77o8` |
| Mango Salt | `9g1go1lj1zxkyc0v9j9c7fsyy12erqcw` |
| SIP User | `v1000` |
| SIP Domain | `vpbx400374818.mangosip.ru` |
| SIP Password | `p?BJq78tmDk2` |
| Telegram Bot | `@levitan_dialer_bot` |
| Telegram Chat ID | `176203333` |
| OpenRouter Model | `deepseek/deepseek-chat-v3-0324` |
