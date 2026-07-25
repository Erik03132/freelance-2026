# ADR-002: Self-Learning Loop для агентов

**Дата:** 2026-07-09
**Статус:** Accepted
**Контекст:** Прокачка агентов (ADR-001) дала LLM-CLI тулы. По концепции Atai Barkai «Self Learning for Agents» самый ценный сигнал — поведение людей, использующих продукт (приняли/отредактировали/отвергли результат). Нужен слой захвата этих сигналов и авто-подстройки промптов.

## Решение

Общий пакет `freelance-agent/.agent/agents/learning/` (НЕ агент, shared infra), подключаемый ко всем агентам опционально (try/except, не ломает агента при отсутствии).

**Поток сигнала (human behavioral loop):**
1. При генерации: `capture_start(agent, action, spec, meta)` → пишет запись в `signals.jsonl`, возвращает `sid`.
2. В промпт генерации внедряется `build_learned_context(agent)` — агрегированные инсайты из прошлых принятых сигналов (авто-применение).
3. Позже пользователь фиксирует исход: CLI `--feedback <sid> accepted|edited|rejected [note]` → `capture_outcome(sid, outcome, note)`.

**Хранилище:** append-only `freelance-agent/.agent/agents/learning/signals.jsonl` (git-friendly, читается легко).

**Что улучшается:** промпты (learned context). Дефолты и приоритеты аудита — вне scope (ADR-002).

**Агрегация (learner.py):** по agent считаются accepted%/edited%/rejected%, топ action, предпочтения из `meta` (напр. framework), частые паттерны в принятых vs отвергнутых spec. Итог — строка-контекст для промпта.

## Альтернативы
- SQLite/Chroma — отвергнуты: избыточно для объёма сигналов одного пользователя; JSONL проще и прозрачнее.
- Авто-сбор от оркестратора — отвергнут: шумно, противоречит «people using your product» (прямые вызовы людьми).

## Последствия
- Новый пакет `learning/` (~4 файла) + `signals.jsonl`.
- В каждый агент добавляется: capture при генерации, вставка learned context в промпт, флаг `--feedback` в CLI.
- Профили агентов дополняются секцией Self-Learning.
