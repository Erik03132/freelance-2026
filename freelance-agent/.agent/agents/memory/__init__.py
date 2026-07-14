"""Memory Tree package. Importable: `from memory import remember, recall`."""

from .store import compact, recall, recall_scored, remember


def enrich_context(agent: str, query: str, ctx: str = "", top_k: int = 2) -> str:
    """Merge smart-RAG memory recall (top-K) into the learned context string."""
    try:
        hits = recall_scored(agent, query, top_k=top_k)
        mem_ctx = "\n".join(f"- {h.get('fact', '')}" for h in hits if h.get("fact"))
        if mem_ctx and ctx:
            return "Previous patterns:\n" + mem_ctx + "\n" + ctx
        if mem_ctx:
            return "Previously you did:\n" + mem_ctx
    except Exception:
        pass
    return ctx


__all__ = ["remember", "recall", "recall_scored", "enrich_context", "compact"]
