from sherl import (
    SEARCH_PROVIDERS, GEO_MODELS, COMPETITOR_FACTORS,
    research, geo_scan, competitor_audit, market_research,
    format_geo, format_comparison, format_confidence,
)


def test_search_providers():
    assert len(SEARCH_PROVIDERS) >= 2
    assert "serper" in SEARCH_PROVIDERS


def test_geo_models():
    assert len(GEO_MODELS) >= 1


def test_competitor_factors():
    assert len(COMPETITOR_FACTORS) >= 3


def test_research_no_key():
    result = research("AI SEO trends 2026")
    assert result is not None
    assert "answer" in result
    assert "provider" in result
    assert "live" in result
    assert "sources" in result
    # Without any API keys, should fall back to LLM or return error gracefully
    assert result.get("answer") is None or isinstance(result["answer"], str)


def test_geo_scan():
    result = geo_scan("TestBrand", "CRM")
    assert result is not None
    # geo_scan returns a dict with brand/query results
    assert isinstance(result, dict)


def test_competitor_audit_no_key():
    result = competitor_audit("amoCRM", api_key="")
    assert result is not None
    assert "report" in result


def test_market_research_no_key():
    result = market_research("AI-обзвон в России 2026", api_key="")
    assert result is not None
    assert "brief" in result


def test_format_geo():
    result = format_geo({"brand": "Test", "query": "test", "results": []})
    assert "Test" in result


def test_format_comparison():
    rows = [{"name": "A", "score": 0.8}, {"name": "B", "score": 0.6}]
    result = format_comparison(rows, criteria=["quality"])
    assert "A" in result
    assert "B" in result


def test_format_confidence():
    result = format_confidence(0.95)
    assert isinstance(result, str)
    assert "0.95" in result
