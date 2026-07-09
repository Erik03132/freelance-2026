# Levitan — Active Tasks

Важные задачи и инициативы по улучшению агента. Обновляется по ходу сессий.

---

## [ACTIVE] Real-time голосовой агент (full-duplex) — вместо turn-based

**Статус:** DRAFT-набросок готов, ждёт сборки audio-моста и теста.
**Приоритет:** высокий (качественный скачок конверсии холодных звонков)
**Дата старта:** 2026-07-09

### Контекст
Источник идеи: OpenAI GPT-Live (dailyprompts/8895) — full-duplex voice, backchannel, barge-in.
Цель: превратить робота-опросник (turn-based WAV-своп) в «продавца», с которым можно
говорить как с живым человеком. Главная бизнес-выгода — выше конверсия (меньше сбросов
на паузах, умение перебить = барж-ин).

### Что выяснено (2026-07-09)
- **Mango REST API НЕ даёт live-аудио.** Проба прав:
  `commands/callback`, `queries/recording/post` → OK;
  `commands/call`, `commands/play`, `media/*`, `config/users` → **3128 (нет прав)**.
  ⇒ Потоковый аудио берём не из Mango, а локально из **baresip** (ext 22, SIP/RTP).
- OpenAI Realtime API — актуальная GA-модель **`gpt-realtime-2.1`** (есть mini-версия).
  Для phone-пайплайнов дока рекомендует **WebSocket** (используем) или SIP.
- **Экономика** (на 1 дозвонившийся звонок, агент ~60с, клиент ~45с):
  - full `gpt-realtime-2.1`: ≈ **$0.10**
  - mini `gpt-realtime-2.1-mini`: ≈ **$0.03**
  - Кампания 100 обзвонов (30% дозвон = 30 разговоров): full ≈ $2.9, mini ≈ $1.0
  - Текущая turn-based схема (DeepSeek+локальный Whisper/TTS): ≈ $0.12 на всю 100-звонку
  - Реал-тайм дороже в ~8–25×, но доп. расход $1–3 на 100 звонков окупается ростом
    конверсии хотя бы на 1 лид.

### Что сделано в коде
Файл: `deploy/levitan_turnbased.py` — добавлен класс `RealtimeDialog` (DRAFT, синтаксис OK):
- `REALTIME_MODEL` по умолчанию = `gpt-realtime-2.1-mini`.
- `session.update` приведён к GA-форме: `session.type:"realtime"`,
  выходное аудио под `audio.output.format`, `reasoning.effort:"low"`.
- Убран заголовок `OpenAI-Beta: realtime=v1` (в GA не нужен).
- События приведены к GA: `response.output_audio.delta`,
  `response.output_audio_transcript.done`, `conversation.item.input_audio_transcription.completed`.
- Поток A: capture FIFO → `input_audio_buffer.append`; Поток B: audio.delta → playback FIFO.
- Запуск: `python3 levitan_turnbased.py realtime <phone>`.

### Что осталось довести (блокеры до теста)
1. **Яндекс Cloud API-ключ** — сервисный аккаунт с ролями `ai.speechkit-stt.user`, `ai.speechkit-tts.user`, `ai.languageModels.user`, `ai.models.user` + `YC_API_KEY`, `YC_FOLDER_ID` в `.env`. **БЛОКЕР: аккаунта пока нет, задача на следующую сессию**.
2. `OPENAI_API_KEY` в `.env` (Realtime API отдельный от OpenRouter/DeepSeek).
3. `pip install websockets` в venv.
4. **baresip audio-мост** — playback через `aufile` из FIFO, capture через `record` в FIFO; конверсия 8k↔24k через `auresamp.so`. Единственный нетривиальный кусок.

### Риски
- Зависимость от baresip/VPS (текущие блокеры проекта) реал-тайм не убирает.
- STT на плохих линиях/hold music — в Realtime API транскрипция своя (whisper-1/gpt-4o-transcribe).

---