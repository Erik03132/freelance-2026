"""🔨 Artemiy — Frontend Agent (LLM-CLI).

Запуск: python3 -m artemiy [opts]
Генерация фронтенда мирового уровня: компоненты, страницы, аудит.
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
    from security import scan_leaks
except ImportError:
    def scan_leaks(code):
        return []

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

try:
    from healing import run_with_healing
except ImportError:
    run_with_healing = None


AGENT = "artemiy"


def _ctx(query: str) -> str:
    """Soul constitution + learned context + memory recall, merged for the prompt."""
    base = build_learned_context(AGENT)
    soul = soul_context(AGENT)
    if soul:
        base = soul + ("\n\n" + base if base else "")
    return enrich_context(AGENT, query, base)


def _validate_frontend(out) -> list:
    """Deterministic quality gate for generated frontend output."""
    issues = []
    if not out or not str(out).strip():
        return ["output is empty"]
    low = str(out).lower()
    if "llm unavailable" in low:
        return []  # offline fallback template is acceptable, don't loop
    leaks = scan_leaks(str(out))
    if leaks:
        issues.append(f"remove leaked secrets: {', '.join(leaks)}")
    if "<" not in str(out):
        issues.append("output must contain markup (no HTML/JSX tags found)")
    return issues

from . import (
    COMPONENT_TYPES,
    DEFAULTS,
    FRAMEWORKS,
    audit_code,
    audit_file,
    audit_with_llm,
    generate_component,
    generate_page,
    generate_scaffold,
)


def _save(name: str, content: str) -> str:
    out = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def _ext(framework: str) -> str:
    return {"astro": "astro", "react": "tsx", "vanilla": "html"}[framework]


def _guard(code: str, sid: str) -> None:
    """Security guardrail: warn on leaked secrets/.env in generated output."""
    leaks = scan_leaks(code)
    if leaks:
        print(f"⚠️  SECURITY GUARD: possible leak(s) in output: {', '.join(leaks)}")
        print("   Move secrets to server-side / env proxy; never ship keys to frontend.")
        capture_start("artemiy", "leak_detected", f"signal {sid}", {"issues": leaks})


def main():
    parser = argparse.ArgumentParser(
        description="🔨 Artemiy — Frontend Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
        "  python3 -m artemiy --component hero --framework astro --spec 'Gradient hero with CTA'\n"
        "  python3 -m artemiy --page 'Landing for eco-farm'\n"
        "  python3 -m artemiy --audit index.html\n",
    )

    parser.add_argument("--component", "-c", type=str, default=None,
                        choices=COMPONENT_TYPES + [None],
                        help=f"Component type ({', '.join(COMPONENT_TYPES)})")
    parser.add_argument("--page", "-p", type=str, default=None,
                        help="Generate a full page from a brief")
    parser.add_argument("--scaffold", "-s", type=str, default=None,
                        help="Generate a project scaffold by name")
    parser.add_argument("--audit", "-a", type=str, default=None,
                        help="Audit a file (HTML/JSX) for SEO/CWV")
    parser.add_argument("--spec", type=str, default="",
                        help="Component specification (natural language)")
    parser.add_argument("--framework", "-f", type=str, default="astro",
                        choices=FRAMEWORKS,
                        help="Target framework (default: astro)")
    parser.add_argument("--list-components", action="store_true",
                        help="List available component types")
    parser.add_argument("--list-frameworks", action="store_true",
                        help="List supported frameworks")
    parser.add_argument("--deep-audit", action="store_true",
                        help="Use LLM for deep audit (requires OpenRouter key)")
    parser.add_argument("--feedback", type=str, default=None, nargs=2,
                        metavar=("SID", "OUTCOME"),
                        help="Record verdict for a signal: --feedback <sid> accepted|edited|rejected")

    args = parser.parse_args()

    ensure_soul(AGENT, "Артемий", "Frontend Agent — сайты мирового уровня")

    if args.feedback:
        sid, outcome = args.feedback
        ok = capture_outcome(sid, outcome)
        print(f"{'✅' if ok else '❌'} Feedback '{outcome}' recorded for {sid}")
        if ok:
            lessons = build_learned_context(AGENT)
            if lessons and evolve_soul(AGENT, lessons):
                print(f"🧬 Soul evolved: folded fresh lessons into {AGENT}.soul.md")
        _stats = mem_compact(AGENT)
        if _stats["removed"]:
            print(f"🗜️  Memory compacted: {_stats['before']}→{_stats['after']} (-{_stats['removed']})")
        return

    if args.list_components:
        print("Available components:")
        for t in COMPONENT_TYPES:
            print(f"  - {t}")
        return

    if args.list_frameworks:
        print("Supported frameworks:")
        for fw in FRAMEWORKS:
            print(f"  - {fw}: {DEFAULTS[fw]['label']}")
        return

    if args.component:
        print(f"🔨 Generating {args.framework} component: {args.component}")
        ctx = _ctx(args.spec)
        sid = capture_start("artemiy", "generate_component", args.spec, {"framework": args.framework})
        if run_with_healing:
            res = run_with_healing(
                ctx,
                lambda p: generate_component(args.component, args.spec, args.framework, learned_context=p),
                _validate_frontend,
                max_retries=1,
            )
            result = res.output
            if res.attempts > 1:
                print(f"🩹 Self-healing: {res.attempts} attempts, {'clean' if res.ok else 'still had issues'}")
        else:
            result = generate_component(args.component, args.spec, args.framework, learned_context=ctx)
        if result:
            path = _save(f"{args.component}.{_ext(args.framework)}", result)
            print(f"✅ Saved to {path}")
            _guard(result, sid)
            remember("artemiy", f"generated {args.framework} {args.component}: {args.spec}", kind="generation")
            print(f"📡 Signal {sid} logged — later: python3 -m artemiy --feedback {sid} accepted|edited|rejected")
        else:
            print("❌ Failed")
            sys.exit(1)
        return

    if args.page:
        print(f"🔨 Generating {args.framework} page from brief")
        ctx = _ctx(args.page)
        sid = capture_start("artemiy", "generate_page", args.page, {"framework": args.framework})
        result = generate_page(args.page, args.framework, learned_context=ctx)
        if result:
            path = _save(f"page.{_ext(args.framework)}", result)
            print(f"✅ Saved to {path}")
            _guard(result, sid)
            remember("artemiy", f"generated {args.framework} page: {args.page[:100]}", kind="generation")
            print(f"📡 Signal {sid} logged — later: python3 -m artemiy --feedback {sid} accepted|edited|rejected")
        else:
            print("❌ Failed")
            sys.exit(1)
        return

    if args.scaffold:
        print(f"🔨 Scaffolding {args.framework} project: {args.scaffold}")
        result = generate_scaffold(args.scaffold, args.framework)
        if result:
            path = _save("scaffold.md", result)
            print(f"✅ Saved to {path}")
        else:
            print("❌ Failed")
            sys.exit(1)
        return

    if args.audit:
        print(f"🔨 Auditing {args.audit}")
        if args.deep_audit:
            try:
                with open(args.audit, encoding="utf-8") as f:
                    code = f.read()
                report = audit_with_llm(code)
            except Exception as e:
                print(f"❌ {e}")
                sys.exit(1)
            if report:
                path = _save("audit_report.md", report)
                print(f"✅ Deep audit saved to {path}")
            else:
                print("❌ LLM unavailable")
                sys.exit(1)
        else:
            result = audit_file(args.audit)
            if "error" in result:
                print(f"❌ {result['error']}")
                sys.exit(1)
            print(f"Score: {result['score']}% ({result['passed']}/{result['total']})")
            for f in result["findings"]:
                print(f"  {f}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
