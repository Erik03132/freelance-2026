"""Learning aggregation — turn captured signals into prompt context."""

from __future__ import annotations

import re
from collections import Counter

from .signal import read_signals

STOPWORDS = {
    "the", "a", "an", "of", "to", "and", "or", "for", "in", "on", "with",
    "is", "are", "be", "this", "that", "it", "as", "at", "by", "from", "не",
    "и", "с", "для", "по", "в", "на", "это", "как", "the", "component",
}


def _tokenize(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-zа-яё]+", text.lower()) if w not in STOPWORDS and len(w) > 2]


def build_learned_context(agent: str, min_samples: int = 3) -> str:
    """Aggregate past outcomes into a short context string for prompts.

    Returns empty string when not enough data.
    """
    recs = read_signals(agent)
    starts = {r["sid"]: r for r in recs if r.get("phase") == "start"}
    outcomes = {}
    for r in recs:
        if r.get("phase") == "outcome":
            outcomes[r["sid"]] = r

    judged = [(starts[s], o) for s, o in outcomes.items() if s in starts]
    if len(judged) < min_samples:
        return ""

    total = len(judged)
    accepted = sum(1 for _, o in judged if o["outcome"] == "accepted")
    edited = sum(1 for _, o in judged if o["outcome"] == "edited")
    rejected = sum(1 for _, o in judged if o["outcome"] == "rejected")

    acc_pct = round(100 * accepted / total)
    rej_pct = round(100 * rejected / total)

    # meta preferences (e.g. framework) among accepted
    meta_counter: Counter = Counter()
    for s, _ in judged:
        if _["outcome"] in ("accepted", "edited"):
            for k, v in s.get("meta", {}).items():
                meta_counter[f"{k}={v}"] += 1

    # top keywords in accepted vs rejected specs
    acc_words: Counter = Counter()
    rej_words: Counter = Counter()
    for s, o in judged:
        toks = _tokenize(s.get("spec", ""))
        if o["outcome"] in ("accepted", "edited"):
            acc_words.update(toks)
        elif o["outcome"] == "rejected":
            rej_words.update(toks)

    lines = ["[Learned from past usage]"]
    lines.append(f"- Acceptance rate: {acc_pct}% accepted, {rej_pct}% rejected (n={total})")
    for pref, n in meta_counter.most_common(3):
        if n >= 2:
            lines.append(f"- Users favor {pref} (seen {n}x in accepted)")
    top_acc = [w for w, _ in acc_words.most_common(5)]
    if top_acc:
        lines.append(f"- Common in accepted requests: {', '.join(top_acc)}")
    return "\n".join(lines)
