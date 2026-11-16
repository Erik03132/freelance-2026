"""Eval for REV-2 — eval set schema/loader/validation (Habr #1070534) — offline.

Запуск: python3 tools/tests/eval_rag_evalset.py
"""

from __future__ import annotations

import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.rag_evalset import (  # noqa: E402
    EvalCase,
    GoldEvidence,
    SPLITS,
    load_eval_set,
    load_holdout,
    load_visible,
    validate_case,
    validate_eval_set,
)


def _run() -> tuple[int, list[str]]:
    fails: list[str] = []

    good = {
        "id": "ops-047",
        "query": "После обновления агент перестал отвечать. Где посмотреть код ошибки E204?",
        "scenario": "exact_entity",
        "difficulty": "medium",
        "answerability": "answerable",
        "expected_document_ids": ["runbook-errors-v3"],
        "gold_evidence": [
            {"document_id": "runbook-errors-v3", "section_id": "errors/e204", "relevance": 2},
            {"document_id": "release-notes-2-4", "section_id": "known-issues", "relevance": 1},
        ],
        "expected_facts": ["E204 означает недоступность upstream API"],
        "acceptable_answer": "Короткая инструкция с источником",
        "why_it_matters": "Частый вопрос первой линии",
        "source": "support_log",
        "reviewed_by": "domain_expert",
        "dataset_version": "2026-08-14",
    }
    unanswerable = {
        "id": "out-003",
        "query": "Есть ли в корпусе ответ про лимиты на 10 000 запросов?",
        "scenario": "no_answer",
        "answerability": "unanswerable",
        "expected_document_ids": [],
        "gold_evidence": [],
        "expected_facts": [],
        "expected_documents": None,
    }

    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "eval.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(good, ensure_ascii=False) + "\n")
            f.write(json.dumps(unanswerable, ensure_ascii=False) + "\n")

        cases = load_eval_set(path)

        # TP-1: загрузка двух кейсов + поля
        if len(cases) != 2:
            fails.append(f"TP-1: должно быть 2 кейса, получили {len(cases)}")
        c = cases[0]
        if not (c.id == "ops-047" and c.query.startswith("После обновления")):
            fails.append("TP-1: id/query не прочитаны")
        if c.answerability != "answerable" or c.scenario != "exact_entity":
            fails.append("TP-1: answerability/scenario неверны")
        if len(c.gold_evidence) != 2 or c.gold_evidence[0].relevance != 2:
            fails.append("TP-1: gold_evidence не разобран (relevance 2)")

        # TP-2: валидация валидного набора → списки ошибок пусты
        errors = validate_eval_set(cases)
        if any(errors.values()):
            fails.append(f"TP-2: валидный набор дал ошибки: {errors}")

        # TP-3: relevance_map (document_id -> max grade)
        rm = c.relevance_map()
        if rm.get("runbook-errors-v3") != 2 or rm.get("release-notes-2-4") != 1:
            fails.append(f"TP-3: relevance_map неверна: {rm}")

        # TP-4: известные нарушения ловятся
        bad = EvalCase(
            id="",
            query="",
            scenario="unknown",
            answerability="answerable",
            expected_document_ids=[],
        )
        errs = validate_case(bad)
        if not any("scenario" in e for e in errs):
            fails.append(f"TP-4: неизвестный scenario не пойман: {errs}")
        if not any("expected_document_ids" in e for e in errs):
            fails.append(f"TP-4: answerable без expected не пойман: {errs}")

        bad_rel = EvalCase(
            id="r",
            query="q",
            scenario="paraphrase",
            answerability="answerable",
            expected_document_ids=["d"],
            gold_evidence=[GoldEvidence(document_id="d", relevance=5)],
        )
        if not any("relevance" in e for e in validate_case(bad_rel)):
            fails.append(f"TP-4: relevance вне 0-2 не поймана: {validate_case(bad_rel)}")

        # TP-5: unanswerable не требует expected; unanswerable с expected — ошибка
        if validate_case(cases[1]) != []:
            fails.append(f"TP-5: легальный unanswerable дал ошибки: {validate_case(cases[1])}")
        bad_un = EvalCase(
            id="u",
            query="q",
            scenario="no_answer",
            answerability="unanswerable",
            expected_document_ids=["d"],
        )
        if not any("unanswerable" in e for e in validate_case(bad_un)):
            fails.append(f"TP-5: unanswerable с expected не пойман: {validate_case(bad_un)}")

        # TP-6 (RSI-002): split — дефолт visible, фильтрация работает
        if c.split != "visible":
            fails.append(f"TP-6: дефолтный split должен быть visible, получен '{c.split}'")
        holdout_raw = dict(good)
        holdout_raw["id"] = "hold-001"
        holdout_raw["split"] = "holdout"
        mixed_path = os.path.join(td, "mixed.jsonl")
        with open(mixed_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(good, ensure_ascii=False) + "\n")
            f.write(json.dumps(holdout_raw, ensure_ascii=False) + "\n")
        all_cases = load_eval_set(mixed_path)
        vis = load_eval_set(mixed_path, split="visible")
        hol = load_eval_set(mixed_path, split="holdout")
        if len(all_cases) != 2 or len(vis) != 1 or len(hol) != 1:
            fails.append(
                f"TP-6: фильтр split неверен: all={len(all_cases)} vis={len(vis)} hol={len(hol)}"
            )
        elif vis[0].id != "ops-047" or hol[0].id != "hold-001":
            fails.append(f"TP-6: split перепутал кейсы: vis={vis[0].id} hol={hol[0].id}")
        if load_visible(mixed_path)[0].id != "ops-047":
            fails.append("TP-6: load_visible вернул не тот кейс")
        if load_holdout(mixed_path)[0].id != "hold-001":
            fails.append("TP-6: load_holdout вернул не тот кейс")

        # TP-7 (RSI-002): невалидный split и holdout без reviewed_by ловятся
        if SPLITS != {"visible", "holdout"}:
            fails.append(f"TP-7: набор split'ов неожидан: {sorted(SPLITS)}")
        try:
            load_eval_set(mixed_path, split="secret")
            fails.append("TP-7: невалидный split не поднял ошибку")
        except ValueError:
            pass
        bad_split = EvalCase(
            id="s",
            query="q",
            scenario="paraphrase",
            answerability="unanswerable",
            split="train",
        )
        if not any("split" in e for e in validate_case(bad_split)):
            fails.append(f"TP-7: split вне списка не пойман: {validate_case(bad_split)}")
        holdout_no_review = EvalCase(
            id="h",
            query="q",
            scenario="paraphrase",
            answerability="unanswerable",
            split="holdout",
            reviewed_by="",
        )
        if not any("reviewed_by" in e for e in validate_case(holdout_no_review)):
            fails.append(
                f"TP-7: holdout без reviewed_by не пойман: {validate_case(holdout_no_review)}"
            )
        holdout_reviewed = EvalCase(
            id="h2",
            query="q",
            scenario="paraphrase",
            answerability="unanswerable",
            split="holdout",
            reviewed_by="igor",
        )
        if validate_case(holdout_reviewed) != []:
            fails.append(f"TP-7: легальный holdout дал ошибки: {validate_case(holdout_reviewed)}")

    return len(fails), fails


if __name__ == "__main__":
    n, fails = _run()
    if fails:
        print(f"❌ EVAL FAILED ({n}):")
        for f in fails:
            print(f"  - {f}")
        sys.exit(1)
    print("✅ EVAL PASSED — REV-2 eval-set schema: JSONL loader, validation, relevance_map OK")
