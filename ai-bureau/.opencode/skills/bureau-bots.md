# Паттерны создания AI-ботов для клиентов

## Smart Fallback — наш ключевой стандарт
См. `SMART_FALLBACK_STANDARD.md` — полная методология.
Когда скоринг LLM < 0.65:
1. **Reframing** — сужение контекста через наводящие вопросы
2. **Гибридный поиск** — semantic + keyword (точность +40%)
3. **Seamless Handoff** — перевод на менеджера с AI-выжимкой диалога

## Архитектура бота
```
User → Telegram/VK/Web API
         ↓
    Handler (polling/webhook)
         ↓
    Router (по командам/состояниям)
         ↓
    RAG → LLM (Gemini/GPT) → CRM
         ↓
    Response → User
```

## Best Practices
1. **Error Handling:** всегда оборачивать handler в try/except
2. **Rate Limiting:** не более 30 сообщений/сек в Telegram
3. **FSM:** для сложных диалогов и сбора данных
4. **Cost-Aware:** дешёвая модель для простых запросов, дорогая для сложных

## RAG (Retrieval-Augmented Generation) — быстрый старт

### Диагностика: 3 причины почему RAG не работает
1. **Чанки нарезаны бездумно** — рецепт не разрезан, заголовок таблицы в одном чанке, данные в другом. Фикс: `RecursiveCharacterTextSplitter` или нарезка по разделам.
2. **Поиск не находит нужное** — только векторный поиск теряет точные термины, только BM25 теряет смысл. Фикс: Hybrid (dense + sparse) + Re-ranking (cross-encoder).
3. **Качество не измеряется** — «вроде работает» на 5 вопросах. Фикс: eval dataset (50-100 пар) + RAGAS метрики (Faithfulness, Context Precision, Context Recall).

### Рекомендуемый стек (2026)
| Компонент | Рекомендация |
|-----------|-------------|
| VectorDB | Qdrant (self-hosted) |
| Embeddings (RU) | `deepvk/USER-bge-m3` |
| Hybrid | Dense + Sparse (SPLADE/BM42) |
| Re-ranker | `cross-encoder/ms-marco-MiniLM` |
| Оценка | RAGAS |

### Алгоритм «The Source of Truth»
```
Intent Classification → Query Enhancement (Multi-Query + HyDE)
→ Hybrid Search (Dense + Sparse → RRF) → Re-ranking (Cross-encoder)
→ Context Assembly (дедупликация, обрезка) → Generation с citation
→ Faithfulness Check (опционально)
```

### Anti-patterns
- ❌ Только векторный поиск → ✅ Hybrid (dense + sparse)
- ❌ Один запрос → один поиск → ✅ Multi-query (3 варианта)
- ❌ Нет overlap → ✅ overlap 15-20%
- ❌ Нет метрик → ✅ RAGAS на тестовом датасете
- ❌ LLM решает всё → ✅ Жёсткий промпт: «Только из контекста»
- ❌ LangChain чёрный ящик → ✅ Кастомный пайплайн с логами

---

## Интеграции
- Telegram Bot API (polling/webhook)
- VK API (через vk_api, User Token для загрузки фото)
- Bitrix24 CRM (webhook, REST API — см. Bitrix skill)
- Внешние API через httpx/axios

## Production Readiness
- Health check endpoint (`/health`)
- Нет hardcoded секретов (только env vars)
- Graceful error handling
- Логирование событий (без PII)
- Бот обязан отвечать на /start

## Структура bot-проекта
```
project/
├── bot/
│   ├── handler.py/ts    # Обработчик сообщений
│   ├── router.py/ts     # Маршрутизация
│   ├── fsm.py/ts        # Конечный автомат
│   └── keyboard.py/ts   # Клавиатуры
├── ai/
│   ├── rag.py/ts        # Retrieval-Augmented Generation
│   ├── llm.py/ts        # LLM клиент
│   └── prompts/         # Системные промпты
├── integrations/
│   └── crm.py/ts        # CRM клиент
└── config.py/ts         # Настройки из env
```
