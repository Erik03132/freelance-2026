"""Eval for HZ-5 model benchmark harness — offline, deterministic.

Запуск: python3 tools/tests/eval_model_bench.py
Прогонять перед правками model_bench.py (правило №9).
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.model_bench import selftest  # noqa: E402


if __name__ == "__main__":
    sys.exit(selftest())
