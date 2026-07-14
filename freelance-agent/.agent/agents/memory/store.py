"""Memory Tree — local-first persistent memory for agents (OpenHuman-inspired).

Simple scored store: facts appended per agent, recalled by token-overlap with a query.
No vector DB — enough for one user's project context (no cold starts).
"""

from __future__ import annotations

import json
import os
import re
import time

STORE_DIR = os.path.dirname(os.path.abspath(__file__))


def _store_path(agent: str) -> str:
    os.makedirs(STORE_DIR, exist_ok=True)
    return os.path.join(STORE_DIR, f"{agent}.jsonl")


def _tokenize(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-zа-яё]+", text.lower()) if len(w) > 2}


def remember(agent: str, fact: str, kind: str = "fact") -> None:
    """Append a memory fact for an agent."""
    if not fact or not fact.strip():
        return
    rec = {"ts": time.time(), "agent": agent, "kind": kind, "fact": fact.strip()}
    with open(_store_path(agent), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def compact(agent: str, keep: int = 500) -> dict:
    """Compress an agent's memory: dedupe identical facts, keep newest `keep`.

    Chen mechanic #5 — auto-compress/optimize memory so recall stays fast and
    the store never grows unbounded. Rewrites the jsonl atomically.
    Returns {"before", "after", "removed"}.
    """
    path = _store_path(agent)
    if not os.path.exists(path):
        return {"before": 0, "after": 0, "removed": 0}

    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except Exception:
                continue

    before = len(records)

    # dedupe by normalized fact text, keeping the most recent occurrence
    by_fact: dict[str, dict] = {}
    for rec in records:
        norm = " ".join(rec.get("fact", "").lower().split())
        if not norm:
            continue
        prev = by_fact.get(norm)
        if prev is None or rec.get("ts", 0) >= prev.get("ts", 0):
            by_fact[norm] = rec

    deduped = sorted(by_fact.values(), key=lambda r: r.get("ts", 0), reverse=True)
    kept = deduped[:keep]
    # write back oldest-first to preserve append-order semantics
    kept.sort(key=lambda r: r.get("ts", 0))

    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for rec in kept:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    os.replace(tmp, path)

    after = len(kept)
    return {"before": before, "after": after, "removed": before - after}


def recall_scored(
    agent: str, query: str, top_k: int = 3, min_score: float = 0.0
) -> list[dict]:
    """Smart RAG top-K: return the most relevant facts as ranked dicts.

    Chen mechanic #2 — retrieve only the few most relevant items (ranked by
    Jaccard token overlap), not the whole store. Each dict carries the original
    record plus a "score". Filtered by `min_score`, capped at `top_k`.
    """
    path = _store_path(agent)
    if not os.path.exists(path):
        return []
    q_tokens = _tokenize(query)
    scored = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            fact_tokens = _tokenize(rec.get("fact", ""))
            if not q_tokens or not fact_tokens:
                overlap = 0.0
            else:
                overlap = len(q_tokens & fact_tokens) / (len(q_tokens | fact_tokens) or 1)
            if overlap > min_score:
                item = dict(rec)
                item["score"] = round(overlap, 4)
                scored.append(item)
    scored.sort(key=lambda x: -x["score"])
    return scored[:top_k]


def recall(agent: str, query: str, top_k: int = 3) -> str:
    """Return top_k relevant memory facts as a text block, or '' if none.

    Backward-compatible string view built on top of `recall_scored`.
    """
    hits = recall_scored(agent, query, top_k=top_k)
    if not hits:
        return ""
    return "Project memory:\n" + "\n".join(f"- {h.get('fact', '')}" for h in hits)
