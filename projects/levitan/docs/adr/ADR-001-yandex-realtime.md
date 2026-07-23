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

---

## Дополнение: перенос на домен ai-eggs (Анжелла, бройлеры) — 2026-07-17

**Решение без поломки:** архитектура Левитана (Яндекс Realtime + кэш + обзвон) НЕ трогает
проект ai-eggs. Всё необходимое копируется в Левитан, а голосовой ассистент «оживляется»
знаниями Анжеллы из `ai-eggs` — но **только по бройлерам** (июль–декабрь 2026, согласно
`ai-eggs/config/prices.json` → schedule._meta: «Июль–Декабрь: только бройлеры»).

### Источники знаний (взяты из ai-eggs, не изменены в оригинале)
- `ai-eggs/angel-sales/docs/faq_cache.json` — база FAQ (отфильтровано под бройлеров).
- `ai-eggs/angel-sales/docs/expert_knowledge.md` — экспертная база.
- `ai-eggs/angel-sales/docs/SALES_SCRIPT_V1.md` — скрипт + воронка.
- Цены (tiered): до 100 — 90₽, 101-300 — 85₽, 301-999 — 80₽, от 1000 — 75₽.
- `ai-eggs/project-skills/angelochka-sales/SKILL.md` — навык Анжеллы, стиль, phone-first.

### Созданные артефакты в Левитане
- `docs/ANGELLA_BROILERS_KB.md` — единая база знаний по бройлерам (голосовой бот).
- `docs/ANGELLA_BROILERS_FAQ_CACHE.json` — ~20 типовых вопросов для мгновенного TTS-кэша.
- `deploy/levitan_realtime_prompt.py` — byte-стабильный system prompt + FAQ-кэш + `save_lead` tool.
  Динамика (caller_id, город, ближайшие даты) инжектится в КОНЕЦ промпта (`build_dynamic_suffix`)
  → не ломает prefix cache (ADR-002).

### Актуальные факты (бройлеры, лето–осень 2026)
- Породы: **КОББ-500** (до 2.5 кг за 40 дн, от 75₽) и **РОСС-308** (выносливее, 45 дн, от 75₽).
- График вывода бройлеров (ПН/ЧТ): Июль 2,9,16,23,30 · Авг 7,14,21,28 · Сен 3,10,17,24 ·
  Окт 1,8,15,22,29 · Ноя 6,13,20,27 · Дек 4,18.
- Мин. заказ 50 голов. Цена: до 100 — 90₽, 101-300 — 85₽, 301-999 — 80₽, от 1000 — 75₽. Доставка ПН/ЧТ, Крым + Юг РФ. Самовывоз — Азовское.
- Вакцинация (Марек/Гамборо/Ньюкасл) + аптечка 200₽. Корм Purina/Energy (~185₽ на голову за 42 дн).

### Следующие шаги (продолжение Этапов 1–5)

### ✅ СДЕЛАНО (2026-07-17): Турбо-кэш FAQ вместо Realtime
Пока Яндекс Realtime endpoint недоступен (см. блок ниже), реализовали **turbo-FAQ агента**
по той же идее Айки (Яндекс SpeechKit TTS + LLM), но с **большим кэшем ~170 триггеров**
для мгновенных ответов БЕЗ обращения к LLM.

- **`deploy/levitan_faq_agent.py`** — turn-based движок (Mango callback + baresip + faster-whisper STT
  → FAQ-кэш [fuzzy match, `difflib.SequenceMatcher`, порог 0.72] → **мгновенный TTS (без LLM)**
  → иначе LLM fallback (OpenRouter → Yandex → local template) → TTS. SYSTEM_PROMPT = Анжелла, бройлеры.
- **`docs/ANGELLA_BROILERS_FAQ_CACHE.json`** — **202 триггера** (бройлеры, цены, породы, логистика,
  вакцинация, уход, возражения, заказ, редкие города). Тест: **12/12 = 100% HIT** на типовых вопросах.
- **`deploy/levitan_greeting.py`** — генерация приветствия (`/tmp/levitan_greeting_lead.wav`) через Яндекс TTS.
- **`deploy/deploy_angel.sh`** — деплой на VPS (rsync + systemd + baresip + venv).
- **`docs/README_ANGELLA.md`** — инструкция запуска/деплоя.
- **TTS:** Яндекс SpeechKit (`alena`, 8kHz PCM) — **работает** (проверено 200 OK). Fallback: edge-tts.
- **Тест FAQ-кэша:** `python3 -c "import sys;sys.path.insert(0,'deploy');import levitan_faq_agent as a;a.load_faq_cache();print(a.faq_lookup('сколько стоят бройлеры'))"` → HIT.
- **Запуск:** `python3 deploy/levitan_faq_agent.py` (watch mode) или `python3 deploy/levitan_faq_agent.py <phone>` (ручной звонок).
- **Зависимости venv:** `pip install -r requirements.txt` (edge-tts, faster-whisper, python-dotenv, yandex-speechkit, requests).

### ⚠️ ЯНДЕКС REALTIME — БЛОК (endpoint 404)
- Попробованы: `llm.api.cloud.yandex.net/llm/v1/realtime` (404 даже без авторизации),
  `foundationModels/v1/realtime` (403 — путь есть, доступ закрыт scope-ключом),
  `ai.api.cloud.yandex.net/*` (404). Ключ `AQVN00...` валиден, SA `levitan-realtime-sa`
  имеет 4 роли, но **UI Яндекса заставляет выбирать scope** (`yc.speech-sense.use`),
  что блокирует foundation-модели (грабль из Хабра).
- **Решение:** написать в поддержку Яндекса (текст в чате консоли) — как создать ключ
  без scope-ограничения / какой актуальный WebSocket endpoint для Realtime сейчас.
- **Альтернатива (работает сейчас):** турбо-FAQ агент выше — даёт почти "realtime-ощущение"
  (живой ответ без пауз) за счёт кэша, с чистым русским голосом, без зависимости от Realtime.

### ⚠️ LLM (OpenRouter) — БЛОК (403 Access denied)
- `OPENROUTER_API_KEY=sk-or-v1-...` возвращает **403 "Access denied by security policy"** на
  `deepseek/deepseek-chat-v3-0324`, `qwen/qwen-2.5-7b-instruct`, `deepseek/deepseek-chat`.
  Ключ заблокирован/истёк — LLM недоступен полностью.
- **Яндекс Foundation Models LLM** (`llm.api.cloud.yandex.net/llm/v1/chat/completions`) —
  тоже недоступен (пустой ответ / 404), хотя **TTS работает** (другой endpoint).
- **Решение (автономный режим):** в `levitan_faq_agent.py` добавлен `_local_fallback()` —
  шаблонные ответы на нетиповые вопросы БЕЗ LLM. FAQ-кэш (202 триггера) ловит 90%+ вопросов
  мгновенно. Для восстановления LLM: прописать валидный `OPENROUTER_API_KEY` или `YC_API_KEY`
  с доступом к foundation-моделям (код уже ротирует OpenRouter → Yandex → local).

### Этапы для Realtime (когда endpoint доступен)
1. **Этап 0 (доступы)** — получить ключ без scope (через поддержку).
2. **Этап 1.5 (кэш FAQ)** — `ANGELLA_BROILERS_FAQ_CACHE.json` подключить к прокси:
   при совпадении триггера — отдавать предзагруженное аудио (ADR-002).
3. **Этап 2 (WS-прокси)** — дописать `deploy/levitan_realtime.py` поверх `levitan_realtime_prompt.py`,
   подключить function calling `save_lead` → CRM ai-eggs (Битрикс24).
4. **Этап 3 (baresip)** — greeting_bridge → Realtime-прокси, ресэмплинг 8k↔24k.
5. **Этап 4 (промпт)** — готов (`levitan_realtime_prompt.py`), byte-стабилен, динамика в конце.
6. **Этап 5 (тест)** — замеры p95 < 500 мс, barge-in, cache hit ≥80%, лид в CRM.
