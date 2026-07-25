#!/usr/bin/env python3
"""CLI for Learning Loop — capture_start, capture_outcome, context."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Make sibling modules importable
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from learning_signal import capture_start, capture_outcome, capture_outcome_latest, read_signals
from learner import build_learned_context


def main() -> int:
    parser = argparse.ArgumentParser(prog="learning", description="Learning loop CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # capture_start
    p_start = sub.add_parser("capture_start", help="Record task start signal")
    p_start.add_argument("--agent", required=True)
    p_start.add_argument("--spec", required=True)
    p_start.add_argument("--meta", default="{}", help="JSON metadata")

    # capture_outcome
    p_out = sub.add_parser("capture_outcome", help="Record task outcome")
    p_out.add_argument("--agent", required=True)
    p_out.add_argument("--outcome", required=True, choices=["accepted", "edited", "rejected"])

    # context
    p_ctx = sub.add_parser("context", help="Build learned context for prompt injection")
    p_ctx.add_argument("--agent", required=True)
    p_ctx.add_argument("--min-samples", type=int, default=3)

    args = parser.parse_args()

    if args.cmd == "capture_start":
        try:
            meta = json.loads(args.meta)
        except json.JSONDecodeError as e:
            print(f"Invalid --meta JSON: {e}", file=sys.stderr)
            return 1
        sid = capture_start(args.agent, args.spec, meta)
        print(sid)
        return 0

    if args.cmd == "capture_outcome":
        capture_outcome_latest(args.agent, args.outcome)
        print(f"Recorded {args.outcome} for {args.agent} (latest task)")
        return 0

    if args.cmd == "context":
        ctx = build_learned_context(args.agent, min_samples=args.min_samples)
        if ctx:
            print(ctx)
        else:
            print("(not enough data yet)")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())