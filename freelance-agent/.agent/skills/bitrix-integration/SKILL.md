---
name: bitrix-integration
description: "Проектный скилл интеграции AI-агентов с Bitrix24. Используется для разработки голосовых агентов, webhook-обработчиков и автоматизации CRM. Применять при работе с Анжелочкой и Мариной."
metadata:
  level: project
  projects: [ai-eggs, ai-grant-consalt]
  version: 1.0.0
---

# Bitrix24 AI Integration Skill - [PROJECT]

> Источник: templates/ai-agent-implementation/BITRIX_AGENT_CHECKLIST.md
> Дата: 2026-04-30 | Конвертирован в проектный SKILL

## Когда активировать
- Настройка webhook от Bitrix24 (звонки, лиды, сделки)
- Разработка AI-обработчика звонков (Анжелочка)
- Интеграция бота с CRM Bitrix24
- Работа с REST API Bitrix24
- Настройка Open Lines / VoIP

---

## 🏗️ Архитектура AI + Bitrix24

### Проверенная схема (из успешного внедрения)
```
Звонок → Bitrix24 VoIP → Webhook → Python/Node.js Handler
    → Transcription (Whisper/FunASR) → LLM (Gemini Flash)
    → Обновление CRM (deal, contact) → Уведомление менеджеру
```

### Компоненты
| Компонент | Технология | Статус |
|-----------|-----------|--------|
| CRM | Bitrix24 (облако/коробка) | Production |
| Транскрибация | FunASR / Whisper | Trial |
| LLM | Gemini Flash (основной) | Production |
| Webhook handler | Python FastAPI | Production |
| Голос (TTS) | ElevenLabs / VoiceBox | Trial |
| Очередь | SQLite (без Redis!) | Production |

---

## 📋 Чеклист интеграции (из BITRIX_AGENT_CHECKLIST.md)

### Фаза 1: Настройка Bitrix24
- [ ] Создать приложение в Битрикс24 → OAuth (если облако) или system (коробка)
- [ ] Получить ACCESS_TOKEN и REFRESH_TOKEN
- [ ] Настроить webhook в CRM Events → `ONCRMDEALADD`, `ONCRMDEALUPDATE`
- [ ] Настроить webhook для звонков → `ONVOXIMPLANTCALLSTART`, `ONVOXIMPLANTCALLEND`
- [ ] Добавить исходящий Webhook URL → `https://your-server.ru/bitrix/webhook`
- [ ] Проверить доступность сервера из Битрикс24 (без CORS блокировки)

### Фаза 2: Обработчик Webhook
```python
# FastAPI обработчик (минимальный шаблон)
from fastapi import FastAPI, Request, BackgroundTasks
import hmac, hashlib

app = FastAPI()

@app.post("/bitrix/webhook")
async def handle_bitrix_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    data = await request.json()
    event = data.get("event", "")

    # Верификация подписи Bitrix24
    token = data.get("auth", {}).get("application_token", "")
    if not verify_bitrix_token(token):
        return {"status": "forbidden"}

    # Асинхронная обработка (быстрый ответ!)
    background_tasks.add_task(process_bitrix_event, event, data)
    return {"status": "ok"}  # Bitrix ждёт ответа < 5 секунд!
```

### Фаза 3: REST API Bitrix24
```python
import httpx

BITRIX_WEBHOOK_URL = "https://company.bitrix24.ru/rest/1/YOUR_TOKEN/"

async def update_deal(deal_id: int, fields: dict) -> dict:
    """Обновить сделку в CRM"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BITRIX_WEBHOOK_URL}crm.deal.update",
            json={"id": deal_id, "fields": fields}
        )
        return response.json()

async def add_comment(entity_id: int, text: str) -> dict:
    """Добавить комментарий к сделке"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BITRIX_WEBHOOK_URL}crm.timeline.comment.add",
            json={
                "fields": {
                    "ENTITY_ID": entity_id,
                    "ENTITY_TYPE": "deal",
                    "COMMENT": text,
                }
            }
        )
        return response.json()
```

### Фаза 4: Обработка звонков
```python
async def process_call_end(call_data: dict):
    """Обработка завершённого звонка"""
    call_id = call_data.get("CALL_ID")
    phone = call_data.get("PHONE_NUMBER")
    duration = call_data.get("CALL_DURATION", 0)

    # 1. Скачать запись звонка
    recording_url = await get_call_recording(call_id)

    # 2. Транскрибировать (FunASR лучше для русского!)
    transcript = await transcribe_audio(recording_url)

    # 3. Анализ через LLM
    analysis = await analyze_call(transcript, phone)

    # 4. Обновить CRM
    deal_id = await find_or_create_deal(phone)
    await update_deal(deal_id, {
        "UF_CRM_CALL_TRANSCRIPT": transcript,
        "UF_CRM_AI_SUMMARY": analysis["summary"],
        "UF_CRM_CALL_SENTIMENT": analysis["sentiment"],
    })
    await add_comment(deal_id, f"📞 AI Анализ звонка:\n{analysis['summary']}")
```

---

## 🔑 Метрики успешного внедрения (из чеклиста)

| Метрика | До AI | После AI |
|---------|--------|---------|
| Время обработки звонка | 15 мин (вручную) | 30 сек (авто) |
| Процент заполненных карточек | 40% | 95% |
| Время ответа на повторный звонок | 2+ часа | < 15 мин |
| Потери лидов (нет контакта в CRM) | 25% | 3% |

---

## ⚠️ Критические правила Bitrix24 API

1. **Лимиты запросов:** 2 запроса/секунду (иначе бан на 24 часа!)
   ```python
   import asyncio
   # Throttle между запросами
   await asyncio.sleep(0.6)  # максимум ~1.5 RPS
   ```

2. **Timeout webhook:** Bitrix ждёт ответа максимум 5 секунд
   - ВСЕГДА отвечать немедленно → обрабатывать асинхронно

3. **Token refresh:** ACCESS_TOKEN живёт 1 час
   ```python
   async def refresh_token():
       # Логика обновления через REFRESH_TOKEN
       ...
   ```

4. **Поля CRM:** Пользовательские поля начинаются с `UF_CRM_`
   - Создавать только нужные, не перегружать CRM

5. **Webhook верификация:** Всегда проверять `application_token`

---

## 🛡️ Безопасность Bitrix24 интеграции

- Хранить токены ТОЛЬКО в env vars (не в коде!)
- Webhook endpoint — за HTTPS (Let's Encrypt)
- IP whitelist Bitrix24 серверов если возможно
- Логировать все входящие события (для дебаггинга)
- Rate limiting на webhook endpoint (защита от флуда)

---

## 📁 Структура проекта (рекомендуемая)
```
project/
├── bitrix/
│   ├── webhook.py         # Обработчик webhook
│   ├── crm_client.py      # REST API клиент
│   ├── call_processor.py  # Обработка звонков
│   └── models.py          # Pydantic модели
├── ai/
│   ├── transcriber.py     # FunASR/Whisper
│   ├── analyzer.py        # Gemini Flash анализ
│   └── voice.py           # TTS (ElevenLabs)
└── config.py              # Настройки из env
```

---

## Constraints
- НИКОГДА не хранить Bitrix токены в коде
- Webhook отвечает < 5 секунд (все тяжёлые операции — async)
- Rate limit: максимум 1.5 запроса/секунду к API
- Тестировать на тестовом портале Bitrix24 до prod
- Логировать все события для отладки
