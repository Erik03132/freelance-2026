"""Memory Tree package. Importable: `from memory import remember, recall`."""

from .store import recall, remember


def enrich_context(agent: str, query: str, ctx: str = "", top_k: int = 2) -> str:
    """Merge memory recall into the learned context string."""
    try:
        mem = recall(agent, query, top_k=top_k)
        mem_ctx = ""
        if mem:
            mem_ctx = "\n".join(f"- {m['fact']}" for m in mem if isinstance(m, dict))
        if mem_ctx and ctx:
            return "Previous patterns:\n" + mem_ctx + "\n" + ctx
        if mem_ctx:
            return "Previously you did:\n" + mem_ctx
    except Exception:
        pass
    return ctx


__all__ = ["remember", "recall", "enrich_context"]
