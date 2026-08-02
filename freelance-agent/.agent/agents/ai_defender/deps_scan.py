"""AI-Defender — dependency & tooling scans (SCA layer).

Runs external tools if available: pip-audit, npm audit, bandit, gitleaks.
Missing tools degrade gracefully — scanner stays usable without them.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path


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
    results = [scan_pip_audit(path), scan_npm_audit(path), scan_bandit(path), scan_gitleaks(path)]
    return [r for r in results if r["available"]]


def _find_file(path: str, pattern: str) -> str | None:
    root = Path(path) if os.path.isdir(path) else Path(path).parent
    for p in root.rglob(pattern):
        if ".git" not in p.parts:
            return str(p)
    return None
