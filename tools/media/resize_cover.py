#!/usr/bin/env python3
"""Resize kwork cover to 660x440 and save as JPG."""
import subprocess
import sys
import os

# Source file path
src = sys.argv[1] if len(sys.argv) > 1 else None
dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kwork_cover_660x440.jpg")

if not src:
    print("Usage: python3 resize_cover.py <source_image_path>")
    print("Drag and drop the PNG file from Finder as the argument")
    sys.exit(1)

# Use sips (built-in macOS tool, no PIL needed)
try:
    subprocess.run([
        "sips", "-z", "440", "660",
        src,
        "--out", dst,
        "-s", "format", "jpeg",
        "-s", "formatOptions", "95"
    ], check=True)
    
    size = os.path.getsize(dst)
    print(f"✅ Saved: {dst}")
    print(f"📐 Dimensions: 660×440 px")
    print(f"📦 Size: {size / 1024:.1f} KB")
    print(f"📂 Format: JPEG (quality 95)")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
