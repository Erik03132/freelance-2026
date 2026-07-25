---
name: retell-conductor
description: Быстрое прототипирование голосовых агентов через Retell AI Conductor. Использовать для MVP и экспериментов. Для продакшна с большим объёмом — voice_bridge.py.
---

## Когда использовать

✅ **Используй Retell Conductor:**
- Быстрое прототипирование (30 минут вместо 2 дней)
- Клиентские MVP для ai-bureau
- Тестирование новых сценариев
- Обучение и эксперименты
- Малый объём (<50 звонков/день)

❌ **Используй voice_bridge.py (текущий стек):**
- Продакшн Анжелочки (100+ звонков/день)
- Нужна кастомная логика (FAQ cache, CRM, каскад TTS)
- Важна низкая стоимость ($0.10 vs $0.50 за звонок)
- Требуется полный контроль над STT/TTS/LLM

## Сравнение подходов

| Критерий | voice_bridge.py | Retell Conductor |
|----------|-----------------|------------------|
| **Стоимость звонка** | $0.10-0.50 | $0.25-0.75 |
| **Время создания** | 2-3 дня | 30 минут |
| **Контроль** | 100% | 30% |
| **Гибкость** | Высокая | Средняя |
| **Качество TTS** | Gemini Kore (отлично) | Retell TTS (хорошо) |
| **Качество STT** | faster-whisper (отлично) | Retell STT (хорошо) |
| **Тестирование** | Ручное | UI с тестами |
| **Vendor lock-in** | Нет | Да |

## Быстрый старт с Retell Conductor

### 1. Создание агента

```bash
# Открой Retell AI Dashboard
# https://dashboard.retellai.com

# Создай новый агент через Conductor
# Опиши на естественном языке:
"""
Ты — голосовой ассистент компании ВезёмЦыплят.
Отвечай на вопросы о породах птиц, ценах, доставке.
Если не знаешь ответ — предложи связаться с менеджером.
"""
```

### 2. Генерация промптов

Conductor автоматически генерирует:
- System prompt
- Function calls (CRM lookup, FAQ search)
- Test scenarios

### 3. Настройка параметров

```yaml
# В UI Retell Conductor
response_readiness: 0.7        # Готовность к ответу (0-1)
interruption_sensitivity: 0.5  # Чувствительность к прерываниям (0-1)
voice: "female_1"              # Голос агента
language: "ru"                 # Язык
```

### 4. Тестирование

```bash
# В UI Retell Conductor
# 1. Запусти тестовый звонок
# 2. Проверь сценарии:
#    - Приветствие
#    - Вопрос о ценах
#    - Вопрос о доставке
#    - Просьба связаться с менеджером
# 3. Посмотри transcript и метрики
```

## Шаблоны агентов

### FAQ-бот (простой)

```yaml
name: FAQ Bot
description: Отвечает на частые вопросы
prompt: |
  Ты — FAQ-бот компании {company_name}.
  Отвечай кратко (1-2 предложения) на вопросы из базы знаний.
  Если вопрос не в базе — предложи связаться с менеджером.

functions:
  - search_faq(question: str) -> str
  - transfer_to_manager() -> void

voice: female_1
language: ru
```

### Sales-ассистент (средний)

```yaml
name: Sales Assistant
description: Помогает с продажами
prompt: |
  Ты — ассистент по продажам {company_name}.
  Узнай потребности клиента, предложи подходящие товары.
  Используй CRM для персонализации.

functions:
  - lookup_customer(phone: str) -> Customer
  - get_products(category: str) -> Product[]
  - create_lead(name: str, phone: str, interest: str) -> Lead
  - transfer_to_sales() -> void

voice: male_1
language: ru
response_readiness: 0.8
```

### Support-агент (сложный)

```yaml
name: Support Agent
description: Техническая поддержка
prompt: |
  Ты — агент поддержки {company_name}.
  Диагностируй проблему, предложи решения.
  Если не можешь помочь — создай тикет и передай специалисту.

functions:
  - get_ticket_history(customer_id: str) -> Ticket[]
  - search_knowledge_base(query: str) -> Article[]
  - create_ticket(customer_id: str, issue: str, priority: str) -> Ticket
  - transfer_to_specialist(ticket_id: str) -> void

voice: female_2
language: ru
interruption_sensitivity: 0.3
```

## Миграция: Retell → voice_bridge.py

Если прототип на Retell заходит → мигрируй на свой стек:

### 1. Экспорт конфигурации

```python
# Из Retell Conductor экспортируй:
retell_config = {
    "system_prompt": "...",
    "functions": [...],
    "voice_settings": {...},
    "test_scenarios": [...]
}
```

### 2. Адаптация под voice_bridge.py

```python
# 1. System prompt → angela_response() в voice_bridge.py
def angela_response(transcript: str, crm: dict | None = None, context: str = "") -> str:
    prompt = retell_config["system_prompt"] + f"\n\nКлиент: {transcript}"
    # ... вызов LLM

# 2. Functions → кастомные функции
def lookup_customer(phone: str) -> dict | None:
    # Bitrix24 CRM lookup
    return find_contact(phone)

def search_faq(question: str) -> str | None:
    # FAQ cache search
    return lookup_faq(question)

# 3. Voice settings → voice_engine.py
# Retell voice: female_1 → Gemini Kore / edge-tts Светлана
```

### 3. Тестирование

```bash
# Запусти тестовые сценарии из Retell
python test_voice_call.py --scenarios retell_test_scenarios.json
```

## Best Practices

✅ **Делай:**
- Используй Retell для быстрого MVP (30 минут)
- Тестируй все сценарии в UI перед продакшном
- Экспортируй конфигурацию для миграции на свой стек
- Сравнивай стоимость: Retell vs свой стек

❌ **Не делай:**
- Не используй Retell для 100+ звонков/день (дорого)
- Не полагайся на Retell для критичной логики (FAQ cache, CRM)
- Не забывай про vendor lock-in

## Интеграция с foundation

### Структура

```
foundation/skills/code/retell-conductor/
├── SKILL.md (этот файл)
└── templates/
    ├── faq-bot.yaml
    ├── sales-assistant.yaml
    └── support-agent.yaml
```

### Использование в проектах

```bash
# Скопируй шаблон в проект
cp foundation/skills/code/retell-conductor/templates/faq-bot.yaml \
   projects/ai-bureau/config/retell-agents/

# Настрой под клиента
# Открой в Retell Conductor
# Протестируй
```

## Troubleshooting

**Retell слишком дорогой:**
- Мигрируй на voice_bridge.py
- Используй для малых объёмов (<50 звонков/день)

**Не хватает контроля:**
- Добавь кастомную логику в voice_bridge.py
- Используй FAQ cache, CRM интеграцию

**Нужна кастомная TTS:**
- Используй voice_engine.py (Gemini Kore, edge-tts, Silero)
- Retell TTS не кастомизируется

## Ресурсы

- [Retell AI Dashboard](https://dashboard.retellai.com)
- [Retell Conductor Docs](https://docs.retellai.com/conductor)
- Пример: `projects/ai-eggs/agent/voice_bridge.py` (свой стек)
- Шаблоны: `foundation/skills/code/retell-conductor/templates/`
