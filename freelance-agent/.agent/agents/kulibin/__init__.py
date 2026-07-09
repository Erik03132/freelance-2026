"""Python API for Kulibin — importable from other agents."""

from .code_analyzer import analyze, deep_audit
from .lib_scout import evaluate, scout
from .perf_config import EVAL_CRITERIA, FILE_EXTENSIONS, LANGUAGES
from .proto import benchmark_snippet, generate_prototype
from .security_audit import owasp_audit, security_audit

__all__ = [
    "analyze",
    "deep_audit",
    "scout",
    "evaluate",
    "generate_prototype",
    "benchmark_snippet",
    "security_audit",
    "owasp_audit",
    "LANGUAGES",
    "FILE_EXTENSIONS",
    "EVAL_CRITERIA",
]
