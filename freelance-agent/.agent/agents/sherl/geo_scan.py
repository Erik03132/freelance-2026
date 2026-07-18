"""GEO scan + competitor audit for Sherl (built on real search)."""

from __future__ import annotations

from .llm_client import call_llm
from .research_config import COMPETITOR_FACTORS, GEO_MODELS
from .searcher import research


def geo_scan(brand: str, query: str, api_key: str | None = None) -> dict:
    """Check brand presence in AI/web results for a query."""
    full = f"{brand} {query}"
    res = research(full, api_key=api_key)
    answer = res.get("answer", "")
    mentioned = brand.lower() in answer.lower()
    return {
        "brand": brand,
        "query": query,
        "mentioned": mentioned,
        "provider": res.get("provider"),
        "live": res.get("live", False),
        "sources": res.get("sources", []),
        "context": answer[:500],
    }


def competitor_audit(name: str, api_key: str | None = None, learned_context: str = "") -> dict:
    """Structured competitor analysis from open sources."""
    res = research(f"{name} product features pricing reviews", api_key=api_key)
    answer = res.get("answer", "")
    # LLM structuration of raw findings
    structured = call_llm(
        f"""From the research below about competitor "{name}", extract a structured report:
- Strong sides
- Weak sides
- Opportunities for us
- Threats
- Commercial factors checklist ({', '.join(COMPETITOR_FACTORS)})

Research:
{answer[:3000]}

{learned_context}""",
        max_tokens=1500,
        temperature=0.2,
        api_key=api_key,
    )
    return {
        "name": name,
        "live": res.get("live", False),
        "sources": res.get("sources", []),
        "report": structured or answer,
    }


def market_research(question: str, api_key: str | None = None, learned_context: str = "") -> dict:
    res = research(question, api_key=api_key)
    structured = call_llm(
        f"""From the research, produce a market brief for: "{question}"
- Key facts (with source hints)
- Trends
- Conclusions
- Recommendations

Research:
{res.get('answer', '')[:3000]}

{learned_context}""",
        max_tokens=1800,
        temperature=0.2,
        api_key=api_key,
    )
    return {
        "question": question,
        "live": res.get("live", False),
        "sources": res.get("sources", []),
        "brief": structured or res.get("answer", ""),
    }
