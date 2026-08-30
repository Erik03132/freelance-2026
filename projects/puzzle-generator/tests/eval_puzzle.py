"""
Eval Suite: генератор схем пазла «Танцы в облаках» v2 (generate2, 18.08.2026).
Проверяет: фигурная плитка 18x25, зазор ≥3 мм, детали ≤30 мм, 0.2 pt,
клип сюжета по деталям (голубой не пересекает швы), детерминизм.

Запуск:  python3 tests/eval_puzzle.py
"""

import math  # noqa: F401
import os
import random
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lxml import etree  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

import generate2 as generate  # noqa: E402

NS = {"svg": "http://www.w3.org/2000/svg"}
BLACK = "rgb(0%, 0%, 0%)"
BLUE = "rgb(16.078186%, 67.059326%, 88.627625%)"


class EvalSuite:
    def __init__(self):
        self.tests = []
        self.passed = 0
        self.failed = 0

    def add(self, name, category, fn):
        self.tests.append((name, category, fn))

    def run(self, filter_cat=None):
        for name, cat, fn in self.tests:
            if filter_cat and cat != filter_cat:
                continue
            try:
                fn()
                print(f"  ✅ [{cat}] {name}")
                self.passed += 1
            except AssertionError as e:
                print(f"  ❌ [{cat}] {name}: {e}")
                self.failed += 1
            except Exception as e:
                print(f"  💥 [{cat}] {name}: {type(e).__name__}: {e}")
                self.failed += 1

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'─' * 60}")
        print(f"  Results: {self.passed}/{total} passed")
        if total:
            print(f"  Score: {self.passed / total * 100:.0f}%")
        return self.failed == 0


def build_suite():
    suite = EvalSuite()

    # ═══════════════════════════════════════
    # GRID (фигурная плитка)
    # ═══════════════════════════════════════

    def test_grid_size():
        assert generate.NX * generate.NY == 450, "сетка 18x25 должна давать 450 ячеек"

    suite.add("Сетка 18x25 = 450 деталей", "grid", test_grid_size)

    def test_grid_fills_field():
        rng = random.Random(7)
        cells = generate.build_tiles(rng)
        assert len(cells) == 450, f"ожидалось 450 деталей, получено {len(cells)}"
        xs = [c.bounds for c in cells]
        assert max(b[2] for b in xs) <= generate.W + 1e-3
        assert max(b[3] for b in xs) <= generate.H + 1e-3
        assert min(b[0] for b in xs) >= -1e-3
        assert min(b[1] for b in xs) >= -1e-3

    suite.add("Детали внутри поля 310x430", "grid", test_grid_fills_field)

    def test_all_polygons_valid():
        rng = random.Random(7)
        cells = generate.build_tiles(rng)
        invalid = [c for c in cells if not c.is_valid or c.is_empty]
        assert not invalid, f"невалидных полигонов: {len(invalid)}"

    suite.add("Все детали — валидные полигоны shapely", "grid", test_all_polygons_valid)

    # ═══════════════════════════════════════
    # SIZES & GAPS
    # ═══════════════════════════════════════

    def _polygons(seed=7):
        return generate.build_tiles(random.Random(seed))

    def test_piece_size_limit():
        for seed in (1, 7, 42):
            polys = _polygons(seed)
            for p in polys:
                x0, y0, x1, y1 = p.bounds
                size = max(x1 - x0, y1 - y0)
                assert size <= 30.0 + 1e-6, f"seed={seed}: деталь {size:.2f} мм > 30"

    suite.add("Детали ≤ 30 мм по большей стороне (3 seed)", "sizes", test_piece_size_limit)

    def test_min_gap():
        polys = _polygons(7)
        n = len(polys)
        min_d = float("inf")
        for i in range(n):
            b0 = polys[i].bounds
            for j in range(i + 1, n):
                b1 = polys[j].bounds
                if (
                    b0[0] - 5 <= b1[2]
                    and b0[2] + 5 >= b1[0]
                    and b0[1] - 5 <= b1[3]
                    and b0[3] + 5 >= b1[1]
                ):
                    d = polys[i].distance(polys[j])
                    if d < min_d:
                        min_d = d
        assert min_d >= 3.0 - 0.02, f"минимальный зазор {min_d:.3f} мм < 3.0"

    suite.add("Зазор между деталями ≥ 3 мм", "sizes", test_min_gap)

    # ═══════════════════════════════════════
    # ARTWORK LAYER
    # ═══════════════════════════════════════

    def test_artwork_present():
        lines = generate.draw_artwork()
        assert len(lines) >= 40, f"сюжетных элементов мало: {len(lines)}"
        total_len = sum(len(ln.coords) for ln in lines)
        assert total_len >= 400, "рисунок слишком маленький"

    suite.add("Сюжетный слой присутствует (40+ линий)", "artwork", test_artwork_present)

    def test_artwork_clipped_in_tiles():
        rng = random.Random(7)
        polys = generate.build_tiles(rng)
        blue = generate.clip_to_tiles(generate.draw_artwork(), polys)
        assert blue, "клип не дал голубых линий"
        union = unary_union(polys).buffer(0.01)
        for ln in blue:
            assert union.covers(ln), "голубая линия выходит за пределы деталей (пересекает шов)"
        # суммарная длина разрыва на швах — рисунок "продолжается" сквозь детали

    suite.add(
        "Голубые линии клипаются по деталям (не пересекают швы)",
        "artwork",
        test_artwork_clipped_in_tiles,
    )

    def test_zone_layout():
        assert generate.Z_GROUND < generate.Z_SUN <= generate.Z_SKY, "зоны по возрастанию"
        assert generate.zone_of(0.10) == "ground"
        assert generate.zone_of(0.35) == "sun"
        assert generate.zone_of(0.90) == "sky"

    suite.add("Зоны композиции (земля<солнце<небо)", "artwork", test_zone_layout)

    # ═══════════════════════════════════════
    # SVG OUTPUT
    # ═══════════════════════════════════════

    def test_svg_structure():
        rng = random.Random(7)
        polys = generate.build_tiles(rng)
        blues = generate.clip_to_tiles(generate.draw_artwork(), polys)
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "test.svg")
            generate.export_svg(polys, [generate.line_d(b) for b in blues], out)
            tree = etree.parse(out)
            root = tree.getroot()
            assert root.get("width").endswith("mm")
            widths = set(p.get("stroke-width") for p in root.xpath("//svg:path", namespaces=NS))
            assert widths == {"0.2"}, f"толщина линий: {widths}"
            blacks = [
                p for p in root.xpath("//svg:path", namespaces=NS) if p.get("stroke") == BLACK
            ]
            bluel = [p for p in root.xpath("//svg:path", namespaces=NS) if p.get("stroke") == BLUE]
            rects = [r for r in root.xpath("//svg:rect", namespaces=NS) if r.get("stroke") == BLACK]
            assert len(blacks) == len(
                polys
            ), f"чёрных контуров {len(blacks)} vs деталей {len(polys)}"
            assert rects, "отсутствует рамка поля"
            assert len(bluel) == len(blues)

    suite.add("SVG: единицы mm, толщина 0.2, цвета, кол-во путей", "svg", test_svg_structure)

    def test_deterministic_output():
        p1 = generate.build_tiles(random.Random(3))
        p2 = generate.build_tiles(random.Random(3))
        c1 = list(p1[0].exterior.coords)
        c2 = list(p2[0].exterior.coords)
        assert len(c1) == len(c2)
        for (x1, y1), (x2, y2) in zip(c1, c2):
            assert abs(x1 - x2) < 1e-6 and abs(y1 - y2) < 1e-6

    suite.add("Детерминизм генерации по seed", "grid", test_deterministic_output)

    return suite


if __name__ == "__main__":
    filter_cat = None
    if len(sys.argv) > 1:
        arg = sys.argv[1].lstrip("--")
        if arg in ("grid", "sizes", "artwork", "svg"):
            filter_cat = arg

    print("\n" + "=" * 60)
    print("  Puzzle-Generator Eval Suite v2 (Танцы в облаках)")
    if filter_cat:
        print(f"  Filter: {filter_cat}")
    print("=" * 60)

    suite = build_suite()
    suite.run(filter_cat)
    ok = suite.summary()
    sys.exit(0 if ok else 1)
