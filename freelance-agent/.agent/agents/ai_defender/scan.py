"""AI-Defender — static security scanner (no LLM).

Detects secret leaks, injections, dangerous sinks. Deterministic regex layer
used as fast fallback before external tools (gitleaks/bandit) and LLM audit.
"""

from __future__ import annotations

import os
import re

def _is_secret_log(line: str) -> re.Match | None:
    """Секрет пишется в лог: логирующий вызов + конкатенация/интерполяция + секрет-слово."""
    if not re.search(r"(?i)(console\.\w+|print|logger\.\w+|logging\.\w+)\s*\(", line):
        return None
    if "+" not in line and "${" not in line and "f\"" not in line.lower() and "f'" not in line.lower():
        return None
    return re.search(r"(?i)(password|passwd|secret|token|api[_-]?key|authorization|apikey)", line)


# (pattern_id, regex-or-callable, severity, human-readable label)
SECURITY_SMELLS: list[tuple[str, re.Pattern | object, str, str]] = [
    (
        "hardcoded_secret",
        re.compile(
            r"""(?i)(password|passwd|secret|token|api[_-]?key|access[_-]?key|"""
            r"""private[_-]?key|client[_-]?secret)\s*[:=]\s*["'][^"']{8,}["']"""
        ),
        "CRITICAL",
        "Захардкоженный секрет в коде",
    ),
    (
        "public_secret_var",
        re.compile(r"""(?i)(VITE_|NEXT_PUBLIC_|PUBLIC_|REACT_APP_)(API|SECRET|TOKEN|KEY|PASSWORD)"""),
        "CRITICAL",
        "Секретная переменная уходит в браузер",
    ),
    (
        "sql_concat",
        re.compile(r"""(?i)(SELECT|INSERT|UPDATE|DELETE|WHERE)\b[^;]*\+\s*(request|req\.|params|body|query|user_input|name|message)"""),
        "HIGH",
        "SQL-конкатенация с пользовательским вводом (SQLi)",
    ),
    (
        "command_injection",
        re.compile(r"""(?i)(os\.(system|popen)|subprocess\.(run|call|Popen)|exec|spawn)\s*\([^)]*(request|req\.|params|body|message|input|user|command)"""),
        "HIGH",
        "Командная инъекция (shell-вызов с пользовательским вводом)",
    ),
    (
        "eval_usage",
        re.compile(r"""(?i)\b(eval|exec)\s*\([^)]*(request|req\.|params|body|input|message|text|content|data)"""),
        "HIGH",
        "eval/exec с недоверенным вводом",
    ),
    (
        "pickle_loads",
        re.compile(r"""(?i)(pickle|marshal)\.(loads|load)\s*\("""),
        "HIGH",
        "Небезопасная десериализация (pickle)",
    ),
    (
        "path_traversal",
        re.compile(r"""(?i)(open|join|send_file|read_text|read_bytes|read)\s*\([^)]*(request\.|req\.|params|filename|user_input|args)"""),
        "MEDIUM",
        "Возможный path traversal / недоверенный путь",
    ),
    (
        "dangerous_innerhtml",
        re.compile(r"""(?i)(innerHTML|outerHTML|dangerouslySetInnerHTML|v-html|insertAdjacentHTML)\s*=|\.html\([^)]*\)"""),
        "MEDIUM",
        "XSS-риск: установка HTML из кода",
    ),
    (
        "secret_in_log",
        _is_secret_log,
        "MEDIUM",
        "Секрет пишется в лог",
    ),
    (
        "weak_crypto",
        re.compile(r"""(?i)(hashlib\.(md5|sha1)|_md5|\.digest\(\))\s*\([^)]*(password|token|secret)"""),
        "MEDIUM",
        "Слабый хеш для пароля/токена",
    ),
    (
        "shell_true",
        re.compile(r"""(?i)subprocess\.(run|call|Popen)\([^)]*shell\s*=\s*True"""),
        "MEDIUM",
        "shell=True (риск инъекции)",
    ),
    (
        "request_no_timeout",
        re.compile(r"""(?i)requests\.(get|post|put|delete|patch)\((?!.*timeout\s*=)[^)]*\)"""),
        "LOW",
        "HTTP-запрос без таймаута (проверить)",
    ),
    (
        "env_in_frontend",
        re.compile(r"""(?i)(import\s+.*\.env|from\s+["']\.\.?/.*\.env["']|process\.env\.\w+\s+in\s+client|loadEnv\(["'][^"']*\.env)"""),
        "LOW",
        "env подтягивается во фронтенд",
    ),
]

_SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
_MASK = re.compile(r"([A-Za-z0-9_\-]{4})[A-Za-z0-9_\-]{8,}")


def mask_secret(value: str) -> str:
    """Маскируем найденный секрет: sk-or-1dd83e5b... -> sk-or-1dd8..."""
    return _MASK.sub(r"\1...", value)


def _iter_files(path: str, exts: set[str] | None = None) -> list[str]:
    if exts is None:
        exts = {
            ".py", ".js", ".jsx", ".ts", ".tsx", ".html", ".astro", ".vue",
            ".go", ".rs", ".php", ".java", ".rb", ".sh", ".yml", ".yaml",
            ".json", ".env", ".toml", ".ini", ".conf",
        }
    if os.path.isfile(path):
        return [path] if os.path.splitext(path)[1] in exts or "env" in path else []
    out = []
    for root, _dirs, files in os.walk(path):
        parts = root.split(os.sep)
        if any(part in {".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build", "site-packages"} for part in parts):
            continue
        for f in files:
            ext = os.path.splitext(f)[1]
            if ext in exts or f == ".env" or f.endswith(".env"):
                out.append(os.path.join(root, f))
    return out


def scan_file(path: str) -> list[dict]:
    """Сканирует один файл. Возвращает список находок."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return []
    findings = []
    for i, line in enumerate(lines, start=1):
        for pid, pattern, severity, label in SECURITY_SMELLS:
            m = pattern(line) if callable(pattern) else pattern.search(line)
            if not m:
                continue
            snippet = line.strip()[:160]
            findings.append(
                {
                    "file": path,
                    "line": i,
                    "pattern": pid,
                    "severity": severity,
                    "label": label,
                    "snippet": mask_secret(snippet),
                }
            )
    return findings


def scan_path(path: str) -> dict:
    """Сканирует файл/директорию. Возвращает отчёт."""
    files = _iter_files(path)
    findings = []
    for fp in files:
        findings.extend(scan_file(fp))
    findings.sort(key=lambda f: (_SEVERITY_ORDER.get(f["severity"], 9), f["file"], f["line"]))
    by_pattern: dict[str, int] = {}
    for f in findings:
        by_pattern[f["pattern"]] = by_pattern.get(f["pattern"], 0) + 1
    return {
        "files_scanned": len(files),
        "findings": findings,
        "by_pattern": by_pattern,
        "by_severity": {
            sev: sum(1 for f in findings if f["severity"] == sev)
            for sev in _SEVERITY_ORDER
        },
        "summary": sorted(by_pattern.items(), key=lambda kv: -kv[1]),
    }
