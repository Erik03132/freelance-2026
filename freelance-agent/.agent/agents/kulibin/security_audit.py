"""Security audit for Kulibin — static scan + LLM OWASP check."""

from __future__ import annotations

import os
import re

from .llm_client import call_llm
from .perf_config import FILE_EXTENSIONS

try:
    from security import scan_leaks, security_audit as _static_audit
except ImportError:
    def scan_leaks(code):
        return []
    def _static_audit(code):
        return {"score": 0, "passed": 0, "total": 0, "findings": [], "leaks": []}


_EXT_ALL = []
for _exts in FILE_EXTENSIONS.values():
    _EXT_ALL.extend(_exts)
_EXT_ALL += [".html", ".astro"]


def _iter_files(path: str) -> list[str]:
    if os.path.isfile(path):
        return [path] if any(path.endswith(e) for e in _EXT_ALL) else []
    out = []
    for root, _d, files in os.walk(path):
        for f in files:
            if any(f.endswith(e) for e in _EXT_ALL):
                out.append(os.path.join(root, f))
    return out


def security_audit(path: str) -> dict:
    """Static security audit across source files."""
    files = _iter_files(path)
    per_file = {}
    all_leaks = {}
    for fp in files:
        try:
            with open(fp, encoding="utf-8") as f:
                code = f.read()
        except Exception:
            continue
        res = _static_audit(code)
        if res["leaks"]:
            per_file[fp] = res["leaks"]
            for l in res["leaks"]:
                all_leaks[l] = all_leaks.get(l, 0) + 1
    return {
        "files_scanned": len(files),
        "issues_by_file": per_file,
        "summary": dict(sorted(all_leaks.items(), key=lambda x: -x[1])),
    }


def owasp_audit(path: str, api_key: str | None = None, learned_context: str = "") -> str | None:
    """LLM OWASP review (SQLi, XSS, auth, validation)."""
    files = _iter_files(path)[:8]
    snippets = []
    for fp in files:
        try:
            with open(fp, encoding="utf-8") as f:
                snippets.append(f"# {fp}\n{f.read()[:1500]}")
        except Exception:
            continue
    if not snippets:
        return None
    prompt = f"""You are an application security engineer. Review this code against OWASP Top 10.
Focus on: SQL injection, XSS, broken auth, sensitive data exposure, security misconfig,
server-side validation. For each issue give: location, severity, fix.

{chr(10).join(snippets)}

{learned_context}

Return a ranked markdown report."""
    return call_llm(prompt, max_tokens=2200, temperature=0.2, api_key=api_key)
