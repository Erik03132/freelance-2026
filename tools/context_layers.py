#!/usr/bin/env python3
"""BK-2 — Слоистый контекст для долгих агентов (урок BookTrans, Habr #1070088).

BookTrans держит 5 слоёв контекста (мир / сюжет / стык / вперёд / работа) с
периодическим сжатием накопительного конспекта, вместо плоского дампа. Здесь —
детерминированный помощник, который раскладывает факты по слоям и периодически
сжимает слой в конспект (fold), чтобы контекст не раздувался на длинных агентах
(claude-mem context injection, trajectory_eval).

Использование:
    from tools.context_layers import LayeredContext
    ctx = LayeredContext()
    ctx.add("work", "вызвал lookup_order(123)")
    ctx.add("story", "пользователь ищет статус заказа")
    digest = ctx.compact("work")   # сворачивает слой в конспект

Офлайн: `python3 tools/tests/eval_context_layers.py` (deterministic, для eval_gate).
"""

from __future__ import annotations

# 5 слоёв контекста (мир/сюжет/стык/вперёд/работа) — порядок важен для рендера.
LAYERS = ["world", "story", "seam", "forward", "work"]

# Порог: при достижении стольки записей в слое — auto-compact.
COMPACT_THRESHOLD = 8


class LayeredContext:
    """Хранит факты по 5 слоям + периодически сжимает слой в конспект."""

    def __init__(self, layers: list[str] | None = None, threshold: int = COMPACT_THRESHOLD):
        self.layers = list(layers or LAYERS)
        self.threshold = threshold
        self._entries: dict[str, list[str]] = {l: [] for l in self.layers}
        self._digests: dict[str, list[str]] = {l: [] for l in self.layers}

    def add(self, layer: str, text: str) -> None:
        if layer not in self._entries:
            raise KeyError(f"неизвестный слой: {layer}")
        self._entries[layer].append(text.strip())
        if len(self._entries[layer]) >= self.threshold:
            self.compact(layer)

    def compact(self, layer: str) -> str:
        """Сворачивает накопленные записи слоя в один конспект и очищает слой."""
        items = self._entries[layer]
        if not items:
            return ""
        digest = f"[summary of {len(items)} items] " + "; ".join(items)
        self._digests[layer].append(digest)
        self._entries[layer] = []
        return digest

    def render(self) -> dict[str, dict]:
        """Возвращает snapshot: слой -> {entries, digests}."""
        return {
            l: {"entries": list(self._entries[l]), "digests": list(self._digests[l])}
            for l in self.layers
        }

    def total_items(self) -> int:
        return sum(len(v) for v in self._entries.values()) + sum(
            len(d) for d in self._digests.values()
        )
