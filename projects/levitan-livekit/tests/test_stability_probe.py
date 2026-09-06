"""Тесты нагрузочного probe гейта стабильности (AVM-0b).

Запуск: python3 -m pytest tests/test_stability_probe.py -v
"""

import importlib.util
import os
import sys

AGENT_DIR = os.path.join(os.path.dirname(__file__), "..", "agent")
sys.path.insert(0, os.path.abspath(AGENT_DIR))

_spec = importlib.util.spec_from_file_location(
    "stability_probe", os.path.join(AGENT_DIR, "stability_probe.py")
)
sp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sp)


def test_classify_ok():
    code, bucket = sp.classify(200, None)
    assert bucket == "ok" and code == "200"


def test_classify_402():
    code, bucket = sp.classify(402, "pay")
    assert bucket == "402"


def test_classify_429():
    code, bucket = sp.classify(429, "rate")
    assert bucket == "429"


def test_classify_502():
    code, bucket = sp.classify(502, "bad gateway")
    assert bucket == "502"


def test_classify_timeout_none():
    code, bucket = sp.classify(None, "conn")
    assert bucket == "other" and code == "timeout_or_connerr"


def test_classify_other_5xx():
    code, bucket = sp.classify(500, "err")
    assert bucket == "other"


def test_questions_pool_nonempty():
    assert len(sp.PROBE_QUESTIONS) >= 5


def test_build_body_shape():
    body, q = sp.build_body("free-cascade")
    assert body["model"] == "free-cascade"
    assert any(m["role"] == "user" and m["content"] == q for m in body["messages"])
    assert q in sp.PROBE_QUESTIONS


def test_summarize_gate_pass():
    args = type("A", (), {"min_success_rate": 0.95, "base_url": "x", "model": "y"})()
    results = [{"bucket": "ok"} for _ in range(19)] + [{"bucket": "429"}]
    s = sp.summarize(results, args)
    assert s["total"] == 20
    assert s["success_rate"] == 0.95
    assert s["gate_pass"] is True


def test_summarize_gate_fail():
    args = type("A", (), {"min_success_rate": 0.95, "base_url": "x", "model": "y"})()
    results = [{"bucket": "ok"} for _ in range(17)] + [
        {"bucket": "502"},
        {"bucket": "429"},
        {"bucket": "timeout_or_connerr"},
    ]
    s = sp.summarize(results, args)
    assert s["success_rate"] == 0.85
    assert s["gate_pass"] is False
