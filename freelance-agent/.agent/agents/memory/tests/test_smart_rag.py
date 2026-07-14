"""Tests for smart RAG top-K retrieval (Chen mechanic #2).

Retrieve only the few most relevant facts (ranked), not the whole store.
"""

import os
import sys
import tempfile

import pytest

_AGENTS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _AGENTS not in sys.path:
    sys.path.insert(0, _AGENTS)

import memory  # noqa: E402
from memory import enrich_context  # noqa: E402
from memory import store as mem_store  # noqa: E402


@pytest.fixture
def tmp_store(monkeypatch):
    d = tempfile.mkdtemp()
    monkeypatch.setattr(mem_store, "STORE_DIR", d)
    return d


def test_recall_scored_empty_store(tmp_store):
    assert memory.recall_scored("ghost", "anything") == []


def test_recall_scored_returns_ranked_dicts(tmp_store):
    memory.remember("artemiy", "generated astro hero with gradient", kind="gen")
    memory.remember("artemiy", "generated react pricing table", kind="gen")
    memory.remember("artemiy", "fixed css layout shift", kind="fix")
    hits = memory.recall_scored("artemiy", "astro hero gradient", top_k=3)
    assert isinstance(hits, list)
    assert all(isinstance(h, dict) and "fact" in h and "score" in h for h in hits)
    # most relevant first
    assert "astro hero" in hits[0]["fact"]


def test_recall_scored_respects_top_k(tmp_store):
    for i in range(10):
        memory.remember("kulibin", f"optimized query pipeline step {i}", kind="fact")
    hits = memory.recall_scored("kulibin", "optimized query pipeline", top_k=3)
    assert len(hits) == 3


def test_recall_scored_min_score_filters(tmp_store):
    memory.remember("sherl", "competitor pricing data collected", kind="fact")
    memory.remember("sherl", "totally unrelated banana content", kind="fact")
    hits = memory.recall_scored("sherl", "competitor pricing", top_k=5, min_score=0.1)
    facts = [h["fact"] for h in hits]
    assert any("competitor pricing" in f for f in facts)
    assert not any("banana" in f for f in facts)


def test_recall_string_backward_compat(tmp_store):
    memory.remember("rembrandt", "designed warm palette hero", kind="fact")
    out = memory.recall("rembrandt", "warm palette")
    assert isinstance(out, str)
    assert "warm palette" in out


def test_enrich_context_actually_injects_memory(tmp_store):
    memory.remember("artemiy", "user favors astro over next", kind="pref")
    ctx = enrich_context("artemiy", "build an astro landing", ctx="")
    assert "astro" in ctx.lower()
    assert ctx != ""


def test_enrich_context_merges_with_base_ctx(tmp_store):
    memory.remember("artemiy", "prefers vanilla css", kind="pref")
    ctx = enrich_context("artemiy", "vanilla css component", ctx="BASE_LEARNED")
    assert "BASE_LEARNED" in ctx
    assert "vanilla css" in ctx.lower()


def test_enrich_context_no_memory_returns_base(tmp_store):
    ctx = enrich_context("artemiy", "nothing stored here", ctx="ONLY_BASE")
    assert ctx == "ONLY_BASE"
