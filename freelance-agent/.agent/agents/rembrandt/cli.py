"""🔨 Rembrandt — Universal Designer Agent (LLM-CLI).

Запуск: python3 -m rembrandt [opts]
Генерация дизайн-систем (DESIGN.md), UI-компонентов и изображений (Leonardo.ai).

Использование:
    python3 -m rembrandt --design "Modern agricultural brand"
    python3 -m rembrandt --component "hero" --spec "Gradient hero with CTA"
    python3 -m rembrandt --prompt "farm poultry chickens" --output photo.png
    python3 -m rembrandt --brand path/to/brand.json --component "button"
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

AGENT = "rembrandt"
_base_learned = build_learned_context


def build_learned_context(agent, min_samples=3):  # noqa: F811 — wrap to inject soul
    base = _base_learned(agent, min_samples)
    s = soul_context(agent)
    if s:
        return s + ("\n\n" + base if base else "")
    return base

from .brand_system import BrandSystem, INCUBIRD_DEFAULT, load_brand
from .component_generator import COMPONENT_TYPES, generate_component
from .design_generator import generate_design_md
from .image_generator import download_image, leonardo_generate


def _save(name: str, content: str) -> str:
    out = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def _guard(code: str, sid: str) -> None:
    """Security guardrail: warn on leaked secrets/.env in generated output."""
    leaks = scan_leaks(code)
    if leaks:
        print(f"⚠️  SECURITY GUARD: possible leak(s) in output: {', '.join(leaks)}")
        print("   Move secrets to server-side / env proxy; never ship keys to frontend.")
        capture_start("rembrandt", "leak_detected", f"signal {sid}", {"issues": leaks})


def main():
    parser = argparse.ArgumentParser(
        description="🔨 Rembrandt — Universal Designer Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 -m rembrandt --design "Modern agricultural brand, warm earth tones"
  python3 -m rembrandt --component "hero" --spec "Hero with gradient bg and CTA" --style incubird
  python3 -m rembrandt --prompt "farm poultry chickens" --output photo.png
  python3 -m rembrandt --list-components
        """,
    )
    parser.add_argument("--design", "-d", type=str, default=None,
                        help="Generate DESIGN.md from a design brief")
    parser.add_argument("--component", "-c", type=str, default=None,
                        choices=COMPONENT_TYPES + [None],
                        help=f"Generate a UI component ({', '.join(COMPONENT_TYPES)})")
    parser.add_argument("--spec", "-s", type=str, default="",
                        help="Component specification (natural language)")
    parser.add_argument("--style", type=str, default="incubird",
                        choices=["incubird", "custom"],
                        help="Brand style to use")
    parser.add_argument("--brand", type=str, default=None,
                        help="Path to custom brand JSON file")
    parser.add_argument("--prompt", "-p", type=str, default=None,
                        help="Image description for Leonardo.ai generation")
    parser.add_argument("--output", "-o", type=str, default=None,
                        help="Output file path for image")
    parser.add_argument("--list-components", action="store_true",
                        help="List available component types")
    parser.add_argument("--list-brands", action="store_true",
                        help="List available brand systems")
    parser.add_argument("--feedback", type=str, default=None, nargs=2,
                        metavar=("SID", "OUTCOME"),
                        help="Record verdict for a signal: --feedback <sid> accepted|edited|rejected")

    args = parser.parse_args()

    ensure_soul(AGENT, "Рембрандт", "Universal Designer Agent")

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

    brand: BrandSystem = INCUBIRD_DEFAULT
    if args.brand:
        brand = load_brand(args.brand)
    elif args.style == "custom" and not args.brand:
        print("❌ --style custom requires --brand path/to/brand.json")
        sys.exit(1)

    if args.list_components:
        print("Available component types:")
        for t in COMPONENT_TYPES:
            print(f"  - {t}")
        return

    if args.list_brands:
        print("Available brand systems:")
        print(f"  - incubird (default): {INCUBIRD_DEFAULT.name}")
        if args.brand:
            print(f"  - custom: {args.brand}")
        return

    if args.design:
        print(f"🎨 Generating DESIGN.md from brief: {args.design}")
        ctx = enrich_context("rembrandt", args.design, build_learned_context("rembrandt"))
        result = generate_design_md(args.design, learned_context=ctx)
        if result:
            path = _save("design.md", result)
            print(f"✅ DESIGN.md saved to {path}")
        else:
            print("❌ Failed to generate DESIGN.md")
            sys.exit(1)
        return

    if args.component:
        spec = args.spec or f"Generate a {args.component} component in {brand.name} style"
        print(f"🎨 Generating component: {args.component}")
        ctx = enrich_context("rembrandt", spec, build_learned_context("rembrandt"))
        sid = capture_start("rembrandt", "generate_component", spec, {"style": args.style})
        result = generate_component(args.component, spec, brand, learned_context=ctx)
        if result:
            path = _save(f"{args.component}.html", result)
            print(f"✅ Component saved to {path}")
            _guard(result, sid)
            print(f"📡 Signal {sid} logged — later: python3 -m rembrandt --feedback {sid} accepted|edited|rejected")
        else:
            print("❌ Failed to generate component")
            sys.exit(1)
        return

    if args.prompt:
        print(f"🎨 Generating image: {args.prompt}")
        image_url = leonardo_generate(args.prompt)
        if image_url:
            output_path = args.output or os.path.join(
                os.path.dirname(__file__), "output", "generated.png"
            )
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            if download_image(image_url, output_path):
                print(f"✅ Image saved to {output_path}")
            else:
                print("❌ Failed to download image")
                sys.exit(1)
        else:
            print("❌ Failed to generate image")
            sys.exit(1)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
