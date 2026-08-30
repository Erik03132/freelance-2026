#!/usr/bin/env python3
"""
AVM — прототип голосовой трубы STT -> OpenRouter LLM -> TTS.
КОНЦЕПТ: любой вопрос (предвиденный или нет) идёт в ОДНУ быструю LLM-трубу.
НЕТ кэша-шлюза, НЕТ воронки fast-path перед LLM. Модель — первична.
Кэш/заглушки — опциональный ускоритель, не блокирующий непредвиденное.

Использование:
  python3 openrouter_voice_pipe.py --question "Сколько стоит доставка в Москву?"
  python3 openrouter_voice_pipe.py --audio client_question.mp3   # STT -> LLM -> TTS
  python3 openrouter_voice_pipe.py --model anthropic/claude-haiku-4.5 --question "Что умеете?"

Зависимости: openai, edge-tts, (опц.) faster-whisper для --audio.
"""

import argparse
import asyncio
import os
import time

# --- OpenRouter (OpenAI-compatible) ---
from openai import AsyncOpenAI


# --- TTS (offline, no key) --- ленивый import, только при озвучке
def _tts_module():
    import edge_tts  # noqa: F401 (ленивый import, не нужен для --no-tts)

    return edge_tts


# --- STT (local Whisper) — опц., только для --audio ---
try:
    from faster_whisper import WhisperModel

    _HAVE_WHISPER = True
except Exception:
    _HAVE_WHISPER = False

SYSTEM_PROMPT = (
    "Ты — голосовой менеджер компании. Отвечай КРАТКО (1-2 предложения), "
    "по существу, на любой вопрос клиента. Не выдумывай фактов. "
    "Если не знаешь точного ответа — честно скажи и предложи уточнить."
)

OR_BASE = "https://openrouter.ai/api/v1"


def get_client() -> AsyncOpenAI:
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY не задан (проверь .env)")
    return AsyncOpenAI(api_key=key, base_url=OR_BASE)


async def llm_reply(client: AsyncOpenAI, model: str, user_text: str) -> str:
    """ЕДИНАЯ труба: любой вопрос -> LLM. Без кэша/воронки перед вызовом."""
    t0 = time.time()
    out = []
    stream = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        temperature=0.3,
        max_tokens=400,
        stream=True,
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content or ""
        if delta:
            out.append(delta)
    text = "".join(out)
    ttft_proxy = (
        time.time() - t0
    )  # от вызова до первого токена нельзя точно замерить при stream без raw
    print(f"[LLM] model={model} chars={len(text)} elapsed={ttft_proxy:.2f}s")
    return text


async def tts_speak(text: str, voice: str = "ru-RU-SvetlanaNeural") -> str:
    """Edge TTS -> mp3 файл (без ключа). Возвращает путь."""
    edge_tts = _tts_module()
    path = f"/tmp/avm_reply_{int(time.time())}.mp3"
    comm = edge_tts.Communicate(text, voice)
    await comm.save(path)
    print(f"[TTS] saved {path} ({len(text)} chars)")
    return path


def stt_audio(path: str) -> str:
    if not _HAVE_WHISPER:
        raise RuntimeError("faster_whisper не установлен — нужен --question вместо --audio")
    model = WhisperModel("tiny", device="cpu")
    segs, _ = model.transcribe(path, language="ru")
    return " ".join(s.text for s in segs)


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--question", help="текст вопроса (без STT)")
    ap.add_argument("--audio", help="файл вопроса (mp3/wav) для STT")
    ap.add_argument("--model", default="google/gemini-3.7-flash")
    ap.add_argument("--no-tts", action="store_true", help="только текст, без озвучки")
    args = ap.parse_args()

    if not args.question and not args.audio:
        ap.error("нужен --question или --audio")
    if args.audio and not args.question:
        print("[STT] распознаю аудио...")
        args.question = stt_audio(args.audio)

    print(f"[USER] {args.question}")
    client = get_client()
    reply = await llm_reply(client, args.model, args.question)
    print(f"[AGENT] {reply}")
    if not args.no_tts:
        await tts_speak(reply)


if __name__ == "__main__":
    asyncio.run(main())
