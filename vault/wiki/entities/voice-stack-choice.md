---
type: wiki
tags: [voice-agents, telephony, vapi, mango, livekit, pipecat, levitan, cost]
status: done
updated: 2026-11-17
sources: [06-Library/tools/vapi-voice-ai/digest.md]
---

# Выбор голосового стека: Vapi против Mango + LiveKit + pipecat

Источник: `06-Library/tools/vapi-voice-ai/digest.md` (2026-09-23), статус диджеста `proposed`. Цифры вендора — заявления Vapi, независимо не проверялись.

## Что такое Vapi

Облачный оркестратор voice-агентов: единый SDK сводит telephony (Telnyx по умолчанию, импорт номеров Twilio/Plivo) + STT (Deepgram/Whisper/AssemblyAI/Gladia) + LLM (OpenAI/Anthropic/Gemini/Groq/Perplexity) + TTS (ElevenLabs/Azure/Cartesia/PlayHT). Агент собирается конфигуративно: media server, маршрутизация, мониторинг из коробки. Заявлено 2.5M+ агентов, 1B звонков, 99.9% uptime.

## Что даёт

- Serverless functions: webhook-логика внутри платформы (расписание, CRM) без своего VPS.
- Мониторинг: дашборд (latency, CSAT, транскрипт) плюс интеграция Langfuse.
- Guardrails: защита от галлюцинаций, фильтрация PII.
- Enterprise: SSO/OAuth/RBAC, SOC 2 / HIPAA / PCI, заявленная латентность <500 ms.
- CRM и автоматизация: HubSpot, Salesforce, Zendesk, Google Sheets, Notion, Zapier, Make, GoHighLevel.
- WebRTC SDK для браузера, iOS/Android SDK.

## Когда брать Vapi

Быстрый старт voice-проекта (запись в салон, лидогенерация, входящая поддержка); нужен мониторинг и отчётность «из коробки» для клиента; интеграции через Zapier/Make/CRM без кода; точечные проекты до ~1000 звонков в месяц.

## Когда оставить текущий стек

Для массового обзвона (100+ звонков в день), кастомной SIP-логики (baresip, DTMF, transfer, NAT), on-prem/РФ-размещения и жёсткого контроля media pipeline — оставить Mango + LiveKit + pipecat.

## Деньги

- Vapi: ~$0.08–0.12 за минуту (зависит от выбранных STT/TTS/LLM).
- Mango Office: ₽2–3 за минуту на мобильные РФ, примерно $0.02–0.03.
- Для массового обзвона Mango + OmniRoute дешевле в 3–5 раз.

## Риски

SaaS-only, данные идут через облако Vapi. Зависимость от Telnyx/Twilio (US): для РФ-номеров нужна магистраль. Цена непредсказуема при высоких объёмах (pay-per-call). Для ПД и 152-ФЗ — тот же вопрос, что в `elevenlabs-realtime`.

## Пример потока (салон красоты)

Входящий звонок → Vapi Telephony → STT Deepgram → LLM GPT-4o → serverless-функция проверяет расписание через Bitrix24 webhook → TTS ElevenLabs озвучивает подтверждение → запись в дашборде и callback в CRM.

## Статус в проекте

Levitan: Proposed (ADR-003 в самом дайджесте), к пилотированию на отдельном voice-проекте. Требуется аккаунт Vapi и пилот на записи в салон.

## Оговорка

Дайджест от 23.09.2026 не учитывает end-to-end STS-класс (см. `elevenlabs-realtime`, 25.10.2026). Вывод «для обзвона оставить как есть» перед следующим решением по AVM перечитывать вместе с ним.
