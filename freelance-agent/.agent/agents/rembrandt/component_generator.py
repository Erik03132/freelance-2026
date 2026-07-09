"""HTML/CSS component generation from design system spec."""

from .brand_system import BrandSystem
from .llm_client import call_llm


COMPONENT_TYPES = [
    "button", "card", "input", "nav", "hero", "section",
    "badge", "stats", "footer", "modal", "form", "header",
]

COMPONENT_PROMPT = """You are a UI developer. Generate a single HTML file with embedded CSS for a {component_type} component.

Design system:
- Theme: {theme}
- Colors: {colors}
- Primary font: {font_primary}
- Heading font: {font_heading}
- Spacing: {spacing}
- Border radii: {radii}

Specification: {spec}

{learned_context}

Requirements:
- Vanilla HTML + CSS only (no frameworks, no JS, no Tailwind)
- Mobile + desktop versions (CSS media queries)
- Use CSS custom properties from the design system
- No placeholder images
- Production-grade styling
- Return ONLY the HTML code, no explanation."""


def _format_colors(brand: BrandSystem) -> str:
    return "; ".join(f"{c.name}: {c.value}" for c in brand.colors[:5])


def _format_spacing(brand: BrandSystem) -> str:
    s = brand.spacing
    return f"base {s.get('base', 4)}px, card {s.get('card_padding', 24)}px, section gap {s.get('section_gap', 64)}px"


def _format_radii(brand: BrandSystem) -> str:
    comps = brand.components
    radii = []
    for name in ["button", "card", "input", "badge"]:
        if name in comps and "radius" in comps[name]:
            radii.append(f"{name}: {comps[name]['radius']}px")
    return ", ".join(radii) if radii else "8px default"


def generate_component(
    component_type: str,
    spec: str,
    brand: BrandSystem,
    api_key: str | None = None,
    learned_context: str = "",
) -> str | None:
    """
    Generate HTML/CSS for a component.

    Args:
        component_type: Type from COMPONENT_TYPES
        spec: Natural language spec (e.g. "Primary CTA button with hover effect")
        brand: BrandSystem to use for design tokens
        api_key: OpenRouter API key (loaded from env if None)
        learned_context: self-learning insights injected into the prompt

    Returns:
        HTML string or None on failure
    """
    if component_type not in COMPONENT_TYPES:
        return None

    prompt = COMPONENT_PROMPT.format(
        component_type=component_type,
        theme=brand.theme,
        colors=_format_colors(brand),
        font_primary=brand.typography.get("font_primary", "sans-serif"),
        font_heading=brand.typography.get("font_heading", "serif"),
        spacing=_format_spacing(brand),
        radii=_format_radii(brand),
        spec=spec,
        learned_context=learned_context or "",
    )

    result = call_llm(prompt, complexity="simple", max_tokens=2000, temperature=0.2, api_key=api_key)
    if result:
        return result
    return _render_fallback(component_type, spec, brand)


def _render_fallback(component_type: str, spec: str, brand: BrandSystem) -> str:
    """Render a minimal fallback component when LLM is unavailable."""
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{component_type.title()} — {brand.name}</title>
<style>
  :root {{
    {"".join(f'  --{c.token.lstrip("--")}: {c.value};' for c in brand.colors if c.token)}
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: {brand.typography.get("font_primary", "sans-serif")};
    background: var(--color-cream, #faf3e8);
    color: var(--color-soil, #4a3728);
    padding: 48px 24px;
  }}
  .component-wrapper {{
    max-width: {brand.spacing.get("max_width", "1200px")};
    margin: 0 auto;
  }}
</style>
</head>
<body>
<div class="component-wrapper">
  <p>Component: <strong>{component_type}</strong></p>
  <p>Spec: {spec}</p>
  <p><em>LLM unavailable — install component_generator with OpenRouter key for AI-generated components.</em></p>
</div>
</body>
</html>"""
