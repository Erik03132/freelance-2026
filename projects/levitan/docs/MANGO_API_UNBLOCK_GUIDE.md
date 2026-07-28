# Инструкция: Разблокировка Mango API в ЛК МТС (Манго-Офис)

## Проблема
```
Mango API: config/*, media/*, commands/call → 3128 (Service disabled)
```

## Что нужно включить в ЛК МТС

### 1. Зайти в ЛК МТС (Манго-Офис)
- URL: `https://app.mango-office.ru/`
- Войдите под аккаунтом администратора VPBX

### 2. Настройки VPBX → API
Путь: **Настройки → Интеграции → API** (или **VPBX → API**)

### 3. Включить доступы для API-ключа
Найдите ваш API-ключ (`vpbx400374818` или другой) и включите:

| Раздел API | Методы | Зачем нужен |
|------------|--------|-------------|
| **Конфигурация** | `config/users` | Получить список SIP-пользователей, их номера, статусы |
| **Медиа** | `media/*` (upload, download, list) | Загрузка приветствий, TTS аудио, скачивание записей |
| **Команды** | `commands/call` | Прямые исходящие вызовы (не callback!) |

> **Важно:** `commands/callback` уже работает (result: 1000) — его НЕ трогать.

### 4. Сохранить и проверить
После включения — нажать **Сохранить**. Изменения вступают в силу сразу или в течение 1-2 минут.

---

## Проверка после включения

### Быстрый тест (curl)
```bash
# 1. config/users — должен вернуть список пользователей
curl -X POST "https://app.mango-office.ru/vpbx/config/users" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "vpbx_api_key=ВАШ_API_KEY&json={}&sign=ВАШ_СИГН"

# 2. media/list — должен вернуть список файлов
curl -X POST "https://app.mango-office.ru/vpbx/media/list" \
  -d "vpbx_api_key=...&json={}&sign=..."

# 3. commands/call — тестовый звонок (будет ошибка без реального номера, но НЕ 3128)
curl -X POST "https://app.mango-office.ru/vpbx/commands/call" \
  -d "vpbx_api_key=...&json={\"command_id\":\"test\",\"from\":{\"extension\":\"23\"},\"to_number\":\"79991112233\"}&sign=..."
```

Ожидаемый результат: **НЕ 3128** (может быть 1000, 1001, 404, 400 — главное не "Service disabled").

---

## Архитектура вызова (для понимания, зачем нужны эти API)

```
ИСХОДЯЩИЙ ЗВОНОК (callback через ext 23):
┌─────────────────────────────────────────────────────────────┐
│ 1. Mango callback API (commands/callback)                   │
│    → Mango звонит на SIP:user1@vpbx400374818 (baresip)       │
│    → baresip отвечает → играет GREETING_WAV                 │
│    → клиент говорит → baresip пишет в FIFO                  │
│    → FAQ-агент читает, отвечает через TTS → baresip         │
└─────────────────────────────────────────────────────────────┘
    НУЖНО: commands/callback ✅ УЖЕ РАБОТАЕТ

ПРИВЕТСТВИЕ И TTS (media/*):
┌─────────────────────────────────────────────────────────────┐
│ 1. levitan_greeting.py → synthesize_wav() → WAV файл        │
│ 2. media/upload → загружаем в Mango → получаем audio_id     │
│ 3. commands/play/start → проигрываем audio_id в звонке      │
└─────────────────────────────────────────────────────────────┘
    НУЖНО: media/upload, media/list, play/start

ЗАПИСИ РАЗГОВОРОВ (media/*, config/*):
┌─────────────────────────────────────────────────────────────┐
│ 1. webhook: recording_added → получаем recording_id         │
│ 2. media/download → скачиваем MP3 для STT                   │
│ 3. config/users → маппинг extension ↔ SIP user              │
└─────────────────────────────────────────────────────────────┘
    НУЖНО: media/download, config/users

ПРЯМОЙ ЗВОНОК (commands/call) — резерв:
┌─────────────────────────────────────────────────────────────┐
│ Если callback не работает — fallback на прямой вызов        │
│ commands/call звонит сразу на номер клиента                 │
└─────────────────────────────────────────────────────────────┘
    НУЖНО: commands/call
```

---

## Чек-лист готовности к продакшену

| Компонент | Статус | Действие |
|-----------|--------|----------|
| VPS | ✅ | Работает |
| baresip patched | ✅ | VIDMODE_OFF fix |
| levitan-webhook (8087) | ✅ | Принимает events |
| levitan-faq-agent | ✅ | 238 триггеров |
| Mango callback | ✅ | result: 1000 |
| **Mango API: config/*** | ❌ **3128** | **Включить в ЛК** |
| **Mango API: media/*** | ❌ **3128** | **Включить в ЛК** |
| **Mango API: commands/call** | ❌ **3128** | **Включить в ЛК** |
| GREETING_WAV | ✅ | `/tmp/levitan_greeting_lead.wav` |

---

## После разблокировки — тестовый сценарий

```bash
# На VPS:
# 1. Перегенерировать приветствие (на случай изменения текста)
cd /opt/levitan && python3 deploy/levitan_greeting.py

# 2. Запустить FAQ-агента в режиме прослушки
python3 deploy/levitan_faq_agent.py &
# или systemd: systemctl start levitan-faq-agent

# 3. Сделать тестовый callback с телефона
# В Telegram боте или curl:
curl -X POST "https://app.mango-office.ru/vpbx/commands/callback" \
  -d "vpbx_api_key=...&json={\"command_id\":\"test1\",\"from\":{\"extension\":\"23\"},\"to_number\":\"79859234644\"}&sign=..."

# Ожидаемый результат:
# - Звонок приходит на baresip (ext 23)
# - Играет приветствие
# - Клиент отвечает / говорит
# - FAQ-агент отвечает (кеш или LLM)
# - Запись создаётся → webhook ловит recording_added
```

---

## Контакты для поддержки МТС

Если в ЛК нет галочек или они не сохраняются:
- Техподдержка: `8-800-555-00-55` (МТС Бизнес)
- Чат в ЛК: правый нижний угол
- Email: `support@mango-office.ru`

**Шаблон обращения:**
> Добрый день. VPBX `vpbx400374818`. Нужно включить доступ к API методам:
> - `config/users`
> - `media/*` (upload, download, list)
> - `commands/call`
> Сейчас возвращают ошибку 3128 "Service disabled". API-ключ настроен, callback работает. Просьба активировать сервисы.