#!/usr/bin/env python3
"""REV-1 — метрики retrieval, отдельные от генерации (урок Habr #1070534).

Per-case функции → агрегаты mean(). Retrieval (Recall@k / MRR@k / nDCG@k)
считается ТОЛЬКО по answerable-кейсам; для «нет ответа» есть abstention.
nDCG использует graded relevance 0/1/2 (см. gold_evidence в rag_evalset).

Офлайн, stdlib. Для eval_gate:
    python3 tools/tests/eval_rag_metrics.py
"""

from __future__ import annotations

import math
from statistics import mean
from collections.abc import Iterable, Mapping, Sequence


def recall_at_k(retrieved: Sequence[str], expected: Sequence[str], k: int | None = None) -> float:
    """1.0, если хотя бы один обязательный документ попал в top-k, иначе 0.0."""
    top = retrieved if k is None else retrieved[:k]
    return 1.0 if set(top) & set(expected) else 0.0


def mrr_at_k(retrieved: Sequence[str], expected: Sequence[str], k: int | None = None) -> float:
    """Обратный ранг первого обязательного документа (0, если его нет в top-k)."""
    top = retrieved if k is None else retrieved[:k]
    exp = set(expected)
    for i, doc in enumerate(top):
        if doc in exp:
            return 1.0 / (i + 1)
    return 0.0


def _dcg(gains: Sequence[int]) -> float:
    return sum((2**g - 1) / math.log2(i + 2) for i, g in enumerate(gains))


def ndcg_at_k(
    retrieved: Sequence[str],
    relevance: Mapping[str, int],
    k: int | None = None,
) -> float:
    """nDCG@k по градациям 0/1/2. relevance: document_id -> grade (0 == нет)."""
    top = retrieved if k is None else retrieved[:k]
    gains = [relevance.get(doc, 0) for doc in top]
    dcg = _dcg(gains)
    idcg = _dcg(sorted(gains, reverse=True))
    return dcg / idcg if idcg > 0 else 0.0


def aggregate(values: Iterable[float]) -> float:
    """Среднее по кейсам (для Recall@k / MRR@k / nDCG@k)."""
    vals = list(values)
    return mean(vals) if vals else 0.0


def abstention_accuracy(predicted: Sequence[bool], actual: Sequence[bool]) -> float:
    """Доля корректных решений «отвечать / воздержаться» по всем кейсам."""
    if not predicted:
        return 0.0
    return sum(1 for p, a in zip(predicted, actual) if p == a) / len(predicted)


def false_answer_rate(predicted: Sequence[bool], actual: Sequence[bool]) -> float:
    """На unanswerable-кейсах: доля «уверенных ответов», которые давать нельзя."""
    unans = [p for p, a in zip(predicted, actual) if not a]
    return (sum(unans) / len(unans)) if unans else 0.0
