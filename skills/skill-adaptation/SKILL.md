---
name: skill-adaptation
description: Adapt external AI-agent skills (Auto-Company, Claude Code, Codex) to Hermes multi-profile structure.
version: 0.1.0
author: Erik03132, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skills, adaptation, import, external, workflow]
    related_skills: [hermes-agent-skill-authoring]
---

# Skill Adaptation

Adapt skills from external AI-agent frameworks (Auto-Company, Claude Code, Codex,
OpenCode) to our Hermes + 6-profile structure. Use when importing a skill from
an external repo, or when the user says "adapt this skill" / "port this skill".

## When to Use

- User links an external AI-agent skill/repo and says "adapt this" / "port this"
- ACTIVE_TASKS has an "adapt external skill" task
- A new skill is needed that mirrors an existing external pattern
- Don't use for: writing skills from scratch (use hermes-agent-skill-authoring),
  or for skills that don't map to our profile structure

## Prerequisites

- Source skill files accessible (GitHub raw URLs, local clone, or paste)
- Target profile identified (sherlock/femida/defender/marketer/financier/health)
- Git workspace clean enough to commit the new skill

## Procedure

### 1. Fetch original files

```bash
curl -sL "https://raw.githubusercontent.com/<owner>/<repo>/<path>/SKILL.md" -o original.md
```

Grab supporting files too: `scripts/`, `references/`, `templates/`.

### 2. Analyze structure

Identify:
- Frontmatter format (ours: `---` + name/description/argument-hint/disable-model-invocation)
- Tool references (Claude Code `Task tool` → our `delegate_task`)
- Agent/role names (`.claude/agents/*` → our 6 profiles)
- Source/tool dependencies (web-scraping → our web_search/web_extract)
- Output paths (`~/.claude/research_output/` → our `projects/hh-ai-agent/docs/outbox/`)

### 3. Adapt content

Apply substitutions from `references/adaptation-patterns.md`:
- Replace external tool names with Hermes tools
- Replace external agent names with our profiles
- Replace external sources with ours (HH API, Kwork, Supabase, GitHub, arXiv)
- Adjust file paths to our conventions
- Remove emojis, marketing language, framework-specific boilerplate
- Translate non-English text

### 4. Create in-repo structure

```
skills/<name>/SKILL.md
skills/<name>/references/    # methodology, patterns
skills/<name>/scripts/       # validation, utilities
```

Frontmatter must follow Hermes hardline:
- `name`: lowercase, hyphens, ≤64 chars
- `description`: ≤60 chars, one sentence, ends with period
- `argument-hint`: CLI-style usage hint
- `disable-model-invocation: true` (for multi-agent skills)

### 5. Create runtime copies

```bash
# Mirror to ~/.hermes for skill_view visibility
mkdir -p ~/.hermes/skills/<name>/{references,scripts}
cp skills/<name>/SKILL.md ~/.hermes/skills/<name>/
cp -r skills/<name>/references/. ~/.hermes/skills/<name>/references/
cp -r skills/<name>/scripts/. ~/.hermes/skills/<name>/scripts/

# Create chief bundle
cat > ~/.hermes/profiles/chief/skill-bundles/<name>.yaml << EOF
name: <name>
skills:
- <name>
EOF
```

### 6. Update router and task tracker

- Add row to `skills/skill-router.md` (in both repo and `~/.hermes/skills/`)
- Update ACTIVE_TASKS.md status to ✅ ДОСТАВЛЕН

### 7. Commit

```bash
git add skills/<name>/ skills/skill-router.md ACTIVE_TASKS.md
git commit -m "skills: add <name> (adapted from <source>)"
```

Pre-commit hooks will run (ruff, gitleaks, no-secrets). If they fail on
unrelated files, scope the commit to only your files.

## Pitfalls

- **Pre-commit hook drift**: ruff/format fixes can touch unrelated files. Always
  `git add` only your files, not `git add -A`.
- **Protected skills**: `hermes-agent-skill-authoring` and other bundled skills
  cannot be patched. Create a new umbrella instead.
- **Stale copies**: `~/.hermes/profiles/*/skills/` can hold old versions. Delete
  duplicates when updating a skill.
- **Path assumptions**: External skills hardcode `~/.claude/`, `~/Documents/`, etc.
  Replace with our `projects/<project>/docs/outbox/` convention.
- **Bundle missing**: Without the chief bundle, the skill won't appear in
  `/expert-council` invocations.

## Verification

- [ ] `skill_view(name="<name>")` returns the new skill
- [ ] Row present in `skill-router.md`
- [ ] ACTIVE_TASKS.md updated to ✅ ДОСТАВЛЕН
- [ ] `~/.hermes/skills/<name>/SKILL.md` exists and is identical to repo
- [ ] Chief bundle exists at `~/.hermes/profiles/chief/skill-bundles/<name>.yaml`
- [ ] Pre-commit passes (or failures are scoped to unrelated files)
