"""DESIGN.md generation from a design brief."""

import json

from .brand_system import BrandSystem, DesignToken
from .llm_client import call_llm


APPLE_DESIGN_RULES = """
## Apple Design Rules (apply to ALL generated output)

### Motion & Springs
- Default UI spring: damping 1.0, response 0.3-0.4 (critically damped, no overshoot)
- Momentum/flick spring: damping ~0.8, response 0.3-0.4 (slight bounce only for physical gestures)
- CSS motion: animate ONLY `transform` and `opacity`, hint with `will-change`
- Interruptibility: never lock input during transition, animate from current value not target
- Use `requestAnimationFrame` as display-synced clock

### Materials & Depth
- Translucent chrome: `backdrop-filter: blur(20px) saturate(180%)` with semi-transparent bg
- Material weight encodes hierarchy (darker = structural, lighter = interactive)
- Never stack light translucent on another surface
- Scroll edge effects instead of hard dividers
- Materialize: animate blur + scale together on enter/exit

### Typography
- Default: `font: 100%/1.5 system-ui, sans-serif; font-optical-sizing: auto;`
- Display text: `font-size: clamp(2rem, 5vw, 4rem); line-height: 1.05; letter-spacing: -0.02em;`
- Tracking (letter-spacing) is size-specific: negative for large text, near 0 for body
- Leading inversely tracks size: tight on headings, loose on body
- Spacing in rem/em, not px (respect user's text-size setting)

### Accessibility (MANDATORY)
- prefers-reduced-motion: replace slides/springs with opacity cross-fade
- prefers-reduced-transparency: solid backgrounds, drop blur
- prefers-contrast: near-solid backgrounds with defined border

### Design Principles
1. Purpose — every element earns its place
2. Agency — keep people in control, easy undo
3. Familiarity — consistent, predictable interactions
4. Simplicity — strip unnecessary, be concise and clear
5. Craft — every spacing/timing/alignment is deliberate
"""

DESIGN_SYSTEM_PROMPT = """You are a design system expert. Given a design brief, generate a complete brand system in JSON format.

{apple_rules}

Respond ONLY with valid JSON matching this schema:
{{
  "name": "Brand name",
  "theme": "light" | "dark" | "warm",
  "colors": [
    {{"name": "ColorName", "value": "#hex", "token": "--color-name", "role": "Usage description"}}
  ],
  "typography": {{
    "font_primary": "font-family",
    "font_heading": "font-family",
    "weights": {{"light": 300, "regular": 400, "medium": 500, "bold": 700}},
    "scale": {{"h1": "48px", "h2": "32px", ...}}
  }},
  "spacing": {{
    "base": 4,
    "scale": [4, 8, 12, 16, 24, 32, 48, 64, 96],
    "card_padding": 24,
    "section_gap": 64,
    "max_width": "1200px"
  }},
  "components": {{
    "button": {{"radius": 8, "padding": "12px 24px"}},
    "card": {{"radius": 12, "padding": 24}}
  }},
  "guidelines": ["Do use...", "Don't use..."]
}}

Design brief: {brief}

{learned_context}

Return ONLY valid JSON, no markdown, no explanation."""


def generate_design_md(brief: str, api_key: str | None = None, learned_context: str = "") -> str | None:
    """
    Generate a complete DESIGN.md from a natural language brief.

    Args:
        brief: Design description (e.g. "Modern agricultural brand, warm earth tones")
        api_key: OpenRouter API key (loaded from env if None)
        learned_context: self-learning insights injected into the prompt

    Returns:
        DESIGN.md content as string, or None if generation fails
    """
    prompt = DESIGN_SYSTEM_PROMPT.format(apple_rules=APPLE_DESIGN_RULES, brief=brief, learned_context=learned_context or "")
    content = call_llm(prompt, complexity="complex", max_tokens=2000, temperature=0.3, api_key=api_key)
    if not content:
        return None

    try:
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
            if content.startswith("json"):
                content = content[4:].strip()

        data = json.loads(content)
        colors = [DesignToken(**c) for c in data.get("colors", [])]
        brand = BrandSystem(
            name=data.get("name", brief[:30]),
            theme=data.get("theme", "light"),
            colors=colors,
            typography=data.get("typography", {}),
            spacing=data.get("spacing", {}),
            components=data.get("components", {}),
            guidelines=data.get("guidelines", []),
        )
        return render_design_md(brand)
    except Exception:
        return None


def render_design_md(brand: BrandSystem) -> str:
    """Render a BrandSystem into Refero-compatible DESIGN.md format."""
    lines = []
    lines.append(f"# {brand.name} — Design System")
    lines.append(f"> **Theme:** {brand.theme}")
    lines.append("")
    lines.append("> **Apple Design Reference:** `apple-design.md` — WWDC 2018-2026 fluid interface rules applied")
    lines.append("")

    lines.append("## Tokens — Colors")
    lines.append("")
    if brand.colors:
        lines.append("| Name | Value | Token | Role |")
        lines.append("|------|-------|-------|------|")
        for c in brand.colors:
            lines.append(f"| {c.name} | `{c.value}` | `{c.token}` | {c.role} |")
        lines.append("")

    if brand.typography:
        lines.append("## Typography")
        lines.append("")
        pf = brand.typography.get("font_primary", "")
        if pf:
            lines.append(f"**Primary font:** {pf}")
        hf = brand.typography.get("font_heading", "")
        if hf:
            lines.append(f"**Heading font:** {hf}")
        scale = brand.typography.get("scale", {})
        if scale:
            lines.append("")
            lines.append("| Role | Size |")
            lines.append("|------|------|")
            for role, size in scale.items():
                lines.append(f"| {role} | {size} |")
        lines.append("")

    if brand.spacing:
        lines.append("## Spacing")
        lines.append("")
        lines.append(f"**Base unit:** {brand.spacing.get('base', 4)}px")
        lines.append(f"**Max width:** {brand.spacing.get('max_width', '1200px')}")
        if brand.spacing.get("scale"):
            scale_values = ", ".join(f"{s}px" for s in brand.spacing["scale"])
            lines.append(f"**Scale:** {scale_values}")
        lines.append("")

    if brand.components:
        lines.append("## Components")
        lines.append("")
        for name, spec in brand.components.items():
            lines.append(f"### {name.title()}")
            for key, val in spec.items():
                lines.append(f"- **{key}:** {val}")
            lines.append("")

    if brand.guidelines:
        lines.append("## Guidelines")
        lines.append("")
        for g in brand.guidelines:
            lines.append(f"- {g}")
        lines.append("")

    return "\n".join(lines)
