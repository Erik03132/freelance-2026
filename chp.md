# Чекпоинт: 16.06.2026

## 🔥 Главное событие дня
Создана **Voice Angela** — голосовой ассистент для входящих звонков на базе Анжелы (ai-eggs). Голос Kore (Gemini TTS). Готовится к тесту завтра 09:00 MSK.

## Архитектура Voice Angela
```
Клиент → Mango → baresip (SIP) → sndfile → dec.wav
                                         ↓
           voice_bridge.py: VAD → Whisper STT → Angela (OpenRouter)
                                         ↓
           TTS Kore (Gemini через прокси) → upload → Mango play/start
                                         ↓
                                    Loop
```

## Что сделано

### Код (локально + VPS)
- `voice_bridge.py` — PM2 процесс `voice-angela` на VPS
- `test_voice_call.py` — скрипт тестового звонка
- `test_angela_kore.py` — локальный текстовый тест (Mac)
- `mango_webhook_vps.py` — расширен: пишет события звонков в `/var/log/voice-angela/events.jsonl`
- `start_voice_test.sh` — быстрый запуск теста

### Конфиги VPS
- `/root/.baresip/config` — добавлены `sndfile.so`, `ctrl_tcp.so`, удалён `dtmfio.so` (нет модуля)
- `/root/.baresip/accounts` — SIP-аккаунт `user4@vpbx400161137.mangosip.ru`
- PM2: `voice-angela` (id 21), `mango-webhook` (id 8)

### Зависимости VPS
- `edge-tts` (установлен, но не используется — используем Kore)
- `faster-whisper` (base model, CPU int8)
- `ffmpeg` (конвертация 24kHz→8kHz)
- Прокси SOCKS5 для Gemini TTS (`_TTS_PROXY` в voice_bridge.py)

## Тесты
- **Angela (OpenRouter DeepSeek):** ✅ Знает цены, породы, доставку
- **Kore TTS (через прокси):** ✅ HTTP 200, ~0.4-1с генерация
- **Whisper STT:** ✅ Установлен
- **VAD (энергетический):** ✅
- **Mango API (commands/callback):** result: 1000 — **но звонки не доходят ночью**
- **Mango play/start:** ✅ (проверен в автодозвоне)
- **baresip регистрация:** ⚠ Не посылает REGISTER на Mango SIP — нужна диагностика

## Заблокировано до завтра 09:00 MSK
Тестовый звонок через Mango API не проходит ночью. Рабочий автодозвон работает только в 09:00 MSK (см. scheduler.log).

## Как запустить тест завтра
```bash
ssh root@72.56.38.19
cd /root/antigravity/ai-eggs
bash agent/start_voice_test.sh
# Или:
python3 agent/test_voice_call.py --phone "+79687896924"
```

## Файлы сессии
- `tools/habr_intelligence.py` — v2: VC.ru, GitHub, Telegram @vibecoding_tg и др.
- `ACTIVE_TASKS.md` — P1 RAG & Eval (#17 LLM as judge, #18 RAGAS, #19 Recall@K)
- `voice_bridge.py` — голосовая Анжела
- `docs/superpowers/specs/2026-06-16-realtime-voice-angela.md` — спецификация
- `agent-lab/test_angela_kore.py` — локальный тест Angela

## Важные заметки
- Gemini TTS (Kore) на VPS работает ТОЛЬКО через SOCKS5 прокси
- На Mac Gemini TTS не работает — User location not supported (ограничение API-ключа РФ)
- baresip `dtmfio.so` отсутствует в модулях — удалён из конфига (DTMF работает через Mango webhook)
- `auto_confirm_call.py` — эталон реализации Mango callback API (включает поле `sip` в `from`)
