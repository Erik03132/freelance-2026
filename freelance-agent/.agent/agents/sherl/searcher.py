"""Real web search for Sherl (Serper / Perplexity), with OpenRouter LLM fallback."""

from __future__ import annotations

import json

import requests

from .llm_client import (
    call_llm,
    load_openrouter_key,
    load_perplexity_key,
    load_serper_key,
)


def search_serper(query: str, api_key: str | None = None) -> dict | None:
    """Google search via Serper.dev. Returns raw JSON or None."""
    key = api_key or load_serper_key()
    if not key:
        return None
    try:
        resp = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": key, "Content-Type": "application/json"},
            json={"q": query, "gl": "ru", "hl": "ru"},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


def search_perplexity(query: str, api_key: str | None = None) -> str | None:
    """Perplexity online search. Returns answer text or None."""
    key = api_key or load_perplexity_key()
    if not key:
        return None
    try:
        resp = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={
                "model": "sonar",
                "messages": [{"role": "user", "content": query}],
            },
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def _serper_to_sources(data: dict) -> list[dict]:
    out = []
    for item in data.get("organic", [])[:8]:
        out.append({
            "title": item.get("title", ""),
            "url": item.get("link", ""),
            "snippet": item.get("snippet", ""),
        })
    return out


def research(query: str, api_key: str | None = None, learned_context: str = "") -> dict:
    """
    Multi-source research. Tries real search first, falls back to LLM.

    Returns: {"provider": str, "sources": [...], "answer": str, "live": bool}
    """
    data = search_serper(query, api_key)
    if data:
        sources = _serper_to_sources(data)
        answer = data.get("answerBox", {}).get("answer") or "\n".join(
            s["snippet"] for s in sources[:3]
        )
        return {"provider": "serper", "sources": sources, "answer": answer, "live": True}

    ptext = search_perplexity(query, api_key)
    if ptext:
        return {
            "provider": "perplexity",
            "sources": [{"title": "Perplexity", "url": "", "snippet": ptext[:300]}],
            "answer": ptext,
            "live": True,
        }

    # Fallback: LLM (no live data — mark low confidence)
    llm = call_llm(
        f"You are Sherl, a research agent. Provide a structured answer with "
        f"caveats for: {query}\nNote: no live search available — mark as unverified."
        f"{learned_context}",
        api_key=api_key,
    )
    if llm:
        return {
            "provider": "openrouter-fallback",
            "sources": [],
            "answer": llm,
            "live": False,
        }
    return {"provider": "none", "sources": [], "answer": "", "live": False}
