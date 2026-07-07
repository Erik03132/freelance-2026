# Ralph Agent Instructions for Levitan AI Voice Agent

You are an autonomous coding agent working on the Levitan AI Voice Agent project.

## Your Task

1. Read the PRD at `scripts/ralph/prd.json`
2. Read the progress log at `scripts/ralph/progress.txt` (check Codebase Patterns section first)
3. Check you're on the correct branch from PRD `branchName`. If not, check it out or create from main.
4. Pick the **highest priority** user story where `passes: false`
5. Implement that single user story
6. Run quality checks (see Quality Commands below)
7. Update AGENTS.md files if you discover reusable patterns
8. If checks pass, commit ALL changes with message: `feat: [Story ID] - [Story Title]`
9. Update scripts/ralph/prd.json to set `passes: true` for the completed story
10. Append your progress to `scripts/ralph/progress.txt`

## Quality Commands for this project

ALWAYS activate the virtual environment first:
```bash
source .venv/bin/activate
```

Then run:
- ALL tests: `python3 -m pytest tests/ -v`
- Lint: `ruff check src/`
- Legacy integration test: `python3 test_all.py` (requires .env, may skip)

## Progress Report Format

APPEND to progress.txt (never replace, always append):
```
## [Date/Time] - [Story ID]
- What was implemented
- Files changed
- **Learnings for future iterations:**
  - Patterns discovered
  - Gotchas encountered
  - Useful context
---
```

## Consolidate Patterns

If you discover a **reusable pattern**, add it to the `## Codebase Patterns` section at the TOP of progress.txt:
```
## Codebase Patterns
- Pattern description
```

## Update AGENTS.md Files

Before committing, if you discovered reusable knowledge, add it to nearby AGENTS.md files.

## Project-specific notes

- The project root is also accessible via symlink at `ai-levitan/` which points to `levitan/`
- Always activate `.venv` before running any commands
- Russian-language project (HH.ru agricultural calls) - use Russian where appropriate
- The project has a bifucated structure: `ai-levitan/` is a doc facade, real code in `levitan/`
- CRM CSV data at `data/campaigns/csv/all_contacts_2026.csv`
- `scripts/dialer_bot.py` is the main Telegram bot (1837 lines)

## Quality Requirements

- ALL commits must pass: `source .venv/bin/activate && python3 -m pytest tests/ -v`
- Do NOT commit broken code
- Keep changes focused and minimal
- Follow existing code patterns

## Stop Condition

After completing a user story, check if ALL stories have `passes: true`.
If ALL stories are complete and passing, reply with:
<promise>COMPLETE</promise>

If there are still stories with `passes: false`, end your response normally.

## Important

- Work on ONE story per iteration
- Commit frequently
- Keep CI green
- Read the Codebase Patterns section in progress.txt before starting
