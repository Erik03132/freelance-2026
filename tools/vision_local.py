#!/usr/bin/env python3
"""LFM-1/LFM-2 — локальный vision-коннектор (LFM2.5-VL-3B) для 8ГБ Mac.

Backends (pluggable):
  - "mlx_vlm": Apple Silicon, `pip install mlx-vlm`, модель
    LiquidAI/LFM2.5-VL-3B-MLX-8bit (~3ГБ RAM, влезает в 8ГБ Mac).
  - "ollama":   `ollama pull <model>` (проверить имя в library), `ollama run`.

Используется агентами (Angela/мультиагент) для on-device vision (ADR-002, приватно):
документы/OCR+layout, скрины/UI, grounding (bounding box по NL), vision+function-calling.

Лицензия LFM1.0 (LFM-3): open-weight, бесплатно коммерчески до $10M выручки.
Перед коммерческим деплоем вскрыть LICENSE в репозитории.
"""

from __future__ import annotations

import shutil
import subprocess
import sys

DEFAULT_MODEL_MLX = "LiquidAI/LFM2.5-VL-3B-MLX-8bit"
DEFAULT_MODEL_OLLAMA = "lfm2.5-vl"  # проверить наличие в Ollama library


def backend_available(backend: str) -> bool:
    if backend == "mlx_vlm":
        try:
            import mlx_vlm  # noqa: F401

            return True
        except ImportError:
            return False
    if backend == "ollama":
        return shutil.which("ollama") is not None
    return False


def understand(
    image_path: str,
    prompt: str,
    backend: str = "mlx_vlm",
    model: str | None = None,
) -> str:
    """Возвращает текст-ответ локальной VLM по изображению + промпту."""
    model = model or (DEFAULT_MODEL_MLX if backend == "mlx_vlm" else DEFAULT_MODEL_OLLAMA)
    if backend == "mlx_vlm":
        if not backend_available("mlx_vlm"):
            raise RuntimeError("mlx_vlm не установлен: pip install mlx-vlm")
        cmd = [
            sys.executable, "-m", "mlx_vlm.generate",
            "--model", model, "--image", image_path, "--prompt", prompt,
        ]
        out = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return out.stdout.strip()
    if backend == "ollama":
        if not backend_available("ollama"):
            raise RuntimeError("ollama не найден в PATH")
        cmd = ["ollama", "run", model, f"{prompt}\n[image:{image_path}]"]
        out = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return out.stdout.strip()
    raise ValueError(f"неизвестный backend: {backend}")


def detect_objects(
    image_path: str,
    query: str,
    backend: str = "mlx_vlm",
    model: str | None = None,
) -> str:
    """Grounding: найти объекты по естественному описанию (bounding box)."""
    prompt = (
        "Locate the following object(s) in the image and return bounding boxes "
        f"in [x1,y1,x2,y2] format: {query}"
    )
    return understand(image_path, prompt, backend=backend, model=model)
