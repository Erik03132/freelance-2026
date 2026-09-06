---
name: retell-conductor
description: "Быстрое прототипирование голосовых агентов через Retell AI Conductor. Для MVP и экспериментов. Для продакшна с большим объёмом — voice_bridge.py."
tools: [bash, read, write, edit, webfetch]
model: standard
source: "/Users/igorvasin/freelance-2026/foundation/skills/code/retell-conductor/SKILL.md"
---

# Retell Conductor — голосовые агенты (MVP)

## Когда использовать
✅ **Retell Conductor:** быстрое прототипирование (30 мин), клиентские MVP, эксперименты, малый объём (<50 звонков/день)
❌ **voice_bridge.py (свой стек):** продакшн (100+/день), кастомная логика, низкая стоимость

## Быстрый старт
1. Открой https://dashboard.retellai.com
2. Создай агента через Conductor — опиши на естественном языке
3. Conductor сгенерирует system prompt, function calls, тесты
4. Настрой параметры: response_readiness, interruption_sensitivity, voice

## Шаблоны агентов

### FAQ-бот
```yaml
prompt: |
  Ты — FAQ-бот компании {company_name}.
  Отвечай кратко (1-2 предложения) из базы знаний.
  Если вопрос не в базе — предложи связаться с менеджером.
functions: [search_faq, transfer_to_manager]
```

### Sales-ассистент
```yaml
prompt: |
  Ты — ассистент по продажам {company_name}.
  Узнай потребности, предложи товары, используй CRM.
functions: [lookup_customer, get_products, create_lead, transfer_to_sales]
```

### Support-агент
```yaml
prompt: |
  Ты — агент поддержки {company_name}.
  Диагностируй проблему, создай тикет при необходимости.
functions: [get_ticket_history, search_knowledge_base, create_ticket, transfer_to_specialist]
```

## Миграция Retell → voice_bridge.py
```python
# Экспорт из Retell → адаптация под свой стек
retell_config = {"system_prompt": "...", "functions": [...], "voice_settings": {...}}
# system prompt → angela_response() в voice_bridge.py
# function calls → кастомные функции (CRM lookup, FAQ cache)
# voice settings → voice_engine.py (Gemini Kore / edge-tts)
```