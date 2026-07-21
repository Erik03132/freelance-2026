"""Python API for Artemiy — importable from other agents."""

from .audit import audit_code, audit_file, audit_with_llm
from .component_gen import COMPONENT_TYPES, generate_component
from .frontend_config import DEFAULTS, FRAMEWORKS
from .brand_md import fetch_brand_design
from .page_gen import generate_page, generate_scaffold
from .slide_gen import generate_slides

__all__ = [
    "COMPONENT_TYPES",
    "DEFAULTS",
    "FRAMEWORKS",
    "audit_code",
    "audit_file",
    "audit_with_llm",
    "fetch_brand_design",
    "generate_component",
    "generate_page",
    "generate_scaffold",
    "generate_slides",
]
