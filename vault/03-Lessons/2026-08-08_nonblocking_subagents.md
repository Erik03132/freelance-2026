# PF-1: Неблокирующие субагенты (Prime Agent паттерн)

**Реализован как паттерн для /goal и executing-plans.**

## Суть

Вместо последовательного запуска N субагентов (каждый ждёт предыдущего), запускаем всех параллельно
и собираем результаты по мере готовности. Это сокращает wall-clock время в N раз.

## Паттерн

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

def execute_plan_with_subagents(plan_steps: list[dict], agent_func) -> dict:
    """
    Запускает все шаги плана параллельно через agent_func.
    Собирает результаты по мере готовности.
    """
    results = {}
    with ThreadPoolExecutor(max_workers=min(8, len(plan_steps))) as executor:
        futures = {
            executor.submit(agent_func, step): step["id"]
            for step in plan_steps
            if step.get("status") != "done"
        }
        for future in as_completed(futures):
            step_id = futures[future]
            try:
                results[step_id] = future.result(timeout=600)
            except Exception as e:
                results[step_id] = {"error": str(e), "status": "failed"}
    return results
```

## Интеграция с AP-1

Принцип AP-1 (каждый тикет = субагент со свежим контекстом) + PF-1 (параллельный запуск):
- Тикеты, не зависящие друг от друга → запускаются параллельно
- Зависимые тикеты → последовательно (порядок определён планом)
- Контекст каждого субагента изолирован (AP-1) → нет конфликтов

## Где применять

1. `/goal` — при цели с несколькими изолированными подцелями
2. `executing-plans` — фазы плана, которые не зависят друг от друга
3. `ce-work` — параллельные шаги имплементации

## Ограничения

- Не для LLM-агентов с общим состоянием (модель не шарит контекст)
- Каждый субагент = свежий вызов модели → цена = N × стоимость одного вызова
- Timeout per subagent: 600с (для длинных задач)

**Статус:** паттерн задокументирован. Интеграция в /goal — следующая итерация.
