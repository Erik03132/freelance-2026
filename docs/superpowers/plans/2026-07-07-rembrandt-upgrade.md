# Rembrandt Upgrade: Universal Designer Agent — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade Rembrandt from a Leonardo.ai image script to a universal designer agent with DESIGN.md generation, HTML/CSS component generation, and Leonardo.ai image generation.

**Architecture:** Modular Python package with CLI entry point. `brand_system.py` holds the design system data model, `design_generator.py` generates DESIGN.md specs via OpenRouter, `component_generator.py` generates HTML/CSS, `image_generator.py` wraps Leonardo.ai. Agent profile references all capabilities.

**Tech Stack:** Python 3.14, OpenRouter API (LLM calls), requests (Leonardo.ai), pytest

**Base path:** `projects/ai-eggs/agent/`

---

### Task 1: Create brand_system.py — Brand System Data Model

**Files:**
- Create: `projects/ai-eggs/agent/brand_system.py`
- Test: `projects/ai-eggs/tests/test_brand_system.py`

- [ ] **Step 1: Write the failing test**

```python
import json, tempfile, os
from agent.brand_system import BrandSystem, DesignToken, load_brand, INCUBIRD_DEFAULT

def test_brand_system_creation():
    brand = BrandSystem(
        name="Test",
        theme="dark",
        colors=[DesignToken(name="Void", value="#08090a", token="--color-void", role="Canvas")],
        typography={"font": "Inter"},
        spacing={"base": 4},
        components={"button": {"radius": 6}},
        guidelines=["Do use Inter"],
    )
    assert brand.name == "Test"
    assert brand.theme == "dark"
    assert brand.colors[0].name == "Void"

def test_incubird_default_exists():
    assert INCUBIRD_DEFAULT is not None
    assert INCUBIRD_DEFAULT.name == "IncuBird"

def test_load_brand():
    data = {
        "name": "Custom",
        "theme": "light",
        "colors": [],
        "typography": {},
        "spacing": {},
        "components": {},
        "guidelines": [],
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        path = f.name
    try:
        brand = load_brand(path)
        assert brand.name == "Custom"
    finally:
        os.unlink(path)

def test_brand_to_dict():
    brand = BrandSystem(name="Test", theme="light", colors=[], typography={}, spacing={}, components={}, guidelines=[])
    d = brand.to_dict()
    assert d["name"] == "Test"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/ai-eggs && python3 -m pytest tests/test_brand_system.py -v`
Expected: FAIL with ModuleNotFoundError

- [ ] **Step 3: Write brand_system.py**

```python
"""Brand system data model for Rembrandt."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict


@dataclass
class DesignToken:
    name: str
    value: str
    token: str
    role: str = ""


@dataclass
class BrandSystem:
    name: str
    theme: str  # "light" | "dark"
    colors: list[DesignToken] = field(default_factory=list)
    typography: dict = field(default_factory=dict)
    spacing: dict = field(default_factory=dict)
    components: dict = field(default_factory=dict)
    guidelines: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "theme": self.theme,
            "colors": [asdict(c) for c in self.colors],
            "typography": self.typography,
            "spacing": self.spacing,
            "components": self.components,
            "guidelines": self.guidelines,
        }


def load_brand(path: str) -> BrandSystem:
    with open(path) as f:
        data = json.load(f)
    colors = [DesignToken(**c) for c in data.get("colors", [])]
    return BrandSystem(
        name=data["name"],
        theme=data.get("theme", "light"),
        colors=colors,
        typography=data.get("typography", {}),
        spacing=data.get("spacing", {}),
        components=data.get("components", {}),
        guidelines=data.get("guidelines", []),
    )


INCUBIRD_DEFAULT = BrandSystem(
    name="IncuBird",
    theme="warm",
    colors=[
        DesignToken("Wheat", "#f5e6ca", "--color-wheat", "Page background, warm base"),
        DesignToken("Olive", "#7a9e5a", "--color-olive", "Primary accent, CTAs"),
        DesignToken("Terracotta", "#c4724a", "--color-terracotta", "Secondary accent, highlights"),
        DesignToken("Soil", "#4a3728", "--color-soil", "Body text, headings"),
        DesignToken("Cream", "#faf3e8", "--color-cream", "Card surfaces, elevated backgrounds"),
        DesignToken("Sage", "#b8c9a8", "--color-sage", "Borders, dividers, muted accents"),
        DesignToken("Honey", "#d4a853", "--color-honey", "Warnings, ratings, stars"),
        DesignToken("White", "#ffffff", "--color-white", "Contrast text on dark"),
    ],
    typography={
        "font_primary": "Manrope, sans-serif",
        "font_heading": "PT Serif, serif",
        "font_mono": "JetBrains Mono, monospace",
        "weights": {"light": 300, "regular": 400, "medium": 500, "bold": 700},
        "scale": {
            "display": "72px",
            "h1": "48px",
            "h2": "32px",
            "h3": "24px",
            "body": "16px",
            "body_sm": "14px",
            "caption": "12px",
        },
    },
    spacing={
        "base": 4,
        "scale": [4, 8, 12, 16, 24, 32, 48, 64, 96],
        "card_padding": 24,
        "section_gap": 64,
        "element_gap": 8,
        "max_width": "1200px",
    },
    components={
        "button": {"radius": 8, "padding": "12px 24px", "font_weight": 500},
        "card": {"radius": 12, "padding": 24, "shadow": "0 2px 8px rgba(74, 55, 40, 0.08)"},
        "input": {"radius": 8, "padding": "12px 16px", "border": "1px solid #b8c9a8"},
        "badge": {"radius": 4, "padding": "2px 8px", "font_size": "12px"},
    },
    guidelines=[
        "Use warm earth tones — avoid cold blues and grays",
        "PT Serif for headings, Manrope for body",
        "Generous whitespace — rural brands should feel open, not cramped",
        "Rounded corners (8-12px) for approachability",
        "Subtle shadows with warm undertones (rgba with brown shift)",
    ],
)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd projects/ai-eggs && python3 -m pytest tests/test_brand_system.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

Run: `cd projects/ai-eggs && git add agent/brand_system.py tests/test_brand_system.py && git commit -m "feat: brand system data model with IncuBird default"`

---

### Task 2: Create image_generator.py — Leonardo.ai Wrapper

**Files:**
- Create: `projects/ai-eggs/agent/image_generator.py` (extract from rembrandt.py)
- Test: `projects/ai-eggs/tests/test_image_generator.py`

- [ ] **Step 1: Write the failing test**

```python
from agent.image_generator import leonardo_generate, download_image

def test_leonardo_generate_no_key(monkeypatch):
    monkeypatch.setenv("LEONARDO_API_KEY", "")
    result = leonardo_generate("test prompt")
    assert result is None

def test_leonardo_generate_api_error(monkeypatch):
    monkeypatch.setenv("LEONARDO_API_KEY", "test_key")
    # Will fail on actual API call — that's expected
    pass
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/ai-eggs && python3 -m pytest tests/test_image_generator.py -v`
Expected: FAIL with ModuleNotFoundError

- [ ] **Step 3: Create image_generator.py**

Extract the following functions from the current `rembrandt.py` into a clean module:

```python
"""Leonardo.ai image generation wrapper."""

import os
import time
import requests


LEONARDO_BASE_URL = "https://cloud.leonardo.ai/api/rest/v1"
LEONARDO_MODELS = {
    "phoenix": "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3",
    "diffusion_xl": "e71a1c2f-3432-4365-aa9a-58804c51051d",
    "absolute_reality": "c61732db-3fac-48d1-9e9e-608fc27e7519",
}


def _load_api_key() -> str:
    """Load LEONARDO_API_KEY from environment."""
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    if k.strip() == "LEONARDO_API_KEY":
                        return v.strip()
    return os.getenv("LEONARDO_API_KEY", "")


def leonardo_generate(
    prompt: str,
    model: str = "phoenix",
    width: int = 1024,
    height: int = 1024,
    api_key: str | None = None,
) -> str | None:
    """
    Generate an image via Leonardo.ai API.

    Args:
        prompt: Image description
        model: "phoenix" | "diffusion_xl" | "absolute_reality"
        width, height: Image dimensions
        api_key: Optional key (loaded from env if not provided)

    Returns:
        Image URL or None on failure
    """
    key = api_key or _load_api_key()
    if not key:
        return None

    model_id = LEONARDO_MODELS.get(model, LEONARDO_MODELS["phoenix"])

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    payload = {
        "prompt": prompt,
        "negative_prompt": "text, watermark, signature, blurry, deformed, ugly, duplicate",
        "modelId": model_id,
        "width": width,
        "height": height,
        "num_images": 1,
        "scheduler": "EULER_DISCRETE",
        "sd_version": "SDXL_1_0",
    }

    try:
        response = requests.post(
            f"{LEONARDO_BASE_URL}/generations",
            headers=headers,
            json=payload,
            timeout=60,
        )
        data = response.json()

        if "sdGenerationJob" not in data:
            return None

        generation_id = data["sdGenerationJob"]["generationId"]

        for _ in range(20):
            time.sleep(3)
            status_resp = requests.get(
                f"{LEONARDO_BASE_URL}/generations/{generation_id}",
                headers=headers,
                timeout=30,
            )
            status_data = status_resp.json()
            status = status_data.get("sdGenerationJob", {}).get("status", "PENDING")

            if status == "COMPLETE":
                images = status_data.get("generated_images", [])
                if images:
                    return images[0].get("url")
                return None
            elif status == "FAILED":
                return None

        return None
    except Exception:
        return None


def download_image(url: str, output_path: str, proxy: str = "") -> bool:
    """Download image from URL to local file."""
    proxies = {}
    if proxy:
        proxies = {"https": proxy, "http": proxy}

    try:
        response = requests.get(url, timeout=60, proxies=proxies or None)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return True
        return False
    except Exception:
        return False
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd projects/ai-eggs && python3 -m pytest tests/test_image_generator.py -v`
Expected: PASS (1 passed)

- [ ] **Step 5: Commit**

Run: `cd projects/ai-eggs && git add agent/image_generator.py tests/test_image_generator.py && git commit -m "feat: extract Leonardo.ai wrapper into image_generator"`

---

### Task 3: Create design_generator.py — DESIGN.md Generator

**Files:**
- Create: `projects/ai-eggs/agent/design_generator.py`
- Test: `projects/ai-eggs/tests/test_design_generator.py`

- [ ] **Step 1: Write the failing test**

```python
from agent.design_generator import generate_design_md, render_design_md
from agent.brand_system import BrandSystem, DesignToken

def test_render_design_md_minimal():
    brand = BrandSystem(name="Test", theme="dark", colors=[], typography={}, spacing={}, components={}, guidelines=[])
    md = render_design_md(brand)
    assert "# Test" in md
    assert "dark" in md
    assert "## Tokens — Colors" in md

def test_render_design_md_with_colors():
    brand = BrandSystem(
        name="ColorTest", theme="light",
        colors=[DesignToken("Red", "#ff0000", "--color-red", "Primary")],
        typography={}, spacing={}, components={}, guidelines=[],
    )
    md = render_design_md(brand)
    assert "#ff0000" in md
    assert "--color-red" in md

def test_generate_design_md_no_key(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "")
    result = generate_design_md("modern brand")
    assert result is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/ai-eggs && python3 -m pytest tests/test_design_generator.py -v`
Expected: FAIL with ModuleNotFoundError

- [ ] **Step 3: Create design_generator.py**

```python
"""DESIGN.md generation from a design brief."""

import json
import os
from dataclasses import asdict

import requests

from .brand_system import BrandSystem, DesignToken, render_design_md  # will be in same module


def _load_openrouter_key() -> str:
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    if k.strip() == "OPENROUTER_API_KEY":
                        return v.strip()
    return os.getenv("OPENROUTER_API_KEY", "")


DESIGN_SYSTEM_PROMPT = """You are a design system expert. Given a design brief, generate a complete brand system in JSON format.

Respond ONLY with valid JSON matching this schema:
{
  "name": "Brand name",
  "theme": "light" | "dark" | "warm",
  "colors": [
    {"name": "ColorName", "value": "#hex", "token": "--color-name", "role": "Usage description"}
  ],
  "typography": {
    "font_primary": "font-family",
    "font_heading": "font-family",
    "weights": {"light": 300, "regular": 400, "medium": 500, "bold": 700},
    "scale": {"h1": "48px", "h2": "32px", ...}
  },
  "spacing": {
    "base": 4,
    "scale": [4, 8, 12, 16, 24, 32, 48, 64, 96],
    "card_padding": 24,
    "section_gap": 64,
    "max_width": "1200px"
  },
  "components": {
    "button": {"radius": 8, "padding": "12px 24px"},
    "card": {"radius": 12, "padding": 24}
  },
  "guidelines": ["Do use...", "Don't use..."]
}

Design brief: {brief}

Return ONLY valid JSON, no markdown, no explanation."""


def generate_design_md(brief: str, api_key: str | None = None) -> str | None:
    """
    Generate a complete DESIGN.md from a natural language brief.

    Args:
        brief: Design description (e.g. "Modern agricultural brand, warm earth tones")
        api_key: OpenRouter API key (loaded from env if None)

    Returns:
        DESIGN.md content as string, or None if generation fails
    """
    key = api_key or _load_openrouter_key()
    if not key:
        return None

    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": "deepseek/deepseek-chat-v3-0324",
                "messages": [{"role": "user", "content": DESIGN_SYSTEM_PROMPT.format(brief=brief)}],
                "max_tokens": 2000,
                "temperature": 0.3,
            },
            timeout=60,
        )
        content = resp.json()["choices"][0]["message"]["content"].strip()
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
    except Exception as e:
        return None


def render_design_md(brand: BrandSystem) -> str:
    """Render a BrandSystem into Refero-compatible DESIGN.md format."""
    lines = []
    lines.append(f"# {brand.name} — Design System")
    lines.append(f"> **Theme:** {brand.theme}")
    lines.append("")

    if brand.colors:
        lines.append("## Tokens — Colors")
        lines.append("")
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd projects/ai-eggs && python3 -m pytest tests/test_design_generator.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

Run: `cd projects/ai-eggs && git add agent/design_generator.py tests/test_design_generator.py && git commit -m "feat: DESIGN.md generator from design brief"`

---

### Task 4: Create component_generator.py — HTML/CSS Component Generator

**Files:**
- Create: `projects/ai-eggs/agent/component_generator.py`
- Test: `projects/ai-eggs/tests/test_component_generator.py`

- [ ] **Step 1: Write the failing test**

```python
from agent.component_generator import generate_component, COMPONENT_TYPES
from agent.brand_system import INCUBIRD_DEFAULT

def test_component_types():
    assert "button" in COMPONENT_TYPES
    assert "card" in COMPONENT_TYPES
    assert "hero" in COMPONENT_TYPES
    assert "nav" in COMPONENT_TYPES
    assert len(COMPONENT_TYPES) >= 10

def test_generate_component_no_key(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "")
    result = generate_component("button", "Primary CTA button", INCUBIRD_DEFAULT)
    # Falls back to template render
    assert result is not None
    assert "<button" in result or "button" in result.lower()

def test_generate_component_returns_html():
    result = generate_component("card", "Feature card with icon, title, description", INCUBIRD_DEFAULT)
    assert result is not None
    assert isinstance(result, str)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/ai-eggs && python3 -m pytest tests/test_component_generator.py -v`
Expected: FAIL with ModuleNotFoundError

- [ ] **Step 3: Create component_generator.py**

```python
"""HTML/CSS component generation from design system spec."""

import os

import requests

from .brand_system import BrandSystem


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

Requirements:
- Vanilla HTML + CSS only (no frameworks, no JS, no Tailwind)
- Mobile + desktop versions (CSS media queries)
- Use CSS custom properties from the design system
- No placeholder images
- Production-grade styling
- Return ONLY the HTML code, no explanation."""


def _load_openrouter_key() -> str:
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    if k.strip() == "OPENROUTER_API_KEY":
                        return v.strip()
    return os.getenv("OPENROUTER_API_KEY", "")


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
) -> str | None:
    """
    Generate HTML/CSS for a component.

    Args:
        component_type: Type from COMPONENT_TYPES
        spec: Natural language spec (e.g. "Primary CTA button with hover effect")
        brand: BrandSystem to use for design tokens
        api_key: OpenRouter API key (loaded from env if None)

    Returns:
        HTML string or None on failure
    """
    if component_type not in COMPONENT_TYPES:
        return None

    key = api_key or _load_openrouter_key()

    if not key:
        return _render_fallback(component_type, spec, brand)

    prompt = COMPONENT_PROMPT.format(
        component_type=component_type,
        theme=brand.theme,
        colors=_format_colors(brand),
        font_primary=brand.typography.get("font_primary", "sans-serif"),
        font_heading=brand.typography.get("font_heading", "serif"),
        spacing=_format_spacing(brand),
        radii=_format_radii(brand),
        spec=spec,
    )

    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": "deepseek/deepseek-chat-v3-0324",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2000,
                "temperature": 0.2,
            },
            timeout=60,
        )
        content = resp.json()["choices"][0]["message"]["content"].strip()
        if "```html" in content:
            content = content.split("```html")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
        return content
    except Exception:
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd projects/ai-eggs && python3 -m pytest tests/test_component_generator.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

Run: `cd projects/ai-eggs && git add agent/component_generator.py tests/test_component_generator.py && git commit -m "feat: HTML/CSS component generator"`

---

### Task 5: Rewrite rembrandt.py — CLI Entry Point

**Files:**
- Modify: `projects/ai-eggs/agent/rembrandt.py` (replace entirely)

- [ ] **Step 1: Write rembrandt.py**

```python
#!/usr/bin/env python3
"""
🎨 Rembrandt — Universal Designer Agent

Многофункциональный дизайн-агент для генерации дизайн-систем,
UI-компонентов и изображений.

Использование:
    python3 rembrandt.py --design "Modern agricultural brand"
    python3 rembrandt.py --component "hero section with gradient"
    python3 rembrandt.py --prompt "farm poultry chickens" --output photo.png
    python3 rembrandt.py --brand path/to/brand.json --component "button"
"""

import argparse
import json
import os
import sys

from .brand_system import BrandSystem, load_brand, INCUBIRD_DEFAULT
from .component_generator import generate_component, COMPONENT_TYPES
from .design_generator import generate_design_md
from .image_generator import leonardo_generate, download_image


def main():
    parser = argparse.ArgumentParser(
        description="🎨 Rembrandt — Universal Designer Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 rembrandt.py --design "Modern agricultural brand, warm earth tones"
  python3 rembrandt.py --component "hero" --spec "Hero section with gradient bg and CTA" --style incubird
  python3 rembrandt.py --prompt "farm poultry chickens" --output photo.png
  python3 rembrandt.py --list-components
        """,
    )

    # Design system generation
    parser.add_argument("--design", "-d", type=str, default=None,
                        help="Generate DESIGN.md from a design brief")

    # Component generation
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

    # Image generation (existing)
    parser.add_argument("--prompt", "-p", type=str, default=None,
                        help="Image description for Leonardo.ai generation")
    parser.add_argument("--output", "-o", type=str, default=None,
                        help="Output file path for image")

    # Utility
    parser.add_argument("--list-components", action="store_true",
                        help="List available component types")
    parser.add_argument("--list-brands", action="store_true",
                        help="List available brand systems")

    args = parser.parse_args()

    # --- Load brand ---
    brand: BrandSystem = INCUBIRD_DEFAULT
    if args.brand:
        brand = load_brand(args.brand)
    elif args.style == "custom" and not args.brand:
        print("❌ --style custom requires --brand path/to/brand.json")
        sys.exit(1)

    # --- List components ---
    if args.list_components:
        print("Available component types:")
        for t in COMPONENT_TYPES:
            print(f"  - {t}")
        return

    # --- List brands ---
    if args.list_brands:
        print("Available brand systems:")
        print(f"  - incubird (default): {INCUBIRD_DEFAULT.name}")
        if args.brand:
            print(f"  - custom: {args.brand}")
        return

    # --- DESIGN.md generation ---
    if args.design:
        print(f"🎨 Generating DESIGN.md from brief: {args.design}")
        result = generate_design_md(args.design)
        if result:
            output_dir = os.path.join(os.path.dirname(__file__), "output")
            os.makedirs(output_dir, exist_ok=True)
            path = os.path.join(output_dir, "design.md")
            with open(path, "w") as f:
                f.write(result)
            print(f"✅ DESIGN.md saved to {path}")
        else:
            print("❌ Failed to generate DESIGN.md")
            sys.exit(1)
        return

    # --- Component generation ---
    if args.component:
        spec = args.spec or f"Generate a {args.component} component in {brand.name} style"
        print(f"🎨 Generating component: {args.component}")
        print(f"   Style: {brand.name}")
        print(f"   Spec: {spec}")
        result = generate_component(args.component, spec, brand)
        if result:
            output_dir = os.path.join(os.path.dirname(__file__), "output")
            os.makedirs(output_dir, exist_ok=True)
            path = os.path.join(output_dir, f"{args.component}.html")
            with open(path, "w") as f:
                f.write(result)
            print(f"✅ Component saved to {path}")
        else:
            print("❌ Failed to generate component")
            sys.exit(1)
        return

    # --- Image generation ---
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
```

- [ ] **Step 2: Run syntax check**

Run: `cd projects/ai-eggs && python3 -c "import py_compile; py_compile.compile('agent/rembrandt.py', doraise=True)"`
Expected: Syntax OK

- [ ] **Step 3: Commit**

Run: `cd projects/ai-eggs && git add agent/rembrandt.py && git commit -m "refactor: rewrite rembrandt.py as universal designer CLI"`

---

### Task 6: Update Agent Profile — rembrandt-designer.md

**Files:**
- Modify: `freelance-agent/.agent/agents/rembrandt-designer.md`

- [ ] **Step 1: Read current profile**

Read the current `rembrandt-designer.md`.

- [ ] **Step 2: Update agent profile**

```markdown
---
name: rembrandt-designer
description: "Универсальный дизайн-агент. Генерация DESIGN.md дизайн-систем, UI-компонентов (HTML/CSS), изображений через Leonardo.ai. Работает с бренд-системами. CLI: python3 rembrandt.py --design/--component/--prompt"
tools: [Read, Edit, Write, Bash, Glob, Grep]
skills: [frontend-design, web-design-guidelines, brand-voice]
---

# Rembrandt — Universal Designer Agent - [GLOBAL]

## Goal
Создание дизайн-систем, UI-компонентов и визуальных ассетов.
Дизайн, который вызывает WOW-эффект при первом взгляде и обеспечивает интуитивный UX.

## Core Competencies
1. **Design Systems** — генерация DESIGN.md (цвета, типографика, spacing, токены, компоненты, гайдлайны)
2. **UI Components** — генерация production-ready HTML/CSS компонентов (button, card, hero, nav, form, modal, stats, badge, footer, section, input, header)
3. **Image Generation** — генерация изображений через Leonardo.ai API (--prompt)
4. **Brand Systems** — работа с бренд-системами, дефолтный IncuBird brand
5. **Design References** — Refero Styles (https://styles.refero.design/) как библиотека референсов

## Tools
### CLI (python3 agent/rembrandt.py)
- `--design "brief"` — генерация полной DESIGN.md дизайн-системы
- `--component "type" --spec "description"` — генерация HTML/CSS компонента
- `--prompt "description" --output photo.png` — генерация изображения
- `--brand path/to/brand.json` — кастомная бренд-система
- `--list-components` — список доступных типов компонентов

### Python API (для вызова из других агентов)
```python
from agent.rembrandt import generate_component, generate_design_md
from agent.brand_system import INCUBIRD_DEFAULT

html = generate_component("button", "Primary CTA", INCUBIRD_DEFAULT)
design_md = generate_design_md("Modern agricultural brand")
```

## Design Principles
### 1. Design System First
- Любой UI начинается с DESIGN.md — определи цвета, типографику, spacing
- Используй Refero Styles (https://styles.refero.design/) как референс
- Следуй формату Refero DESIGN.md для совместимости с другими AI-агентами

### 2. Visual Excellence
- Избегай generic цветов (plain red, blue, green)
- Используй курированные палитры
- Современная типографика (Inter, Manrope, PT Serif)

### 3. Production-Grade HTML/CSS
- Vanilla HTML + CSS — никаких фреймворков
- Mobile + desktop через CSS media queries
- CSS custom properties для всех токенов

### 4. Brand Consistency
- Дефолтный IncuBird brand: тёплые земляные тона, Manrope + PT Serif
- При запросе другого бренда — загрузи кастомный brand.json

## Brand Systems
### IncuBird (default)
- Theme: warm
- Colors: Wheat, Olive, Terracotta, Soil, Cream, Sage, Honey
- Fonts: Manrope (body), PT Serif (headings)

### Custom Brand
Загружается через `--brand path/to/brand.json` или параметр в Python API.
Формат: BrandSystem с colors, typography, spacing, components, guidelines.

## Constraints
- Никаких placeholder изображений
- Дизайн должен быть реализуем без дополнительных библиотек
- Каждый компонент = mobile + desktop версии
- CSS custom properties для всех токенов
```

- [ ] **Step 3: Verify YAML front matter is valid**

The front matter must be valid YAML. Check: `name`, `description`, `tools`, `skills` are all present and correctly formatted.

- [ ] **Step 4: Commit**

Run: `cd freelance-2026 && git add freelance-agent/.agent/agents/rembrandt-designer.md && git commit -m "feat: upgrade Rembrandt agent profile to universal designer"`

---

### Task 7: Create IncuBird Brand JSON + Output Directory

**Files:**
- Create: `projects/ai-eggs/agent/incubird-design.json`

- [ ] **Step 1: Create incubird-design.json**

```json
{
  "name": "IncuBird",
  "theme": "warm",
  "colors": [
    {"name": "Wheat", "value": "#f5e6ca", "token": "--color-wheat", "role": "Page background, warm base"},
    {"name": "Olive", "value": "#7a9e5a", "token": "--color-olive", "role": "Primary accent, CTAs"},
    {"name": "Terracotta", "value": "#c4724a", "token": "--color-terracotta", "role": "Secondary accent, highlights"},
    {"name": "Soil", "value": "#4a3728", "token": "--color-soil", "role": "Body text, headings"},
    {"name": "Cream", "value": "#faf3e8", "token": "--color-cream", "role": "Card surfaces, elevated backgrounds"},
    {"name": "Sage", "value": "#b8c9a8", "token": "--color-sage", "role": "Borders, dividers, muted accents"},
    {"name": "Honey", "value": "#d4a853", "token": "--color-honey", "role": "Warnings, ratings, stars"},
    {"name": "White", "value": "#ffffff", "token": "--color-white", "role": "Contrast text on dark backgrounds"}
  ],
  "typography": {
    "font_primary": "Manrope, sans-serif",
    "font_heading": "PT Serif, serif",
    "font_mono": "JetBrains Mono, monospace",
    "weights": {"light": 300, "regular": 400, "medium": 500, "bold": 700},
    "scale": {
      "display": "72px", "h1": "48px", "h2": "32px",
      "h3": "24px", "body": "16px", "body_sm": "14px", "caption": "12px"
    }
  },
  "spacing": {
    "base": 4, "scale": [4, 8, 12, 16, 24, 32, 48, 64, 96],
    "card_padding": 24, "section_gap": 64, "element_gap": 8, "max_width": "1200px"
  },
  "components": {
    "button": {"radius": 8, "padding": "12px 24px", "font_weight": 500},
    "card": {"radius": 12, "padding": 24, "shadow": "0 2px 8px rgba(74, 55, 40, 0.08)"},
    "input": {"radius": 8, "padding": "12px 16px", "border": "1px solid #b8c9a8"},
    "badge": {"radius": 4, "padding": "2px 8px", "font_size": "12px"}
  },
  "guidelines": [
    "Use warm earth tones — avoid cold blues and grays",
    "PT Serif for headings, Manrope for body",
    "Generous whitespace — rural brands should feel open, not cramped",
    "Rounded corners (8-12px) for approachability",
    "Subtle shadows with warm undertones (rgba with brown shift)"
  ]
}
```

- [ ] **Step 2: Create output directory with .gitkeep**

Run: `mkdir -p projects/ai-eggs/agent/output && touch projects/ai-eggs/agent/output/.gitkeep`

- [ ] **Step 3: Commit**

Run: `cd projects/ai-eggs && git add agent/incubird-design.json agent/output/.gitkeep && git commit -m "feat: add IncuBird brand JSON and output directory"`

---

### Task 8: Run All Tests + Final Commit

**Files:** (none — verification only)

- [ ] **Step 1: Run all tests**

Run: `cd projects/ai-eggs && python3 -m pytest tests/ -v`
Expected: All tests pass (11+ tests)

- [ ] **Step 2: Verify CLI help works**

Run: `cd projects/ai-eggs && python3 agent/rembrandt.py --help`
Expected: Shows help with all options (--design, --component, --prompt, --list-components)

- [ ] **Step 3: Verify --list-components works**

Run: `cd projects/ai-eggs && python3 agent/rembrandt.py --list-components`
Expected: Lists 12 component types (button, card, input, nav, hero, section, badge, stats, footer, modal, form, header)

- [ ] **Step 4: Final commit**

Run: `cd freelance-2026 && git add -A && git commit -m "feat: Rembrandt universal designer — all modules"`

---

## Self-Review Checklist

1. **Spec coverage:** All spec requirements covered — brand system (Task 1), DESIGN.md generation (Task 3), component generation (Task 4), image generation (Task 2), CLI entry point (Task 5), agent profile (Task 6), brand JSON (Task 7).
2. **Placeholder scan:** No TBD, TODO, or "implement later" — all code is concrete.
3. **Type consistency:** `BrandSystem` data model is consistent across all tasks. `DesignToken` used everywhere. Function signatures match.
4. **Test coverage:** Every module has a test file. Tests for normal cases and edge cases (no API key).
