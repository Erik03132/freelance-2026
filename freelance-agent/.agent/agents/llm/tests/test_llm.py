"""Tests for the shared LLM client package."""

import os
import sys
import tempfile

_AGENTS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _AGENTS not in sys.path:
    sys.path.insert(0, _AGENTS)

from llm import (  # noqa: E402
    DEFAULT_MODEL,
    ROUTE,
    _compress,
    _find_env,
    _load_key,
    call_llm,
    load_openrouter_key,
    load_perplexity_key,
    load_serper_key,
)


# ── Constants ───────────────────────────────────────────────────────────

def test_default_model():
    assert DEFAULT_MODEL == "deepseek/deepseek-chat-v3-0324"


def test_route_has_simple_and_complex():
    assert "simple" in ROUTE
    assert "complex" in ROUTE
    assert ROUTE["simple"] == DEFAULT_MODEL


# ── _find_env ───────────────────────────────────────────────────────────

def test_find_env_with_dotenv(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=bar\n")
    result = _find_env(start=str(tmp_path / "fake_file.py"))
    assert result == str(env_file)


def test_find_env_without_dotenv(tmp_path):
    result = _find_env(start=str(tmp_path / "fake_file.py"))
    assert result == ""


# ── _load_key ───────────────────────────────────────────────────────────

def test_load_key_from_dotenv(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("OPENROUTER_API_KEY=sk-test-123\nOTHER=value\n")
    key = _load_key("OPENROUTER_API_KEY", start=str(tmp_path / "fake.py"))
    assert key == "sk-test-123"


def test_load_key_missing_returns_env_or_empty(tmp_path):
    key = _load_key("NONEXISTENT_KEY", start=str(tmp_path / "fake.py"))
    assert key == ""


def test_load_key_env_var_fallback(monkeypatch):
    monkeypatch.setenv("TEST_LLM_KEY_999", "from-env")
    key = _load_key("TEST_LLM_KEY_999", start="/nonexistent/path/fake.py")
    assert key == "from-env"


def test_load_key_ignores_comments(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("# OPENROUTER_API_KEY=sk-commented\nOPENROUTER_API_KEY=sk-real\n")
    key = _load_key("OPENROUTER_API_KEY", start=str(tmp_path / "fake.py"))
    assert key == "sk-real"


# ── load_*_key convenience functions ────────────────────────────────────

def test_load_openrouter_key_delegates_to_load_key(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("OPENROUTER_API_KEY=sk-or-test\n")
    key = load_openrouter_key(start=str(tmp_path / "fake.py"))
    assert key == "sk-or-test"


def test_load_serper_key(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("SERPER_API_KEY=serper-123\n")
    key = load_serper_key(start=str(tmp_path / "fake.py"))
    assert key == "serper-123"


def test_load_perplexity_key(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("PERPLEXITY_API_KEY=pplx-456\n")
    key = load_perplexity_key(start=str(tmp_path / "fake.py"))
    assert key == "pplx-456"


# ── _compress ───────────────────────────────────────────────────────────

def test_compress_short_text_unchanged():
    assert _compress("hello") == "hello"


def test_compress_long_text_truncated():
    long = "x" * 2000
    result = _compress(long, max_chars=100)
    assert len(result) < len(long)
    assert result.endswith("\n...[truncated]")


def test_compress_exact_boundary():
    text = "a" * 1500
    assert _compress(text) == text


# ── call_llm ────────────────────────────────────────────────────────────

def test_call_llm_no_key_returns_none(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    result = call_llm("test", api_key="")
    assert result is None
