"""Default frontend configuration for Artemiy."""

from __future__ import annotations

FRAMEWORKS = ["astro", "react", "vanilla"]

COMPONENT_TYPES = [
    "button", "card", "input", "nav", "hero", "section",
    "badge", "stats", "footer", "modal", "form", "header",
    "table", "accordion", "tabs", "toast",
]

DEFAULTS = {
    "astro": {
        "label": "Astro 5 (SSG/SSR, islands)",
        "styling": "Vanilla CSS (scoped) / Tailwind по запросу",
        "note": "Генерируй .astro компоненты с frontmatter + scoped <style>",
    },
    "react": {
        "label": "React + Vite (TSX)",
        "styling": "CSS Modules / Tailwind по запросу",
        "note": "Генерируй функциональные компоненты с хуками, TypeScript",
    },
    "vanilla": {
        "label": "Vanilla HTML/CSS/JS",
        "styling": "Vanilla CSS, custom properties",
        "note": "Генерируй единый HTML файл с embedded CSS/JS",
    },
}

SEO_CHECKS = [
    "уникальный <title> 50-60 символов",
    "уникальный <meta description> 150-160 символов",
    "единственный <h1>",
    "семантические HTML5 теги (<main>, <article>, <nav>)",
    "Schema.org разметка",
    "OG-теги",
    "alt на всех <img>",
]

CWV_TARGETS = {
    "LCP": "< 2.5s (WebP, preload fonts)",
    "INP": "< 100ms (minimize JS)",
    "CLS": "< 0.1 (image dimensions)",
}
