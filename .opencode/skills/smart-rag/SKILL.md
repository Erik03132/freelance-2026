---
name: smart-rag
description: Умный семантический поиск для RAG с sentence-transformers. Использовать когда нужен поиск по смыслу, а не по ключевым словам. Работает в узких доменах без датасетов.
---

## Когда использовать
- RAG-система не находит релевантные ответы
- Пользователи жалуются на точность поиска
- Нужен поиск по смыслу, а не по словам
- Узкий домен без размеченных датасетов

## Установка

```bash
# Создаём venv с Python 3.12
python3.12 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
pip install sentence-transformers chromadb
```

## Быстрый старт

```python
from sentence_transformers import SentenceTransformer

# Загружаем модель (384 dim, быстрая)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Кодируем тексты
texts = ["Как кормить попугая", "Клетка для птицы"]
embeddings = model.encode(texts)

# Поиск по смыслу
query = "чем питается корелла"
query_emb = model.encode([query])
similarities = model.similarity(query_emb, embeddings)
```

## Интеграция с ChromaDB

```python
import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="./chroma_db")

# Используем sentence-transformers
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_or_create_collection(
    name="knowledge",
    embedding_function=ef
)

# Добавляем документы
collection.add(
    documents=["Текст 1", "Текст 2"],
    ids=["doc1", "doc2"]
)

# Поиск
results = collection.query(
    query_texts=["запрос"],
    n_results=3
)
```

## Модели

| Модель | Размер | Скорость | Качество | Использование |
|--------|--------|----------|----------|---------------|
| all-MiniLM-L6-v2 | 384 dim | ⚡⚡⚡ | ⭐⭐⭐ | Быстрый поиск |
| all-mpnet-base-v2 | 768 dim | ⚡⚡ | ⭐⭐⭐⭐ | Точный поиск |
| multilingual-e5-base | 768 dim | ⚡⚡ | ⭐⭐⭐⭐ | Мультиязычный |

## Best Practices

✅ **Делай:**
- Нормализуй эмбеддинги для косинусного сходства
- Разбивай длинные тексты на чанки 200-500 символов
- Тестируй recall на реальном датасете
- Кэшируй эмбеддинги для статичных документов

❌ **Не делай:**
- Не используй BGE без дообучения в узких доменах
- Не храни эмбеддинги в памяти для больших коллекций
- Не забывай про batch processing для скорости

## Сравнение с keyword search

**Keyword search:**
- Запрос: "уход за птицей"
- Найдёт только где есть слова "уход", "птица"

**Semantic search:**
- Запрос: "уход за птицей"
- Найдёт: "Корелла требует ежедневного внимания", "Клетку нужно чистить"

**Результат:** +40% к релевантности в узких доменах.

## Troubleshooting

**Модель не загружается:**
```bash
# Проверь Python версию (нужна 3.12, не 3.14)
python --version

# Очисти кэш
rm -rf ~/.cache/huggingface
```

**Медленная скорость:**
- Используй all-MiniLM-L6-v2 вместо mpnet
- Увеличь batch_size до 64
- Включи GPU: `device="cuda"`

## Ресурсы
- [Sentence-Transformers Docs](https://www.sbert.net/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- Пример: `agent-lab/sentence_embedder.py`
