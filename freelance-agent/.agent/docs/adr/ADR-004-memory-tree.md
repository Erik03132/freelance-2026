# ADR-004: Memory Tree (SuperContext) + Model routing

**Дата:** 2026-07-09
**Статус:** Accepted
**Контекст:** По концепции OpenHuman (tinyhumansai/OpenHuman): brain = local-first persistent memory (Memory Tree / SuperContext), model routing (выбор LLM под задачу), TokenJuice (сжатие контекста). Нужно дать агентам персистентную память (no cold starts) и умный выбор модели — поверх уже построенного learning loop + security.

## Решение

**Memory Tree (SuperContext)** — общий пакет `freelance-agent/.agent/agents/memory/` (как `learning/`/`security/`):
- `remember(agent, fact, kind="fact")` — append в `memory/<agent>.jsonl`
- `recall(agent, query, top_k=3)` — scoring по пересечению токенов, возвращает топ фактов как текст
Перед генерацией агент вызывает `recall()` и объединяет с learned_context (единый блок в промпте); после успешной генерации — `remember()` ключевого факта. Так агенты помнят проект между вызовами.

**Model routing + TokenJuice** — в каждом `llm_client`:
- `ROUTE = {"simple": deepseek-chat-v3-0324, "complex": claude-sonnet-4}` (OpenRouter)
- `call_llm(..., complexity="simple")` выбирает модель; тяжёлые задачи (deep_audit, owasp, design, page) → "complex"
- `_compress(text, max_chars)` — усечение длинных snippet-ов перед моделью (TokenJuice-lite)

## Альтернативы
- Векторная БД (chroma) для Memory Tree — отвергнута: избыточно, scored token-overlap достаточно для локальной памяти одного пользователя.
- LLM-сжатие (настоящий TokenJuice) — отвергнуто: оверхед вызова; truncate достаточен.

## Последствия
- Новый пакет `memory/` (~2 файла).
- Все 4 агента: recall перед генерацией + remember после; model routing в тяжёлых вызовах.
- Профили дополняются секцией Memory/Model routing.
