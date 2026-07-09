"""Default research config for Sherl (intel agent)."""

from __future__ import annotations

# Search providers priority: real search first, LLM fallback last
SEARCH_PROVIDERS = ["serper", "perplexity", "openrouter"]

SOURCES = {
    "web": "Google / general web",
    "ai": "AI assistants (ChatGPT, Perplexity, Gemini)",
    "dev": "GitHub, ProductHunt, Crunchbase",
    "docs": "Official docs, blogs, reports",
}

GEO_MODELS = ["ChatGPT", "Perplexity", "Gemini", "Claude"]

CONFIDENCE_LEVELS = ["высокий", "средний", "низкий"]

COMPETITOR_FACTORS = [
    "Цены указаны на сайте",
    "Есть кейсы/отзывы",
    "Работает demo/trial",
    "Есть интеграции",
    "Активный блог/новости",
    "Наличие API",
]
