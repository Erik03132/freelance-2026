"""Smoke tests for prompts module."""

from levitan.prompts import (
    GREETING,
    SYSTEM_PROMPT,
    VOICE_NOT_HEARD,
    CLOSING_INTERESTED,
    CLOSING_NOT_INTERESTED,
    CLOSING_CALLBACK,
    NO_ANSWER_GREETING,
)


def test_greeting_exists():
    assert GREETING
    assert len(GREETING) > 20
    assert "Глобал Филдс" in GREETING


def test_system_prompt_exists():
    assert SYSTEM_PROMPT
    assert len(SYSTEM_PROMPT) > 200
    assert "Иван" in SYSTEM_PROMPT
    assert "Зерновые" in SYSTEM_PROMPT


def test_voice_not_heard():
    assert VOICE_NOT_HEARD
    assert "Не расслышал" in VOICE_NOT_HEARD


def test_closing_interested():
    assert CLOSING_INTERESTED
    assert "менеджер свяжется" in CLOSING_INTERESTED


def test_closing_not_interested():
    assert CLOSING_NOT_INTERESTED
    assert "До свидания" in CLOSING_NOT_INTERESTED


def test_closing_callback():
    assert CLOSING_CALLBACK
    assert "перезвоним" in CLOSING_CALLBACK


def test_no_answer_greeting():
    assert NO_ANSWER_GREETING
    assert NO_ANSWER_GREETING.startswith("Здравствуйте")


def test_all_prompts_are_unique():
    prompts = [
        GREETING,
        VOICE_NOT_HEARD,
        CLOSING_INTERESTED,
        CLOSING_NOT_INTERESTED,
        CLOSING_CALLBACK,
        NO_ANSWER_GREETING,
    ]
    assert len(set(prompts)) == len(prompts)
