"""Python API for Artemiy — importable from other agents."""

from .audit import audit_code, audit_file, audit_with_llm
from .component_gen import COMPONENT_TYPES, generate_component
from .frontend_config import DEFAULTS, FRAMEWORKS
from .page_gen import generate_page, generate_scaffold

__all__ = [
    "generate_component",
    "COMPONENT_TYPES",
    "generate_page",
    "generate_scaffold",
    "audit_code",
    "audit_file",
    "audit_with_llm",
    "FRAMEWORKS",
    "DEFAULTS",
]
