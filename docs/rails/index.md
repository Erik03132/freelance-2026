# Rails Catalog — Enforcement Mechanisms

Status: `active` | `draft` | `shelved` | `deprecated`

| ID | Rail | Principle | Enforcement Mechanism | Status | Source Incident |
|----|------|-----------|----------------------|--------|-----------------|
| R01 | No direct push to main | Branch protection | GitHub branch protection rule | active | — |
| R02 | Ruff lint + format | Code style | pre-commit hook (ruff) | active | — |
| R03 | Tests for new code | TDD | pre-commit + CI gate | active | — |
| R04 | ADR for arch changes | Architecture decisions | pre-commit (commit-msg) | active | — |
| R05 | CLAUDE.md updated on bugfix | Learn from errors | pre-commit (commit-msg) | active | — |
| R06 | CONTEXT.md for domain terms | Shared vocabulary | pre-commit (commit-msg) | active | — |
| R07 | No secrets in code | Security | pre-commit + CI secret scan | active | — |
| R08 | Handoff for >10min tasks | Parallel work | AGENTS.md + commit-msg hint | active | — |
| R09 | Fresh LLM review on PR | Unbiased review | CI job (fresh session + checklist) | draft | — |
| R10 | Two-axis Review before merge | Standards + Spec | `/code-review` command + CI gate | draft | — |
| R11 | Eval suite before prompt/model change | AI quality | `pytest tests/eval_*.py` in CI | draft | — |
| R12 | Session summary → claude-mem | Cross-session memory | `finish-day` protocol | active | — |
| R13 | Decision → claude-mem | Architecture traceability | `finish-day` protocol | active | — |
| R14 | Bugfix → claude-mem + CLAUDE.md | Learn from bugs | pre-commit + `finish-day` | active | — |
| R15 | Scaffold self-improvement log | Agent improvement | `~/.config/opencode/docs/self_improve_log.md` | active | ADR-001 |
| R16 | Proxy policy for Russian services | Network reliability | `.env` + code guards | active | ADR-002 |
| R17 | OmniRoute for AI requests | Cost/latency optimization | `OPENAI_BASE_URL` env | active | — |
| R18 | Model tier cascade | Cost control | AGENTS.md tier rules | active | — |
| R19 | GeekNeural dedup for stable context | Token savings | `cached_read` tool | active | — |
| R20 | Gardeners (full-corpus scans) | Entropy control | Periodic `smart-search` + `finish-day` | draft | Article case 3 |
| R21 | PR template with required sections | Structured PRs | GitHub PR template + CI check | draft | Article case 1 |
| R22 | Fake in tests ≠ prod behavior | Test fidelity | Gardener scan + CI gate | draft | Article case 2 |
| R23 | Path filters in CI cover all PR classes | CI completeness | Gardener audit | draft | Article case 3 |
| R24 | Webhook snapshot timing | CI metadata freshness | Document + test | draft | Article surprise |
| R25 | Rail without doc = red | Rail traceability | CI gate (`rail_doc_gate.py`) | draft | Article failure |

---

## Enforcement Types

| Type | Examples | Reliability |
|------|----------|-------------|
| **Silent Gates** (deterministic, no human) | pre-commit, CI jobs, branch protection | 100% |
| **Lenses** (semantic checks before work) | CONTEXT.md, ADR check, GDPR registry | High |
| **Fresh Reviewer** (new LLM session + checklist) | `/code-review`, PR review job | High |
| **Gardeners** (periodic full-corpus) | Entropy scan, dead code, drift | Medium |
| **Ceremonies** (stage boundaries) | `start-day`, `finish-day`, sprint closure | Human-dependent |
| **Registries** (SSOT read at 3 points) | CONTEXT.md, CLAUDE.md, ADR/ | High if gated |

---

## Adding a New Rail

1. **Incident occurs** → record in `claude-mem` kind=bugfix/decision
2. **Design rail** with enforcement mechanism (prefer Silent Gate)
3. **Add to this table** with status `draft`
4. **Implement mechanism** (hook, CI job, script)
5. **Test on real PR** → promote to `active`
6. **Document in CLAUDE.md** if agent needs to know

---

## Self-Improvement Trigger (Target B)

Per ADR-001: Any of these signals → scaffold update → log in `self_improve_log.md`:
- Tier failure ≥2 times
- Eval regression
- Bugfix pattern repeats
- Architectural decision
- Feedback from human

Format: `[date] signal → update target → change → result`