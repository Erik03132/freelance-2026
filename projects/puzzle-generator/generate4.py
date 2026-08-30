#!/usr/bin/env python3
"""Генератор схемы пазла «Танцы в облаках» — v4: ФИГУРНЫЕ ДЕТАЛИ.

Концепция (по эталону .ai): пазл собирается из ~78 крупных органических
фигур-деталей (люди, птицы, деревья, облака, солнце, дома), каждая фигура —
замкнутый контур ≤30 мм. Внутри каждой детали — гравировка (голубые линии).

- Чёрные замкнутые контуры = рез (детали + рамка)
- Голубые линии = прорисовка/гравировка
- Поле: 310×430 мм, толщина линий 0.2 pt
"""

import argparse
import math
import os
import random

import numpy as np
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union
from shapely import affinity

W, H = 310.0, 430.0
LINE_W = 0.2
BLACK = "#000000"
BLUE = "#29abe2"

FRAME_M = 8.0  # отступ рамки от края листа


# ─────────────────────────── ФИГУРЫ ───────────────────────────


def _ring(pts):
    """Замкнуть полилинию."""
    return pts + [pts[0]]


def dancer(cx, cy, s, arm_up=True, skirt=True, lean=0.0):
    """Танцующая фигура: голова, торс, руки, юбка/ноги. Замкнутый контур."""
    pts = []
    head_r = 1.8 * s
    # голова — круг
    for t in np.linspace(0, 2 * math.pi, 22):
        pts.append((cx + head_r * math.cos(t), cy + 4.5 * s + head_r * math.sin(t)))
    # шея вниз к плечам
    pts.append((cx - head_r * 0.6, cy + 3.1 * s))
    # левое плечо → рука вверх
    if arm_up:
        pts.append((cx - 2.6 * s, cy + 3.3 * s))
        pts.append((cx - 3.2 * s, cy + 4.6 * s))
        pts.append((cx - 1.9 * s, cy + 5.6 * s))
    else:
        pts.append((cx - 2.7 * s, cy + 2.9 * s))
        pts.append((cx - 3.4 * s, cy + 1.8 * s))
        pts.append((cx - 2.6 * s, cy + 0.8 * s))
    # левый бок → талия
    pts.append((cx - 1.7 * s, cy + 2.0 * s))
    pts.append((cx - 1.5 * s, cy + 0.9 * s))
    if skirt:
        # юбка — широкая вниз
        for t in np.linspace(0, 1, 20):
            ang = math.pi * t
            pts.append(
                (
                    cx + math.cos(lean) * (-2.9 * s + 2.9 * s * math.cos(ang)),
                    cy - 0.9 * s + 3.1 * s * math.sin(ang),
                )
            )
    else:
        pts.append((cx - 1.2 * s, cy + 0.5 * s))
        pts.append((cx - 0.9 * s, cy))
        pts.append((cx - 0.4 * s, cy + 0.4 * s))
        pts.append((cx, cy + 0.2 * s))
    # правая сторона вверх
    if skirt:
        pts.append((cx + 1.5 * s, cy + 0.9 * s))
        pts.append((cx + 1.7 * s, cy + 2.0 * s))
    else:
        pts.append((cx + 0.4 * s, cy + 0.4 * s))
        pts.append((cx + 0.9 * s, cy))
        pts.append((cx + 1.2 * s, cy + 0.5 * s))
        pts.append((cx + 1.5 * s, cy + 0.9 * s))
        pts.append((cx + 1.7 * s, cy + 2.0 * s))
    # правое плечо → рука
    if arm_up:
        pts.append((cx + 2.6 * s, cy + 3.3 * s))
        pts.append((cx + 3.2 * s, cy + 4.6 * s))
        pts.append((cx + 1.9 * s, cy + 5.6 * s))
    else:
        pts.append((cx + 2.7 * s, cy + 2.9 * s))
        pts.append((cx + 3.4 * s, cy + 1.8 * s))
        pts.append((cx + 2.6 * s, cy + 0.8 * s))
    pts.append((cx + head_r * 0.6, cy + 3.1 * s))
    return Polygon(_ring(pts))


def bird(cx, cy, s, facing_right=True):
    """Птица: тело, крылья, хвост, голова. Замкнутый контур."""
    d = 1 if facing_right else -1
    pts = []
    # тело — овал (голова слева, хвост справа)
    for t in np.linspace(0, 2 * math.pi, 26):
        pts.append((cx + d * 3.2 * s * math.cos(t), cy + 2.0 * s * math.sin(t)))
    # клюв
    pts.append((cx + d * 3.4 * s, cy + 0.4 * s))
    pts.append((cx + d * 4.4 * s, cy + 0.9 * s))
    pts.append((cx + d * 3.4 * s, cy + 0.9 * s))
    # хвост — веер
    pts.append((cx - d * 3.4 * s, cy + 0.3 * s))
    pts.append((cx - d * 5.2 * s, cy - 0.8 * s))
    pts.append((cx - d * 4.6 * s, cy + 0.8 * s))
    pts.append((cx - d * 5.6 * s, cy + 1.1 * s))
    pts.append((cx - d * 4.2 * s, cy + 1.3 * s))
    return Polygon(_ring(pts))


def fir(cx, base_y, s):
    """Ель: ствол + 3 яруса кроны. Замкнутый контур."""
    pts = []
    tw = 0.5 * s
    top_y = base_y - 12 * s
    # левый контур снизу вверх
    pts.append((cx - tw, base_y))
    for t in np.linspace(0, 1, 12):
        y = base_y - 12 * s * t
        w = (4.2 - 2.6 * t) * s * (0.6 + 0.4 * math.sin(math.pi * t))
        pts.append((cx - w, y))
    # макушка
    pts.append((cx, top_y))
    # правый контур сверху вниз
    for t in np.linspace(1, 0, 12):
        y = base_y - 12 * s * t
        w = (4.2 - 2.6 * t) * s * (0.6 + 0.4 * math.sin(math.pi * t))
        pts.append((cx + w, y))
    pts.append((cx + tw, base_y))
    return Polygon(_ring(pts))


def cloud(cx, cy, w, h, rng):
    """Облако: серия перекрывающихся кругов, объединённых в один контур."""
    bumps = rng.randint(4, 6)
    circles = []
    x = cx - w / 2
    for k in range(bumps):
        r = h * rng.uniform(0.8, 1.2) / 2
        circles.append(
            Polygon(
                [
                    (x + r * math.cos(t), cy + r * math.sin(t))
                    for t in np.linspace(0, 2 * math.pi, 20)
                ]
            )
        )
        x += w / bumps * rng.uniform(0.9, 1.1)
    merged = unary_union(circles)
    if merged.geom_type == "Polygon":
        out = merged
    else:
        out = max(merged.geoms, key=lambda p: p.area)
    # кламп по ширине/высоте (гарантия ≤28 мм по ширине)
    minx, miny, maxx, maxy = out.bounds
    cur_w, cur_h = maxx - minx, maxy - miny
    f = min(1.0, 28.0 / cur_w, 14.0 / cur_h)
    if f < 1.0:
        out = affinity.scale(out, xfact=f, yfact=f, origin=(cx, cy))
    return out


def sun_ray(cx, cy, r0, r1, ang):
    """Луч солнца — вытянутый треугольник."""
    w = 0.08 * r1
    pts = [
        (cx + r0 * math.cos(ang - w), cy + r0 * math.sin(ang - w)),
        (cx + r1 * math.cos(ang), cy + r1 * math.sin(ang)),
        (cx + r0 * math.cos(ang + w), cy + r0 * math.sin(ang + w)),
    ]
    return Polygon(pts)


def sun(cx, cy, r, rays=10):
    """Солнце: круг + лучи."""
    circle = Polygon(
        [(cx + r * math.cos(t), cy + r * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 32)]
    )
    parts = [circle]
    for k in range(rays):
        ang = k * 2 * math.pi / rays
        parts.append(sun_ray(cx, cy, r + 1.0, r + 4.0, ang))
    merged = unary_union(parts)
    if merged.geom_type == "Polygon":
        return merged
    return max(merged.geoms, key=lambda p: p.area)


def house(cx, base_y, s):
    """Дом: стены + двускатная крыша + труба."""
    pts = []
    hw = 5.0 * s
    wh = 6.0 * s
    roof_h = 3.5 * s
    # основание
    pts.append((cx - hw, base_y))
    pts.append((cx - hw, base_y + wh))
    # крыша — конёк
    pts.append((cx - hw - 0.5 * s, base_y + wh))
    pts.append((cx, base_y + wh + roof_h))
    pts.append((cx + hw + 0.5 * s, base_y + wh))
    pts.append((cx + hw, base_y + wh))
    pts.append((cx + hw, base_y))
    return Polygon(_ring(pts))


def church(cx, base_y, s):
    """Церковь: тело + купол-луковка + крест."""
    pts = []
    bw = 3.2 * s
    bh = 7.0 * s
    # тело
    pts.append((cx - bw, base_y))
    pts.append((cx - bw, base_y + bh))
    # купол — полукруг
    for t in np.linspace(0, 1, 18):
        ang = math.pi * t
        pts.append(
            (
                cx - bw + 2 * bw * math.sin(ang),
                base_y
                + bh
                + 2.6 * s * math.sin(ang) * 0
                + (2.6 * s) * math.sin(math.pi * 0.5) * math.sin(ang),
            )
        )
    # крест
    pts.append((cx - bw, base_y + bh + 2.8 * s))
    pts.append((cx - bw - 0.6 * s, base_y + bh + 2.8 * s))
    pts.append((cx - bw - 0.6 * s, base_y + bh + 3.6 * s))
    pts.append((cx - bw, base_y + bh + 3.6 * s))
    pts.append((cx - bw, base_y + bh + 4.4 * s))
    pts.append((cx + bw, base_y + bh + 4.4 * s))
    pts.append((cx + bw, base_y + bh + 3.6 * s))
    pts.append((cx + bw + 0.6 * s, base_y + bh + 3.6 * s))
    pts.append((cx + bw + 0.6 * s, base_y + bh + 2.8 * s))
    pts.append((cx + bw, base_y + bh + 2.8 * s))
    pts.append((cx + bw, base_y + bh))
    pts.append((cx + bw, base_y))
    return Polygon(_ring(pts))


def star(cx, cy, r, points=6):
    """Звезда."""
    pts = []
    for k in range(points * 2):
        ang = math.pi * k / points - math.pi / 2
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    return Polygon(_ring(pts))


def flower(cx, cy, r, petals=6, rng=None):
    """Цветок: лепестки + центр. r — полный радиус цветка."""
    parts = []
    rr = r * 0.5  # длина лепестка
    for k in range(petals):
        ang = k * 2 * math.pi / petals
        px, py = cx + rr * math.cos(ang), cy + rr * math.sin(ang)
        base = ang - math.pi / 2
        w = r * 0.28
        petal = Polygon(
            [
                (px + w * math.cos(base + t), py + w * math.sin(base + t))
                for t in np.linspace(0, math.pi, 12)
            ]
        )
        parts.append(petal)
        parts.append(affinity.rotate(petal, 180, origin=(px, py)))
    center = Circle = Polygon(
        [
            (cx + r * 0.35 * math.cos(t), cy + r * 0.35 * math.sin(t))
            for t in np.linspace(0, 2 * math.pi, 16)
        ]
    )
    parts.append(center)
    merged = unary_union(parts)
    if merged.is_empty:
        return center
    if merged.geom_type == "Polygon":
        return merged
    return max(merged.geoms, key=lambda p: p.area)


# ─────────────────────────── КОМПОЗИЦИЯ ───────────────────────────


def build_scene(rng):
    """Разместить ~78 фигур по зонам сцены с зазором ≥3 мм. Возвращает list[Polygon]."""
    figures = []
    placed = []

    def try_place(poly, tries=25):
        """Проверить пересечения/зазор ≥3 мм с уже размещёнными. Вернуть смещённый полигон или None."""
        for shift in range(tries):
            dx = rng.uniform(-6, 6)
            dy = rng.uniform(-6, 6)
            cand = affinity.translate(poly, dx, dy)
            if all(cand.distance(q) >= 3.0 for q in placed):
                return cand
        return None

    def add(poly):
        placed_p = try_place(poly)
        if placed_p is not None:
            placed.append(placed_p)
            figures.append(placed_p)

    r = rng

    # ── Земля (низ): ели, дома, церковь, люди, цветы ──
    y_ground = H * 0.28

    for k in range(20):
        xc = W * (0.02 + 0.05 * k) + r.uniform(-2, 2)
        s = r.uniform(2.2, 2.5)
        add(fir(xc, y_ground + r.uniform(-4, 4), s))

    for xf in (0.12, 0.30, 0.66, 0.90, 0.05):
        add(house(W * xf + r.uniform(-3, 3), y_ground + r.uniform(-3, 3), r.uniform(2.5, 2.7)))

    for xf in (0.46, 0.78, 0.20):
        add(church(W * xf + r.uniform(-3, 3), y_ground + r.uniform(-2, 2), r.uniform(2.3, 2.5)))

    for k in range(8):
        xc = W * (0.06 + 0.13 * k) + r.uniform(-2, 2)
        add(
            dancer(
                xc,
                H * 0.12 + r.uniform(-2, 4),
                r.uniform(3.0, 3.3),
                arm_up=r.random() > 0.5,
                skirt=r.random() > 0.35,
            )
        )

    # цветы на земле
    for _ in range(12):
        xc = r.uniform(15, W - 15)
        yc = r.uniform(8, H * 0.24)
        add(flower(xc, yc, r.uniform(8, 12), petals=rng.randint(5, 8)))

    # ── Солнце (середина) ──
    add(sun(W * 0.50, H * 0.48, 10.5, rays=10))

    # ── Небо (верх): облака, птицы, звёзды, танцоры ──
    for k in range(10):
        xc = W * (0.06 + 0.11 * k) + r.uniform(-3, 3)
        yc = H * (0.58 + 0.05 * r.uniform(-1, 1))
        add(cloud(xc, yc, r.uniform(20, 25), r.uniform(8, 11), r))

    for k in range(18):
        xc = W * (0.02 + 0.055 * k) + r.uniform(-3, 3)
        yc = H * (0.66 + 0.06 * (k % 4)) + r.uniform(0, 5)
        add(bird(xc, yc, r.uniform(2.6, 2.9), facing_right=r.random() > 0.5))

    # танцоры в небе
    for k in range(14):
        xc = W * (0.04 + 0.07 * k) + r.uniform(-3, 3)
        yc = H * (0.76 + 0.05 * (k % 3)) + r.uniform(-2, 3)
        add(
            dancer(
                xc,
                yc,
                r.uniform(2.9, 3.2),
                arm_up=r.random() > 0.5,
                skirt=r.random() > 0.4,
                lean=r.uniform(-0.4, 0.4),
            )
        )

    # звёзды
    for _ in range(8):
        xc = r.uniform(12, W - 12)
        yc = H * r.uniform(0.84, 0.97)
        add(star(xc, yc, r.uniform(4.0, 6.0)))

    return figures


def clip_to_field(figs):
    """Обрезать фигуры по внутренней области рамки (FRAME_M от края листа)."""
    m = FRAME_M
    field = Polygon([(m, m), (W - m, m), (W - m, H - m), (m, H - m)])
    out = []
    for f in figs:
        if not f.is_valid:
            f = f.buffer(0)
        if f.is_empty or not f.is_valid:
            continue
        g = f.intersection(field)
        if g.geom_type == "Polygon" and g.area > 2:
            out.append(g)
        elif g.geom_type == "MultiPolygon":
            out.extend([p for p in g.geoms if p.area > 2])
    return out


# ─────────────────────────── ГРАВИРОВКА ───────────────────────────


def engrave(fig):
    """Внутренние голубые линии для детали."""
    lines = []
    cx, cy = fig.centroid.x, fig.centroid.y
    minx, miny, maxx, maxy = fig.bounds
    w, h = maxx - minx, maxy - miny
    # пара внутренних контуров — повтор контура детали внутрь
    inner = fig.buffer(-1.2)
    if inner.is_valid and not inner.is_empty:
        if inner.geom_type == "Polygon":
            lines.append(LineString(inner.exterior.coords))
        elif inner.geom_type == "MultiPolygon":
            for p in inner.geoms:
                lines.append(LineString(p.exterior.coords))
    # крестовая штриховка
    if w > 8 and h > 8:
        for t in [0.3, 0.5, 0.7]:
            lines.append(LineString([(minx + w * t, miny + 1.5), (minx + w * t, maxy - 1.5)]))
            lines.append(LineString([(minx + 1.5, miny + h * t), (maxx - 1.5, miny + h * t)]))
    return lines


# ─────────────────────────── SVG ───────────────────────────


def svg_header():
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">'


def path_d(poly):
    coords = list(poly.exterior.coords)
    d = f"M {coords[0][0]:.3f} {coords[0][1]:.3f}"
    for x, y in coords[1:]:
        d += f" L {x:.3f} {y:.3f}"
    d += " Z"
    return d


def line_d(line):
    coords = list(line.coords)
    d = f"M {coords[0][0]:.3f} {coords[0][1]:.3f}"
    for x, y in coords[1:]:
        d += f" L {x:.3f} {y:.3f}"
    return d


def main():
    ap = argparse.ArgumentParser(
        description="Генератор пазла «Танцы в облаках» v4 — фигурные детали"
    )
    ap.add_argument(
        "-o", "--out", default=os.path.join(os.path.dirname(__file__), "output", "v4.svg")
    )
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    figs = build_scene(rng)
    figs = clip_to_field(figs)

    print(f"Фигур-деталей: {len(figs)}")

    # рамка
    frame = Polygon(
        [
            (FRAME_M, FRAME_M),
            (W - FRAME_M, FRAME_M),
            (W - FRAME_M, H - FRAME_M),
            (FRAME_M, H - FRAME_M),
        ]
    )

    lines = []
    cut_paths = 0
    for f in figs:
        d = path_d(f)
        lines.append(f'<path d="{d}" fill="none" stroke="{BLACK}" stroke-width="{LINE_W}"/>')
        cut_paths += 1
        # гравировка
        for eng in engrave(f):
            lines.append(
                f'<path d="{line_d(eng)}" fill="none" stroke="{BLUE}" stroke-width="{LINE_W}"/>'
            )

    # рамка — последний рез
    lines.append(
        f'<path d="{path_d(frame)}" fill="none" stroke="{BLACK}" stroke-width="{LINE_W}"/>'
    )
    cut_paths += 1

    svg = [svg_header()] + lines + ["</svg>"]
    with open(args.out, "w") as fh:
        fh.write("\n".join(svg))

    print(f"Голубых линий: {sum(1 for l in lines if BLUE in l)}")
    print(f"Чёрных контуров (рез): {cut_paths}")
    print(f"SVG записан: {args.out}")


if __name__ == "__main__":
    main()
