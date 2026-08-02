"""AI-Defender — LLM deep audit (OWASP + agentic/MCP focus).

Uses shared `llm` package from freelance-agent (OpenRouter) with graceful fallback.
"""

from __future__ import annotations

import os

try:
    from llm import call_llm
except ImportError:  # noqa: F811

    def call_llm(*args, **kwargs) -> str | None:
        return None


AUDIT_FRAMES = {
    "owasp": """You are a senior application security engineer. Review the code below against
OWASP Top 10. Report ONLY issues that are real and reachable. For each: file:line,
severity (CRITICAL/HIGH/MEDIUM/LOW), what it is, and a concrete minimal fix.
Do NOT inflate severity. Skip theoretical issues. Rank by severity.

{code}

{context}

Return a ranked markdown report. If nothing is wrong, say "No critical findings.""" ,
    "mcp": """You are an AI-agent security specialist. The code below is an agent system:
MCP server handlers, tool registration, config, or agent prompts. Audit for:
1) Prompt injection vectors (untrusted input reaching the LLM/system prompt or tool args),
2) MCP tools with overly broad permissions / missing validation,
3) Secrets in configs/logs,
4) Missing output validation of LLM responses (tool misuse from hallucinated args),
5) Path traversal / unsafe file access in tools.
For each: file:line, severity, risk, fix. Do not inflate severity.

{code}

{context}

Return a ranked markdown report. If nothing is wrong, say "No critical findings.""",
}

MAX_FILES = 6
MAX_CHARS_PER_FILE = 2000


def _iter_files(path: str) -> list[str]:
    if os.path.isfile(path):
        return [path]
    exts = {".py", ".js", ".ts", ".tsx", ".json", ".jsonc", ".yaml", ".yml", ".md"}
    out = []
    for root, _dirs, files in os.walk(path):
        if ".git" in root.split(os.sep) or "node_modules" in root.split(os.sep):
            continue
        for f in files:
            if os.path.splitext(f)[1] in exts:
                out.append(os.path.join(root, f))
    return out[:MAX_FILES]


def _collect_snippets(path: str) -> str:
    files = _iter_files(path)
    snippets = []
    for fp in files:
        try:
            with open(fp, encoding="utf-8", errors="replace") as f:
                body = f.read()
        except OSError:
            continue
        if "node_modules" in fp or ".min.js" in fp:
            continue
        snippets.append(f"# {fp}\n{body[:MAX_CHARS_PER_FILE]}")
    return "\n\n".join(snippets)


def deep_audit(
    path: str,
    frame: str = "owasp",
    context: str = "",
    api_key: str | None = None,
) -> str | None:
    """LLM deep audit. frame: 'owasp' | 'mcp'. Returns markdown or None."""
    code = _collect_snippets(path)
    if not code.strip():
        return None
    prompt = AUDIT_FRAMES.get(frame, AUDIT_FRAMES["owasp"]).format(
        code=code, context=context
    )
    return call_llm(prompt, max_tokens=2600, temperature=0.2, api_key=api_key)
