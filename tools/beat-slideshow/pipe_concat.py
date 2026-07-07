#!/usr/bin/env python3
"""Склеивает клипы через pipe — стриминг декодера напрямую в энкодер."""
import subprocess, sys
from pathlib import Path

clips_dir = Path(sys.argv[1])
output = sys.argv[2]
audio = sys.argv[3] if len(sys.argv) > 3 else None

clips = sorted(clips_dir.glob("clip_*.mp4"))
print(f"Склейка {len(clips)} клипов через pipe...")

W, H, FPS = 1080, 1920, 25

enc_cmd = [
    "ffmpeg", "-y",
    "-f", "rawvideo", "-pix_fmt", "yuv420p",
    "-s", f"{W}x{H}", "-r", str(FPS),
    "-i", "-",
]
if audio:
    enc_cmd.extend(["-i", audio])
enc_cmd.extend([
    "-c:v", "h264_videotoolbox", "-b:v", "4M",
    "-pix_fmt", "yuv420p", "-r", str(FPS),
])
if audio:
    enc_cmd.extend(["-c:a", "aac", "-b:a", "192k", "-shortest"])
enc_cmd.extend(["-movflags", "+faststart", output])

encoder = subprocess.Popen(enc_cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

for i, clip in enumerate(clips):
    dec = subprocess.Popen([
        "ffmpeg", "-i", str(clip),
        "-f", "rawvideo", "-pix_fmt", "yuv420p",
        "-s", f"{W}x{H}", "-r", str(FPS), "-"
    ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    try:
        while True:
            chunk = dec.stdout.read(1024 * 1024)  # 1MB chunks
            if not chunk:
                break
            if encoder.stdin and not encoder.stdin.closed:
                encoder.stdin.write(chunk)
            else:
                print(f"\n  Энкодер закрылся на клипе {i+1}!")
                break
    except BrokenPipeError:
        print(f"\n  Broken pipe на клипе {i+1}")
        break

    dec.wait()
    print(f"\r  {i+1}/{len(clips)}", end="", flush=True)

print()
if encoder.stdin and not encoder.stdin.closed:
    encoder.stdin.close()
encoder.wait()

if encoder.returncode != 0:
    err = encoder.stderr.read().decode()[-500:]
    print(f"Ошибка энкодера: {err}")
else:
    print(f"Готово: {output}")
