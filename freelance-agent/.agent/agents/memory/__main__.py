#!/usr/bin/env python3
"""CLI for Memory — remember, recall, compact."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from store import remember, recall, recall_scored, compact


def main() -> int:
    parser = argparse.ArgumentParser(prog="memory", description="Agent memory CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_rem = sub.add_parser("remember", help="Store a fact")
    p_rem.add_argument("agent", help="Agent name")
    p_rem.add_argument("fact", help="Fact text")
    p_rem.add_argument("--kind", default="fact", choices=["fact", "preference", "pattern", "mistake"])

    p_rec = sub.add_parser("recall", help="Retrieve relevant facts")
    p_rec.add_argument("agent", help="Agent name")
    p_rec.add_argument("query", help="Search query")
    p_rec.add_argument("--top", type=int, default=5)

    p_com = sub.add_parser("compact", help="Deduplicate & summarize")
    p_com.add_argument("agent", help="Agent name")
    p_com.add_argument("--keep", type=int, default=500)

    args = parser.parse_args()

    if args.cmd == "remember":
        remember(args.agent, args.fact, args.kind)
        print(f"Remembered [{args.kind}] for {args.agent}")
        return 0

    if args.cmd == "recall":
        facts = recall_scored(args.agent, args.query, top_k=args.top)
        if facts:
            for i, f in enumerate(facts, 1):
                print(f"{i}. [{f.get('kind','fact')}] {f['fact']} (score: {f.get('score', 0):.2f})")
        else:
            print("(no matching facts)")
        return 0

    if args.cmd == "compact":
        result = compact(args.agent, keep=args.keep)
        print(f"Compacted {args.agent}: {result['before']} -> {result['after']} entries (removed {result['removed']})")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())