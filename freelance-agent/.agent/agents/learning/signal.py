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
    """Record the user's verdict on a previously captured signal.

    Looks up the matching start record to preserve the agent field.
    """
    _ensure_store()
    outcome = outcome.lower()
    if outcome not in ("accepted", "edited", "rejected"):
        return False
    agent = _find_agent_by_sid(sid)
    rec = {
        "sid": sid,
        "ts": time.time(),
        "phase": "outcome",
        "agent": agent,
        "outcome": outcome,
        "note": note,
    }
    with open(SIGNAL_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return True


def _find_agent_by_sid(sid: str) -> str:
    """Search the signal store for a start record with the given sid."""
    if not os.path.exists(SIGNAL_FILE):
        return ""
    with open(SIGNAL_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if rec.get("sid") == sid and rec.get("phase") == "start":
                return rec.get("agent", "")
    return ""


def read_signals(agent: str | None = None) -> list[dict]:
    """Return all signal records, optionally filtered by agent.

    Outcome records (which don't store agent directly) are matched via
    their corresponding start record by sid.
    """
    if not os.path.exists(SIGNAL_FILE):
        return []
    starts: dict[str, str] = {}
    with open(SIGNAL_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if rec.get("phase") == "start" and rec.get("sid"):
                starts[rec["sid"]] = rec.get("agent", "")

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
            if agent is None:
                out.append(rec)
            elif rec.get("agent") == agent:
                out.append(rec)
            elif rec.get("phase") == "outcome":
                start_agent = starts.get(rec.get("sid", ""), "")
                if start_agent == agent:
                    out.append(rec)
    return out
