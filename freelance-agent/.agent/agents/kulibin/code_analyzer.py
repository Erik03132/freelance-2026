"""Static + LLM code analysis for Kulibin (Python + JS/TS)."""

from __future__ import annotations

import os
import re

from .llm_client import call_llm
from .perf_config import EVAL_CRITERIA, FILE_EXTENSIONS, JS_SMELLS, PY_SMELLS


def _iter_files(path: str, languages: list[str]) -> list[str]:
    exts = []
    for lang in languages:
        exts.extend(FILE_EXTENSIONS.get(lang, []))
    found = []
    if os.path.isfile(path):
        if any(path.endswith(e) for e in exts):
            return [path]
        return []
    for root, _dirs, files in os.walk(path):
        for f in files:
            if any(f.endswith(e) for e in exts):
                found.append(os.path.join(root, f))
    return found


def analyze(path: str, languages: list[str] | None = None) -> dict:
    """Static heuristic analysis. Returns summary + per-file findings."""
    languages = languages or ["python", "js", "ts"]
    files = _iter_files(path, languages)
    total = {"python": 0, "js": 0, "ts": 0}
    smells = {}

    for fp in files:
        try:
            with open(fp, encoding="utf-8") as f:
                code = f.read()
        except Exception:
            continue
        lang = _detect_lang(fp)
        if lang == "python":
            patterns = PY_SMELLS
            total["python"] += 1
        elif lang in ("js", "ts"):
            patterns = JS_SMELLS
            total[lang] += 1
        else:
            continue
        for name, pat in patterns:
            n = len(re.findall(pat, code, re.IGNORECASE | re.MULTILINE))
            if n:
                smells[name] = smells.get(name, 0) + n

    return {
        "files_scanned": len(files),
        "by_language": total,
        "smells": dict(sorted(smells.items(), key=lambda x: -x[1])),
        "languages": languages,
    }


def _detect_lang(fp: str) -> str:
    if fp.endswith(".py"):
        return "python"
    if fp.endswith((".ts", ".tsx")):
        return "ts"
    if fp.endswith((".js", ".jsx", ".mjs", ".cjs")):
        return "js"
    return ""


def deep_audit(path: str, api_key: str | None = None, learned_context: str = "") -> str | None:
    """LLM deep audit with concrete improvements."""
    files = _iter_files(path, ["python", "js", "ts"])[:10]
    snippets = []
    for fp in files:
        try:
            with open(fp, encoding="utf-8") as f:
                snippets.append(f"# {fp}\n{f.read()[:1500]}")
        except Exception:
            continue
    if not snippets:
        return None
    prompt = f"""You are a performance & architecture engineer. Audit this codebase:

{chr(10).join(snippets)}

{learned_context}

Return a report:
1. Top performance bottlenecks (ranked)
2. Architecture issues
3. Concrete fixes with code (where short)
4. Priority order"""
    return call_llm(prompt, max_tokens=2500, temperature=0.2, api_key=api_key)
