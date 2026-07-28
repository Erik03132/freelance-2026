# Project Context — Auto-Generated Index

## Repository Overview
Workspace for freelance AI projects — shared across Open Code and ZCode.

## Structure

| Path | Purpose |
|---|---|
| `foundation/skills/` | Canonical skills (shared across Open Code + ZCode) |
| `foundation/agents/` | Agent definitions (e.g., sherl-research) |
| `foundation/libraries/` | Reusable code libraries |
| `projects/<name>/` | Active projects |
| `archive/` | Closed projects |
| `templates/` | Project/skill/agent skeletons |
| `tools/` | Global scripts (categorized) |
| `.opencode.jsonc` | Open Code config (primary) |
| `ecosystem.config.cjs` | PM2 process config |
| `AGENTS.md` | (at ~/.zcode/) Global instructions |

## Open Code ↔ ZCode Bridge
- `.opencode.jsonc` `skill.paths` includes both `.opencode/skills` and `foundation/skills`
- Agent skills migrated from `.opencode/skills/agents/` → `foundation/skills/code/agents/`
- Both tools now share a single skill source of truth

## Active Projects
- ai-eggs
- ai-scout
- angel-backend
- hh-ai-agent
- levitan
- agent-lab
- ai-bureau

## Tools Categories
- `tools/deploy/` — deployment scripts
- `tools/backup/` — backup & sync
- `tools/expect/` — Expect automation (.exp)
- `tools/media/` — media processing
- `tools/ops/` — operations / admin
- `tools/angela/` — Mango Office integration
- `tools/geekneural/` — GeekNeural tools
- `tools/scripts/` — utility scripts
- `tools/transcribe-mcp/` — transcription MCP
- `tools/omni-auto-router/` — auto-router
