"""OpenRouter LLM client for Rembrandt (shared across rembrandt modules)."""

import os

import requests

DEFAULT_MODEL = "deepseek/deepseek-chat-v3-0324"

# Model routing (OpenHuman-inspired): simple tasks -> cheap/fast, complex -> quality
ROUTE = {
    "simple": "deepseek/deepseek-chat-v3-0324",
    "complex": "anthropic/claude-sonnet-4",
}


def _compress(text: str, max_chars: int = 1500) -> str:
    """TokenJuice-lite: truncate over-long context before the model."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n...[truncated]"


def load_openrouter_key() -> str:
    env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    if k.strip() == "OPENROUTER_API_KEY":
                        return v.strip()
    return os.getenv("OPENROUTER_API_KEY", "")


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
            # strip the first fenced block
            parts = content.split("```")
            if len(parts) >= 3:
                block = parts[1]
                if block.startswith(("html", "jsx", "tsx", "python", "css", "json")):
                    block = block.split("\n", 1)[1] if "\n" in block else ""
                content = block.strip()
        return content
    except Exception:
        return None
