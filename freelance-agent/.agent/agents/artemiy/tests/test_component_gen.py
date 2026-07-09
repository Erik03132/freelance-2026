from artemiy import COMPONENT_TYPES, DEFAULTS, generate_component, generate_page, generate_scaffold


def test_component_types():
    assert "button" in COMPONENT_TYPES
    assert "card" in COMPONENT_TYPES
    assert "hero" in COMPONENT_TYPES
    assert len(COMPONENT_TYPES) >= 6


def test_frameworks():
    assert "astro" in DEFAULTS
    assert "react" in DEFAULTS
    assert "vanilla" in DEFAULTS
    assert DEFAULTS["astro"]["label"]


def test_generate_component_no_key():
    result = generate_component("button", "Primary CTA", "astro", api_key="")
    assert result is not None
    assert "button" in result.lower() or "Button" in result


def test_generate_component_with_empty_api_key():
    result = generate_component("card", "Feature card", "react", api_key="")
    assert result is not None
    assert isinstance(result, str)


def test_generate_component_invalid_type():
    result = generate_component("nope", "test", "astro", api_key="")
    assert result is None


def test_generate_component_invalid_framework():
    result = generate_component("button", "test", "unknown", api_key="")
    assert result is not None


def test_generate_page_no_key():
    result = generate_page("Landing page for eco-farm", "astro", api_key="")
    assert result is None


def test_generate_scaffold_no_key():
    result = generate_scaffold("my-app", "astro", api_key="")
    assert result is None
