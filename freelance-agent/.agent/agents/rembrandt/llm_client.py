"""OpenRouter LLM client for Rembrandt — shim over shared llm package."""

from llm import (  # noqa: F401
    DEFAULT_MODEL,
    ROUTE,
    _compress,
    call_llm,
    load_openrouter_key,
)
