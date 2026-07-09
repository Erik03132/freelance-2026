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


def recall(agent: str, query: str, top_k: int = 3) -> str:
    """Return top_k relevant memory facts as a text block, or '' if none."""
    path = _store_path(agent)
    if not os.path.exists(path):
        return ""
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
                overlap = 0
            else:
                overlap = len(q_tokens & fact_tokens) / (len(q_tokens | fact_tokens) or 1)
            if overlap > 0:
                scored.append((overlap, rec.get("fact", "")))
    if not scored:
        return ""
    scored.sort(key=lambda x: -x[0])
    top = [f for _, f in scored[:top_k]]
    return "Project memory:\n" + "\n".join(f"- {t}" for t in top)
