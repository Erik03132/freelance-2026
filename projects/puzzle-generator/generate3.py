#!/usr/bin/env python3
"""
generate3.py — v3: organic grid (v1 sine-wave edges + deformed nodes)
                  + unified artwork layer clipped to tiles.

Grid: parametric sine waves on edges (amp 0.45-0.8mm → gap 3mm via buffer(-1.5))
      + jitter on node positions (±1.5mm → non-rectangular cells)
Artwork: full-field drawing clipped to cells (picture continues across seams)

Запуск:  ./venv/bin/python3 generate3.py --seed 7 -o output/v3_Танцы.svg
"""

import argparse
import math
import random

import numpy as np
from shapely.geometry import LineString, MultiLineString, Polygon
from shapely.ops import unary_union

W, H = 310.0, 430.0
NX, NY = 18, 25
BUFFER = 1.5
LINE_W = 0.2

BLACK = "rgb(0%, 0%, 0%)"
BLUE = "rgb(16.078186%, 67.059326%, 88.627625%)"

Z_GROUND = 0.30
Z_SUN = 0.56
Z_SKY = 1.00


def zone_of(fy):
    if fy >= Z_SUN:
        return "sky"
    if fy >= Z_GROUND:
        return "sun"
    if fy >= Z_GROUND - 0.05:
        return "forest"
    return "ground"


# --- GRID: parametric sine waves on edges (v1 approach) ---


def build_grid(rng):
    x_pos = np.zeros(NX + 1)
    y_pos = np.zeros(NY + 1)
    for i in range(1, NX):
        x_pos[i] = i * W / NX
    x_pos[NX] = W
    for j in range(1, NY):
        y_pos[j] = j * H / NY
    y_pos[NY] = H

    amp_x = [rng.uniform(0.45, 0.8) for _ in range(NX + 1)]
    amp_y = [rng.uniform(0.45, 0.8) for _ in range(NY + 1)]
    ph_x = [rng.uniform(0, 2 * math.pi) for _ in range(NX + 1)]
    ph_y = [rng.uniform(0, 2 * math.pi) for _ in range(NY + 1)]
    per_x = [rng.uniform(4.5, 6.0) for _ in range(NX + 1)]
    per_y = [rng.uniform(4.5, 6.0) for _ in range(NY + 1)]

    def vert_x(i, yv):
        return x_pos[i] + amp_x[i] * math.sin(2 * math.pi * yv / per_x[i] + ph_x[i])

    def horiz_y(j, xv):
        return y_pos[j] + amp_y[j] * math.sin(2 * math.pi * xv / per_y[j] + ph_y[j])

    polys = []
    for j in range(NY):
        for i in range(NX):
            x_l, x_r = x_pos[i], x_pos[i + 1]
            y_b, y_t = y_pos[j], y_pos[j + 1]
            edge_b = [(float(a), horiz_y(j, float(a))) for a in np.linspace(x_l, x_r, 14)]
            edge_t = [(float(a), horiz_y(j + 1, float(a))) for a in np.linspace(x_l, x_r, 14)]
            edge_l = [(vert_x(i, float(b)), float(b)) for b in np.linspace(y_b, y_t, 14)]
            edge_r = [(vert_x(i + 1, float(b)), float(b)) for b in np.linspace(y_b, y_t, 14)]
            ring = edge_b + edge_r[1:] + edge_t[::-1][1:] + edge_l[::-1][1:]
            g = Polygon(ring).buffer(-BUFFER, join_style="round")
            if g is None or g.is_empty:
                g = Polygon(ring)
            if not g.is_valid:
                g = g.buffer(0)
            if g.geom_type == "MultiPolygon":
                g = max(g.geoms, key=lambda p: p.area)
            if g.is_valid and g.area > 1:
                polys.append(g)
    return polys


# --- ARTWORK: unified drawing across entire field ---


def wline(pts):
    return LineString(pts)


def draw_artwork():
    """Единый сюжетный слой: узнаваемые фигуры людей, птиц, деревьев, облаков —
    как в эталоне. Каждая фигура = несколько кривых LineString (контур тела)."""
    lines = []
    rng = random.Random(11)

    # ═══ ЧЕЛОВЕК: танцующая фигура (силуэт) ═══

    def person(cx, cy, h, arm_up=False, skirt=True):
        """Нарисовать фигуру человека. cx,cy — центр ступней. h — рост."""
        l = []
        head_r = h * 0.12
        neck_y = cy - h * 0.72
        shoulder_y = cy - h * 0.65
        waist_y = cy - h * 0.45
        knee_y = cy - h * 0.2
        # голова — круг
        head = [
            (cx + head_r * math.cos(t), neck_y + head_r + head_r * math.sin(t))
            for t in np.linspace(0, 2 * math.pi, 20)
        ]
        l.append(wline(head))
        # шея + торс — кривая вниз
        torso = [(cx, neck_y), (cx - h * 0.02, shoulder_y), (cx + h * 0.01, waist_y)]
        l.append(wline(torso))
        # левая рука
        if arm_up:
            lhand = [
                (cx - h * 0.02, shoulder_y),
                (cx - h * 0.18, shoulder_y - h * 0.15),
                (cx - h * 0.25, shoulder_y - h * 0.3),
            ]
        else:
            lhand = [
                (cx - h * 0.02, shoulder_y),
                (cx - h * 0.2, shoulder_y + h * 0.05),
                (cx - h * 0.15, shoulder_y + h * 0.2),
            ]
        l.append(wline(lhand))
        # правая рука
        if arm_up:
            rhand = [
                (cx + h * 0.02, shoulder_y),
                (cx + h * 0.18, shoulder_y - h * 0.15),
                (cx + h * 0.25, shoulder_y - h * 0.3),
            ]
        else:
            rhand = [
                (cx + h * 0.02, shoulder_y),
                (cx + h * 0.2, shoulder_y + h * 0.05),
                (cx + h * 0.15, shoulder_y + h * 0.2),
            ]
        l.append(wline(rhand))
        if skirt:
            # юбка — широкая дуга
            skirt_pts = [
                (
                    cx + h * 0.25 * math.sin(t * math.pi),
                    waist_y + h * 0.45 * (1 - math.cos(t * math.pi)) / 2,
                )
                for t in np.linspace(0, 1, 20)
            ]
            l.append(wline(skirt_pts))
        else:
            # ноги — две кривые
            lleg = [(cx - h * 0.02, waist_y), (cx - h * 0.08, knee_y), (cx - h * 0.05, cy)]
            rleg = [(cx + h * 0.02, waist_y), (cx + h * 0.08, knee_y), (cx + h * 0.05, cy)]
            l.append(wline(lleg))
            l.append(wline(rleg))
        return l

    # ═══ ПТИЦА: силуэт с крыльями-дугами ═══

    def bird(cx, cy, span, facing_right=True):
        l = []
        d = 1 if facing_right else -1
        # тело — овал
        body = [
            (cx + d * span * 0.15 * math.cos(t), cy + span * 0.06 * math.sin(t))
            for t in np.linspace(0, 2 * math.pi, 16)
        ]
        l.append(wline(body))
        # левое крыло — дуга вверх
        lwing = [
            (cx, cy),
            (cx - d * span * 0.3, cy - span * 0.25),
            (cx - d * span * 0.5, cy - span * 0.15),
        ]
        l.append(wline(lwing))
        # правое крыло — дуга вверх
        rwing = [
            (cx, cy),
            (cx + d * span * 0.1, cy - span * 0.3),
            (cx + d * span * 0.35, cy - span * 0.2),
        ]
        l.append(wline(rwing))
        # хвост
        tail = [(cx - d * span * 0.15, cy), (cx - d * span * 0.3, cy + span * 0.08)]
        l.append(wline(tail))
        return l

    # ═══ ЕЛЬ: силуэт с кроной ═══

    def tree_silhouette(cx, base_y, h):
        l = []
        # ствол
        trunk_w = h * 0.06
        trunk = [
            (cx - trunk_w, base_y),
            (cx - trunk_w, base_y - h * 0.35),
            (cx + trunk_w, base_y - h * 0.35),
            (cx + trunk_w, base_y),
        ]
        l.append(wline(trunk))
        # крона — 3 яруса «ёлочки» с закруглениями
        for k in range(3):
            y_base = base_y - h * (0.3 + 0.25 * k)
            w = h * (0.35 - 0.08 * k)
            peak = base_y - h * (0.55 + 0.15 * k)
            # левый склон — кривая
            left = [
                (cx - w * (1 - t**0.6), y_base - (y_base - peak) * t) for t in np.linspace(0, 1, 14)
            ]
            # правый склон
            right = [
                (cx + w * (1 - t**0.6), y_base - (y_base - peak) * t) for t in np.linspace(0, 1, 14)
            ]
            l.append(wline(left + right[::-1]))
        return l

    # ═══ ОБЛАКО: серия «дыбов» ═══

    def cloud(cx, cy, w, h):
        l = []
        bumps = rng.randint(3, 5)
        pts = []
        x = cx - w / 2
        for k in range(bumps):
            bw = w / bumps
            bh = h * rng.uniform(0.6, 1.0)
            bump = [(x + t * bw, cy + bh * math.sin(math.pi * t)) for t in np.linspace(0, 1, 12)]
            pts.extend(bump)
            x += bw * 0.85
        if len(pts) >= 2:
            l.append(wline(pts))
        return l

    # ═══ РИСУЕМ ФИГУРЫ ═══

    # лес: ели вдоль линии леса
    y_forest = H * Z_GROUND
    for k in range(10):
        xc = W * (0.03 + 0.1 * k) + rng.uniform(-2, 2)
        hgt = rng.uniform(12, 20)
        lines.extend(tree_silhouette(xc, y_forest + rng.uniform(-1, 3), hgt))

    # горизонт леса
    forest_line = [
        (x, y_forest + 1.5 * math.sin(x * 0.07) + math.sin(x * 0.19))
        for x in np.linspace(0, W, 200)
    ]
    lines.append(wline(forest_line))

    # солнце: полукруг + коловрат-спираль
    sun_cx, sun_cy = W * 0.52, H * 0.44
    R_sun = 28.0
    # горизонт
    lines.append(wline([(sun_cx - 55, sun_cy), (sun_cx + 55, sun_cy)]))
    # полукруг
    dome = [
        (sun_cx + R_sun * math.cos(t), sun_cy - R_sun * math.sin(t))
        for t in np.linspace(0, math.pi, 50)
    ]
    lines.append(wline(dome))
    # лучи — изогнутые дуги
    for k in range(12):
        ang0 = k * math.pi / 12
        r_in, r_out = R_sun + 2, R_sun + rng.uniform(6, 14)
        pts = [
            (
                sun_cx + (r_in + t * (r_out - r_in)) * math.cos(ang0 + 0.2 * math.sin(t * 2)),
                sun_cy - (r_in + t * (r_out - r_in)) * math.sin(ang0 + 0.2 * math.sin(t * 2)),
            )
            for t in np.linspace(0, 1, 12)
        ]
        lines.append(wline(pts))
    # коловрат: спираль + лепестки
    rc = 7.5
    spiral = [
        (
            sun_cx + rc * t * math.cos(4 * math.pi * t + math.pi),
            sun_cy - rc * t * math.sin(4 * math.pi * t + math.pi),
        )
        for t in np.linspace(0.1, 1.0, 50)
    ]
    lines.append(wline(spiral))
    for k in range(8):
        a0 = math.pi + k * math.pi / 4
        arc = [
            (
                sun_cx + rc * 0.35 * math.cos(a0 + t * 1.3),
                sun_cy - rc * 0.35 * math.sin(a0 + t * 1.3),
            )
            for t in np.linspace(0, 1, 14)
        ]
        lines.append(wline(arc))

    # небо: облака
    for k in range(4):
        y0 = H * (0.62 + 0.09 * k)
        x0 = W * rng.uniform(0.05, 0.35)
        lines.extend(cloud(x0 + rng.uniform(0, 30), y0, rng.uniform(35, 70), rng.uniform(4, 7)))

    # птицы: силуэты с крыльями
    for _ in range(8):
        xp = rng.uniform(15, W - 15)
        yp = H * rng.uniform(0.62, 0.93)
        lines.extend(bird(xp, yp, rng.uniform(6, 12), facing_right=rng.random() > 0.5))

    # танцующие фигуры: 4-5 человек в небе
    dancers = [
        (0.22, 0.78, True, True),
        (0.35, 0.82, False, True),
        (0.50, 0.76, True, False),
        (0.65, 0.80, False, True),
        (0.78, 0.74, True, True),
    ]
    for fx, fy, arm_up, skirt in dancers:
        cx = W * fx
        cy = H * fy
        lines.extend(person(cx, cy, rng.uniform(14, 20), arm_up=arm_up, skirt=skirt))

    # звёзды: шестилучевые
    for _ in range(8):
        xs = rng.uniform(15, W - 15)
        ys = H * rng.uniform(0.58, 0.97)
        r1 = rng.uniform(2, 3.5)
        r2 = r1 * 0.45
        pts = []
        for k in range(12):
            ang = math.pi * k / 6
            r = r1 if k % 2 == 0 else r2
            pts.append((xs + r * math.cos(ang), ys + r * math.sin(ang)))
        pts.append(pts[0])
        lines.append(wline(pts))

    # земля: волны + орнамент + домики + лодка
    for wv in range(2):
        y0 = H * (0.08 + 0.06 * wv)
        pts = [(x, y0 + 2.5 * math.sin(x * 0.06 + wv * 2)) for x in np.linspace(0, W, 200)]
        lines.append(wline(pts))

    y_m = H * 0.035
    x = 5.0
    step = 10.0
    while x < W - 5:
        pts = [
            (x, y_m),
            (x, y_m + 3.5),
            (x + step * 0.3, y_m + 3.5),
            (x + step * 0.3, y_m + 1),
            (x + step * 0.7, y_m + 1),
            (x + step * 0.7, y_m + 3.5),
            (x + step, y_m + 3.5),
            (x + step, y_m),
        ]
        lines.append(wline(pts))
        x += step

    for hx in [W * 0.10, W * 0.85]:
        base = H * 0.17
        lines.append(
            wline([(hx, base), (hx, base + 8), (hx + 10, base + 8), (hx + 10, base), (hx, base)])
        )
        roof = [
            (hx - 1 + t * 12, base + 8 + 5 * math.sin(math.pi * t)) for t in np.linspace(0, 1, 30)
        ]
        lines.append(wline(roof))
        lines.append(
            wline([(hx + 3, base), (hx + 3, base + 3.5), (hx + 6, base + 3.5), (hx + 6, base)])
        )
        win_cx, win_cy, win_r = hx + 7, base + 5, 1.5
        circle = [
            (win_cx + win_r * math.cos(t), win_cy + win_r * math.sin(t))
            for t in np.linspace(0, 2 * math.pi, 20)
        ]
        lines.append(wline(circle))

    ccx, ccb = W * 0.58, H * 0.15
    lines.append(wline([(ccx - 7, ccb), (ccx - 7, ccb + 10), (ccx + 7, ccb + 10), (ccx + 7, ccb)]))
    dome_ck = [
        (ccx - 6 + t * 12, ccb + 10 + 7 * math.sin(math.pi * t)) for t in np.linspace(0, 1, 30)
    ]
    lines.append(wline(dome_ck))
    lines.append(wline([(ccx, ccb + 17), (ccx, ccb + 20)]))
    lines.append(wline([(ccx - 1.5, ccb + 18.5), (ccx + 1.5, ccb + 18.5)]))

    lx, ly = W * 0.40, H * 0.11
    hull = [(lx + t * 14, ly + 2 * math.sin(math.pi * t) - t * 0.5) for t in np.linspace(0, 1, 30)]
    lines.append(wline(hull))
    lines.append(wline([(lx + 5, ly - 0.5), (lx + 5, ly - 8)]))
    sail = [
        (lx + 5 + 6 * math.sin(math.pi * t * 0.5), ly - 8 + 7.5 * t) for t in np.linspace(0, 1, 20)
    ]
    lines.append(wline(sail))

    return lines


def clip_to_tiles(lines, polys):
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


# --- SVG EXPORT ---


def path_d(poly):
    coords = list(poly.exterior.coords)
    d = f"M{coords[0][0]:.2f},{coords[0][1]:.2f}"
    for x, y in coords[1:]:
        d += f" L{x:.2f},{y:.2f}"
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("-o", "--out", default="output/v3_Танцы.svg")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    polys = build_grid(rng)
    lines = draw_artwork()
    blue = clip_to_tiles(lines, polys)
    export_svg(polys, [line_d(b) for b in blue], args.out)
    print(f"детали: {len(polys)}  голубых сегментов: {len(blue)}  → {args.out}")


if __name__ == "__main__":
    main()
