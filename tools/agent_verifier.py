"""
AV-1 + AV-3: Независимая верификация (Проверяла) + доказательства в отчётах.

Модуль для системной проверки результатов агентов другой моделью.
"""

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

VERIFICATION_PROMPT = """You are an independent verifier (Проверяла). Your job is NOT to redo the work —
verify whether the agent's output is correct, complete, and backed by evidence.

Input:
{agent_output}

Verification checklist:
1. FACTS: Are all factual claims backed by data, sources, or citations?
2. LOGIC: Is the reasoning chain complete (no gaps)?
3. SPEC: Does the output match what was requested?
4. EVIDENCE: Is every claim accompanied by proof (test output, screenshot ref, curl result, citation)?
5. EDGE CASES: Were edge cases and failure modes considered?

Return a JSON verdict:
{{
  "verdict": "PASS" | "FAIL" | "PASS_WITH_NOTES",
  "confidence": 0.0-1.0,
  "issues": ["issue description"],
  "missing_evidence": ["claim without proof"],
  "suggestions": ["how to fix"]
}}
"""


def verify_agent_output(
    agent_output: str,
    model: str | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    """Прогоняет ответ агента через независимого проверяющего (Tier 2/3)."""

    key = api_key or os.getenv("OPENROUTER_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return {"error": "no_api_key"}

    prompt = VERIFICATION_PROMPT.format(agent_output=agent_output[:8000])

    try:
        import httpx

        resp = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model or "anthropic/claude-sonnet-4-20250514",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "response_format": {"type": "json_object"},
            },
            timeout=120,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        try:
            return json.loads(content.strip().lstrip("```json").rstrip("```"))
        except json.JSONDecodeError:
            return {"verdict": "FAIL", "error": "could_not_parse_verifier_output", "raw": content}
    except Exception as e:
        return {"error": str(e), "verdict": "FAIL"}


class ReopensTracker:
    """AV-2: Считает reopens/приёмку агентских результатов."""

    def __init__(self, log_path: str = "data/agent_reopens.jsonl"):
        self.log_path = log_path
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

    def record_submission(self, agent_id: str, task_id: str, output_checksum: str) -> None:
        with open(self.log_path, "a") as f:
            json.dump(
                {
                    "type": "submission",
                    "agent_id": agent_id,
                    "task_id": task_id,
                    "checksum": output_checksum,
                    "timestamp": __import__("datetime").datetime.now().isoformat(),
                },
                f,
            )
            f.write("\n")

    def record_acceptance(
        self, agent_id: str, task_id: str, accepted: bool, reason: str = ""
    ) -> None:
        with open(self.log_path, "a") as f:
            json.dump(
                {
                    "type": "acceptance",
                    "agent_id": agent_id,
                    "task_id": task_id,
                    "accepted": accepted,
                    "reason": reason,
                    "timestamp": __import__("datetime").datetime.now().isoformat(),
                },
                f,
            )
            f.write("\n")

    def get_reopen_rate(self, agent_id: str = "", days: int = 7) -> float:
        from datetime import datetime, timedelta

        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        first_accepts = {}
        submissions = {}

        if not os.path.exists(self.log_path):
            return 0.0

        with open(self.log_path) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if agent_id and entry.get("agent_id") != agent_id:
                    continue
                if entry.get("timestamp", "") < cutoff:
                    continue
                tid = entry["task_id"]
                if entry["type"] == "submission":
                    submissions[tid] = submissions.get(tid, 0) + 1
                elif entry["type"] == "acceptance":
                    if entry["accepted"] and tid not in first_accepts:
                        first_accepts[tid] = submissions.get(tid, 1)

        total_first = sum(first_accepts.values())
        if total_first == 0:
            return 0.0
        total_submissions = sum(submissions.get(tid, 1) for tid in first_accepts)
        reopens = total_submissions - total_first
        return reopens / max(1, total_submissions)
