"""Tests for the self-healing generation loop (Chen mechanic #4 + #3).

detect error -> patch prompt -> re-run -> self-terminate on success or budget.
"""

import os
import sys

_AGENTS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _AGENTS not in sys.path:
    sys.path.insert(0, _AGENTS)

import healing  # noqa: E402


def test_first_try_success_no_retry():
    calls = []

    def gen(prompt):
        calls.append(prompt)
        return "good output"

    def validate(out):
        return []  # no issues

    result = healing.run_with_healing("base", gen, validate, max_retries=3)
    assert result.output == "good output"
    assert result.ok is True
    assert result.attempts == 1
    assert len(calls) == 1


def test_heals_then_succeeds():
    prompts = []

    def gen(prompt):
        prompts.append(prompt)
        # fail on first attempt, succeed once prompt was corrected
        return "bad" if len(prompts) == 1 else "fixed"

    def validate(out):
        return ["missing X"] if out == "bad" else []

    result = healing.run_with_healing("base", gen, validate, max_retries=3)
    assert result.ok is True
    assert result.attempts == 2
    # second prompt must contain the corrective directive
    assert "missing X" in prompts[1]
    assert "base" in prompts[1]


def test_gives_up_after_budget():
    def gen(prompt):
        return "always bad"

    def validate(out):
        return ["still broken"]

    result = healing.run_with_healing("base", gen, validate, max_retries=2)
    assert result.ok is False
    assert result.attempts == 3  # initial + 2 retries
    assert result.issues == ["still broken"]


def test_heal_prompt_appends_directives():
    healed = healing.heal_prompt("do the thing", ["no title", "bad contrast"])
    assert "do the thing" in healed
    assert "no title" in healed
    assert "bad contrast" in healed


def test_heal_prompt_empty_issues_returns_original():
    assert healing.heal_prompt("p", []) == "p"


def test_none_output_treated_as_failure():
    def gen(prompt):
        return None

    def validate(out):
        return ["empty"] if not out else []

    result = healing.run_with_healing("base", gen, validate, max_retries=1)
    assert result.ok is False
    assert result.attempts == 2


def test_validator_exception_is_contained():
    def gen(prompt):
        return "x"

    def validate(out):
        raise ValueError("boom")

    result = healing.run_with_healing("base", gen, validate, max_retries=1)
    # validator failure should not crash the loop; treated as a healable issue
    assert result.ok is False
