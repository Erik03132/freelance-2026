# Open Source Real-Time Voice Agent Solutions

> Дата: 06.07.2026
> Статус: Сохранено для последующего рассмотрения
> Проект: ai-levitan (Фаза 5: Real-time AI Voice Agent)

---

## 🏆 Топ решения (по звёздам GitHub)

### 1. Pipecat (13.3k ⭐) — Рекомендуется
> https://github.com/pipecat-ai/pipecat

**Что это:** Open-source Python фреймворк для real-time голосовых и мультимодальных агентов.

**Ключевые особенности:**
- Voice-first архитектура
- 30+ интеграций STT/LLM/TTS
- Multi-agent поддержка (handoff, fan-out, sidecar)
- WebRTC и WebSocket транспорт
- MCP поддержка
- Встроенный CLI для деплоя

**Поддерживаемые сервисы:**
| Категория | Сервисы |
|-----------|---------|
| **STT** | Deepgram, Whisper, Google, Azure, xAI, Groq |
| **LLM** | OpenAI, Anthropic, Gemini, Grok, DeepSeek, Ollama |
| **TTS** | ElevenLabs, Cartesia, OpenAI, xAI, Google, Azure |
| **S2S** | OpenAI Realtime, Gemini Live, Grok Voice, Ultravox |
| **Транспорт** | Daily (WebRTC), LiveKit, FastAPI, Twilio, Telnyx |

**Пример кода:**
```python
from pipecat.pipeline.pipeline import Pipeline
from pipecat.services.deepgram import DeepgramSTTService
from pipecat.services.openai import OpenAILLMService
from pipecat.services.cartesia import CartesiaTTSService

# Минимальный voice agent
stt = DeepgramSTTService(model="nova-3")
llm = OpenAILLMService(model="gpt-4.1-mini")
tts = CartesiaTTSService(model="sonic-3")

pipeline = Pipeline([stt, llm, tts])
```

**Оценка для ai-levitan:** ⭐⭐⭐⭐⭐
- ✅ Python (наш стек)
- ✅ Поддержка DeepSeek (наш LLM)
- ✅ Поддержка Mango (через Twilio/Telnyx сериализаторы)
- ✅ Sub-second латентность
- ✅ Активное развитие (10,647 коммитов)

---

### 2. LiveKit Agents (11.3k ⭐)
> https://github.com/livekit/agents

**Что это:** Фреймворк для построения real-time голосовых AI агентов с WebRTC.

**Ключевые особенности:**
- Semantic turn detection (transformer model)
- MCP поддержка
- Multi-agent handoff
- Телефонная интеграция (SIP)
- Встроенные тесты

**Пример кода:**
```python
from livekit.agents import Agent, AgentSession, JobContext

@server.rtc_session()
async def entrypoint(ctx: JobContext):
    session = AgentSession(
        stt=inference.STT("deepgram/nova-3"),
        llm=inference.LLM("openai/gpt-4.1-mini"),
        tts=inference.TTS("cartesia/sonic-3"),
    )
    agent = Agent(instructions="Ты менеджер по продажам зерна.")
    await session.start(agent=agent, room=ctx.room)
```

**Оценка для ai-levitan:** ⭐⭐⭐⭐
- ✅ Отличная WebRTC поддержка
- ✅ SIP интеграция для телефонии
- ✅ Semantic turn detection
- ⚠️ Требует LiveKit сервер
- ⚠️ Меньше плагинов чем Pipecat

---

### 3. Patter (931 ⭐) — Vapi/Retell Alternative
> https://github.com/PatterAI/Patter

**Что это:** Open-source voice-AI SDK для создания телефонных агентов.

**Ключевые особенности:**
- Дай номер телефона за 4 строки кода
- Python и TypeScript
- MIT лицензия
- Twilio, Telnyx, Plivo поддержка

**Оценка для ai-levitan:** ⭐⭐⭐
- ✅ Простота использования
- ✅ Телефония из коробки
- ⚠️ Меньше возможностей чем Pipecat
- ⚠️ Молодой проект

---

### 4. Feros (100 ⭐) — Rust Voice Agent OS
> https://github.com/ferosai/feros

**Что это:** Open-source voice agent OS на Rust с sub-second латентностью.

**Ключевые особенности:**
- Rust runtime (максимальная производительность)
- AI-driven builder
- Self-hosted
- Sub-second латентность

**Оценка для ai-levitan:** ⭐⭐⭐
- ✅ Максимальная производительность
- ✅ Self-hosted
- ⚠️ Rust (не наш стек)
- ⚠️ Мало документации

---

### 5. TEN VAD (2.2k ⭐) — Voice Activity Detection
> https://github.com/TEN-framework/ten-vad

**Что это:** Low-latency, high-performance Voice Activity Detector.

**Ключевые особенности:**
- Low-latency VAD
- Lightweight (<1MB)
- C implementation
- Для real-time голосовых агентов

**Оценка для ai-levitan:** ⭐⭐⭐⭐
- ✅ Можно использовать вместо Silero VAD
- ✅ Low-latency
- ✅ Lightweight

---

### 6. CyberVerse (1.4k ⭐) — Digital Human Platform
> https://github.com/Lynpoint/CyberVerse

**Что это:** Self-hosted real-time digital human agent platform.

**Ключевые особенности:**
- WebRTC
- Persona memory
- RAG
- Digital-human video
- Lip-sync

**Оценка для ai-levitan:** ⭐⭐
- ✅ Если нужен цифровой аватар
- ⚠️ Избыточно для телефонии

---

### 7. axiom-voice-agent (135 ⭐) — Offline Voice Agent
> https://github.com/pheonix-delta/axiom-voice-agent

**Что это:** <400ms latency voice agent, полностью offline, 4GB VRAM.

**Ключевые особенности:**
- <400ms латентность
- Полностью offline (без API)
- 4GB VRAM
- Apache 2.0

**Оценка для ai-levitan:** ⭐⭐⭐
- ✅ Offline работа (без интернета)
- ✅ Low-latency
- ⚠️ Требует GPU
- ⚠️ Мало документации

---

## 📊 Сравнительная таблица

| Решение | ⭐ | Язык | STT | LLM | TTS | Телефония | Латентность | Сложность |
|---------|-----|------|-----|-----|-----|-----------|-------------|-----------|
| **Pipecat** | 13.3k | Python | ✅30+ | ✅20+ | ✅30+ | ✅Twilio/Telnyx | <500мс | Средняя |
| **LiveKit** | 11.3k | Python | ✅ | ✅ | ✅ | ✅SIP | <500мс | Средняя |
| **Patter** | 931 | Python | ✅ | ✅ | ✅ | ✅Twilio/Telnyx | <500мс | Низкая |
| **Feros** | 100 | Rust | ✅ | ✅ | ✅ | ✅ | <200мс | Высокая |
| **TEN VAD** | 2.2k | C | ✅VAD | — | — | — | <50мс | Низкая |
| **xAI Builder** | — | No-code | ✅ | ✅Grok | ✅ | ✅Номер | <1сек | Нулевая |

---

## 🎯 Рекомендации для ai-levitan

### Текущий стек
```
Mango callback → Zoiper → faster-whisper → DeepSeek → edge-tts → CRM
```

### Вариант A: Миграция на Pipecat (рекомендуется)
```
Mango callback → LiveKit/SIP → Pipecat Pipeline → CRM

Pipeline:
  STT: Deepgram (nova-3) или faster-whisper (local)
  LLM: DeepSeek Chat V3 (OpenRouter)
  TTS: edge-tts (local) или ElevenLabs
```

**Почему Pipecat:**
- Python (наш стек)
- Поддержка DeepSeek (наш LLM)
- Поддержка edge-tts (наш TTS)
- MCP для интеграции с CRM
- Sub-second латентность
- Активное развитие

### Вариант B: Улучшение текущего пайплайна
```
Текущий пайплайн + улучшения:
1. Заменить Silero VAD на TEN VAD (low-latency)
2. Добавить edge-tts streaming (параллельная генерация)
3. Добавить DeepSeek streaming (параллельная генерация)
```

### Вариант C: Гибрид
```
Текущий пайплайн для mass outgoing
+ Pipecat для incoming hotline
+ xAI Voice Agent для premium клиентов
```

---

## 🔧 Компоненты для улучшения текущего пайплайна

### 1. TEN VAD (замена Silero VAD)
```bash
pip install ten-vad
```
**Преимущества:**
- Low-latency (<50мс)
- Lightweight (<1MB)
- C implementation (быстрее Python)

### 2. Pipecat Streaming Pipeline
```python
# Параллельная обработка
async def streaming_pipeline(audio_stream):
    # STT (параллельно с TTS предыдущего ответа)
    stt_task = asyncio.create_task(stt.transcribe(audio_stream))
    
    # LLM (параллельно с TTS)
    llm_task = asyncio.create_task(llm.generate(stt_result))
    
    # TTS (стриминг)
    async for chunk in tts.stream(llm_result):
        yield chunk
```

### 3. MCP для CRM интеграции
```python
# Автоматическая запись в CRM
@mcp_tool
async def save_lead(culture: str, volume: str, region: str, phone: str):
    """Сохранить лид в CRM"""
    await crm.create_lead({
        "culture": culture,
        "volume": volume,
        "region": region,
        "phone": phone
    })
```

---

## 📋 План рассмотрения

### Неделя 1: Исследование
- [ ] Установить Pipecat локально
- [ ] Запустить пример basic_agent.py
- [ ] Оценить латентность с DeepSeek
- [ ] Проверить интеграцию с Mango (через SIP)

### Неделя 2: Прототип
- [ ] Создать прототип voice agent на Pipecat
- [ ] Подключить DeepSeek + edge-tts
- [ ] Протестировать на 10 звонках
- [ ] Сравнить с текущим пайплайном

### Неделя 3: Решение
- [ ] Аналитика: латентность, стоимость, качество
- [ ] Решение: миграция на Pipecat или улучшение текущего
- [ ] Документирование результатов

---

## 💰 Оценка стоимости

| Вариант | Стоимость/звонок | Латентность | Сложность |
|---------|------------------|-------------|-----------|
| Текущий пайплайн | ~$0.01 | 2-5 сек | — |
| Pipecat (DeepSeek) | ~$0.02 | <1 сек | Средняя |
| Pipecat (OpenAI) | ~$0.15 | <500 мс | Средняя |
| xAI Voice Agent | ~$0.25 | <1 сек | Низкая |
| Offline (axiom) | ~$0 | <400 мс | Высокая |

---

## 📝 Заключение

**Рекомендация:** Рассмотреть **Pipecat** как основной фреймворк для Фазы 5.

**Причины:**
1. Python (наш стек)
2. Поддержка DeepSeek (наш LLM)
3. 30+ интеграций STT/LLM/TTS
4. Sub-second латентность
5. Активное развитие (13.3k ⭐)
6. MCP для CRM интеграции

**Следующий шаг:** Установить Pipecat и запустить basic_agent.py.
