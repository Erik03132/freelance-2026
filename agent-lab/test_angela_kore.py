#!/usr/bin/env python3
"""
test_angela_kore.py — локальный тест голосовой Анжелы.

Симуляция диалога без телефона:
1. Ты печатаешь вопрос (как клиент)
2. Angela отвечает текстом (OpenRouter DeepSeek)
3. Kore озвучивает ответ через динамики (afplay)

Запуск: python3 agent-lab/test_angela_kore.py
"""
from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env", override=True)

GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")


def angela(question: str, history: str = "") -> str:
    pp = Path(__file__).parent.parent / "ai-eggs" / "config" / "prices.json"
    price_ctx = ""
    if pp.exists():
        with open(pp) as f:
            data = json.load(f)
        cats = data.get("categories", {})
        lines = ["Прайс-лист ВезёмЦыплят:"]
        for cv in cats.values():
            if not isinstance(cv, dict):
                continue
            lbl = cv.get("label", "")
            lines.append(f"\n{lbl}:")
            for name, info in cv.get("items", {}).items():
                p = info.get("price", "?")
                desc = info.get("description", "")[:60]
                lines.append(f"  {name}: {p}₽ — {desc}")
        price_ctx = "\n".join(lines)

    prompt = (
        "Ты — Анжела, голосовой ассистент птицеводческого бизнеса ВезёмЦыплят. "
        "Отвечай КРАТКО (1-3 предложения), естественно.\n"
        f"{price_ctx}\n"
        f"{history}\n"
        "Клиент: " + question
    )

    for model in ["deepseek/deepseek-chat", "qwen/qwen-turbo"]:
        try:
            r = requests.post("https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"},
                json={"model": model, "messages": [{"role": "user", "content": prompt}],
                      "max_tokens": 256, "temperature": 0.3},
                timeout=20)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"  ⚠ Angela {model}: {e}")
    return "Извините, повторите, пожалуйста."


def kore_speak(text: str) -> None:
    print(f"  🎤 Kore озвучивает ({len(text)} символов)...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={GEMINI_KEY}"
    payload = {
        "contents": [{"parts": [{"text": text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Kore"}}
            }
        }
    }
    r = requests.post(url, json=payload, timeout=30)
    if r.status_code != 200:
        print(f"  ⚠ Kore error: {r.status_code}")
        return
    audio = base64.b64decode(r.json()["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
    wav_path = Path("/tmp/kore_last.wav")
    subprocess.run(["ffmpeg", "-y", "-f", "s16le", "-ar", "24000", "-ac", "1",
        "-i", "-", "-ar", "48000", "-ac", "1", "-f", "wav", str(wav_path)],
        input=audio, capture_output=True, timeout=15)
    subprocess.run(["afplay", str(wav_path)])


def main():
    print("═" * 50)
    print("  Анжела + Kore — тестовый диалог")
    print("  (пиши вопросы, 'exit' для выхода)")
    print("═" * 50)
    print()

    # Greeting
    print("🤖 Анжела: Привет! Я Анжела, ассистент ВезёмЦыплят.")
    kore_speak("Привет! Я Анжела, ассистент ВезёмЦыплят. Чем могу помочь?")
    print()

    history = ""
    while True:
        try:
            q = input("🗣 Ты: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not q:
            continue
        if q.lower() in ("exit", "quit", "выход"):
            break

        print("  🤔 Angela думает...")
        resp = angela(q, history)
        print(f"\n🤖 Анжела: {resp}")
        kore_speak(resp)
        print()

        history += f"Клиент: {q}\nАнжела: {resp}\n"
        if len(history) > 2000:
            history = history[-1500:]


if __name__ == "__main__":
    main()
