# RB-3: Self-hosted эмбеддинги для smart-rag (08.08.2026)

## Задача
Текущий smart-rag использует внешние API/модели для эмбеддингов.
Опция: self-hosted `text-embeddings-inference` + `multilingual-e5-small` — скорость/цена/приватность.

## Варианты

| Подход | Латенция | Цена | Приватность | Зависимости |
|--------|----------|------|-------------|-------------|
| Внешний API | ~100-300 мс | $/M токенов | Облако | ключ, сеть |
| TEI (huggingface) | ~10-30 мс | 0 | Локально | GPU/CPU, Docker |
| Ollama embeddings | ~30-80 мс | 0 | Локально | Ollama |

## Рекомендация
1. **Ollama `nomic-embed-text` или `mxbai-embed-large`** — самый дешёвый вход (уже есть Ollama на VPS). Для RU-корпусов: `multilingual-e5-small` через TEI лучше (RU-качество).
2. **text-embeddings-inference** — если нужен batch и стабильность (Rust, графнаг).
3. Dimension: e5-small = 384, nomic = 768, mxbai = 1024. **Важно:** смена модели эмбеддингов ломает индексы — мигрировать с переиндексацией.

## Интеграция в smart-rag
`smart-rag/SKILL.md` уже поддерживает sentence-transformers. Добавить флаг эмбеддинг-провайдера:
```python
EMBED_MODELS = {
    "api": SentenceTransformer('all-MiniLM-L6-v2'),
    "ollama": None,  # POST /api/embeddings
    "tei": None,     # POST /embed
}
```

## Статус
Документ-рекомендация. Внедрение: при появлении нагрузки на smart-rag (сейчас корпусы маленькие, внешние API дешевле). Оценка 7/10 — берём при масштабировании.