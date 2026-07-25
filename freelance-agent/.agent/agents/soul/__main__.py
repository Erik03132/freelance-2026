#!/usr/bin/env python3
"""CLI for Soul — scaffold, read, fold, replace_auto_zone."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SOUL_DIR = Path(__file__).parent
sys.path.insert(0, str(SOUL_DIR))

from store import scaffold, read, fold, replace_auto_zone


def main() -> int:
    parser = argparse.ArgumentParser(prog="soul", description="Soul CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_new = sub.add_parser("scaffold", help="Create new soul file")
    p_new.add_argument("agent", help="Agent name (sherlock, shakespeare, etc.)")
    p_new.add_argument("role", help="Role description")

    p_read = sub.add_parser("read", help="Print soul file")
    p_read.add_argument("agent", help="Agent name")

    p_fold = sub.add_parser("fold", help="Append lesson to AUTO zone")
    p_fold.add_argument("agent", help="Agent name")
    p_fold.add_argument("lesson", help="Lesson text")

    p_replace = sub.add_parser("replace", help="Replace AUTO zone entirely")
    p_replace.add_argument("agent", help="Agent name")
    p_replace.add_argument("content", help="New AUTO zone content")

    args = parser.parse_args()

    if args.cmd == "scaffold":
        path = scaffold(args.agent, args.role)
        print(f"Created {path}")
        return 0

    if args.cmd == "read":
        content = read(args.agent)
        if content:
            print(content)
        else:
            print(f"No soul file for {args.agent}", file=sys.stderr)
        return 0

    if args.cmd == "fold":
        fold(args.agent, args.lesson)
        print(f"Folded lesson into {args.agent}.soul.md")
        return 0

    if args.cmd == "replace":
        replace_auto_zone(args.agent, args.content)
        print(f"Replaced AUTO zone in {args.agent}.soul.md")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())