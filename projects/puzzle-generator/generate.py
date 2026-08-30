#!/usr/bin/env python3
"""
Генератор схемы лазерного реза «Танцы в облаках» — 450 деталей, 310x430 мм.

Схема строится как «пэчворк»: поле разбивается на сетку 18x25 (450 ячеек),
каждая ячейка — замкнутая деталь с волнистыми краями и гарантированным зазором 3 мм
(negative buffer 1.5 мм). Внутри деталей рисуются голубые прорисовки (гравировка) по
сюжетным зонам ТЗ: нижняя — земля/деревня, средняя — солнце с коловратом,
верхняя — небесный хоровод.

Выход: SVG 310x430 мм, чёрные контуры деталей 0.2 pt, голубые прорисовки 0.2 pt.

Запуск:  python3 generate.py [-o out.svg] [--seed N]
"""

import argparse
import os
import math
import hashlib
import numpy as np
from shapely.geometry import Polygon

# ---------- параметры ----------
W, H = 310.0, 430.0  # поле, мм
NX, NY = 18, 25  # сетка: 18x25 = 450 деталей
GAP = 3.0  # мин. расстояние между деталями, мм
LINE_PT = 0.2  # толщина линий, pt
FIELD_MARGIN = 0.0  # поле без рамки: детали занимают весь лист
BUFFER = GAP / 2.0  # отступ каждой детали, мм

BLACK = "rgb(0%, 0%, 0%)"
BLUE = "rgb(16.078186%, 67.059326%, 88.627625%)"
PT2MM = 0.352778

ZM = {"ground": 0.30, "sun": 0.56, "sky": 1.00}  # зоны по доле высоты


# ---------- вспомогательное ----------
def seed_rng(seed):
    return np.random.default_rng(seed)


def wavy_line_along_x(xs, y_base, amp, phase, period):
    """y = y_base + amp*sin(...) — волнистая горизонтальная грань."""
    y = y_base + amp * np.sin(2 * math.pi * xs / period + phase)
    return list(zip(xs, y))


def wavy_line_along_y(ys, x_base, amp, phase, period):
    x = x_base + amp * np.sin(2 * math.pi * ys / period + phase)
    return list(zip(x, ys))


def build_grid(rng):
    """Волнистая сетка. Возвращает vertices (x_i, y_j) и контуры ячеек."""
    # позиции линий с джиттером
    x_pos = np.zeros(NX + 1)
    y_pos = np.zeros(NY + 1)
    for i in range(1, NX):
        x_pos[i] = i * W / NX + rng.uniform(-0.8, 0.8)
    x_pos[NX] = W
    for j in range(1, NY):
        y_pos[j] = j * H / NY + rng.uniform(-0.8, 0.8)
    y_pos[NY] = H

    amp_x = rng.uniform(0.45, 0.8, NX + 1)
    amp_y = rng.uniform(0.45, 0.8, NY + 1)
    ph_x = rng.uniform(0, 2 * math.pi, NX + 1)
    ph_y = rng.uniform(0, 2 * math.pi, NY + 1)
    per_x = rng.uniform(4.5, 6.0, NX + 1)
    per_y = rng.uniform(4.5, 6.0, NY + 1)

    def vert_x(i, yv):
        return x_pos[i] + amp_x[i] * math.sin(2 * math.pi * yv / per_x[i] + ph_x[i])

    def horiz_y(j, xv):
        return y_pos[j] + amp_y[j] * math.sin(2 * math.pi * xv / per_y[j] + ph_y[j])

    cells = []
    for j in range(NY):
        for i in range(NX):
            x_l, x_r = x_pos[i], x_pos[i + 1]
            y_b, y_t = y_pos[j], y_pos[j + 1]
            # нижний край: x: l->r на уровне y_b
            xs = np.linspace(x_l, x_r, 14)
            edge_b = [(float(a), horiz_y(j, float(a))) for a in xs]
            # правый край: y: b->t на уровне x_r
            ys = np.linspace(y_b, y_t, 14)
            edge_r = [(vert_x(i + 1, float(a)), float(a)) for a in ys]
            # верхний край: x: r->l на уровне y_t
            xs2 = np.linspace(x_r, x_l, 14)
            edge_t = [(float(a), horiz_y(j + 1, float(a))) for a in xs2]
            # левый край: y: t->b на уровне x_l
            ys2 = np.linspace(y_t, y_b, 14)
            edge_l = [(vert_x(i, float(a)), float(a)) for a in ys2]
            ring = edge_b + edge_r + edge_t + edge_l
            g = Polygon(ring).buffer(-BUFFER, join_style="round")
            if g is not None and not g.is_empty and g.is_valid:
                geom = g
            else:
                g = g if g is not None else Polygon(ring)
                g = g.buffer(0) if not g.is_valid else g
                if g.geom_type == "MultiPolygon":
                    g = max(g.geoms, key=lambda p: p.area)
                geom = g
            cells.append(
                {
                    "i": i,
                    "j": j,
                    "ring": ring,
                    "geom": geom,
                }
            )
    return cells


def scale_prims(prims, cx, cy, s):
    """prims: list of list-of-points (локальные ~-1..1) → абсолютные мм."""
    out = []
    for line in prims:
        out.append([(cx + p[0] * s, cy + p[1] * s) for p in line])
    return out


# ---------- примитивы прорисовки (локальные координаты, x и y ~ -1..1) ----------


def _arc_seg(cx, cy, r, a0, a1, step=0.18):
    pts = []
    a = a0
    while a <= a1 + 1e-6:
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        a += step
    return pts


def prim_spiral():
    # спираль-завиток (3 витка)
    pts = []
    for t in np.linspace(0, 4.4 * math.pi, 60):
        r = 0.28 * (1 - t / (4.4 * math.pi)) * (1 + 0.2)
        pts.append((r * math.cos(t), r * math.sin(t)))
    return [pts]


def prim_wave():
    lines = []
    for k in range(3):
        x0 = -0.62 + k * 0.55
        pts = _arc_seg(x0, -0.15, 0.28, -0.35 * math.pi, 0.35 * math.pi)
        lines.append(pts)
    return lines


def prim_fir():
    lines = []
    top = (-0.62, 0.6)
    lines.append([top, (0.62, 0.6)])
    lines.append([(-0.5, 0.2), (-0.12, 0.2), (-0.02, 0.18), (0.02, 0.18), (0.12, 0.2), (0.5, 0.2)])
    lines.append([(-0.28, -0.2), (-0.05, -0.2), (0.0, -0.19), (0.05, -0.2), (0.28, -0.2)])
    lines.append([(-0.1, -0.55), (0.0, -0.53), (0.1, -0.55)])
    lines.append([(0.0, -0.55), (0.0, -0.8)])
    return lines


def prim_house():
    lines = []
    # стены
    lines.append([(-0.75, -0.55), (-0.75, 0.2), (0.72, 0.2), (0.72, -0.55)])
    lines.append([(-0.75, 0.2), (0.0, 0.72), (0.72, 0.2)])
    # труба + дым
    lines.append([(0.38, 0.55), (0.5, 0.55), (0.5, 0.22)])
    pts = _arc_seg(0.44, 0.78, 0.1, math.pi, 2 * math.pi) + _arc_seg(
        0.6, 0.82, 0.08, math.pi, 1.9 * math.pi
    )
    lines.append(pts)
    # наличник окна
    lines.append([(-0.6, -0.3), (-0.35, -0.3), (-0.35, -0.02), (-0.6, -0.02), (-0.6, -0.3)])
    lines.append([(-0.475, -0.3), (-0.475, -0.02), (-0.6, -0.16), (-0.35, -0.16)])
    # второе окно + конёк на крыше
    lines.append([(0.04, -0.46), (0.3, -0.46), (0.3, -0.18), (0.04, -0.18), (0.04, -0.46)])
    return lines


def prim_fir():
    lines = []
    lines.append([(-0.68, 0.68), (0.0, 0.36), (0.68, 0.68)])
    lines.append([(-0.44, 0.3), (0.0, 0.0), (0.44, 0.3)])
    lines.append([(-0.26, -0.08), (0.0, -0.34), (0.26, -0.08)])
    lines.append([(-0.1, -0.42), (0.0, -0.6), (0.1, -0.42)])
    lines.append([(0.0, -0.6), (0.0, -0.78)])
    return lines


def prim_dancer_f():
    lines = []
    # голова + кокошник
    lines.append(_arc_seg(0.0, 0.86, 0.1, 0, 2 * math.pi))
    lines.append(_arc_seg(0.0, 0.86, 0.17, 0.35 * math.pi, 0.65 * math.pi))
    lines.append([(-0.16, 0.75), (0.16, 0.75)])
    # коса с закруткой
    lines.append([(0.13, 0.72), (0.3, 0.2), (0.1, -0.05), (0.05, 0.0)])
    for t in np.linspace(0, 1, 24):
        a = 3.2 - 3.0 * t
        r = 0.07 * (1 - t) + 0.05 * t
        lines.append([(0.05 + r * math.cos(a), 0.0 + r * math.sin(a) * 0.7)])
    # сарафан (трапеция)
    lines.append([(-0.26, 0.62), (-0.34, -0.3), (0.34, -0.3), (0.28, 0.62), (-0.26, 0.62)])
    # вышивка: ромбики на груди
    lines.append([(-0.1, 0.42), (0.0, 0.5), (0.1, 0.42), (0.0, 0.34), (-0.1, 0.42)])
    lines.append([(-0.14, 0.22), (0.0, 0.32), (0.14, 0.22), (0.0, 0.12), (-0.14, 0.22)])
    # бусы — подборка петель
    for bx in (-0.12, 0.0, 0.12):
        lines.append(_arc_seg(bx, -0.02, 0.05, -0.6 * math.pi, 0.6 * math.pi))
    # подол раскрыт (две дуги + волна)
    lines.append(_arc_seg(-0.18, -0.45, 0.4, -0.5 * math.pi, 0.12 * math.pi))
    lines.append(_arc_seg(0.18, -0.45, 0.4, -0.12 * math.pi, 0.5 * math.pi))
    lines.append([(-0.4, -0.5), (0.4, -0.5)])
    # руки: поднятая + отведённая с «рукавом»
    lines.append([(0.24, 0.5), (0.58, 0.8), (0.55, 0.92)])
    lines.append([(-0.22, 0.5), (-0.5, 0.66), (-0.62, 0.5)])
    lines.append([(-0.5, 0.66), (-0.78, 0.7), (-0.88, 0.55)])  # летящий рукав-лента
    return lines


def prim_dancer_m():
    lines = []
    # голова + шапка-ушанка
    lines.append(_arc_seg(0.0, 0.86, 0.1, 0, 2 * math.pi))
    lines.append([(-0.14, 0.78), (-0.1, 0.95), (0.1, 0.95), (0.14, 0.78)])
    lines.append([(-0.14, 0.8), (-0.26, 0.9)])  # ухо-клапан
    lines.append([(0.14, 0.8), (0.26, 0.9)])
    # рубаха
    lines.append([(-0.26, 0.62), (-0.22, -0.26), (0.24, -0.22), (0.28, 0.62), (-0.26, 0.62)])
    lines.append([(-0.13, 0.2), (0.15, 0.2)])  # пояс
    # руки подняты
    lines.append([(0.24, 0.42), (0.58, 0.72), (0.55, 0.9)])
    lines.append([(-0.22, 0.42), (-0.56, 0.68), (-0.5, 0.86)])
    # порты (V) и сапоги с каблуком
    lines.append([(-0.16, -0.26), (-0.16, -0.5), (-0.34, -0.7)])
    lines.append([(-0.05, -0.5), (0.0, -0.72)])
    lines.append([(0.2, -0.24), (0.22, -0.5), (0.35, -0.7)])
    lines.append([(0.28, -0.6), (0.14, -0.62), (0.24, -0.72), (0.36, -0.7), (0.28, -0.6)])  # каблук
    return lines


def prim_cloud():
    lines = []
    # основание-гряда
    xs = np.linspace(-0.8, 0.8, 14)
    lines.append([(float(x), 0.22 + 0.1 * math.sin(2 * math.pi * x / 0.9)) for x in xs])
    # лепестки облака — арки
    lines.append(_arc_seg(-0.45, -0.05, 0.34, -0.55 * math.pi, 0.55 * math.pi))
    lines.append(_arc_seg(-0.1, 0.05, 0.38, -0.75 * math.pi, 0.6 * math.pi))
    lines.append(_arc_seg(0.32, -0.05, 0.34, -0.55 * math.pi, 0.45 * math.pi))
    # хвост-завиток
    pts = []
    for t in np.linspace(0, 1, 40):
        a = -0.6 + 3.4 * t
        r = 0.1 * (1 - t) + 0.06 * t
        pts.append((0.85 + r * math.cos(a), -0.28 + r * math.sin(a) * 0.7))
    lines.append(pts)
    return lines


def prim_kolovrat():
    lines = []
    # 4 спиральные лопасти
    for k in range(4):
        a0 = k * math.pi / 2 + 0.4
        pts = []
        for t in np.linspace(0, 1, 26):
            r = 0.42 * t
            a = a0 + 2.2 * t
            pts.append((r * math.cos(a), r * math.sin(a)))
        lines.append(pts)
    # срединный вихрь
    lines.append(_arc_seg(0.0, 0.0, 0.1, 0, 2 * math.pi))
    lines.append([(0.0, 0.0), (0.06, -0.14), (0.16, -0.05), (0.05, 0.18), (-0.08, 0.2)])
    return lines


def prim_rhombus():
    lines = [[(0.0, 0.7), (0.55, 0.0), (0.0, -0.7), (-0.55, 0.0), (0.0, 0.7)]]
    lines.append([(-0.62, 0.0), (0.62, 0.0)])
    lines.append([(0.0, -0.78), (0.0, 0.78)])
    lines.append(_arc_seg(0.0, 0.0, 0.28, 0, 2 * math.pi))
    return lines


def prim_fence():
    lines = [[(-0.8, -0.1), (0.8, -0.1)]]
    for k in range(5):
        x = -0.8 + k * 0.4
        lines.append([(x, -0.1), (x, 0.7)])
    return lines


def prim_snowflake():
    lines = []
    for k in range(6):
        a = k * math.pi / 3
        v = (math.cos(a), math.sin(a))
        p1 = (0.14 * v[0], 0.14 * v[1])
        p2 = (0.85 * v[0], 0.85 * v[1])
        lines.append([p1, p2])
        per = (-v[1], v[0])
        lines.append(
            [
                (0.4 * v[0] + 0.12 * per[0], 0.4 * v[1] + 0.12 * per[1]),
                (0.4 * v[0], 0.4 * v[1]),
                (0.4 * v[0] + 0.12 * per[0], 0.4 * v[1] + 0.12 * per[1]),
            ]
        )
    lines.append(_arc_seg(0.0, 0.0, 0.2, 0, 2 * math.pi))
    return lines


def prim_boat():
    lines = []
    lines.append(_arc_seg(0.0, -0.15, 0.55, 0.0, math.pi))
    lines.append([(-0.55, -0.15), (0.1, -0.3)])
    lines.append([(0.28, -0.22), (0.55, -0.15), (0.42, 0.05), (0.15, -0.05)])
    lines.append([(0.28, -0.22), (0.28, 0.05)])
    return lines


def prim_wriggle():
    pts = []
    for t in np.linspace(0, 1, 40):
        x = -0.8 + 1.6 * t
        y = 0.55 * math.sin(2.2 * math.pi * t)
        pts.append((x, y))
    return [pts]


# -- sun zone --
def prim_sun_half():
    lines = []
    lines.append(_arc_seg(0.0, 0.0, 0.72, -0.15 * math.pi, math.pi + 0.15 * math.pi))
    for k, a in enumerate(np.linspace(0.05 * math.pi, math.pi - 0.05 * math.pi, 7)):
        p = (0.72 * math.cos(a), 0.72 * math.sin(a))
        dr = (p[0] / (abs(p[0]) + 0.001), p[1] / (abs(p[1]) + 0.001) if abs(p[1]) > 0.01 else 1.0)
        scale = 0.95
        lines.append([p, (p[0] * scale + dr[0] * -0.0, p[1])])  # reserved
    return lines


def prim_sun_rays():
    lines = []
    lines.append(_arc_seg(0.0, 0.0, 0.7, 0, 2 * math.pi))
    for k in range(8):
        a = k * math.pi / 4
        v = (math.cos(a), math.sin(a))
        lines.append([(0.72 * v[0], 0.72 * v[1]), (1.0 * v[0], 1.0 * v[1])])
    return lines


def prim_kolovrat():
    lines = []
    # коловрат: 4 изогнутые «лопасти»-дуги вокруг центра
    for k in range(4):
        a0 = k * math.pi / 2
        r = 0.35
        a = np.linspace(a0 + 0.3, a0 + math.pi / 2 + 0.3, 24)
        pts = [
            (
                r * math.cos(aa) * (1 - 0.18 * ((aa - a0 - 0.3) / (math.pi / 2))),
                r * math.sin(aa) * (1 - 0.18 * ((aa - a0 - 0.3) / (math.pi / 2))),
            )
            for aa in a
        ]
        lines.append(pts)
    lines.append(_arc_seg(0.0, 0.0, 0.18, 0, 2 * math.pi))
    return lines


def prim_sun_spiral():
    lines = [prim_spiral()[0][::-1]]
    lines.append(_arc_seg(0.0, 0.0, 0.72, 0, 2 * math.pi))
    return lines


# -- sky zone --
def prim_cloud():
    lines = []
    xs = np.linspace(-0.75, 0.75, 12)
    base = [(float(x), 0.28 + 0.12 * math.sin(2 * math.pi * x / 0.9)) for x in xs]
    lines.append(base)
    lines.append(_arc_seg(-0.3, -0.1, 0.42, -0.5 * math.pi, 0.5 * math.pi))
    lines.append(_arc_seg(0.3, -0.1, 0.42, -0.5 * math.pi, 0.5 * math.pi))
    return lines


def prim_bird():
    lines = []
    lines.append([(-0.75, 0.0), (-0.3, 0.25), (-0.05, 0.0), (-0.35, -0.22)])
    lines.append([(-0.35, 0.0), (0.0, 0.45), (0.35, 0.0), (0.0, -0.4)])
    return lines


def prim_dancer_f():
    lines = []
    # голова
    lines.append(_arc_seg(0.0, 0.78, 0.12, 0, 2 * math.pi))
    # коса
    lines.append([(0.12, 0.7), (0.35, 0.35), (0.1, 0.05)])
    # тело/сарафан (трапеция)
    lines.append([(-0.22, 0.5), (-0.28, -0.35), (0.26, -0.2), (0.3, 0.5), (-0.22, 0.5)])
    # подол раскрыт (дуга)
    lines.append(_arc_seg(0.0, -0.55, 0.42, -0.2 * math.pi, math.pi + 0.2 * math.pi))
    # рука вверх
    lines.append([(0.24, 0.4), (0.6, 0.75), (0.45, 0.85)])
    # вторая рука в сторону-вверх
    lines.append([(-0.18, 0.4), (-0.55, 0.6), (-0.62, 0.45)])
    # орнамент на сарафане
    lines.append([(-0.12, 0.15), (0.2, 0.2)])
    lines.append([(-0.16, -0.05), (0.2, 0.0)])
    return lines


def prim_dancer_m():
    lines = []
    lines.append(_arc_seg(0.0, 0.78, 0.12, 0, 2 * math.pi))
    # шапка
    lines.append(_arc_seg(0.0, 0.78, 0.2, math.pi, 2 * math.pi))
    # тело рубаха
    lines.append([(-0.26, 0.5), (-0.2, -0.3), (0.22, -0.25), (0.28, 0.5), (-0.26, 0.5)])
    # руки подняты
    lines.append([(0.24, 0.35), (0.6, 0.7), (0.55, 0.85)])
    lines.append([(-0.22, 0.35), (-0.58, 0.65), (-0.5, 0.8)])
    # порты
    lines.append([(-0.15, -0.32), (-0.15, -0.62)])
    lines.append([(0.2, -0.3), (0.2, -0.6)])
    lines.append([(-0.15, -0.62), (-0.28, -0.78), (-0.1, -0.78), (-0.05, -0.65)])
    lines.append([(0.2, -0.6), (0.1, -0.78), (0.28, -0.78), (0.22, -0.62)])
    return lines


def prim_ribbon():
    # S-лента / завиток
    pts = []
    for t in np.linspace(0, 1, 46):
        x = -0.68 + 1.36 * t
        y = 0.65 * math.sin(3.0 * math.pi * t + 0.3) * (1 - 0.25 * t)
        pts.append((x, y))
    return [pts]


def prim_star_orn():
    lines = []
    for k in range(8):
        a = k * math.pi / 4
        v = (math.cos(a), math.sin(a))
        p1 = (0.55 * v[0], 0.55 * v[1])
        p2 = (0.9 * v[0], 0.9 * v[1])
        lines.append([p1, p2])
    lines.append(_arc_seg(0.0, 0.0, 0.42, 0, 2 * math.pi))
    lines.append(_arc_seg(0.0, 0.0, 0.16, 0, 2 * math.pi))
    return lines


def prim_clouds_spiral():
    pts = []
    for t in np.linspace(0, 1, 50):
        r = 0.15 + 0.7 * t
        a = -1.2 + 5.0 * t
        pts.append((r * math.cos(a), r * math.sin(a)))
    return [pts]


def prim_double_bird():
    lines = []
    lines.append([(-0.75, 0.35), (-0.4, 0.05), (-0.75, -0.15)])
    lines.append([(-0.4, 0.05), (0.0, 0.5), (0.4, 0.05)])
    lines.append([(0.4, 0.05), (0.75, 0.4), (0.75, -0.2)])
    return lines


def prim_accordion():
    """Гармонь — отсылка к сказу Писахова."""
    lines = []
    lines.append([(-0.55, -0.5), (0.55, -0.5), (0.55, 0.5), (-0.55, 0.5), (-0.55, -0.5)])
    # меха — зигзаг-складки
    for k in range(5):
        x = -0.45 + k * 0.22
        lines.append([(x, -0.4), (x + 0.11, -0.2), (x, 0.0), (x + 0.11, 0.2), (x, 0.4)])
    # клавиатура (точки)
    for k in range(4):
        lines.append(_arc_seg(-0.3 + k * 0.2, 0.58, 0.05, 0, 2 * math.pi))
    return lines


def prim_boot():
    """Сапог, пристукивающий о землю."""
    lines = []
    lines.append(
        [
            (-0.15, -0.78),
            (-0.05, 0.15),
            (0.25, 0.15),
            (0.3, -0.3),
            (0.55, -0.45),
            (0.7, -0.3),
            (0.55, -0.2),
            (0.3, -0.15),
        ]
    )
    lines.append(
        [
            (-0.15, -0.78),
            (0.3, -0.62),
            (0.62, -0.72),
            (0.68, -0.92),
            (0.55, -0.85),
            (0.42, -0.98),
            (0.3, -0.85),
        ]
    )
    lines.append([(-0.06, 0.12), (-0.06, -0.1)])
    # отскок: пыль-дорожки
    lines.append([(0.7, -0.98), (0.82, -0.94), (0.86, -1.04), (0.72, -0.74), (0.9, -0.7)])
    return lines


def prim_mug():
    """Кружка «лётное пиво» + пузырьки."""
    lines = []
    lines.append([(-0.3, -0.55), (-0.3, 0.15), (0.3, 0.15), (0.3, -0.55), (-0.3, -0.55)])
    lines.append(_arc_seg(0.3, 0.05, 0.18, -0.5 * math.pi, 0.5 * math.pi))
    # пена/пар
    lines.append([(-0.2, 0.15), (-0.1, 0.32), (0.05, 0.2), (0.2, 0.34)])
    lines.append(_arc_seg(-0.05, -0.2, 0.06, 0, 2 * math.pi))
    lines.append(_arc_seg(0.15, -0.1, 0.045, 0, 2 * math.pi))
    return lines


def prim_horse():
    """Конёк-пряник (северный орнамент)."""
    lines = []
    # корпус
    lines.append(
        [
            (-0.55, 0.1),
            (0.6, 0.1),
            (0.78, -0.05),
            (0.7, -0.18),
            (0.5, -0.1),
            (0.3, -0.15),
            (0.1, -0.1),
        ]
    )
    # шея и голова с ухом
    lines.append([(0.6, 0.1), (0.62, 0.42), (0.72, 0.52), (0.78, 0.4), (0.62, 0.3)])
    lines.append([(0.62, 0.42), (0.52, 0.34), (0.6, 0.28)])
    lines.append([(0.66, 0.45), (0.72, 0.52)])
    # ноги
    lines.append([(-0.45, -0.1), (-0.5, -0.55), (-0.38, -0.58)])
    lines.append([(-0.15, -0.12), (-0.2, -0.55), (-0.08, -0.58)])
    lines.append([(0.1, -0.14), (0.18, -0.55), (0.3, -0.57)])
    lines.append([(0.42, -0.13), (0.5, -0.5), (0.6, -0.52)])
    # орнамент на корпусе — ромбик
    lines.append([(-0.2, 0.0), (-0.05, 0.06), (0.1, 0.0), (-0.05, -0.06), (-0.2, 0.0)])
    return lines


def prim_meander():
    """Меандр-орнамент (греческий зигзаг)."""
    lines = []
    y = 0.0
    pts = []
    for k in range(6):
        x0 = -0.9 + k * 0.36
        pts = [
            (x0, y),
            (x0, y + 0.55),
            (x0 + 0.18, y + 0.55),
            (x0 + 0.18, y),
            (x0 + 0.18, y + 0.55),
        ]
        lines.append(pts)
    lines.append([(-0.9, y), (0.9, y)])
    return lines


def prim_serpentine():
    """Волна-серпантин с завитком (лента из ТЗ)."""
    pts = []
    for t in np.linspace(0, 1, 50):
        x = -0.8 + 1.6 * t
        y = 0.6 * math.sin(2.6 * math.pi * t)
        pts.append((x, y))
    lines = [pts]
    lines.append([(-0.62, 0.2), (-0.42, 0.32), (-0.3, 0.18)])
    lines.append([(0.62, -0.2), (0.42, -0.32), (0.3, -0.18)])
    return lines


PRIMS_GROUND = [
    prim_wave,
    prim_fir,
    prim_house,
    prim_rhombus,
    prim_fence,
    prim_snowflake,
    prim_boat,
    prim_spiral,
    prim_wriggle,
    prim_accordion,
    prim_boot,
    prim_mug,
    prim_horse,
    prim_meander,
    prim_serpentine,
]
PRIMS_SUN = [prim_sun_rays, prim_kolovrat, prim_sun_half, prim_sun_spiral, prim_sun_spiral]
PRIMS_SKY = [
    prim_cloud,
    prim_bird,
    prim_dancer_f,
    prim_dancer_m,
    prim_ribbon,
    prim_star_orn,
    prim_double_bird,
    prim_clouds_spiral,
    prim_cloud,
    prim_accordion,
    prim_serpentine,
    prim_meander,
]


def zone_of(cy):
    if cy < ZM["ground"] * H:
        return "ground"
    if cy < ZM["sun"] * H:
        return "sun"
    return "sky"


def pick_prims(zone, cx, cy, det_id):
    h = hashlib.md5(f"{det_id}|{cx:.0f}|{cy:.0f}".encode()).hexdigest()
    if zone == "ground":
        pool = PRIMS_GROUND
        # мужчина с собакой — самая нижняя центральная деталь (выделено отдельно)
        return pool[int(h[:2], 16) % len(pool)]
    if zone == "sun":
        pool = PRIMS_SUN
        return pool[int(h[2:4], 16) % len(pool)]
    pool = PRIMS_SKY
    return pool[int(h[4:6], 16) % len(pool)]


# ---------- SVG-экспорт ----------
def export_svg(polys, deco_paths, out_path):
    """polys: список (polygon, kind) деталей. deco_paths: голубые пути."""
    mm = PT2MM
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{W:.1f}mm" height="{H:.1f}mm" viewBox="0 0 {W:.2f} {H:.2f}">',
    ]
    # внешняя рамка
    lines.append(
        f'<path fill="none" stroke-width="0.2" stroke-linecap="butt" stroke-linejoin="miter" '
        f'stroke="rgb(0%, 0%, 0%)" d="M 0 0 L {W} 0 L {W} {H} L 0 {H} Z"/>'
    )
    # детали (чёрные контуры)
    for poly, _ in polys:
        coords = list(poly.exterior.coords)
        if not poly.is_valid or len(coords) < 3:
            continue
        d = "M " + " L ".join(f"{x:.3f} {y:.3f}" for x, y in coords[:-1]) + " Z"
        lines.append(
            f'<path fill="none" stroke-width="0.2" stroke-linecap="butt" stroke-linejoin="miter" '
            f'stroke="rgb(0%, 0%, 0%)" d="{d}"/>'
        )
    # голубые прорисовки
    for pts in deco_paths:
        if len(pts) < 2:
            continue
        d = "M " + " L ".join(f"{x:.3f} {y:.3f}" for x, y in pts)
        lines.append(
            f'<path fill="none" stroke-width="0.2" stroke-linecap="butt" stroke-linejoin="miter" '
            f'stroke="rgb(16.078186%, 67.059326%, 88.627625%)" d="{d}"/>'
        )
    lines.append("</svg>")
    with open(out_path, "w") as f:
        f.write("\n".join(lines))
    print(f"SVG записан: {out_path}  ({len(polys)} деталей, {len(deco_paths)} голубых путей)")


# ---------- main ----------
def main():
    ap = argparse.ArgumentParser(description="Генератор схемы пазла «Танцы в облаках»")
    ap.add_argument(
        "-o",
        "--out",
        default=os.path.join(
            os.path.dirname(__file__), "output", "Танцы в облаках_310 x 430_450 дет.svg"
        ),
    )
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--dry-run", action="store_true", help="только отчёт о параметрах, без записи")
    args = ap.parse_args()

    rng = seed_rng(args.seed)
    cells = build_grid(rng)
    valid = [
        c for c in cells if c["geom"] is not None and c["geom"].is_valid and not c["geom"].is_empty
    ]
    print(f"Сетка: {NX}x{NY}={NX*NY} ячеек, валидных полигонов: {len(valid)}")

    # большое «сюжетное ядро»: самая нижняя центральная деталь → мужчина с собакой
    lower_center = None
    best = 1e9
    for c in valid:
        gx, gy = c["geom"].centroid.x, c["geom"].centroid.y
        if gy < 0.18 * H:
            dist = abs(gx - W / 2) + (gy - 0.12 * H) * 0.5
            if dist < best:
                best = dist
                lower_center = c

    deco = []
    for c in valid:
        gx, gy = c["geom"].centroid.x, c["geom"].centroid.y
        b = c["geom"].bounds
        s = 0.30 * min(b[2] - b[0], b[3] - b[1])
        if s <= 0.1:
            continue
        zone = zone_of(gy)
        if c is lower_center:
            prims = [prim_dancer_m, prim_wriggle]  # мужик + собака-зигзаг
        else:
            prims = [pick_prims(zone, gx, gy, c["i"] + c["j"] * NX)]
        for pf in prims:
            local = pf()
            deco.extend(scale_prims(local, gx, gy, s))

    if args.dry_run:
        print("dry-run: деталей", len(valid), "голубых линий", len(deco))
        return

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    export_svg([(c["geom"], None) for c in valid], deco, args.out)


if __name__ == "__main__":
    main()
