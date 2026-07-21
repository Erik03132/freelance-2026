"""CLI smoke tests — verify all 4 agents can be invoked without crashing."""

import os
import subprocess
import sys

import pytest

_AGENTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON = sys.executable
_HAS_KEY = bool(
    os.environ.get("OPENROUTER_API_KEY")
    or os.path.exists(os.path.join(os.path.dirname(_AGENTS), ".env"))
    or os.path.exists(os.path.join(os.path.dirname(os.path.dirname(_AGENTS)), ".env"))
)


def _run(args, timeout=15, no_key=False):
    """Run CLI command, return (exit_code, stdout, stderr).

    If no_key=True, run in an isolated directory without .env access.
    """
    cwd = _AGENTS
    if no_key:
        import tempfile
        cwd = tempfile.mkdtemp()
    result = subprocess.run(
        [PYTHON, "-m"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.returncode, result.stdout, result.stderr


# ── Artemiy ─────────────────────────────────────────────────────────────

def test_artemiy_help():
    rc, out, err = _run(["artemiy", "--help"])
    assert rc == 0
    assert "Artemiy" in out or "Frontend" in out


def test_artemiy_list_components():
    rc, out, err = _run(["artemiy", "--list-components"])
    assert rc == 0
    assert "button" in out.lower()


def test_artemiy_list_frameworks():
    rc, out, err = _run(["artemiy", "--list-frameworks"])
    assert rc == 0
    assert "astro" in out.lower()


@pytest.mark.skipif(_HAS_KEY, reason="API key available — would make real LLM call")
def test_artemiy_no_key_returns_none():
    rc, out, err = _run(["artemiy", "--component", "button", "--spec", "test"])
    assert rc == 0 or "error" not in err.lower()


# ── Kulibin ─────────────────────────────────────────────────────────────

def test_kulibin_help():
    rc, out, err = _run(["kulibin", "--help"])
    assert rc == 0
    assert "Kulibin" in out or "Engineering" in out


def test_kulibin_list_languages():
    rc, out, err = _run(["kulibin", "--list-languages"])
    assert rc == 0
    assert "python" in out.lower()


def test_kulibin_list_criteria():
    rc, out, err = _run(["kulibin", "--list-criteria"])
    assert rc == 0
    assert len(out.strip()) > 0


def test_kulibin_audit_nonexistent():
    rc, out, err = _run(["kulibin", "--audit", "/nonexistent/path"])
    # Should handle gracefully
    assert rc == 0 or "error" in out.lower() or "not found" in out.lower()


# ── Sherl ───────────────────────────────────────────────────────────────

def test_sherl_help():
    rc, out, err = _run(["sherl", "--help"])
    assert rc == 0
    assert "Sherl" in out or "Research" in out


def test_sherl_list_providers():
    rc, out, err = _run(["sherl", "--list-providers"])
    assert rc == 0
    assert len(out.strip()) > 0


@pytest.mark.skipif(_HAS_KEY, reason="API key available — would make real LLM call")
def test_sherl_no_key_returns_none():
    rc, out, err = _run(["sherl", "--research", "test query"])
    assert rc == 0 or "error" not in err.lower()


# ── Rembrandt ───────────────────────────────────────────────────────────

def test_rembrandt_help():
    rc, out, err = _run(["rembrandt", "--help"])
    assert rc == 0
    assert "Rembrandt" in out or "Designer" in out


def test_rembrandt_list_components():
    rc, out, err = _run(["rembrandt", "--list-components"])
    assert rc == 0
    assert "button" in out.lower()


def test_rembrandt_list_brands():
    rc, out, err = _run(["rembrandt", "--list-brands"])
    assert rc == 0
    assert len(out.strip()) > 0


@pytest.mark.skipif(_HAS_KEY, reason="API key available — would make real LLM call")
def test_rembrandt_no_key_returns_none():
    rc, out, err = _run(["rembrandt", "--component", "button", "--spec", "test"])
    assert rc == 0 or "error" not in err.lower()
