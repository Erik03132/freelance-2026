---
name: self-improvement
description: "Самообучение агентов: Learning (signals → context), Soul (constitution + evolving lessons), Memory (local store + recall). Переносит Antigravity learning loop в OpenCode."
tools: [bash, read, write, edit]
model: sonnet
source: "/Users/igorvasin/freelance-2026/freelance-agent/.agent/agents/learning/,soul/,memory/"
---

# Self-Improvement Skill — OpenCode Wrapper for Antigravity Learning Loop

> **Источник:** `freelance-agent/.agent/agents/{learning,soul,memory}/` (Python modules: learner.py, signal.py, store.py)

## Архитектура (3 слоя)

```
┌─────────────────────────────────────────────────────────────┐
│  TASK COMPLETE                                              │
└──────────────┬──────────────────────────────────────────────┘
               ▼
┌─────────────────────────────────────────────────────────────┐
│  1. LEARNING — signal capture                               │
│     capture_start(agent, spec, meta)  → signals.jsonl       │
│     capture_outcome(agent, outcome)   → accepted/edited/rej │
│     build_learned_context(agent)        → prompt injection  │
└──────────────┬──────────────────────────────────────────────┘
               ▼
┌─────────────────────────────────────────────────────────────┐
│  2. SOUL — living constitution                              │
│     ## Constitution (human, never auto-edited)              │
│     ## Evolving Lessons (machine, auto-folded)              │
│     <!-- SOUL:AUTO:BEGIN --> ... <!-- SOUL:AUTO:END -->     │
└──────────────┬──────────────────────────────────────────────┘
               ▼
┌─────────────────────────────────────────────────────────────┐
│  3. MEMORY — local RAG                                      │
│     remember(agent, fact, kind)     → agent.jsonl           │
│     recall(agent, query, top_k=3)   → scored facts          │
│     compact(agent, keep=500)        → dedupe + trim         │
└──────────────────────────────────────────────────────────────┘
```

---

## Команды (bash через Python CLI)

```bash
# 1. LEARNING — сигналы
python3 -m learning capture_start  --agent sherlock --spec "GEO audit for ai-eggs" --meta '{"model":"sonnet"}'
python3 -m learning capture_outcome --agent sherlock --outcome accepted
python3 -m learning context --agent sherlock   # → готовый блок для промпта

# 2. SOUL — живая конституция
python3 -m soul scaffold sherlock "Research Agent"
python3 -m soul read sherlock
python3 -m soul fold sherlock "Users prefer bullet-point reports over prose"

# 3. MEMORY — факты
python3 -m memory remember sherlock "ai-eggs uses DeepSeek V3 for Tier 1" --kind fact
python3 -m memory recall sherlock "ai-eggs model"
python3 -m memory compact sherlock
```

---

## Интеграция в OpenCode Workflow

### В AGENTS.md (уже есть) — автоматический вызов:

```markdown
# После finish-day / handoff / PR merge:
python3 -m learning capture_outcome --agent $(current_agent) --outcome accepted
python3 -m memory compact $(current_agent)
python3 -m soul fold $(current_agent) "$(lesson_from_session)"
```

### В skill usage:

```python
# В начале задачи:
from learning import capture_start
capture_start(agent="shakespeare", spec="Landing for Levitan voice agents", meta={"model": "fable"})

# В конце задачи (после review пользователем):
from learning import capture_outcome
capture_outcome(agent="shakespeare", outcome="accepted")  # или "edited" / "rejected"

# При следующем вызове skill("agents/shakespeare"):
from learning import build_learned_context
context = build_learned_context("shakespeare")  # инжектируется в промпт
```

---

## Файловая структура (общая с Antigravity)

```
freelance-agent/.agent/agents/
├── learning/
│   ├── signals.jsonl          # все сигналы всех агентов
│   ├── learner.py             # build_learned_context()
│   └── signal.py              # capture_start/outcome
├── soul/
│   ├── sherlock.soul.md       # living constitution
│   ├── shakespeare.soul.md
│   ├── kulibin.soul.md
│   └── store.py               # scaffold/read/write/replace_auto_zone
└── memory/
    ├── sherlock.jsonl         # facts per agent
    ├── shakespeare.jsonl
    └── store.py               # remember/recall/compact
```

---

## Пример Soul файла (sherlock.soul.md)

```markdown
# Sherl — Soul

## Constitution
> Human-owned. The unchanging identity & hard rules.

**Role:** Research Agent — GEO/Market Intelligence, Perplexity, competitor audit.

**Hard rules:**
- Never hallucinate sources. Every claim = URL.
- Output format: Executive Summary → Details → Sources.
- Parallel search: web + AI chatbots + specialized platforms.

## Evolving Lessons
> Machine-owned. Auto-folded from usage signals + memory.

<!-- SOUL:AUTO:BEGIN -->
- Users favor bullet-point reports over prose (seen 5x in accepted)
- Common in accepted requests: "competitor", "pricing", "geo", "audit"
- Acceptance rate: 78% accepted, 15% rejected (n=27)
<!-- SOUL:AUTO:END -->
```

---

## Пример Memory recall

```bash
$ python3 -m memory recall sherlock "ai-eggs model"
Project memory:
- ai-eggs uses DeepSeek V3 for Tier 1 tasks
- ai-eggs falls back to Sonnet for Tier 2
- Sherl last used Perplexity for GEO audit 2026-07-20
```

---

## Commands для OpenCode

| Команда | Что делает |
|---------|------------|
| `skill("self-improvement")` | Активирует доступ к функциям |
| `python3 -m learning context --agent X` | Готовый блок для инжекта в промпт |
| `python3 -m soul read X` | Читаетconstitution + lessons |
| `python3 -m memory recall X "query"` | Топ-3 релевантных факта |

---

## Следующий шаг: авто-хуки

Сейчас — ручной вызов. Для полной автоматизации нужно:
1. Добавить в `finish-day` / `handoff` вызовы `capture_outcome`
2. Сделать wrapper `agent_run(agent, task)` который сам делает start/outcome
3. Подключить к `claude-mem` для кросс-сессионной памяти (уже есть `memory_add`)

Хочешь — соберу **авто-хук в finish-day** прямо сейчас?