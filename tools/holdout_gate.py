#!/usr/bin/env python3
"""RSI-002 — сейф: гейт закрытого набора (holdout).

Проблема, которую решает: у нас агент сам пишет eval и сам по нему проверяется —
классическая петля закона Гудхарта. Holdout — набор, которого оптимизатор не видит;
прогоняется только на приёмке.

Правила:
  * holdout-кейсы лежат в `<любой>/tests/holdout/*.jsonl`, `split: "holdout"`;
  * у каждого кейса обязателен `reviewed_by` (набор пишет человек, не агент);
  * пустой сейф — это ПРОВАЛ громко, а не «зелёный» результат.

Использование:
  python3 tools/holdout_gate.py                 # проверить сейф
  python3 tools/holdout_gate.py --dry-run       # только перечислить файлы
  python3 tools/holdout_gate.py --root . --min 5
  python3 tools/holdout_gate.py --help

Коды выхода: 0 — сейф непуст и валиден; 1 — пуст или есть ошибки; 2 — ошибка запуска.
"""

from __future__ import annotations

import argparse
import os
import sys

ROOT_DEFAULT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DEFAULT not in sys.path:
    sys.path.insert(0, ROOT_DEFAULT)

from tools.rag_evalset import load_eval_set, validate_case  # noqa: E402

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".next", "dist", "build"}
HOLDOUT_DIRNAME = "holdout"


def find_holdout_files(root: str) -> list[str]:
    """Все `*/tests/holdout/*.jsonl` под root (без обхода мусорных каталогов)."""
    found: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".cache")]
        if os.path.basename(dirpath) != HOLDOUT_DIRNAME:
            continue
        if os.path.basename(os.path.dirname(dirpath)) != "tests":
            continue
        for name in sorted(filenames):
            if name.endswith(".jsonl"):
                found.append(os.path.join(dirpath, name))
    return sorted(found)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="holdout_gate.py",
        description="RSI-002: гейт закрытого eval-набора (holdout). Пустой сейф = провал.",
        epilog=(
            "Примеры:\n"
            "  python3 tools/holdout_gate.py\n"
            "  python3 tools/holdout_gate.py --root . --min 5 --dry-run\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "--root", default=ROOT_DEFAULT, help="корень поиска (по умолчанию — корень репо)"
    )
    ap.add_argument("--min", type=int, default=1, help="минимум кейсов в сейфе (по умолчанию 1)")
    ap.add_argument(
        "--dry-run", action="store_true", help="только перечислить файлы, без валидации"
    )
    args = ap.parse_args(argv)

    if not os.path.isdir(args.root):
        print(f"❌ --root '{args.root}' не каталог", file=sys.stderr)
        return 2

    files = find_holdout_files(args.root)
    if args.dry_run:
        print(f"holdout: найдено файлов {len(files)}")
        for f in files:
            print(f"  {os.path.relpath(f, args.root)}")
        return 0

    if not files:
        print("❌ HOLDOUT GATE FAILED: сейф пуст — ни одного */tests/holdout/*.jsonl.")
        print("   Сейф не может быть пустым: без закрытого набора агент проверяет сам себя.")
        print("   Что делать: человек пишет кейсы (split=holdout, reviewed_by=<кто>) в")
        print("   tests/holdout/ — см. tools/tests/holdout/README.md.")
        return 1

    total = 0
    problems: list[str] = []
    for path in files:
        rel = os.path.relpath(path, args.root)
        try:
            all_cases = load_eval_set(path)
        except (ValueError, KeyError) as exc:
            problems.append(f"{rel}: не читается — {exc}")
            continue
        leaked = [c.id for c in all_cases if c.split != "holdout"]
        if leaked:
            problems.append(f"{rel}: кейсы вне holdout в закрытом файле — {', '.join(leaked)}")
        cases = [c for c in all_cases if c.split == "holdout"]
        total += len(cases)
        for case in cases:
            for err in validate_case(case):
                problems.append(f"{rel} :: {case.id}: {err}")
        print(f"  {rel}: holdout-кейсов {len(cases)}")

    print("---")
    if problems:
        print(f"❌ HOLDOUT GATE FAILED: {len(problems)} проблем(ы)")
        for p in problems:
            print(f"   - {p}")
        return 1
    if total < args.min:
        print(f"❌ HOLDOUT GATE FAILED: кейсов {total}, требуется минимум {args.min}")
        return 1
    print(f"✅ HOLDOUT GATE PASSED: {total} утверждённых кейсов в {len(files)} файле(ах)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
