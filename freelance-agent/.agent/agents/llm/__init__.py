"""Shared OpenRouter LLM client for all agents.

Replaces 4 duplicate llm_client.py files (artemiy, kulibin, sherl, rembrandt).
Uses Sherl's robust _find_env() that walks up 6 parent directories.

Usage from any agent:
    from llm import call_llm, load_openrouter_key, ROUTE
"""

from __future__ import annotations

import os

import requests

DEFAULT_MODEL = "deepseek/deepseek-chat-v3-0324"

ROUTE = {
    "simple": "deepseek/deepseek-chat-v3-0324",
    "complex": "anthropic/claude-sonnet-4",
}


def _find_env(start: str | None = None) -> str:
    """Walk up to 6 parent directories from *start* to find .env."""
    d = os.path.dirname(os.path.abspath(start or __file__))
    for _ in range(6):
        cand = os.path.join(d, ".env")
        if os.path.exists(cand):
            return cand
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return ""


def _load_key(env_name: str, start: str | None = None) -> str:
    """Load a single key from .env by name, with env-var fallback."""
    env_path = _find_env(start)
    if env_path:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    if k.strip() == env_name:
                        return v.strip()
    return os.getenv(env_name, "")


def load_openrouter_key(start: str | None = None) -> str:
    return _load_key("OPENROUTER_API_KEY", start)


def load_serper_key(start: str | None = None) -> str:
    return _load_key("SERPER_API_KEY", start)


def load_perplexity_key(start: str | None = None) -> str:
    return _load_key("PERPLEXITY_API_KEY", start)


def load_proxy(start: str | None = None) -> None:
    """Load HTTP_PROXY/HTTPS_PROXY from .env into os.environ."""
    env_path = _find_env(start)
    if not env_path:
        return
    for var in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY"):
        val = _load_key(var, start)
        if val and var not in os.environ:
            os.environ[var] = val
        # lowercase variants for requests/urllib3
        lc = var.lower()
        if val and lc not in os.environ:
            os.environ[lc] = val


def _compress(text: str, max_chars: int = 1500) -> str:
    """TokenJuice-lite: truncate over-long context before the model."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n...[truncated]"


def call_llm(
    prompt: str,
    *,
    model: str | None = None,
    max_tokens: int = 2500,
    temperature: float = 0.2,
    api_key: str | None = None,
    complexity: str = "simple",
) -> str | None:
    """Call OpenRouter chat completion. Returns content string or None.

    complexity: "simple" -> deepseek, "complex" -> sonnet (model routing).
    """
    load_proxy()
    key = api_key if api_key is not None else load_openrouter_key()
    if not key:
        return None
    model = model or ROUTE.get(complexity, DEFAULT_MODEL)
    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
            timeout=60,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"].strip()
        if "```" in content:
            parts = content.split("```")
            if len(parts) >= 3:
                block = parts[1]
                if block.startswith(("html", "jsx", "tsx", "python", "css", "json")):
                    block = block.split("\n", 1)[1] if "\n" in block else ""
                content = block.strip()
        return content
    except Exception:
        return None
