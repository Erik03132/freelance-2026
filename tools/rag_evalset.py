#!/usr/bin/env python3
"""REV-2 — формат кейса ручного RAG eval set (урок Habr #1070534).

JSONL, один объект на кейс. Стабильные ссылки — document_id / section_id
(НЕ chunk_id: смена chunking не должна ломать gold-метки).

Ключевые поля (из статьи):
  id, query, scenario, difficulty, answerability, expected_document_ids,
  gold_evidence [{document_id, section_id, relevance 0-2}], expected_facts,
  acceptable_answer, why_it_matters, source, reviewed_by, dataset_version.

answerability хранит вопросы БЕЗ ответа — иначе система не учится воздерживаться.
Для unanswerable expected_document_ids может быть пустым (это норма).

Офлайн, stdlib. Для eval_gate:
    python3 tools/tests/eval_rag_evalset.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

SCENARIOS = {
    "exact_entity",
    "paraphrase",
    "long_section",
    "tables",
    "versions",
    "no_answer",
    "bad_wording",
    "sensitive",
}
ANSWERABILITY = {"answerable", "unanswerable"}

REQUIRED = (
    "id",
    "query",
    "scenario",
    "answerability",
    "expected_document_ids",
    "gold_evidence",
    "expected_facts",
)


@dataclass
class GoldEvidence:
    document_id: str
    section_id: str = ""
    relevance: int = 1  # 0 - фон, 1 - полезен, 2 - отвечает напрямую


@dataclass
class EvalCase:
    id: str
    query: str
    scenario: str
    answerability: str
    expected_document_ids: list[str] = field(default_factory=list)
    gold_evidence: list[GoldEvidence] = field(default_factory=list)
    expected_facts: list[str] = field(default_factory=list)
    acceptable_answer: str = ""
    difficulty: str = ""
    why_it_matters: str = ""
    source: str = ""
    reviewed_by: str = ""
    dataset_version: str = ""

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> EvalCase:
        ev = [
            GoldEvidence(
                document_id=e.get("document_id", ""),
                section_id=e.get("section_id", ""),
                relevance=int(e.get("relevance", 1)),
            )
            for e in d.get("gold_evidence") or []
        ]
        return cls(
            id=str(d["id"]),
            query=str(d["query"]),
            scenario=str(d.get("scenario", "")),
            answerability=str(d.get("answerability", "answerable")),
            expected_document_ids=list(d.get("expected_document_ids") or []),
            gold_evidence=ev,
            expected_facts=list(d.get("expected_facts") or []),
            acceptable_answer=str(d.get("acceptable_answer", "")),
            difficulty=str(d.get("difficulty", "")),
            why_it_matters=str(d.get("why_it_matters", "")),
            source=str(d.get("source", "")),
            reviewed_by=str(d.get("reviewed_by", "")),
            dataset_version=str(d.get("dataset_version", "")),
        )

    @classmethod
    def from_json_line(cls, line: str) -> EvalCase:
        return cls.from_dict(json.loads(line))

    def relevance_map(self) -> dict[str, int]:
        """document_id -> max grade (для nDCG@k по doc-у, а не по chunk-у)."""
        out: dict[str, int] = {}
        for e in self.gold_evidence:
            out[e.document_id] = max(out.get(e.document_id, 0), e.relevance)
        return out


def load_eval_set(path: str) -> list[EvalCase]:
    """Чтение JSONL-набора. Пустые строки пропускаются."""
    cases: list[EvalCase] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                cases.append(EvalCase.from_json_line(line))
    return cases


def validate_case(case: EvalCase) -> list[str]:
    """Ошибки кейса. Пустой список == валиден."""
    errs: list[str] = []
    if not case.id:
        errs.append("id пустой")
    if not case.query:
        errs.append("query пустой")
    if case.scenario not in SCENARIOS:
        errs.append(f"scenario '{case.scenario}' вне списка {sorted(SCENARIOS)}")
    if case.answerability not in ANSWERABILITY:
        errs.append(f"answerability '{case.answerability}' вне {sorted(ANSWERABILITY)}")
    if case.answerability == "answerable" and not case.expected_document_ids:
        errs.append("answerable без expected_document_ids")
    for e in case.gold_evidence:
        if not e.document_id:
            errs.append("gold_evidence с пустым document_id")
        if not (0 <= e.relevance <= 2):
            errs.append(f"gold_evidence relevance {e.relevance} вне 0-2")
    if case.answerability == "unanswerable" and case.expected_document_ids:
        errs.append("unanswerable, но указаны expected_document_ids")
    return errs


def validate_eval_set(cases: list[EvalCase]) -> dict[str, list[str]]:
    """{case_id: [ошибки]} для всех кейсов."""
    return {c.id: validate_case(c) for c in cases}
