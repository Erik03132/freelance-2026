"""Unit tests for ai_defender.scan."""

import os
import tempfile

from ai_defender.scan import scan_path, mask_secret


def _write(tmp, name, content):
    path = os.path.join(tmp, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def test_masks_secret():
    assert "sk-or-1dd8..." == mask_secret("sk-or-1dd83e5bf00f4") or "..." in mask_secret("sk-or-1dd83e5bf00f4")


def test_detects_hardcoded_secret():
    with tempfile.TemporaryDirectory() as tmp:
        _write(tmp, "v.py", 'API_KEY = "sk-or-1234567890abcdef"')  # gitleaks:allow
        res = scan_path(tmp)
        patterns = {f["pattern"] for f in res["findings"]}
        assert "hardcoded_secret" in patterns


def test_detects_sql_injection():
    with tempfile.TemporaryDirectory() as tmp:
        _write(tmp, "db.py", 'q = "SELECT * FROM users WHERE name = " + req.body.name')
        res = scan_path(tmp)
        assert any(f["pattern"] == "sql_concat" for f in res["findings"])


def test_clean_code_no_findings():
    with tempfile.TemporaryDirectory() as tmp:
        _write(tmp, "ok.py", 'user = os.environ.get("API_KEY", "")')
        _write(tmp, "ok2.py", 'db.execute("SELECT * FROM u WHERE id = ?", (uid,))')
        res = scan_path(tmp)
        assert res["findings"] == []


def test_skips_git_dir():
    with tempfile.TemporaryDirectory() as tmp:
        g = os.path.join(tmp, ".git")
        os.makedirs(g)
        _write(g, "leak.py", 'TOKEN = "sk-or-1234567890abcdef"')  # gitleaks:allow
        _write(tmp, "real.py", "x = 1")
        res = scan_path(tmp)
        assert all(".git" not in f["file"] for f in res["findings"])
