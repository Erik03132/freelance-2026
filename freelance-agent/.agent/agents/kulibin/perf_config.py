"""Default config for Kulibin (performance & innovation engineer)."""

from __future__ import annotations

LANGUAGES = ["python", "js", "ts"]

FILE_EXTENSIONS = {
    "python": [".py"],
    "js": [".js", ".jsx", ".mjs", ".cjs"],
    "ts": [".ts", ".tsx"],
}

# Heuristics for local static analysis (cheap, no LLM)
PY_SMELLS = [
    ("bare_except", r"except\s*:"),
    ("broad_except", r"except\s+Exception"),
    ("print_debug", r"\bprint\("),
    ("todo_marker", r"#\s*TODO|FIXME"),
    ("hardcoded_secret", r"(password|api_key|secret|token)\s*=\s*['\"][^'\"]+['\"]"),
    ("sync_sleep", r"\btime\.sleep\("),
    ("eval_usage", r"\b(eval|exec)\("),
]

JS_SMELLS = [
    ("console_log", r"console\.(log|debug|warn)\("),
    ("todo_marker", r"//\s*TODO|FIXME"),
    ("var_usage", r"\bvar\s+"),
    ("any_type", r":\s*any\b"),
    ("hardcoded_secret", r"(password|apiKey|secret|token)\s*[:=]\s*['\"][^'\"]+['\"]"),
    ("nested_callbacks", r"}\s*\)\s*\)\s*\)"),
]

EVAL_CRITERIA = [
    "Размер бандла/зависимости (minimize)",
    "Зрелость (stable release, активный maint)",
    "Применимость к нашим проектам (Astro/React/Python)",
    "Лицензия (MIT/Apache предпочтительно)",
    "Совместимость (backward compat)",
]
