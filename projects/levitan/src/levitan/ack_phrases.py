"""Фразы-заполнители (pre-synth ack) — ES-14.

Контекст (docs/cases/voice-live-pace.md, ES-14): после того как клиент закончил
говорить, LLM-ответ и его TTS-синтез занимают время. Оператор воспринимает эту
паузу как "робот завис" и тянется к аварийному стопу. Решение — проиграть
заранее синтезированную короткую ack-фразу ("момент / секундочку / ищу") сразу
после речи клиента, до начала LLM-стрима.

Этот модуль — чистая логика выбора ack-фразы по действию (без аудио/Mango/TTS).
Само проигрывание вшивается в call_session.process_client_audio (см. ниже).

Правила из one-pager:
- дифференцировать под действие (повтор/поиск/уточнение/получение);
- НЕ дублировать формулировку финального ответа (иначе звучит как эхо).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class AckAction(StrEnum):
    """Смысл действия, под который подбираем ack-фразу."""

    THINKING = "thinking"  # обдумываем / ищем ответ
    SEARCH = "search"  # ищем в базе/системе
    CLARIFY = "clarify"  # уточняем деталь
    REPEAT = "repeat"  # переспрашиваем (barge-in / не расслышали)
    NOTE = "note"  # фиксируем информацию
    ACK = "ack"  # дефолтное "принял"


# Базовый пул ack-фраз (без точек/длинных конструкций — проигрываются мгновенно).
DEFAULT_PHRASES = {
    AckAction.THINKING: ["Момент", "Секундочку", "Сейчас"],
    AckAction.SEARCH: ["Ищу", "Смотрю", "Секунду, проверяю"],
    AckAction.CLARIFY: ["Уточню", "Переспрошу", "Так, деталь"],
    AckAction.REPEAT: ["Повторите, пожалуйста", "Простите, не расслышал", "Ещё раз, пожалуйста"],
    AckAction.NOTE: ["Записал", "Принято", "Отметил"],
    AckAction.ACK: ["Понял вас", "Хорошо", "Да-да"],
}


@dataclass
class AckPhraseSet:
    """Набор ack-фраз. Расширяем/переопределяем без правки движка."""

    phrases: dict = field(default_factory=lambda: dict(DEFAULT_PHRASES))


def select_ack(
    action: AckAction, phrases: AckPhraseSet | None = None, *, avoid: str | None = None
) -> str:
    """Выбрать ack-фразу под действие.

    Args:
        action: тип действия.
        phrases: пул фраз (по умолчанию DEFAULT_PHRASES).
        avoid: финальная фраза агента — если ack её дублирует (по нормализации),
            берём другую из пула, чтобы не звучало как эхо.

    Returns:
        Текст ack-фразы (без точки на конце в пуле).
    """
    pool = (phrases or AckPhraseSet()).phrases
    candidates = pool.get(action, pool[AckAction.ACK])

    if avoid:
        avoid_n = _norm(avoid)
        # Попробать найти фразу, не дублирующую финал
        for cand in candidates:
            if _norm(cand) and _norm(cand) not in avoid_n:
                return cand
    return candidates[0]


def _norm(text: str) -> str:
    import re

    return re.sub(r"[^\wа-яё]+", " ", text.lower()).strip()
