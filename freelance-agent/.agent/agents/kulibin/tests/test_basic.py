from kulibin import (
    EVAL_CRITERIA, FILE_EXTENSIONS, LANGUAGES,
    analyze, deep_audit, scout, evaluate,
    generate_prototype, benchmark_snippet,
    security_audit, owasp_audit,
)


def test_languages():
    assert "python" in LANGUAGES
    assert len(LANGUAGES) >= 3


def test_file_extensions():
    ext_set = {e for exts in FILE_EXTENSIONS.values() for e in exts}
    assert ".py" in ext_set
    assert len(FILE_EXTENSIONS) >= 3


def test_eval_criteria():
    assert len(EVAL_CRITERIA) >= 3


def test_analyze_non_existent():
    result = analyze("/nonexistent/path")
    assert result["files_scanned"] == 0


def test_security_audit_non_existent():
    result = security_audit("/nonexistent/path")
    assert result["files_scanned"] == 0


def test_deep_audit_no_key():
    result = deep_audit("/nonexistent/path", api_key="")
    assert result is None


def test_scout_no_key():
    result = scout("rate limiting in FastAPI", api_key="")
    assert result is None


def test_evaluate_no_key():
    result = evaluate("FastAPI", api_key="")
    assert result is None


def test_generate_prototype_no_key():
    result = generate_prototype("in-memory cache with TTL", "python", api_key="")
    assert result is None


def test_benchmark_snippet_no_key():
    result = benchmark_snippet("def foo(): pass", api_key="")
    assert result is None


def test_owasp_audit_no_key():
    result = owasp_audit("/nonexistent/path", api_key="")
    assert result is None
