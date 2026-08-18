"""AI-Defender — dependency & tooling scans (SCA layer).

Runs external tools if available: pip-audit, npm audit, bandit, gitleaks.
Missing tools degrade gracefully — scanner stays usable without them.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path


# Known official package sources. Typosquatters publish lookalikes on the
# "wrong" registry — e.g. PyPI `deepseek-harness` squats the official npm
# `@deepseek-ai/dsh` (Habr #1070296, HZ-4). name -> expected source.
KNOWN_PACKAGE_SOURCES: dict[str, dict] = {
    "deepseek-harness": {
        "expected_registry": "npm",
        "official": "@deepseek-ai/dsh",
        "note": "Официальный DeepSeek Harness — npm @deepseek-ai/dsh. PyPI-deepseek-harness — тайпсквоттинг третьей стороны.",
    },
}

# Packages that attract typosquats. Declared names within edit-distance 2 of a
# target are flagged for manual source verification before install.
_TYPOSQUAT_TARGETS = (
    "openai", "requests", "numpy", "pandas", "tensorflow", "torch", "pip",
    "setuptools", "cryptography", "boto3", "django", "flask", "react",
    "lodash", "express", "axios", "webpack", "deepseek-harness",
)


def _run(cmd: list[str], cwd: str, timeout: int = 120) -> tuple[str, str, int]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return proc.stdout, proc.stderr, proc.returncode
    except FileNotFoundError:
        return "", f"command not found: {cmd[0]}", -1
    except subprocess.TimeoutExpired:
        return "", f"timeout after {timeout}s: {cmd[0]}", -1


def _available(name: str) -> bool:
    return shutil.which(name) is not None


def scan_pip_audit(path: str) -> dict:
    """pip-audit: known CVEs in Python dependencies."""
    if not _available("pip-audit"):
        return {"tool": "pip-audit", "available": False, "findings": [], "error": "pip-audit not installed"}
    reqs = _find_file(path, "requirements*.txt") or _find_file(path, "pyproject.toml")
    if not reqs:
        return {"tool": "pip-audit", "available": True, "findings": [], "note": "no requirements found"}
    out, err, _code = _run(["pip-audit", "-r", str(reqs), "--format", "json", "-l"], cwd=str(Path(reqs).parent))
    try:
        data = json.loads(out)
    except (json.JSONDecodeError, ValueError):
        return {
            "tool": "pip-audit",
            "available": True,
            "findings": [],
            "error": "parse failed",
            "detail": (err or out)[-300:],
        }
    findings = []
    for dep in data.get("dependencies", []):
        for vuln in dep.get("vulns", []):
            findings.append(
                {
                    "package": dep.get("name"),
                    "version": dep.get("version"),
                    "advisory": vuln.get("id"),
                    "severity": "HIGH",
                    "fix": (vuln.get("fix_versions") or [None])[0],
                    "description": vuln.get("description", "")[:200],
                }
            )
    return {"tool": "pip-audit", "available": True, "findings": findings}


def scan_npm_audit(path: str) -> dict:
    """npm audit --json: known CVEs in JS dependencies."""
    if not (Path(path) / "package.json").exists():
        return {"tool": "npm", "available": False, "findings": [], "note": "no package.json"}
    if not _available("npm"):
        return {"tool": "npm", "available": False, "findings": [], "error": "npm not installed"}
    out, _err, _code = _run(["npm", "audit", "--json"], cwd=path, timeout=180)
    try:
        data = json.loads(out)
    except (json.JSONDecodeError, ValueError):
        return {"tool": "npm", "available": True, "findings": [], "error": "parse failed or no lockfile"}
    findings = []
    for adv_id, adv in (data.get("advisories") or {}).items():
        findings.append(
            {
                "package": adv.get("name"),
                "severity": (adv.get("severity") or "HIGH").upper(),
                "advisory": adv_id,
                "fix": (adv.get("range") or ""),
                "description": (adv.get("title") or "")[:200],
            }
        )
    return {"tool": "npm", "available": True, "findings": findings}


_SKIP_DIRS = {".venv", "venv", "node_modules", "__pycache__", "dist", "build", ".git", "site-packages"}


def scan_bandit(path: str) -> dict:
    """bandit: Python SAST (injections, hardcoded secrets, insecure calls)."""
    if not _available("bandit"):
        return {"tool": "bandit", "available": False, "findings": [], "error": "bandit not installed"}
    skip = ",".join(_SKIP_DIRS)
    out, err, code = _run(["bandit", "-r", path, "-x", skip, "-f", "json", "-q"], cwd=path, timeout=180)
    try:
        data = json.loads(out)
    except (json.JSONDecodeError, ValueError):
        return {
            "tool": "bandit",
            "available": True,
            "findings": [],
            "error": "parse failed",
            "detail": (err or out)[-300:],
        }
    if code != 0 and not data.get("results"):
        return {
            "tool": "bandit",
            "available": True,
            "findings": [],
            "error": f"bandit exited {code}",
            "detail": (err or out)[-300:],
        }
    findings = []
    for r in data.get("results", []):
        findings.append(
            {
                "file": r.get("filename"),
                "line": r.get("line_number"),
                "pattern": r.get("test_id"),
                "severity": (r.get("issue_severity") or "MEDIUM").upper(),
                "label": r.get("issue_text", "")[:160],
            }
        )
    return {"tool": "bandit", "available": True, "findings": findings}


def scan_gitleaks(path: str) -> dict:
    """gitleaks: secrets in git history and working tree."""
    if not _available("gitleaks"):
        return {"tool": "gitleaks", "available": False, "findings": [], "error": "gitleaks not installed"}
    out, _err, code = _run(["gitleaks", "git", "--redact", "--exit-code", "0"], cwd=path, timeout=300)
    findings = []
    for line in out.splitlines():
        if "Finding:" in line or "Secret:" in line:
            findings.append({"label": line.strip()[:200]})
    return {"tool": "gitleaks", "available": True, "findings": findings}


def scan_all(path: str) -> list[dict]:
    """Запускает все доступные внешние сканеры."""
    results = [scan_pip_audit(path), scan_npm_audit(path), scan_bandit(path), scan_gitleaks(path), scan_typosquat(path)]
    return [r for r in results if r["available"]]


def _edit_distance(a: str, b: str) -> int:
    """Levenshtein distance, capped at 2 (we only care about close lookalikes)."""
    if a == b:
        return 0
    if abs(len(a) - len(b)) > 2:
        return 99
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[-1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[len(b)]


def _extract_declared_deps(path: str) -> dict[str, list[str]]:
    """Собирает заявленные зависимости: PyPI (requirements/pyproject) + npm (package.json)."""
    deps: dict[str, list[str]] = {"pypi": [], "npm": []}
    root = Path(path) if os.path.isdir(path) else Path(path).parent
    for p in root.rglob("requirements*.txt"):
        if ".git" in p.parts:
            continue
        try:
            for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("-"):
                    continue
                name = re.split(r"[=<>!~ ]", line, 1)[0].strip().lower()
                if name:
                    deps["pypi"].append(name)
        except OSError:
            pass
    pj = root / "package.json"
    if pj.exists():
        try:
            data = json.loads(pj.read_text(encoding="utf-8", errors="replace"))
            for section in ("dependencies", "devDependencies", "peerDependencies"):
                for name in (data.get(section) or {}):
                    deps["npm"].append(name.lower())
        except (OSError, json.JSONDecodeError):
            pass
    pp = root / "pyproject.toml"
    if pp.exists():
        try:
            text = pp.read_text(encoding="utf-8", errors="replace")
            in_deps = False
            for line in text.splitlines():
                if re.match(r"^\s*dependencies\s*=\s*\[", line):
                    in_deps = True
                    continue
                if in_deps:
                    line = line.strip()
                    if line == "]":
                        break
                    m = re.match(r'["\']([^"\']+)["\']', line)
                    if m:
                        name = re.split(r"[=<>!~ ]", m.group(1), 1)[0].strip().lower()
                        if name:
                            deps["pypi"].append(name)
        except OSError:
            pass
    return deps


def scan_typosquat(path: str) -> dict:
    """Supply-chain: verify declared packages come from official sources (HZ-4)."""
    deps = _extract_declared_deps(path)
    findings = []
    seen: set[str] = set()
    for registry, names in deps.items():
        for name in names:
            base = name.split("@", 1)[-1] if registry == "npm" else name
            info = KNOWN_PACKAGE_SOURCES.get(base)
            if info and info["expected_registry"] != registry and base not in seen:
                seen.add(base)
                findings.append(
                    {
                        "package": name,
                        "registry": registry,
                        "severity": "HIGH",
                        "pattern": "typosquat",
                        "label": (
                            f"Тайпсквоттинг-риск: '{name}' заявлен в {registry}, "
                            f"но официальный источник — {info['official']} ({info['expected_registry']}). "
                            f"{info['note']}"
                        ),
                    }
                )
                continue
            for target in _TYPOSQUAT_TARGETS:
                if name != target and _edit_distance(name, target) <= 2 and name not in seen:
                    seen.add(name)
                    findings.append(
                        {
                            "package": name,
                            "registry": registry,
                            "severity": "MEDIUM",
                            "pattern": "typosquat_suspect",
                            "label": f"Похоже на '{target}' (edit-distance <=2) — проверить официальный источник перед установкой.",
                        }
                    )
                    break
    return {"tool": "typosquat", "available": True, "findings": findings}


def _find_file(path: str, pattern: str) -> str | None:
    root = Path(path) if os.path.isdir(path) else Path(path).parent
    for p in root.rglob(pattern):
        if ".git" not in p.parts:
            return str(p)
    return None
