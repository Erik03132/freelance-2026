"""Eval for LFM-1/LFM-2 vision connector (LFM2.5-VL-3B) — offline logic.

Запуск: python3 tools/tests/eval_vision_local.py
Реальный прогон модели (MLX/Ollama) — на Mac пользователя (LFM-4).
"""

from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.vision_local import understand, backend_available  # noqa: E402


def _run() -> tuple[int, list[str]]:
    fails: list[str] = []

    # TP-1: неизвестный backend -> ValueError
    try:
        understand("x.jpg", "p", backend="bogus")
        fails.append("TP-1: неизвестный backend не выбросил ValueError")
    except ValueError:
        pass

    # TP-2: mlx_vlm недоступен в CI -> RuntimeError (без скачивания весов)
    if importlib.util.find_spec("mlx_vlm") is None:
        try:
            understand("x.jpg", "p", backend="mlx_vlm")
            fails.append("TP-2: mlx_vlm недоступен, ожидали RuntimeError")
        except RuntimeError:
            pass

    # TP-3: detect_objects формирует grounding-промпт и возвращает результат
    captured: dict = {}

    import tools.vision_local as vl

    vl.understand = lambda *a, **k: captured.update({"args": a, "kw": k}) or "ok"
    res = vl.detect_objects("img.png", "red car")
    if "red car" not in captured["args"][1] or "bounding box" not in captured["args"][1]:
        fails.append(f"TP-3: grounding-промпт некорректен: {captured['args'][1]}")
    if res != "ok":
        fails.append("TP-3: detect_objects не вернул результат")

    # TP-4: backend_available не падает на известных бэкендах
    try:
        _ = backend_available("mlx_vlm")
        _ = backend_available("ollama")
    except Exception as e:  # noqa: BLE001
        fails.append(f"TP-4: backend_available упал: {e}")

    return len(fails), fails


if __name__ == "__main__":
    n, fails = _run()
    if fails:
        print(f"❌ EVAL FAILED ({n}):")
        for f in fails:
            print(f"  - {f}")
        sys.exit(1)
    print(
        "✅ EVAL PASSED — LFM-1/LFM-2 vision connector logic OK (модель прогоняется на Mac, LFM-4)"
    )
