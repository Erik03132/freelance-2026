"""Eval for REV-1 — retrieval metrics (Habr #1070534) — offline, stdlib.

Запуск: python3 tools/tests/eval_rag_metrics.py
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.rag_metrics import (  # noqa: E402
    recall_at_k,
    mrr_at_k,
    ndcg_at_k,
    aggregate,
    abstention_accuracy,
    false_answer_rate,
)


def _close(a: float, b: float, tol: float = 1e-6) -> bool:
    return abs(a - b) <= tol


def _run() -> tuple[int, list[str]]:
    fails: list[str] = []

    # REV-TP1: Recall@k
    if recall_at_k(["a", "b", "c"], ["b"], k=2) != 1.0:
        fails.append("REV-TP1: Recall@2 должен быть 1.0 (b в top-2)")
    if recall_at_k(["a", "b", "c"], ["b"], k=1) != 0.0:
        fails.append("REV-TP1: Recall@1 должен быть 0.0 (b вне top-1)")
    if recall_at_k(["a"], [], k=5) != 0.0:
        fails.append("REV-TP1: пустые expected → 0.0")

    # REV-TP2: MRR@k
    if not _close(mrr_at_k(["x", "b", "c"], ["b"]), 0.5):
        fails.append(f"REV-TP2: MRR должен быть 0.5, получили {mrr_at_k(['x', 'b', 'c'], ['b'])}")
    if mrr_at_k(["x", "y"], ["b"], k=2) != 0.0:
        fails.append("REV-TP2: нет expected в top-k → 0.0")

    # REV-TP3: nDCG@k (graded 0/1/2) — эталон посчитан вручную для рангов a→0,b→2,c→1
    rel = {"b": 2, "c": 1}
    got = ndcg_at_k(["a", "b", "c"], rel, k=3)
    # DCG = 0 + (2^2-1)/log2(3) + (2^1-1)/log2(4) = 3/1.58496 + 1/2 = 2.39278...
    # IDCG (2,1,0) = (2^2-1)/log2(2) + (2^1-1)/log2(3) + 0 = 3 + 0.63093 = 3.63093
    expected_ndcg = 2.39278 / 3.63093
    if not _close(got, expected_ndcg, 1e-3):
        fails.append(f"REV-TP3: nDCG@3 должен быть ~{expected_ndcg:.4f}, получили {got:.4f}")
    if ndcg_at_k(["a", "x", "y"], rel, k=3) != 0.0:
        fails.append("REV-TP3: нет релевантных → 0.0")

    # REV-TP4: aggregate mean
    if not _close(aggregate([1.0, 0.0, 1.0]), 2.0 / 3.0):
        fails.append("REV-TP4: mean([1,0,1]) должен быть 2/3")
    if aggregate([]) != 0.0:
        fails.append("REV-TP4: пустой список → 0.0")

    # REV-TP5: abstention
    # predicted=[ответить, ответить, воздержаться], actual=[answerable, unanswerable, unanswerable]
    pred = [True, True, False]
    actual = [True, False, False]
    if not _close(abstention_accuracy(pred, actual), 2 / 3):
        fails.append("REV-TP5: abstention_accuracy должен быть 2/3")
    if not _close(false_answer_rate(pred, actual), 0.5):
        fails.append("REV-TP5: false_answer_rate (1 из 2 unanswerable) должен быть 0.5")
    if false_answer_rate([True], [True]) != 0.0:
        fails.append("REV-TP5: нет unanswerable → 0.0")

    return len(fails), fails


if __name__ == "__main__":
    n, fails = _run()
    if fails:
        print(f"❌ EVAL FAILED ({n}):")
        for f in fails:
            print(f"  - {f}")
        sys.exit(1)
    print("✅ EVAL PASSED — REV-1 metrics: Recall@k, MRR@k, nDCG@k, abstention OK")