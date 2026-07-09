"""Proof-of-concept generation for Kulibin."""

from __future__ import annotations

from .llm_client import call_llm


def generate_prototype(idea: str, language: str = "python", api_key: str | None = None, learned_context: str = "") -> str | None:
    """Generate an isolated PoC script for an idea."""
    if language not in ("python", "js", "ts"):
        language = "python"
    prompt = f"""You are Kulibin, an engineer. Write a minimal, self-contained
proof-of-concept ({language}) for this idea:

IDEA: {idea}

{learned_context}

Requirements:
- Single file, runnable, minimal dependencies
- Demonstrates the core concept only
- Clean, readable, no comments unless needed
- Return ONLY the code."""
    return call_llm(prompt, max_tokens=1500, temperature=0.2, api_key=api_key)


def benchmark_snippet(code: str, api_key: str | None = None, learned_context: str = "") -> str | None:
    """Suggest a benchmarking approach for a code snippet."""
    prompt = f"""Suggest how to benchmark/measure performance of this code, and
identify the likely bottlenecks:

{code[:3000]}

{learned_context}

Return: measurement approach + expected bottlenecks + quick wins."""
    return call_llm(prompt, max_tokens=1200, temperature=0.2, api_key=api_key)
