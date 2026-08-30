# Expert Council — opt-in multi-perspective review

Default behaviour for `expert-source-review` is single expert (4-paragraph verdict).
For high-stakes decisions, escalate to a 4-role council. This file documents when
and how.

## When to escalate

Council = 4x cost of single expert. Use only when one of:

- Decision **>30 min work** to reverse if wrong
- **>10 000₽** annual impact (money or time × rate)
- **New class of tool** (not "another tool in the existing class")
- **Strategic** (куда идём, что строим, чем заменить)
- User said: "council", "совет экспертов", "давай через 4 роли", "проверь советом"

If single expert can decide in 30 sec ("пропускаем, шум") — don't escalate.

## The 4 roles

### 1. Expert (moderator)
- Default 4-paragraph format
- Synthesises the other 3 at the end
- 3-5 bullets

### 2. Skeptic
- Risks, edge cases, anti-patterns
- Conflicts of interest (автор продвигает SaaS? имеет аффилиат-ссылку?)
- Vendor lock-in (привязка к инфраструктуре X?)
- Marketing claims vs reality
- Заканчивает списком **Red lines** (нельзя игнорировать, иначе стоп)

### 3. Analyst
- Numbers, benchmarks, метрики (verify stars via GitHub API!)
- License, maintenance, last commit, contributors count
- 2-3 alternatives table (Плюс/Минус)
- Ссылки на источники

### 4. Financier
- Прямая стоимость (₽, часы)
- Скрытая стоимость (обучение, миграция, откат)
- ROI (что вернётся, через сколько)
- Скрытые риски (вендор-лок, ToS-нарушения)

## Output format

```
## Council Review

**Source:** <URL/title>
**Stakes:** <low/medium/high/strategic>

### Expert
<3-5 bullets>

### Skeptic
<3-5 bullets>
**Red lines:**
- <thing we cannot ignore>

### Analyst
<3-5 bullets>
**Comparison:**
| Альтернатива | Плюс | Минус |
|---|---|---|
| A | ... | ... |
| B | ... | ... |

### Financier
<3-5 bullets>
**Total cost:** <X₽ + Y часов>
**Hidden costs:** <что не видно>

### Verdict (Expert)
Что: ...
Зачем: ...
Берём: да/нет/позже
Не берём потому что: ...
```

## Honest limitations (собрано из пилота 2026-08-20)

- **Council = 4x tokens.** Don't use for trivial stuff.
- **All 4 roles = same LLM.** They share blind spots. If you need adversarial
  debate (genuine disagreement, not 4 flavours of "looks ok"), council doesn't
  help — escalate to human.
- **Council ≠ replacement for Igor.** If the decision is "нужна ли нам эта
  архитектура" — Igor decides, council informs.

## When council actually helps (empirical, from session 2026-08-20)

Tested on 3 cases (CodeGraph / Попов / Hermes Bot Mode). Council added value
in these dimensions:

- **Hidden risks** (vendor lock-in, ToS, автор продвигает свой SaaS)
- **Hidden costs** (обучение, миграция, привязка к вендору)
- **Red lines** — formalisation of "things we cannot ignore"
- **Numbers** (ROI в час Игоря, не в токенах; стоимость альтернатив)

Council did NOT add value for:
- "Это шум" → single expert already says нет
- Technical correctness ("работает ли код") → use code-review, not council

## Trigger phrases

Single expert (default):
- "разбери", "выступи экспертом", "насколько нам применимо"
- "как тебе?", "твоё мнение"

Council:
- "council", "совет экспертов", "давай через 4 роли"
- "проверь советом", "expert council mode"
- "серьёзный разбор", "перед решением >10к₽"
- "разбери как стратегический выбор"

## Implementation note

Council = 4 separate reasoning passes with different system prompts, then a
final synthesis pass. Today, all 4 are the same model (Hermes-4 via OmniRoute)
in the same context window — that's a known limitation, see above.

If future versions use 4 different models (Skeptic on Nous, Analyst on Sonnet,
etc.), the diversity is real. Not worth doing now for ad-hoc reviews.

## Filesystem

- Skill: `~/.hermes/skills/expert-council.md` (Hermes skills root, separate
  from expert-source-review — this is a separate workflow)
- Pilot results: `~/freelance-2026/docs/solutions/expert-council-pilot.md`
- 4 roles + output format: see skill body

Don't write a separate "council skill" inside `expert-source-review` — they
overlap and confuse callers. Council is its own skill.