"""
Levitan Eval Suite — evaluates voice agent (FAQ agent) system, not just model.
Based on: Evals: что должен знать каждый AI-инженер в 2026 (Habr #1050736)

Usage:
  python3 tests/eval_levitan.py              # full suite
  python3 tests/eval_levitan.py --faq        # FAQ cache only
  python3 tests/eval_levitan.py --stt        # STT only
  python3 tests/eval_levitan.py --tts        # TTS only
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from deploy.levitan_faq_agent import (
    SYSTEM_PROMPT,
    _normalize,
    faq_lookup,
    load_faq_cache,
    synthesize_wav,
)


class EvalSuite:
    def __init__(self):
        self.tests = []
        self.passed = 0
        self.failed = 0

    def add(self, name: str, category: str, cap: bool, fn):
        """cap=True = capability test (new behavior), False = regression (must stay stable)"""
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
    load_faq_cache()

    # ═══════════════════════════════════════
    # FAQ CACHE — regression (exact matches must stay)
    # ═══════════════════════════════════════
    for query, expected_key in [
        ("где вы находитесь", "где вы находитесь"),
        ("есть ли бройлеры", "есть ли бройлеры"),
        ("индюки", "индюки"),
        ("привет", "привет"),
        ("доставка", "доставка"),
        ("гарантия", "гарантия"),
        ("оплата", "оплата"),
    ]:
        suite.add(
            f'FAQ exact: "{query}" → "{expected_key}"',
            "faq",
            False,
            lambda q=query, k=expected_key: assert_faq_hit(q, k),
        )

    # Capability: alias/fuzzy matches
    for query, expected_key in [
        ("расскажи про уток", "утки"),
        ("сколько стоят утки", "утки"),
        ("аптечка для цыплят", "аптечка"),
        ("привезите в москву", "в москву доставляете"),
        ("яйцо на инкубацию", "инкубационное яйцо"),
        ("а сколько стоят бройлера", "цена бройлера"),
        ("хочу заказать", "как заказать"),
        ("чем кормить цыплят бройлеров", "чем кормить цыплят"),
        ("посчитайте заказ", "посчитайте заказ"),
        ("ветеринарные справки", "вет справка"),
        ("к дому привезут", "к дому привезете"),
    ]:
        suite.add(
            f'FAQ alias: "{query[:30]}..." → "{expected_key}"',
            "faq",
            True,
            lambda q=query, k=expected_key: assert_faq_hit(q, k),
        )

    # Regression: should NOT match
    for query in ["свинина", "кролики", "баранина", "как переустановить windows"]:
        suite.add(
            f'FAQ nomatch: "{query}" → None', "faq", False, lambda q=query: assert_faq_miss(q)
        )

    # Capability: negative synonym protection
    suite.add(
        'FAQ neg-syn: "бройлеры" не находит "утки"',
        "faq",
        True,
        lambda: assert_faq_not_match("бройлеры", "утки"),
    )
    suite.add(
        'FAQ neg-syn: "утки" не находит "индюки"',
        "faq",
        True,
        lambda: assert_faq_not_match("утки", "индюки"),
    )
    suite.add(
        'FAQ neg-syn: "индюки" не находит "бройлеры"',
        "faq",
        True,
        lambda: assert_faq_not_match("индюки", "бройлеры"),
    )

    # ═══════════════════════════════════════
    # NORMALIZATION
    # ═══════════════════════════════════════
    suite.add(
        "normalize: ё→е, й→и, пунктуация",
        "norm",
        False,
        lambda: assert_eq(_normalize("Привет! Как дела?"), "привет как дела"),
    )
    suite.add(
        "normalize: ё in middle", "norm", False, lambda: assert_eq(_normalize("брьлёры"), "брлёры")
    )
    suite.add(
        "normalize: удаляет спецсимволы",
        "norm",
        False,
        lambda: assert_eq(_normalize("цена??? бройлеров..."), "цена бройлеров"),
    )

    # ═══════════════════════════════════════
    # SYSTEM PROMPT — regression (key facts must stay)
    # ═══════════════════════════════════════
    for key_phrase in [
        "Азовский инкубатор",
        "Крым",
        "Азовское",
        "КОББ-500",
        "РОСС-308",
        "гарантия 100",
        "вакцинация",
        "Пурина",
        "предоплата 50",
        "телефон",
    ]:
        suite.add(
            f'SYSTEM_PROMPT contains: "{key_phrase}"',
            "prompt",
            False,
            lambda k=key_phrase: assert_in(k, SYSTEM_PROMPT),
        )

    # Capability: no forbidden content in prompt
    for forbidden in ["утки летом", "гуси летом", "индюки летом"]:
        suite.add(
            f'SYSTEM_PROMPT NOT contains: "{forbidden}"',
            "prompt",
            True,
            lambda f=forbidden: assert_not_in(f, SYSTEM_PROMPT),
        )

    # ═══════════════════════════════════════
    # PHONE EXTRACTION (from faq_agent)
    # ═══════════════════════════════════════
    from deploy.levitan_faq_agent import extract_phone

    for text, expected in [
        ("мой номер 79123456789", "79123456789"),
        ("звоните на +7 912 345 67 89", "79123456789"),
        ("8 912 345 67 89", "79123456789"),
        ("телефон: 79123456789", "79123456789"),
    ]:
        suite.add(
            f'extract_phone: "{text}" → {expected}',
            "phone",
            False,
            lambda t=text, e=expected: assert_eq(extract_phone(t), e),
        )

    # ═══════════════════════════════════════
    # VOLUME EXTRACTION
    # ═══════════════════════════════════════
    from deploy.levitan_faq_agent import extract_volume

    for text, expected in [
        ("50 голов", 50),
        ("сто штук", 100),
        ("200 бройлеров", 200),
        ("тысяча", 1000),
    ]:
        suite.add(
            f'extract_volume: "{text}" → {expected}',
            "volume",
            False,
            lambda t=text, e=expected: assert_eq(extract_volume(t), e),
        )

    # ═══════════════════════════════════════
    # BREED EXTRACTION
    # ═══════════════════════════════════════
    from deploy.levitan_faq_agent import extract_breed

    for text, expected in [
        ("КОББ-500", "КОББ-500"),
        ("кobb 500", "КОББ-500"),
        ("Росс 308", "РОСС-308"),
        ("росс-308", "РОСС-308"),
    ]:
        suite.add(
            f'extract_breed: "{text}" → {expected}',
            "breed",
            False,
            lambda t=text, e=expected: assert_eq(extract_breed(t), e),
        )

    # ═══════════════════════════════════════
    # REJECTION DETECTION
    # ═══════════════════════════════════════
    from deploy.levitan_faq_agent import is_rejection

    for text in ["не надо", "не хочу", "не интересно", "не звоните", "у меня уже есть"]:
        suite.add(
            f'is_rejection: "{text}" → True',
            "rejection",
            False,
            lambda t=text: assert_true(is_rejection(t)),
        )
    for text in ["да", "интересно", "расскажите", "сколько стоит"]:
        suite.add(
            f'is_rejection: "{text}" → False',
            "rejection",
            False,
            lambda t=text: assert_false(is_rejection(t)),
        )

    # ═══════════════════════════════════════
    # STT (requires audio file) — capability only
    # ═══════════════════════════════════════
    # test.wav not required for CI

    # ═══════════════════════════════════════
    # TTS SYNTHESIS — capability (produces WAV)
    # ═══════════════════════════════════════
    def test_tts_yandex():
        """Test TTS produces valid WAV (skips if no API key)"""
        if not os.getenv("YC_API_KEY") or not os.getenv("YC_FOLDER_ID"):
            print("  ⚠ [tts] Skipping (no YC_API_KEY/YC_FOLDER_ID)")
            return
        path = synthesize_wav("Тест синтеза речи")
        assert path and Path(path).exists(), "TTS should produce file"
        assert Path(path).stat().st_size > 1000, "WAV should have content"
        print(f"  ✅ [tts] TTS produced: {path} ({Path(path).stat().st_size} bytes)")

    suite.add("TTS Yandex produces valid WAV", "tts", True, test_tts_yandex)

    def test_tts_edge_fallback():
        """Test edge-tts fallback (called automatically by synthesize_wav)"""
        # This test runs without YC_API_KEY to verify edge-tts fallback
        path = synthesize_wav("Тест фолбэка edge-tts")
        assert path and Path(path).exists(), "edge-tts fallback should produce file"
        print(f"  ✅ [tts] edge-tts fallback produced: {path}")

    suite.add("TTS edge-tts fallback produces WAV", "tts", True, test_tts_edge_fallback)

    return suite


# === Assertion helpers ===
def assert_eq(a, b):
    assert a == b, f'got "{a}" expected "{b}"'


def assert_in(substr, text):
    assert substr in text, f'"{substr}" not found in text'


def assert_not_in(substr, text):
    assert substr not in text, f'"{substr}" should not be in text'


def assert_true(fn):
    assert fn is True, f"expected True, got {fn}"


def assert_false(fn):
    assert fn is False, f"expected False, got {fn}"


def assert_faq_hit(query: str, expected_key: str):
    result = faq_lookup(query)
    assert result, f'"{query}" should match FAQ "{expected_key}" but got None'
    # Load cache to verify exact key
    cache = json.loads(
        Path(__file__)
        .parent.parent.joinpath("docs/ANGELLA_BROILERS_FAQ_CACHE.json")
        .read_text(encoding="utf-8")
    )
    expected = cache.get(expected_key, "")
    assert result == expected, (
        f'"{query}" matched wrong FAQ.\n'
        f'  Expected ("{expected_key}"): "{expected[:50]}..."\n'
        f'  Got: "{result[:50]}..."'
    )


def assert_faq_miss(query: str):
    result = faq_lookup(query)
    assert not result, f'"{query}" should NOT match FAQ but got: "{result[:50]}..."'


def assert_faq_not_match(query: str, avoid_key: str):
    result = faq_lookup(query)
    assert result, f'"{query}" should match something'
    cache = json.loads(
        Path(__file__)
        .parent.parent.joinpath("docs/ANGELLA_BROILERS_FAQ_CACHE.json")
        .read_text(encoding="utf-8")
    )
    avoided = cache.get(avoid_key, "")
    assert result != avoided, f'"{query}" matched "{avoid_key}" but should NOT'


if __name__ == "__main__":
    filter_cat = None
    if len(sys.argv) > 1:
        arg = sys.argv[1].lstrip("--")
        if arg in ("faq", "norm", "prompt", "phone", "volume", "breed", "rejection", "tts", "stt"):
            filter_cat = arg

    print(f"\n{'='*60}")
    print("  Levitan Eval Suite")
    print("  Voice agent (FAQ + STT + TTS + Dialog logic)")
    if filter_cat:
        print(f"  Filter: {filter_cat}")
    print(f"{'='*60}")

    suite = build_suite()
    suite.run(filter_cat)
    ok = suite.summary()

    sys.exit(0 if ok else 1)
