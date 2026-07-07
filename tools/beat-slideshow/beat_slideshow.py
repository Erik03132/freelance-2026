#!/usr/bin/env python3
"""
Генератор слайдшоу: фото меняются в такт музыке.

Использование:
  ./beat_slideshow.py <папка_с_фото> <музыка.mp3> [output.mp4]

Пример:
  ./beat_slideshow.py ~/Photos/party ~/Music/track.mp3 result.mp4

Требования: ffmpeg, venv/ с установленными librosa, numpy
"""

import sys
import os
import subprocess
import json
from pathlib import Path

SUPPORTED_IMAGES = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}


def collect_photos(folder: str) -> list[Path]:
    photos = sorted(
        p for p in Path(folder).iterdir()
        if p.suffix.lower() in SUPPORTED_IMAGES
    )
    if not photos:
        print(f"Нет фото в {folder}")
        sys.exit(1)
    print(f"Найдено фото: {len(photos)}")
    return photos


def detect_beats(audio_path: str) -> list[float]:
    import librosa
    print("Анализ битов...")
    y, sr = librosa.load(audio_path)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr).tolist()
    print(f"  Темп: {tempo:.1f} BPM,  битов: {len(beat_times)}")
    return beat_times


def audio_duration(audio_path: str) -> float:
    result = subprocess.run([
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", audio_path
    ], capture_output=True, text=True, check=True)
    info = json.loads(result.stdout)
    return float(info["format"]["duration"])


def build_slideshow(
    photos: list[Path],
    beat_times: list[float],
    audio_path: str,
    output: str,
    width: int = 1920,
    height: int = 1080,
    fade: float = 0.3,
    fps: int = 25,
):
    total_duration = audio_duration(audio_path)
    print(f"Длительность трека: {total_duration:.1f}с")

    # Строим сегменты: на каждый бит — смена фото
    # Каждый сегмент длится от своего beat_time до следующего
    photo_cycle = photos * ((len(beat_times) // len(photos)) + 1)
    segments = []
    for i, beat in enumerate(beat_times):
        next_beat = beat_times[i + 1] if i + 1 < len(beat_times) else total_duration
        segments.append({
            "photo": photo_cycle[i],
            "start": max(0, beat - fade),        # начинаем чуть раньше для кроссфейда
            "duration": next_beat - beat + fade,  # длим до следующего бита + запас на fade
        })

    # ffmpeg inputs: каждый фото как отдельный input
    inputs = []
    for i, seg in enumerate(segments):
        duration = max(seg["duration"], 0.1)
        inputs.extend(["-loop", "1", "-t", f"{duration:.3f}", "-i", str(seg["photo"])])

    # filter_complex
    filter_parts = []
    n_segs = len(segments)

    # Ken Burns zoompan для каждого сегмента
    for i in range(n_segs):
        dur = max(segments[i]["duration"], 0.1)
        dur_frames = max(int(dur * fps), 1)
        filter_parts.append(
            f"[{i}:v]"
            f"scale={width}:{height}:force_original_aspect_ratio=crop,"
            f"zoompan=z='min(zoom+0.0012,1.3)':d={dur_frames}:"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height},"
            f"settb=AVTB,fps={fps},setpts=PTS-STARTPTS"
            f"[v{i}]"
        )

    # Кроссфейды: цепочкой v0 + v1 → v01, v01 + v2 → v02, ...
    prev = "v0"
    for i in range(1, n_segs):
        offset = segments[i]["start"] - segments[0]["start"]
        fade_dur = min(fade, segments[i - 1]["duration"] * 0.5)
        current = f"v{i}_mix"
        filter_parts.append(
            f"[{prev}][v{i}]xfade=transition=fade:"
            f"duration={fade_dur:.2f}:offset={offset:.3f}"
            f"[{current}]"
        )
        prev = current

    # Сборка фильтра
    filter_complex = "; ".join(filter_parts)

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-i", audio_path,
        "-filter_complex", filter_complex,
        "-map", f"[{prev}]",
        "-map", f"{n_segs}:a",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        output,
    ]

    print("Рендер видео...")
    subprocess.run(cmd, check=True)
    print(f"Готово: {output}")


def main():
    if len(sys.argv) < 3:
        print("Использование: beat_slideshow.py <папка_с_фото> <музыка.mp3> [output.mp4]")
        sys.exit(1)

    photo_dir = sys.argv[1]
    audio_path = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) > 3 else "slideshow.mp4"

    if not os.path.isdir(photo_dir):
        print(f"Папка не найдена: {photo_dir}")
        sys.exit(1)
    if not os.path.isfile(audio_path):
        print(f"Аудио не найдено: {audio_path}")
        sys.exit(1)

    photos = collect_photos(photo_dir)
    beat_times = detect_beats(audio_path)
    build_slideshow(photos, beat_times, audio_path, output)


if __name__ == "__main__":
    main()
