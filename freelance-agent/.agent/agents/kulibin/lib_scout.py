"""Library scouting for Kulibin — LLM-powered recommendations."""

from __future__ import annotations

from .llm_client import call_llm
from .perf_config import EVAL_CRITERIA


def scout(task: str, context: str = "Astro/React/Python projects", api_key: str | None = None, learned_context: str = "") -> str | None:
    """Recommend libraries/tools for a given task."""
    criteria = "\n".join(f"- {c}" for c in EVAL_CRITERIA)
    prompt = f"""You are Kulibin, an engineering library scout. Find the best open-source
libraries/tools to solve this task:

TASK: {task}
CONTEXT: {context}

{learned_context}

For each recommendation provide:
- Name + repo URL
- What problem it solves
- Size / bundle impact (estimate)
- Maturity (stars, maintenance)
- Why it fits our stack
- Risks / alternatives

Evaluation criteria:
{criteria}

Return a ranked markdown list (top 3-5)."""
    return call_llm(prompt, max_tokens=2000, temperature=0.3, api_key=api_key)


def evaluate(library: str, api_key: str | None = None, learned_context: str = "") -> str | None:
    """Evaluate a specific library against our criteria."""
    criteria = "\n".join(f"- {c}" for c in EVAL_CRITERIA)
    prompt = f"""Evaluate the library "{library}" for our stack (Astro/React/Python).

{learned_context}

Assess against:
{criteria}

Return: verdict (adopt/trial/avoid), pros, cons, integration effort, alternatives."""
    return call_llm(prompt, max_tokens=1500, temperature=0.2, api_key=api_key)
