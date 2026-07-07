#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build a vertical 1080x1920 MP4 slideshow for Maria's 10th birthday.

Parameters (confirmed by user):
- Output: /Users/igorvasin/Desktop/maria_10_ave_maria_1080x1920.mp4
- Resolution: 1080x1920 (9:16 vertical)
- Music: Giorgia Fumanti - Ave Maria (~70 BPM)
- Rhythm: slide change every 4 beats
- Include MOV videos
- No text titles
- Best photos selected, chronological order
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from datetime import datetime



# ─── Paths ────────────────────────────────────────────────────────────────────
SOURCE_DIR  = Path("/Users/igorvasin/Documents/Маша/download")
MUSIC_SRC   = Path("/Users/igorvasin/Downloads/Giorgia Fumanti - Ave Maria.mp3")
PROJECT_DIR = Path("/Users/igorvasin/freelance-2026/my-project/media/masha")
ASSETS_DIR  = PROJECT_DIR / "assets"
CLIPS_DIR   = PROJECT_DIR / "clips"
MUSIC_DIR   = PROJECT_DIR / "music"
OUT_FILE    = Path("/Users/igorvasin/Desktop/maria_10_ave_maria_1080x1920.mp4")

# ─── Parameters ───────────────────────────────────────────────────────────────
TARGET_W        = 1080
TARGET_H        = 1920
FPS             = 30
BPM             = 70.0
BEATS_PER_SLIDE = 4
FADE_S          = 0.6
TARGET_TOTAL_S  = None  # will be read from music

# ─── Logging helpers ──────────────────────────────────────────────────────────
def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def run(cmd, **kwargs):
    """Run a shell command and print it."""
    if isinstance(cmd, list):
        print("$ " + " ".join(str(c) for c in cmd), flush=True)
    else:
        print("$ " + cmd, flush=True)
    result = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True, **kwargs)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}", flush=True)
        raise RuntimeError(f"Command failed: {cmd}")
    return result

def run_with_timeout(cmd, timeout_sec=30, **kwargs):
    """Run command with timeout; return (ok, result_or_None)."""
    if isinstance(cmd, list):
        print("$ " + " ".join(str(c) for c in cmd), flush=True)
    else:
        print("$ " + cmd, flush=True)
    try:
        result = subprocess.run(
            cmd, shell=isinstance(cmd, str), capture_output=True, text=True,
            timeout=timeout_sec, **kwargs
        )
        return result.returncode == 0, result
    except subprocess.TimeoutExpired as e:
        log(f"TIMEOUT after {timeout_sec}s: {cmd if isinstance(cmd, str) else ' '.join(str(c) for c in cmd)}")
        return False, e
    except Exception as e:
        log(f"ERROR running command: {e}")
        return False, e

# ─── Music duration ───────────────────────────────────────────────────────────
def get_music_duration(path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=True
    )
    return float(result.stdout.strip())

# ─── Asset preparation ────────────────────────────────────────────────────────
def is_file_local(path):
    """Check if file data is actually stored locally (not an iCloud placeholder)."""
    try:
        result = subprocess.run(
            ["stat", "-f", "%b", str(path)],
            capture_output=True, text=True, timeout=5, check=True
        )
        blocks = int(result.stdout.strip())
        return blocks > 0
    except Exception:
        return False

def prepare_dirs():
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    CLIPS_DIR.mkdir(parents=True, exist_ok=True)
    MUSIC_DIR.mkdir(parents=True, exist_ok=True)

def copy_music():
    dest = MUSIC_DIR / "ave_maria.mp3"
    if not dest.exists():
        shutil.copy2(MUSIC_SRC, dest)
        log(f"Music copied -> {dest}")
    return dest

def convert_heic_to_jpg(src, dst):
    ok, _ = run_with_timeout(
        ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "90",
         str(src), "--out", str(dst)],
        timeout_sec=60
    )
    return ok

def convert_image_to_jpg(src, dst):
    """Normalize JPG/PNG/DNG to JPG using ffmpeg (with timeout)."""
    ok, res = run_with_timeout(
        ["ffmpeg", "-y", "-i", str(src),
         "-vf", "scale='min(2560,iw)':-1",
         "-q:v", "2",
         str(dst)],
        timeout_sec=30
    )
    if not ok:
        err = res.stderr[-200:] if hasattr(res, 'stderr') and res.stderr else ""
        log(f"  ffmpeg conversion failed: {err}")
    return ok

def collect_assets():
    """Convert/copy all source images and videos to assets/."""
    image_assets = []
    video_assets = []
    counter_img = 1
    counter_vid = 1

    files = sorted(SOURCE_DIR.iterdir())
    log(f"Found {len(files)} source files")

    for f in files:
        ext = f.suffix.lower()
        if not f.is_file():
            continue

        if not is_file_local(f):
            log(f"  SKIP (not local/iCloud): {f.name}")
            continue

        if ext in (".jpg", ".jpeg", ".png", ".heic", ".dng"):
            out_name = f"img_{counter_img:03d}.jpg"
            out_path = ASSETS_DIR / out_name
            if out_path.exists():
                log(f"  skip (exists): {out_name}")
                image_assets.append(out_path)
                counter_img += 1
                continue

            ok = False
            if ext in (".heic", ".dng"):
                ok = convert_heic_to_jpg(f, out_path)
                if ok:
                    log(f"  {ext.upper()} -> JPG: {f.name}")
            else:
                ok = convert_image_to_jpg(f, out_path)
                if ok:
                    log(f"  converted: {f.name}")

            if ok:
                image_assets.append(out_path)
                counter_img += 1

        elif ext == ".mov":
            if not is_file_local(f):
                log(f"  SKIP (not local/iCloud): {f.name}")
                continue
            out_name = f"vid_{counter_vid:03d}.mp4"
            out_path = ASSETS_DIR / out_name
            if out_path.exists():
                log(f"  skip (exists): {out_name}")
                video_assets.append(out_path)
                counter_vid += 1
                continue

            # Convert MOV to normalized vertical MP4 (center crop, 30fps)
            ok, res = run_with_timeout(
                ["ffmpeg", "-y", "-i", str(f),
                 "-vf", f"scale='if(gte(iw/ih,{TARGET_W}/{TARGET_H}),-1,{TARGET_W})':'if(gte(iw/ih,{TARGET_W}/{TARGET_H}),{TARGET_H},-1)',crop={TARGET_W}:{TARGET_H}",
                 "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                 "-r", str(FPS), "-pix_fmt", "yuv420p", "-an",
                 str(out_path)],
                timeout_sec=120
            )
            if ok:
                log(f"  MOV -> MP4: {f.name}")
                video_assets.append(out_path)
                counter_vid += 1
            else:
                err = res.stderr.strip()[:200] if hasattr(res, 'stderr') and res.stderr else "timeout/error"
                log(f"  FAILED MOV: {f.name}: {err}")

    log(f"Total image assets: {len(image_assets)}")
    log(f"Total video assets: {len(video_assets)}")
    return image_assets, video_assets

# ─── Quality scoring for images ───────────────────────────────────────────────
def image_quality_score(path):
    """Return a quality score based on sharpness and exposure using ffmpeg."""
    tmp = tempfile.NamedTemporaryFile(suffix=".raw", delete=False)
    tmp.close()
    try:
        ok, res = run_with_timeout(
            ["ffmpeg", "-y", "-i", str(path),
             "-vf", "scale=512:512:force_original_aspect_ratio=decrease,format=gray",
             "-frames:v", "1",
             "-f", "rawvideo", "-pix_fmt", "gray",
             tmp.name],
            timeout_sec=20
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
        # Sobel-like sharpness: variance of edges
        edges_ok, _ = run_with_timeout(
            ["ffmpeg", "-y", "-i", str(path),
             "-vf", "scale=512:512:force_original_aspect_ratio=decrease,format=gray,edgedetect=low=0.1:high=0.4",
             "-frames:v", "1",
             "-f", "rawvideo", "-pix_fmt", "gray",
             tmp.name],
            timeout_sec=20
        )
        if edges_ok:
            with open(tmp.name, "rb") as f:
                edge_data = f.read()
            edge_pixels = list(edge_data)
            edge_mean = sum(edge_pixels) / len(edge_pixels)
            edge_var = sum((x - edge_mean) ** 2 for x in edge_pixels) / len(edge_pixels)
        else:
            edge_var = variance

        # Exposure: prefer neither too dark nor too bright
        exposure_penalty = abs(mean - 128) / 128.0
        score = edge_var * (1.0 - 0.5 * exposure_penalty)
        return score
    except Exception as e:
        log(f"Quality check failed for {path}: {e}")
        return 0.0
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass

def select_best_images(image_assets, target_count):
    """Select best images while preserving chronological order."""
    if len(image_assets) <= target_count:
        return image_assets

    log("Scoring image quality...")
    scored = [(p, image_quality_score(p)) for p in image_assets]
    # Filter out bottom 25% by quality
    scores = sorted([s for _, s in scored])
    threshold_idx = int(len(scores) * 0.25)
    threshold = scores[threshold_idx] if threshold_idx < len(scores) else 0

    good = [p for p, s in scored if s >= threshold]
    good.sort(key=lambda p: p.name)  # chronological by filename

    if len(good) <= target_count:
        return good

    # Evenly subsample to target_count while keeping chronological order
    step = len(good) / target_count
    selected = [good[int(i * step)] for i in range(target_count)]
    log(f"Selected {len(selected)} best images (from {len(image_assets)} total)")
    return selected

# ─── Build ordered asset list ─────────────────────────────────────────────────
def build_timeline(image_assets, video_assets, total_needed):
    """Combine images and videos chronologically into one timeline."""
    all_assets = []
    for p in image_assets:
        all_assets.append(("image", p))
    for p in video_assets:
        all_assets.append(("video", p))

    # Sort by original filename stem to maintain chronological order
    def sort_key(item):
        kind, path = item
        # Try to preserve original filename ordering; fallback to asset name
        return path.name

    all_assets.sort(key=sort_key)

    if len(all_assets) > total_needed:
        # If too many, we already limited images; videos are included.
        # As last resort, evenly subsample combined timeline.
        step = len(all_assets) / total_needed
        all_assets = [all_assets[int(i * step)] for i in range(total_needed)]

    log(f"Timeline length: {len(all_assets)} assets")
    return all_assets

# ─── Generate individual slide clips ──────────────────────────────────────────
def generate_clip(kind, src_path, idx, duration):
    out_path = CLIPS_DIR / f"clip_{idx:03d}.mp4"

    # Choose subtle Ken Burns direction (alternate zoom/pan)
    zoom_expr = "zoom+0.0004" if idx % 2 == 0 else "zoom-0.0003"
    # Ensure zoom stays in reasonable range
    zoom_expr = f"min(max({zoom_expr},1.0),1.12)"

    # Center crop expressions for zoompan
    x_expr = "iw/2-(iw/zoom/2)"
    y_expr = "ih/2-(ih/zoom/2)"

    frames = int(round(duration * FPS))

    if kind == "image":
        vf = (
            f"scale='if(gte(iw/ih,{TARGET_W}/{TARGET_H}),-1,{TARGET_W})':'if(gte(iw/ih,{TARGET_W}/{TARGET_H}),{TARGET_H},-1)',"
            f"crop={TARGET_W}:{TARGET_H},"
            f"zoompan=z='{zoom_expr}':x='{x_expr}':y='{y_expr}':d={frames}:s={TARGET_W}x{TARGET_H},"
            f"eq=contrast=1.03:brightness=0.015:saturation=1.05,"
            f"colorchannelmixer=rr=1.04:rg=0.02:rb=-0.02:gr=-0.01:gg=1.02:gb=0.01"
        )
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", str(src_path),
            "-vf", vf,
            "-t", str(duration),
            "-r", str(FPS), "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-an",
            str(out_path)
        ]
    else:  # video
        vf = (
            f"scale='if(gte(iw/ih,{TARGET_W}/{TARGET_H}),-1,{TARGET_W})':'if(gte(iw/ih,{TARGET_W}/{TARGET_H}),{TARGET_H},-1)',"
            f"crop={TARGET_W}:{TARGET_H},"
            f"eq=contrast=1.03:brightness=0.015:saturation=1.05,"
            f"colorchannelmixer=rr=1.04:rg=0.02:rb=-0.02:gr=-0.01:gg=1.02:gb=0.01"
        )
        cmd = [
            "ffmpeg", "-y", "-stream_loop", "-1", "-i", str(src_path),
            "-vf", vf,
            "-t", str(duration),
            "-r", str(FPS), "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-an",
            str(out_path)
        ]

    ok, res = run_with_timeout(cmd, timeout_sec=60)
    if not ok:
        err = res.stderr[:500] if hasattr(res, 'stderr') and res.stderr else str(res)
        log(f"Failed to generate clip {idx}: {err}")
        raise RuntimeError(f"Clip generation failed for {src_path}")
    return out_path

# ─── Build final video with xfade ─────────────────────────────────────────────
def build_final_video(clip_paths, music_path, out_path):
    n = len(clip_paths)
    music_duration = get_music_duration(music_path)
    slide_interval = music_duration / n  # time between slide starts
    fade = FADE_S

    log(f"Music duration: {music_duration:.3f}s")
    log(f"Slides: {n}, interval: {slide_interval:.3f}s, fade: {fade:.3f}s")

    # Inputs: clips then music
    inputs = []
    for cp in clip_paths:
        inputs.extend(["-i", str(cp)])
    inputs.extend(["-i", str(music_path)])

    # Build xfade chain
    # Each clip i (except last) has duration slide_interval + fade
    # Last clip has duration slide_interval
    filters = []
    prev_label = "0"
    for i in range(n - 1):
        offset = (i + 1) * slide_interval
        next_label = f"xf{i}" if i < n - 2 else "v"
        filters.append(
            f"[{prev_label}][{i+1}]xfade=transition=fade:duration={fade}:offset={offset:.6f}[{next_label}]"
        )
        prev_label = next_label

    filter_complex = ";".join(filters)

    # Build per-clip durations via setpts/trim? ffmpeg xfade needs inputs long enough.
    # We'll create clips with correct durations already, so just concat.

    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", f"{n}:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-r", str(FPS),
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(out_path)
    ]

    ok, res = run_with_timeout(cmd, timeout_sec=1200)
    if not ok:
        err = res.stderr[-1000:] if hasattr(res, 'stderr') and res.stderr else str(res)
        log(f"Final render failed: {err}")
        raise RuntimeError("Final render failed")
    log(f"Final video saved: {out_path}")

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    log("Starting slideshow build")
    prepare_dirs()
    music_path = copy_music()
    TARGET_TOTAL_S = get_music_duration(music_path)

    image_assets, video_assets = collect_assets()

    # Determine number of slides based on music length and beat interval
    beat_interval = 60.0 / BPM
    slide_interval_target = beat_interval * BEATS_PER_SLIDE
    n_slides = round(TARGET_TOTAL_S / slide_interval_target)
    log(f"Target slides for {BPM} BPM: {n_slides}")

    # Reserve slots for videos
    n_videos = len(video_assets)
    n_images_needed = n_slides - n_videos
    if n_images_needed < 0:
        n_images_needed = 0
        # If too many videos, limit them
        video_assets = video_assets[:n_slides]

    selected_images = select_best_images(image_assets, n_images_needed)
    timeline = build_timeline(selected_images, video_assets, n_slides)
    actual_slides = len(timeline)

    # Recalculate exact slide interval for actual slide count
    slide_interval = TARGET_TOTAL_S / actual_slides
    clip_duration = slide_interval + FADE_S

    log(f"Generating {actual_slides} slide clips...")
    clip_paths = []
    for idx, (kind, src) in enumerate(timeline):
        dur = slide_interval if idx == actual_slides - 1 else clip_duration
        cp = generate_clip(kind, src, idx, dur)
        clip_paths.append(cp)

    log("Building final video with crossfade transitions...")
    build_final_video(clip_paths, music_path, OUT_FILE)

    # Verify output
    out_duration = get_music_duration(OUT_FILE)  # ffprobe works for video too
    size_mb = OUT_FILE.stat().st_size / (1024 * 1024)
    log(f"Done! Duration: {out_duration:.2f}s, Size: {size_mb:.1f} MB")

if __name__ == "__main__":
    main()
