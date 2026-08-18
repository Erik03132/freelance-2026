"""Eval for RAG-1/RAG-2/RAG-5 retrieval + reranker (Habr #1070662) — offline.

Запуск: python3 tools/tests/eval_rag_retrieval.py
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.rag_retrieval import (  # noqa: E402
    VectorStore,
    embed_query,
    embed_document,
    rerank,
    rag_retrieve,
    build_prompt,
    QUERY_PREFIX,
    DOC_PREFIX,
)


def _run() -> tuple[int, list[str]]:
    fails: list[str] = []

    # детерминированный fake-embedder: вектор из первых 3 "слов"-чисел (для тестов)
    def embed_fn(text: str) -> list[float]:
        # префикс игнорируем для самой логики; важен сам факт наличия префикса (RAG-2)
        nums = [float(t) for t in text.replace(",", " ").split() if t.replace(".", "", 1).isdigit()]
        vec = nums[:3] + [0.0] * (3 - len(nums[:3]))
        return vec

    # TP-1: search возвращает ближайший по cosine первым
    store = VectorStore()
    store.add("a 1 0 0", [1.0, 0.0, 0.0])
    store.add("b 0 1 0", [0.0, 1.0, 0.0])
    store.add("c 0 0 1", [0.0, 0.0, 1.0])
    res = store.search([0.9, 0.1, 0.0], top_k=1)
    if res[0]["text"] != "a 1 0 0":
        fails.append(f"TP-1: search должен вернуть ближайший 'a', получили {res[0]['text']}")

    # TP-2: metadata filter исключает несовпадающие
    store2 = VectorStore()
    store2.add("x", [1.0, 0.0, 0.0], {"lang": "ru"})
    store2.add("y", [1.0, 0.0, 0.0], {"lang": "en"})
    r = store2.search([1.0, 0.0, 0.0], top_k=5, filter_metadata={"lang": "ru"})
    if len(r) != 1 or r[0]["text"] != "x":
        fails.append(f"TP-2: metadata filter должен дать только 'x', получили {r}")

    # TP-3: rerank переупорядочивает кандидатов
    def reranker_fn(q, text):
        # cross-encoder: документ 'b' релевантнее 'a' вопреки cosine-порядку
        return 1.0 if text == "b" else 0.2

    cands = [
        {"text": "a", "score": 0.9, "metadata": {}},
        {"text": "b", "score": 0.5, "metadata": {}},
    ]
    out = rerank("q", cands, reranker_fn, top_k=2)
    if out[0]["text"] != "b":
        fails.append(f"TP-3: rerank должен поднять 'b' наверх, получили {out[0]['text']}")

    # TP-4: rag_retrieve возвращает <= top_k_final и применяет rerank
    store3 = VectorStore()
    store3.add("a", [1.0, 0.0, 0.0], {})
    store3.add("b", [0.8, 0.6, 0.0], {})
    store3.add("c", [0.0, 0.0, 1.0], {})
    hits = rag_retrieve(store3, "1 0 0", embed_fn, reranker_fn, top_k_retrieve=50, top_k_final=1)
    if len(hits) != 1 or hits[0]["text"] != "b":
        fails.append(f"TP-4: rag_retrieve должен вернуть rerank-'b', получили {hits}")

    # TP-5: пустой store → []
    if rag_retrieve(VectorStore(), "q", embed_fn, reranker_fn) != []:
        fails.append("TP-5: пустой store должен дать []")

    # TP-6 (RAG-2): асимметричные префиксы — embed_fn получает префиксованный текст
    seen = {}

    def spy(text: str) -> list[float]:
        seen["last"] = text
        return [0.0, 0.0, 0.0]

    embed_query("q", spy)
    if not seen["last"].startswith(QUERY_PREFIX):
        fails.append(f"TP-6: embed_query должен добавлять '{QUERY_PREFIX}', получили {seen['last']!r}")
    embed_document("d", spy)
    if not seen["last"].startswith(DOC_PREFIX):
        fails.append(f"TP-6: embed_document должен добавлять '{DOC_PREFIX}', получили {seen['last']!r}")

    # TP-7 (RAG-5): build_prompt содержит grounding + контекст + вопрос
    p = build_prompt("Вопрос?", ["кусок1", "кусок2"])
    if "опираясь ТОЛЬКО на приведённый контекст" not in p:
        fails.append("TP-7: build_prompt без инструкции заземления")
    if "Вопрос?" not in p or "кусок1" not in p:
        fails.append("TP-7: build_prompt без вопроса/контекста")

    return len(fails), fails


if __name__ == "__main__":
    n, fails = _run()
    if fails:
        print(f"❌ EVAL FAILED ({n}):")
        for f in fails:
            print(f"  - {f}")
        sys.exit(1)
    print("✅ EVAL PASSED — RAG-1 retrieval+reranker, RAG-2 prefixes, RAG-5 grounding OK")
