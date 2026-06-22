from __future__ import annotations

"""
🧬 Игорёк — Core Agent (Ядро AI-агента нового поколения).

Версия: 0.2 — "Goose Upgrade"
Добавлено из анализа Goose AI Agent:
  ✅ Memory — постоянная память между сессиями (файл memory.json)
  ✅ Hints — подсказки (.hints файлы, автоматически подгружаются)
  ✅ Permission System — 3 уровня автономности

Это ШАБЛОН. Сам по себе — универсальный помощник «Игорёк».
Чтобы получить специалиста — создай "ребёнка":
  - Анжела (птицеводство)
  - Шерлок (аналитика)  
  - Мустай (законодательство)

Архитектура:
  ┌─────────────────────────────────────────────┐
  │              🧬 Игорёк (Core Agent)         │
  │                                             │
  │  ┌──────────┐  ┌───────┐  ┌──────────────┐ │
  │  │ 🧠 LLM   │  │ 🔧    │  │ 📚 RAG       │ │
  │  │ (каскад) │  │ Tools │  │ (knowledge/) │ │
  │  └────┬─────┘  └───┬───┘  └──────┬───────┘ │
  │       └──────┬─────┘─────────────┘          │
  │       ┌──────▼──────┐  ┌──────────────────┐ │
  │       │ 🔄 ReAct    │  │ 🆕 Memory        │ │
  │       │ Loop        │  │ (между сессиями) │ │
  │       └─────────────┘  └──────────────────┘ │
  │  ┌──────────────┐  ┌────────────────────┐   │
  │  │ 🆕 Hints     │  │ 🆕 Permissions     │   │
  │  │ (подсказки)  │  │ (уровни доступа)   │   │
  │  └──────────────┘  └────────────────────┘   │
  └─────────────────────────────────────────────┘
"""
import asyncio
import json
import os
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

# LangGraph
try:
    from langgraph.prebuilt import create_react_agent
    HAS_LANGGRAPH = True
except ImportError:
    HAS_LANGGRAPH = False
    print("⚠️ LangGraph не установлен. Агент работает в simple mode.")

try:
    from langchain_openai import ChatOpenAI
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False

from tools import CORE_TOOLS
from rag_memory import get_memory
from llm_engine import call_llm


# ============================================================
# 🆕 PERMISSION SYSTEM (из Goose)
# Три уровня автономности агента
# ============================================================
class PermissionLevel:
    """
    Уровни автономности (идея из Goose AI):
    
    ADVISORY  — агент только советует, ничего не делает сам
    ASSISTED  — агент делает, но спрашивает разрешение  
    AUTONOMOUS — агент делает всё сам (осторожно!)
    """
    ADVISORY = "advisory"       # Только рекомендации
    ASSISTED = "assisted"       # Делает с подтверждением
    AUTONOMOUS = "autonomous"   # Полная автономия


# ============================================================
# 🆕 PERSISTENT MEMORY (из Goose Memory Extension)
# Память между сессиями — агент помнит факты о пользователе
# ============================================================
class PersistentMemory:
    """
    Постоянная память агента между сессиями.
    
    Хранит: факты о пользователе, предпочтения, важные решения.
    Файл: memory.json рядом с агентом.
    
    Пример:
      memory.remember("Клиент Иванов предпочитает КОББ-500")
      memory.remember("Доставка в Краснодар по четвергам")
    """

    def __init__(self, memory_file: str | Path):
        self.file = Path(memory_file)
        self.facts: list[dict] = []
        self._load()

    def _load(self):
        if self.file.exists():
            try:
                self.facts = json.loads(self.file.read_text(encoding="utf-8"))
                if self.facts:
                    print(f"🧠 Memory: загружено {len(self.facts)} фактов")
            except Exception:
                self.facts = []

    def _save(self):
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.file.write_text(
            json.dumps(self.facts, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def remember(self, fact: str, category: str = "general"):
        """Запомнить факт."""
        entry = {
            "fact": fact,
            "category": category,
            "timestamp": datetime.now().isoformat(),
        }
        self.facts.append(entry)
        self._save()
        print(f"🧠 Запомнил: {fact}")

    def recall(self, query: str = "", limit: int = 5) -> list[str]:
        """Вспомнить факты (последние или по ключевому слову)."""
        if not self.facts:
            return []
        if query:
            # Поиск по ключевым словам
            query_words = set(query.lower().split())
            scored = []
            for f in self.facts:
                fact_lower = f["fact"].lower()
                score = sum(1 for w in query_words if w in fact_lower)
                if score > 0:
                    scored.append((score, f["fact"]))
            scored.sort(reverse=True)
            return [text for _, text in scored[:limit]]
        else:
            # Последние N фактов
            return [f["fact"] for f in self.facts[-limit:]]

    def forget_all(self):
        """Забыть всё (сброс памяти)."""
        self.facts = []
        self._save()

    def get_context(self) -> str:
        """Получить все факты как контекст для промпта."""
        if not self.facts:
            return ""
        facts_text = "\n".join(f"• {f['fact']}" for f in self.facts[-20:])
        return f"\n\nТВОЯ ПАМЯТЬ (факты, которые ты запомнил ранее):\n{facts_text}\n"


# ============================================================
# 🆕 HINTS SYSTEM (из Goose .goosehints)
# Подсказки — автоматически подгружаемый контекст
# ============================================================
class HintsLoader:
    """
    Система подсказок (идея из Goose .goosehints).
    
    Подсказки — это .md файлы, которые автоматически добавляются 
    в промпт агента. Позволяют настроить поведение без кода.
    
    Иерархия (от общего к частному):
      1. agent-lab/.hints/global.md   — для ВСЕХ агентов
      2. agent-lab/.hints/igorek.md   — для Игорька
      3. children/.hints/angela.md    — для Анжелы
    
    Более конкретные подсказки имеют приоритет.
    """

    def __init__(self, hints_dirs: list[str | Path] = None):
        self.hints_dirs = [Path(d) for d in (hints_dirs or [])]
        self.hints_text = ""
        self._load()

    def _load(self):
        """Загружает все .md файлы из папок подсказок."""
        all_hints = []
        for hints_dir in self.hints_dirs:
            if not hints_dir.exists():
                continue
            for hint_file in sorted(hints_dir.glob("*.md")):
                text = hint_file.read_text(encoding="utf-8").strip()
                if text:
                    all_hints.append(f"[Подсказка из {hint_file.name}]\n{text}")

        if all_hints:
            self.hints_text = "\n\n".join(all_hints)
            print(f"📝 Hints: загружено {len(all_hints)} подсказок")

    def get_context(self) -> str:
        """Получить подсказки как контекст для промпта."""
        if not self.hints_text:
            return ""
        return f"\n\nДОПОЛНИТЕЛЬНЫЕ ИНСТРУКЦИИ:\n{self.hints_text}\n"


# ============================================================
# 🧬 CORE AGENT — ИГОРЁК
# ============================================================
class CoreAgent:
    """
    Игорёк — универсальное ядро AI-агента.
    
    v0.2 "Goose Upgrade":
      + PersistentMemory — помнит факты между сессиями
      + HintsLoader — подгружает подсказки из .md файлов
      + PermissionLevel — 3 уровня автономности
    
    Параметры:
      name:             Имя агента
      system_prompt:    Характер и правила
      tools:            Инструменты (функции с @tool)
      knowledge_dir:    Папка знаний (для RAG)
      hints_dirs:       Папки с подсказками (.md файлы)
      permission:       Уровень автономности
      max_iterations:   Максимум шагов ReAct-цикла
    """

    VERSION = "0.2"

    def __init__(
        self,
        name: str = "Игорёк",
        system_prompt: str = "",
        tools: list = None,
        knowledge_dir: str | Path = None,
        hints_dirs: list[str | Path] = None,
        permission: str = PermissionLevel.ASSISTED,
        max_iterations: int = 5,
    ):
        self.name = name
        self.system_prompt = system_prompt or self._default_prompt()
        self.tools = tools or CORE_TOOLS
        self.max_iterations = max_iterations
        self.permission = permission
        self.history: list[dict] = []

        # Базовая директория агента
        base_dir = Path(__file__).parent

        # 📚 RAG Memory
        if knowledge_dir:
            self.rag = get_memory(knowledge_dir)
        else:
            self.rag = get_memory()

        # 🆕 Persistent Memory
        memory_file = base_dir / ".memory" / f"{name.lower().replace(' ', '_')}.json"
        self.memory = PersistentMemory(memory_file)

        # 🆕 Hints
        default_hints = [base_dir / ".hints"]
        self.hints = HintsLoader(hints_dirs or default_hints)

        # 🆕 Добавляем инструмент «запомнить» в набор
        self._add_memory_tool()

        # 🔄 ReAct Agent
        self._agent = None
        if HAS_LANGGRAPH and HAS_LANGCHAIN:
            self._init_langgraph_agent()

        # Отчёт
        perm_emoji = {"advisory": "👀", "assisted": "🤝", "autonomous": "🚀"}
        print(
            f"🤖 {self.name} v{self.VERSION}: запущен | "
            f"Tools: {len(self.tools)} | "
            f"RAG: {len(self.rag.documents)} docs | "
            f"Memory: {len(self.memory.facts)} facts | "
            f"Mode: {perm_emoji.get(self.permission, '')} {self.permission}"
        )

    def _default_prompt(self) -> str:
        return (
            "Ты — Игорёк, универсальный AI-помощник. "
            "Отвечай кратко и по делу на русском языке. "
            "Используй инструменты когда нужна конкретная информация. "
            "ВАЖНО: Когда пользователь просит запомнить что-то — ОБЯЗАТЕЛЬНО вызови "
            "инструмент remember_fact. Не просто говори 'запомнил', а реально вызови инструмент! "
            "Если не уверен — честно скажи."
        )

    def _add_memory_tool(self):
        """Добавляет инструмент запоминания в набор tools."""
        from langchain.tools import tool

        memory = self.memory  # Замыкание

        @tool
        def remember_fact(fact: str) -> str:
            """Запоминает важный факт о пользователе или контексте.
            Используй, когда пользователь сообщает что-то, что стоит запомнить
            на будущее: имя, предпочтения, город, предыдущие заказы.
            
            Args:
                fact: Факт для запоминания (короткая фраза)
            """
            memory.remember(fact)
            return f"Запомнил: {fact}"

        self.tools = list(self.tools) + [remember_fact]

    def _init_langgraph_agent(self):
        """Инициализирует ReAct-агента через LangGraph."""
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if not openrouter_key:
            print("⚠️ OPENROUTER_API_KEY не задан. ReAct отключен.")
            return

        try:
            llm = ChatOpenAI(
                model="openrouter/elephant-alpha",
                openai_api_key=openrouter_key,
                openai_api_base="https://openrouter.ai/api/v1",
                temperature=0,
                max_tokens=4096,
            )
            self._agent = create_react_agent(model=llm, tools=self.tools)
            print("✅ ReAct Agent инициализирован (LangGraph)")
        except Exception as e:
            print(f"⚠️ LangGraph init error: {e}")

    def _build_full_prompt(self) -> str:
        """Собирает полный системный промпт: base + memory + hints."""
        parts = [self.system_prompt]

        # Добавляем память
        mem_ctx = self.memory.get_context()
        if mem_ctx:
            parts.append(mem_ctx)

        # Добавляем подсказки
        hints_ctx = self.hints.get_context()
        if hints_ctx:
            parts.append(hints_ctx)

        return "\n".join(parts)

    async def run(self, user_message: str) -> str:
        """
        Обработать сообщение пользователя.
        
        ReAct: агент сам выбирает инструменты.
        Simple: fallback (prompt → LLM → ответ).
        """
        print(f"\n{'='*50}")
        print(f"👤 {user_message}")
        print(f"{'='*50}")

        if self._agent:
            answer = await self._run_react(user_message)
        else:
            answer = await self._run_simple(user_message)

        # Сохраняем в историю диалога
        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": answer})

        print(f"\n🤖 {self.name}: {answer}")
        return answer

    async def _run_react(self, user_message: str) -> str:
        """ReAct-цикл через LangGraph."""
        try:
            messages = [{"role": "system", "content": self._build_full_prompt()}]
            for msg in self.history[-10:]:
                messages.append(msg)
            messages.append({"role": "user", "content": user_message})

            result = await self._agent.ainvoke(
                {"messages": messages},
                config={"recursion_limit": self.max_iterations * 2},
            )

            response_messages = result.get("messages", [])
            if response_messages:
                return response_messages[-1].content
            return "Не удалось сформировать ответ."

        except Exception as e:
            print(f"⚠️ ReAct error: {e}, fallback → simple")
            return await self._run_simple(user_message)

    async def _run_simple(self, user_message: str) -> str:
        """Простой режим (prompt → RAG → LLM → ответ)."""
        full_prompt = self._build_full_prompt()

        # RAG-контекст
        rag_results = self.rag.search(user_message)
        if rag_results:
            full_prompt += "\n\nКОНТЕКСТ ИЗ БАЗЫ ЗНАНИЙ:\n" + "\n---\n".join(rag_results)

        messages = [{"role": "system", "content": full_prompt}]
        for msg in self.history[-10:]:
            messages.append(msg)
        messages.append({"role": "user", "content": user_message})

        return await call_llm(messages)


# ============================================================
# ИНТЕРАКТИВНЫЙ РЕЖИМ
# ============================================================
async def main():
    """Запуск Игорька в интерактивном режиме."""
    agent = CoreAgent(name="Игорёк")

    print("\n🧬 Игорёк — Agent Lab v0.2 (Goose Upgrade)")
    print("Команды: 'память' — показать память | 'выход' — завершить\n")

    while True:
        try:
            user_input = input("👤 Ты: ")
        except (EOFError, KeyboardInterrupt):
            break

        if user_input.lower() in ("выход", "exit", "quit"):
            break
        elif user_input.lower() in ("память", "memory"):
            facts = agent.memory.recall(limit=10)
            if facts:
                print("🧠 Память Игорька:")
                for f in facts:
                    print(f"  • {f}")
            else:
                print("🧠 Память пуста")
            continue

        await agent.run(user_input)

    print(f"\n👋 Пока! Запомнил {len(agent.memory.facts)} фактов.")


if __name__ == "__main__":
    asyncio.run(main())
