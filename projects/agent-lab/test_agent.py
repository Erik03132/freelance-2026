from __future__ import annotations

"""
🧪 Финальный тест Игорька v0.3
Elephant Alpha + Tavily + Perplexity + DuckDuckGo + Memory
"""
import asyncio
from core_agent import CoreAgent
from tools import EXTENDED_TOOLS


async def test():
    print("=" * 60)
    print("🧪 ФИНАЛЬНЫЙ ТЕСТ: Игорёк v0.3")
    print("  LLM: Elephant Alpha (каскад 5 уровней)")
    print("  Search: Tavily → Perplexity → DuckDuckGo")
    print("=" * 60)

    agent = CoreAgent(
        name="Игорёк",
        tools=EXTENDED_TOOLS,
    )

    tools_list = [t.name for t in agent.tools]
    print(f"\n📊 СТАТУС:")
    print(f"  Tools:  {len(agent.tools)} — {tools_list}")
    print(f"  Memory: {len(agent.memory.facts)} facts")
    print(f"  Hints:  {'✅' if agent.hints.hints_text else '❌'}")

    # Тест 1: Простой ответ
    print("\n--- Тест 1: Кто ты? ---")
    await agent.run("Привет! Кто ты и что умеешь?")

    # Пауза — уважаем rate limit
    print("\n⏳ Пауза 3с...")
    await asyncio.sleep(3)

    # Тест 2: Расчёт
    print("\n--- Тест 2: Расчёт ---")
    await agent.run("Посчитай: 200 бройлеров по 90₽ + 150 несушек по 250₽")

    await asyncio.sleep(3)

    # Тест 3: RAG — поиск в базе знаний
    print("\n--- Тест 3: RAG ---")
    await agent.run("Какой адрес самовывоза?")

    await asyncio.sleep(3)

    # Тест 4: ⭐ WEB SEARCH (Tavily!) 
    print("\n--- Тест 4: ⭐ Поиск в интернете (Tavily) ---")
    await agent.run("Найди в интернете: какая погода сейчас в Уфе?")

    await asyncio.sleep(3)

    # Тест 5: Memory
    print("\n--- Тест 5: Память ---")
    await agent.run("Запомни: клиент Иванов из Симферополя заказал 300 бройлеров КОББ-500")

    # Итоги
    facts = agent.memory.recall()
    print(f"\n🧠 Память: {facts}")
    
    print("\n" + "=" * 60)
    print("✅ ФИНАЛЬНЫЙ ТЕСТ ЗАВЕРШЁН!")
    print(f"📊 Memory: {len(agent.memory.facts)} фактов на диске")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test())
