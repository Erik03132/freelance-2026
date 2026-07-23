#!/usr/bin/env python3
"""
Transcribe MCP — транскрибация аудио + саммари через LLM.

MCP-сервер поверх faster-whisper. Разговор по JSON-RPC 2.0 через stdio.
Поддерживает: mp3, wav, m4a, ogg, flac, webm, opus.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import uuid
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

PROTOCOL_VERSION = "2024-11-05"
SESSION_ID = os.environ.get("TRANSCRIBE_SESSION") or ("tx-" + uuid.uuid4().hex[:8])
OMNI_URL = os.environ.get(
    "OMNI_URL", "http://217.149.23.113:20128/v1/chat/completions"
)
MODEL_CACHE = {}  # model_size → WhisperModel


def _log(msg: str) -> None:
    sys.stderr.write(f"[transcribe:{SESSION_ID}] {msg}\n")
    sys.stderr.flush()


def _get_model(model_size: str = "base"):
    """Ленивая загрузка модели Whisper."""
    if model_size not in MODEL_CACHE:
        _log(f"loading model '{model_size}' (first call, may take a moment)...")
        from faster_whisper import WhisperModel

        MODEL_CACHE[model_size] = WhisperModel(
            model_size, device="cpu", compute_type="int8", cpu_threads=4,
        )
        _log(f"model '{model_size}' loaded")
    return MODEL_CACHE[model_size]


def _check_ffmpeg() -> str | None:
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        return None
    except FileNotFoundError:
        return "ffmpeg не найден. Установи: brew install ffmpeg"


def _convert_to_wav(input_path: str) -> str | None:
    """Конвертирует любой аудиоформат в 16kHz mono WAV."""
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()
    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-loglevel", "error",
                "-i", input_path,
                "-ar", "16000", "-ac", "1", "-sample_fmt", "s16",
                tmp.name,
            ],
            check=True, capture_output=True, timeout=300,
        )
        return tmp.name
    except subprocess.CalledProcessError as e:
        os.unlink(tmp.name)
        err = e.stderr.decode()[:200]
        return f"FFMPEG_ERROR:{err}"
    except Exception as e:
        os.unlink(tmp.name)
        return f"FFMPEG_ERROR:{e}"


def _call_llm(prompt: str, model: str = "openrouter/deepseek/deepseek-chat") -> str:
    """Вызов LLM через OmniRoute для суммаризации."""
    import urllib.request

    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2048,
        "stream": False,
    }).encode()
    req = urllib.request.Request(
        OMNI_URL, data=body, method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        resp = urllib.request.urlopen(req, timeout=120)
        data = json.loads(resp.read())
        return (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "Ошибка: пустой ответ LLM")
        )
    except Exception as e:
        return f"Ошибка вызова LLM: {e}"


# ── Инструменты MCP ─────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "transcribe_audio",
        "description": (
            "Транскрибация аудиофайла в текст через Whisper. "
            "Поддерживает mp3, wav, m4a, ogg, flac, webm, opus."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "путь к аудиофайлу",
                },
                "model_size": {
                    "type": "string",
                    "enum": ["tiny", "base", "small", "medium", "large"],
                    "default": "base",
                    "description": (
                        "размер модели (tiny=быстро, base=баланс, "
                        "large=точно, но медленно)"
                    ),
                },
                "language": {
                    "type": "string",
                    "description": (
                        "язык (ru/en/de/fr/es и т.д., "
                        "по умолчанию автоопределение)"
                    ),
                },
                "response_format": {
                    "type": "string",
                    "enum": ["text", "srt", "vtt", "json"],
                    "default": "text",
                    "description": "формат вывода",
                },
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "summarize_transcript",
        "description": (
            "Саммари транскрибации — сжатие текста и выделение "
            "ключевых мыслей через DeepSeek/Claude."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "transcript": {
                    "type": "string",
                    "description": "текст транскрибации",
                },
                "style": {
                    "type": "string",
                    "enum": ["brief", "detailed", "bullets", "action_items"],
                    "default": "brief",
                    "description": (
                        "brief=3-5 предложений, detailed=подробно, "
                        "bullets=списком, action_items=только задачи"
                    ),
                },
            },
            "required": ["transcript"],
        },
    },
    {
        "name": "transcribe_and_summarize",
        "description": (
            "Транскрибация + саммари в один шаг. "
            "Результат: JSON с transcript, summary, duration."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "путь к аудиофайлу",
                },
                "model_size": {
                    "type": "string",
                    "enum": ["tiny", "base", "small", "medium", "large"],
                    "default": "base",
                },
                "language": {"type": "string"},
                "summary_style": {
                    "type": "string",
                    "enum": ["brief", "detailed", "bullets", "action_items"],
                    "default": "bullets",
                },
            },
            "required": ["file_path"],
        },
    },
]


def handle_transcribe(args: dict) -> dict:
    file_path = args["file_path"]
    model_size = args.get("model_size", "base")
    language = args.get("language")
    response_format = args.get("response_format", "text")

    # Проверки
    if not os.path.isfile(file_path):
        return {"error": f"Файл не найден: {file_path}"}

    err = _check_ffmpeg()
    if err:
        return {"error": err}

    file_size = os.path.getsize(file_path)
    if file_size > 500 * 1024 * 1024:
        return {"error": f"Файл слишком большой ({file_size/1024/1024:.0f}MB). Максимум 500MB."}

    ext = Path(file_path).suffix.lower()
    supported = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm", ".opus", ".aac", ".aiff", ".wma"}
    if ext not in supported:
        return {"error": f"Формат {ext} не поддерживается. Используй: {', '.join(sorted(supported))}"}

    # Конвертация в WAV
    _log(f"converting {file_path} → wav ...")
    wav_path = _convert_to_wav(file_path)
    if wav_path and wav_path.startswith("FFMPEG_ERROR:"):
        return {"error": wav_path}
    if wav_path is None:
        return {"error": "Ошибка конвертации (ffmpeg)"}

    try:
        # Транскрибация
        model = _get_model(model_size)
        kwargs = {}
        if language:
            kwargs["language"] = language

        _log(f"transcribing {file_path} (model={model_size})...")
        segments, info = model.transcribe(wav_path, beam_size=5, **kwargs)
        detected_lang = info.language if hasattr(info, "language") else None

        if response_format == "json":
            result = {
                "language": detected_lang,
                "duration_sec": round(info.duration, 1) if hasattr(info, "duration") else None,
                "segments": [],
            }
            text_parts = []
            for seg in segments:
                result["segments"].append({
                    "start": round(seg.start, 2),
                    "end": round(seg.end, 2),
                    "text": seg.text.strip(),
                })
                text_parts.append(seg.text.strip())
            result["text"] = " ".join(text_parts)
        elif response_format == "srt":
            lines = []
            for i, seg in enumerate(segments, 1):
                start = _fmt_srt_time(seg.start)
                end = _fmt_srt_time(seg.end)
                lines.append(f"{i}\n{start} --> {end}\n{seg.text.strip()}\n")
            result = "\n".join(lines)
        elif response_format == "vtt":
            lines = ["WEBVTT\n"]
            for seg in segments:
                start = _fmt_vtt_time(seg.start)
                end = _fmt_vtt_time(seg.end)
                lines.append(f"{start} --> {end}\n{seg.text.strip()}\n")
            result = "\n".join(lines)
        else:
            text_parts = [seg.text.strip() for seg in segments]
            result = " ".join(text_parts)

        _log(f"done: {file_path} ({detected_lang}, {info.duration:.0f}s)")
        return {"result": result, "language": detected_lang}

    except Exception as e:
        return {"error": f"Ошибка транскрибации: {e}"}
    finally:
        if wav_path and os.path.exists(wav_path):
            os.unlink(wav_path)


def _fmt_srt_time(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int((sec - int(sec)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _fmt_vtt_time(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:05.2f}"


def handle_summarize(args: dict) -> dict:
    transcript = args["transcript"]
    style = args.get("style", "brief")

    prompts = {
        "brief": (
            "Сделай краткую выжимку (3-5 предложений) из текста ниже. "
            "Только суть, без воды.\n\n{text}"
        ),
        "detailed": (
            "Сделай подробный пересказ текста ниже. "
            "Сохрани все ключевые мысли, аргументы, выводы.\n\n{text}"
        ),
        "bullets": (
            "Выдели ключевые мысли из текста ниже в виде маркированного списка. "
            "Каждый пункт — одна законченная мысль.\n\n{text}"
        ),
        "action_items": (
            "Извлеки из текста ниже только конкретные действия, задачи, "
            "решения и договорённости. Если действий нет — напиши \"Нет действий\".\n\n{text}"
        ),
    }

    if not transcript.strip():
        return {"error": "Пустой текст"}

    chunks = _chunk_text(transcript, 12000)
    if len(chunks) > 1:
        _log(f"splitting into {len(chunks)} chunks for summarization")

    results = []
    for chunk in chunks:
        prompt = prompts.get(style, prompts["brief"]).format(text=chunk)
        result = _call_llm(prompt)
        results.append(result)

    combined = "\n\n---\n\n".join(results) if len(results) > 1 else results[0]

    if len(chunks) > 1:
        # Сводим саммари чанков в один
        final = _call_llm(
            "Сведи следующие части саммари в один связный текст:\n\n" + combined
        )
        return {"result": final, "chunks": len(chunks)}
    return {"result": combined}


def _chunk_text(text: str, max_chars: int = 12000) -> list[str]:
    """Разбивает текст на куски по границе предложений."""
    if len(text) <= max_chars:
        return [text]
    chunks = []
    while text:
        if len(text) <= max_chars:
            chunks.append(text)
            break
        split = text.rfind(".", 0, max_chars)
        if split == -1:
            split = text.rfind(" ", 0, max_chars)
        if split == -1:
            split = max_chars
        chunks.append(text[: split + 1])
        text = text[split + 1 :]
    return chunks


def handle_transcribe_summarize(args: dict) -> dict:
    t_result = handle_transcribe(args)
    if "error" in t_result:
        return t_result

    transcript = t_result["result"] if isinstance(t_result["result"], str) else t_result["result"].get("text", str(t_result["result"]))
    if not transcript:
        return {"error": "Транскрибация не дала текста"}

    summary_args = {
        "transcript": transcript,
        "style": args.get("summary_style", "bullets"),
    }
    s_result = handle_summarize(summary_args)

    return {
        "transcript": transcript,
        "summary": s_result.get("result", "Ошибка саммари"),
        "language": t_result.get("language"),
        "duration_sec": t_result.get("result", {}).get("duration_sec") if isinstance(t_result.get("result"), dict) else None,
    }


# ── MCP JSON-RPC 2.0 over stdio ─────────────────────────────────────────────

HANDLERS = {
    "transcribe_audio": handle_transcribe,
    "summarize_transcript": handle_summarize,
    "transcribe_and_summarize": handle_transcribe_summarize,
}


def handle_request(msg: dict) -> dict | None:
    method = msg.get("method", "")

    if method == "initialize":
        return {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "transcribe-mcp", "version": "1.0.0"},
        }

    elif method == "tools/list":
        return {"tools": TOOLS}

    elif method == "tools/call":
        name = msg.get("params", {}).get("name", "")
        arguments = msg.get("params", {}).get("arguments", {})
        handler = HANDLERS.get(name)
        if not handler:
            return {"isError": True, "content": [{"type": "text", "text": f"Unknown tool: {name}"}]}
        try:
            result = handler(arguments)
            if "error" in result:
                return {"isError": True, "content": [{"type": "text", "text": result["error"]}]}
            text = json.dumps(result, ensure_ascii=False, indent=2)
            return {"content": [{"type": "text", "text": text}]}
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": f"Error: {e}"}]}

    elif method == "notifications/initialized":
        return None

    return None


def main():
    _log(f"server ready (PID {os.getpid()})")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue

        req_id = msg.get("id")
        result = handle_request(msg)

        if result is not None and req_id is not None:
            response = {"jsonrpc": "2.0", "id": req_id, **result}
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
