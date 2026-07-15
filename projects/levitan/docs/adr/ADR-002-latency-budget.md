# ADR-002: Бюджет задержки голосового агента (latency budget) для Realtime-архитектуры

**Дата:** 2026-07-15
**Статус:** Proposed
**Контекст:** синтез из видео «I Made My AI Voice Agent 2x Faster (Every Setting)» + свежий (2026) консенсус по voice-agent latency (LiveKit, ElevenLabs, Vapi, OnCallClerk, HuggingFace playbook). Дополняет ADR-001 (миграция на Яндекс Realtime).

## Контекст и решение

ADR-001 переводит Levitan на **speech-to-speech realtime** (Яндекс Realtime). В такой архитектуре STT→LLM→TTS **слиты в одну модель**, поэтому классические «pipeline»-оптимизации (стрим токенов LLM→TTS вручную, speculative generation по partial transcript) уже делает сам realtime-движок. Цель ADR-002 — зафиксировать те рычаги, которые **остаются на нашей стороне** и ещё не реализованы в `deploy/levitan_realtime.py` / `greeting_bridge`.

**Целевой бюджет (perceived latency, p95):** `< 500 мс` для коротких turns (из ADR-001). Декомпозиция по стадиям (нормы из playbook):

| Стадия | Good | Acceptable | Broken |
|---|---|---|---|
| Endpointing (VAD) | <300ms | <600ms | >800ms |
| LLM TTFT (realtime) | <400ms | <900ms | >1500ms |
| TTS TTFB | <250ms | <500ms | >800ms |
| Network egress (телефония) | <100ms | <250ms | >400ms |

Телефония (SIP/Mango) добавляет **~600ms+** сетевого оверхеда против ~100ms у WebRTC — это самый дешёвый и самый недооценённый рычаг для Levitan.

## Применимые решения (в порядке ROI)

### 1. Byte-стабильный system prompt + prefix caching (ADR-001 Этап 4)
- Prompt держим **коротким** (роль + факты + цены + запреты, без JSON) — уже в плане.
- **Новое:** чтобы сработал server-side prefix cache провайдера (TTFT 800ms→300ms), system-блок должен быть **byte-идентичен между turns**.
- ⚠️ **Ошибка, которую нельзя допускать:** динамику (`Дата: {today}`, данные лида, `caller_id`) НЕ вставлять в начало промпта — это ломает кэш. Класть в **конец** system-блока или в первое user-сообщение.
- Реализация: в `session.update` промпт собирается один раз, динамика инжектится в trailing-часть.

### 2. VoIP / SIP-роутинг и кодек (greeting_bridge, ADR-001 Этап 3)
- **Колокация:** VPS с прокси держать в регионе, близком к POP Mango (РФ), не US. Cross-region добавляет 60–200ms на каждый leg.
- **Кодек:** в baresip/SIP эмитить **ulaw_8000** (PSTN end-to-end 8kHz μ-law) — убирает транскодинг-шаг. Текущий план `auresamp 8k↔24k` для Яндекса ок, но на выходе к SIP — сразу 8k μ-law, без лишнего ресэмпла/encode.
- **Тёплый пул WS:** TLS handshake = 50–100ms на каждый новый коннект. Держать пул готовых соединений к Mango/Яндексу, не открывать с нуля на каждый звонок.
- **Стабильность RTP:** AEC (`echoCancellation`) обязателен, иначе эхо + повторные попытки добавляют джиттер.

### 3. Endpointing / VAD-тюнинг (если остаётся каскадный путь или server_vad)
- Silence threshold → **~300ms** вместо дефолтных 0.5–1.5s. Одна настройка = −200–400ms на turn, но риск срезать паузы → мерить interruption rate в проде.
- Barge-in: `speech_started` прерывает ответ (из ADR-001), `min_interruption_words: 2–3` чтобы шум не резал.

### 4. UX во время tool-call `save_lead` → CRM
- `save_lead` синхронно блокирует ответ на 200ms–2.4s (P95 из playbook). Пока идёт запись — проигрывать **filler-аудио** («Секунду, проверяю…») + можно spoken acknowledgment до вызова. Иначе >2s тишины = ощущение зависания.
- Предзагрузить аудио фразы на старте сессии (убирает ~240ms TTS TTFB на статичных репликах).

### 5. Greeting pre-buffer («assistant-speaks-first»)
- Приветствие синтезировать заранее (или сразу по коннекту), начать воспроизводить при установлении вызова — убирает первый RTT из perceived latency.

### 6. Two-tier model routing (опц.)
- Короткие классификационные turns («да/нет», подтверждение) гнать на меньшей модели; frontier-модель — только на сложные. Средний TTFT режет вдвое. Для Realtime — выбор между `yc` realtime-моделями по размеру.

## Что НЕ применимо (уже решает realtime-модель)
- Ручной стрим LLM-токенов в TTS по sentence boundaries.
- Speculative LLM по partial transcript (модель сама работает поверх потока аудио).
- Выбор отдельного STT/TTS провайдера — слито в realtime.

## Метрики (обязательно к замеру, ADR-001 Этап 5)
- Логировать timestamps на границах стадий в каждом turn: EOU → LLM TTFT → TTS TTFB → network egress.
- Отчитывать **p50 / p95 / p99** отдельно. p95 — то, что чувствует пользователь.
- Проверять cache hit rate системного промпта (цель ≥80% после прогрева).

## Риски
- **Динамика в начале промпта** ломает prefix caching → регресс TTFT.
- **Cross-region VPS** (если Mango POP далеко от сервера) → +100–200ms на leg.
- **Тёплый пул WS** требует управления жизненным циклом соединений (reconnect при обрыве).
- **Слишком агрессивный endpointing** режет паузы → растёт interruption rate.

## Критерии готовности
- [ ] System prompt byte-стабилен, динамика — в конце/в user-msg (prefix cache ≥80%).
- [ ] SIP-мост эмитит ulaw_8000, VPS колоцирован с Mango POP.
- [ ] Тёплый пул WS к Mango/Яндексу.
- [ ] VAD silence threshold ~300ms, barge-in по `speech_started`.
- [ ] Filler-аудио + greeting pre-buffer вокруг `save_lead`.
- [ ] Замеры p95 по стадиям: perceived latency < 500 мс.
