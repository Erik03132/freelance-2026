"""Security scanning — shared static checks for generated/audited code.

Reusable by generators (guardrail) and Kulibin (security-lint) WITHOUT an LLM.
"""

from __future__ import annotations

import re

# Static patterns that indicate a credential/secret leak in shipped code
SECURITY_SMELLS = {
    "hardcoded_secret": r"""(?i)(password|passwd|api[_-]?key|apikey|secret|token|access[_-]?key|private[_-]?key)\s*[:=]\s*["'][^"']{8,}["']""",
    "env_in_frontend": r"""(?i)(import\s+.*\.env|from\s+["']\.\.?/.*\.env["']|loadEnv\(["'][^"']*\.env)""",
    "public_secret_var": r"""(?i)(VITE_|NEXT_PUBLIC_|PUBLIC_)(API|SECRET|TOKEN|KEY)""",
    "secret_in_log": r"""(?i)(console\.(log|error|warn)|print|logger\.(info|debug|error))\s*\([^)]*(password|secret|token|api[_-]?key)""",
    "dangerous_innerhtml": r"""(?i)(innerHTML|dangerouslySetInnerHTML|v-html|insertAdjacentHTML)\s*=|\.html\([^)]*\)""",
    "eval_usage": r"""(?i)\b(eval|exec|setTimeout\(\s*["'])""",
    "sql_concat": r"""(?i)(SELECT|INSERT|UPDATE|DELETE).*\+.*(request|req\.|params|body|query)""",
}


def scan_leaks(code: str) -> list[str]:
    """Return list of human-readable leak warnings found in code."""
    warnings = []
    for name, pat in SECURITY_SMELLS.items():
        if re.search(pat, code, re.IGNORECASE | re.MULTILINE):
            warnings.append(name)
    return warnings


def security_audit(code: str) -> dict:
    """Static security audit. Returns score + findings."""
    findings = []
    score = 0
    total = len(SECURITY_SMELLS)
    for name, pat in SECURITY_SMELLS.items():
        if re.search(pat, code, re.IGNORECASE | re.MULTILINE):
            findings.append(f"⚠ {name}")
        else:
            findings.append(f"✅ {name}")
            score += 1
    return {
        "score": round(100 * score / total),
        "passed": score,
        "total": total,
        "findings": findings,
        "leaks": scan_leaks(code),
    }
