#!/usr/bin/env python3
"""RAG-1 / RAG-2 / RAG-5 — retrieval + reranker-стадия (урок Habr #1070662).

Локальный, dependency-free RAG-ретривал:
  - VectorStore: in-memory, cosine, фильтр по metadata, pickle save/load;
  - reranker-стадия: bi-encoder top_k_retrieve → cross-encoder rerank → top_k_final;
  - асимметричные префиксы search_query: / search_document: (RAG-2);
  - генерация с инструкцией «опирайся только на контекст» (RAG-5).

Модели (embed/rerank/generate) инжектируются — модуль offline-дружелюбен и
тестируется на детерминированных векторах. Локальный Ollama-стек
(nomic-embed-text + ms-marco-MiniLM + llama) — эталонная архитектура (RAG-3, ADR-002).

Использование:
    from tools.rag_retrieval import VectorStore, rag_retrieve, embed_query
    store = VectorStore()
    store.add_document(text, embed_fn)          # с префиксом search_document:
    q = embed_query(question, embed_fn)         # с префиксом search_query:
    hits = rag_retrieve(store, question, embed_fn, reranker_fn,
                        top_k_retrieve=50, top_k_final=5)

Офлайн: `python3 tools/tests/eval_rag_retrieval.py` (deterministic, для eval_gate).
"""

from __future__ import annotations

import math
import os
import pickle

QUERY_PREFIX = "search_query:"
DOC_PREFIX = "search_document:"
GROUNDING = "Отвечай, опираясь ТОЛЬКО на приведённый контекст. Не используй внешние знания."


def embed_query(text: str, embed_fn, prefix: str = QUERY_PREFIX):
    """Эмбеддинг запроса с асимметричным префиксом (RAG-2)."""
    return embed_fn(prefix + text)


def embed_document(text: str, embed_fn, prefix: str = DOC_PREFIX):
    """Эмбеддинг документа с асимметричным префиксом (RAG-2)."""
    return embed_fn(prefix + text)


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class VectorStore:
    """Хранилище чанков + эмбеддингов с cosine-поиском и фильтром по metadata."""

    def __init__(self) -> None:
        self.chunks: list[str] = []
        self.embeddings: list[list[float]] = []
        self.metadata: list[dict] = []

    def add(self, text: str, embedding: list[float], metadata: dict | None = None) -> None:
        self.chunks.append(text)
        self.embeddings.append(list(embedding))
        self.metadata.append(metadata or {})

    def add_document(self, text: str, embed_fn, metadata: dict | None = None) -> None:
        self.add(text, embed_document(text, embed_fn), metadata)

    def save(self, path: str) -> None:
        with open(path, "wb") as f:
            pickle.dump(
                {"chunks": self.chunks, "embeddings": self.embeddings, "metadata": self.metadata},
                f,
            )

    def load(self, path: str) -> None:
        with open(path, "rb") as f:
            d = pickle.load(f)
        self.chunks = d["chunks"]
        self.embeddings = d["embeddings"]
        self.metadata = d["metadata"]

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 3,
        score_threshold: float = 0.0,
        filter_metadata: dict | None = None,
    ) -> list[dict]:
        """top-k по cosine + опциональный фильтр по metadata."""
        if not self.embeddings:
            return []
        q = list(query_embedding)
        scored = []
        for i, (emb, meta) in enumerate(zip(self.embeddings, self.metadata)):
            if filter_metadata and not all(meta.get(k) == v for k, v in filter_metadata.items()):
                continue
            s = _cosine(q, emb)
            if s >= score_threshold:
                scored.append({"text": self.chunks[i], "score": s, "metadata": meta})
        scored.sort(key=lambda x: -x["score"])
        return scored[:top_k]


def rerank(query: str, candidates: list[dict], reranker_fn, top_k: int = 2) -> list[dict]:
    """Cross-encoder rerank: пересортировка кандидатов по reranker_fn(query, text)."""
    for c in candidates:
        c["rerank_score"] = float(reranker_fn(query, c["text"]))
    return sorted(candidates, key=lambda x: -x["rerank_score"])[:top_k]


def rag_retrieve(
    store: VectorStore,
    query_text: str,
    embed_fn,
    reranker_fn,
    top_k_retrieve: int = 50,
    top_k_final: int = 5,
) -> list[dict]:
    """Полный пайплайн: embed(query) → bi-encoder top_k_retrieve → rerank → top_k_final."""
    q_emb = embed_query(query_text, embed_fn)
    candidates = store.search(q_emb, top_k=top_k_retrieve)
    if not candidates:
        return []
    return rerank(query_text, candidates, reranker_fn, top_k=top_k_final)


def build_prompt(question: str, chunks: list[str], grounding: str = GROUNDING) -> str:
    """Промпт генерации с инструкцией заземления (RAG-5)."""
    context = "\n---\n".join(chunks)
    return (
        f"{grounding}\n\n"
        f"Контекст:\n---\n{context}\n---\n\n"
        f"Вопрос: {question}\n\nОтвет:"
    )
