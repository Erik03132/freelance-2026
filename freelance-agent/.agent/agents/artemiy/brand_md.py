"""Fetch brand design tokens from a public URL for Artemiy's generation.

Two strategies:
1. DESIGN.md from designmd.supply (if accessible)
2. Fallback: scrape page <meta> tags for colors, fonts, og:image
"""

from __future__ import annotations

import os
import re

import requests

USER_AGENT = "Artemiy/1.0 (frontend agent; +https://github.com/anomalyco/freelance-2026)"


def fetch_brand_design(domain: str, timeout: int = 15) -> str:
    """Fetch brand design tokens from *domain*.

    Returns a Markdown string suitable for injecting into Artemiy's prompt
    context.  Returns empty string on any failure (degrade gracefully).
    """
    domain = domain.strip().removeprefix("https://").removeprefix("http://").split("/")[0]
    md = _try_designmd_supply(domain, timeout)
    if md:
        return md
    md = _try_meta_scrape(domain, timeout)
    return md


def _try_designmd_supply(domain: str, timeout: int) -> str:
    """Try fetching a pre-generated DESIGN.md from designmd.supply."""
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY", "")
    proxies = {"https": proxy} if proxy else None
    try:
        resp = requests.get(
            f"https://www.designmd.supply/guides/{domain}",
            headers={"User-Agent": USER_AGENT},
            timeout=timeout,
            proxies=proxies,
        )
        if resp.status_code == 200:
            text = resp.text
            if "DESIGN.md" in text or "design-tokens" in text:
                return f"[Design tokens from designmd.supply for {domain}]\n{text[:5000]}"
    except Exception:
        pass
    try:
        resp = requests.get(
            f"https://designmd.cc/api/design?domain={domain}",
            headers={"User-Agent": USER_AGENT},
            timeout=timeout,
            proxies=proxies,
        )
        if resp.status_code == 200:
            return f"[Design tokens from designmd.cc for {domain}]\n{resp.text[:5000]}"
    except Exception:
        pass
    return ""


def _try_meta_scrape(domain: str, timeout: int) -> str:
    """Fallback: scrape <meta> tags for design clues."""
    proxy = os.environ.get("HTTP_PROXY", "")
    proxies = {"http": proxy, "https": proxy} if proxy else None
    try:
        resp = requests.get(
            f"https://{domain}",
            headers={"User-Agent": USER_AGENT},
            timeout=timeout,
            proxies=proxies,
        )
        if resp.status_code != 200:
            return ""
        html = resp.text
    except Exception:
        return ""

    lines = [f"[Meta design tokens for {domain} (fallback)]"]
    colors = set()
    fonts = set()

    for match in re.findall(r'<meta[^>]*name="theme-color"[^>]*content="([^"]+)"', html):
        if re.match(r'^#[0-9a-fA-F]{3,8}$', match):
            colors.add(match)
    for match in re.findall(r'<meta[^>]*name="msapplication-TileColor"[^>]*content="([^"]+)"', html):
        if re.match(r'^#[0-9a-fA-F]{3,8}$', match):
            colors.add(match)

    for match in re.findall(r'<link[^>]*href="[^"]*fonts\.googleapis[^"]*family=([^"&]+)', html):
        fonts.add(match.replace("+", " "))

    for match in re.findall(r'--(?:primary|accent|brand|color-primary)[^:]*:\s*([^;}]+)', html):
        v = match.strip()
        if re.match(r'^#[0-9a-fA-F]{3,8}$', v):
            colors.add(v)

    if colors:
        lines.append(f"- Colors: {', '.join(sorted(colors)[:6])}")
    if fonts:
        lines.append(f"- Fonts: {', '.join(fonts)}")
    if not colors and not fonts:
        return ""
    return "\n".join(lines)
