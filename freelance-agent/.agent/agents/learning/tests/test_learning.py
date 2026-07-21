"""Tests for self-learning loop — signal capture + learner aggregation."""

import json
import os
import sys
import tempfile

_AGENTS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _AGENTS not in sys.path:
    sys.path.insert(0, _AGENTS)

# Patch STORE_DIR before importing to use a temp directory
import learning  # noqa: E402
import learning.signal as _signal_mod  # noqa: E402

_ORIG_STORE_DIR = _signal_mod.STORE_DIR
_ORIG_SIGNAL_FILE = _signal_mod.SIGNAL_FILE


def _use_tmpdir(tmpdir):
    _signal_mod.STORE_DIR = tmpdir
    _signal_mod.SIGNAL_FILE = os.path.join(tmpdir, "signals.jsonl")


def _restore_store():
    _signal_mod.STORE_DIR = _ORIG_STORE_DIR
    _signal_mod.SIGNAL_FILE = _ORIG_SIGNAL_FILE


# ── signal.py tests ─────────────────────────────────────────────────────

def test_capture_start_returns_sid():
    with tempfile.TemporaryDirectory() as d:
        _use_tmpdir(d)
        try:
            sid = learning.capture_start("artemiy", "component", "button hero")
            assert isinstance(sid, str)
            assert len(sid) == 12
        finally:
            _restore_store()


def test_capture_start_writes_jsonl():
    with tempfile.TemporaryDirectory() as d:
        _use_tmpdir(d)
        try:
            learning.capture_start("sherl", "research", "AI trends 2026")
            with open(_signal_mod.SIGNAL_FILE) as f:
                lines = [l.strip() for l in f if l.strip()]
            assert len(lines) == 1
            rec = json.loads(lines[0])
            assert rec["agent"] == "sherl"
            assert rec["action"] == "research"
            assert rec["phase"] == "start"
            assert rec["outcome"] is None
        finally:
            _restore_store()


def test_capture_outcome_valid():
    with tempfile.TemporaryDirectory() as d:
        _use_tmpdir(d)
        try:
            sid = learning.capture_start("kulibin", "audit", "utils.py")
            ok = learning.capture_outcome(sid, "accepted")
            assert ok is True
            with open(_signal_mod.SIGNAL_FILE) as f:
                lines = [l.strip() for l in f if l.strip()]
            assert len(lines) == 2
            outcome_rec = json.loads(lines[1])
            assert outcome_rec["phase"] == "outcome"
            assert outcome_rec["outcome"] == "accepted"
            assert outcome_rec["sid"] == sid
        finally:
            _restore_store()


def test_capture_outcome_invalid():
    with tempfile.TemporaryDirectory() as d:
        _use_tmpdir(d)
        try:
            ok = learning.capture_outcome("fake", "maybe")
            assert ok is False
        finally:
            _restore_store()


def test_read_signals_empty():
    with tempfile.TemporaryDirectory() as d:
        _use_tmpdir(d)
        try:
            signals = learning.read_signals()
            assert signals == []
        finally:
            _restore_store()


def test_read_signals_filter_by_agent():
    with tempfile.TemporaryDirectory() as d:
        _use_tmpdir(d)
        try:
            learning.capture_start("artemiy", "component", "nav bar")
            learning.capture_start("sherl", "research", "market fit")
            sherl_signals = learning.read_signals(agent="sherl")
            assert len(sherl_signals) == 1
            assert sherl_signals[0]["agent"] == "sherl"
        finally:
            _restore_store()


def test_capture_start_multiple_same_agent():
    with tempfile.TemporaryDirectory() as d:
        _use_tmpdir(d)
        try:
            s1 = learning.capture_start("artemiy", "component", "hero")
            s2 = learning.capture_start("artemiy", "page", "landing")
            assert s1 != s2
            signals = learning.read_signals(agent="artemiy")
            assert len(signals) == 2
        finally:
            _restore_store()


# ── learner.py tests ────────────────────────────────────────────────────

def _seed_signals(tmpdir, agent, specs_outcomes):
    """Helper: write start+outcome pairs directly to JSONL.

    NOTE: outcome records include 'agent' field to match read_signals(agent) filter.
    This works around a real bug: capture_outcome() doesn't write 'agent' to outcome
    records, so read_signals(agent) drops them. The tests below document both the
    intended behavior (with agent in outcomes) and the actual bug (without agent).
    """
    _use_tmpdir(tmpdir)
    records = []
    for i, (spec, outcome) in enumerate(specs_outcomes):
        sid = f"seed_{i}_{outcome[:3]}"
        records.append(json.dumps({
            "sid": sid, "ts": 0, "phase": "start",
            "agent": agent, "action": "test", "spec": spec,
            "meta": {}, "outcome": None,
        }))
        records.append(json.dumps({
            "sid": sid, "ts": 1, "phase": "outcome",
            "agent": agent, "outcome": outcome, "note": "",
        }))
    with open(_signal_mod.SIGNAL_FILE, "w") as f:
        f.write("\n".join(records) + "\n")


def test_build_learned_context_insufficient_data():
    with tempfile.TemporaryDirectory() as d:
        _use_tmpdir(d)
        try:
            ctx = learning.build_learned_context("artemiy", min_samples=3)
            assert ctx == ""
        finally:
            _restore_store()


def test_build_learned_context_enough_data():
    with tempfile.TemporaryDirectory() as d:
        _seed_signals(d, "artemiy", [
            ("hero button component", "accepted"),
            ("nav bar footer", "accepted"),
            ("sidebar layout", "rejected"),
            ("modal dialog", "edited"),
        ])
        try:
            ctx = learning.build_learned_context("artemiy", min_samples=3)
            assert "[Learned from past usage]" in ctx
            assert "Acceptance rate" in ctx
            assert "n=4" in ctx
        finally:
            _restore_store()


def test_build_learned_context_meta_preferences():
    with tempfile.TemporaryDirectory() as d:
        _use_tmpdir(d)
        try:
            records = []
            for i in range(4):
                sid = f"meta_{i}"
                records.append(json.dumps({
                    "sid": sid, "ts": 0, "phase": "start",
                    "agent": "artemiy", "action": "component",
                    "spec": f"component {i}", "meta": {"framework": "react"},
                    "outcome": None,
                }))
                records.append(json.dumps({
                    "sid": sid, "ts": 1, "phase": "outcome",
                    "agent": "artemiy", "outcome": "accepted", "note": "",
                }))
            with open(_signal_mod.SIGNAL_FILE, "w") as f:
                f.write("\n".join(records) + "\n")
            ctx = learning.build_learned_context("artemiy", min_samples=3)
            assert "framework=react" in ctx
        finally:
            _restore_store()


def test_build_learned_context_wrong_agent_empty():
    with tempfile.TemporaryDirectory() as d:
        _seed_signals(d, "sherl", [
            ("query1", "accepted"),
            ("query2", "accepted"),
            ("query3", "rejected"),
        ])
        try:
            ctx = learning.build_learned_context("artemiy", min_samples=3)
            assert ctx == ""
        finally:
            _restore_store()


def test_capture_outcome_preserves_agent():
    """verify capture_outcome preserves agent field for read_signals filter."""
    with tempfile.TemporaryDirectory() as d:
        _use_tmpdir(d)
        try:
            sid = learning.capture_start("artemiy", "component", "hero")
            learning.capture_outcome(sid, "accepted")
            signals = learning.read_signals("artemiy")
            phases = [s["phase"] for s in signals]
            assert "start" in phases
            assert "outcome" in phases
        finally:
            _restore_store()


def test_build_learned_context_with_real_signals():
    """VERIFY build_learned_context() works with real capture/capture_outcome."""
    with tempfile.TemporaryDirectory() as d:
        _use_tmpdir(d)
        try:
            for _ in range(4):
                s = learning.capture_start("artemiy", "component", "button")
                learning.capture_outcome(s, "accepted")
            ctx = learning.build_learned_context("artemiy", min_samples=3)
            assert "acceptance" in ctx.lower()
            assert "artemiy" not in ctx  # shouldn"t leak agent name
        finally:
            _restore_store()
