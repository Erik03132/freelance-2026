"""Component generation for Artemiy (Astro/React/Vanilla)."""

from __future__ import annotations

from .frontend_config import COMPONENT_TYPES, DEFAULTS
from .llm_client import call_llm

COMPONENT_PROMPT = """You are a senior frontend engineer. Generate a production-ready {framework} component for a "{component_type}" UI element.

Framework: {framework} — {note}
Styling: {styling}

Specification: {spec}

{learned_context}

Requirements:
- Production-grade, accessible (WCAG AA), mobile-first
- Semantic markup, no placeholder images
- Clean, readable code — no comments unless required
- Return ONLY the code, no explanation, no markdown fences around the whole answer."""

PROMPT_BY_FRAMEWORK = {
    "astro": "Use .astro syntax: frontmatter between ---, scoped <style>. Include responsive CSS.",
    "react": "Use TypeScript .tsx, functional component with hooks, CSS Modules or inline styles. Include 'use client' if needed.",
    "vanilla": "Output a single HTML file with embedded <style> and minimal <script>. CSS custom properties for theming.",
}


def generate_component(
    component_type: str,
    spec: str = "",
    framework: str = "astro",
    api_key: str | None = None,
    learned_context: str = "",
) -> str | None:
    if component_type not in COMPONENT_TYPES:
        return None
    if framework not in DEFAULTS:
        framework = "astro"

    cfg = DEFAULTS[framework]
    prompt = COMPONENT_PROMPT.format(
        framework=framework,
        component_type=component_type,
        note=cfg["note"] + " " + PROMPT_BY_FRAMEWORK.get(framework, ""),
        styling=cfg["styling"],
        spec=spec or f"Generate a {component_type} component",
        learned_context=learned_context or "",
    )

    result = call_llm(prompt, max_tokens=2500, temperature=0.2, api_key=api_key)
    return result or _render_fallback(component_type, spec, framework)


def _render_fallback(component_type: str, spec: str, framework: str) -> str:
    return f"""// LLM unavailable — install OpenRouter key for AI-generated {framework} components.
// Component: {component_type}
// Spec: {spec}
export function {component_type.title()}() {{
  return <div className="{component_type}">{component_type}</div>;
}}
"""
