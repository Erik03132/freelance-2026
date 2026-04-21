"""
🐣 Анжела — «ребёнок» Core Agent.

Это пример того, как из универсального ядра сделать специалиста.
Всё что нужно:
  1. Системный промпт (характер + правила)
  2. Папка со знаниями (knowledge/)
  3. Специфичные инструменты (опционально)

Запуск:
  python -m children.angela
"""
import asyncio
import sys
import os

# Добавляем родительский каталог в path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core_agent import CoreAgent
from tools import CORE_TOOLS, tool


# === Специфичные инструменты Анжелы ===

@tool
def calculate_feed(breed: str, count: int, days: int = 40) -> str:
    """Рассчитывает количество корма для птицы.
    Используй, когда клиент спрашивает сколько корма нужно.
    
    Args:
        breed: Порода (бройлер, несушка, индюк, утка)
        count: Количество голов
        days: Период выращивания в днях
    """
    # Нормы потребления корма (кг на 1 голову за весь период)
    feed_rates = {
        "бройлер": 4.5,    # ~4.5 кг за 40 дней
        "несушка": 0.12,   # 120г в день
        "индюк": 16.0,     # за 120 дней
        "утка": 7.0,       # за 50 дней
    }

    breed_lower = breed.lower()
    rate = None
    for key, value in feed_rates.items():
        if key in breed_lower:
            rate = value
            break

    if rate is None:
        return f"Не знаю норму для породы '{breed}'. Знаю: бройлер, несушка, индюк, утка."

    if "несушка" in breed_lower:
        total_kg = rate * count * days
    else:
        total_kg = rate * count

    bags_25kg = -(-int(total_kg) // 25)  # Округление вверх
    
    return (
        f"Расчёт корма для {count} голов ({breed}):\n"
        f"Общий расход: {total_kg:.0f} кг\n"
        f"Мешков по 25 кг: {bags_25kg} шт\n"
        f"Период: {days} дней"
    )


# Инструменты Анжелы = базовые + свои
ANGELA_TOOLS = CORE_TOOLS + [calculate_feed]


# === Системный промпт Анжелы (её «характер») ===
ANGELA_PROMPT = """
Ты — Анжелочка, менеджер по продажам компании «Азовский инкубатор».

ТВОЯ ЦЕЛЬ: помочь клиенту выбрать товар и получить его НОМЕР ТЕЛЕФОНА для бронирования.

ПРАВИЛА:
1. Обращайся к клиентам СТРОГО на «Вы».
2. Давай полный ответ в чате, не отправляй на сайт.
3. При заказе бройлеров — предложи комбикорм и аптечку (200₽).
4. Если клиент спрашивает про кур — НЕ предлагай уток или гусей.
5. Если не знаешь точную информацию — скажи «Сейчас уточню!»
6. Говори кратко, профессионально, без уменьшительных слов.

ИСПОЛЬЗУЙ ИНСТРУМЕНТЫ:
- search_knowledge — для поиска цен и товаров
- calculate_feed — для расчёта количества корма
- calculate — для расчёта суммы заказа
"""


async def main():
    """Запуск Анжелы в интерактивном режиме."""
    agent = CoreAgent(
        name="Анжелочка",
        system_prompt=ANGELA_PROMPT,
        tools=ANGELA_TOOLS,
        knowledge_dir=os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge"),
    )

    print("\n🐣 Анжелочка — AI-менеджер по продажам")
    print("Напишите 'выход' для завершения\n")

    while True:
        try:
            user_input = input("👤 Клиент: ")
        except (EOFError, KeyboardInterrupt):
            break
        if user_input.lower() in ("выход", "exit", "quit"):
            break
        await agent.run(user_input)


if __name__ == "__main__":
    asyncio.run(main())
