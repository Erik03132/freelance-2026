---
name: bot-development
description: Build AI bots with Smart Fallback, RAG pipeline, Telegram/VK/web integration. Hybrid search, re-ranking, evaluation. Production readiness.
---

## Smart Fallback — ключевой стандарт
Когда скоринг LLM < 0.65:
1. **Reframing** — сужение контекста через наводящие вопросы
2. **Гибридный поиск** — semantic + keyword (точность +40%)
3. **Seamless Handoff** — перевод на менеджера с AI-выжимкой диалога

## Архитектура бота
```
User → Handler (polling/webhook) → Router → RAG → LLM → CRM → Response
```

## RAG — быстрый старт

### 3 причины почему RAG не работает
1. **Чанки нарезаны бездумно** — Фикс: `RecursiveCharacterTextSplitter` или нарезка по разделам.
2. **Поиск не находит нужное** — Фикс: Hybrid (dense + sparse) + Re-ranking
3. **Качество не измеряется** — Фикс: eval dataset + RAGAS метрики

### Anti-patterns
- ❌ Только векторный поиск → ✅ Hybrid (dense + sparse)
- ❌ Один запрос → один поиск → ✅ Multi-query (3 варианта)
- ❌ Нет метрик → ✅ RAGAS
- ❌ LLM решает всё → ✅ Жёсткий промпт: «Только из контекста»

## Production Readiness
- Health check endpoint (`/health`)
- Нет hardcoded секретов (только env vars)
- Graceful error handling, логирование (без PII)
