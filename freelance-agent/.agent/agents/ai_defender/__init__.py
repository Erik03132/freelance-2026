"""AI-Defender — Security Agent package.

Importable from other agents. Exposes:
- scan.scan_path        — static regex scan
- deps_scan.scan_all    — external tooling (pip-audit/npm/bandit/gitleaks)
- llm_audit.deep_audit  — LLM deep audit (owasp/mcp frames)
- report.build_report   — unified report -> SECURITY.md + JSON
"""

from .deps_scan import scan_all
from .llm_audit import deep_audit
from .report import build_report, render_markdown, save_report
from .scan import scan_file, scan_path

__all__ = [
    "scan_path",
    "scan_file",
    "scan_all",
    "deep_audit",
    "build_report",
    "render_markdown",
    "save_report",
]
