#!/usr/bin/env python3
"""
Умное слайдшоу: находит фото конкретного человека, выбирает лучшие,
сортирует по времени съёмки и монтирует под музыку с синхронизацией по битам.

Использование:
  ./smart_slideshow.py <папка_с_фото> <фото_человека.jpg> <музыка.mp3> [output.mp4]

Как работает:
  1. По референсному фото кодирует лицо
  2. Сканирует все фото в папке, находит те, где есть этот человек
  3. Оценивает качество: резкость, яркость, размер лица
  4. Читает EXIF-дату, сортирует по времени
  5. Отбирает топ-N лучших (по одному на бит)
  6. Монтирует слайдшоу с кроссфейдами под удары музыки
"""

import sys
import os
import subprocess
import json
import math
from pathlib import Path
from collections import defaultdict

import numpy as np
from PIL import Image, ExifTags
import face_recognition

SUPPORTED_IMAGES = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}

# ============================================================
#  Шаг 1: сбор фото
# ============================================================

def collect_photos(folder: str) -> list[Path]:
    photos = []
    for p in Path(folder).iterdir():
        if p.suffix.lower() in SUPPORTED_IMAGES:
            photos.append(p)
    return photos


# ============================================================
#  Шаг 2: EXIF — дата съёмки
# ============================================================

def get_exif_date(path: Path) -> float | None:
    """Возвращает timestamp из EXIF или None."""
    try:
        img = Image.open(path)
        exif = img.getexif()
        if not exif:
            return None
        for tag_id, value in exif.items():
            tag_name = ExifTags.TAGS.get(tag_id, "")
            if tag_name in ("DateTimeOriginal", "DateTime", "DateTimeDigitized"):
                from datetime import datetime
                return datetime.strptime(value, "%Y:%m:%d %H:%M:%S").timestamp()
    except Exception:
        return None
    return None


# ============================================================
#  Шаг 3: качество фото
# ============================================================

def score_sharpness(img: np.ndarray) -> float:
    """Оценка резкости через дисперсию Лапласиана."""
    import cv2
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    return float(laplacian.var())


def score_brightness(img: np.ndarray) -> float:
    """Штраф за пересвет/недосвет. 1.0 = идеально, 0 = плохо."""
    gray = np.mean(img, axis=2)  # среднее по каналам
    mean_val = np.mean(gray)
    # Идеальная яркость ~128, штрафуем отклонения
    score = 1.0 - abs(mean_val - 128) / 128
    return max(0.0, float(score))


def score_face_quality(face_locations: list, img_shape: tuple) -> float:
    """Оценка: насколько лицо крупное и центрированное."""
    if not face_locations:
        return 0.0
    h, w = img_shape[:2]
    best = 0.0
    center_x, center_y = w / 2, h / 2
    for top, right, bottom, left in face_locations:
        face_w = right - left
        face_h = bottom - top
        face_area = face_w * face_h
        img_area = w * h
        # Доля кадра, занятая лицом (идеал ~10-20%)
        area_ratio = face_area / img_area
        area_score = 1.0 - abs(area_ratio - 0.12) / 0.12
        area_score = max(0.0, min(1.0, area_score))
        # Центрирование лица
        face_cx = (left + right) / 2
        face_cy = (top + bottom) / 2
        dist = math.sqrt((face_cx - center_x)**2 + (face_cy - center_y)**2)
        max_dist = math.sqrt(center_x**2 + center_y**2)
        centering_score = 1.0 - dist / max_dist
        combined = area_score * 0.6 + centering_score * 0.4
        best = max(best, combined)
    return best


# ============================================================
#  Шаг 4: поиск человека
# ============================================================

def encode_reference_face(ref_path: str) -> list:
    """Кодирует ВСЕ лица с референсного фото. Возвращает список кодировок."""
    img = face_recognition.load_image_file(ref_path)
    encodings = face_recognition.face_encodings(img, model="hog")
    if not encodings:
        print(f"Лицо не найдено на референсном фото: {ref_path}")
        sys.exit(1)
    print(f"На референсе найдено {len(encodings)} лиц(а), используются все")
    return encodings


def find_person_photos(
    photos: list[Path],
    ref_encodings: list,
    tolerance: float = 0.55,
    solo_only: bool = True,
    portrait_only: bool = True,
) -> list[dict]:
    """
    Возвращает список dict с фото, где найден человек:
    {path, face_loc, timestamp, sharpness, brightness, face_quality, total_score}

    solo_only — только фото где ОДИН человек (нет посторонних)
    portrait_only — только портретные (высота > ширина)
    """
    results = []
    total = len(photos)
    skipped_solo = 0
    skipped_landscape = 0

    for idx, path in enumerate(photos):
        print(f"\rСканирование: {idx+1}/{total}", end="", flush=True)
        try:
            img = face_recognition.load_image_file(str(path))
            h, w = img.shape[:2]
            if h < 80 or w < 80:
                continue
        except Exception:
            continue

        if portrait_only and h <= w:
            skipped_landscape += 1
            continue

        face_locations = face_recognition.face_locations(img, model="hog")
        if not face_locations:
            continue

        face_encodings = face_recognition.face_encodings(img, face_locations)

        # Проверяем совпадение с ЛЮБЫМ из референсных лиц
        any_match = False
        matched_locs = []
        for i, face_enc in enumerate(face_encodings):
            for ref_enc in ref_encodings:
                if face_recognition.compare_faces([face_enc], ref_enc, tolerance=tolerance)[0]:
                    any_match = True
                    matched_locs.append(face_locations[i])
                    break

        if not any_match:
            continue

        if solo_only and len(face_locations) > 1:
            skipped_solo += 1
            continue

        sharp = score_sharpness(img)
        bright = score_brightness(img)
        face_q = score_face_quality(matched_locs, img.shape)
        ts = get_exif_date(path)

        total_score = sharp * 0.35 + bright * 0.15 + face_q * 0.50

        results.append({
            "path": path,
            "timestamp": ts,
            "sharpness": sharp,
            "brightness": bright,
            "face_quality": face_q,
            "total_score": total_score,
        })

    print()
    if skipped_solo:
        print(f"  Пропущено групповых фото: {skipped_solo}")
    if skipped_landscape:
        print(f"  Пропущено альбомных фото: {skipped_landscape}")
    return results


# ============================================================
#  Шаг 5: отбор лучших и сортировка
# ============================================================

def select_and_sort(
    found: list[dict],
    beat_count: int,
    min_score: float = 0.3,
    prefer_diverse: bool = True,
) -> list[Path]:
    """
    Отбирает лучшие фото, сортирует по времени.
    Если фото с EXIF-датой недостаточно, добирает по качеству.
    """
    if not found:
        print("Не найдено ни одного фото с этим человеком!")
        sys.exit(1)

    # Фильтруем по минимальному качеству
    good = [r for r in found if r["total_score"] >= min_score]
    if len(good) < beat_count:
        # Снижаем порог или берём всё что есть
        good = sorted(found, key=lambda r: r["total_score"], reverse=True)
        good = good[:max(beat_count, len(good))]

    # Разделяем: с датой и без
    with_date = [r for r in good if r["timestamp"] is not None]
    without_date = [r for r in good if r["timestamp"] is None]

    # Сортируем с датой по времени
    with_date.sort(key=lambda r: r["timestamp"])

    # Сортируем без даты по качеству (для добивки)
    without_date.sort(key=lambda r: r["total_score"], reverse=True)

    print(f"Найдено с человеком: {len(found)},  хороших: {len(good)},  с датой: {len(with_date)}")

    # Если prefer_diverse — убираем дубли по близкому времени (< 2 сек)
    if prefer_diverse and with_date:
        deduped = [with_date[0]]
        for r in with_date[1:]:
            if r["timestamp"] - deduped[-1]["timestamp"] > 2.0:
                deduped.append(r)
        with_date = deduped

    # Отбираем: сначала хронология, потом добивка по качеству
    selected = with_date[:beat_count]
    if len(selected) < beat_count:
        selected += without_date[:beat_count - len(selected)]

    # Если всё ещё мало — циклически повторяем (равномерно)
    if len(selected) < beat_count and len(selected) > 0:
        while len(selected) < beat_count:
            selected += selected[:beat_count - len(selected)]

    return [r["path"] for r in selected[:beat_count]]


# ============================================================
#  Шаг 6: аудиоанализ (биты)
# ============================================================

def detect_beats(audio_path: str, max_beats: int = 40) -> list[float]:
    import librosa
    print("Анализ битов...")
    y, sr = librosa.load(audio_path)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    tempo_val = float(tempo.item()) if hasattr(tempo, 'item') else float(tempo)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr).tolist()
    print(f"  Темп: {tempo_val:.1f} BPM,  битов: {len(beat_times)}")

    # Прореживаем если битов > max_beats (лимит ffmpeg)
    if len(beat_times) > max_beats:
        step = len(beat_times) / max_beats
        sampled = [beat_times[int(i * step)] for i in range(max_beats)]
        print(f"  Прорежено до {len(sampled)} битов (лимит ffmpeg)")
        return sampled
    return beat_times


def audio_duration(audio_path: str) -> float:
    result = subprocess.run([
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", audio_path
    ], capture_output=True, text=True, check=True)
    info = json.loads(result.stdout)
    return float(info["format"]["duration"])


# ============================================================
#  Шаг 7: монтаж видео — с вариативными эффектами
# ============================================================

# Набор переходов (xfade): мягкие, без перебора
TRANSITIONS = [
    "fade",       # основной — мягкий
    "fade",       # снова fade (чаще всего)
    "dissolve",   # растворение
    "fade",       # fade
    "fadewhite",  # воздушная вспышка
    "fade",       # fade
    "fadeblack",  # драматичная пауза
    "fade",       # fade
    "circleopen", # мягкое открытие кругом
]


# Вариации зума: (zoom_expr, x_expr, y_expr)
ZOOM_VARIANTS = [
    # zoom-in к центру
    ("min(zoom+0.0012,1.25)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    # zoom-out от центра
    ("max(zoom-0.0012,1.0)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    # zoom-in + панорама вправо
    ("min(zoom+0.0010,1.2)", "iw/2-(iw/zoom/2)+on*2", "ih/2-(ih/zoom/2)"),
    # zoom-in + панорама влево
    ("min(zoom+0.0010,1.2)", "iw/2-(iw/zoom/2)-on*2", "ih/2-(ih/zoom/2)"),
    # static — без зума
    ("1.0", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
]


def build_slideshow(
    photos: list[Path],
    beat_times: list[float],
    audio_path: str,
    output: str,
    width: int = 1080,
    height: int = 1920,
    fade: float = 0.5,
    fps: int = 25,
):
    total_duration = audio_duration(audio_path)
    print(f"Длительность трека: {total_duration:.1f}с")
    print(f"Фото в слайдшоу: {len(photos)}")

    # Циклически повторяем фото если их меньше чем битов
    photo_pool = list(photos)
    while len(photo_pool) < len(beat_times):
        photo_pool.extend(photos)

    segments = []
    for i, beat in enumerate(beat_times):
        next_beat = beat_times[i + 1] if i + 1 < len(beat_times) else total_duration
        segments.append({
            "photo": photo_pool[i],
            "start": max(0, beat - fade),
            "duration": next_beat - beat + fade,
        })

    inputs = []
    for seg in segments:
        duration = max(seg["duration"], 0.1)
        inputs.extend(["-loop", "1", "-t", f"{duration:.3f}", "-i", str(seg["photo"])])

    filter_parts = []
    n_segs = len(segments)

    for i in range(n_segs):
        dur = max(segments[i]["duration"], 0.1)
        dur_frames = max(int(dur * fps), 1)

        # Вариация зума — по кругу
        zoom_z, zoom_x, zoom_y = ZOOM_VARIANTS[i % len(ZOOM_VARIANTS)]

        filter_parts.append(
            f"[{i}:v]"
            f"scale=w={width}:h={height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},"
            f"zoompan=z='{zoom_z}':d={dur_frames}:"
            f"x='{zoom_x}':y='{zoom_y}':s={width}x{height},"
            f"settb=AVTB,fps={fps},setpts=PTS-STARTPTS"
            f"[v{i}]"
        )

    prev = "v0"
    for i in range(1, n_segs):
        offset = segments[i]["start"] - segments[0]["start"]
        fade_dur = min(fade, segments[i - 1]["duration"] * 0.4)
        current = f"v{i}_mix"

        # Вариация перехода — по кругу
        transition = TRANSITIONS[(i - 1) % len(TRANSITIONS)]

        filter_parts.append(
            f"[{prev}][v{i}]xfade=transition={transition}:"
            f"duration={fade_dur:.2f}:offset={offset:.3f}"
            f"[{current}]"
        )
        prev = current

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


# ============================================================
#  main
# ============================================================

def main():
    if len(sys.argv) < 4:
        print(
            "Использование:\n"
            "  Распознавание: smart_slideshow.py <папка_с_фото> <фото_человека.jpg> <музыка.mp3> [output.mp4]\n"
            "  Напрямую:     smart_slideshow.py direct <папка_с_фото> <музыка.mp3> [output.mp4]"
        )
        sys.exit(1)

    # Режим direct — без распознавания лиц, фото уже отобраны
    if sys.argv[1] == "direct":
        photo_dir = sys.argv[2]
        audio_path = sys.argv[3]
        output = sys.argv[4] if len(sys.argv) > 4 else "slideshow.mp4"

        if not os.path.isdir(photo_dir):
            print(f"Папка не найдена: {photo_dir}")
            sys.exit(1)
        if not os.path.isfile(audio_path):
            print(f"Аудио не найдено: {audio_path}")
            sys.exit(1)

        photos = collect_photos(photo_dir)
        print(f"Фото в папке: {len(photos)}")
        if not photos:
            sys.exit(1)

        beat_times = detect_beats(audio_path, max_beats=min(len(photos), 40))
        print(f"Битов: {len(beat_times)}")

        build_slideshow(photos, beat_times, audio_path, output)
        return

    # Обычный режим — с распознаванием лиц
    photo_dir = sys.argv[1]
    ref_photo = sys.argv[2]
    audio_path = sys.argv[3]
    output = sys.argv[4] if len(sys.argv) > 4 else "smart_slideshow.mp4"

    for path, label in [(photo_dir, "Папка"), (ref_photo, "Референс"), (audio_path, "Аудио")]:
        if not os.path.exists(path):
            print(f"{label} не найден(о): {path}")
            sys.exit(1)

    print(f"Эталонное фото: {ref_photo}")
    ref_encodings = encode_reference_face(ref_photo)

    photos = collect_photos(photo_dir)
    print(f"Всего фото в папке: {len(photos)}")

    beat_times = detect_beats(audio_path)

    # Ограничиваем выборку для скорости (если > 500 фото)
    if len(photos) > 500:
        step = max(1, len(photos) // 400)
        photos = photos[::step]
        print(f"  Выборка для скорости: {len(photos)} из {len(photos) * step}")

    found = find_person_photos(photos, ref_encodings, tolerance=0.6)

    selected = select_and_sort(found, len(beat_times))

    print(f"Отобрано для слайдшоу: {len(selected)}")
    for p in selected:
        print(f"  {p.name}")

    build_slideshow(selected, beat_times, audio_path, output)


if __name__ == "__main__":
    main()
