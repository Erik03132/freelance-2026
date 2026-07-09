"""Self-Learning Loop — signal capture for agents (human behavioral signals).

Append-only JSONL store of how people use the agents:
what was generated, and later — accepted / edited / rejected.
"""

from __future__ import annotations

import json
import os
import time
import uuid

STORE_DIR = os.path.dirname(os.path.abspath(__file__))
SIGNAL_FILE = os.path.join(STORE_DIR, "signals.jsonl")


def _ensure_store() -> None:
    os.makedirs(STORE_DIR, exist_ok=True)
    if not os.path.exists(SIGNAL_FILE):
        open(SIGNAL_FILE, "w").close()


def capture_start(
    agent: str,
    action: str,
    spec: str,
    meta: dict | None = None,
    result_ref: str = "",
) -> str:
    """Log a generation event. Returns a signal id (sid)."""
    _ensure_store()
    sid = uuid.uuid4().hex[:12]
    rec = {
        "sid": sid,
        "ts": time.time(),
        "phase": "start",
        "agent": agent,
        "action": action,
        "spec": spec,
        "meta": meta or {},
        "result_ref": result_ref,
        "outcome": None,
    }
    with open(SIGNAL_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return sid


def capture_outcome(sid: str, outcome: str, note: str = "") -> bool:
    """Record the user's verdict on a previously captured signal."""
    _ensure_store()
    outcome = outcome.lower()
    if outcome not in ("accepted", "edited", "rejected"):
        return False
    rec = {
        "sid": sid,
        "ts": time.time(),
        "phase": "outcome",
        "outcome": outcome,
        "note": note,
    }
    with open(SIGNAL_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return True


def read_signals(agent: str | None = None) -> list[dict]:
    """Return all signal records, optionally filtered by agent."""
    if not os.path.exists(SIGNAL_FILE):
        return []
    out = []
    with open(SIGNAL_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if agent is None or rec.get("agent") == agent:
                out.append(rec)
    return out
