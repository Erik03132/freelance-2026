"""Eval for REV-3 — eval runner + per-case trace (Habr #1070534) — offline.

Запуск: python3 tools/tests/eval_rag_evalrunner.py
"""

from __future__ import annotations

import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.rag_evalset import EvalCase, GoldEvidence  # noqa: E402
from tools.rag_evalrunner import run_eval, check_gates, write_report  # noqa: E402


def _close(a: float, b: float, tol: float = 1e-3) -> bool:
    return abs(a - b) <= tol


def _cases() -> list[EvalCase]:
    return [
        EvalCase(
            id="c1",
            query="код ошибки E204",
            scenario="exact_entity",
            answerability="answerable",
            expected_document_ids=["docA"],
            gold_evidence=[GoldEvidence(document_id="docA", relevance=2)],
        ),
        EvalCase(
            id="c2",
            query="как оформить служебную",
            scenario="paraphrase",
            answerability="answerable",
            expected_document_ids=["docB"],
            gold_evidence=[
                GoldEvidence(document_id="docB", relevance=2),
                GoldEvidence(document_id="docA", relevance=1),
            ],
        ),
        EvalCase(
            id="c3",
            query="этого в корпусе нет",
            scenario="no_answer",
            answerability="unanswerable",
            expected_document_ids=[],
        ),
    ]


def _retrieve(query: str, top_k: int) -> list[dict]:
    if "E204" in query:
        order = ["docA", "docC", "docB"]
    elif "служебн" in query:
        order = ["docA", "docB", "docC"]  # docB на 2-й позиции -> MRR=0.5
    else:
        order = ["docC", "docA", "docB"]
    return [{"id": d, "score": 1.0 - i * 0.05} for i, d in enumerate(order)][:top_k]


def _answer(query: str, retrieved) -> str:
    if "E204" in query:
        return "E204: upstream API недоступен"
    if "служебн" in query:
        return "Инструкция по служебной записке"
    return ""  # воздержание


def _run() -> tuple[int, list[str]]:
    fails: list[str] = []
    cases = _cases()

    traces, metrics = run_eval(
        cases,
        _retrieve,
        top_k=3,
        config_id="dense-v1",
        index_version="2026-08-14",
        prompt_version="answer-v5",
        answer_fn=_answer,
    )

    # TP-1: trace per case — структура и ранги
    if len(traces) != 3:
        fails.append(f"TP-1: должно быть 3 trace, получили {len(traces)}")
    t1 = traces[0]
    if t1.case_id != "c1" or t1.config_id != "dense-v1" or t1.index_version != "2026-08-14":
        fails.append("TP-1: токены trace (config/index) не заполнены")
    if [r.id for r in t1.retrieved] != ["docA", "docC", "docB"] or [
        r.rank for r in t1.retrieved
    ] != [1, 2, 3]:
        fails.append(f"TP-1: retrieved/rank неверны: {t1.retrieved}")
    if t1.answer != "E204: upstream API недоступен":
        fails.append(f"TP-1: answer не заполнен: {t1.answer!r}")
    if t1.latency_ms < 0:
        fails.append("TP-1: latency_ms отрицательна")

    # TP-2: агрегаты retrieval (эталоны посчитаны вручную)
    if not _close(metrics["recall_at_k"], 1.0):
        fails.append(f"TP-2: recall@3 должен быть 1.0, получили {metrics['recall_at_k']}")
    if not _close(metrics["mrr_at_k"], 0.75):
        fails.append(f"TP-2: mrr@3 (1.0 и 0.5) должен быть 0.75, получили {metrics['mrr_at_k']}")
    if not _close(metrics["ndcg_at_k"], (1.0 + 0.7968) / 2, 1e-2):
        fails.append(f"TP-2: ndcg@3 должен быть ~0.898, получили {metrics['ndcg_at_k']}")
    if metrics["n_answerable"] != 2 or metrics["n_total"] != 3:
        fails.append("TP-2: n_answerable/n_total неверны")

    # TP-3: срезы — exact_entity и paraphrase отдельно
    sc = metrics["by_scenario"]
    if not _close(sc["exact_entity"]["recall_at_k"], 1.0) or not _close(
        sc["exact_entity"]["mrr_at_k"], 1.0
    ):
        fails.append(f"TP-3: exact_entity срез неверен: {sc.get('exact_entity')}")
    if not _close(sc["paraphrase"]["mrr_at_k"], 0.5):
        fails.append(
            f"TP-3: paraphrase мrr@3 должен быть 0.5, получили {sc['paraphrase']['mrr_at_k']}"
        )

    # TP-4: abstention — c3 воздерживается (пустой answer)
    ab = metrics["abstention"]
    if not _close(ab["accuracy"], 1.0) or ab["false_answer_rate"] != 0.0:
        fails.append(f"TP-4: abstention неверный: {ab}")

    # TP-5: check_gates — критичный срез со своим порогом
    if check_gates(metrics, {"exact_entity": {"recall_at_k": 1.0}}) != []:
        fails.append("TP-5: pass-гейт не должен нарушаться")
    missed = check_gates(metrics, {"paraphrase": {"mrr_at_k": 1.0}})
    if not any("paraphrase" in m for m in missed):
        fails.append(f"TP-5: fail-гейт (mrr>=1.0) должен нарушаться, получили {missed}")

    # TP-6: write_report — JSONL traces
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "traces.jsonl")
        write_report(traces, path)
        with open(path, encoding="utf-8") as f:
            lines = [ln for ln in f if ln.strip()]
        if len(lines) != 3:
            fails.append(f"TP-6: в отчёте должно быть 3 строки, получили {len(lines)}")

    return len(fails), fails


if __name__ == "__main__":
    n, fails = _run()
    if fails:
        print(f"❌ EVAL FAILED ({n}):")
        for f in fails:
            print(f"  - {f}")
        sys.exit(1)
    print("✅ EVAL PASSED — REV-3 runner: per-case trace, sliced metrics, gates, JSONL report OK")
