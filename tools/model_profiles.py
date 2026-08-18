#!/usr/bin/env python3
"""BK-4 — Per-task model profiles с cross-agent фолбэком (урок BookTrans, Habr #1070088).

BookTrans назначает модели НА ЗАДАЧУ (translator/editor/scout/formatter lists),
а не глобальный каскад. Здесь формализуем это как слой профилей поверх
DSH-1 seam + нашего FREE_MODELS cascade: каждая задача получает упорядоченный
список моделей; выбирается первая доступная (fallback вниз по списку).

Использование:
    from tools.model_profiles import select_model, MODEL_PROFILES
    model = select_model("translate", available={"deepseek/deepseek-chat", "openrouter/.../llama-3.3-70b"})

Офлайн: `python3 tools/tests/eval_model_profiles.py` (deterministic, для eval_gate).
"""

from __future__ import annotations

import os

# Per-task профили: задача -> упорядоченный список моделей [primary, fallback, ...].
# Имена моделей совместимы с OmniRoute/OpenRouter (DSH-1 seam).
MODEL_PROFILES: dict[str, list[str]] = {
    "translate": [
        "deepseek/deepseek-chat",
        "openrouter/google/gemini-flash-1.5",
        "openrouter/meta-llama/llama-3.3-70b-instruct",
    ],
    "edit": [
        "anthropic/claude-sonnet-4-20250514",
        "deepseek/deepseek-chat",
        "openrouter/google/gemini-flash-1.5",
    ],
    "scout": [
        "openrouter/perplexity/sonar",
        "openrouter/google/gemini-flash-1.5",
        "deepseek/deepseek-chat",
    ],
    "format": [
        "deepseek/deepseek-chat",
        "openrouter/meta-llama/llama-3.3-70b-instruct",
    ],
    "reason": [
        "anthropic/claude-opus-4-8",
        "anthropic/claude-sonnet-4-20250514",
        "deepseek/deepseek-chat",
    ],
}

# Глобальный фолбэк, если задача не описана профилем (FREE_MODELS cascade tail).
GLOBAL_FALLBACK = ["deepseek/deepseek-chat", "openrouter/meta-llama/llama-3.3-70b-instruct"]


def _available_set() -> set[str]:
    """Множество доступных моделей: из ENV (через запятую) или пусто (всё доступно)."""
    raw = os.environ.get("AVAILABLE_MODELS", "")
    if not raw.strip():
        return set()  # пусто = все доступны (offline-дружелюбно)
    return {m.strip() for m in raw.split(",") if m.strip()}


def select_model(task_type: str, available: set[str] | None = None) -> str | None:
    """Возвращает первую доступную модель профиля задачи (fallback вниз).

    available=None → считаем доступными все (offline-режим).
    Если ни одна из профиля не доступна → GLOBAL_FALLBACK.
    Если и там нет → None (задача не может быть решена текущим пулом).
    """
    if available is None:
        available = _available_set()
    all_available = len(available) == 0
    profile = MODEL_PROFILES.get(task_type, GLOBAL_FALLBACK)
    for model in profile:
        if all_available or model in available:
            return model
    for model in GLOBAL_FALLBACK:
        if all_available or model in available:
            return model
    return None


def select_chain(task_type: str, available: set[str] | None = None) -> list[str]:
    """Полная цепочка фолбэка для задачи (профиль + глобальный хвост, без дублей)."""
    if available is None:
        available = _available_set()
    all_available = len(available) == 0
    chain = list(MODEL_PROFILES.get(task_type, []))
    for m in GLOBAL_FALLBACK:
        if m not in chain:
            chain.append(m)
    if all_available:
        return chain
    return [m for m in chain if m in available]
