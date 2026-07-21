import os
import pytest
from rembrandt import generate_design_md, render_design_md, BrandSystem, DesignToken

_HAS_KEY = bool(os.environ.get("OPENROUTER_API_KEY") or os.path.exists(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")))

def test_render_design_md_minimal():
    brand = BrandSystem(name="Test", theme="dark", colors=[], typography={}, spacing={}, components={}, guidelines=[])
    md = render_design_md(brand)
    assert "# Test" in md
    assert "dark" in md
    assert "## Tokens — Colors" in md

def test_render_design_md_with_colors():
    brand = BrandSystem(
        name="ColorTest", theme="light",
        colors=[DesignToken("Red", "#ff0000", "--color-red", "Primary")],
        typography={}, spacing={}, components={}, guidelines=[],
    )
    md = render_design_md(brand)
    assert "#ff0000" in md
    assert "--color-red" in md

@pytest.mark.skipif(_HAS_KEY, reason="API key available — would make real LLM call")
def test_generate_design_md_no_key(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "")
    result = generate_design_md("modern brand")
    assert result is None
