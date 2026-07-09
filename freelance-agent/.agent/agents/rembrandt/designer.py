"""RembrandtDesigner — high-level wrapper (compatible with ai-eggs callers)."""

from __future__ import annotations

from .brand_system import (
    BrandSystem,
    DesignToken,
    INCUBIRD_DEFAULT,
    load_brand,
)
from .component_generator import COMPONENT_TYPES, generate_component
from .design_generator import generate_design_md
from .image_generator import download_image, leonardo_generate


class RembrandtDesigner:
    """Convenience facade over Rembrandt's generation modules."""

    def __init__(self, brand: BrandSystem | None = None):
        self.brand = brand or INCUBIRD_DEFAULT

    def generate_component(self, component_type: str, spec: str = "") -> str | None:
        return generate_component(component_type, spec, self.brand)

    def generate_design(self, brief: str) -> str | None:
        return generate_design_md(brief)

    def generate_cover(self, topic: str, context: str = "", model: str = "phoenix") -> str | None:
        """Generate a cover image and return its URL (or local path if downloaded)."""
        prompt = topic
        if context:
            prompt = f"{topic}. {context}"
        return leonardo_generate(prompt, model=model)

    def download(self, url: str, output_path: str) -> bool:
        return download_image(url, output_path)
