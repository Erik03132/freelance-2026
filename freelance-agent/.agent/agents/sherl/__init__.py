"""Python API for Sherl — importable from other agents."""

from .geo_scan import competitor_audit, geo_scan, market_research
from .report import format_comparison, format_confidence, format_geo
from .research_config import COMPETITOR_FACTORS, GEO_MODELS, SEARCH_PROVIDERS
from .searcher import research

__all__ = [
    "research",
    "geo_scan",
    "competitor_audit",
    "market_research",
    "format_geo",
    "format_comparison",
    "format_confidence",
    "SEARCH_PROVIDERS",
    "GEO_MODELS",
    "COMPETITOR_FACTORS",
]
