# ADR-003: Vapi AI как voice-стек для новых агентов

**Статус:** Proposed (к пилотированию)
**Дата:** 2026-09-23
**Контекст:** Расширение voice-стека проекта Levitan

---

## Контекст

Текущий стек Levitan для обзвона:
- **Telephony:** Mango Office (callback API)
- **Media/SIP:** LiveKit + pipecat-agent (self-hosted на VPS)
- **STT:** Whisper (локальный) / Mango S2T
- **LLM:** DeepSeek / Gemini / Qwen (через OmniRoute)
- **TTS:** Azure / ElevenLabs (greeting_monologue.wav — предзаписанный)
- **Оркестрация:** pipecat-agent + FastAPI webhook + guarded_run

Для новых голосовых проектов (запись в салоны, лидогенерация, входящая поддержка) нужна альтернатива быстрее в запуске, чем сборка pipecat+LiveKit+Mango с нуля.

## Решение

Использовать **Vapi AI** как voice-оркестратор для новых voice-проектов, оставив текущий Mango+LiveKit+pipecat стек для Levitan-обзвона.

### Маппинг на стек Vapi vs текущий:

| Компонент | Текущий (Levitan) | Vapi |
|-----------|-------------------|------|
| Telephony | Mango callback API | Встроенный (Telnyx/Twilio/Plivo) |
| Media | LiveKit self-hosted | Встроенный WebRTC/SIP |
| STT | Whisper локальный | Deepgram / Whisper / Gladia / AssemblyAI |
| LLM | DeepSeek/Gemini через OmniRoute | OpenAI / Anthropic / Gemini / Groq (нативно) |
| TTS | Azure / ElevenLabs / pre-recorded | ElevenLabs / Azure / Cartesia / PlayHT |
| Оркестрация | pipecat-agent + FastAPI | Vapi Cloud (serverless functions) |
| Мониторинг | journalctl + custom | Встроенный дашборм + Langfuse |
| Webhook/CRM | FastAPI на VPS | Serverless functions / Zapier / native integrations |

### Когда использовать Vapi:

✅ **Vapi предпочтителен:**
- Новые voice-проекты с коротким time-to-market (салоны, запись, лидогенерация)
- Проекты, где нужен enterprise-мониторинг из коробки
- Входящие звонки с расписанием (Google Calendar, запись)
- Клиенты, которым нужна отчётность по звонкам «из коробки»
- Интеграция через Zapier/Make/HubSpot/Salesforce без написания кода

❌ **Оставить Mango+LiveKit+pipecat (текущий):**
- Массовые обзвонные кампании (100+ звонков/день) — критична стоимость за звонок
- Проекты, где нужен полный контроль над media pipeline
- Сценарии с кастомной SIP-логикой (baresip, DTMF, transfer)
- Проекты с жёсткими требованиями к размещению (on-prem, РФ-сервер)
- Уже работающий Levitan (миграция нецелесообразна)

## Пример использования

Голосовой агент для записи в салон красоты:
1. Входящий звонок → Vapi (Telephony)
2. STT (Deepgram) → LLM (GPT-4o) → TTS (ElevenLabs)
3. LLM проверяет расписание через serverless function → Bitrix24 webhook
4. Подтверждает запись голосом клиенту
5. Мониторинг в Vapi Dashboard + callback в CRM

## Финансы

- **Vapi:** pay-per-call (~$0.08-0.12/мин за STT+TTS+LLM в зависимости от провайдеров)
- **Текущий стек:** Mango (₽2-3/мин за мобильные) + VPS + STT/LLM (OmniRoute free/cheap)
- Для массового обзвона текущий стек дешевле
- Для точечных voice-проектов Vapi оправдан скоростью запуска

## Статус

**Proposed.** Требуется:
1. Зарегистрировать Vapi-аккаунт (dashboard.vapi.ai)
2. Спилотный проект: voice-агент для одной целевой ниши (запись в салон/клинику)
3. Сравнить latency, CSAT, стоимость/звонок с текущим стеком
4. Решение: Accepted / Deprecated / Adjusted

## Ссылки

- Vapi AI: https://vapi.ai
- SDK (web): https://github.com/VapiAI/client-sdk-web
- Docs: https://docs.vapi.ai
- Integrations: OpenAI, Anthropic, ElevenLabs, Deepgram, Twilio, Zapier, HubSpot, Salesforce
