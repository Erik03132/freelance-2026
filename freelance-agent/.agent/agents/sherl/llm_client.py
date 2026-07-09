"""OpenRouter LLM client for Sherl (shared across sherl modules)."""

import os

import requests

DEFAULT_MODEL = "deepseek/deepseek-chat-v3-0324"

ROUTE = {
    "simple": "deepseek/deepseek-chat-v3-0324",
    "complex": "anthropic/claude-sonnet-4",
}


def _compress(text: str, max_chars: int = 1500) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n...[truncated]"


def _find_env() -> str:
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):
        cand = os.path.join(d, ".env")
        if os.path.exists(cand):
            return cand
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return ""


def load_openrouter_key() -> str:
    env_path = _find_env()
    if env_path:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    if k.strip() == "OPENROUTER_API_KEY":
                        return v.strip()
    return os.getenv("OPENROUTER_API_KEY", "")


def load_serper_key() -> str:
    env_path = _find_env()
    if env_path:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    if k.strip() == "SERPER_API_KEY":
                        return v.strip()
    return os.getenv("SERPER_API_KEY", "")


def load_perplexity_key() -> str:
    env_path = _find_env()
    if env_path:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    if k.strip() == "PERPLEXITY_API_KEY":
                        return v.strip()
    return os.getenv("PERPLEXITY_API_KEY", "")


def call_llm(
    prompt: str,
    *,
    model: str | None = None,
    max_tokens: int = 2500,
    temperature: float = 0.2,
    api_key: str | None = None,
    complexity: str = "simple",
) -> str | None:
    key = api_key or load_openrouter_key()
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
