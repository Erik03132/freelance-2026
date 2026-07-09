# ADR-001: Миграция голосового агента на Яндекс Realtime (speech-to-speech)

**Дата:** 2026-07-09
**Статус:** Accepted (в реализации)
**Контекст:** Habr-кейс «OpenAI Realtime против Яндекс Realtime» (habr.com/ru/articles/1057176)

## Контекст и решение

Levitan — голосовой агент обзвона аграриев РФ. Текущая трёхзвенка (STT→LLM→TTS, `deploy/levitan_turnbased.py`) даёт **~4.4 с** задержки — в живом диалоге воспринимается как «бот завис». Нужен real-time speech-to-speech.

**Решение:** перевести агента на **Яндекс Realtime API** (AI Studio), оставив трёхзвенку как fallback.

### Почему не OpenAI Realtime
- Заблокирован в РФ → клиент без VPN не подключится.
- Английский акцент на русском (промптом не лечится, fine-tune голоса недоступен).
- Оплата из РФ — отдельный квест.

### Почему Яндекс Realtime
- Родной русский без акцента.
- Работает из РФ напрямую → **~330 мс** end-to-end (против ~740 мс OpenAI под VPN).
- Оплата рублями, ~пары руб./мин.
- Та же событийная модель, что у OpenAI (`input_audio_buffer.append`, `response.output_audio.delta`, `speech_started`, function calling) — миграция тривиальна.

## Архитектура

```
Клиент (телефон)
   │ SIP/RTP 8kHz
   ▼
Mango callback → baresip (ext 22, greeting_bridge)
   │ PCM 8kHz s16 (FIFO)
   ▼
FastAPI WS-прокси (deploy/levitan_realtime.py)  ← держит YC_API_KEY
   │ PCM 24kHz s16 (auresamp 8k↔24k)
   ▼
Яндекс Realtime WS  (wss://llm.api.cloud.yandex.net/.../realtime)
   │ response.output_audio.delta (PCM 24kHz)
   ▼
прокси → baresip (auresamp 24k→8k) → клиенту
```

**Ключевое:** backend-прокси обязателен — у Яндекса нет ephemeral-токенов для клиента, а SIP/браузер не ставит `Authorization: Api-Key`. Прокси держит ключ и перекачивает аудио + события.

## Этапы реализации

### Этап 1 — Доступы и зависимости
1. **Яндекс Cloud:** сервисный аккаунт с ролями `ai.speechkit-stt.user`, `ai.speechkit-tts.user`, `ai.languageModels.user`, **`ai.models.user`** (критично для Realtime). Новый API-ключ без scope-ограничений.
2. `.env`: добавить `YC_API_KEY`, `YC_FOLDER_ID`, `YC_REALTIME_MODEL` (по умолчанию `yandex-rt`), `YC_REALTIME_VOICE` (`alena`).
3. `requirements.txt`: добавить `websockets>=12.0`.
4. `pip install websockets` в venv.

### Этап 2 — WS-прокси (deploy/levitan_realtime.py), TDD
1. Тесты (`tests/test_realtime_proxy.py`): мок WS Яндекса, проверка мостов `client→yc` и `yc→client`, session.update, barge-in, function calling → CRM.
2. FastAPI endpoint `/voice/stream-rt` (WebSocket):
   - `websockets.connect(RT_URL, additional_headers={"Authorization": f"Api-Key {YC_API_KEY}"})`.
   - Отправка `session.update` (промпт, голос, `server_vad`, tools: `save_lead`).
   - `asyncio.gather(client_to_yc(), yc_to_client())`.
3. Ресэмплинг 8k↔24k (через `audioop`/`librosa` или `auresamp` в baresip — см. Этап 3).
4. Function calling: при `response.output_item.done` с tool `save_lead` → POST `/api/contacts` в CRM (порт 8088).

### Этап 3 — baresip audio-мост (greeting_bridge)
1. `config`: `audio_player aufile,<play_fifo>`, `audio_source aufile,<cap_fifo>` (FIFO, raw PCM s16).
2. `auresamp.so`: 8kHz (SIP) ↔ 24kHz (прокси). Либо ресэмплинг в Python-прокси.
3. `controller.py`: вместо `/call/transfer` на оператора — мост в Realtime-прокси (подключение WS при `call_established`).
4. `echoCancellation`: baresip `aec` модуль или `ausrc` с AEC.

### Этап 4 — Промпт под голос
1. `SYSTEM_PROMPT` → формат «роль + факты + цены + запреты», **без JSON**.
2. Жёсткое «не выдумывай услуги/цены».
3. Tool `save_lead(culture, volume, region, basis, deadline)` — модель сама вызывает при сборе данных.

### Этап 5 — Интеграция и тест
1. CRM: `save_lead` → POST `/api/contacts`.
2. Mango callback → baresip → прокси → Яндекс.
3. Замеры: latency < 500 мс, barge-in работает, эхо не зацикливается, лид в CRM.
4. Fallback: `levitan_turnbased.py` остаётся отдельным эндпоинтом.

## Риски
- **Доступы Яндекса**: с 2026-06-01 обмен пользовательских OAuth на IAM закрыт — роли назначать руками в консоли.
- **baresip AEC**: на ноутбучных колонках может ловить эхо — нужен `echoCancellation` или наушники на старте.
- **PCM sample rate**: Яндекс хочет 24kHz, SIP = 8kHz — ресэмплинг обязателен.
- **Промпт**: JSON-формат ломает голос — только естественная речь.

## Критерии готовности
- [ ] Тесты прокси зелёные.
- [ ] Latency end-to-end < 500 мс.
- [ ] Barge-in работает (`speech_started` прерывает ответ).
- [ ] Лид сохраняется в CRM через function calling.
- [ ] Трёхзвенка доступна как fallback.
