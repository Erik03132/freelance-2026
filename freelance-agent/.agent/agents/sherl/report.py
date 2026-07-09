"""Report formatting for Sherl (markdown tables)."""

from __future__ import annotations

from .research_config import GEO_MODELS


def format_geo(result: dict) -> str:
    status = "✅ упомянут" if result.get("mentioned") else "❌ не найден"
    lines = [f"## GEO-Scan: {result['brand']}", ""]
    lines.append(f"**Запрос:** {result['query']}")
    lines.append(f"**Присутствие:** {status}")
    lines.append(f"**Источник:** {result.get('provider')} (live={result.get('live')})")
    lines.append("")
    if result.get("context"):
        lines.append(f"> {result['context']}")
        lines.append("")
    for s in result.get("sources", [])[:5]:
        url = s.get("url", "")
        lines.append(f"- [{s.get('title', '')}]({url})" if url else f"- {s.get('title', '')}")
    return "\n".join(lines)


def format_comparison(rows: list[dict], criteria: list[str]) -> str:
    """rows: list of {name, **criteria_values}"""
    header = "| Критерий | " + " | ".join(r["name"] for r in rows) + " |"
    sep = "|" + "---|" * (len(rows) + 1)
    lines = ["## Сравнение", "", header, sep]
    for c in criteria:
        cells = [str(r.get(c, "—")) for r in rows]
        lines.append(f"| {c} | " + " | ".join(cells) + " |")
    lines.append("")
    return "\n".join(lines)


def format_confidence(level: str) -> str:
    return f"**Достоверность:** {level}"
