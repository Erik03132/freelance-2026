# Igor's proxy topology (as of 2026-08-21)

## Live tunnel (SSH)

- PID 1108, `/usr/bin/ssh -N -L 127.0.0.1:64468:172.120.21.141:64468 -i ~/freelance-2026/.ssh_agent_key ... root@217.149.23.113`
- Listens on `127.0.0.1:64468`. Verified `lsof -nP -iTCP:64468 -sTCP:LISTEN`.
- **Bridge 8888**: the local HTTP→SOCKS bridge (`proxy_bridge.py`) is **NOT listening** — it is the *second* convention and only used when manually started.

## Env (global, in ~/.zshrc)

```bash
export HTTP_PROXY="http://user:pass@127.0.0.1:64468"
export HTTPS_PROXY="http://user:pass@127.0.0.1:64468"
export ALL_PROXY="http://user:pass@127.0.0.1:64468"
export NO_PROXY="localhost,127.0.0.1,bitrix24.ru,incubird.bitrix24.ru,b24-*.bitrix24.ru,app.mango-office.ru"
```

## Verified working commands

```bash
# Direct (must be a RU/foreign IP)
curl -s --max-time 8 --noproxy '*' https://ipinfo.io/json
# Through tunnel
curl -s --max-time 8 -x socks5h://127.0.0.1:64468 https://ipinfo.io/json
```

## Diagnosis

- Split routing **works at SSH level**: tunnel 127.0.0.1:64468 is UP.
- SOCKS creds: `Q3NeJXTY:dsBaWh2L` → node.
- RU-domains in NO_PROXY are respected only when curl (and most terminal apps) are run; GUI apps (browsers, desktop clients) **do NOT read zsh exports** — they need either a switchy/系统-proxy-level config pointing to the same 127.0.0.1:64468, or a system-wide daemon.
- The **status 8888 is NOT a broken proxy** — it's simply a second, optional bridge that is currently down.
- If a «service doesn't open without VPN / hangs», first `lsof` both 64468 and 8888; then check `NO_PROXY`.

## Pitfalls

- Unit: RU → via tunnel → good; RU via RU → must remain DIRECT. That's the whole point of **NO_PROXY (direct, without proxy)**.
- **«Игорь в РФ: софт с РФ-нодой должен идти напрямую, иначе он через US-ноду и отвалится»** → the wifi-router may fail / «нога».
- To prevent "flapping" hands, **RU direct, foreign via SOCKS** is a single rule; t**ip is not a proxy that alternately fixes RU and breaks foreign services.
- **GUI apps on macOS do NOT read shell exports.**