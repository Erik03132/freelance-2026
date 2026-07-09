"""🔍 Sherl — Research Agent (LLM-CLI).

Запуск: python3 -m sherl [opts]
Разведка: реальный поиск (Serper/Perplexity), GEO-скан, аудит конкурентов.

Использование:
    python3 -m sherl --research "лучшие CRM для малого бизнеса 2026"
    python3 -m sherl --geo-scan "Levitan" --query "CRM для автозвонков"
    python3 -m sherl --competitor "amoCRM"
    python3 -m sherl --market "рынок AI-обзвона в России"
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
    from memory import enrich_context, recall, remember
except ImportError:
    def enrich_context(agent, query, ctx="", top_k=2):
        return ctx
    def recall(agent, query, top_k=3):
        return []
    def remember(agent, fact, kind):
        pass

from . import (
    SEARCH_PROVIDERS,
    competitor_audit,
    format_geo,
    geo_scan,
    market_research,
    research,
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
        description="🔍 Sherl — Research Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
        "  python3 -m sherl --research 'AI SEO trends 2026'\n"
        "  python3 -m sherl --geo-scan 'Levitan' --query 'CRM обзвон'\n"
        "  python3 -m sherl --competitor 'amoCRM'\n",
    )
    parser.add_argument("--research", "-r", type=str, default=None,
                        help="Multi-source research query")
    parser.add_argument("--geo-scan", type=str, default=None,
                        help="Brand name for GEO presence scan")
    parser.add_argument("--query", "-q", type=str, default="",
                        help="Query used with --geo-scan")
    parser.add_argument("--competitor", "-c", type=str, default=None,
                        help="Competitor name for audit")
    parser.add_argument("--market", "-m", type=str, default=None,
                        help="Market research question")
    parser.add_argument("--list-providers", action="store_true",
                        help="List search providers")
    parser.add_argument("--feedback", type=str, default=None, nargs=2,
                        metavar=("SID", "OUTCOME"),
                        help="Record verdict for a signal: --feedback <sid> accepted|edited|rejected")

    args = parser.parse_args()

    if args.feedback:
        sid, outcome = args.feedback
        ok = capture_outcome(sid, outcome)
        print(f"{'✅' if ok else '❌'} Feedback '{outcome}' recorded for {sid}")
        return

    if args.list_providers:
        print("Search providers (priority):", ", ".join(SEARCH_PROVIDERS))
        return

    if args.research:
        print(f"🔍 Researching: {args.research}")
        ctx = enrich_context("sherl", args.research, build_learned_context("sherl"))
        sid = capture_start("sherl", "research", args.research)
        res = research(args.research, learned_context=ctx)
        tag = "LIVE" if res["live"] else "NO-LIVE (LLM fallback)"
        print(f"[{tag}] via {res['provider']}")
        print(res["answer"][:2000])
        if res["sources"]:
            print("\nSources:")
            for s in res["sources"][:5]:
                print(f"  - {s.get('title')}: {s.get('url')}")
        print(f"\n📡 Signal {sid} logged — later: python3 -m sherl --feedback {sid} accepted|edited|rejected")
        return

    if args.geo_scan:
        print(f"🔍 GEO-scan: {args.geo_scan} / {args.query}")
        ctx = enrich_context("sherl", f"{args.geo_scan} {args.query}", build_learned_context("sherl"))
        sid = capture_start("sherl", "geo_scan", f"{args.geo_scan} {args.query}")
        result = geo_scan(args.geo_scan, args.query)
        text = format_geo(result)
        path = _save("geo_scan.md", text)
        print(text)
        print(f"\n✅ Saved to {path}")
        return

    if args.competitor:
        print(f"🔍 Competitor audit: {args.competitor}")
        ctx = enrich_context("sherl", args.competitor, build_learned_context("sherl"))
        sid = capture_start("sherl", "competitor_audit", args.competitor)
        result = competitor_audit(args.competitor, learned_context=ctx)
        path = _save(f"competitor_{args.competitor}.md", result["report"])
        print(result["report"][:2000])
        print(f"\n✅ Saved to {path}")
        print(f"📡 Signal {sid} logged — later: python3 -m sherl --feedback {sid} accepted|edited|rejected")
        return

    if args.market:
        print(f"🔍 Market research: {args.market}")
        ctx = enrich_context("sherl", args.market, build_learned_context("sherl"))
        sid = capture_start("sherl", "market_research", args.market)
        result = market_research(args.market, learned_context=ctx)
        path = _save("market.md", result["brief"])
        print(result["brief"][:2000])
        print(f"\n✅ Saved to {path}")
        print(f"📡 Signal {sid} logged — later: python3 -m sherl --feedback {sid} accepted|edited|rejected")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
