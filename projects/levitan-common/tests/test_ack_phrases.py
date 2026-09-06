"""Тесты ES-14: выбор ack-фразы (pre-synth заполнитель)."""

from levitan.ack_phrases import AckAction, AckPhraseSet, select_ack


def test_default_phrase_returned():
    assert select_ack(AckAction.THINKING) in ("Момент", "Секундочку", "Сейчас")


def test_action_specific_phrase():
    assert select_ack(AckAction.SEARCH) in ("Ищу", "Смотрю", "Секунду, проверяю")
    assert select_ack(AckAction.NOTE) in ("Записал", "Принято", "Отметил")


def test_avoid_duplicates_final():
    # Если финал уже содержит ack-фразу, выбираем другую из пула
    out = select_ack(AckAction.THINKING, avoid="Момент, сейчас посмотрю")
    assert out != "Момент"
    assert out in ("Секундочку", "Сейчас")


def test_avoid_exact_match():
    out = select_ack(AckAction.THINKING, avoid="Секундочку")
    assert out != "Секундочку"


def test_no_avoid_returns_first():
    assert select_ack(AckAction.ACK) == "Понял вас"


def test_custom_phrase_set():
    custom = AckPhraseSet(phrases={AckAction.THINKING: ["Ща-ща", "Мигом"], AckAction.ACK: ["Ок"]})
    assert select_ack(AckAction.THINKING, phrases=custom) == "Ща-ща"


def test_unknown_action_falls_back_to_ack():
    assert select_ack(AckAction.REPEAT) in (
        "Повторите, пожалуйста",
        "Простите, не расслышал",
        "Ещё раз, пожалуйста",
    )
