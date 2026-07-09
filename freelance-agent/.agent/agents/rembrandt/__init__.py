"""🔨 Rembrandt — Universal Designer Agent package (global location).

Moved from projects/ai-eggs/agent/ to freelance-agent/.agent/agents/rembrandt/.
Python API + CLI (python3 -m rembrandt).
"""

from .brand_system import (
    BrandSystem,
    DesignToken,
    INCUBIRD_DEFAULT,
    load_brand,
)
from .component_generator import COMPONENT_TYPES, generate_component
from .design_generator import generate_design_md, render_design_md
from .designer import RembrandtDesigner
from .image_generator import download_image, leonardo_generate

__all__ = [
    "BrandSystem",
    "DesignToken",
    "INCUBIRD_DEFAULT",
    "load_brand",
    "generate_component",
    "COMPONENT_TYPES",
    "generate_design_md",
    "render_design_md",
    "RembrandtDesigner",
    "leonardo_generate",
    "download_image",
]
