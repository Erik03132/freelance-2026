#!/usr/bin/env python3
"""LFM-1/LFM-2 — локальный OpenAI-совместимый сервер для LFM2.5-VL-3B (Mac, MLX).

Позволяет OpenCode видеть LFM2.5-VL-3B в меню выбора ЛЛМ как локальную vision-модель.
Использует уже установленный mlx-vlm (ленивый импорт — модуль грузится без mlx_vlm в CI).

Запуск (в venv, где pip install mlx-vlm):
    python tools/lfm_vl_server.py
Модель грузится в память (~3ГБ) при первом запросе. Слушает http://127.0.0.1:8000/v1.

OpenCode: провайдер lfm-vl в opencode.jsonc (baseURL http://127.0.0.1:8000/v1).
Приватно (ADR-002): всё локально, картинки не уходят в облако.
Лицензия LFM1.0 (free <$10M revenue).

Примечание: модель non-reasoning 3B — для vision-задач; основной "мозг" агента
оставьте на сильной модели (OmniRoute/Qwen), выбирайте LFM2.5-VL-3B точечно.
"""

from __future__ import annotations

import base64
import json
import os
import re
import tempfile
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

MODEL_ID = os.environ.get("LFM_VL_MODEL", "LiquidAI/LFM2.5-VL-3B-MLX-8bit")
_CACHE: dict = {}
_CACHE_LOCK = threading.Lock()


def extract_text_and_image(messages) -> tuple[str, str | None]:
    """Из OpenAI-сообщений достать текст-промпт и URL первого изображения."""
    text_parts: list[str] = []
    image_url: str | None = None
    for msg in messages:
        if msg.get("role") != "user":
            # промпты ассистента/системы тоже собираем как контекст
            content = msg.get("content", "")
            if isinstance(content, str):
                text_parts.append(content)
            continue
        content = msg.get("content", "")
        if isinstance(content, str):
            text_parts.append(content)
            continue
        for part in content:
            if part.get("type") == "text":
                text_parts.append(part.get("text", ""))
            elif part.get("type") == "image_url":
                if image_url is None:
                    image_url = part["image_url"]["url"]
    return "\n".join(text_parts).strip(), image_url


def resolve_image(url: str | None) -> str | None:
    """URL/хранилище -> локальный путь к картинке."""
    if not url:
        return None
    if url.startswith("data:"):
        m = re.match(r"data:image/[^;]+;base64,(.*)", url)
        if not m:
            return None
        raw = base64.b64decode(m.group(1))
        p = tempfile.mktemp(suffix=".png")
        with open(p, "wb") as f:
            f.write(raw)
        return p
    if url.startswith("http://") or url.startswith("https://"):
        p = tempfile.mktemp(suffix=".jpg")
        urllib.request.urlretrieve(url, p)
        return p
    if url.startswith("file://"):
        return url[len("file://"):]
    return url  # локальный путь


def _load_model():
    if "model" not in _CACHE:
        with _CACHE_LOCK:
            if "model" not in _CACHE:
                from mlx_vlm import load, generate
                from mlx_vlm.utils import load_config

                model, processor = load(MODEL_ID)
                config = load_config(model)
                _CACHE["model"] = model
                _CACHE["processor"] = processor
                _CACHE["config"] = config
                _CACHE["generate"] = generate
    return _CACHE


def generate_response(prompt: str, image_path: str | None) -> str:
    """Лениво грузит mlx_vlm и генерирует ответ по промпту + картинке."""
    c = _load_model()
    image = [image_path] if image_path else None
    return c["generate"](c["model"], c["processor"], image, prompt, c["config"])


def _last_user_content(messages):
    for msg in reversed(messages):
        if msg.get("role") == "user":
            return msg.get("content", "")
    return ""


class _Handler(BaseHTTPRequestHandler):
    def _send(self, payload: bytes, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path.rstrip("/") == "/v1/models":
            body = json.dumps(
                {"object": "list", "data": [{"id": "LFM2.5-VL-3B", "object": "model"}]}
            ).encode()
            self._send(body)
        else:
            self._send(b'{"error":"not found"}', 404)

    def do_POST(self):
        if self.path.rstrip("/") not in ("/v1/chat/completions",):
            self._send(b'{"error":"not found"}', 404)
            return
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        prompt, img_url = extract_text_and_image(body.get("messages", []))
        image_path = resolve_image(img_url)
        try:
            text = generate_response(prompt, image_path)
        except Exception as e:  # noqa: BLE001
            self._send(json.dumps({"error": str(e)}).encode(), 500)
            return
        resp = {
            "id": "chatcmpl-local",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": body.get("model", "LFM2.5-VL-3B"),
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": text},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }
        self._send(json.dumps(resp).encode())

    def log_message(self, *args):  # тихий лог
        pass


def main():
    port = int(os.environ.get("LFM_VL_PORT", "8000"))
    print(f"LFM2.5-VL-3B server on http://127.0.0.1:{port}/v1 (model={MODEL_ID})")
    HTTPServer(("127.0.0.1", port), _Handler).serve_forever()


if __name__ == "__main__":
    main()
