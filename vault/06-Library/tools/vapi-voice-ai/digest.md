---
type: tool-digest
tags: [voice-agent, telephony, stt, llm, tts, orchestration, saas, bitrix24, zapier, enterprise]
status: proposed
updated: 2026-09-23
---

# Vapi AI — developer-first оркестратор голосовых AI-агентов

**Сайт:** https://vapi.ai | **Документация:** https://docs.vapi.ai | **SDK:** https://github.com/VapiAI/client-sdk-web (68★)
**Лицензия:** SaaS (pay-per-call + подписка). **Статус:** 2.5M+ agents, 1B calls, 99.9% uptime.

## Что это
Облачный оркестратор voice-агентов. Единый SDK объединяет telephony (Telnyx/Twilio/Plivo) + STT (Deepgram/Whisper/AssemblyAI/Gladia) + LLM (OpenAI/Anthropic/Gemini/Groq/Perplexity) + TTS (ElevenLabs/Azure/Cartesia/PlayHT). Агенты собираются конфигуративно — media server, маршрутизация, мониторинг из коробки.

## Ключевые фичи
- **Telephony:** встроенный провайдер (Telnyx по умолчанию) + импорт номеров из Twilio/Plivo
- **Serverless functions:** webhook-логика внутри платформы (проверка расписания, CRM) — без своего VPS
- **Мониторинг:** встроенный дашборд (latency, CSAT, transcript) + Langfuse интеграция
- **AI Guardrails:** защита от галлюцинаций, фильтрация PII
- **Enterprise:** SSO/OAuth/RBAC, SOC 2 / HIPAA / PCI compliant, <500ms latency
- **CRM:** HubSpot, Salesforce, Zendesk, Google Sheets, Notion, Zapier, Make, GoHighLevel
- **Web/мобиль:** WebRTC SDK (браузер), iOS/Android SDK

## Когда использовать (маппинг на стек)
**✅ Vapi предпочтителен:**
- Быстрый старт voice-проекта (запись в салон, лидогенерация, входящая поддержка)
- Нужен мониторинг/отчётность «из коробки» для клиента
- Интеграция через Zapier/Make/HubSpot/Salesforce без кода
- Точечные voice-проекты (< 1000 звонков/мес)

**❌ Оставить текущий стек (Mango + LiveKit + pipecat):**
- Массовый обзвон (100+ звонков/день) — критична стоимость/звонок
- Кастомная SIP-логика (baresip, DTMF, transfer, NAT)
- On-prem / РФ-размещение
- Жёсткий контроль над media pipeline

## Финансы
- **Vapi:** ~$0.08–0.12/мин (STT+TTS+LLM зависит от провайдеров)
- **Mango Office:** ₽2–3/мин за мобильные РФ (≈ $0.02–0.03/мин)
- Для массового обзвона Mango+OmniRoute дешевле в 3–5×

## Пример: запись в салон красоты
```
Входящий звонок → Vapi Telephony → STT (Deepgram) → LLM (GPT-4o)
→ Serverless fn: проверить расписание через Bitrix24 webhook
→ TTS (ElevenLabs) озвучить подтверждение
→ Запись в дашборде + callback в CRM
```

## Статус в проекте
- **Levitan:** Proposed (ADR-003) — к пилотированию на отдельном voice-проекте
- Требуется: регистрация Vapi-аккаунта + спилотить запись в салон

## Ограничения
- SaaS-only (no on-prem) — данные ходят через облако Vapi
- Зависимость от Telnyx/Twilio (US-провайдеры) — для РФ номеров нужна магистраля
- Cost непредсказуем при высоких объёсах (pay-per-call)

**См. также:** [[ADR-003-vapi-voice-stack]] (Levitan)
