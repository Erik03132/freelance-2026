"""Self-Learning Loop package.

Importable: `from learning import capture_start, capture_outcome, build_learned_context`.

Safe to import from any agent — if the package is unavailable, callers
should wrap imports in try/except (agents degrade gracefully).
"""

from .learner import build_learned_context
from .signal import capture_outcome, capture_start, read_signals

__all__ = [
    "capture_start",
    "capture_outcome",
    "read_signals",
    "build_learned_context",
]
