#!/usr/bin/env python3
"""
Прямой слайдшоу: фото + видео + заставки + продление музыки.

Использование:
  python3 direct_slideshow.py <папка_с_медиа> <музыка.mp3> [output.mp4]

Что делает:
  1. Конвертирует HEIC → JPG (через sips)
  2. Пропускает DNG, убирает HEIC-дубли Live Photos
  3. Создаёт заставку в начале и конце
  4. Рендерит каждый сегмент отдельно (фото с зумом, видео как есть)
  5. Склеивает всё с мягкими переходами (dip to black)
  6. Продлевает музыку зацикливанием если нужно
"""

import sys
import os
import subprocess
import json
import math
import tempfile
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WIDTH = 1080
HEIGHT = 1920
FPS = 25
FADE = 0.4
PHOTO_DUR = 3.8
TITLE_DUR = 4.0
BATCH_SIZE = 20

PHOTO_EXT = {'.jpg', '.jpeg', '.png', '.heic'}
VIDEO_EXT = {'.mov', '.mp4'}
SKIP_EXT = {'.dng'}

ZOOM_VARIANTS = [
    ("min(zoom+0.0012,1.25)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    ("max(zoom-0.0012,1.0)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    ("min(zoom+0.0010,1.2)", "iw/2-(iw/zoom/2)+on*2", "ih/2-(ih/zoom/2)"),
    ("min(zoom+0.0010,1.2)", "iw/2-(iw/zoom/2)-on*2", "ih/2-(ih/zoom/2)"),
    ("1.0", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
]


def convert_heic(folder: Path, tmpdir: Path) -> dict:
    """Конвертирует HEIC → JPG через sips. Возвращает {stem: jpg_path}."""
    converted = {}
    heic_files = [f for f in folder.iterdir() if f.suffix.lower() == '.heic']
    for i, f in enumerate(heic_files):
        out = tmpdir / f"{f.stem}.jpg"
        subprocess.run(["sips", "-s", "format", "jpeg", str(f), "--out", str(out)],
                       capture_output=True, check=False)
        converted[f.stem] = out
        print(f"\r  HEIC→JPG: {i+1}/{len(heic_files)}", end="", flush=True)
    if heic_files:
        print()
    return converted


def find_live_photo_dupes(folder: Path) -> set:
    """Находит HEIC у которых есть парный MOV (Live Photo)."""
    video_stems = {f.stem for f in folder.iterdir() if f.suffix.lower() in VIDEO_EXT}
    dupes = set()
    for f in folder.iterdir():
        if f.suffix.lower() == '.heic' and f.stem in video_stems:
            dupes.add(f.stem)
    return dupes


def collect_media(folder: Path, heic_map: dict, dupes: set) -> list[dict]:
    """Собирает медиа в хронологическом порядке (по имени)."""
    media = []
    for f in sorted(folder.iterdir()):
        ext = f.suffix.lower()
        stem = f.stem

        if ext in SKIP_EXT:
            continue
        if ext == '.heic':
            if stem in dupes:
                continue  # используем MOV вместо HEIC
            if stem in heic_map:
                media.append({"type": "photo", "path": heic_map[stem], "stem": stem})
        elif ext in PHOTO_EXT:
            media.append({"type": "photo", "path": f, "stem": stem})
        elif ext in VIDEO_EXT:
            media.append({"type": "video", "path": f, "stem": stem})

    return media


def video_duration(path: str) -> float:
    r = subprocess.run([
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", str(path)
    ], capture_output=True, text=True, check=True)
    return float(json.loads(r.stdout)["format"]["duration"])


def create_title_card(text: str, subtitle: str, out_path: Path):
    """Создаёт красивую заставку через PIL."""
    img = Image.new('RGB', (WIDTH, HEIGHT), (8, 8, 12))
    draw = ImageDraw.Draw(img)

    # Градиентный фон
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(8 + t * 12)
        g = int(8 + t * 8)
        b = int(12 + t * 20)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Текст
    try:
        font_main = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 72)
        font_sub = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
    except Exception:
        font_main = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # Центрируем
    bbox = draw.textbbox((0, 0), text, font=font_main)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(((WIDTH - tw) / 2, HEIGHT // 2 - th), text, fill=(240, 240, 245), font=font_main)

    if subtitle:
        bbox2 = draw.textbbox((0, 0), subtitle, font=font_sub)
        tw2 = bbox2[2] - bbox2[0]
        draw.text(((WIDTH - tw2) / 2, HEIGHT // 2 + th + 20), subtitle,
                  fill=(180, 180, 200), font=font_sub)

    img.save(str(out_path), "JPEG", quality=95)


def render_photo_clip(photo: Path, duration: float, out_path: Path, variant_idx: int):
    """Рендерит фото-клип с зум-эффектом и fade in/out."""
    dur_frames = max(int(duration * FPS), 1)
    zoom_z, zoom_x, zoom_y = ZOOM_VARIANTS[variant_idx % len(ZOOM_VARIANTS)]
    fade_out_start = max(duration - FADE, 0.1)

    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-t", f"{duration:.3f}", "-i", str(photo),
        "-vf",
        f"scale=w={WIDTH}:h={HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT},"
        f"zoompan=z='{zoom_z}':d={dur_frames}:"
        f"x='{zoom_x}':y='{zoom_y}':s={WIDTH}x{HEIGHT},"
        f"settb=AVTB,fps={FPS},setpts=PTS-STARTPTS,"
        f"fade=t=in:st=0:d={FADE},fade=t=out:st={fade_out_start:.2f}:d={FADE}",
        "-c:v", "h264_videotoolbox", "-b:v", "4M",
        "-pix_fmt", "yuv420p", "-an",
        str(out_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True)


def render_video_clip(video: Path, duration: float, out_path: Path):
    """Рендерит видео-клип: обрезает по длительности, масштабирует, fade."""
    fade_out_start = max(duration - FADE, 0.1)

    cmd = [
        "ffmpeg", "-y", "-i", str(video),
        "-t", f"{duration:.3f}",
        "-vf",
        f"scale=w={WIDTH}:h={HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT},"
        f"settb=AVTB,fps={FPS},setpts=PTS-STARTPTS,"
        f"fade=t=in:st=0:d={FADE},fade=t=out:st={fade_out_start:.2f}:d={FADE}",
        "-c:v", "h264_videotoolbox", "-b:v", "4M",
        "-pix_fmt", "yuv420p", "-an",
        str(out_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True)


def extend_music(audio_path: str, target_dur: float, out_path: Path):
    """Продлевает музыку зацикливанием до target_dur."""
    src_dur = video_duration(audio_path)
    if src_dur >= target_dur:
        # Просто обрезаем
        subprocess.run([
            "ffmpeg", "-y", "-i", audio_path, "-t", f"{target_dur:.1f}",
            "-c:a", "aac", "-b:a", "192k", str(out_path)
        ], capture_output=True, check=True)
        return

    # Зацикливаем: исход + последние 30с повторяем
    loop_start = max(0, src_dur - 30)
    needed = target_dur - src_dur
    loops = int(needed / 30) + 1

    # Создаём список для concat
    list_file = out_path.parent / "audio_list.txt"
    with open(list_file, "w") as f:
        f.write(f"file '{audio_path}'\n")
        for _ in range(loops):
            f.write(f"file '{audio_path}'\n")

    # concat + trim
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-t", f"{target_dur:.1f}",
        "-c:a", "aac", "-b:a", "192k",
        str(out_path)
    ], capture_output=True, check=True)


def main():
    if len(sys.argv) < 3:
        print("Использование: direct_slideshow.py <папка_с_медиа> <музыка.mp3> [output.mp4]")
        sys.exit(1)

    media_dir = Path(sys.argv[1])
    audio_path = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) > 3 else "final.mp4"

    if not media_dir.is_dir():
        print(f"Папка не найдена: {media_dir}")
        sys.exit(1)
    if not os.path.isfile(audio_path):
        print(f"Аудио не найдено: {audio_path}")
        sys.exit(1)

    tmpdir = Path(os.path.expanduser("~/masha-project/_tmp_slideshow"))
    clips_dir = tmpdir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 1. Конвертация HEIC
        print("Конвертация HEIC...")
        heic_map = convert_heic(media_dir, tmpdir)

        # 2. Live Photo дедупликация
        dupes = find_live_photo_dupes(media_dir)
        if dupes:
            print(f"Live Photos: {len(dupes)} HEIC пропущено (используем MOV)")

        # 3. Сбор медиа
        media = collect_media(media_dir, heic_map, dupes)
        n_photos = sum(1 for m in media if m["type"] == "photo")
        n_videos = sum(1 for m in media if m["type"] == "video")
        print(f"Медиа: {n_photos} фото, {n_videos} видео, всего {len(media)}")

        # 4. Заставки
        print("Создание заставок...")
        intro_path = tmpdir / "intro.jpg"
        outro_path = tmpdir / "outro.jpg"
        create_title_card("Маша", "Ave Maria", intro_path)
        create_title_card("Ave Maria", "Giorgia Fumanti", outro_path)

        # 5. Расчёт таймлайна
        video_durs = {}
        for m in media:
            if m["type"] == "video":
                video_durs[m["stem"]] = video_duration(str(m["path"]))

        total = TITLE_DUR  # intro
        segments = [{"type": "title", "path": intro_path, "duration": TITLE_DUR}]
        for m in media:
            if m["type"] == "video":
                dur = min(video_durs.get(m["stem"], 3.0), 5.0)  # максимум 5с на видео
            else:
                dur = PHOTO_DUR
            segments.append({"type": m["type"], "path": m["path"], "duration": dur, "stem": m.get("stem", "")})
            total += dur
        segments.append({"type": "title", "path": outro_path, "duration": TITLE_DUR})
        total += TITLE_DUR

        music_dur = video_duration(audio_path)
        print(f"Таймлайн: {total:.0f}с (музыка: {music_dur:.0f}с)")
        if total > music_dur:
            print(f"  Музыка продлевается на {total - music_dur:.0f}с")

        # 6. Рендеринг каждого сегмента
        print(f"Рендер {len(segments)} сегментов...")
        clip_paths = []
        for i, seg in enumerate(segments):
            clip_path = clips_dir / f"clip_{i:04d}.mp4"
            if clip_path.exists() and clip_path.stat().st_size > 1000:
                clip_paths.append(clip_path)
                continue
            if seg["type"] == "video":
                render_video_clip(seg["path"], seg["duration"], clip_path)
            else:
                render_photo_clip(seg["path"], seg["duration"], clip_path, i)
            clip_paths.append(clip_path)
            print(f"\r  Сегмент {i+1}/{len(segments)}", end="", flush=True)
        print()

        # 7. Склейка
        print("Склейка клипов...")
        concat_list = tmpdir / "concat.txt"
        with open(concat_list, "w") as f:
            for cp in clip_paths:
                f.write(f"file '{cp}'\n")

        video_only = tmpdir / "video_only.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
            "-c", "copy", str(video_only)
        ], capture_output=True, check=True)

        # 8. Продление музыки
        print("Подготовка музыки...")
        audio_ext = tmpdir / "audio_ext.m4a"
        extend_music(audio_path, total, audio_ext)

        # 9. Финальный mux
        print("Финальный рендер...")
        subprocess.run([
            "ffmpeg", "-y",
            "-i", str(video_only),
            "-i", str(audio_ext),
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            output
        ], capture_output=True, check=True)

        print(f"Готово: {output}")
        print(f"  Длительность: {total:.0f}с")
        print(f"  Разрешение: {WIDTH}x{HEIGHT}")

    finally:
        pass  # не удаляем — папка постоянная для возобновления


if __name__ == "__main__":
    main()
