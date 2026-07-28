"""
Agent-Lab Eval Suite — evaluates CoreAgent (Igor'ek) capabilities.
Tests: LLM cascade, tools, memory, hints, permissions, RAG.
"""
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core_agent import CoreAgent, PersistentMemory
from llm_engine import OPENROUTER_MODELS
from tools import CORE_TOOLS, EXTENDED_TOOLS


class EvalSuite:
    def __init__(self):
        self.tests = []
        self.passed = 0
        self.failed = 0

    def add(self, name: str, category: str, cap: bool, fn):
        self.tests.append((name, category, cap, fn))

    def run(self, filter_cat: str = None):
        for name, cat, cap, fn in self.tests:
            if filter_cat and cat != filter_cat:
                continue
            try:
                fn()
                tag = "✅" if cap else "🟢"
                print(f"  {tag} [{cat}] {name}")
                self.passed += 1
            except AssertionError as e:
                print(f"  ❌ [{cat}] {name}: {e}")
                self.failed += 1
            except Exception as e:
                print(f"  💥 [{cat}] {name}: {type(e).__name__}: {e}")
                self.failed += 1

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'─'*60}")
        print(f"  Results: {self.passed}/{total} passed")
        if total:
            print(f"  Score: {self.passed/total*100:.0f}%")
        return self.failed == 0


def build_suite() -> EvalSuite:
    suite = EvalSuite()

    # LLM CASCADE
    def test_cascade_levels():
        assert len(OPENROUTER_MODELS) >= 3, f"Expected ≥3 cascade levels, got {len(OPENROUTER_MODELS)}"

    suite.add("LLM cascade has ≥3 levels", "cascade", False, test_cascade_levels)

    def test_cascade_first_model():
        assert OPENROUTER_MODELS[0].startswith("openrouter/")

    suite.add("Cascade first is OpenRouter model", "cascade", False, test_cascade_first_model)

    # TOOLS
    def test_tools_count():
        # CoreAgent adds 1 memory tool internally
        assert len(EXTENDED_TOOLS) >= 5, f"Expected ≥5 base tools, got {len(EXTENDED_TOOLS)}"

    suite.add("Base tools count ≥5", "tools", False, test_tools_count)

    def test_required_tools():
        tool_names = {t.name for t in EXTENDED_TOOLS}
        required = {"get_current_time", "calculate", "search_knowledge", "web_search", "execute_code_in_sandbox"}
        for r in required:
            assert r in tool_names, f"Missing required tool: {r}"

    suite.add("Required tools present", "tools", False, test_required_tools)

    # CORE AGENT INIT
    def test_agent_init():
        agent = CoreAgent(name="Test", tools=EXTENDED_TOOLS)
        assert agent.name == "Test"
        assert len(agent.tools) >= len(EXTENDED_TOOLS)  # +1 memory tool
        assert agent.memory is not None
        assert agent.hints is not None
        assert agent.rag is not None
        assert agent.permission in ("advisory", "assisted", "autonomous")

    suite.add("CoreAgent initializes correctly", "agent", False, test_agent_init)

    def test_agent_permission_levels():
        for level in ("advisory", "assisted", "autonomous"):
            agent = CoreAgent(name="Test", tools=[], permission=level)
            assert agent.permission == level

    suite.add("Permission levels accepted", "permissions", False, test_agent_permission_levels)

    # PERSISTENT MEMORY
    def test_persistent_memory():
        mem = PersistentMemory("/tmp/test_eval_memory.json")
        initial = len(mem.recall())
        mem.remember("test_fact", "test_category")
        assert len(mem.recall()) == initial + 1
        facts = mem.recall("test_fact")
        assert any("test_fact" in f for f in facts)

    suite.add("PersistentMemory remember/recall", "memory", False, test_persistent_memory)

    # HINTS
    def test_hints_load():
        agent = CoreAgent(name="TestHints", tools=[])
        assert hasattr(agent.hints, 'hints_text')

    suite.add("Hints system loads", "hints", False, test_hints_load)

    # CALCULATION
    def test_calculator():
        calc_tool = next((t for t in EXTENDED_TOOLS if t.name == "calculate"), None)
        assert calc_tool, "calculate tool missing"
        result = calc_tool.invoke({"expression": "200 * 90 + 150 * 250"})
        assert "55500" in result, f"Calc failed: {result}"

    suite.add("Calculator works", "calc", False, test_calculator)

    # SEARCH
    def test_tavily_search():
        if not os.getenv("TAVILY_API_KEY"):
            print("  ⚠ [search] Skipping Tavily (no TAVILY_API_KEY)")
            return
        ws_tool = next((t for t in EXTENDED_TOOLS if t.name == "web_search"), None)
        assert ws_tool
        result = ws_tool.invoke({"query": "Python asyncio tutorial"})
        assert result
        assert len(result) > 50

    suite.add("Tavily search returns results", "search", True, test_tavily_search)

    def test_duckduckgo_fallback():
        ws_tool = next((t for t in EXTENDED_TOOLS if t.name == "web_search"), None)
        assert ws_tool
        old_key = os.environ.pop("TAVILY_API_KEY", "")
        try:
            result = ws_tool.invoke({"query": "Python programming"})
            assert result
        finally:
            if old_key:
                os.environ["TAVILY_API_KEY"] = old_key

    suite.add("DuckDuckGo fallback works", "search", True, test_duckduckgo_fallback)

    # SANDBOX
    def test_sandbox_tool():
        assert any(t.name == "execute_code_in_sandbox" for t in EXTENDED_TOOLS)

    suite.add("Sandbox tool available", "web", True, test_sandbox_tool)

    # RAG
    def test_knowledge_base_tool():
        agent = CoreAgent(name="TestRAG", tools=EXTENDED_TOOLS)
        kb_tool = next((t for t in agent.tools if t.name == "search_knowledge"), None)
        assert kb_tool is not None, "knowledge_base tool missing"

    suite.add("Knowledge base tool available", "rag", True, test_knowledge_base_tool)

    # INTEGRATION
    async def test_agent_simple_response():
        if not os.getenv("OPENROUTER_API_KEY") and not os.getenv("GEMINI_API_KEY"):
            print("  ⚠ [integration] Skipping (no LLM API key)")
            return
        agent = CoreAgent(name="Игорёк", tools=EXTENDED_TOOLS)
        await agent.run("Привет! Кто ты?")

    suite.add("Agent runs without crash", "integration", True,
              lambda: asyncio.run(test_agent_simple_response()))

    return suite


if __name__ == "__main__":
    filter_cat = None
    if len(sys.argv) > 1:
        arg = sys.argv[1].lstrip("--")
        if arg in ("cascade", "tools", "agent", "memory", "hints", "permissions", "calc", "search", "web", "rag", "integration"):
            filter_cat = arg

    print(f"\n{'='*60}")
    print(f"  Agent-Lab Eval Suite")
    print(f"  Core Agent (Igor'ek) - LLM cascade, tools, memory, RAG")
    if filter_cat:
        print(f"  Filter: {filter_cat}")
    print(f"{'='*60}")

    suite = build_suite()
    suite.run(filter_cat)
    ok = suite.summary()

    sys.exit(0 if ok else 1)
