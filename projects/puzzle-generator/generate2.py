#!/usr/bin/env python3
"""
generate2.py — v2 художественное ядро пазла «Танцы в облаках» (18.08.2026).

Чем отличается от v1 (generate.py):
  v1: 451 замкнутая «вафля» (волнистая сетка) + примитив в каждой ячейке.
  v2: фигурные детали (эталон: сеть гладких Безье-швов, детали «кляксы»)
      + ЕДИНЫЙ сюжетный слой, проходящий СКВОЗЬ швы (потом клипается по деталям).

Приёмы:
  1. Криволинейная сетка: вершины (NX+1)×(NY+1) смещаются плавным полем деформации,
     у которого амплитуда/частота зависят от зоны (небо/солнце/лес/земля).
  2. Грань между соседними вершинами = кубическая Безье с контролами по нормали
     (радиус изгиба зависит от зоны) → детали овальные/фигурные, без прямых рёбер.
  3. buffer(-BUFFER) на каждую деталь → единый зазор 3 мм (как у требований ТЗ).
  4. Сюжетный слой рисуется на всё поле (лес, полусолнце-коловрат, танцоры, облака,
     птицы, орнамент) голубыми Безье-линиями, затем разрезается по швам (shapely
     intersection с union деталей) — рисунок «продолжается» от детали к детали.

Запуск:  ./venv/bin/python3 generate2.py --seed 7 -o output/v2_Танцы.svg
"""

import argparse
import math
import random

import numpy as np
from shapely.geometry import LineString, MultiLineString, Polygon
from shapely.ops import unary_union

W, H = 310.0, 430.0
NX, NY = 18, 25
BUFFER = 1.5  # мм на деталь → зазор 3 мм
LINE_W = 0.2  # pt

BLACK = "rgb(0%, 0%, 0%)"
BLUE = "rgb(16.078186%, 67.059326%, 88.627625%)"

# --- зоны по высоте (доли поля H) ---
Z_GROUND = 0.30  # земля
Z_SUN = 0.56  # полусолнце/линия леса
Z_SKY = 1.00  # небо

# --- криволинейная сетка (пластичная деформация по зонам) ---


def zone_of(fy):
    """fy — доля высоты (0..1 от низа). Возвращает зону: 'sky'|'sun'|'forest'|'ground'."""
    if fy >= Z_SUN:
        return "sky"
    if fy >= Z_GROUND:
        return "sun"
    if fy >= Z_GROUND - 0.05:
        return "forest"
    return "ground"


def aura(fy):
    """Амплитуда деформации по высоте (в мм)."""
    if fy >= Z_SUN:  # небо: крупные облачные волны
        return 2.6 + 2.2 * math.sin(fy * 9)
    if fy >= Z_GROUND:  # солнце: дуги
        return 1.8
    if fy >= Z_GROUND - 0.05:  # лес: ёлочный зигзаг
        return 1.4
    return 2.2 + 1.3 * math.sin(fy * 11)  # земля: орнамент


def freq(fy):
    if fy >= Z_SUN:
        return 2.0 + 0.8 * math.sin(fy * 7)
    if fy >= Z_GROUND:
        return 3.2
    if fy >= Z_GROUND - 0.05:
        return 6.5  # ёлки: частая волна
    return 3.8


def build_deformed_grid(rng):
    """Строит сетку точек (NX+1)x(NY+1) с плавной деформацией по зонам."""
    pts = []
    for j in range(NY + 1):
        fy = j / NY
        row = []
        for i in range(NX + 1):
            fx = i / NX
            ex = rng.uniform(-1, 1)  # мера локальной деформации
            ey = rng.uniform(-1, 1)
            x = (
                W * fx
                + aura(fy) * math.sin(math.pi * fx * freq(fy) + 0.6 * fy * 7 + ex)
                + 0.35 * math.sin(fx * 20 + ex * 3)
            )
            y = H * fy + 0.4 * math.sin(math.pi * fy * 1.4 + ey * 2.1)
            # фиксируем края жестко (поле)
            if fx < 0.03 or fx > 0.97:
                x = W * fx
            if fy < 0.02 or fy > 0.98:
                y = H * fy
            row.append((x, y))
        pts.append(row)
    return pts


def bezier4(p0, p1, n0, n1, amp=2.2, seed=0.0):
    """Кубическая Безье между p0 и p1; контролы отклоняются по нормали на amp (мм)."""
    import numpy as np

    p0 = np.array(p0, dtype=float)
    p1 = np.array(p1, dtype=float)
    d = p1 - p0
    L = np.hypot(*d)
    if L < 1e-9:
        return p0, p0, p1, p1
    n = np.array([-d[1], d[0]]) / L
    c0 = p0 + n * amp * n0
    c1 = p1 + n * amp * n1
    return tuple(p0), tuple(c0), tuple(c1), tuple(p1)


def sample_bezier(p0, c0, c1, p1, n=14):
    out = []
    for t in np.linspace(0, 1, n):
        a = 1 - t
        x = a**3 * p0[0] + 3 * a**2 * t * c0[0] + 3 * a * t**2 * c1[0] + t**3 * p1[0]
        y = a**3 * p0[1] + 3 * a**2 * t * c0[1] + 3 * a * t**2 * c1[1] + t**3 * p1[1]
        out.append((x, y))
    return out


def tile_polygon(pts, i, j, rng):
    """Деталь (i,j): замкнутое кольцо из 4 Безье-граней вокруг вершины (i,j)."""
    # ссылки на 4 угла ячейки
    p00 = pts[j][i]
    p10 = pts[j][i + 1]
    p11 = pts[j + 1][i + 1]
    p01 = pts[j + 1][i]
    fy = (j + 0.5) / NY
    z = zone_of(fy)
    amp = 2.4 if z == "sky" else (1.8 if z == "sun" else (1.3 if z == "forest" else 2.0))

    # нормали к сторонам
    def edge(a, b, pa, pb):
        a = np.array(a)
        b = np.array(b)
        d = b - a
        L = np.hypot(*d) or 1
        n = np.array([-d[1] / L, d[0] / L])
        return bezier4(a, b, n * pa, n * pb, amp=amp * (1 + 0.35 * rng.random()))

    # 4 грани: низ (i,i+1), право (до j+1), верх (от i+1 к i), лево (от j+1 к j)
    b = sample_bezier(*edge(p00, p10, -1, -1))
    r = sample_bezier(*edge(p10, p11, 1, 1))
    t = sample_bezier(*edge(p11, p01, 1, 1))
    l = sample_bezier(*edge(p01, p00, -1, -1))
    ring = b + r[1:] + t[1:] + l[1:]
    poly = Polygon(ring)
    return poly


def build_tiles(rng):
    """Детали из ОБЩИХ рёбер: каждая грань между двумя узлами сетки строится один раз
    и используется обеими соседними ячейками → соседние полигоны совпадают по грани,
    buffer(-BUFFER) даёт ровный зазор 3 мм."""
    pts = build_deformed_grid(rng)

    def edge_key(a, b):
        a = (round(a[0], 6), round(a[1], 6))
        b = (round(b[0], 6), round(b[1], 6))
        return tuple(sorted([a, b]))

    edges = {}

    def get_edge(a, b, fy_center):
        k = edge_key(a, b)
        if k in edges:
            return edges[k]
        aa = np.array(a, dtype=float)
        bb = np.array(b, dtype=float)
        d = bb - aa
        L = np.hypot(*d)
        n = np.array([-d[1] / L, d[0] / L])
        z = zone_of(fy_center)
        amp = 1.9 if z == "sky" else (1.45 if z == "sun" else (1.0 if z == "forest" else 1.6))
        amp *= 1 + 0.18 * rng.random()
        bz = bezier4(aa, bb, n, n, amp=amp)
        seg = sample_bezier(*bz)
        edges[k] = seg
        return seg

    polys = []
    channel_lines = []

    def edge_geom(a, b, fy_center):
        seg = get_edge(a, b, fy_center)
        return LineString(seg)

    for j in range(NY):
        for i in range(NX):
            fy_c = (j + 0.5) / NY
            p00 = pts[j][i]
            p10 = pts[j][i + 1]
            p11 = pts[j + 1][i + 1]
            p01 = pts[j + 1][i]
            channel_lines.append(LineString(get_edge(p00, p10, fy_c)))
            channel_lines.append(LineString(get_edge(p10, p11, fy_c)))
            channel_lines.append(LineString(get_edge(p11, p01, fy_c)))
            channel_lines.append(LineString(get_edge(p01, p00, fy_c)))
    channels = unary_union([ln.buffer(BUFFER) for ln in channel_lines])
    FIELD = Polygon([(0, 0), (W, 0), (W, H), (0, H)])

    for j in range(NY):
        for i in range(NX):
            p00 = pts[j][i]
            p10 = pts[j][i + 1]
            p11 = pts[j + 1][i + 1]
            p01 = pts[j + 1][i]
            fy_c = (j + 0.5) / NY
            bottom = get_edge(p00, p10, fy_c)
            right = get_edge(p10, p11, fy_c)
            top = get_edge(p11, p01, fy_c)
            left = get_edge(p01, p00, fy_c)
            ring = bottom + right[1:] + top[1:] + left[1:]
            poly = Polygon(ring)
            if not poly.is_valid or poly.area <= 1:
                poly = poly.buffer(0)
            if poly.is_valid and poly.area > 1:
                part = poly.difference(channels)
                if part.geom_type == "Polygon":
                    parts = [part]
                elif part.geom_type == "MultiPolygon":
                    parts = list(part.geoms)
                else:
                    parts = []
                for pp in parts:
                    pp = pp.intersection(FIELD)
                    if pp.is_valid and pp.area > 1:
                        polys.append(pp)
    return polys


# --- экспорт SVG ---


def path_d(poly, closed=True):
    coords = list(poly.exterior.coords)
    d = f"M{coords[0][0]:.2f},{coords[0][1]:.2f}"
    for x, y in coords[1:]:
        d += f" L{x:.2f},{y:.2f}"
    if closed:
        d += " Z"
    return d


def export_svg(polys, blue_paths, out):
    bb = f"0 0 {W:.2f} {H:.2f}"
    head = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.2f}mm" height="{H:.2f}mm" '
        f'viewBox="{bb}">\n'
        f'  <rect width="{W:.2f}" height="{H:.2f}" fill="none" stroke="{BLACK}" stroke-width="{LINE_W}"/>\n'
    )
    body = []
    for p in polys:
        body.append(
            f'  <path fill="none" stroke="{BLACK}" stroke-width="{LINE_W}" d="{path_d(p)}"/>'
        )
    for pd in blue_paths:
        body.append(f'  <path fill="none" stroke="{BLUE}" stroke-width="{LINE_W}" d="{pd}"/>')
    with open(out, "w") as f:
        f.write(head + "\n".join(body) + "\n</svg>\n")


# --- СЮЖЕТНЫЙ СЛОЙ (единый рисунок, потом клипается по деталям) ---


def wline(pts):
    """LineString из точек в мм."""
    return LineString(pts)


def draw_artwork():
    """Возвращает список LineString — единый сюжетный слой на всё поле (до клипа)."""
    lines = []
    rng = random.Random(11)

    # 1) ЛИНИЯ ЛЕСА: ёлочный зигзаг вдоль y≈0.296H
    yf = Z_GROUND - 0.004
    y = H * yf
    pts = []
    x = 0.0
    while x <= W:
        peak = y - rng.uniform(4.5, 8.5)
        pts += [
            (x, y),
            (x + rng.uniform(2, 5), peak + rng.uniform(-1, 1)),
            (x + rng.uniform(3, 7), y),
        ]
        x += rng.uniform(3, 7)
    lines.append(wline(pts))

    # 2-4) Ели вдоль леса (частичные, «грядка»)
    for k in range(5):
        xc = rng.uniform(15, W - 15)
        hgt = rng.uniform(9, 16)
        lines.append(wline([(xc, y + 0.5), (xc, y + 0.5 - hgt * 0.55)]))
        lines.append(wline([(xc - hgt * 0.35, y + 0.5 - hgt * 0.55), (xc, y + 0.5 - hgt * 0.05)]))
        lines.append(wline([(xc + hgt * 0.35, y + 0.5 - hgt * 0.55), (xc, y + 0.5 - hgt * 0.05)]))

    # 3) ПОЛУСОЛНЦЕ + коловрат
    cx, cy = W * 0.54, H * 0.43
    R = 30.0
    for ang in np.linspace(0, math.pi, 14):
        lines.append(wline([(cx, cy), (cx + R * math.cos(ang), cy + R * math.sin(ang))]))
    # дуга солнца
    arc = [(cx + R * math.cos(t), cy + R * math.sin(t)) for t in np.linspace(0, math.pi, 40)]
    lines.append(wline(arc))
    # коловрат: спираль-дуги
    rc = 7.0
    for a in range(8):
        a0 = math.pi + a * math.pi / 4
        arc = [
            (cx + rc * math.cos(a0 + t * 0.9), cy + rc * math.sin(a0 + t * 0.9))
            for t in np.linspace(0, 1.1, 16)
        ]
        lines.append(wline(arc))

    # 4) НЕБО: облачные волны + птицы + танцоры
    for wv in range(3):
        y0 = H * (0.60 + 0.10 * wv)
        pts = []
        x = 0.0
        while x <= W:
            pts.append((x, y0 + 4 * math.sin(x * 0.045 + wv)))
            x += 1.0
        lines.append(wline(pts))

    # птицы (запятые)
    for _ in range(7):
        xp = rng.uniform(20, W - 20)
        yp = H * rng.uniform(0.62, 0.90)
        s = rng.uniform(2, 4)
        lines.append(wline([(xp, yp), (xp + s, yp - s * 0.5), (xp + 2 * s, yp)]))

    # танцующие фигуры (пара силуэтов в ряд, в стиле ТЗ)
    dancers_y = H * 0.74
    for fx in [0.30, 0.44, 0.60]:
        cx = W * fx
        r = 3.4
        lines.append(
            wline([(cx - r, dancers_y - r * 0.8), (cx + r, dancers_y - r * 0.8)])
        )  # руки-лента верх
        lines.append(wline([(cx, dancers_y - 2.2 * r), (cx, dancers_y + 0.3 * r)]))  # ось тела
        lines.append(wline([(cx - r, dancers_y), (cx + r, dancers_y)]))  # юбка-лента
        lines.append(
            wline(
                [
                    (cx, dancers_y - 2.2 * r),
                    (cx - r, dancers_y - 1.1 * r),
                    (cx + r, dancers_y - 1.1 * r),
                ]
            )
        )  # голова-плечи

    # звёзды-снежинки
    for _ in range(12):
        xs = rng.uniform(15, W - 15)
        ys = H * rng.uniform(0.55, 0.97)
        rr = rng.uniform(1.5, 3.0)
        for a in range(6):
            ang = math.pi * a / 3
            lines.append(wline([(xs, ys), (xs + rr * math.cos(ang), ys + rr * math.sin(ang))]))

    # 5) ЗЕМЛЯ: волны + орнамент + домики + лодка
    for wv in range(2):
        y0 = H * (0.08 + 0.07 * wv)
        pts = []
        x = 0.0
        while x <= W:
            pts.append((x, y0 + 3 * math.sin(x * 0.07 + wv * 2)))
            x += 1.0
        lines.append(wline(pts))

    # орнамент-меандр (полоса внизу)
    y_m = H * 0.04
    x = 0.0
    step = 8.0
    while x < W:
        lines.append(
            wline(
                [
                    (x, y_m),
                    (x, y_m + 3),
                    (x + step * 0.6, y_m + 3),
                    (x + step * 0.6, y_m),
                    (x + step, y_m),
                    (x + step, y_m + 3),
                ]
            )
        )
        x += step

    # домики с церковью
    for hx in [W * 0.12, W * 0.82]:
        base = H * 0.18
        lines.append(wline([(hx, base), (hx, base + 8), (hx + 10, base + 8), (hx + 10, base)]))
        lines.append(wline([(hx - 1, base + 8), (hx + 5, base + 14), (hx + 11, base + 8)]))
        lines.append(wline([(hx + 4, base), (hx + 4, base + 3)]))
    # церковь
    ccx, ccb = W * 0.62, H * 0.17
    lines.append(wline([(ccx - 7, ccb), (ccx - 7, ccb + 10), (ccx + 7, ccb + 10), (ccx + 7, ccb)]))
    lines.append(wline([(ccx - 6, ccb + 10), (ccx, ccb + 16), (ccx + 6, ccb + 10)]))
    lines.append(wline([(ccx, ccb), (ccx, ccb + 2)]))

    # лодка
    lx, ly = W * 0.44, H * 0.12
    lines.append(wline([(lx, ly), (lx + 12, ly), (lx + 10, ly + 3), (lx + 2, ly + 3), (lx, ly)]))
    lines.append(wline([(lx + 2, ly), (lx + 4, ly - 4)]))
    lines.append(wline([(lx + 4, ly - 4), (lx + 6, ly - 1.5)]))

    return lines


def clip_to_tiles(lines, polys):
    """Резка рисунка по деталям: голубой не должен пересекать чёрный шов."""
    union = unary_union(polys)
    out = []
    for ln in lines:
        inter = ln.intersection(union)
        if inter.is_empty:
            continue
        if isinstance(inter, LineString):
            segs = [inter]
        elif isinstance(inter, MultiLineString):
            segs = list(inter.geoms)
        else:
            segs = [inter]
        for s in segs:
            if s.geom_type == "LineString" and len(s.coords) >= 2:
                out.append(s)
    return out


def line_d(ln):
    coords = list(ln.coords)
    d = f"M{coords[0][0]:.2f},{coords[0][1]:.2f}"
    for x, y in coords[1:]:
        d += f" L{x:.2f},{y:.2f}"
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("-o", "--out", default="output/v2_Танцы.svg")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    polys = build_tiles(rng)
    lines = draw_artwork()
    blue = clip_to_tiles(lines, polys)
    export_svg(polys, [line_d(b) for b in blue], args.out)
    print(f"детали: {len(polys)}  голубых сегментов: {len(blue)}  → {args.out}")


if __name__ == "__main__":
    main()
