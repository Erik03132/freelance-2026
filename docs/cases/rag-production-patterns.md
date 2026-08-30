## rag-production-patterns — препроцессинг запроса, семантический кэш, UPSERT
**Автор/источник:** Антон (A__T), SberDevices, Habr 1071570 (20.08.2026) — ГигаСправка: RAG-сервис DocSense (Qdrant) поверх базы техподдержки Сбера.
**Суть (2-3 строки):** Контекстная справка на ошибках ТВ: LLM-препроцессор чистит разговорный запрос перед эмбеддингом, RAG (RecursiveCharacterTextSplitter, chunk 4000/overlap 400, UPSERT по content-hash id), семантический кэш в Qdrant (~100x экономия токенов), LLM-as-Judge + CSAT, Arize Phoenix observability.
**Стек:** GigaChat, EmbeddingsGigaR, Qdrant, RecursiveCharacterTextSplitter, Arize Phoenix, LLM-as-Judge.
**Что применимо у нас:** [ДА] — 3 фичи: (ES-19) LLM-препроцессор запроса перед retrieval (заполняет реальный gap в smart-rag), (ES-20) семантический кэш для RAG, (ES-21) идемпотентные инкрементальные апдейты (UPSERT) + LLM-as-Judge→инвалидация кэша. Не берём: two-level SDK-контекст (app-интеграция), Quality Gates MLP (есть AP-1/eval_gate), temperature≈0 (есть LV-3/NF), observability (есть trajectory_eval).
**Действие:** [ ] ES-19..ES-21 → ACTIVE_TASKS (секция «🧠 Эксперт-сессия»)
