"""VAD-профиль против галлюцинаций тишины (ES-12) + чёрный список артефактов.

Контекст (docs/cases/voice-live-pace.md, ES-12): faster-whisper с `vad_filter=True`
уже отсекает тишину, НО пограничный сигнал (шорох/стук/эхо), который VAD принял
за речь, Whisper галлюцинирует в целые фразы ("Продолжение следует…" — 5506
срабатываний в источнике). Лечится двумя слоями:

1. VAD-профиль целиком: доля речевых кусков + длина плато. Если клип на 95% —
   тишина, а Whisper "услышал" длинную фразу, это шум, а не речь → возвращаем "".
2. Артефакт-блеклист: известные галлюцинации Whisper, которые занимают реплику
   целиком (вся очищенная реплика == известный мусор) → возвращаем "".

Оба слоя — чистые функции (тестируемы без аудио/Mango/сети).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np

# ── Известные галлюцинации Whisper на пограничном/тихом сигнале (RU) ──────────
# Нормализованные (lower, без пунктуации/пробелов по краям). Если ВСЯ очищенная
# реплика совпадает с одной из фраз или целиком её содержит — это артефакт.
DEFAULT_ARTIFACT_PHRASES = (
    "продолжение следует",
    "продолжение следует",  # опечатко-устойчивый дубль
    "спасибо за внимание",
    "конец записи",
    "тишина",
    "тестирование микрофона",
    "проверка связи",
    "музыкальная заставка",
    "реклама",
    "subscribe",
    "подпишитесь на канал",
)

_NON_WORD = re.compile(r"[^\wа-яё]+", re.IGNORECASE)


def normalize(text: str) -> str:
    """Нормализация для сравнения с блеклистом: lower, только буквы/цифры."""
    return _NON_WORD.sub(" ", text.lower()).strip()


@dataclass
class VADProfile:
    """Профиль речи клипа. Допускаем, что короткие клипы могут быть целиком речью.

    Attributes:
        min_speech_fraction: доля речевых сэмплов от общего числа (RMS-гейт).
            Ниже — клип считаем тишиной/шумом, Whisper сгаллюцинировал.
        min_speech_frames: минимальное число речевых кадров, чтобы считать речью
            (защита от одного всплеска энергии на коротком клипе).
        min_plateau_ms: минимальная длина непрерывного речевого плато. Короче —
            щелчок/стук, а не слог.
        speech_rms_threshold: АБСОЛЮТНЫЙ RMS-гейт кадра (доля от единицы амплитуды
            PCM16-float). Телефонная речь ~0.05-0.15, линия/шорох ~0.001-0.005.
            Релейный (относительно пика клипа) порог НЕ берём: на плоском шуме
            пик = шум, и весь клип ложно проходит.
    """

    min_speech_fraction: float = 0.15
    min_speech_frames: int = 3
    min_plateau_ms: float = 120.0
    speech_rms_threshold: float = 0.02


def _rms_frames(audio: np.ndarray, frame_ms: int = 20, sample_rate: int = 8000):
    """Вернуть список RMS-значений по кадрам."""
    frame_len = max(1, int(sample_rate * frame_ms / 1000.0))
    n_frames = max(1, len(audio) // frame_len)
    frames = []
    for i in range(n_frames):
        chunk = audio[i * frame_len : (i + 1) * frame_len]
        if chunk.size == 0:
            frames.append(0.0)
        else:
            frames.append(float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2))))
    return frames


def analyze_speech(
    audio: np.ndarray, sample_rate: int = 8000, profile: VADProfile | None = None
) -> dict:
    """Посчитать VAD-профиль клипа: доля речи, число кусков, длина плато.

    Возвращает словарь, пригодный для логирования и для `check_speech_quality`.
    """
    profile = profile or VADProfile()
    if audio is None or audio.size == 0:
        return {
            "speech_fraction": 0.0,
            "speech_chunks": 0,
            "plateau_ms": 0.0,
            "speech_frames": 0,
            "total_frames": 0,
        }

    frames = _rms_frames(audio, sample_rate=sample_rate)
    threshold = profile.speech_rms_threshold
    speech_mask = [f >= threshold for f in frames]

    speech_frames = sum(speech_mask)
    total_frames = len(speech_mask)
    speech_fraction = (speech_frames / total_frames) if total_frames else 0.0

    # Число речевых кусков и длина самого длинного плато
    chunks = 0
    plateau = 0
    max_plateau = 0
    in_speech = False
    for s in speech_mask:
        if s:
            if not in_speech:
                chunks += 1
                in_speech = True
                plateau = 1
            else:
                plateau += 1
            max_plateau = max(max_plateau, plateau)
        else:
            in_speech = False

    frame_ms = 20.0
    return {
        "speech_fraction": speech_fraction,
        "speech_chunks": chunks,
        "plateau_ms": max_plateau * frame_ms,
        "speech_frames": speech_frames,
        "total_frames": total_frames,
    }


def check_speech_quality(analysis: dict, profile: VADProfile | None = None) -> bool:
    """VAD-профиль пройден? True = это речь, False = тишина/шум (отбрасываем)."""
    profile = profile or VADProfile()
    if analysis["speech_frames"] < profile.min_speech_frames:
        return False
    if analysis["speech_fraction"] < profile.min_speech_fraction:
        return False
    if analysis["plateau_ms"] < profile.min_plateau_ms:
        return False
    return True


def is_artifact_phrase(text: str, blacklist=DEFAULT_ARTIFACT_PHRASES) -> bool:
    """Реплика целиком = известный артефакт Whisper? True → трактуем как тишину."""
    cleaned = normalize(text)
    if not cleaned:
        return False
    for phrase in blacklist:
        np_ = normalize(phrase)
        if not np_:
            continue
        # Совпадение целиком ИЛИ артефакт занимает всю (очищенную) реплику
        if cleaned == np_ or np_ in cleaned:
            return True
    return False
