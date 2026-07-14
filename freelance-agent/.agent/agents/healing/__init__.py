"""Self-healing generation loop (Shen Shon Chen mechanics #4 + #3).

detect error -> patch the prompt with corrective directives -> re-run ->
self-terminate on success OR when the retry budget is spent.

Pure stdlib, no deps, no network. Callers inject `generate` and `validate`
callbacks, so this is fully testable and reusable across every agent.

    from healing import run_with_healing
    res = run_with_healing(prompt, gen_fn, validate_fn, max_retries=2)
    if res.ok: use(res.output)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

__all__ = ["run_with_healing", "heal_prompt", "HealResult"]


@dataclass
class HealResult:
    output: Optional[str]
    ok: bool
    attempts: int
    issues: List[str] = field(default_factory=list)


def heal_prompt(prompt: str, issues: List[str]) -> str:
    """Augment a prompt with corrective directives derived from validation issues."""
    if not issues:
        return prompt
    directives = "\n".join(f"- {i}" for i in issues)
    return (
        f"{prompt}\n\n"
        f"[SELF-CORRECTION] The previous attempt failed these checks. "
        f"Fix ALL of them this time:\n{directives}"
    )


def _safe_validate(validate: Callable[[Optional[str]], List[str]], out: Optional[str]) -> List[str]:
    try:
        return list(validate(out) or [])
    except Exception as e:  # validator crash = a healable signal, never a hard crash
        return [f"validator error: {e}"]


def run_with_healing(
    prompt: str,
    generate: Callable[[str], Optional[str]],
    validate: Callable[[Optional[str]], List[str]],
    max_retries: int = 2,
) -> HealResult:
    """Run generate->validate, healing the prompt between attempts.

    Args:
        prompt: initial prompt.
        generate: fn(prompt) -> output (or None).
        validate: fn(output) -> list of issue strings ([] means valid).
        max_retries: extra attempts after the first (total = 1 + max_retries).

    Returns a HealResult; self-terminates on first clean validation.
    """
    current = prompt
    issues: List[str] = []
    attempts = 0
    for _ in range(max_retries + 1):
        attempts += 1
        out = generate(current)
        issues = _safe_validate(validate, out)
        if not issues:
            return HealResult(output=out, ok=True, attempts=attempts, issues=[])
        current = heal_prompt(prompt, issues)
    return HealResult(output=out, ok=False, attempts=attempts, issues=issues)
