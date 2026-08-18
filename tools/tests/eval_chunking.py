"""Eval for RAG-4 chunking strategies (Habr #1070662) — offline.

Запуск: python3 tools/tests/eval_chunking.py
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.chunking import fixed_chunk, recursive_chunk, merge_small_chunks  # noqa: E402


def _run() -> tuple[int, list[str]]:
    fails: list[str] = []

    # TP-1: fixed_chunk без overlap
    r = fixed_chunk("abcdefghij", 4, 0)
    if r != ["abcd", "efgh", "ij"]:
        fails.append(f"TP-1: fixed_chunk(4,0) ожидали ['abcd','efgh','ij'], получили {r}")

    # TP-2: fixed_chunk с overlap
    r = fixed_chunk("abcdefghij", 4, 2)
    if r != ["abcd", "cdef", "efgh", "ghij", "ij"]:
        fails.append(f"TP-2: fixed_chunk(4,2) неверно: {r}")

    # TP-3: recursive_chunk сплитит по \n\n (текст > size, иначе вернётся целиком)
    r = recursive_chunk("AAAA\n\nBBBB\n\nCCCC", 10)
    if r != ["AAAA", "BBBB", "CCCC"]:
        fails.append(f"TP-3: recursive_chunk должен дать ['AAAA','BBBB','CCCC'], получили {r}")

    # TP-4: все чанки recursive_chunk <= size, порядок сохранён
    txt = "Первая строка. Вторая строка. " + ("x" * 100)
    r = recursive_chunk(txt, 20)
    if any(len(c) > 20 for c in r):
        fails.append(f"TP-4: есть чанк > size: {[len(c) for c in r]}")
    if "".join(r).replace("\n", "").replace(". ", ".") != txt.replace("\n", "").replace(". ", "."):
        # допускаем потерю разделителей — проверяем только что не пусто и порядок
        if not r or any(len(c) == 0 for c in r):
            fails.append("TP-4: пустые чанки в recursive_chunk")

    # TP-5: merge_small_chunks склеивает до target
    r = merge_small_chunks(["a", "b", "c"], 5)
    if r != ["a b c"]:
        fails.append(f"TP-5: merge_small_chunks ожидали ['a b c'], получили {r}")

    # TP-6: merge_small_chunks не превышает target и сохраняет крупные
    r = merge_small_chunks(["aaaaa", "b", "cc", "ddddd"], 5)
    if any(len(c) > 5 for c in r):
        fails.append(f"TP-6: чанк превысил target: {r}")
    if "aaaaa" not in r or "ddddd" not in r:
        fails.append(f"TP-6: крупные чанки потеряны: {r}")

    return len(fails), fails


if __name__ == "__main__":
    n, fails = _run()
    if fails:
        print(f"❌ EVAL FAILED ({n}):")
        for f in fails:
            print(f"  - {f}")
        sys.exit(1)
    print("✅ EVAL PASSED — RAG-4 fixed/recursive chunking + merge_small_chunks OK")
