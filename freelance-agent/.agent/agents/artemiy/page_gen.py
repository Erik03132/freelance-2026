"""Page/scaffold generation for Artemiy."""

from __future__ import annotations

from .frontend_config import DEFAULTS
from .llm_client import call_llm

PAGE_PROMPT = """You are a senior frontend engineer. Generate a complete {framework} page from this brief:

BRIEF: {brief}

Framework: {framework} — {note}
Styling: {styling}

{learned_context}

Requirements:
- Full page layout (header, hero, sections, footer) matching the brief
- Mobile-first, accessible (WCAG AA), Core Web Vitals optimized
- Semantic HTML, SEO-ready (title, meta, OG, Schema.org where relevant)
- Production-grade code, no placeholder content
- Return ONLY the code."""


def generate_page(
    brief: str,
    framework: str = "astro",
    api_key: str | None = None,
    learned_context: str = "",
) -> str | None:
    if framework not in DEFAULTS:
        framework = "astro"
    cfg = DEFAULTS[framework]
    prompt = PAGE_PROMPT.format(
        brief=brief,
        framework=framework,
        note=cfg["note"],
        styling=cfg["styling"],
        learned_context=learned_context or "",
    )
    return call_llm(prompt, max_tokens=4000, temperature=0.3, api_key=api_key)


def generate_scaffold(
    name: str,
    framework: str = "astro",
    api_key: str | None = None,
) -> str | None:
    """Generate a project scaffold description (file tree + key files)."""
    if framework not in DEFAULTS:
        framework = "astro"
    prompt = f"""Generate a minimal {framework} project scaffold named "{name}".
Return a file tree and the content of the 3 most important files (config, layout, entry).
Focus on performance and clean structure. Return ONLY the structure as markdown."""
    return call_llm(prompt, max_tokens=2000, temperature=0.2, api_key=api_key)
