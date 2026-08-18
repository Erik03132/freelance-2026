"""Eval for BK-2 layered context — offline, deterministic.

Запуск: python3 tools/tests/eval_context_layers.py
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.context_layers import LayeredContext, LAYERS  # noqa: E402


def _run() -> tuple[int, list[str]]:
    fails: list[str] = []

    # TP-1: 5 слоёв инициализируются пустыми
    ctx = LayeredContext()
    if set(ctx.layers) != set(LAYERS):
        fails.append(f"TP-1: слои не совпадают: {ctx.layers}")
    if ctx.total_items() != 0:
        fails.append("TP-1: пустой контекст должен быть 0 items")

    # TP-2: add раскладывает по слоям
    ctx.add("work", "вызвал lookup_order(123)")
    ctx.add("story", "пользователь ищет статус заказа")
    r = ctx.render()
    if r["work"]["entries"] != ["вызвал lookup_order(123)"]:
        fails.append(f"TP-2: work entries неверны: {r['work']['entries']}")
    if r["story"]["entries"] != ["пользователь ищет статус заказа"]:
        fails.append("TP-2: story entries неверны")

    # TP-3: compact сворачивает слой в конспект и очищает записи
    ctx.add("work", "вызвал render()")
    d = ctx.compact("work")
    if "summary of 2 items" not in d:
        fails.append(f"TP-3: digest не содержит сводку: {d}")
    if ctx.render()["work"]["entries"] != []:
        fails.append("TP-3: после compact записи должны очиститься")
    if ctx.render()["work"]["digests"] != [d]:
        fails.append("TP-3: digest не сохранён в digests")

    # TP-4: auto-compact по threshold
    low = LayeredContext(threshold=3)
    for i in range(3):
        low.add("work", f"step {i}")
    # после 3-й записи сработал auto-compact
    if low.render()["work"]["entries"] != []:
        fails.append("TP-4: auto-compact не сработал при threshold")
    if not low.render()["work"]["digests"]:
        fails.append("TP-4: auto-compact не оставил digest")

    # TP-5: неизвестный слой -> KeyError
    try:
        ctx.add("nope", "x")
        fails.append("TP-5: неизвестный слой должен бросать KeyError")
    except KeyError:
        pass

    return len(fails), fails


if __name__ == "__main__":
    n, fails = _run()
    if fails:
        print(f"❌ EVAL FAILED ({n}):")
        for f in fails:
            print(f"  - {f}")
        sys.exit(1)
    print(f"✅ EVAL PASSED — BK-2 layered context ({len(LAYERS)} слоёв, compact OK)")
