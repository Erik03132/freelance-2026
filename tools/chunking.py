#!/usr/bin/env python3
"""RAG-4 — chunking-стратегии (урок Habr #1070662).

Используется при ingestion в claude-mem / долгом контексте:
  - fixed_chunk: фиксированный размер + overlap;
  - recursive_chunk: рекурсивный сплит по разделителям (\n\n, \n, ". ", " ", "")
    с hard-split, если разделители исчерпаны;
  - merge_small_chunks: склейка мелочи до target_size (structure-aware-финал).

Dependency-free, deterministic, offline (для eval_gate).
"""

from __future__ import annotations

DEFAULT_SEPARATORS = ("\n\n", "\n", ". ", " ", "")


def fixed_chunk(text: str, size: int, overlap: int = 0) -> list[str]:
    """Фиксированный размер + overlap (step = size - overlap)."""
    if size <= 0:
        raise ValueError("size must be > 0")
    if overlap < 0 or overlap >= size:
        raise ValueError("overlap must be in [0, size)")
    if not text:
        return []
    step = size - overlap
    return [text[i : i + size] for i in range(0, len(text), step)]


def recursive_chunk(text: str, size: int, separators=DEFAULT_SEPARATORS) -> list[str]:
    """Рекурсивный сплит по разделителям; hard-split когда разделители кончились."""
    if size <= 0:
        raise ValueError("size must be > 0")
    if not text:
        return []
    if len(text) <= size:
        return [text]
    for i, sep in enumerate(separators):
        if sep == "":
            return [text[j : j + size] for j in range(0, len(text), size)]
        if sep in text:
            out: list[str] = []
            for piece in text.split(sep):
                if not piece:
                    continue
                out.extend(recursive_chunk(piece, size, separators[i + 1 :]))
            return out
    return [text[j : j + size] for j in range(0, len(text), size)]


def merge_small_chunks(chunks: list[str], target: int, sep: str = " ") -> list[str]:
    """Жадная склейка подряд идущих чанков до target_size."""
    if target <= 0:
        raise ValueError("target must be > 0")
    merged: list[str] = []
    cur = ""
    for c in chunks:
        if not c:
            continue
        if not cur:
            cur = c
        elif len(cur) + len(sep) + len(c) <= target:
            cur = cur + sep + c
        else:
            merged.append(cur)
            cur = c
    if cur:
        merged.append(cur)
    return merged
