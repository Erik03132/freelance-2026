"""Tests for security scanning — all 7 SECURITY_SMELLS patterns + audit scoring."""

import os
import sys

_AGENTS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _AGENTS not in sys.path:
    sys.path.insert(0, _AGENTS)

from security import SECURITY_SMELLS, scan_leaks, security_audit  # noqa: E402

# ── Fixture code snippets (positive = should match) ──────────────────────

HARDCODED_SECRET = '''\
API_KEY = "sk-1234567890abcdef"
password = 'hunter2production'
SECRET = "supersecretvalue123"
'''

ENV_IN_FRONTEND = '''\
import dotenv
from '../../.env' import load
loadEnv('.env.local')
'''

PUBLIC_SECRET_VAR = '''\
const key = import.meta.env.VITE_API_KEY;
const token = process.env.NEXT_PUBLIC_SECRET;
'''

SECRET_IN_LOG = '''\
console.log("Password:", password);
print(f"Token: {token}")
logger.error("API key leaked", api_key=key)
'''

DANGEROUS_INNERHTML = '''\
element.innerHTML = userContent;
div.dangerouslySetInnerHTML = {__html: raw};
v-html="dynamicContent"
$(".container").html(response);
'''

EVAL_USAGE = '''\
eval(userInput);
exec(code);
setTimeout("alert('xss')", 100);
'''

SQL_CONCAT = '''\
query = "SELECT * FROM users WHERE id = " + request.params.id
cursor.execute("INSERT INTO logs VALUES (" + req.body.data + ")")
db.query(f"UPDATE users SET name={params.name}")
'''

# ── Negative fixtures (should NOT match) ────────────────────────────────

SAFE_CODE = '''\
import os
API_KEY = os.environ.get("API_KEY")
logger.info("Processing request")
element.textContent = safeContent;
result = int("1 + 1")
query = "SELECT * FROM users WHERE id = %s"
'''

SAFE_ENV_IMPORT = '''\
import os
from config import settings
'''


# ── Tests: scan_leaks positive cases ────────────────────────────────────

def test_hardcoded_secret_detected():
    leaks = scan_leaks(HARDCODED_SECRET)
    assert "hardcoded_secret" in leaks


def test_env_in_frontend_detected():
    leaks = scan_leaks(ENV_IN_FRONTEND)
    assert "env_in_frontend" in leaks


def test_public_secret_var_detected():
    leaks = scan_leaks(PUBLIC_SECRET_VAR)
    assert "public_secret_var" in leaks


def test_secret_in_log_detected():
    leaks = scan_leaks(SECRET_IN_LOG)
    assert "secret_in_log" in leaks


def test_dangerous_innerhtml_detected():
    leaks = scan_leaks(DANGEROUS_INNERHTML)
    assert "dangerous_innerhtml" in leaks


def test_eval_usage_detected():
    leaks = scan_leaks(EVAL_USAGE)
    assert "eval_usage" in leaks


def test_sql_concat_detected():
    leaks = scan_leaks(SQL_CONCAT)
    assert "sql_concat" in leaks


# ── Tests: scan_leaks negative cases ────────────────────────────────────

def test_safe_code_no_leaks():
    leaks = scan_leaks(SAFE_CODE)
    assert leaks == []


def test_safe_env_import_no_leak():
    leaks = scan_leaks(SAFE_ENV_IMPORT)
    assert "env_in_frontend" not in leaks


def test_empty_code_no_leaks():
    assert scan_leaks("") == []


# ── Tests: all 7 patterns exist ─────────────────────────────────────────

def test_all_seven_patterns_registered():
    expected = {
        "hardcoded_secret", "env_in_frontend", "public_secret_var",
        "secret_in_log", "dangerous_innerhtml", "eval_usage", "sql_concat",
    }
    assert set(SECURITY_SMELLS.keys()) == expected


def test_all_patterns_are_regex_strings():
    for name, pat in SECURITY_SMELLS.items():
        assert isinstance(pat, str), f"{name} should be a regex string"
        assert len(pat) > 10, f"{name} pattern too short"


# ── Tests: security_audit scoring ───────────────────────────────────────

def test_clean_code_perfect_score():
    result = security_audit(SAFE_CODE)
    assert result["score"] == 100
    assert result["passed"] == 7
    assert result["total"] == 7
    assert result["leaks"] == []
    assert all(f.startswith("✅") for f in result["findings"])


def test_dirty_code_zero_score():
    all_bad = HARDCODED_SECRET + ENV_IN_FRONTEND + PUBLIC_SECRET_VAR + \
              SECRET_IN_LOG + DANGEROUS_INNERHTML + EVAL_USAGE + SQL_CONCAT
    result = security_audit(all_bad)
    assert result["score"] == 0
    assert result["passed"] == 0
    assert result["total"] == 7
    assert len(result["leaks"]) == 7
    assert all(f.startswith("⚠") for f in result["findings"])


def test_partial_score():
    result = security_audit(HARDCODED_SECRET)
    assert 0 < result["score"] < 100
    assert result["passed"] < 7
    assert "hardcoded_secret" in result["leaks"]


def test_audit_findings_count_matches_total():
    result = security_audit("x = 1")
    assert len(result["findings"]) == result["total"] == 7
