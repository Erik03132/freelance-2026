# 📜 ХРОНИКА ДНЯ: 19.06.2026 (пятница)

> Автоматическая хроника всех сессий за день.
> Каждая сессия дописывает сюда свои действия в реальном времени.

---

## 🕐 Сессия ~07:00 | Voice Angela Realtime

- **07:00** — 🔧 Исправлен `angela-bot` в краш-лупе 8617 раз (прокси `localhost:1080` → `172.120.21.141:64469`)
- **07:10** — 🔧 Исправлен баг `call_id` в `mango_webhook.py` (NameError при событии Appeared)
- **07:15** — 🔍 Диагностика: `dec.wav = 44 байта` — Mango НЕ шлёт RTP клиента на VPS
- **07:30** — 📡 tcpdump подтвердил: 0 RTP пакетов от Mango (81.88.88.55) при callback
- **07:45** — 🔄 Переключение с baresip на **Asterisk 20.6**
- **07:50** — ⚙️ Asterisk переведён с `chan_sip` → **PJSIP** (chan_sip deprecated в v20)
- **08:00** — ✅ PJSIP зарегистрирован: `user4@vpbx400161137.mangosip.ru` → `Registered`
- **08:05** — ✅ Добавлен `identify` по IP Mango: `81.88.86.11`, `81.88.88.0/24`
- **08:10** — 🔧 Dialplan `from-mango`: `Answer → MixMonitor → AGI(angela_agi.py)`
- **08:15** — 🎉 **ПРОРЫВ**: `mixmon_*.wav` растёт с RMS=2126 — Asterisk пишет речь клиента!
- **08:20** — ✅ Whisper STT транскрибировал: `'1,2,3,1,2,3,4,5,7,8,9,10...'` — верно!
- **08:25** — 📝 Написан `/opt/angela_agi.py` с нуля: VAD + STT + LLM + TTS цикл
- **08:30** — ✅ Анжела произнесла приветствие голосом на линию (edge-tts → Playback)
- **08:45** — ⚡ Оптимизация скорости: Whisper `base`→`tiny` (3x быстрее), LLM `qwen-72b`→`llama-8b` (4x быстрее), VAD пауза 1.2→0.8 сек
- **09:00** — 🔧 Исправлен UNIQUEID→`${EPOCH}` в dialplan (mixmon_.wav → mixmon_1234.wav)
- **09:10** — 🔧 Добавлен Gemini TTS Kore через прокси, fallback на edge-tts
- **09:13** — ⚠️ Диалоговый цикл нестабилен: после приветствия тишина (STT→LLM→TTS не всегда отрабатывает)
- **13:13** — 📝 Записано в хронику и chp.md

---

## 📊 Итог дня

### ✅ Работает
| Компонент | Статус |
|-----------|--------|
| Asterisk PJSIP регистрация | ✅ |
| MixMonitor запись речи клиента | ✅ RMS=2126 |
| faster-whisper STT | ✅ |
| edge-tts TTS + Playback | ✅ |
| Приветствие голосом на линию | ✅ |

### ⚠️ В работе
| Проблема | Статус |
|----------|--------|
| Диалоговый цикл STT→LLM→TTS | ⚠️ нестабилен |
| Kore голос (Gemini TTS) | ⚠️ VPS нет доступа к Gemini API |
| UNIQUEID пустой иногда | ⚠️ фикс через EPOCH |

### 🔧 Файлы созданы/изменены
- `/opt/angela_agi.py` — Realtime AGI движок
- `/etc/asterisk/pjsip.conf` — PJSIP + Mango
- `/etc/asterisk/extensions.conf` — Dialplan
- `/root/antigravity/ai-eggs/.env` — прокси исправлен
- `/opt/mango_webhook.py` — call_id баг исправлен

---

## 🎯 Следующие шаги
1. Отладить диалоговый цикл (добавить `/tmp/angela_agi.log` вывод)
2. Тест полного диалога: вопрос → ответ LLM голосом
3. Подключить Kore (Gemini TTS через прокси уже добавлен, нужен тест)
4. PM2 watchdog для Asterisk
