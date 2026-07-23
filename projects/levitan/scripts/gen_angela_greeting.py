#!/usr/bin/env python3
"""
Генерация приветствия Анжеллы (Азовский инкубатор, бройлеры, август 2026)

Использует edge-tts → ffmpeg → WAV 8kHz mono с 4с лид-сайленса.
Результат: /tmp/levitan_play.wav
"""

import subprocess, struct, wave, sys, os

GREETING_TEXT = (
    "Здравствуйте! Вас приветствует Азовский инкубатор. "
    "Рады предложить вам суточных бройлеров "
    "Кобб-500 и Росс-308. "
    "Цена от 75 рублей за голову в зависимости от объёма. "
    "Ближайшие поставки: первого августа, "
    "с пятнадцатого по восемнадцатое августа "
    "и с двадцать пятого по двадцать восьмое августа. "
    "Вам это интересно?"
)

LEAD_SILENCE_SEC = 10
SAMPLE_RATE = 8000
OUTPUT = "/tmp/levitan_play.wav"
TMP_MP3 = "/tmp/_angela_greeting.mp3"
TMP_WAV = "/tmp/_angela_greeting_raw.wav"
VOICE = "ru-RU-SvetlanaNeural"


def main():
    print(f"=== Анжелла: генерация приветствия ===")
    print(f"Текст: {GREETING_TEXT[:80]}...")
    print(f"Голос: {VOICE}")

    # 1. edge-tts → MP3
    r = subprocess.run(
        ["edge-tts", "--voice", VOICE, "--text", GREETING_TEXT,
         "--write-media", TMP_MP3],
        capture_output=True, text=True
    )
    if r.returncode:
        print(f"edge-tts error: {r.stderr}")
        sys.exit(1)
    print(f"TTS MP3: {os.path.getsize(TMP_MP3)} bytes")

    # 2. ffmpeg → WAV 8kHz mono s16le
    r = subprocess.run(
        ["ffmpeg", "-y", "-i", TMP_MP3,
         "-acodec", "pcm_s16le", "-ar", str(SAMPLE_RATE), "-ac", "1",
         TMP_WAV],
        capture_output=True, text=True
    )
    if r.returncode:
        print(f"ffmpeg error: {r.stderr}")
        sys.exit(1)

    # 3. Читаем WAV, добавляем лид-сайленс
    with wave.open(TMP_WAV, "rb") as w:
        frames = w.readframes(w.getnframes())
        params = w.getparams()

    silence = struct.pack("<" + "h" * (SAMPLE_RATE * LEAD_SILENCE_SEC),
                          *([0] * (SAMPLE_RATE * LEAD_SILENCE_SEC)))

    with wave.open(OUTPUT, "wb") as w:
        w.setparams(params)
        w.writeframes(silence + frames)

    print(f"Готово: {OUTPUT}")
    print(f"Размер: {os.path.getsize(OUTPUT)} bytes")
    print(f"Длительность: {LEAD_SILENCE_SEC}s тишины + голос")

    # 4. Проверка
    r = subprocess.run(
        ["ffprobe", OUTPUT], capture_output=True, text=True
    )
    for line in r.stderr.split("\n"):
        if "Duration" in line or "Audio" in line:
            print(f"  {line.strip()}")

    # 5. Cleanup
    for f in [TMP_MP3, TMP_WAV]:
        if os.path.exists(f):
            os.remove(f)


if __name__ == "__main__":
    main()
