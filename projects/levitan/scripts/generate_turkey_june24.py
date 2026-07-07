#!/usr/bin/env python3
"""
Генерация WAV для обзвона индюшат — 24 июня.
Диалоговый формат (без ДА/НЕТ, открытый вопрос).
Голос: Gemini TTS Kore. Формат: 8kHz mono pcm_s16le.
Структура: 7с тишина + голос + 0.5с бип + 10с тишина
"""
import base64
import os
import subprocess
import wave
from pathlib import Path

import requests
from dotenv import load_dotenv

# Загружаем .env из ai-eggs
ENV_PATH = Path("/Users/igorvasin/freelance-2026/projects/ai-eggs/.env")
load_dotenv(ENV_PATH, override=True)

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
PROXY   = os.getenv("HTTPS_PROXY") or os.getenv("TELEGRAM_PROXY")

TEXT = (
    "Здравствуйте! Это Азовский инкубатор. "
    "Ранее вы заказывали у нас индюшат. "
    "Следующая партия поступает двадцать четвёртого июня. "
    "Подскажите, актуален ли для вас заказ? "
    "Если есть вопросы — задайте, мы ответим."
)

OUT_DIR = Path("/Users/igorvasin/freelance-2026/projects/levitan/data/turkey_audio")
OUT_DIR.mkdir(parents=True, exist_ok=True)
RAW_WAV  = OUT_DIR / "turkey_june24_dialog.wav"
FINAL_WAV = OUT_DIR / "turkey_june24_final.wav"

print(f"Текст ({len(TEXT)} символов):")
print(f"  {TEXT}")
print(f"Прокси: {PROXY or 'нет'}")

# === Шаг 1: Gemini TTS (Kore) ===
print("\n=== Шаг 1: Gemini TTS (Kore) ===")
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={API_KEY}"
payload = {
    "contents": [{"parts": [{"text": TEXT}]}],
    "generationConfig": {
        "responseModalities": ["AUDIO"],
        "speechConfig": {
            "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Kore"}}
        }
    }
}
proxies = {"https": PROXY, "http": PROXY} if PROXY else None
r = requests.post(url, json=payload, proxies=proxies, timeout=60)
if r.status_code != 200:
    print(f"ОШИБКА: HTTP {r.status_code}")
    print(r.text[:500])
    exit(1)

data = r.json()
audio_b64 = data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
audio_bytes = base64.b64decode(audio_b64)
print(f"  Получено: {len(audio_bytes)} байт аудио (PCM 24kHz)")

# Сохраняем RAW WAV 24kHz
with wave.open(str(RAW_WAV), "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(24000)
    w.writeframes(audio_bytes)
dur = len(audio_bytes) / 2 / 24000
print(f"  Сохранено: {RAW_WAV} ({dur:.1f}с, 24kHz)")

# === Шаг 2: Сборка финального WAV (8kHz) ===
print("\n=== Шаг 2: Сборка финального WAV ===")
WORK = Path("/tmp/_turkey_build")
WORK.mkdir(exist_ok=True)

voice_8k   = WORK / "voice_8k.wav"
silence_7s = WORK / "silence_7s.wav"
bip        = WORK / "bip.wav"
silence_10 = WORK / "silence_10s.wav"

# Конвертируем голос 24kHz → 8kHz mono
subprocess.run([
    "ffmpeg", "-y", "-i", str(RAW_WAV),
    "-ar", "8000", "-ac", "1", "-acodec", "pcm_s16le", str(voice_8k)
], check=True, capture_output=True)

# Длительность голоса
with wave.open(str(voice_8k), "rb") as w:
    dur8 = w.getnframes() / w.getframerate()
print(f"  Голос 8kHz: {dur8:.1f}с")

# 7с тишина (lead — чтобы клиент успел сказать «алло»)
subprocess.run([
    "ffmpeg", "-y", "-f", "lavfi",
    "-i", "anullsrc=r=8000:cl=mono",
    "-t", "7", "-acodec", "pcm_s16le", str(silence_7s)
], check=True, capture_output=True)

# Бип 800Hz 0.5с
subprocess.run([
    "ffmpeg", "-y", "-f", "lavfi",
    "-i", "sine=frequency=800:sample_rate=8000",
    "-t", "0.5", "-acodec", "pcm_s16le", str(bip)
], check=True, capture_output=True)

# 10с тишина (хвост — клиент говорит ответ)
subprocess.run([
    "ffmpeg", "-y", "-f", "lavfi",
    "-i", "anullsrc=r=8000:cl=mono",
    "-t", "10", "-acodec", "pcm_s16le", str(silence_10)
], check=True, capture_output=True)

# Склейка: 7с тишина + голос + бип + 10с тишина
subprocess.run([
    "ffmpeg", "-y",
    "-i", str(silence_7s),
    "-i", str(voice_8k),
    "-i", str(bip),
    "-i", str(silence_10),
    "-filter_complex", "[0:a][1:a][2:a][3:a]concat=n=4:v=0:a=1[out]",
    "-map", "[out]",
    "-acodec", "pcm_s16le",
    str(FINAL_WAV)
], check=True, capture_output=True)

# Проверка
with wave.open(str(FINAL_WAV)) as w:
    total_sec = w.getnframes() / w.getframerate()
    print(f"\n✅ Готово: {FINAL_WAV}")
    print(f"   Формат: {w.getframerate()}Hz, {w.getnchannels()}ch, {total_sec:.1f}с")
    print(f"   Размер: {FINAL_WAV.stat().st_size // 1024} KB")

print(f"\nДля Mango: загрузи {FINAL_WAV.name} в ЛК Mango → Аудиозаписи")
print(f"Или скопируй на VPS: scp {FINAL_WAV} root@72.56.38.19:/tmp/mango_play_turkey_june24.wav")
