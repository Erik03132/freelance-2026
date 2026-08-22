"""Тесты ES-12: VAD-профиль + блеклист артефактов (чистые, без аудио/сети)."""

import numpy as np
import pytest

from levitan.vad_filter import (
    VADProfile,
    analyze_speech,
    check_speech_quality,
    is_artifact_phrase,
)


def _noise(n, amp=0.001, sr=8000):
    """Тихий шум (тишина/шорох)."""
    rng = np.random.default_rng(0)
    return (rng.standard_normal(n) * amp).astype(np.float32)


def _speech(n, sr=8000):
    """Синусоида 200 Гц — явная речь (плато + доля)."""
    t = np.arange(n) / sr
    return (np.sin(2 * np.pi * 200 * t) * 0.3).astype(np.float32)


# ── analyze_speech ────────────────────────────────────────────────────────────


def test_analyze_silence_is_empty():
    a = analyze_speech(_noise(8000))
    assert a["speech_fraction"] < 0.15
    assert a["speech_frames"] < 3


def test_analyze_speech_has_high_fraction():
    a = analyze_speech(_speech(8000 * 2))
    assert a["speech_fraction"] > 0.5
    assert a["plateau_ms"] >= 120.0
    assert a["speech_chunks"] >= 1


def test_analyze_empty_audio_safe():
    a = analyze_speech(np.array([], dtype=np.float32))
    assert a["speech_fraction"] == 0.0


# ── check_speech_quality ──────────────────────────────────────────────────────


def test_silence_fails_quality():
    assert not check_speech_quality(analyze_speech(_noise(8000)))


def test_speech_passes_quality():
    assert check_speech_quality(analyze_speech(_speech(8000 * 2)))


def test_short_spike_fails_profile():
    # Один всплеск энергии на коротком клипе — не речь
    clip = _noise(8000 * 2)
    clip[1000:1200] = 0.5  # 200 ms всплеск
    assert not check_speech_quality(analyze_speech(clip))


def test_custom_profile_threshold():
    p = VADProfile(min_speech_fraction=0.9)
    mixed = np.concatenate([_speech(8000), _noise(8000 * 4)]).astype(np.float32)
    assert not check_speech_quality(analyze_speech(mixed), profile=p)
    assert check_speech_quality(analyze_speech(_speech(8000 * 3)), profile=p)


# ── is_artifact_phrase (блеклист) ─────────────────────────────────────────────


@pytest.mark.parametrize(
    "text",
    [
        "Продолжение следует…",
        "Продолжение следует",
        "Спасибо за внимание",
        "конец записи.",
        "Проверка связи!",
        "подпишитесь на канал",
    ],
)
def test_artifact_phrases_detected(text):
    assert is_artifact_phrase(text)


@pytest.mark.parametrize(
    "text",
    [
        "",
        "Здравствуйте, выращиваете пшеницу?",
        "Да, у нас 500 тонн ячменя",
        "Подскажите, пожалуйста, цену",
    ],
)
def test_real_speech_not_artifact(text):
    assert not is_artifact_phrase(text)


def test_artifact_with_punctuation_and_case():
    assert is_artifact_phrase("  ПРОДОЛЖЕНИЕ   СЛЕДУЕТ!!! ")
