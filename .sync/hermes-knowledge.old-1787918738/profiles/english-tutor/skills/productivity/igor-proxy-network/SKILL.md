---
name: igor-proxy-network
description: "Handle Igor's macOS proxy/VPN split-routing safely."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [network, proxy, vpn, macos, split-routing, igor-infra]
    homepage: ""
---

# Proxy / VPN split-routing (Igor's Mac)

Igor is in RF. He needs **simultaneously**: RF services direct (no proxy) and foreign services via a US proxy. The pain he reports is "метание" — manually flipping `proxyOn`/`proxyOff` per task, exacerbated by an unstable GUI VPN client (Express).

## The working architecture (verified 2026-08-21)

- **HTTP(S) proxy via SSH tunnel (the reliable auto-up path):** LaunchAgent `com.antigravity.usproxy-tunnel` holds `127.0.0.1:64468` — an ssh `-L` forward VPS→US. It auto-starts at login. This is the endpoint to point foreign apps at:
  `http://<USER>:<PASS>@127.0.0.1:64468`  (or bare `127.0.0.1:64468`)
- **Direct SOCKS5 node:** `172.120.21.141:64469` (auth user:pass). Works for ad-hoc `curl -x socks5h://...`.
- **Credentials:** DO NOT hardcode. Read from `~/.proxy_secret` (`PROXY_IP`, `PROXY_PORT`, `PROXY_USER`, `PROXY_PASS`). Also sourced by `~/.proxy_funcs.sh`, which `.zshrc` sources (`proxy`/`proxyOn`/`proxyOff`/`proxyCheck` aliases). `NO_PROXY` already lists RF services: `bitrix24.ru`, `app.mango-office.ru` etc → they go direct.
- `opencode()` function in `~/.zshrc` sets `HTTP_PROXY/HTTPS_PROXY/ALL_PROXY=http://<user>:<pass>@127.0.0.1:64468` with the same `NO_PROXY` — the foreign-services path.

## Diagnosing his proxy (reusable technique)

- **SOCKS vs HTTP endpoint matter.** Some endpoints are SOCKS5, others HTTP(S) proxy. Wrong type → `exit 28`/timeout after hanging, not a clean error. Probe both:
  - SOCKS: `curl -s -x socks5h://<auth>@<host>:<port> https://api.ipify.org`
  - HTTP: `curl -s -x http://<auth>@<host>:<port> https://api.ipify.org`
- Success = the US IP (e.g. `172.120.21.141`). `--noproxy '*'` shows the direct exit (Helsinki `185.77.216.28` on his setup).
- Who/what is listening: `lsof -nP -iTCP:<port> -sTCP:LISTEN` (shows PID — ssh vs python vs nothing).
- Verify a LaunchAgent is alive: `launchctl list | grep <label>` + `ps aux | grep` the ProgramArguments binary.

## PITFALL — "bridge" that is a TCP pipe is NOT a proxy

`~/proxy_bridge.py` (wrapped by `~/proxy_bridge_manager.sh`, alias `bridgeOn`, port 8888) reads ONE hardcoded `DEST_HOST:PORT`, opens a raw socket, and pipes bytes. It forwards only to that one destination and does **not** speak SOCKS/HTTP CONNECT — so **`-x socks5h://127.0.0.1:8888` and `-x http://127.0.0.1:8888` both fail**, it is useless for routing app traffic. Don't add it as a LaunchAgent or "autostart bridge"; the real path is the 64468 HTTP tunnel. (Herd instinct: "bridge up = stable proxy" is wrong for this one.)

## SAFETY PROTOCOL (hard requirement — Igor explicitly demanded it)

User's correction was explicit: *"не напортачь", "если на автомате и неконтролируется — я останусь без интернета", "если трабл — не знаю что делать".* Treat this as non-negotiable when editing ANY network/proxy/shell config:

1. **Backup first.** `cp ~/.zshrc ~/.zshrc.bak-$(date +%Y%m%d-%H%M%S)` before any edit. Same for any config touched.
2. **One reversible change at a time.** Never batch automated edits to networking into the background. Never `export` a new proxy globally inside an unrelated function.
3. **Verify each step** with a real probe (`curl -x ... https://api.ipify.org`) and a listener check before declaring success.
4. **Give Igor a revert snippet in the reply** — exact commands to undo / check / restart (e.g. the `launchctl load/unload` shpargalka). He does not know what to do on failure; hand him the commands.
5. **Pause and ask** before making a change that could plausibly cut internet. An unattended "auto" full-internet change is the exact thing he fears.

## PITFALL — RF-hosted VPS is unreachable WHILE VPN is ON

Igor's VPS `217.149.23.113` (root@, SSH port 22) is a Russian-hosted box. When his VPN/auto-tunnel is active, **all** traffic egresses abroad, so the VPS sees a foreign source and geo-blocks it: `ping` returns 100% packet loss, `ssh` times out. Turning the VPN OFF makes it reachable instantly (`ping` ~40ms, `ssh -p 22` returns OK).

- Symptom to recognize: "I can't reach my VPS / SSH connection timed out / 100% packet loss" while VPN is on → ask "is your VPN on?" before debugging ports or tunnels.
- The VPS is NOT behind a custom SSH port (22 works once VPN is off). Don't waste cycles scanning 2022/2222.
- The agent shares Igor's Mac, so once he disables VPN the agent can also SSH in via the local key `~/.ssh_agent_key` (path: `~/freelance-2026/.ssh_agent_key`).
- This is the inverse of the foreign-services rule: RF resources (VPS, Bitrix, Mango, Yandex) need VPN OFF / direct; foreign resources (OpenRouter, Gemini) need VPN / proxy ON. They are mutually exclusive on one connection — there is no single mode that reaches both.
- Note: with VPN off, foreign AI services (OpenRouter/Gemini via Hermes OmniRoute) stop working — that's expected; re-enable VPN after VPS work.



Inserting text via a Python `s[:idx]+block+s[idx:]` where `idx` targets the line holding `function opencode() {` corrupts the file — it produces `function opencode() {function opencode() {` (marker glued inside the line). Any such targeted insertion onto the opening brace of a function is fragile. Prefer a fresh-line insertion anchored on a stable unique line, and ALWAYS `zsh -n ~/.zshrc` afterward; on any doubt `cp` the backup back over it.