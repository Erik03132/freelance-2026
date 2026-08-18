"""Eval for BK-4 per-task model profiles — offline, deterministic.

Запуск: python3 tools/tests/eval_model_profiles.py
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.model_profiles import (  # noqa: E402
    MODEL_PROFILES,
    GLOBAL_FALLBACK,
    select_model,
    select_chain,
)


def _run() -> tuple[int, list[str]]:
    fails: list[str] = []

    # TP-1: per-task выбор primary, когда все доступны (offline)
    m = select_model("translate")
    if m != MODEL_PROFILES["translate"][0]:
        fails.append(f"TP-1: translate должен дать primary, получили {m}")
    if select_model("edit") != MODEL_PROFILES["edit"][0]:
        fails.append("TP-1: edit primary mismatch")

    # TP-2: fallback вниз, когда primary недоступен
    avail = {"openrouter/google/gemini-flash-1.5", "openrouter/meta-llama/llama-3.3-70b-instruct"}
    m = select_model("translate", available=avail)  # deepseek-chat недоступен -> gemini
    if m != "openrouter/google/gemini-flash-1.5":
        fails.append(f"TP-2: translate fallback должен дать gemini, получили {m}")

    # TP-3: задача без профиля -> GLOBAL_FALLBACK primary
    m = select_model("unknown_task")
    if m != GLOBAL_FALLBACK[0]:
        fails.append(f"TP-3: unknown_task должен дать global fallback, получили {m}")

    # TP-4: ни одна модель профиля недоступна -> global fallback цепочка
    avail2 = {"openrouter/meta-llama/llama-3.3-70b-instruct"}
    m = select_model("translate", available=avail2)  # ни deepseek, ни gemini
    if m != "openrouter/meta-llama/llama-3.3-70b-instruct":
        fails.append(f"TP-4: translate должен уйти в global fallback, получили {m}")

    # TP-5: select_chain содержит профиль + global без дублей и в правильном порядке
    chain = select_chain("translate")  # offline -> все
    if chain[0] != MODEL_PROFILES["translate"][0]:
        fails.append(f"TP-5: chain[0] должен быть primary, получили {chain[0]}")
    if len(chain) != len(set(chain)):
        fails.append("TP-5: chain содержит дубли")

    return len(fails), fails


if __name__ == "__main__":
    n, fails = _run()
    if fails:
        print(f"❌ EVAL FAILED ({n}):")
        for f in fails:
            print(f"  - {f}")
        sys.exit(1)
    print(f"✅ EVAL PASSED — BK-4 per-task model profiles ({len(MODEL_PROFILES)} задач, fallback OK)")
