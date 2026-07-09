"""Shared security scanning package.

Importable: `from security import scan_leaks, security_audit, SECURITY_SMELLS`.
Safe to import from any agent (pure static, no LLM, no external deps).
"""

from .scan import SECURITY_SMELLS, scan_leaks, security_audit

__all__ = ["scan_leaks", "security_audit", "SECURITY_SMELLS"]
