#!/usr/bin/env python3
"""
Верификация схемы по требованиям ТЗ:
  1. количество деталей ≈ 450
  2. деталь ≤ 30 мм по большей стороне
  3. зазор между деталями ≥ 3 мм
  4. толщина линий 0.2 pt, чёрные контуры / голубые прорисовки
  5. сравнение метрик с эталоном (.ai)

Запуск: python3 verify.py [-s scheme.svg] [-e reference.svg] [--strict]
"""

import argparse
import os
import sys
from lxml import etree
from shapely.geometry import Polygon

NS = {"svg": "http://www.w3.org/2000/svg"}
BLACK = "rgb(0%, 0%, 0%)"
BLUE = "rgb(16.078186%, 67.059326%, 88.627625%)"
MAX_PIECE_SIZE = 30.0  # мм по большей стороне
MIN_GAP = 3.0  # мм
TARGET_COUNT = 450


def parse_svg_polys(fname):
    """Извлекает замкнутые чёрные пути из SVG → list[Polygon]. Внешняя рамка (отсекается по аномальной площади)."""
    tree = etree.parse(fname)
    root = tree.getroot()
    raw = []
    for path in root.xpath("//svg:path", namespaces=NS):
        if path.get("stroke") != BLACK:
            continue
        d = path.get("d")
        if "Z" in d.upper() or "z" in d:
            coords = _path_points(d)
            if len(coords) >= 3:
                p = Polygon(coords)
                if p.is_valid and not p.is_empty and p.area > 0.001:
                    raw.append(p)
    if not raw:
        return []
    med = sorted(p.area for p in raw)[len(raw) // 2]
    return [p for p in raw if p.area < 30 * med + 1e-6]


def _path_points(d):
    import re

    tokens = re.findall(r"[MLZ]|[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", d)
    turn = None
    xs, ys = [], []
    cur = None
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t in "MLZ":
            turn = t
            i += 1
            continue
        x, y = float(t), float(tokens[i + 1])
        if turn == "M":
            cur = (x, y)
            xs, ys = [x], [y]
        elif turn == "L":
            xs.append(x)
            ys.append(y)
        i += 2
    if len(xs) >= 3:
        return list(zip(xs, ys))
    return []


def parse_svg_all(fname):
    tree = etree.parse(fname)
    root = tree.getroot()
    black = blue = 0
    widths = set()
    for path in root.xpath("//svg:path", namespaces=NS):
        w = path.get("stroke-width")
        if w:
            widths.add(w)
        if path.get("stroke") == BLACK:
            black += 1
        elif path.get("stroke") == BLUE:
            blue += 1
    return black, blue, widths


def min_dist(a, b):
    da = a.exterior
    db = b.exterior
    return a.distance(b)


def piece_sizes(polys):
    return [max(bounds_width(p), bounds_height(p)) for p in polys]


def bounds_width(p):
    x0, y0, x1, y1 = p.bounds
    return x1 - x0


def bounds_height(p):
    x0, y0, x1, y1 = p.bounds
    return y1 - y0


def check(ok, msg):
    print(("  PASS  " if ok else "  FAIL  ") + msg)
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-s",
        "--scheme",
        default=os.path.join(
            os.path.dirname(__file__), "output", "Танцы в облаках_310 x 430_450 дет.svg"
        ),
    )
    ap.add_argument("-e", "--reference", default=None)
    ap.add_argument("--strict", action="store_true", help="любой FAIL → exit 1")
    args = ap.parse_args()

    print(f"Схема: {args.scheme}")
    if not os.path.exists(args.scheme):
        print("Файл не найден")
        sys.exit(1)

    polys = parse_svg_polys(args.scheme)
    black, blue, widths = parse_svg_all(args.scheme)

    results = []
    results.append(
        check(
            abs(len(polys) - TARGET_COUNT) <= 25,
            f"количество деталей: {len(polys)} (цель ~{TARGET_COUNT})",
        )
    )

    sizes = piece_sizes(polys)
    over = sum(1 for s in sizes if s > MAX_PIECE_SIZE)
    results.append(
        check(
            over == 0, f"размер ≤{MAX_PIECE_SIZE} мм: max={max(sizes):.1f}, деталей >30 мм: {over}"
        )
    )

    # зазоры: ищем пары ближайших полигонов
    dists = []
    X = [(p.bounds, p) for p in polys]
    for i in range(len(X)):
        bx0, by0, bx1, by1 = X[i][0]
        for j in range(i + 1, len(X)):
            cx0, cy0, cx1, cy1 = X[j][0]
            if bx0 - 12 <= cx1 and bx1 + 12 >= cx0 and by0 - 12 <= cy1 and by1 + 12 >= cy0:
                d = min_dist(X[i][1], X[j][1])
                if d < 12:
                    dists.append(d)
    gap_ok = len(dists) == 0 or min(dists) >= MIN_GAP - 0.05
    results.append(
        check(
            gap_ok,
            f"мин. зазор: {min(dists) if dists else 'нет близких пар':.2f} мм (треб. ≥{MIN_GAP})",
        )
    )

    results.append(
        check(black >= len(polys), f"чёрных контуров: {black} (детали {len(polys)} + рамка)")
    )

    widths_ok = all(abs(float(w) - 0.2) < 1e-6 for w in widths)
    results.append(check(widths_ok, f"толщина линий: {sorted(widths)} (треб. 0.2 pt)"))

    if args.reference:
        ref = args.reference
        print(f"\nЭталон: {ref}")
        try:
            rblack, rblue, rw = parse_svg_all(ref)
            print(f"  эталон: чёрных {rblack}, голубых {rblue}, ширин {sorted(rw)}")
            print(
                f"  сравнение: деталей {len(polys)} (эталон {rblack - 1}); голубых {blue} (эталон {rblue})"
            )
        except Exception as e:
            print(f"  эталон не распарсен: {e}")

    failed = sum(1 for ok in results if not ok)
    print(f"\nИтог: {len(results) - failed}/{len(results)} требований выполнено")
    if args.strict and failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
