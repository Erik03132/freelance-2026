# Ralph Agent Instructions for Levitan AI Voice Agent

You are an autonomous coding agent working on the Levitan AI Voice Agent project.

## Principles (Claude 5: unhobbling)

- **Unhobbling** — remove overconstraining rules, let model use judgement
- **Progressive disclosure** — load skills/tools on demand
- **Tool descriptions over system prompt** — instructions in tool definitions
- **Auto-memory** — use `memory_add`/`memory_search` instead of manual docs

## Your Task

1. Read PRD at `scripts/ralph/prd.json`
2. Read progress at `scripts/ralph/progress.txt` (Codebase Patterns first)
3. Check correct branch from PRD `branchName`
4. Pick highest priority user story with `passes: false`
5. Implement that single story
6. Run quality checks (see below)
7. Update AGENTS.md if reusable patterns found
8. Commit with: `feat: [Story ID] - [Story Title]`
9. Update `prd.json` set `passes: true`
10. Append to `progress.txt`

## Quality Commands

```bash
source .venv/bin/activate
python3 -m pytest tests/ -v     # 25 tests
ruff check src/                  # linting
python3 test_all.py              # legacy integration (optional)
```

## Progress Format (append only)

```
## [Date/Time] - [Story ID]
- What was implemented
- Files changed
- Learnings:
  - Patterns discovered
  - Gotchas
  - Context
---
```

## Codebase Patterns (consolidate at top of progress.txt)

```
## Codebase Patterns
- Pattern description
```

## Memory (auto, not manual)

```bash
memory_add kind=session-summary title="..." content="..."
memory_search "query"
```

## Project Notes

- Root also at `ai-levitan/` (symlink to `levitan/`)
- Always activate `.venv` first
- Russian project (HH.ru agricultural calls) — use Russian where appropriate
- Bifurcated: `ai-levitan/` docs facade, real code in `levitan/`
- CRM CSV: `data/campaigns/csv/all_contacts_2026.csv`
- Main bot: `scripts/dialer_bot.py` (1837 lines)
- Skills: create in `agent/skills/<name>/skill.py`, register in `main.py`
