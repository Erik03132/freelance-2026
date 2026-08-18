# ADR-004 — Local-first RAG Reference Architecture

- **Статус:** Принято (2026-08-14, источник Habr #1070662, секция RAG-3 в ACTIVE_TASKS.md)
- **Контекст:** Урок «RAG с нуля» (bi-encoder → cross-encoder reranker → генерация).
- **Решение:** Зафиксировать **local-first RAG** как эталонную архитектуру ретривала в стеке.

## Принципы (приняты)
1. **Ретривал = bi-encoder (top_k_retrieve 30-50) → cross-encoder rerank → top_k_final 3-5.**
   Реализовано в `tools/rag_retrieval.py` (`rag_retrieve` + `rerank`).
2. **Асимметричные префиксы эмбеддинга** `search_query:` / `search_document:`
   (`embed_query`/`embed_document`).
3. **Local-first inference** — эмбеддинг/rerank/генерация по умолчанию локально
   (приватность внутренних доков, см. ADR-002).

## Модельный выбор (рекомендация, НЕ догма)
- **bi-encoder:** `nomic-embed-text` (Ollama) **ИЛИ** `sentence-transformers`
  (уже в `smart-rag`) — оба локальны, равноценны.
- **cross-encoder reranker:** `ms-marco-MiniLM` (Ollama) **ИЛИ**
  `sentence-transformers` CrossEncoder — локально, без кеша на кандидатах.
- **generate:** `llama3.1:8b` (Ollama) через OmniRoute (роутинг/fallback
  локальный↔облако при перегрузе).
- **embed/rerank инжектируются** — модуль `rag_retrieval.py` не завязан на
  конкретный бэкенд (анти-лок-ин).

## Интеграция
- `smart-rag` и `claude-mem` используют `rag_retrieval.py` (RAG-1/RAG-2/RAG-5).
- OmniRoute маршрутизирует запросы моделям; ADR-002 гарантирует приватность
  RU-сервисов/локальных данных.
- Генерация с инструкцией «опирайся только на контекст» (RAG-5) — галлюцинации
  снижаются; связь с BK-3 (контекст = данные, не инструкции).

## Границы
- Не используем облачные эмбеддинги для внутренних/приватных доков без согласования.
- Ollama — рекомендация, не жёсткая зависимость (sentence-transformers достаточен).
