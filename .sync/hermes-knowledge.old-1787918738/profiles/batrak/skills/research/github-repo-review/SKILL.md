---
name: github-repo-review
description: "Use for 'expert start-<url>' / 'разбери это репо'."
---

# GitHub-repo expert-review workflow (read-only)

The user's "expert start-<github-url>" trigger and the broader pattern
"выступи экспертом по <repo> / разбери это" maps to this workflow. Output is a
single one-pager in `~/freelance-2026/docs/solutions/<slug>.md` plus a patched
INDEX.md entry. Read-only: NO clone, NO install, NO run, NO skill install,
NO Docker pull. The user must explicitly say "делай" before any side-effect.

This skill is the operational handbook. It pairs with
`freelance-workspace-chief` (Chief, user-owned, read-only oversight) which
sets the role context. The Chief says "I am Hermes"; this skill says "here is
exactly how to do a repo review."

## Trigger phrases

- `expert start-<github-url>` (canonical, see Chief skill for batch variant)
- "выступи экспертом по <repo>"
- "разбери это репо / фичу / инструмент"
- "экспертный разбор <url>"

## Sequence (the actual recipe)

1. **README + landing page.** `web_extract(<github-url>)`. Long READMEs (>30 KB)
   get truncated head+tail; cached at `~/.hermes/cache/web/<host>-<hash>.md`.
   Page through with `read_file offset=N limit=200`. Don't try to swallow the
   whole thing.
2. **Tree discovery.** GET `https://api.github.com/repos/<owner>/<repo>/contents/`
   for root, then `/contents/<dir>` recursively. Returns JSON listing every
   file's `name`, `type`, `download_url`. Use this to find SKILL.md (often
   NOT at root — try `/contents/skills/`, `/contents/skills/<name>/`,
   `/contents/docs/`).
3. **Raw fetch.** `https://raw.githubusercontent.com/<owner>/<repo>/main/<path>`
   for direct file content. 404 returns an HTML `<pre>` body — treat the first
   non-JSON/non-text response as "not found", don't waste a follow-up.
4. **Pick 3–5 key files to actually read in full:**
   - `SKILL.md` (always — or its subdir equivalent)
   - `README.md` (selectively: HTTP API table, env vars, security model)
   - `server.py` / main entrypoint (if CLI or HTTP service)
   - `.env.example` (production-readiness signal)
   - `SECURITY.md` (scope of accepted vuln reports = trust signal)
   - `pyproject.toml` / `requirements*.txt` (deps weight)
   - Skip `.github/workflows/` unless the skill touches CI
5. **Don't read .py files >30 KB in full** — page through or extract
   class/function signatures. The point is ARCHITECTURE, not full audit.
6. **Write the one-pager.** Append at the end these three blocks every time:
   - **Конкретные правки в нашей системе** — numbered list of changes that
     would integrate the solution into our agents/projects. Always named
     agent (Шерлок/Кулибин/Angela/Botman) and concrete rule/file path.
   - **Что я НЕ буду делать без явного «да»** — explicit list of things
     the user must approve (clones, Docker pulls, .env edits, skill installs).
     This is the "Fixed ≠ Verified" principle applied to solutions.
   - **Следующие шаги (предлагаю, не делаю без команды)** — numbered 1..N
     next-step list. User responds with "делай" to unblock.
7. **Patch `docs/solutions/INDEX.md`** in the SAME call as the write — link
   under the "Решения / tools (свежие, hand-written)" section. If count
   changed, update the `(N)` in the section header.

## One-pager template (use verbatim)

```
# <repo-name> — <one-line subject>

**Что:** <license, stars/forks/commits, age, last activity>. Real files read:
<list concrete paths>.

**Суть (метод за 1 минуту):**
<2–5 lines — what it does, in our own words, not README paraphrase>

**Вес (диск):** <install size in MB/GB, what we lose if we put it on Mac vs VPS>

**Когда юзать у нас:**
| Слой / Сценарий | У нас применимо для |
| <category> | <specific agent + project> |

**Конкретные правки в нашей системе:**
<numbered list 1..N — file path + what changes>

**Риски/ограничения (экспертиза, авг-2026):**
<numbered list — honest, with code/cite where possible>

**Статус:** <кандидат / внедрить / не применять> + one-line reason.

**Следующие шаги (предлагаю, не делаю без команды):**
<numbered list 1..N>

**Что я НЕ буду делать без явного «да»:**
<bullet list of risky side-effects that need explicit "да">
```

## Pitfalls (learned the hard way)

- **README >50 KB:** don't `read_file path=... limit=2000` and try to parse
  all of it — it returns truncated with `next_offset`. Use `read_file
  offset=N limit=200` to page. Skim structure (headers) first, then read the
  sections you actually need.
- **SKILL.md not at root:** always check `/contents/skills/` and
  `/contents/skills/<name>/` before concluding "no skill". Same for `docs/`
  (vendor-notes.md often hides there). One project this session had it in
  `skills/remove-ai-marks/SKILL.md`, not at root.
- **`web_search` returns noise for niche repos:** 7★ repos with 2 commits may
  match unrelated GitHub searches. Skip search; go straight to
  `web_extract` of the repo URL.
- **"Latest commit 1 hour ago" ≠ mature:** GitHub landing page shows recency,
  not breadth. Cross-check with `commits` count and `contributors` count.
- **GitHub Languages % is rounded** to one decimal — for ~95% Python +
  PowerShell 1.8% + Shell 2.2%, treat the small numbers as informational
  only, don't infer tech stack from them.
- **README claims "no dependencies" but pyproject.toml says otherwise** —
  always cross-check.
- **Watermark/anti-detect tools** have legal/ethical pitfalls even when the
  README doesn't mention them — always check SECURITY.md for "Out of scope"
  sections, those signal what the maintainer won't defend.
- **Bundled/HTTP-client skills vs. codeful skills:** when a skill ships its
  implementation as a separate HTTP service (skill = `curl` + base64), the
  web-extract strategy MUST include the service's `server.py` / `Dockerfile`
  — the skill SKILL.md is then a thin client and tells you nothing about
  the actual architecture.
- **Heavy/optional profiles often have license traps** (CtrlRegen = no LICENSE
  upstream → never published to GHCR; SynthID-score = non-commercial
  research). Always check Docker profile section before recommending local
  build.
- **Vendor detector retirement:** if the upstream commits in the last 6 months
  delete a detector (e.g. Google SynthID-text retired Aug 2026), the tool
  may be a dead-end for that path. Note in risks.
- **Cross-profile guard:** `skill_manage(write_file=..., cross_profile=true)`
  refuses without explicit user direction. Default stays false. New skills
  belong in the active profile, not in a sibling.

## Comparison block (when 2+ reviews in one session)

After the second review in the same session, append to the second one-pager
(short table, 4–6 rows max):

```
**Сравнение с <prev> (только что разобрали):**
| Аспект | <prev> | <current> |
| Звёзды / зрелость | 7★, 2 коммита | 15.1k★, v0.5.0 |
| Назначение | реверс чужого API в CLI | снятие AI-провенанса |
| Архитектура skill | skill = код | skill = тонкий HTTP-клиент |
| Требования к агенту | нет (копи-паста в чат) | запущенный Docker (core) |
| Уровень этики | высокий (явные правила) | очень высокий (ethics.md + scope limits) |
| Где у нас полезно | Шерлок/Botman (интеграции) | Angela/Botman/AI-Scout (гигиена Layer A) |
```

Rows: зрелость, назначение, архитектура skill, требования к агенту,
уровень этики, где у нас полезно. User reads this to compare deltas
without flipping between files.

## Anti-patterns to avoid

- **Don't pretend to summarize a README you only extracted the head of.**
  Either read the whole thing (page through) or say "I read sections X, Y".
- **Don't recommend installing tools without weight + disk cost.** Always
  state MB/GB.
- **Don't promise "100% очистка / 100% скрытие" for any anti-detection
  tool** — vendor detection is an arms race, never settled.
- **Don't expand scope.** If the user asked for a repo review, don't
  side-quest into "and I also fixed your .env". Note in next-steps and stop.
- **Don't write to files outside `docs/solutions/` and `INDEX.md`** without
  explicit ask. The Chief is read-only.

## Verification

The note is done when:
- `docs/solutions/<slug>.md` exists and follows the template
- `docs/solutions/INDEX.md` has the new link, count updated
- The "Конкретные правки" block names specific agents + file paths
- The "Что я НЕ буду делать" block lists at least 2 risky items the user
  must approve
- The user has the three-block structure (правики / не буду / следующие
  шаги) so they can scan and reply with "делай" in one message