"""GeekNeural: тесты ядра дедупликации."""
import os
import tempfile
import uuid

from core.dedup import DedupEngine, estimate_tokens


def _sid():
    return "test_" + uuid.uuid4().hex


def test_dedup_repeat_read_saves_bytes():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "big.txt")
        content = "x" * 5000  # > MIN_DEDUP_BYTES, не volatile
        with open(p, "w") as f:
            f.write(content)

        eng = DedupEngine(_sid())
        r1 = eng.read(p)
        assert r1.deduped is False, "первое чтение должно отдать контент"
        r2 = eng.read(p)
        assert r2.deduped is True, "повтор должен дедупиться"
        assert "уже в контексте" in r2.content
        assert eng.stats.bytes_saved >= 4900
        assert eng.stats.pct_saved > 40


def test_force_returns_full_content():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "big.txt")
        with open(p, "w") as f:
            f.write("y" * 5000)
        eng = DedupEngine(_sid())
        eng.read(p)
        r = eng.read(p, force=True)
        assert r.deduped is False
        assert r.content == "y" * 5000


def test_volatile_not_deduped():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "app.log")
        with open(p, "w") as f:
            f.write("z" * 5000)
        eng = DedupEngine(_sid())
        eng.read(p)
        r = eng.read(p)
        assert r.deduped is False, "логи не дедуплицируем (volatile)"
        assert r.reason == "volatile_or_tiny"


def test_tiny_not_deduped():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "tiny.py")
        with open(p, "w") as f:
            f.write("a=1")
        eng = DedupEngine(_sid())
        eng.read(p)
        r = eng.read(p)
        assert r.deduped is False, "мелкие файлы не дедуплицируем"


def test_read_text_dedup():
    eng = DedupEngine(_sid())
    t = "один и тот же большой кусок контекста " * 100
    r1 = eng.read_text(t, key="k")
    r2 = eng.read_text(t, key="k")
    assert r1.deduped is False and r2.deduped is True
    assert eng.stats.est_tokens_saved > 0


def test_estimate_tokens():
    assert estimate_tokens("abcd") == 1
    assert estimate_tokens("a" * 40) == 10


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nALL TESTS PASSED")
