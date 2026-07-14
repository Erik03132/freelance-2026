"""Tests for memory compaction (Chen mechanic #5 — auto-compress memory)."""

import json
import os
import sys
import tempfile

import pytest

_AGENTS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _AGENTS not in sys.path:
    sys.path.insert(0, _AGENTS)

import memory  # noqa: E402
from memory import store as mem_store  # noqa: E402


@pytest.fixture
def tmp_store(monkeypatch):
    d = tempfile.mkdtemp()
    monkeypatch.setattr(mem_store, "STORE_DIR", d)
    return d


def _count_lines(path):
    with open(path, encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def test_compact_missing_store_noop(tmp_store):
    stats = memory.compact("ghost")
    assert stats["before"] == 0
    assert stats["after"] == 0
    assert stats["removed"] == 0


def test_compact_dedupes_identical_facts(tmp_store):
    for _ in range(5):
        memory.remember("artemiy", "generated astro hero", kind="generation")
    memory.remember("artemiy", "generated react card", kind="generation")
    stats = memory.compact("artemiy")
    assert stats["before"] == 6
    assert stats["after"] == 2
    assert stats["removed"] == 4
    path = mem_store._store_path("artemiy")
    assert _count_lines(path) == 2


def test_compact_preserves_recall(tmp_store):
    memory.remember("sherl", "found pricing for competitor X", kind="fact")
    memory.remember("sherl", "found pricing for competitor X", kind="fact")
    memory.compact("sherl")
    hits = memory.recall("sherl", "pricing competitor")
    assert "competitor" in hits.lower()


def test_compact_keeps_most_recent_when_over_limit(tmp_store):
    for i in range(10):
        memory.remember("kulibin", f"unique fact number {i}", kind="fact")
    stats = memory.compact("kulibin", keep=3)
    assert stats["after"] == 3
    path = mem_store._store_path("kulibin")
    facts = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                facts.append(json.loads(line)["fact"])
    # newest kept
    assert "unique fact number 9" in facts
    assert "unique fact number 0" not in facts


def test_compact_dedupe_keeps_latest_timestamp(tmp_store):
    memory.remember("rembrandt", "same fact", kind="fact")
    memory.remember("rembrandt", "same fact", kind="fact")
    stats = memory.compact("rembrandt")
    assert stats["after"] == 1
    assert stats["removed"] == 1
