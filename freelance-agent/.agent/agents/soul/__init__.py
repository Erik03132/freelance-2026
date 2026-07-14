"""Soul — self-editable agent constitution (soul.md).

A single living file governs each agent (Shen Shon Chen pattern):
- Constitution zone: human-owned identity & hard rules.
- Evolving Lessons zone: machine-owned, folded from learning + memory.

Importable: `from soul import load_soul, soul_context, ensure_soul, evolve_soul`.
Degrades gracefully — wrap imports in try/except in callers.
"""

from __future__ import annotations

from . import store

__all__ = ["load_soul", "soul_context", "ensure_soul", "evolve_soul"]


def load_soul(agent: str) -> str:
    """Return the full soul.md text, or '' if the agent has no soul yet."""
    return store.read(agent)


def ensure_soul(agent: str, name: str = "", role: str = "") -> str:
    """Create a scaffold soul.md if missing. Idempotent. Returns the path."""
    path = store.soul_path(agent)
    if not store.read(agent):
        store.write(agent, store.scaffold(name or agent, role))
    return path


def soul_context(agent: str, max_chars: int = 1500) -> str:
    """Return the soul as an injectable context string (trimmed to max_chars)."""
    text = store.read(agent)
    if not text:
        return ""
    return text[:max_chars]


def evolve_soul(agent: str, lessons: str) -> bool:
    """Fold fresh `lessons` into the Evolving Lessons auto-zone (self-edit).

    Returns True if the soul was updated, False if no soul exists or no lessons.
    """
    if not lessons or not lessons.strip():
        return False
    text = store.read(agent)
    if not text:
        return False
    updated = store.replace_auto_zone(text, lessons)
    if updated == text:
        return False
    store.write(agent, updated)
    return True
