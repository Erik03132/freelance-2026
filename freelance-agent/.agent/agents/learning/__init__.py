"""Self-Learning Loop package.

Importable: `from learning import capture_start, capture_outcome, build_learned_context`.

Safe to import from any agent — if the package is unavailable, callers
should wrap imports in try/except (agents degrade gracefully).
"""

# Lazy imports to avoid issues when running as __main__
_build_learned_context = None
_capture_start = None
_capture_outcome = None
_read_signals = None


def _load():
    global _build_learned_context, _capture_start, _capture_outcome, _read_signals
    if _build_learned_context is None:
        from .learner import build_learned_context as _blc
        from .learning_signal import capture_outcome as _co, capture_start as _cs, read_signals as _rs
        _build_learned_context = _blc
        _capture_start = _cs
        _capture_outcome = _co
        _read_signals = _rs


def capture_start(agent: str, spec: str, meta: dict | None = None) -> str:
    _load()
    return _capture_start(agent, spec, meta)


def capture_outcome(agent: str, outcome: str, note: str = "") -> bool:
    _load()
    return _capture_outcome(agent, outcome, note)


def read_signals(agent: str | None = None):
    _load()
    return _read_signals(agent)


def build_learned_context(agent: str, min_samples: int = 3) -> str:
    _load()
    return _build_learned_context(agent, min_samples)


__all__ = [
    "capture_start",
    "capture_outcome",
    "read_signals",
    "build_learned_context",
]