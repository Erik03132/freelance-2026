#!/usr/bin/env python3
import random
import statistics
import sys

sys.path.insert(0, ".")
from generate4 import build_scene, clip_to_field, W, H, FRAME_M
from shapely.geometry import Polygon

figs = clip_to_field(build_scene(random.Random(7)))
m = FRAME_M


def classify(f):
    w = f.bounds[2] - f.bounds[0]
    h = f.bounds[3] - f.bounds[1]
    area = f.area
    cx = f.centroid.x
    cy = f.centroid.y
    # земля (низ), солнце (30-56%), небо (верх)
    zone = "sky" if cy > H * 0.56 else ("sun" if cy > H * 0.30 else "ground")
    return dict(w=w, h=h, d=max(w, h), area=area, cx=cx, cy=cy, zone=zone)


infos = [classify(f) for f in figs]

print(f"count={len(figs)}")
ds = [d["d"] for d in infos]
print(f"max-side med={statistics.median(ds):.1f}  min={min(ds):.1f}  max={max(ds):.1f}")
dims = ["%.0fx%.0f" % (i["w"], i["h"]) for i in infos]
zones = {}
for i in infos:
    zones.setdefault(i["zone"], 0)
    zones[i["zone"]] += 1
print("zones:", zones)
cov = sum(i["area"] for i in infos) / ((W - 2 * m) * (H - 2 * m))
print(f"coverage: {cov:.1%}")
gt30 = [i for i in infos if i["d"] > 30]
print(">30mm:", len(gt30))
for i in gt30:
    print(
        "   w=%.1f h=%.1f zone=%s cx=%.0f cy=%.0f" % (i["w"], i["h"], i["zone"], i["cx"], i["cy"])
    )
# минимальный зазор
mins = [
    figs[i].distance(figs[j])
    for i in range(len(figs))
    for j in range(i + 1, len(figs))
    if figs[i].distance(figs[j]) < 3
]
print("gap<3 violations:", len(mins))
# outside frame check
rect = Polygon([(m, m), (W - m, m), (W - m, H - m), (m, H - m)])
out = [i for i, f in zip(infos, figs) if not f.within(rect)]
print("только частично/вне рамки:", len(out))
for i in out:
    print(
        "   w=%.1f h=%.1f zone=%s cx=%.0f cy=%.0f" % (i["w"], i["h"], i["zone"], i["cx"], i["cy"])
    )
