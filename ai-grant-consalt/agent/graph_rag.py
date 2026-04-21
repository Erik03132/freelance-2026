"""
Graph RAG Engine — Графовый поиск по нормативным документам.

Принцип из статьи Habr: когда найден релевантный узел,
система подтягивает ВСЕ обязательные связанные нормы.

Архитектура:
1. Keyword matching → находим стартовый узел
2. Graph traversal → подтягиваем связанные узлы (1-2 уровня)
3. Term resolution → подставляем определения терминов
4. Context builder → собираем структурированный контекст для LLM
"""
import os
import json
from difflib import SequenceMatcher

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH_PATH = os.path.join(BASE_DIR, 'data', 'legal_graph.json')


class LegalGraph:
    def __init__(self):
        self.nodes = {}
        self.terms = {}
        self._load_graph()

    def _load_graph(self):
        if not os.path.exists(GRAPH_PATH):
            print(f"⚠️ Legal Graph не найден: {GRAPH_PATH}")
            return
        with open(GRAPH_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.nodes = data.get("nodes", {})
        self.terms = data.get("terms", {})
        print(f"✅ Legal Graph загружен: {len(self.nodes)} узлов, {len(self.terms)} терминов")

    def _keyword_score(self, query: str, node: dict) -> float:
        """Скоринг узла по ключевым словам + fuzzy match по title."""
        q_lower = query.lower()
        q_words = set(q_lower.split())

        score = 0.0

        # 1. Точное совпадение ключевых слов (самый сильный сигнал)
        keywords = node.get("keywords", [])
        for kw in keywords:
            if kw.lower() in q_lower:
                score += 2.0
            # Частичное совпадение слов
            kw_words = set(kw.lower().split())
            overlap = len(q_words & kw_words)
            if overlap > 0:
                score += overlap * 0.5

        # 2. Fuzzy match по заголовку
        title_sim = SequenceMatcher(None, q_lower, node.get("title", "").lower()).ratio()
        score += title_sim * 1.5

        # 3. Совпадение по типу документа
        doc = node.get("document", "").lower()
        if doc and any(d in q_lower for d in doc.split()):
            score += 1.0

        return score

    def _resolve_terms(self, query: str) -> list:
        """Находит термины, использованные в запросе, и возвращает их определения."""
        q_lower = query.lower()
        resolved = []
        for term, definition in self.terms.items():
            if term.lower() in q_lower:
                resolved.append(f"📖 {term}: {definition}")
        return resolved

    def search(self, query: str, max_depth: int = 2, top_k: int = 3) -> dict:
        """
        Графовый поиск: keyword match → graph traversal → context assembly.
        
        Returns:
            {
                "primary_nodes": [...],   # Прямые совпадения
                "linked_nodes": [...],    # Связанные нормы
                "terms": [...],           # Определения терминов
                "context_block": str      # Готовый контекст для LLM
            }
        """
        if not self.nodes:
            return {"primary_nodes": [], "linked_nodes": [], "terms": [], "context_block": ""}

        # 1. Скоринг всех узлов
        scored = []
        for node_id, node in self.nodes.items():
            score = self._keyword_score(query, node)
            if score > 0.5:  # Порог отсечения
                scored.append((node_id, node, score))

        scored.sort(key=lambda x: x[2], reverse=True)
        primary = scored[:top_k]

        # 2. Graph traversal — подтягиваем связанные узлы
        visited = set()
        linked = []

        def traverse(node_id, depth):
            if depth > max_depth or node_id in visited:
                return
            visited.add(node_id)
            node = self.nodes.get(node_id)
            if not node:
                return
            for link_id in node.get("links", []):
                if link_id not in visited and link_id in self.nodes:
                    linked_node = self.nodes[link_id]
                    linked.append((link_id, linked_node))
                    if depth < max_depth:
                        traverse(link_id, depth + 1)

        for node_id, node, score in primary:
            traverse(node_id, 0)

        # Убираем из linked те, что уже в primary
        primary_ids = {nid for nid, _, _ in primary}
        linked = [(nid, n) for nid, n in linked if nid not in primary_ids]

        # 3. Term resolution
        terms = self._resolve_terms(query)

        # 4. Context builder — форматируем для LLM
        context_parts = []

        if primary:
            context_parts.append("📌 ПРЯМЫЕ СОВПАДЕНИЯ (нормативные акты по теме):")
            for node_id, node, score in primary:
                context_parts.append(
                    f"  ▪ [{node['title']}] ({node.get('document', '')})\n"
                    f"    {node['text']}"
                )

        if linked:
            context_parts.append("\n🔗 СВЯЗАННЫЕ НОРМЫ (обязательный контекст):")
            for node_id, node in linked[:5]:  # Ограничиваем до 5 связанных
                context_parts.append(
                    f"  ▪ [{node['title']}] ({node.get('document', '')})\n"
                    f"    {node['text']}"
                )

        if terms:
            context_parts.append("\n📖 ТЕРМИНОЛОГИЯ:")
            context_parts.extend(terms)

        context_block = "\n".join(context_parts) if context_parts else ""

        return {
            "primary_nodes": [(nid, n["title"], s) for nid, n, s in primary],
            "linked_nodes": [(nid, n["title"]) for nid, n in linked[:5]],
            "terms": terms,
            "context_block": context_block,
            "total_nodes": len(primary) + len(linked)
        }

    def get_citation_chain(self, node_id: str) -> list:
        """Получить цепочку цитирования от конкретного узла."""
        chain = []
        visited = set()

        def walk(nid, depth=0):
            if nid in visited or depth > 3 or nid not in self.nodes:
                return
            visited.add(nid)
            node = self.nodes[nid]
            chain.append({
                "depth": depth,
                "id": nid,
                "title": node["title"],
                "document": node.get("document", ""),
                "text": node["text"][:200]
            })
            for link_id in node.get("links", []):
                walk(link_id, depth + 1)

        walk(node_id)
        return chain


# Singleton
_graph = None

def get_legal_graph() -> LegalGraph:
    global _graph
    if _graph is None:
        _graph = LegalGraph()
    return _graph


if __name__ == "__main__":
    graph = get_legal_graph()

    # Тест 1: Налоговые льготы ИТ
    print("\n" + "="*60)
    print("Тест 1: Налоговые льготы для ИТ")
    result = graph.search("Какие льготы по налогу на прибыль для ИТ-компаний?")
    print(f"Primary: {result['primary_nodes']}")
    print(f"Linked:  {result['linked_nodes']}")
    print(f"Terms:   {result['terms']}")
    print(f"\nContext:\n{result['context_block']}")

    # Тест 2: Банкротство
    print("\n" + "="*60)
    print("Тест 2: Субсидиарная ответственность")
    result = graph.search("Какие риски субсидиарной ответственности для директора при банкротстве ООО?")
    print(f"Primary: {result['primary_nodes']}")
    print(f"Linked:  {result['linked_nodes']}")
    print(f"\nContext:\n{result['context_block']}")

    # Тест 3: Гранты ФСИ
    print("\n" + "="*60)
    print("Тест 3: Грант Старт-1 ФСИ")
    result = graph.search("Как получить грант Старт-1 от ФСИ?")
    print(f"Primary: {result['primary_nodes']}")
    print(f"Linked:  {result['linked_nodes']}")
    print(f"\nContext:\n{result['context_block']}")
