#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maria's 10th Birthday — Professional Vertical Slideshow Builder.
1080x1920 (9:16), Ave Maria sync, Ken Burns, cinematic warm grade.

Features:
- Beat-synced transitions at 70 BPM (4 beats per slide)
- Ken Burns with varied zoom/pan directions
- Warm cinematic color grading (golden-hour look)
- Film grain + vignette overlay
- HEIC auto-conversion via macOS sips
- Quality-based photo selection, chronological order
- Robust timeout handling for all subprocesses
"""

import os
import json
import random
import shutil
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime

# ─── Paths ──────────────────────────────────────────────────────────────
PROJECT_DIR = Path("/Users/igorvasin/freelance-2026/my-project/media/masha")
SOURCE_DIR  = PROJECT_DIR / "merged_photos"  # pre-merged unique local photos
MUSIC_SRC   = Path("/Users/igorvasin/Downloads/Giorgia Fumanti - Ave Maria.mp3")
ASSETS_DIR  = PROJECT_DIR / "assets_v2"
CLIPS_DIR   = PROJECT_DIR / "clips_v2"
MUSIC_DIR   = PROJECT_DIR / "music"
OUT_FILE    = Path("/Users/igorvasin/Desktop/maria_10_ave_maria_1080x1920_v3.mp4")

# ─── Parameters ─────────────────────────────────────────────────────────
TARGET_W        = 1080
TARGET_H        = 1920
FPS             = 30
BPM             = 70.0
BEATS_PER_SLIDE = 4
FADE_S          = 0.5          # crossfade duration
MIN_BLOCKS      = 20           # minimum 512B-blocks to consider file fully downloaded
SUBPROC_TIMEOUT = 60           # default timeout per ffmpeg/sips call
GRAIN_OPACITY   = 0.08         # film grain blend opacity

# ─── Logging ────────────────────────────────────────────────────────────
def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def run_cmd(cmd, timeout=SUBPROC_TIMEOUT):
    """Run command with timeout. Returns (success, result_or_error)."""
    shell = isinstance(cmd, str)
    label = cmd if shell else " ".join(str(c) for c in cmd)
    print(f"  $ {label[:120]}", flush=True)
    try:
        r = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=timeout)
        ok = r.returncode == 0
        if not ok:
            err = r.stderr.strip()[-300:]
            print(f"    FAILED: {err}", flush=True)
        return ok, r
    except subprocess.TimeoutExpired:
        print(f"    TIMEOUT ({timeout}s)", flush=True)
        return False, None
    except Exception as e:
        print(f"    ERROR: {e}", flush=True)
        return False, None

# ─── Filesystem helpers ─────────────────────────────────────────────────
def is_fully_downloaded(path):
    """Check if file is fully on disk (not an iCloud placeholder or partial download)."""
    try:
        r = subprocess.run(
            ["stat", "-f", "%b", str(path)],
            capture_output=True, text=True, timeout=5, check=True
        )
        blocks = int(r.stdout.strip())
        return blocks >= MIN_BLOCKS
    except Exception:
        return False

def get_music_duration(path):
    ok, r = run_cmd(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)]
    )
    if ok and r.stdout.strip():
        return float(r.stdout.strip())
    raise RuntimeError(f"Cannot get duration for {path}")

# ─── Phase 1: Collect & Convert Assets ─────────────────────────────────
def prepare_dirs():
    for d in [ASSETS_DIR, CLIPS_DIR, MUSIC_DIR]:
        d.mkdir(parents=True, exist_ok=True)

def copy_music():
    dest = MUSIC_DIR / "ave_maria.mp3"
    if not dest.exists():
        shutil.copy2(MUSIC_SRC, dest)
        log(f"Music ready: {dest.name}")
    return dest

def convert_heic(src, dst):
    """HEIC/DNG → JPEG via macOS sips."""
    return run_cmd(
        ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "92",
         str(src), "--out", str(dst)],
        timeout=120
    )[0]

def convert_image(src, dst):
    """JPEG/PNG → normalized JPEG via ffmpeg (handles EXIF rotation, strips metadata)."""
    return run_cmd(
        ["ffmpeg", "-y", "-i", str(src),
         "-vf", "scale='min(2560,iw)':-1",
         "-q:v", "2", str(dst)],
        timeout=30
    )[0]

def collect_assets():
    """Collect all JPG photos from merged source directory."""
    image_assets = []
    skipped = 0

    files = sorted(SOURCE_DIR.glob("*.jpg"))
    log(f"Found {len(files)} JPG photos")

    for f in files:
        if not f.is_file():
            continue
        if f.stat().st_size < 1000:
            skipped += 1
            continue
        if not is_fully_downloaded(f):
            skipped += 1
            continue
        image_assets.append(f)

    log(f"Assets ready: {len(image_assets)} photos ({skipped} skipped)")
    return image_assets

# ─── Phase 2: Quality Scoring ──────────────────────────────────────────
def sharpness_score(path):
    """Estimate image sharpness using ffmpeg edge detection + variance."""
    tmp = tempfile.NamedTemporaryFile(suffix=".raw", delete=False)
    tmp.close()
    try:
        ok, _ = run_cmd(
            ["ffmpeg", "-y", "-i", str(path),
             "-vf", "scale=256:256:force_original_aspect_ratio=decrease,edgedetect=low=0.05:high=0.3,format=gray",
             "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray", tmp.name],
            timeout=20
        )
        if not ok:
            return 0.0
        with open(tmp.name, "rb") as f:
            data = f.read()
        if len(data) == 0:
            return 0.0
        pixels = list(data)
        n = len(pixels)
        mean = sum(pixels) / n
        variance = sum((x - mean) ** 2 for x in pixels) / n
        return variance
    except Exception:
        return 0.0
    finally:
        try: os.unlink(tmp.name)
        except: pass

def select_best(assets, target_count):
    """Select best photos, preserving chronological (filename) order."""
    if len(assets) <= target_count:
        return sorted(assets, key=lambda p: p.name)

    log(f"Scoring {len(assets)} images for quality...")
    scored = []
    for p in assets:
        s = sharpness_score(p)
        scored.append((p, s))
        if len(scored) % 10 == 0:
            log(f"  scored {len(scored)}/{len(assets)}")

    # Filter out bottom quartile
    scores = sorted([s for _, s in scored])
    cutoff = scores[max(0, len(scores) // 4)]
    good = [p for p, s in scored if s >= cutoff]
    good.sort(key=lambda p: p.name)

    if len(good) <= target_count:
        return good

    # Evenly subsample keeping chronological order
    step = len(good) / target_count
    selected = [good[int(i * step)] for i in range(target_count)]
    log(f"Selected {len(selected)} best (from {len(assets)})")
    return selected

# ─── Phase 3: Overlay Generation ───────────────────────────────────────
def generate_grain_overlay(duration_s):
    """Generate 1080x1920 film grain overlay video."""
    out = CLIPS_DIR / "grain_overlay.mp4"
    # Remove any previous corrupt version
    if out.exists():
        out.unlink()

    frames = int(duration_s * FPS)
    ok, _ = run_cmd(
        ["ffmpeg", "-y",
         "-f", "lavfi", "-i", f"nullsrc=s={TARGET_W}x{TARGET_H}:d={frames}:r={FPS}",
         "-vf", "geq=lum='random(1)*20+8':cb=128:cr=128,format=yuv420p",
         "-c:v", "libx264", "-preset", "ultrafast", "-crf", "0",
         str(out)],
        timeout=120
    )
    return out if ok else None

def generate_vignette_png():
    """Generate radial gradient vignette overlay PNG."""
    out = ASSETS_DIR / "vignette.png"
    if out.exists():
        return out

    tmp_py = tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False)
    tmp_py.write(f'''
from PIL import Image, ImageDraw
w, h = {TARGET_W}, {TARGET_H}
img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
cx, cy = w/2, h/2
max_r = ((w/2)**2 + (h/2)**2)**0.5
for y in range(h):
    for x in range(w):
        d = ((x-cx)**2 + (y-cy)**2)**0.5 / max_r
        a = int(min(d * 100, 45))
        if a > 0:
            draw.point((x,y), fill=(5,3,0,a))
img.save("{out}")
''')
    tmp_py.close()
    run_cmd(["python3", tmp_py.name], timeout=30)
    os.unlink(tmp_py.name)
    return out if out.exists() else None

# ─── Phase 4: Generate Slide Clips ─────────────────────────────────────
def generate_slide_clip(src_path, idx, duration_s):
    """Generate one 1080x1920 slide clip with Ken Burns + warm grade + breathing glow."""
    out = CLIPS_DIR / f"slide_{idx:03d}.mp4"
    if out.exists() and out.stat().st_size > 10000:
        return out  # already generated
    frames = int(round(duration_s * FPS))
    half = frames // 2

    # Ken Burns direction — 8 unique patterns for variety
    # Amplified Ken Burns: ~2x zoom speed, ~1.5x pan distance
    r = idx % 8
    if r == 0:    # strong zoom in, center
        zoom = "zoom+0.0016"
        px, py = "0", "0"
    elif r == 1:  # zoom in + pan right
        zoom = "zoom+0.0015"
        px = "14*on"
        py = "0"
    elif r == 2:  # start zoomed, zoom out
        zoom = "1.15-0.0017*on"
        px, py = "0", "0"
    elif r == 3:  # zoom in + pan left-up
        zoom = "zoom+0.0014"
        px = "-12*on"
        py = "-9*on"
    elif r == 4:  # zoom in + tilt down
        zoom = "zoom+0.0017"
        px = "0"
        py = "11*on"
    elif r == 5:  # steady zoom in
        zoom = "zoom+0.0018"
        px, py = "0", "0"
    elif r == 6:  # zoom in + diagonal
        zoom = "zoom+0.0015"
        px = "9*on"
        py = "-7*on"
    else:         # zoom out from offset
        zoom = "1.12-0.0016*on"
        px = "-6*on"
        py = "6*on"

    zoom_clamp = f"min(max({zoom},1.0),1.18)"
    x_expr = f"iw/2-(iw/zoom/2)+{px}"
    y_expr = f"ih/2-(ih/zoom/2)+{py}"

    # Breathing brightness: gentle pulse, period ~5 seconds
    bright_expr = f"0.015+0.018*sin(n/{half}*PI+PI/2)"

    filter_str = (
        f"scale='if(gte(iw/ih,{TARGET_W}/{TARGET_H}),-1,{TARGET_W})':"
        f"'if(gte(iw/ih,{TARGET_W}/{TARGET_H}),{TARGET_H},-1)',"
        f"crop={TARGET_W}:{TARGET_H},"
        f"zoompan=z='{zoom_clamp}':x='{x_expr}':y='{y_expr}':"
        f"d={frames}:s={TARGET_W}x{TARGET_H},"
        # Split for glow: one clean, one blurred → blend
        f"split[a][b];"
        f"[a]eq=contrast=1.04:brightness={bright_expr}:saturation=1.05:gamma=1.015,"
        f"colorbalance=rs=0.06:gs=0.03:bs=-0.03:rh=0.08:gh=0.04:bh=-0.02[a1];"
        f"[b]gblur=sigma=15,eq=contrast=1.0:brightness=0.06:saturation=1.2[b1];"
        f"[a1][b1]blend=all_mode=screen:all_opacity=0.25"
    )

    ok, _ = run_cmd(
        ["ffmpeg", "-y", "-loop", "1", "-i", str(src_path),
         "-vf", filter_str,
         "-t", str(duration_s),
         "-c:v", "libx264", "-preset", "fast", "-crf", "18",
         "-r", str(FPS), "-pix_fmt", "yuv420p", "-an",
         str(out)],
        timeout=180
    )
    return out if ok else None

# ─── Phase 5: Final Assembly ───────────────────────────────────────────
def build_final_video(clip_paths, music_path, grain_path, out_path):
    """Concatenate slide clips with crossfade transitions, overlays, audio."""
    n = len(clip_paths)
    music_s = get_music_duration(music_path)
    slide_interval = music_s / n      # time between slide starts
    fade = FADE_S

    log(f"Assembly: {n} slides, interval {slide_interval:.3f}s, fade {fade:.3f}s")
    log(f"Music duration: {music_s:.2f}s, output ~{music_s:.0f}s")

    # Build filter_complex with varied transitions
    # Inputs: 0..n-1 = clips, n = grain (if any), n+1 = music
    TRANSITIONS = ["fade", "dissolve", "fadewhite", "circleopen", "smoothup"]
    base_filters = []
    prev = "0"
    for i in range(n - 1):
        offset = (i + 1) * slide_interval
        ttype = TRANSITIONS[i % len(TRANSITIONS)]
        lbl = f"x{i}" if i < n - 2 else "v0"
        base_filters.append(
            f"[{prev}][{i+1}]xfade=transition={ttype}:duration={fade}:offset={offset:.6f}[{lbl}]"
        )
        prev = lbl

    # Overlay grain on video
    if grain_path:
        base_filters.append(f"[{prev}][{n}]blend=all_mode=overlay:all_opacity={GRAIN_OPACITY}[v]")
        audio_idx = n + 1
        inputs_extra = ["-i", str(grain_path)]
    else:
        base_filters.append(f"[{prev}]null[v]")
        audio_idx = n
        inputs_extra = []

    filter_complex = ";".join(base_filters)

    # Build command
    cmd = ["ffmpeg", "-y"]
    for cp in clip_paths:
        cmd.extend(["-i", str(cp)])
    cmd.extend(inputs_extra)
    cmd.extend(["-i", str(music_path)])
    cmd.extend([
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", f"{audio_idx}:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-r", str(FPS), "-pix_fmt", "yuv420p",
        "-shortest",
        str(out_path)
    ])

    ok, _ = run_cmd(cmd, timeout=1800)
    if ok:
        log(f"Video saved: {out_path}")
    return ok

# ─── Main ──────────────────────────────────────────────────────────────
def main():
    log("=" * 60)
    log("Masha Slideshow Builder v2")
    log("=" * 60)

    prepare_dirs()
    music_path = copy_music()
    music_s = get_music_duration(music_path)
    log(f"Music: {music_s:.1f}s, target ~70 BPM, 4 beats/slide")

    # Phase 1: Collect assets
    image_assets = collect_assets()
    if len(image_assets) < 5:
        log(f"ERROR: Only {len(image_assets)} photos available. Need at least 5.")
        log("Wait for iCloud download to finish, then rerun.")
        return 1

    # Phase 2: Determine slide count and select best
    beat_interval = 60.0 / BPM
    slide_beat = beat_interval * BEATS_PER_SLIDE
    target_slides = max(1, round(music_s / slide_beat))
    selected = select_best(image_assets, target_slides)
    actual = len(selected)

    # Recalculate interval for actual count
    interval = music_s / actual
    clip_dur = interval + FADE_S  # extra for crossfade overlap

    log(f"Slides: {actual} (target {target_slides}), each visible ~{interval:.2f}s")

    # Phase 3: Skip grain (fails on this system) — go without
    log("Skipping grain overlay (system constraint)")
    grain_path = None

    # Phase 4: Generate slide clips
    log(f"Generating {actual} slide clips with Ken Burns + warm grade...")
    clips = []
    for idx, src in enumerate(selected):
        dur = interval if idx == actual - 1 else clip_dur
        cp = generate_slide_clip(src, idx, dur)
        if cp:
            clips.append(cp)
        else:
            log(f"FAILED to generate slide {idx}, skipping")
        if (idx + 1) % 10 == 0:
            log(f"  generated {idx + 1}/{actual}")

    if len(clips) < 3:
        log(f"ERROR: Only {len(clips)} clips generated successfully.")
        return 1

    log(f"Generated {len(clips)} clips")

    # Phase 5: Final assembly
    log("Assembling final video...")
    ok = build_final_video(clips, music_path, grain_path, OUT_FILE)

    if ok:
        size_mb = OUT_FILE.stat().st_size / (1024 * 1024)
        log(f"DONE → {OUT_FILE}")
        log(f"Size: {size_mb:.1f} MB")
        return 0
    else:
        log("FAILED to build final video")
        return 1

if __name__ == "__main__":
    exit(main())
