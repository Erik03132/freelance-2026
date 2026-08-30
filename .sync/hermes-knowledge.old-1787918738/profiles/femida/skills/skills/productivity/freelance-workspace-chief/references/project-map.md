# Project Map & Infra Facts — freelance-2026

## Active projects (snapshot; verify against chp.md before reporting)
| Project | Path / group | What it is | Notes |
|---------|--------------|------------|-------|
| AI bureau | umbrella (`ai-bureau/`) | Umbrella for voice agents | Levitan/AVM (local voice manager, pre-product, unstable) + Angela/ai-eggs (Mango outbound, working) |
| Sinergy | `projects/sinergy/` | Idea validation, Blender agents (Builder/Optimist/Skeptic) | Deployed to Vercel, prod alive (17.08). Blender ~3-5 min/run |
| OmniRoute | VPS model router | Routes LLM calls across free-model cascade | VPS 217.149.23.113:20128. NAT-redirect bug fixed 17.08. 26 free models |
| Svo-start / AI Grant Portal | `svo-start/`, `ai-grant-portal-temp/` | Grant applications | In work |
| HH AI Agent | `projects/hh-ai-agent/` | HH.ru auto-apply bot (Playwright+Ollama+Aiogram) | 18 tests pass |
| ai-scout | `ai-scout/` | Content scraping / idea collection | Collector/Analyst/Curator |
| Фемида | legal agent (skill) | Legal expert (contracts, grants, compliance) | pravo.gov.ru only, cross-check, anonymize |
| dashboard | `dashboard/` | Metrics dashboard | — |

## Infra facts
- **VPS Timeweb**: 72.56.38.19 (root@, SSH key `.ssh_agent_key` in workspace root).
  NOTE: chp.md later references 217.149.23.113 as the OmniRoute/VPS IP — verify
  which IP is current before any server action. Memory reports 217.149.23.113
  for OmniRoute dashboard, 72.56.38.19 as the main Timeweb VDS.
- **SSH access**: only via US-proxy HTTP CONNECT (172.120.21.141:64468/64469);
  direct ports closed. VPS RAM ~1.9GB (82-88% used, omniroute ~700MB);
  OOM-kills npm install → use `NODE_OPTIONS=--max-old-space-size=700`.
- **NAS Synology DS720+**: 192.168.0.107 (chp.md also shows .102 once) —
  `erik03132`. Backup target in finish-day Phase 4.
- **GitHub**: Erik03132/freelance-2026 — was PUBLIC, 02.08.2026 live keys leaked
  (gitleaks), now PRIVATE, keys rotated. Treat any historical secret as burned.
- **OmniRoute dashboard**: http://217.149.23.113:20128 (password in VPS
  `/root/.omniroute/.env`).
- **Proxy**: US-proxy 172.120.21.141:64468 (HTTP CONNECT) / 64469 (SOCKS5).
  Chrome needs CDP mode (won't take creds in --proxy-server).

## Recurring pitfalls (from chp.md)
- OpenRouter 403 "security policy" after heavy free-traffic from working IP —
  check key at openrouter.ai; fallback tier at risk.
- Blender speed 3-5 min/run; options: fast-model-first or async validation.
- OpenCode plugin complexity_hint — live trigger never verified.
