---
name: secret-rotation
description: "Rotate a leaked API key across .env files safely."
---

# Secret Rotation (leaked-key recovery)

## When to use
- User pasted a real key into chat (Hermes chat is persisted, so treat it as leaked).
- A `.env.example` or git history contains a real key.
- User says "I revoked the key, now replace it everywhere."

## HARD RULES (from this user)
- Never put the new or old key in chat output. Read it from a local file (`/tmp/.new_key_tmp`), operate on disk only.
- Never `echo` the key. Use `cut -c1-30` for safe prefix verification only.
- Keys are read from env (`os.getenv("OPENROUTER_API_KEY")`), so you edit `.env*` files, NOT source code.
- Do not edit network/proxy config without explicit per-step approval (user is sensitive about losing internet).

## Working technique (validated this session)
1. User writes the new key to a local file (NOT chat):
   `cat > /tmp/.new_key_tmp <<'EOF'`
   `OPENROUTER_API_KEY=sk-or-v1-...full...`
   `EOF`
2. Scan all candidate `.env*` (whole-tree glob) plus known daemon env (`~/.omniroute/.env`).
3. Whole-file regex replace, NOT line-by-line. `.env` values can be multiline (e.g. `KEY=val` followed by `DB_URL='...'` with embedded newlines), so `readlines()` splits wrong. Use `re.compile(r"OPENROUTER_API_KEY=sk-[A-Za-z0-9._\-]{10,}")` and `re.sub` on the full text.
4. Exclude placeholders: skip `your_key`, `<...>`, `${...}`, `***` (masked). The regex `sk-[A-Za-z0-9._\-]{10,}` naturally excludes those.
5. Idempotent + `--dry-run`: first run prints files-to-change without writing; second run writes.
6. Verify: `grep -rl "<old_key_fragment>" --include=".env*" <root>` must return 0; `grep -rho "OPENROUTER_API_KEY=sk-or-v1-[A-Za-z0-9]\{1,6\}"` shows the new prefix is present.

## Pitfalls hit (encode these)
- `hermes config set ... 'null'` stores the STRING 'null', not a deletion. Use `hermes config unset <path>` to remove a key.
- localhost `curl` to OmniRoute (:20128) fails because `http_proxy=socks5h://...` routes localhost too. Prefix with `env NO_PROXY="127.0.0.1,localhost" no_proxy="127.0.0.1,localhost" curl ...`.
- OpenRouter models in OmniRoute need slug `openrouter/<slug>`, not `<slug>`.
- `.env.example` files sometimes contain REAL keys (leak). Rotate them too.
- **Regex class MUST include `.` and `_` for modern keys.** `sk-or-v1-...` and OpenAI-style keys contain dots and underscores. A class like `[A-Za-z0-9\-]` (no dot) silently fails to match `sk-or-v1-...` → zero files changed, no error. Use `[A-Za-z0-9._\-]{10,}`.
- **Scan with `re.sub` on the WHOLE file text, not line-by-line.** `.env` values can span multiple lines (a `KEY=val` line immediately followed by `DB_URL='...'` with embedded `\n`), so `readlines()` splits a logical key line in two and the regex never matches. Read `open(path).read()`, `re.sub`, write back.
- **CRLF / trailing `\r` breaks matching.** If the file has Windows line endings, the captured key string ends with `\r` and `{10,}` quantifier may fall short; also `unit.startswith("рубл")` style checks misbehave. If a dry-run reports 0 files but the key is visibly present, check for `\r` via `cat -A`.
- **Pluralization/unit capture bug:** when rewriting `рублей` the regex `рубл[ейяя]` matches only `рубле` (drops the trailing `й`); the leftover `й` then doubles. Use `рубл[еаяй]*` to swallow the whole word. (This bit us in `text_humanizer._ru_number_to_words` but the lesson generalizes to any unit-suffixed token replacement.)
- **`/tmp/.new_key_tmp` is ephemeral** — cleared on reboot/relogin. If you return to a later session and the file is gone, re-read the key from any local `.env` that already has it (e.g. `grep '^OPENROUTER_API_KEY=' ai-grant-consalt/.env`) rather than asking the user to re-paste. To push to VPS, source the key into a shell var and `sed -i` over SSH (key travels in stdin, never in the process arg list / chat).

## Local vs VPS split
- Local `.env*` in `~/freelance-2026`: the agent can edit directly.
- VPS (`~/.omniroute/.env`, project `.env`): **reachable only when Igor's VPN is OFF.** With VPN on, traffic egresses abroad and the RF-hosted VPS geo-blocks / times out (100% packet loss on ping, SSH timeout). The fix is Igor turning the VPN off — then `ping` and `ssh -p 22 root@217.149.23.113` work from his Mac, and the agent (same machine) can SSH in via the local key `~/.ssh_agent_key`.
- Working push pattern (validated 2026-08-22): source the key locally, pipe a `sed -i` over SSH so the key travels in stdin, never in the command string or chat:
  ```bash
  LOCAL_KEY=$(grep '^OPENROUTER_API_KEY=' /Users/igorvasin/freelance-2026/ai-grant-consalt/.env | cut -d= -f2-)
  ssh -i /Users/igorvasin/freelance-2026/.ssh_agent_key -o StrictHostKeyChecking=no root@217.149.23.113 bash -s <<EOF
    sed -i "s|^OPENROUTER_API_KEY=.*|OPENROUTER_API_KEY=${LOCAL_KEY}|" ~/.omniroute/.env
  EOF
  ```
- Do NOT bake the key into chat. If you cannot reach the VPS, hand the user the exact `sed`/nano command instead.

## Script
See `scripts/rotate_env_key.py` — re-runnable: reads the new key from `/tmp/.new_key_tmp`, dry-run by default, whole-file replace, skips placeholders.
