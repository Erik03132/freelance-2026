# Case library handoff — `docs/cases/` (vs `docs/solutions/`)

`expert-source-review` has TWO output destinations, not one. Picking the wrong one
clutters the workspace. Rule of thumb:

| When the source is… | Write to… | Why |
|---|---|---|
| A **tool / repo / library** we should integrate | `docs/solutions/<slug>.md` (via `github-repo-review` skill) | Solutions are decision-records about *using* something. They age out. |
| A **case study / real-world example / видеоразбор** with reusable lesson | `docs/cases/<slug>.md` + add to `docs/cases/INDEX.md` | Cases are a long-lived knowledge bank: "here's how X is actually used in practice." |

## Triggers for `docs/cases/` (write a case)

Pick at least 2 of:
- Source has a **real example** (screenshots, code, demo, transcript excerpts).
- The lesson **doesn't expire** in 30 days (a tool yes, a pattern no).
- We **might quote/reference it later** ("как у Коновалова в vc.ru", "как в видео Kepano").
- It's a **video / article / channel** worth remembering for future searches.
- We have a **reusable insight** (architecture, anti-pattern, benchmark result).

If the source is purely "tool we install" — that's a Solution, not a Case.

## One-pager template

```markdown
# <slug> — <one-line subject>

**Автор/источник:** <name> (<channel/publication>, <date>, [<url>](<url>)) · <stars/likes/reads> · <active/archived> · <license if relevant>.

**Суть (2-3 строки):** <what it is, in our own words>

**Стек (если есть):** <main components, in 3-5 bullets>

**Что применимо у нас:** [ДА/НЕТ/в очередь] — <one line why>

**Бенчмарки / цифры (если автор приводит):**
- <metric>: <value>
- <metric>: <value>

**Trade-off (если автор признаёт):**
- <honest drawback>

**Сравнение с альтернативами (если есть):**
| Инструмент | Плюс | Минус |
|---|---|---|
| <A> | ... | ... |
| <B> | ... | ... |

**Действие (что мы сделали/планируем):**
- [ ] <concrete next step>

**Ключевые грабли (из источника, чтобы не наступать):**
- <pitfall>
- <pitfall>

**Когда НЕ применять:** <conditions>
```

## INDEX.md format

`docs/cases/INDEX.md` has THREE sections, in this order:

```markdown
## Кейсы

### ✅ Разобрано
- **[<slug>](./<slug>.md)** (<date>, <author>) — <one line> — **→ ES-N / опробовано в X**

### ⏸ В очереди
- <slug> — <one line why deferred>

### ❌ Пропущено
- <slug> — <one line why rejected>
```

Rejected cases belong in INDEX too — same reason as ACTIVE_TASKS.md: prevents re-review
in 3 months.

## INDEX maintenance

- New case → write file → patch INDEX same call as the write.
- ES-N created from case → add inline `**ES-N**` reference in INDEX entry.
- Don't delete from INDEX when "done" — done cases are still reference material.

## Linkage with ACTIVE_TASKS

```
ES-N entry in ACTIVE_TASKS.md      → implementation task
       │
       │ references
       ▼
case file in docs/cases/           → context, why we care, source data
```

ES-N points AT the case file in its body. Case file references ES-N in INDEX.
If we later implement and write `docs/solutions/<slug>-pilot.md`, that file
references BOTH (the case was the "why", the solution is the "what").

## Weekly cron (`hermes-cases-weekly`)

Don't wait for user to drop URLs. The cron job `hermes-cases-weekly` (Mondays 9:00
MSK, job_id `f8bfa5500fa7`) runs the `expert-source-pipeline` skill and:

1. Finds 3-5 fresh public Hermes use-cases from YouTube/Telegram/blogs
2. Applies the `expert-source-review` method to each
3. Writes new case files OR updates existing ones with fresh data
4. Patches `docs/cases/INDEX.md`

The cron output is `deliver=local` — user checks via `cronjob action=list` or
manually runs `cronjob action=run`.

## Filesystem layout (final, Aug 2026)

```
~/freelance-2026/
├── docs/
│   ├── cases/           ← THIS (long-lived knowledge bank)
│   │   ├── INDEX.md
│   │   ├── codegraph.md
│   │   └── ivan-ilyich.md
│   └── solutions/       ← (decision-records about tools, shorter-lived)
│       ├── INDEX.md
│       ├── codegraph-pilot.md
│       └── expert-council-pilot.md
└── ACTIVE_TASKS.md      ← (current backlog, ES-N entries)
```

Don't merge these folders — they serve different lifecycles.