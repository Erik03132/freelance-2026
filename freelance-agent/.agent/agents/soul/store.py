"""Soul store — read/write the self-editable agent constitution (soul.md).

Each agent owns a single living markdown file with two zones:

    ## Constitution        <- human-owned: identity, goal, hard rules (never auto-edited)
    ## Evolving Lessons     <- machine-owned: folded from learning + memory
    <!-- SOUL:AUTO:BEGIN -->
    ...auto-managed...
    <!-- SOUL:AUTO:END -->

Pure stdlib, no deps. Inspired by Shen Shon Chen's "soul.md governs everything".
"""

from __future__ import annotations

import os

SOUL_DIR = os.path.dirname(os.path.abspath(__file__))

AUTO_BEGIN = "<!-- SOUL:AUTO:BEGIN -->"
AUTO_END = "<!-- SOUL:AUTO:END -->"


def soul_path(agent: str) -> str:
    os.makedirs(SOUL_DIR, exist_ok=True)
    return os.path.join(SOUL_DIR, f"{agent}.soul.md")


def read(agent: str) -> str:
    path = soul_path(agent)
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(agent: str, text: str) -> str:
    path = soul_path(agent)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def scaffold(name: str, role: str) -> str:
    """Return an initial soul.md body with both zones."""
    return (
        f"# {name} — Soul\n\n"
        f"## Constitution\n"
        f"> Human-owned. The unchanging identity & hard rules of this agent.\n\n"
        f"**Role:** {role}\n\n"
        f"**Hard rules:**\n"
        f"- (define non-negotiables here)\n\n"
        f"## Evolving Lessons\n"
        f"> Machine-owned. Auto-folded from usage signals + memory. Do not edit by hand.\n\n"
        f"{AUTO_BEGIN}\n"
        f"_(no lessons yet)_\n"
        f"{AUTO_END}\n"
    )


def replace_auto_zone(text: str, lessons: str) -> str:
    """Replace content between AUTO markers with `lessons`. Appends zone if absent."""
    block = f"{AUTO_BEGIN}\n{lessons.strip()}\n{AUTO_END}"
    if AUTO_BEGIN in text and AUTO_END in text:
        head = text.split(AUTO_BEGIN)[0]
        tail = text.split(AUTO_END, 1)[1]
        return head + block + tail
    sep = "" if text.endswith("\n") else "\n"
    return text + sep + "\n## Evolving Lessons\n\n" + block + "\n"
