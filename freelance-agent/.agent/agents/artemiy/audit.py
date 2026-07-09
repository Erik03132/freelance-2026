"""Static frontend audit for Artemiy (no LLM required for basics)."""

from __future__ import annotations

import re

from .frontend_config import CWV_TARGETS, SEO_CHECKS
from .llm_client import call_llm

SEO_PATTERNS = {
    "title": r"<title[^>]*>([^<]+)</title>",
    "meta_description": r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)',
    "h1": r"<h1[^>]*>",
    "main": r"<main[^>]*>",
    "article": r"<article[^>]*>",
    "nav": r"<nav[^>]*>",
    "og": r'<meta[^>]+property=["\']og:',
    "schema": r"application/ld\+json|itemscope|itemtype=",
    "img_alt": r"<img(?![^>]*\balt=)",
}


def audit_code(code: str) -> dict:
    """Static checks on HTML/JSX/markdown code. Returns score + findings."""
    findings = []
    score = 0
    total = len(SEO_PATTERNS)

    for name, pattern in SEO_PATTERNS.items():
        if re.search(pattern, code, re.IGNORECASE):
            score += 1
            findings.append(f"✅ {name.replace('_', ' ')}")
        elif name == "img_alt":
            findings.append("✅ img alt present")
            score += 1
        else:
            findings.append(f"❌ {name.replace('_', ' ')} missing")

    pct = round(100 * score / total)
    return {
        "score": pct,
        "passed": score,
        "total": total,
        "findings": findings,
        "cwv_targets": CWV_TARGETS,
    }


def audit_file(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        return {"error": str(e)}
    result = audit_code(code)
    result["file"] = path
    return result


def audit_with_llm(code: str, api_key: str | None = None) -> str | None:
    """Deep LLM audit with concrete improvements."""
    prompt = f"""You are a Core Web Vitals + SEO expert. Audit this frontend code:

{code[:4000]}

Return a structured report:
1. Critical issues (perf/SEO/a11y)
2. Concrete fixes (with code snippets)
3. Priority order"""
    return call_llm(prompt, max_tokens=2000, temperature=0.2, api_key=api_key)
