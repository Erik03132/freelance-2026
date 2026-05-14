# 📜 ХРОНИКА ДНЯ: 14.05.2026 (четверг)

> Автоматическая хроника всех сессий за день.
> Каждая сессия дописывает сюда свои действия в реальном времени.

---

## 🕐 Сессия 08:47 | `chp`

### 🏁 Чекпоинт дня (09:00 MSK)

**Сделано сегодня (14.05):**

1. **Unified Morning Report** — ОДИН отчёт в 08:00 MSK (cron 02:01, 03:01, 08:01)
2. **Аудит Avito** — 68 объявлений, ~8,000₽/мес впустую (73% бюджета)
3. **Ночной аудит** — исправлены баги angelochka_core.py, scheduler.py

**VPS 72.56.38.19 работает:**
```
angela-bot         → Telegram, прямое соединение
angela-server      → Website-Заботкина (vezemcip.ru)
angela-scheduler   → Задачи по расписанию (02:00, 03:00, 08:00)
ptenchikova-bot    → Песочница Битрикс
vezem-web          → Astro сайт
```

**План P0:**
1. Avito оптимизация (ждём статистику от Андрея)
2. VK автопостинг (Imagen 4.0)
3. Транскрибация 50 звонков за 13.05

---

## 🕐 Сессия ~12:00 | `autocall_setup`

### 📞 Фаза 14.3 — Автодозвон клиенту (освежение решения)

**Проблема:** Нужно вспомнить решение по автодозвону (Фаза 14.3) — исходящие звонки для подтверждения заказов.

**Найдено:**
- Файл: `ai-eggs/agent/outbound_confirm.py` (создан 08.05.2026)
- Статус: ⏸️ На паузе (ждём API-ключи Mango Office)

**Технологический стек:**
| Компонент | API | Назначение |
|-----------|-----|------------|
| **Телефония** | Mango Office `calls/outbound` | Исходящий звонок с аудиофайлом |
| **TTS** | Yandex SpeechKit / Gemini TTS | Генерация голоса (Oksana, ru-RU) |
| **Триггер** | Bitrix24 Webhook | Создание лида → запуск звонка |
| **DTMF** | Mango Office API | Сбор ответа (1 = да, 2 = позже) |

**Сценарий звонка:**
```
🤖 «Здравствуйте! Это Анжела Заботкина из Азовского Инкубатора.
     Ваш заказ подтверждён.
     
     Пожалуйста, нажмите 1, если всё в силе,
     или 2, чтобы перезвонить позже.»
```

---

## 🕐 Сессия ~12:30 | `mango_credentials`

### 🔐 Поиск учётных данных Mango Office

**Проблема:** В проекте нет `.env` файлов с ключами Mango Office.

**Результаты поиска:**
- ❌ Логин — не найден
- ❌ Пароль — не найден
- ❌ API-ключ — не найден
- ❌ Виртуальный номер — не найден

**Найдено в `SMS_CALL_PROVIDERS_RESEARCH.md`:**
- Mango Office: от 500₽/мес + минуты
- Zvonok.com: 0.10₽/вызов + 2.10₽/мин (дешевле для робота)
- Каскад (WA→TG→SMS): экономия до 80%

**Где искать:**
- 1Password / iCloud Keychain
- Браузер (Safari/Chrome) → Пароли
- Telegram (Saved Messages)
- Почта (поиск: "Mango Office")
- Спросить у Андрея (владелец Азовский Инкубатор)

---

## 🕐 Сессия ~13:00 | `tts_research`

### 🎙️ 3 голосовых сервиса из tech-radar.md

**Найдено в `docs/tech-radar.md` и `VOICE_ENGINE_RESEARCH.md`:**

| № | Сервис | Тип | Статус | Ключевая фишка |
|---|--------|-----|--------|----------------|
| 1 | **Gemini 3.1 Flash TTS** | Cloud | 🟢 ADOPT | Скорость + эмоции |
| 2 | **Inworld TTS-2** | Cloud | 🟡 TRIAL | Conversational Awareness (#1 в мире) |
| 3 | **VoxCPM2** | Local | 🔵 ASSESS | Open-source, локально на GPU |

**Важно:**
- ❌ **OpenRouter НЕ поддерживает TTS** — только LLM (текст)
- ❌ **OpenRouter ключ мёртв** с 09.05.2026 (401 User not found)
- ✅ **Gemini TTS** — только через Google AI Studio Direct API + прокси USA

---

## 🕐 Сессия ~13:30 | `mango_login_found`

### 🔐 Учётные данные Mango Office найдены

**Личный кабинет Mango Office (Азовский Инкубатор):**
- 🔐 **Логин:** `16741963`
- 🔐 **Пароль:** `2026incubator!`
- 🌐 **ЛК:** https://office.mango-office.ru/

**Записано в файл:** `ai-eggs/.env.mango.example`

**Созданы файлы:**
1. `ai-eggs/.env.mango.example` — шаблон со всеми ключами
2. `ai-eggs/agent/outbound_confirm.py` — обновлённый скрипт автодозвона

**Структура `.env.mango.example`:**
```bash
# Mango Office (ЛК Азовский Инкубатор)
MANGO_API_URL=https://api.mango-office.ru/v1/calls/outbound
MANGO_API_KEY=your_mango_api_key_here  # Получить в ЛК
MANGO_VIRTUAL_NUMBER=+7XXX-XXX-XX-XX

# TTS — 3 варианта на выбор
GEMINI_API_KEY=your_gemini_api_key_here  # https://aistudio.google.com/apikey
GEMINI_US_PROXY=socks5://Q3NeJXTY:dsBaWh2L@172.120.21.141:64469

INWORLD_API_KEY=your_inworld_api_key_here  # https://inworld.ai/api (премиум)

# Bitrix24 Webhook
BITRIX_WEBHOOK_URL=https://b24-vskitj.bitrix24.ru/rest/15/your_webhook_here/

# Telegram (уведомления)
TELEGRAM_BOT_TOKEN=your_tg_bot_token_here
TELEGRAM_OWNER_CHAT_ID=176203333
```

---

## 📊 ИТОГИ ДНЯ 14.05.2026

### ✅ Выполнено:
1. **Unified Morning Report** — один отчёт в 08:00 ✅
2. **Аудит Avito** — 68 объявлений, 8,000₽/мес впустую ✅
3. **Ночной аудит** — исправлены баги ✅
4. **Фаза 14.3** — освежено решение по автодозвону ✅
5. **TTS Research** — найдено 3 голосовых сервиса ✅
6. **Mango Credentials** — логин/пароль записаны в `.env.mango.example` ✅
7. **Gemini TTS тест** — ✅ API работает, модель `gemini-2.5-flash-preview-tts` ✅
8. **Скрипт автодозвона** — профессиональный текст (17 сек) ✅
9. **Аудиофайл для Андрея** — `andrej_call_100_gosyat.wav` (18 сек, голос Kore) ✅

### 📁 Изменено файлов:
| Файл | Изменения |
|------|-----------|
| `ai-eggs/.env.mango.example` | 🆕 Создан + логин/пароль Mango |
| `ai-eggs/agent/outbound_confirm.py` | 🆕 Обновлён (3 TTS на выбор) |
| `ai-eggs/agent/test_gemini_tts.py` | 🆕 Тест TTS API |
| `ai-eggs/agent/test_gemini_tts_advanced.py` | 🆕 TTS с настройками |
| `ai-eggs/agent/generate_call_script.py` | 🆕 Генератор скриптов |
| `ai-eggs/agent/call_script_confirmation.md` | 🆕 Профи скрипт |
| `ai-eggs/agent/call_script_my_version.md` | 🆕 Мой вариант (17 сек) |
| `ai-eggs/agent/andrej_call_100_gosyat.wav` | 🆕 Аудио готово (Kore, 18 сек) |
| `chronicles/chronicle_2026-05-14.md` | 🔄 Дополнена |

### 🚀 Следующие шаги (P0):
1. **Mango API Key** — зайти в ЛК (16741963 / 2026incubator!) → Настройки → API → создать ключ
2. **Bitrix24 Webhook** — настроить триггер ONCRMLEADADDED
3. **Тест звонка** — загрузить `andrej_call_100_gosyat.wav` в Mango Office → тестовый звонок
4. **Интеграция** — обновить `outbound_confirm.py` для Gemini TTS (не Yandex)

### 🧠 Запомнено (feedback):
- ❌ **Голос Puck** — запрещён («ужасный голос»)
- ✅ **Kore** — голос по умолчанию для TTS

---

> 🤖 Сгенерировано: `tools/finish_day_cron.sh` — Хроника дня v2
- **20:57** — --end
