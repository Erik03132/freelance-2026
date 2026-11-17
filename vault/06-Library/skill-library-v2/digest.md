# Skill Library v2 — Universal Dynamic Skills for Hermes Agents

**Category:** Architecture / Multi-Agent / Skills  
**Date:** 2026-08-23  
**Project:** `freelance-2026` / Hermes Profiles  
**Sources:**
- `coreyhaines31/marketingskills` (60k+ stars, 50+ skills, MIT)
- `dailyprompts.ru` (planned)
- ADR: `vault/04-Decisions/2026-08-23-skill-library-v2.md`
- Lessons: `vault/03-Lessons/2026-08-23-skill-library-v2-lessons.md`

---

## Summary

**Skill Library v2** replaces static profile-bound skills with a federated, tag-based dynamic library:

```
External Sources (GitHub + dailyprompts.ru)
         ↓
    Sync Worker (cron 03:00 MSK)
         ↓
    ~/freelance-2026/vault/06-Library/skills-catalog/
         ↓
    Cache → ~/.hermes/profiles/personal/cache/skills/
         ↓
    Agents query by tag → load only needed skills
```

### Agent ↔ Tag Mapping

| Agent | Tag | Primary Source |
|-------|-----|----------------|
| Marketer | `#marketing` | `coreyhaines31/marketingskills` (50+ skills) |
| Sherlock | `#research` | `simonw/llm` + `dailyprompts.ru/research` |
| Femida | `#legal` | Custom `femida-skills` |
| Defender | `#security` | Custom `ai-defender-skills` |
| Financier | `#finance` | Custom `financier-skills` |
| Health | `#health` | Custom `health-skills` |

### Key Principles

1. **No full downloads** — agents fetch only skills matching their task tags
2. **Always fresh** — daily sync via cron
3. **Offline cache** — local copy for resilience
4. **Cross-references preserved** — skill dependency graph maintained
5. **product-marketing.md** — shared context foundation (per marketingskills pattern)

### Marketing Skills (coreyhaines31/marketingskills)

50+ skills across 8 categories:
- **SEO & Content:** seo-audit, ai-seo, programmatic-seo, schema, content-strategy, link-building, aso, site-architecture
- **CRO:** cro, signup, onboarding, popups, paywalls
- **Content & Copy:** copywriting, copy-editing, cold-email, emails, social, video, image, sms
- **Paid & Measurement:** ads, ad-creative, analytics, conversion-tracking, ab-testing, attribution
- **Growth & Retention:** referrals, free-tools, co-marketing, community-marketing, churn-prevention, lead-magnets
- **Strategy & Monetization:** marketing-plan, pricing, launch, marketing-ideas, marketing-psychology, reverse-engineer-marketing, competitor-profiling, competitors, directory-submissions, marketing-council, marketing-loops, offers
- **Sales & RevOps:** revops, sales-enablement, prospecting
- **Public Relations:** public-relations, influencer-marketing, events

**Installation:** `npx skills add coreyhaines31/marketingskills` (official CLI) — we build Hermes-native bridge instead.

### Next Steps

1. Build sync worker in `freelance-2026/projects/skill-library-bridge/`
2. Configure cron (03:00 MSK daily)
3. Integrate with Marketer agent (tag `#marketing`)
4. Extend to 5 remaining agents
5. Add `dailyprompts.ru` feed when available