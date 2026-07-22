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

### Статус VPS (2026-07-21)
- **Новая VPS:** 217.149.23.113 (Timeweb, 1 vCPU/2GB/30GB, Ubuntu 22.04)
- **baresip 1.0.0** установлен, ждёт настройки Mango SIP аккаунта
- **9 PM2-процессов** запущены: все боты + Astro-сайт
- **UFW:** порты 22/5060/4321/5000/8085/8086/16384-32768 открыты

### Риски
- Зависимость от baresip/VPS — VPS жива, baresip ждёт Mango SIP настройки
- STT на плохих линиях/hold music — в Realtime API транскрипция своя (whisper-1/gpt-4o-transcribe).

---

## [NEW] Оценка BytePlus Seed Speech (SeedTTS 2.0) — альтернатива OpenAI Realtime API

**Статус:** TO-EVALUATE
**Приоритет:** высокий (потенциал 150× экономии на TTS)
**Дата старта:** 2026-07-23

### Контекст
BytePlus Seed Speech — платформа голосовых AI-моделей от ByteDance (TikTok).
SeedTTS 2.0 — SOTA TTS, не уступающий ElevenLabs/OpenAI, при цене на порядки ниже.
Доступен из РФ (Китай, не под санкциями).

### Что известно
- **Bi-directional WebSocket TTS** — real-time, full-duplex, подходит для голосового агента
- **ASR Streaming** — STT в реальном времени (альтернатива Whisper)
- **Voice Replication** — клонирование голоса для единого тона агента
- **Live Interpretation** — перевод в реальном времени
- **Seed 2 Mini:** $0.10/1M input, $0.40/1M output (против $15/1M у OpenAI TTS)
- **Seed 1.6 Flash:** $0.075/1M input, $0.30/1M output (самый дешёвый)
- Используется в CapCut, Lark, Fanqie Novel — battle-tested

### Что нужно проверить
1. **Русский язык** — качество синтеза, поддерживаются ли эмоции/интонации
2. **API из Python** — WebSocket SDK, примеры, авторизация
3. **ASR качество** — сравнить с Whisper/Yandex STT на реальных записях звонков
4. **Voice Replication** — сколько образцов нужно, как загрузить, цена
5. **Экономика для сценария 100 звонков** — сравнить с OpenAI Realtime API ($0.03/звонок mini)
6. **Задержка (latency)** — WebSocket поток vs HTTP polling

### План
1. Завести аккаунт BytePlus, получить API-ключ
2. Написать скрипт `test_byteplus_tts.py` — синтез русского текста, замер качества и скорости
3. Написать `test_byteplus_asr.py` — ASR на тестовой записи звонка
4. Сравнить результаты с OpenAI Realtime API и Yandex SpeechKit
5. Принять решение: использовать как основной TTS/STT бэкенд или как fallback

### Связанные файлы
- `deploy/levitan_turnbased.py` — сюда добавлять второй TTS-бэкенд
- `.env` — нужны ключи BytePlus

---

## [NEW] OmniRoute — AI-шлюз для всех API (внедрён)

**Статус:** INSTALLED (v3.7.9, нужна настройка провайдеров)
**Приоритет:** высокий (замена каскадной системы, авто-fallback, компрессия токенов)
**Дата:** 2026-07-23

### Что сделано
- Установлен на VPS (217.149.23.113:20128) через npm
- Node.js обновлён до v22.23.1 (Next.js 16 требует 22+)
- Запущен через PM2 (автостарт при перезагрузке)
- Настроен SOCKS5-прокси для доступа к заблокированным API из РФ
- Включён TLS fingerprint stealth (JA3/JA4 — маскировка под Chrome)
- Порт 20128 открыт в UFW

### Что нужно сделать
1. **Войти в дашборд:** http://217.149.23.113:20128
   - Пароль: `Levitan2026!`
2. **Добавить OpenRouter API-ключ** (взять из `.env` проекта)
3. **Настроить Auto-Combo** — OmniRoute сам будет выбирать провайдера
4. **RTK + Caveman** — компрессия для снижения расхода токенов

### Эффект для проекта
- Вместо ручного каскада (Tier 0→1→2→3) — OmniRoute сам выбирает
- Экономия ~89% токенов через RTK+Caveman компрессию
- Встроенный TLS stealth заменяет US прокси для заблокированных API
- Единый endpoint для всех AI-запросов

### Связанные файлы
- `~/.omniroute/.env` (на VPS) — конфигурация
- AGENTS.md — будет упрощена каскадная система

---