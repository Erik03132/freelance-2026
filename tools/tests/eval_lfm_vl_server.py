"""Eval for LFM-1 server message parsing (offline, no mlx_vlm needed).

Запуск: python3 tools/tests/eval_lfm_vl_server.py
"""

from __future__ import annotations

import base64
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.lfm_vl_server import extract_text_and_image, resolve_image  # noqa: E402


def _run() -> tuple[int, list[str]]:
    fails: list[str] = []

    # TP-1: текст-only
    p, img = extract_text_and_image([{"role": "user", "content": "привет"}])
    if p != "привет" or img is not None:
        fails.append(f"TP-1: text-only некорректно: p={p!r} img={img!r}")

    # TP-2: система+юзер текст собираются
    p, img = extract_text_and_image([
        {"role": "system", "content": "ты помощник"},
        {"role": "user", "content": "что на фото?"},
    ])
    if "помощник" not in p or "что на фото" not in p or img is not None:
        fails.append(f"TP-2: сбор текста некорректен: {p!r}")

    # TP-3: content-массив с image_url (data URI)
    data = "data:image/png;base64," + base64.b64encode(b"\x89PNG\r\n").decode()
    p, img = extract_text_and_image([
        {"role": "user", "content": [
            {"type": "text", "text": "опиши"},
            {"type": "image_url", "image_url": {"url": data}},
        ]},
    ])
    if p != "опиши" or img is None:
        fails.append(f"TP-3: image_url не извлечён: p={p!r} img={img!r}")
    else:
        path = resolve_image(img)
        if not path or not os.path.exists(path):
            fails.append("TP-3: data URI не сохранён в файл")
        else:
            # cleanup
            try:
                os.remove(path)
            except OSError:
                pass

    # TP-4: несколько картинок — берётся первая
    p, img = extract_text_and_image([
        {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": "file:///tmp/a.png"}},
            {"type": "image_url", "image_url": {"url": "file:///tmp/b.png"}},
        ]},
    ])
    if img != "file:///tmp/a.png":
        fails.append(f"TP-4: взята не первая картинка: {img!r}")

    # TP-5: resolve_image локальный путь
    if resolve_image("/abs/path.jpg") != "/abs/path.jpg":
        fails.append("TP-5: локальный путь не прошёл")
    if resolve_image("file:///x/y.png") != "/x/y.png":
        fails.append("TP-5: file:// не обрезан")

    return len(fails), fails


if __name__ == "__main__":
    n, fails = _run()
    if fails:
        print(f"❌ EVAL FAILED ({n}):")
        for f in fails:
            print(f"  - {f}")
        sys.exit(1)
    print("✅ EVAL PASSED — LFM-1 server message parsing OK")
