# Voice Angela — голосовой ассистент на базе Анжелы

## Цель
Входящий голосовой помощник: клиент звонит → говорит с Анжелой (голос Kore) → Angela отвечает по делу (цены, породы, доставка) → при необходимости перевод на оператора.

## Текущий статус (16.06.2026)
- ✅ MVP реализован, все компоненты работают
- ⏳ Тестовый звонок — завтра 09:00 MSK (ночью Mango не звонит)
- ⏳ Настройка inbound routing в Mango (пока не трогали — рабочие звонки на менеджеров)

## Архитектура (file-based near-real-time)

```
Клиент → Mango → SIP → baresip (auto-answer)
                                  ↓
              sndfile пишет голос клиента в /root/dec.wav
                                  ↓
voice_bridge.py (PM2 voice-angela):
  dec.wav → VAD (энергетический) → Whisper STT (base, ru)
                                  ↓
  Angela → OpenRouter DeepSeek (знает цены + породы + доставку)
                                  ↓
  Kore TTS → Gemini 2.5 Flash Preview TTS (через SOCKS5 прокси)
                                  ↓
  24kHz→8kHz (ffmpeg) → upload to Mango → play/start → клиент слышит
                                  ↓
                              Loop (до 20 реплик)
```

## Компоненты

### VPS (72.56.38.19)
| Компонент | Файл / Путь | PM2 имя |
|-----------|------------|---------|
| Voice bridge | `/root/antigravity/ai-eggs/agent/voice_bridge.py` | `voice-angela` (id 21) |
| Mango webhook | `/opt/mango_webhook.py` | `mango-webhook` (id 8) |
| baresip config | `/root/.baresip/config` | `baresip-watchdog` (id 11) |
| baresip accounts | `/root/.baresip/accounts` | — |
| События звонков | `/var/log/voice-angela/events.jsonl` | — |
| TTS cache | `agent/tts_cache/` | — |
| Логи | `/var/log/voice-angela/` | — |

### Ключевые конфиги baresip
- Порт: 5060
- SIP: `user4@vpbx400161137.mangosip.ru`
- Extension: 22
- Audio source: `aufile,/tmp/mango_play.wav`
- Модули: `uuid`, `aufile`, `g711`, `sndfile`, `ctrl_tcp`
- `auto_answer=yes`, `auto_answer_delay=0`

### Знания Анжелы
- **Цены и породы:** `ai-eggs/config/prices.json` (загружается в `load_price_context()`)
- **LLM:** OpenRouter DeepSeek Chat (fallback Qwen Turbo)
- **Системный промпт:** в `angela_response()` — кратко, естественно, по делу

### TTS
- **Голос:** Kore (Gemini 2.5 Flash Preview TTS)
- **Прокси:** SOCKS5 из .env (ALL_PROXY/HTTP_PROXY), сохраняется в `_TTS_PROXY`
- **Конвертация:** 24kHz PCM → ffmpeg → 8kHz WAV
- **Fallback:** edge-tts (установлен, не используется)

### STT
- **Модель:** faster-whisper base (CPU, int8)
- **Язык:** русский
- **VAD:** энергетический (threshold 0.015)

## Файлы проекта

| Файл | Описание |
|------|----------|
| `ai-eggs/agent/voice_bridge.py` | **Главный** — PM2 voice-angela |
| `ai-eggs/agent/test_voice_call.py` | Тестовый звонок через Mango API |
| `ai-eggs/agent/mango_webhook_vps.py` | Webhook — пишет события звонков |
| `ai-eggs/agent/start_voice_test.sh` | Быстрый запуск теста |
| `agent-lab/test_angela_kore.py` | Локальный текстовый тест (Mac) |
| `docs/superpowers/specs/2026-06-16-realtime-voice-angela.md` | Этот документ |

## Как тестировать

### 1. Локально (текст, Mac)
```bash
python3 agent-lab/test_angela_kore.py
# Печатаешь вопросы — Angela отвечает
```

### 2. Тестовый звонок (VPS, утром 09:00+ MSK)
```bash
ssh root@72.56.38.19
cd /root/antigravity/ai-eggs
bash agent/start_voice_test.sh
# Или:
python3 agent/test_voice_call.py --phone "+79687896924"
```

### 3. Через продакшен автодозвон
```bash
ssh root@72.56.38.19
cd /root/antigravity/ai-eggs
python3 agent/auto_confirm_call.py +79687896924
```

## Известные проблемы
1. **Ночью Mango не звонит** — тест только утром 09:00+ MSK
2. **Gemini TTS не работает без прокси из РФ** — `_TTS_PROXY` обязателен
3. **baresip не шлёт REGISTER** — Mango всё равно может дозвониться (нужна диагностика)
4. **dtmfio.so отсутствует** — удалён из конфига (DTMF через Mango webhook)
5. **Входящая маршрутизация Mango** — пока не настроена (ждём теста)

## Todo
- [ ] Тестовый звонок утром 17.06
- [ ] Настроить inbound routing в Mango (если тест пройдёт)
- [ ] GStreamer для настоящего streaming (вместо file-based)
- [ ] Silero VAD для лучшей детекции речи
- [ ] Предзагруженные audio_id для частых фраз (greeting, повторите, оператор)
