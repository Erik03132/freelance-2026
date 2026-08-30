#!/usr/bin/env python3
"""REV-3 — минимальный runner RAG eval set c per-case trace (урок Habr #1070534).

Runner на каждый кейс сохраняет trace (query, retrieved[{id, rank, score}],
answer, latency_ms, prompt_version) — без следа метрика бесполезна: падение
Recall объясняется trace-ом построчно, а не средним скором.

retrieve_fn(query, top_k) -> list[dict] с полями "id" и "score" (порядок = ранг).
answer_fn(query, retrieved_items) -> str (пусто == воздержание).

Retrieval-метрики (Recall@k/MRR@k/nDCG@k) считаются ТОЛЬКО по answerable-кейсам;
по unanswerable — abstention. Агрегаты даются общие и по сценариям (срезы),
чтобы критичный срез не растворялся в среднем (check_gates).

Офлайн, stdlib. Для eval_gate:
    python3 tools/tests/eval_rag_evalrunner.py
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from collections.abc import Callable

from tools.rag_evalset import EvalCase
from tools.rag_metrics import (
    recall_at_k,
    mrr_at_k,
    ndcg_at_k,
    aggregate,
    abstention_accuracy,
    false_answer_rate,
)


@dataclass
class RetrievedItem:
    id: str
    rank: int
    score: float = 0.0


@dataclass
class CaseTrace:
    case_id: str
    config_id: str
    index_version: str
    prompt_version: str
    query: str
    retrieved: list[RetrievedItem] = field(default_factory=list)
    answer: str = ""
    latency_ms: float = 0.0

    def to_json(self) -> dict:
        return asdict(self)


def run_eval(
    cases: list[EvalCase],
    retrieve_fn: Callable[[str, int], list[dict]],
    top_k: int = 5,
    config_id: str = "",
    index_version: str = "",
    prompt_version: str = "",
    answer_fn: Callable[[str, list], str] | None = None,
) -> tuple[list[CaseTrace], dict]:
    """Прогон набора. Возвращает (traces, metrics)."""
    traces: list[CaseTrace] = []
    for case in cases:
        t0 = time.perf_counter()
        raw = retrieve_fn(case.query, top_k) or []
        latency_ms = (time.perf_counter() - t0) * 1000.0
        items = [
            RetrievedItem(id=str(r.get("id")), rank=i + 1, score=float(r.get("score", 0.0)))
            for i, r in enumerate(raw[:top_k])
        ]
        answer = answer_fn(case.query, items) if answer_fn else ""
        traces.append(
            CaseTrace(
                case_id=case.id,
                config_id=config_id,
                index_version=index_version,
                prompt_version=prompt_version,
                query=case.query,
                retrieved=items,
                answer=answer or "",
                latency_ms=round(latency_ms, 3),
            )
        )
    return traces, summarize(traces, cases, top_k)


def summarize(traces: list[CaseTrace], cases: list[EvalCase], top_k: int = 5) -> dict:
    """Агрегаты: Recall@k / MRR@k / nDCG@k общие и по сценариям + abstention."""
    by_id = {c.id: c for c in cases}
    rec: list[float] = []
    mrr: list[float] = []
    ndcg: list[float] = []
    pred: list[bool] = []
    actual: list[bool] = []
    slices: dict[str, dict[str, list[float]]] = {}

    for t in traces:
        c = by_id.get(t.case_id)
        if c is None:
            continue
        ids = [r.id for r in t.retrieved]
        pred.append(bool(t.answer))
        actual.append(c.answerability == "answerable")
        if c.answerability != "answerable":
            continue
        r = recall_at_k(ids, c.expected_document_ids, top_k)
        m = mrr_at_k(ids, c.expected_document_ids, top_k)
        n = ndcg_at_k(ids, c.relevance_map(), top_k)
        rec.append(r)
        mrr.append(m)
        ndcg.append(n)
        sl = slices.setdefault(c.scenario, {"recall": [], "mrr": [], "ndcg": []})
        sl["recall"].append(r)
        sl["mrr"].append(m)
        sl["ndcg"].append(n)

    return {
        "top_k": top_k,
        "n_total": len(traces),
        "n_answerable": len(rec),
        "recall_at_k": aggregate(rec),
        "mrr_at_k": aggregate(mrr),
        "ndcg_at_k": aggregate(ndcg),
        "by_scenario": {
            s: {
                "n": len(vals["recall"]),
                "recall_at_k": aggregate(vals["recall"]),
                "mrr_at_k": aggregate(vals["mrr"]),
                "ndcg_at_k": aggregate(vals["ndcg"]),
            }
            for s, vals in slices.items()
        },
        "abstention": {
            "accuracy": abstention_accuracy(pred, actual),
            "false_answer_rate": false_answer_rate(pred, actual),
        },
    }


def check_gates(metrics: dict, gates: dict[str, dict[str, float]]) -> list[str]:
    """Возвращает нарушения порогов критичных срезов (пусто == всё в норме)."""
    missed = []
    for scenario, thresholds in gates.items():
        sc = metrics.get("by_scenario", {}).get(scenario)
        if sc is None:
            missed.append(f"{scenario}: срез отсутствует в наборе")
            continue
        for metric, minimum in thresholds.items():
            got = sc.get(metric)
            if got is None:
                missed.append(f"{scenario}/{metric}: метрика не посчитана")
            elif got < minimum:
                missed.append(f"{scenario}/{metric}: {got:.3f} < порога {minimum}")
    return missed


def write_report(traces: list[CaseTrace], path: str) -> None:
    """JSONL-выгрузка traces (для cross-check/trace-анализа)."""
    with open(path, "w", encoding="utf-8") as f:
        for t in traces:
            f.write(json.dumps(t.to_json(), ensure_ascii=False) + "\n")
