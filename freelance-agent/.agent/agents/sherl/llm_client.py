"""OpenRouter LLM client for Sherl — shim over shared llm package."""

from llm import (  # noqa: F401
    DEFAULT_MODEL,
    ROUTE,
    _compress,
    call_llm,
    load_openrouter_key,
    load_perplexity_key,
    load_serper_key,
)
