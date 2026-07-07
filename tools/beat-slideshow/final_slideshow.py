#!/usr/bin/env python3
"""
Финальный слайдшоу: фото + заставки + музыка, одним ffmpeg проходом.
Использует xfade (проверенный подход, работает без чёрного экрана).
Видео-клипы конвертируются в кадры и вставляются как фото.
"""
import sys, os, subprocess, json, math, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT, FPS = 1080, 1920, 25
PHOTO_DUR = 3.8
TITLE_DUR = 4.0
FADE = 0.5

ZOOM_VARIANTS = [
    ("min(zoom+0.0012,1.25)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    ("max(zoom-0.0012,1.0)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    ("min(zoom+0.0010,1.2)", "iw/2-(iw/zoom/2)+on*2", "ih/2-(ih/zoom/2)"),
    ("min(zoom+0.0010,1.2)", "iw/2-(iw/zoom/2)-on*2", "ih/2-(ih/zoom/2)"),
    ("1.0", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
]

TRANSITIONS = ["fade","fade","dissolve","fade","fadewhite","fade","fadeblack","fade","circleopen"]


def audio_duration(path):
    r = subprocess.run(["ffprobe","-v","quiet","-print_format","json","-show_format",path],
                       capture_output=True, text=True, check=True)
    return float(json.loads(r.stdout)["format"]["duration"])


def convert_heic(folder, tmpdir):
    converted = {}
    for f in folder.iterdir():
        if f.suffix.lower() == '.heic':
            out = tmpdir / f"{f.stem}.jpg"
            subprocess.run(["sips","-s","format","jpeg",str(f),"--out",str(out)],
                           capture_output=True, check=False)
            converted[f.stem] = out
    return converted


def extract_video_frame(video, out_path, t=1.0):
    """Извлекает один кадр из видео как фото."""
    subprocess.run(["ffmpeg","-y","-ss",str(t),"-i",str(video),"-frames:v","1",
                    "-q:v","2",str(out_path)], capture_output=True, check=True)


def create_title(text, subtitle, out_path):
    img = Image.new('RGB', (WIDTH, HEIGHT), (8, 8, 12))
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        t = y / HEIGHT
        draw.line([(0,y),(WIDTH,y)], fill=(int(8+t*12), int(8+t*8), int(12+t*20)))
    try:
        f1 = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 72)
        f2 = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
    except: f1 = f2 = ImageFont.load_default()
    b = draw.textbbox((0,0), text, font=f1)
    draw.text(((WIDTH-(b[2]-b[0]))/2, HEIGHT//2-(b[3]-b[1])), text, fill=(240,240,245), font=f1)
    if subtitle:
        b2 = draw.textbbox((0,0), subtitle, font=f2)
        draw.text(((WIDTH-(b2[2]-b2[0]))/2, HEIGHT//2+30), subtitle, fill=(180,180,200), font=f2)
    img.save(str(out_path), "JPEG", quality=95)


def extend_music(audio, target, out):
    src_dur = audio_duration(audio)
    if src_dur >= target:
        subprocess.run(["ffmpeg","-y","-i",audio,"-t",f"{target:.1f}","-c:a","aac","-b:a","192k",str(out)],
                       capture_output=True, check=True)
        return
    with open(str(out)+".list","w") as f:
        for _ in range(int(target/src_dur)+2):
            f.write(f"file '{audio}'\n")
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(out)+".list",
                    "-t",f"{target:.1f}","-c:a","aac","-b:a","192k",str(out)],
                   capture_output=True, check=True)


def main():
    if len(sys.argv) < 3:
        print("Использование: final_slideshow.py <папка_с_медиа> <музыка.mp3> [output.mp4]")
        sys.exit(1)

    media_dir = Path(sys.argv[1])
    audio_path = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) > 3 else "final.mp4"

    tmpdir = Path(tempfile.mkdtemp(prefix="final_"))
    try:
        print("Конвертация HEIC...")
        heic_map = convert_heic(media_dir, tmpdir)

        # Сбор медиа: фото + первый кадр из видео
        print("Подготовка медиа...")
        photos = []
        video_stems = {f.stem for f in media_dir.iterdir() if f.suffix.lower() in {'.mov','.mp4'}}

        for f in sorted(media_dir.iterdir()):
            ext = f.suffix.lower()
            stem = f.stem
            if ext in {'.dng'}: continue
            if ext == '.heic':
                if stem in video_stems:
                    # Live Photo — берём кадр из видео
                    frame = tmpdir / f"{stem}_frame.jpg"
                    extract_video_frame(f.with_suffix('.MOV'), frame)
                    photos.append(frame)
                elif stem in heic_map:
                    photos.append(heic_map[stem])
            elif ext in {'.jpg','.jpeg','.png'}:
                photos.append(f)
            elif ext in {'.mov','.mp4'}:
                frame = tmpdir / f"{stem}_frame.jpg"
                extract_video_frame(f, frame, t=min(1.0, audio_duration(str(f))*0.3))
                photos.append(frame)

        print(f"Фото: {len(photos)}")

        # Заставки
        intro = tmpdir / "intro.jpg"
        outro = tmpdir / "outro.jpg"
        create_title("Маша", "Ave Maria", intro)
        create_title("Ave Maria", "Giorgia Fumanti", outro)

        all_photos = [intro] + photos + [outro]
        n = len(all_photos)
        total = TITLE_DUR + len(photos) * PHOTO_DUR + TITLE_DUR
        print(f"Таймлайн: {total:.0f}с, сегментов: {n}")

        # Длительности
        durations = [TITLE_DUR] + [PHOTO_DUR] * len(photos) + [TITLE_DUR]

        # Расчёт оффсетов для xfade
        offsets = []
        t = 0
        for i in range(n):
            offsets.append(t)
            t += durations[i] - FADE
        total_video = t + durations[-1]

        # Музыка
        print("Подготовка музыки...")
        audio_ext = tmpdir / "audio.m4a"
        extend_music(audio_path, total_video + 2, audio_ext)

        # FFmpeg команда — один проход, xfade
        print("Рендер (один проход)...")
        cmd = ["ffmpeg", "-y"]
        for p in all_photos:
            cmd.extend(["-loop","1","-t",f"{durations[i]:.3f}" if False else f"{durations[all_photos.index(p)]:.3f}","-i",str(p)])
        cmd.extend(["-i", str(audio_ext)])

        # Filter complex
        parts = []
        for i in range(n):
            dur = durations[i]
            dur_frames = max(int(dur * FPS), 1)
            zoom_z, zoom_x, zoom_y = ZOOM_VARIANTS[i % len(ZOOM_VARIANTS)]
            parts.append(
                f"[{i}:v]scale=w={WIDTH}:h={HEIGHT}:force_original_aspect_ratio=increase,"
                f"crop={WIDTH}:{HEIGHT},"
                f"zoompan=z='{zoom_z}':d={dur_frames}:x='{zoom_x}':y='{zoom_y}':s={WIDTH}x{HEIGHT},"
                f"settb=AVTB,fps={FPS},setpts=PTS-STARTPTS[v{i}]"
            )

        prev = "v0"
        for i in range(1, n):
            offset = offsets[i] - offsets[0]
            trans = TRANSITIONS[(i-1) % len(TRANSITIONS)]
            current = f"m{i}"
            parts.append(f"[{prev}][v{i}]xfade=transition={trans}:duration={FADE:.2f}:offset={offset:.3f}[{current}]")
            prev = current

        cmd.extend(["-filter_complex", ";".join(parts)])
        cmd.extend(["-map", f"[{prev}]", "-map", f"{n}:a"])
        cmd.extend(["-c:v", "libx264", "-preset", "medium", "-crf", "23", "-pix_fmt", "yuv420p"])
        cmd.extend(["-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart"])
        cmd.append(output)

        print(f"ffmpeg: {n} inputs, {n-1} xfades")
        subprocess.run(cmd, check=True)
        print(f"Готово: {output}")

    finally:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    main()
