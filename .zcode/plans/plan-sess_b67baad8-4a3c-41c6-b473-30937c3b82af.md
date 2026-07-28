# Harmonized Structure Plan: Open Code + ZCode

## The Core Problem

You have two tool ecosystems sharing one workspace:
- **Open Code** discovers skills from `.opencode/skills/<domain>/` (configured in `.opencode.jsonc`)
- **ZCode** discovers skills from `foundation/skills/<domain>/` and `~/.agents/skills/`
- Both need to coexist without duplicating or moving files constantly

## The Solution: One Source of Truth + Symlinks

### 1. Canonical Skill Location: `foundation/skills/<domain>/<name>/SKILL.md`

**All skills live here permanently.** This is the single source of truth.

Open Code's `.opencode/skills/` directory is **eliminated**. Instead, it will symlink into `foundation/skills/`.

### 2. Open Code ↔ Foundation Bridge

**Action:** Edit `.opencode.jsonc` to add `foundation/skills/` as a skill path, OR replace `.opencode/skills/` with symlinks pointing into `foundation/skills/`.

The cleanest approach — symlinks at `.opencode/skills/`:
```
.opencode/skills/
├── agents -> ../../foundation/skills/code/  (symlink)
├── brand-voice -> ../../foundation/skills/text/ (symlink, future)
├── deployment-procedures -> ../../foundation/skills/code/ (symlink, future)
├── geo-fundamentals -> ../../foundation/skills/code/ (symlink, future)
└── ... (one per domain)
```

Wait — simpler: just add `foundation/skills/` to the skill paths in `.opencode.jsonc`:
```jsonc
{
  "skill": {
    "paths": [
      ".opencode/skills",
      "foundation/skills"
    ]
  }
}
```
This way Open Code scans both directories and finds all skills without symlinks.

**Decision needed:** Symlinks vs. dual-path config. Dual-path is cleaner.

### 3. ZCode ↔ Foundation Bridge

ZCode already discovers `foundation/skills/<domain>/` natively (it's in the workspace). No config change needed for skills.

For **agents** (subagent config like sherlock, shakespeare, etc.):
- Move `.opencode/skills/agents/<name>/SKILL.md` → `foundation/agents/<name>/SKILL.md`
- ZCode doesn't natively auto-discover these project-level agent files, but ZCode's plan/session tools can reference them as skills.
- Keep `.opencode/skills/agents/` as a symlink folder for Open Code compatibility.

### 4. Unified Directory Structure (Target State)

```
freelance-2026/
├── foundation/
│   ├── skills/                    # SKILLS — canonical, shared
│   │   ├── code/<skill>/SKILL.md
│   │   │   └── templates/, references/, scripts/
│   │   ├── text/<skill>/SKILL.md
│   │   ├── productivity/<skill>/SKILL.md
│   │   └── agents/<agent>/SKILL.md   # agent configs (sherlock, shakespeare, etc.)
│   └── agents/                    # AGENTS — agent definitions & reports
│       └── sherl-research/
│   └── libraries/                 # REUSABLE CODE LIBRARIES
│       ├── ai-components/
│       └── task-prioritizer/
│
├── .opencode.jsonc                # Open Code config — skill.paths includes "foundation/skills"
├── .opencode/skills/              # DEPRECATED → replace with symlinks or empty (Open Code now reads foundation/skills)
│   ├── agents -> ../foundation/skills/code/agents  (symlink, optional)
│   └── ... (symlinks)
│
├── projects/<name>/               # Active projects
│   ├── config/project.yaml
│   ├── project-skills/            # Project-local skill overrides/extras
│   └── src/, docs/
│
├── archive/                       # Closed projects
│
├── templates/                     # Templates (keep as-is + expand)
│   ├── project-skeleton/
│   ├── skill-skeleton/
│   └── agent-skeleton/
│
├── tools/                         # Organized tools (reorganize from scripts/)
│   ├── deploy/
│   ├── expect/
│   ├── media/
│   └── ...
│
├── _archive/patches/              # One-off fixes (keep as-is)
│
├── AGENTS.md                      # Workspace-level instructions (ZCode reads this)
├── ecosystem.config.cjs           # PM2 config (keep)
└── opencode.json                  # Legacy Open Code config (keep for compat)
```

### 5. Concrete Steps in Execution Order

**Step 1 — Update `.opencode.jsonc`** (one file):
Add `foundation/skills` to `skill.paths` so Open Code discovers skills from the canonical location.

**Step 2 — Migrate `.opencode/skills/agents/` → `foundation/skills/code/agents/`**:
Move the agent skill definitions from `.opencode/skills/agents/<name>/SKILL.md` into `foundation/skills/code/agents/<name>/SKILL.md`.
Then update `.opencode.jsonc` skill.paths so Open Code still finds them.

**Step 3 — Create `templates/skill-skeleton/` and `templates/agent-skeleton/`** (standardize what's there):
Currently `templates/project-skeleton/` and `templates/ai-agent-implementation/` only. Add proper skeleton structures.

**Step 4 — Create `tools/` subdirectories** from the flat `tools/` folder:
Reorganize existing scripts into categorized subdirectories (`tools/deploy/`, `tools/angela/`, etc.)

**Step 5 — Create empty `PROJECT_CONTEXT.md`** at root — auto-generated index for IDE.

**Step 6 — Create `_archive/patches/` is already there — no change.**

**Step 7 — Cleanup** (future):
- Remove `.opencode/skills/` (or keep as deprecated redirect)
- Remove `opencode.json` at root (already has `opencode.jsonc` as primary)

### 6. What Stays as-Is

- `foundation/` structure is perfect — no changes needed
- `projects/` structure is fine — each project has its `config/project.yaml`
- `archive/` is fine
- `_archive/patches/` is fine
- `agents/` inside foundation is fine

### 7. Key Decisions to Make

1. **Agent skills** (sherlock, shakespeare, marketer, etc.) — keep them under `foundation/skills/code/agents/` or create a new `foundation/skills/agents/` level? → Recommend: `foundation/skills/code/agents/` since they contain code-oriented agent configs.

2. **`.opencode/skills/`** — delete entirely (Open Code reads from `foundation/skills/` via config) or keep as symlinks? → Recommend: delete, just add dual-path to config.

3. **`opencode.json` at root** — keep or remove? → Recommend: remove (`.opencode.jsonc` is the primary).

4. **New folders needed?** → No new `foundation/skills/agents/` — agents go under `foundation/skills/code/agents/` (same pattern as code skills).