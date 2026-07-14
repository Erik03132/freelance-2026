"""Tests for the Soul module — self-editable agent constitution (soul.md).

Inspired by Shen Shon Chen's "soul.md governs everything" self-improving agent talk.
"""

import os
import sys
import tempfile

import pytest

_AGENTS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _AGENTS not in sys.path:
    sys.path.insert(0, _AGENTS)

import soul  # noqa: E402
from soul import store as soul_store  # noqa: E402


@pytest.fixture
def tmp_soul(monkeypatch):
    """Point the soul store at a temp dir so tests never touch real soul.md files."""
    d = tempfile.mkdtemp()
    monkeypatch.setattr(soul_store, "SOUL_DIR", d)
    return d


def test_missing_soul_returns_empty(tmp_soul):
    assert soul.load_soul("ghost") == ""
    assert soul.soul_context("ghost") == ""


def test_ensure_creates_scaffold_with_zones(tmp_soul):
    path = soul.ensure_soul("artemiy", "Артемий", "Frontend agent")
    assert os.path.exists(path)
    text = soul.load_soul("artemiy")
    assert "## Constitution" in text
    assert "## Evolving Lessons" in text
    assert soul_store.AUTO_BEGIN in text
    assert soul_store.AUTO_END in text


def test_ensure_is_idempotent(tmp_soul):
    p1 = soul.ensure_soul("kulibin", "Кулибин", "Engineer")
    with open(p1, "a", encoding="utf-8") as f:
        f.write("\nhuman edit\n")
    p2 = soul.ensure_soul("kulibin", "Кулибин", "Engineer")
    assert p1 == p2
    assert "human edit" in soul.load_soul("kulibin")


def test_soul_context_includes_constitution(tmp_soul):
    soul.ensure_soul("sherl", "Шерлок", "Research agent")
    ctx = soul.soul_context("sherl")
    assert "Research agent" in ctx or "Шерлок" in ctx


def test_evolve_folds_lessons_into_auto_zone(tmp_soul):
    soul.ensure_soul("rembrandt", "Рембрандт", "Designer")
    changed = soul.evolve_soul("rembrandt", lessons="- Users favor framework=astro\n- Acceptance 80%")
    assert changed is True
    text = soul.load_soul("rembrandt")
    assert "framework=astro" in text
    assert "Acceptance 80%" in text


def test_evolve_only_touches_auto_zone(tmp_soul):
    soul.ensure_soul("rembrandt", "Рембрандт", "Designer")
    before = soul.load_soul("rembrandt")
    const_marker = "## Constitution"
    soul.evolve_soul("rembrandt", lessons="- New lesson")
    after = soul.load_soul("rembrandt")
    # Constitution section text preserved
    const_before = before.split(soul_store.AUTO_BEGIN)[0]
    const_after = after.split(soul_store.AUTO_BEGIN)[0]
    assert const_before == const_after
    assert const_marker in const_after


def test_evolve_replaces_previous_lessons(tmp_soul):
    soul.ensure_soul("rembrandt", "Рембрандт", "Designer")
    soul.evolve_soul("rembrandt", lessons="- Old lesson")
    soul.evolve_soul("rembrandt", lessons="- Fresh lesson")
    text = soul.load_soul("rembrandt")
    assert "Fresh lesson" in text
    assert "Old lesson" not in text


def test_evolve_empty_lessons_noop(tmp_soul):
    soul.ensure_soul("rembrandt", "Рембрандт", "Designer")
    assert soul.evolve_soul("rembrandt", lessons="") is False


def test_evolve_missing_soul_returns_false(tmp_soul):
    assert soul.evolve_soul("nobody", lessons="- x") is False


def test_soul_context_respects_max_chars(tmp_soul):
    soul.ensure_soul("artemiy", "Артемий", "Frontend " * 500)
    ctx = soul.soul_context("artemiy", max_chars=200)
    assert len(ctx) <= 200
