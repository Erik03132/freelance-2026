# Hermes Agent tooling patterns (validated 2026-08-21/22)

Patterns for the Hermes Agent desktop client that the Chief can apply or
recommend. Most are config/CLI, no code edits.

## 1. `hermes kanban` as a structured replacement for ACTIVE_TASKS.md

`ACTIVE_TASKS.md` is a 1100+ line hand-edited file. For task tracking with
real status, use the built-in kanban board.

- Init: `hermes kanban init` (creates `~/.hermes/kanban.db`).
- Board per workstream: `hermes kanban boards create <slug> --name "..." --icon "🧠" --switch`.
- Add task (idempotent!): `hermes kanban create "<title>" --body "<note>" --assignee default --idempotency-key <unique>`.
  - `--idempotency-key` prevents duplicate creation on re-run — ALWAYS pass it.
  - Omit `--priority` (it errors on string values like `high`; leave default).
- Block a task up front: add `--initial-status blocked` to `create`.
- Close: `hermes kanban complete <task_id> [<task_id>...] --result "..."`.
- List: `hermes kanban list`.
- Tasks sit in `ready`/`running` until a gateway picks them up — that's fine for
  a tracking board; you don't need the gateway running to track status.
- Validated: board `freelance-2026` created, ES-22/23, ES-15, ES-18/19, ES-24,
  ES-25/27, Hermes-P0 closed; ES-12/14 created `blocked`.

## 2. `hermes fallback add` is INTERACTIVE-ONLY (pitfall)

There is NO non-interactive path. `hermes config set 'fallback.providers' '[...]'`
saves the key but Hermes ignores it (`fallback list` stays empty, warning
"not a recognized config key"). The only working method is the interactive
picker:

```bash
hermes fallback add   # in a real terminal (TTY), not piped
# pick provider+model, repeat for the chain
```

Recommended chain (resilience when the primary model rate-limits):
1. `omniroute` → `auto/best-coding`
2. `omniroute` → `nous/Hermes-4-405B`
3. `omniroute` → `auto/free-coding`

This directly prevents "Mustay stopped working" outages when the primary
(`openai/gpt-5.6-sol`) is overloaded.

## 3. `hermes insights` / `hermes approvals suggest`

- `hermes insights --days 7` — token/cost breakdown. Cheap, read-only, run anytime.
- `hermes approvals suggest` shows repeated approved commands; apply with
  `hermes approvals suggest --apply 1,3` to stop re-prompting on repeats
  (e.g. `python3 -c`, `hermes cron create`). Safe — these are the user's own commands.

## 4. `hermes security audit` needs proxy

Hermes OSV.dev scan times out by default (US-hosted). Run with the foreign
proxy exported: `env HTTPS_PROXY=http://<user>:<pass>@127.0.0.1:64468 hermes
security audit`. (See `igor-proxy-network` skill — foreign resources need VPN/proxy ON.)
