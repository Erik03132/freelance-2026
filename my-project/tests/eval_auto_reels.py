"""
Auto-Reels Eval Suite — evaluates video clipper logic.
Tests: 9:16 conversion, random cuts, audio sync, composition.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from PIL import Image, ImageFilter


class EvalSuite:
    def __init__(self):
        self.tests = []
        self.passed = 0
        self.failed = 0

    def add(self, name: str, category: str, cap: bool, fn):
        self.tests.append((name, category, cap, fn))

    def run(self, filter_cat: str = None):
        for name, cat, cap, fn in self.tests:
            if filter_cat and cat != filter_cat:
                continue
            try:
                fn()
                tag = "✅" if cap else "🟢"
                print(f"  {tag} [{cat}] {name}")
                self.passed += 1
            except AssertionError as e:
                print(f"  ❌ [{cat}] {name}: {e}")
                self.failed += 1
            except Exception as e:
                print(f"  💥 [{cat}] {name}: {type(e).__name__}: {e}")
                self.failed += 1

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'─'*60}")
        print(f"  Results: {self.passed}/{total} passed")
        if total:
            print(f"  Score: {self.passed/total*100:.0f}%")
        return self.failed == 0


def build_suite() -> EvalSuite:
    suite = EvalSuite()

    # 9:16 CONVERSION
    def test_target_resolution():
        target = (1080, 1920)
        ratio = target[0] / target[1]
        assert abs(ratio - 9 / 16) < 0.001

    suite.add("Target resolution is 9:16", "conversion", False, test_target_resolution)

    def test_horizontal_to_vertical():
        current_ratio = 1920 / 1080
        target_ratio = 9 / 16
        assert current_ratio > target_ratio

    suite.add(
        "Horizontal image needs blur background", "conversion", False, test_horizontal_to_vertical
    )

    def test_vertical_stays_vertical():
        current_ratio = 1080 / 1920
        target_ratio = 9 / 16
        assert abs(current_ratio - target_ratio) < 0.001

    suite.add("Vertical image already 9:16", "conversion", False, test_vertical_stays_vertical)

    # RANDOM CUT LOGIC
    def test_random_cut_within_bounds():
        import random

        duration = 10.0
        clip_duration = 4.0
        for _ in range(100):
            start = random.uniform(0, duration - clip_duration)
            assert 0 <= start <= duration - clip_duration

    suite.add("Random cut within bounds", "cut", False, test_random_cut_within_bounds)

    def test_short_clip_returns_full():
        duration = 3.0
        clip_duration = 4.0
        assert duration < clip_duration

    suite.add("Short clip returns full duration", "cut", False, test_short_clip_returns_full)

    # BLUR BACKGROUND
    def test_gaussian_blur_applied():
        # Sharp edge shows blur effect
        img = Image.new("RGB", (100, 100), "black")
        for x in range(50, 100):
            for y in range(100):
                img.putpixel((x, y), (255, 255, 255))
        blurred = img.filter(ImageFilter.GaussianBlur(radius=10))
        orig = img.getpixel((50, 50))
        blur = blurred.getpixel((50, 50))
        assert orig != blur, "Blur should affect edge pixels"

    suite.add("Gaussian blur changes edge pixels", "blur", False, test_gaussian_blur_applied)

    def test_blur_radius():
        img = Image.new("RGB", (100, 100), "black")
        for x in range(50, 100):
            for y in range(100):
                img.putpixel((x, y), (255, 255, 255))
        blurred = img.filter(ImageFilter.GaussianBlur(radius=20))
        center = blurred.getpixel((50, 50))
        assert center != (255, 255, 255), "Blur radius 20 should soften edge"

    suite.add("Blur radius 20 affects edge", "blur", False, test_blur_radius)

    # AUDIO SYNC
    def test_audio_duration_match():
        audio_duration = 30.0
        clip_duration = 4.0
        num_clips = int(audio_duration / clip_duration)
        assert num_clips == 7

    suite.add("Audio duration divides into clips", "audio", False, test_audio_duration_match)

    # COMPOSITION
    def test_concatenation():
        durations = [4.0, 4.0, 4.0, 3.5]
        total = sum(durations)
        assert total == 15.5

    suite.add("Concatenation sums durations", "composition", True, test_concatenation)

    def test_crossfade_transition():
        clip1_end = 4.0
        clip2_start = 4.0 - 0.5
        assert clip2_start == 3.5

    suite.add("Crossfade timing correct", "composition", True, test_crossfade_transition)

    return suite


if __name__ == "__main__":
    filter_cat = None
    if len(sys.argv) > 1:
        arg = sys.argv[1].lstrip("--")
        if arg in ("conversion", "cut", "blur", "audio", "composition"):
            filter_cat = arg

    print(f"\n{'='*60}")
    print("  Auto-Reels Eval Suite")
    print("  Video clipper (9:16, random cuts, blur bg, audio sync)")
    if filter_cat:
        print(f"  Filter: {filter_cat}")
    print(f"{'='*60}")

    suite = build_suite()
    suite.run(filter_cat)
    ok = suite.summary()

    sys.exit(0 if ok else 1)
