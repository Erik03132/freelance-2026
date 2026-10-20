---
type: tool-source
tags: [voice-agent, telephony, stt, llm, tts, orchestration, saas, bitrix24, zapier, enterprise]
status: proposed
updated: 2026-09-23
---

# Vapi AI — полный разбор (source)

**Источник:** https://vapi.ai (оффсайт), https://docs.vapi.ai (документация), https://github.com/VapiAI/client-sdk-web (SDK)
**Дата верификации:** 2026-09-23

---

## 1. Архитектура Vapi

Vapi — это managed voice orchestration layer. Клиент (браузер/телефон) подключается через WebRTC/SIP к Vapi Cloud, где:

```
[Телефон/Telnyx] ←→ [Vapi Cloud: Telephony Gateway]
                            ↓
                       [Media Server: WebRTC/SIP mixing]
                            ↓
                       [Pipeline: STT → LLM → TTS]
                            ↓
                  [Serverless functions: webhooks, CRM]
                            ↓
                  [Monitoring: Dashboard + Langfuse]
```

Всё managed — не нужно поднимать LiveKit/SFU/свой media server.

### 1.1. Pipeline
1. **Input:** аудио от клиента (WebRTC или PSTN через Telnyx/Twilio)
2. **STT:** Deepgram (по умолчанию) / Whisper / AssemblyAI / Gladia
3. **LLM:** GPT-4o, Claude Sonnet, Gemini, Groq, Perplexity, Mistral
4. **TTS:** ElevenLabs, Azure, Cartesia, PlayHT, OpenAI
5. **Output:** аудио обратно клиенту

### 1.2. Telephony
- **По умолчанию:** Telnyx (US/CA номера, международные)
- **Импорт:** Twilio, Plivo, Vonage — можно привести свой номер
- **Исходящие/входящие:** оба поддерживаются
- **SIP:** подключение своего SIP-сервера (гибридный режим)

### 1.3. Serverless functions
Внутри платформы можно писать функции (TypeScript), которые:
- Вызываются на триггеры (начало звонка, после STT, после LLM)
- Могут ходить в любой webhook (Bitrix24, REST API)
- Возвращают данные в контекст LLM

---

## 2. Интеграции (полный список)

### LLM
- OpenAI (GPT-4o, GPT-4o-mini)
- Anthropic (Claude Sonnet, Opus, Haiku)
- Google (Gemini)
- Groq (Llama, Mistral — быстрый)
- Perplexity (с поиском)
- Cohere, Together AI, Fireworks

### STT
- Deepgram (по умолчанию, Nova-2)
- OpenAI Whisper
- AssemblyAI
- Gladia
- Azure Speech

### TTS
- ElevenLabs (основной)
- Azure Speech
- Cartesia (Sonic)
- PlayHT
- OpenAI TTS

### Telephony
- Telnyx (default)
- Twilio
- Plivo
- Vonage
- SIP trunking

### CRM / Productivity
- HubSpot, Salesforce, Zendesk
- Google Calendar, Google Sheets
- Notion, Airtable
- Zapier, Make
- GoHighLevel, Five9, Genesys, Avaya
- Slack, Apollo.io, Clay
- AWS S3, GCP Cloud (для хранения записей)

### Observability
- Langfuse (трейсинг LLM-вызовов)
- Встроенный Dashboard (calls, latency, CSAT, transcripts)

---

## 3. Pricing (на 2026-09-23)

### Тарифы
- **Pay-as-you-go:** ~$0.10/мин (STT ~$0.023 + TTS ~$0.20/мин × доля + LLM ~$0.003-0.01/звонок)
- **Startup:** $0.08/мин при объёме
- **Enterprise:** индивидуальный (SLA, reserved capacity)

### Пример стоимости 1 звонка (3 мин):
- STT: 3 мин × $0.023 = $0.069
- TTS: ~1.5 мин речи × $0.20 = $0.30
- LLM: ~3 запроса × $0.003 = $0.01
- Telephony (Telnyx US): ~$0.01/мин × 3 = $0.03
- **Итого:** ~$0.41/звонок (≈ ₽37)

### Сравнение с Mango Office:
- **Mango (РФ мобильные):** ₽2-3/мин × 3 мин = ₽6-9/звонок
- **Vapi:** ~₽37/звонок (в 4-6× дороже, но включает STT+LLM+TTS)

---

## 4. Сравнение с текущим стеком Levitan

| Компонент | Текущий (Levitan) | Vapi |
|-----------|-------------------|------|
| Telephony | Mango callback API (РФ, дешёвый) | Telnyx/Twilio (глобальный) |
| Media server | LiveKit self-hosted на VPS | Managed (Vapi Cloud) |
| STT | Whisper локальный / Mango S2T | Deepgram/Whisper managed |
| LLM | DeepSeek/Gemini через OmniRoute (free/cheap) | GPT-4o/Claude/Gemini (market rate) |
| TTS | ElevenLabs/Azure или pre-recorded WAV | ElevenLabs/Azure/Cartesia managed |
| Оркестрация | pipecat-agent + FastAPI (свой код) | Vapi config (низкий код) |
| Webhook/CRM | FastAPI на VPS + python-telegram-bot | Serverless fn + Zapier/HubSpot native |
| Мониторинг | journalctl + custom scripts | Dashboard + Langfuse |
| Размещение | VPS в РФ | US/EU cloud |

### Ключевой вывод
Vapi не заменяет текущий стек для массового обзвона Levitan (слишком дорого).
Vapi = инструмент для **новых voice-проектов** где нужна скорость и enterprise-фичи.

---

## 5. Enterprise-фичи

- **SLA:** 99.9% uptime контракт
- **Security:** SOC 2 Type II, HIPAA, PCI DSS
- **Access:** SSO (SAML/OIDC), OAuth2, RBAC
- **AI Guardrails:** защита от галлюцинаций, PII masking, content filtering
- **Scalability:** до millions звонков, sub-500ms latency
- **Support:** dedicated engineer (enterprise)

---

## 6. Примеры использования (из кейсов Vapi)

### Amazon Ring (поддержка)
- 0 → production за 2 недели
- 100% inbound volume через Vapi
- CSAT вырос

### Kavak (латиноамериканский автобиржевой)
- 2× больше клиентов при том же CSAT
- Прибыльность в Мексике за счёт автоматизации

### GoHealth (здравоохранение)
- 250K звонков/мес
- 5× revenue growth

### Instawork (маркетплейс подработки)
- 1M+ звонков/мес
- Десятки use cases

---

## 7. Когда НЕ использовать Vapi

1. Массовые обзвонные кампании (100+/день) — экономика не сходится
2. Жёсткие on-prem требования (данные не должны покидать периметр)
3. Кастомная SIP-логика (baresip, DTMF, transfer, fax)
4. РФ-размещение (Vapi не имеет дата-центров в РФ → проблема с персональными данными по 152-ФЗ)
5. Проекты с предсказуемым budget — pay-per-call непредсказуем

---

## 8. Статус в проекте

**Proposed (ADR-003).** Пилот не начат.

Следующие шаги:
1. Зарегистрировать Vapi-аккаунт (dashboard.vapi.ai)
2. Спилотный проект: voice-агент для записи в салон/клинику
3. Сравнить с текущим стеком (latency, CSAT, cost/call)
4. Решение: Accepted / Deprecated / Adjusted

---

## 9. Ссылки

- Офсайт: https://vapi.ai
- Документация: https://docs.vapi.ai
- SDK (web): https://github.com/VapiAI/client-sdk-web
- Pricing: https://vapi.ai/pricing
- Security: https://security.vapi.ai
- Customers: https://vapi.ai/customers
- Community: https://vapi.ai/community
- Vapicon 2026 (конференция): https://www.vapicon.ai/
