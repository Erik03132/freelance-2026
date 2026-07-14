"""🔧 Kulibin — Engineering Agent (LLM-CLI).

Запуск: python3 -m kulibin [opts]
Инженерный аудит кода (Python/JS/TS), поиск библиотек, генерация PoC.

Использование:
    python3 -m kulibin --audit ./src
    python3 -m kulibin --scout "rate limiting in FastAPI"
    python3 -m kulibin --proto "in-memory cache with TTL"
"""

import argparse
import os
import sys

# Make sibling `learning` package importable regardless of cwd
_AGENTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _AGENTS not in sys.path:
    sys.path.insert(0, _AGENTS)
try:
    from learning import build_learned_context, capture_outcome, capture_start
except ImportError:
    def build_learned_context(agent, min_samples=3):
        return ""
    def capture_start(*a, **k):
        return ""
    def capture_outcome(*a, **k):
        return False

try:
    from .security_audit import security_audit as _sec_scan, owasp_audit as _owasp_audit
except ImportError:
    def _sec_scan(path):
        return {"files_scanned": 0, "issues_by_file": {}, "summary": {}}
    def _owasp_audit(path, api_key=None, learned_context=""):
        return None

try:
    from memory import compact as mem_compact, enrich_context, recall, remember
except ImportError:
    def enrich_context(agent, query, ctx="", top_k=2):
        return ctx
    def recall(agent, query, top_k=3):
        return []
    def remember(agent, fact, kind):
        pass
    def mem_compact(agent, keep=500):
        return {"before": 0, "after": 0, "removed": 0}

try:
    from soul import ensure_soul, evolve_soul, soul_context
except ImportError:
    def ensure_soul(agent, name="", role=""):
        return ""
    def evolve_soul(agent, lessons):
        return False
    def soul_context(agent, max_chars=1500):
        return ""

AGENT = "kulibin"
_base_learned = build_learned_context


def build_learned_context(agent, min_samples=3):  # noqa: F811 — wrap to inject soul
    base = _base_learned(agent, min_samples)
    s = soul_context(agent)
    if s:
        return s + ("\n\n" + base if base else "")
    return base

from . import (
    EVAL_CRITERIA,
    LANGUAGES,
    analyze,
    benchmark_snippet,
    deep_audit,
    evaluate,
    generate_prototype,
    scout,
)


def _save(name: str, content: str) -> str:
    out = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def main():
    parser = argparse.ArgumentParser(
        description="🔧 Kulibin — Engineering Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
        "  python3 -m kulibin --audit ./src\n"
        "  python3 -m kulibin --scout 'image optimization pipeline'\n"
        "  python3 -m kulibin --proto 'WebSocket reconnect with backoff'\n",
    )
    parser.add_argument("--audit", "-a", type=str, default=None,
                        help="Static analysis of a file/dir (Python/JS/TS)")
    parser.add_argument("--deep-audit", type=str, default=None,
                        help="LLM deep audit (requires OpenRouter key)")
    parser.add_argument("--scout", "-s", type=str, default=None,
                        help="Recommend libraries for a task")
    parser.add_argument("--evaluate", "-e", type=str, default=None,
                        help="Evaluate a specific library")
    parser.add_argument("--proto", "-p", type=str, default=None,
                        help="Generate a proof-of-concept")
    parser.add_argument("--lang", type=str, default="python",
                        choices=LANGUAGES, help="Language for --proto")
    parser.add_argument("--benchmark", "-b", type=str, default=None,
                        help="Benchmark suggestions for a code snippet file")
    parser.add_argument("--list-languages", action="store_true",
                        help="List supported languages")
    parser.add_argument("--list-criteria", action="store_true",
                        help="List library evaluation criteria")
    parser.add_argument("--sec-audit", type=str, default=None,
                        help="Static security audit (leaks/OWASP smells)")
    parser.add_argument("--owasp", type=str, default=None,
                        help="LLM OWASP review (requires OpenRouter key)")
    parser.add_argument("--feedback", type=str, default=None, nargs=2,
                        metavar=("SID", "OUTCOME"),
                        help="Record verdict for a signal: --feedback <sid> accepted|edited|rejected")

    args = parser.parse_args()

    ensure_soul(AGENT, "Кулибин", "Engineer — Performance & Innovation")

    if args.feedback:
        sid, outcome = args.feedback
        ok = capture_outcome(sid, outcome)
        print(f"{'✅' if ok else '❌'} Feedback '{outcome}' recorded for {sid}")
        if ok:
            lessons = _base_learned(AGENT)
            if lessons and evolve_soul(AGENT, lessons):
                print(f"🧬 Soul evolved: folded fresh lessons into {AGENT}.soul.md")
        _stats = mem_compact(AGENT)
        if _stats["removed"]:
            print(f"🗜️  Memory compacted: {_stats['before']}→{_stats['after']} (-{_stats['removed']})")
        return

    if args.sec_audit:
        print(f"🔧 Security audit: {args.sec_audit}")
        ctx = enrich_context("kulibin", args.sec_audit, build_learned_context("kulibin"))
        sid = capture_start("kulibin", "security_audit", args.sec_audit)
        res = _sec_scan(args.sec_audit)
        print(f"Files: {res['files_scanned']}")
        if res["summary"]:
            print("Leak summary:")
            for name, n in res["summary"].items():
                print(f"  ⚠ {name}: {n}")
        else:
            print("✅ No obvious leaks")
        print(f"📡 Signal {sid} logged — later: python3 -m kulibin --feedback {sid} accepted|edited|rejected")
        return

    if args.owasp:
        print(f"🔧 OWASP review: {args.owasp}")
        ctx = enrich_context("kulibin", args.owasp, build_learned_context("kulibin"))
        sid = capture_start("kulibin", "owasp_audit", args.owasp)
        report = _owasp_audit(args.owasp, learned_context=ctx)
        if report:
            path = _save("owasp_report.md", report)
            print(f"✅ Saved to {path}")
            print(f"📡 Signal {sid} logged — later: python3 -m kulibin --feedback {sid} accepted|edited|rejected")
        else:
            print("❌ LLM unavailable")
            sys.exit(1)
        return

    if args.list_languages:
        print("Supported languages:", ", ".join(LANGUAGES))
        return
    if args.list_criteria:
        print("Evaluation criteria:")
        for c in EVAL_CRITERIA:
            print(f"  - {c}")
        return

    if args.audit:
        print(f"🔧 Analyzing {args.audit}")
        result = analyze(args.audit)
        print(f"Files: {result['files_scanned']} | By lang: {result['by_language']}")
        if result["smells"]:
            print("Smells:")
            for name, n in result["smells"].items():
                print(f"  ⚠ {name}: {n}")
        else:
            print("✅ No obvious smells")
        return

    if args.deep_audit:
        print(f"🔧 Deep auditing {args.deep_audit}")
        ctx = enrich_context("kulibin", args.deep_audit, build_learned_context("kulibin"))
        sid = capture_start("kulibin", "deep_audit", args.deep_audit)
        report = deep_audit(args.deep_audit, learned_context=ctx)
        if report:
            path = _save("audit_report.md", report)
            print(f"✅ Saved to {path}")
            print(f"📡 Signal {sid} logged — later: python3 -m kulibin --feedback {sid} accepted|edited|rejected")
        else:
            print("❌ LLM unavailable")
            sys.exit(1)
        return

    if args.scout:
        print(f"🔧 Scouting: {args.scout}")
        ctx = enrich_context("kulibin", args.scout, build_learned_context("kulibin"))
        sid = capture_start("kulibin", "scout", args.scout)
        out = scout(args.scout, learned_context=ctx)
        if out:
            path = _save("scout.md", out)
            print(f"✅ Saved to {path}")
            print(f"📡 Signal {sid} logged — later: python3 -m kulibin --feedback {sid} accepted|edited|rejected")
        else:
            print("❌ LLM unavailable")
            sys.exit(1)
        return

    if args.evaluate:
        print(f"🔧 Evaluating: {args.evaluate}")
        ctx = enrich_context("kulibin", args.evaluate, build_learned_context("kulibin"))
        sid = capture_start("kulibin", "evaluate", args.evaluate)
        out = evaluate(args.evaluate, learned_context=ctx)
        if out:
            path = _save("evaluate.md", out)
            print(f"✅ Saved to {path}")
            print(f"📡 Signal {sid} logged — later: python3 -m kulibin --feedback {sid} accepted|edited|rejected")
        else:
            print("❌ LLM unavailable")
            sys.exit(1)
        return

    if args.proto:
        print(f"🔧 Prototyping ({args.lang}): {args.proto}")
        ctx = enrich_context("kulibin", args.proto, build_learned_context("kulibin"))
        sid = capture_start("kulibin", "generate_prototype", args.proto, {"lang": args.lang})
        out = generate_prototype(args.proto, args.lang, learned_context=ctx)
        if out:
            ext = "py" if args.lang == "python" else ("ts" if args.lang == "ts" else "js")
            path = _save(f"prototype.{ext}", out)
            print(f"✅ Saved to {path}")
            print(f"📡 Signal {sid} logged — later: python3 -m kulibin --feedback {sid} accepted|edited|rejected")
        else:
            print("❌ LLM unavailable")
            sys.exit(1)
        return

    if args.benchmark:
        print(f"🔧 Benchmarking {args.benchmark}")
        try:
            with open(args.benchmark, encoding="utf-8") as f:
                code = f.read()
        except Exception as e:
            print(f"❌ {e}")
            sys.exit(1)
        ctx = enrich_context("kulibin", args.benchmark, build_learned_context("kulibin"))
        sid = capture_start("kulibin", "benchmark", args.benchmark)
        out = benchmark_snippet(code, learned_context=ctx)
        if out:
            path = _save("benchmark.md", out)
            print(f"✅ Saved to {path}")
            print(f"📡 Signal {sid} logged — later: python3 -m kulibin --feedback {sid} accepted|edited|rejected")
        else:
            print("❌ LLM unavailable")
            sys.exit(1)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
