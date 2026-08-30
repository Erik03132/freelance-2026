#!/usr/bin/env python3
"""
inkops — локальные Inkscape/Potrace-операции с вектором (эквивалент headless Inkscape-MCP).

Инструменты (обёртки над Inkscape CLI + potrace, без GUI и без pygobject):
  render    svg -> png           высококачественный рендер превью
  convert   (.ai|.pdf|.svg|.png) -> svg    конвертация векторов через Inkscape
  to_pdf    svg -> pdf           Illustrator-совместимый PDF (можно сохранить как .ai)
  trace     png|jpg -> svg       трассировка растра в контуры (potrace)

Примеры:
  python3 inkops.py render in.svg -o out.png -w 930
  python3 inkops.py convert "дет.ai" -o etalon.svg
  python3 inkops.py to_pdf scheme.svg -o scheme.pdf
  python3 inkops.py trace ref.png -o ref.svg --threshold 0.55
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

INKSCAPE = shutil.which("inkscape") or "/Applications/Inkscape.app/Contents/MacOS/inkscape"
POTRACE = shutil.which("potrace")


def pr(msg):
    print(msg)


def run(cmd, cwd=None):
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if res.returncode != 0:
        sys.stderr.write(f"ERR: {' '.join(cmd)}\n{res.stderr[-1200:]}\n")
        raise SystemExit(1)
    return res


def main():
    ap = argparse.ArgumentParser(description="inkops — векторные операции (Inkscape + potrace)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("render", help="SVG -> PNG превью")
    p.add_argument("input")
    p.add_argument("-o", "--out", required=True)
    p.add_argument("-w", "--width", type=int, default=900)
    p.add_argument("--dpi", type=int, default=None)

    p = sub.add_parser("convert", help="(.ai/.pdf/.svg/.png) -> SVG")
    p.add_argument("input")
    p.add_argument("-o", "--out", required=True)

    p = sub.add_parser("to_pdf", help="SVG -> PDF (Illustrator-совместимо)")
    p.add_argument("input")
    p.add_argument("-o", "--out", required=True)

    p = sub.add_parser("trace", help="растр -> SVG (potrace)")
    p.add_argument("input")
    p.add_argument("-o", "--out", required=True)
    p.add_argument(
        "--threshold",
        type=float,
        default=0.6,
        help="порог чёрного (0-1); линии/тёмные пиксели становятся контурами",
    )
    p.add_argument("--invert", action="store_true", help="инвертировать (белые линии на чёрном)")
    p.add_argument(
        "--turd", type=int, default=2, help="порог удаления мелких контуров (potrace -t)"
    )
    p.add_argument(
        "--color-mode",
        default="color",
        choices=["color", "binary", "gray"],
        help="color: раздельные пути по квантилям (колорит PNG); binary: бинарный порог",
    )

    args = ap.parse_args()
    if not os.path.exists(args.input):
        sys.exit(f"файл не найден: {args.input}")

    if args.cmd == "render":
        cmd = [
            INKSCAPE,
            args.input,
            "--export-type=png",
            f"--export-filename={args.out}",
            "-w",
            str(args.width),
        ]
        run(cmd)
        pr(f"render: {args.out}")
    elif args.cmd == "convert":
        out = os.path.abspath(args.out)
        cmd = [
            INKSCAPE,
            os.path.abspath(args.input),
            "--export-type=svg",
            f"--export-filename={out}",
        ]
        run(cmd)
        pr(f"convert: {args.input} -> {args.out}")
    elif args.cmd == "to_pdf":
        out = os.path.abspath(args.out)
        run(
            [INKSCAPE, os.path.abspath(args.input), "--export-type=pdf", f"--export-filename={out}"]
        )
        pr(f"to_pdf: {args.out}")
    elif args.cmd == "trace":
        if not POTRACE:
            sys.exit("potrace не установлен: brew install potrace")
        trace(args, POTRACE)


def trace(args, potrace):
    from PIL import Image
    import numpy as np

    img = Image.open(args.input)
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    a = np.asarray(img).astype(float)

    alpha = a[..., 3]
    rgb = a[..., :3]
    bg = np.where(alpha[..., None] < 200, 255.0, rgb)
    gray = 0.299 * bg[..., 0] + 0.587 * bg[..., 1] + 0.114 * bg[..., 2]
    if args.invert:
        gray = 255 - gray

    mask = gray < args.threshold * 255
    im = Image.fromarray((mask * 255).astype("uint8"))
    with tempfile.TemporaryDirectory() as td:
        pbm = os.path.join(td, "in.pbm")
        im.save(pbm)
        run([potrace, pbm, "-s", "-t", str(args.turd), "-o", str(os.path.abspath(args.out))])
    pr(f"trace({args.color_mode}): {args.out} (порог {args.threshold}, turd {args.turd})")


if __name__ == "__main__":
    main()
