---
name: rf-split-proxy-routing
description: Route RF services direct, foreign via Igor's SSH SOCKS.
---

# RF ↔ US split routing (Igor's Mac)

## Topology

```
RF services   (bitrix24.ru, mango-office, incubird.bitrix24, b24-*.bitrix24)
    └── DIRECT, no VPN            ← via NO_PROXY / no_proxy

Foreign services (OpenRouter, Gemini, зарубежные банки/API)
    └── SOCKS5 via SSH tunnel → 127.0.0.1:64468 → VPS → US node
```

- The live forward is **127.0.0.1:64468** (SSH `-L` launched by `com.antigravity.usproxy-tunnel.plist`, an ssh tunnel to the Timeweb VPS `217.149.23.113` using `~/freelance-2026/.ssh_agent_key`). Creds: `Q3NeJXTY:dsBaWh2L`.
- A second convention is a local HTTP→SOCKS bridge `proxy_bridge.py` on **127.0.0.1:8888** (wraps the same SOCKS). Often NOT running; 64468 is the live one.
- Do **NOT** point at the external node `172.120.21.141:64469/64468` directly from the Mac — a comment in `.zshrc` warns it does NOT work; the tunnel's loopback is what functions.

## Key env (global, in ~/.zshrc)

```bash
export HTTP_PROXY="http://Q3NeJXTY:dsBaWh2L@127.0.0.1:64468"
export HTTPS_PROXY="http://Q3NeJXTY:dsBaWh2L@127.0.0.1:64468"
export ALL_PROXY="http://Q3NeJXTY:dsBaWh2L@127.0.0.1:64468"
export NO_PROXY="localhost,127.0.0.1,bitrix24.ru,incubird.bitrix24.ru,b24-mjxvhq.bitrix24.ru,app.mango-office.ru"
```

`~/.proxy_funcs.sh` provides `proxy` / `proxyOn` / `proxyOff`, `proxyCheck`, `bridgeOn/Off/Status`, `proxyComet`/`proxyMask`. `~/.proxy_secret` holds node creds.

## Diagnostics

```bash
# direct (should be a RU/foreign exit from actual ISP)
curl -s --max-time 8 --noproxy '*' https://ipinfo.io/json
# via tunnel
curl -s --max-time 8 -x socks5h://127.0.0.1:64468 https://ipinfo.io/json
# is the tunnel listening?
lsof -nP -iTCP:64468 -sTCP:LISTEN    # ssh PID = the usproxy-tunnel LaunchAgent
launchctl list | grep -iE "usproxy|gateway|bridge"
```

A node/GeoIP lookup returning `185.77.216.28 (Helsinki, FI)` was observed for the direct path — don't assume "FI = broken"; that's the actual host egress.

## Pitfalls

1. **Edit dotfiles with the `patch` tool, never ad-hoc Python heredoc string surgery.** A mid-session attempt to insert a proxy block before `function opencode() {` used `s = s[:idx] + marker + s[idx:]` and produced `function opencode() {function opencode() {` — it inserted the *search string itself* as a literal, corrupting the function. Verify every string-edit lands correctly, and always `cp ~/.zshrc ~/.zshrc.bak-$(date +%Y%m%d-%H%M%S)` first.
2. **Global vs function-scoped proxy.** `function opencode() { export ... }` localizes the proxy to that command. If RF reports "services still not proxied", the exports must be global (top of `.zshrc`), not inside a function.
3. **RU services must hit NO_PROXY**, or they'll be forced through the US exit and fail to open — that's the «flapping» symptom: same machine, `proxy on` works for foreign but breaks RU, then `proxy off` fixes RU but not foreign. Correct split is DIRECT for RU + SOCKS for everything else, not a toggle.
4. **Two conventions exist** (SSH tunnel 64468 vs python bridge 8888) — check both with `lsof` before concluding the proxy is down.