#!/usr/bin/env python3
"""omniroute-live — живой мониторинг реальных моделей OmniRoute.

Показывает в одном окне: активные запросы (модель/провайдер/статус/время),
последние завершённые, сводку по моделям за сессию.

Использование:
  omniroute-live                 # живой режим (обновление каждые 2с)
  omniroute-live --once          # один снапшот и выход
  omniroute-live --since 300     # сводка за последние 300 сек

Переменные:
  OMNI_BASE=http://127.0.0.1:20128
  OMNI_KEY=<api key>             # или флаг --api-key
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from collections import Counter, defaultdict

BASE = os.environ.get("OMNI_BASE", "http://127.0.0.1:20128")
KEY = os.environ.get("OMNI_KEY", "")
LOGS_URL = f"{BASE}/api/usage/call-logs"
REFRESH = 2.0


def fetch(params: dict, key: str = "") -> list:
    query = "&".join(f"{k}={urllib.request.quote(str(v))}" for k, v in params.items())
    url = f"{LOGS_URL}?{query}" if query else LOGS_URL
    req = urllib.request.Request(url, method="GET")
    req.add_header("Accept", "application/json")
    if key:
        req.add_header("Authorization", f"Bearer {key}")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"[error] HTTP {e.code}: {e.read().decode()[:200]}", file=sys.stderr)
        if e.code == 401:
            print("Укажи ключ: --api-key sk-... или OMNI_KEY", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[error] {e}", file=sys.stderr)
        sys.exit(1)


def short_model(m: str) -> str:
    if not m:
        return "—"
    return m.split("/")[-1][:28]


def provider_of(m: str) -> str:
    if not m:
        return "—"
    return m.split("/")[0][:10]


def fmt_dur(ms: float) -> str:
    if ms <= 0:
        return "…"
    if ms < 1000:
        return f"{ms:.0f}ms"
    return f"{ms/1000:.1f}s"


def fmt_tokens(tokens: dict) -> str:
    t = tokens or {}
    return f"in={t.get('in', 0) // 1000}k out={t.get('out', 0) // 1000}k"


def render(rows: list, since_sec: float, is_once: bool):
    now = time.time() * 1000
    cutoff = now - since_sec * 1000
    recent = [r for r in rows if r.get("timestamp") and r.get("timestamp")]  # keep all; filter below
    # logs are returned desc; active first

    active = [r for r in recent if r.get("active") is True]
    completed = [r for r in recent if r.get("active") is not True and r.get("status")]

    lines = []
    lines.append("=" * 78)
    lines.append(f"OmniRoute Live — реальные модели  ({time.strftime('%H:%M:%S')})")
    lines.append("=" * 78)

    if active:
        lines.append(f"  ▶ АКТИВНЫЕ ЗАПРОСЫ ({len(active)}):")
        for r in active[:10]:
            try:
                iso = r.get("timestamp", "")
                if iso:
                    import datetime
                    dt = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
                    elapsed = (now - dt.timestamp() * 1000) / 1000
                else:
                    elapsed = 0
            except Exception:
                elapsed = 0
            m = short_model(r.get("model"))
            p = provider_of(r.get("model"))
            status = r.get("status")
            st = "RUN" if not status or status == 0 else f"HTTP {status}"
            combo = r.get("comboName") or r.get("requestedModel") or ""
            lines.append(f"     {st:<7} {p:<10} {m:<30} {elapsed:>6.0f}s  {combo}")
        lines.append("")

    lines.append(f"  ✓ ПОСЛЕДНИЕ ЗАВЕРШЁННЫЕ ({len(completed)}):")
    for r in completed[:12]:
        m = short_model(r.get("model"))
        p = provider_of(r.get("model"))
        dur = fmt_dur(r.get("duration", 0))
        tk = fmt_tokens(r.get("tokens"))
        status = r.get("status") or "?"
        combo = r.get("comboName") or ""
        lines.append(f"     {status:<7} {p:<10} {m:<30} {dur:>8}  {tk:<24} {combo}")
    lines.append("")

    # сводка по моделям (completed за окно)
    model_counter = Counter(r.get("model") or "?" for r in completed)
    lines.append("  📊 СВОДКА ПО МОДЕЛЯМ (за последние %.0f мин):" % (since_sec / 60))
    for m, cnt in model_counter.most_common(10):
        p = provider_of(m)
        lines.append(f"     {cnt:>3}x  {p:<10} {short_model(m):<30}")
    lines.append("")

    out = "\n".join(lines)
    if is_once:
        print(out)
    else:
        sys.stdout.write("\033[H\033[2J" + out + "\n")
        sys.stdout.flush()


def main():
    ap = argparse.ArgumentParser(description="Живой мониторинг моделей OmniRoute")
    ap.add_argument("--api-key", default=KEY, help="API key OmniRoute")
    ap.add_argument("--once", action="store_true", help="один снапшот и выход")
    ap.add_argument("--since", type=float, default=300, help="окно сводки, сек (default 300)")
    ap.add_argument("--interval", type=float, default=REFRESH, help="интервал обновления, сек")
    args = ap.parse_args()

    key = args.api_key or KEY

    if args.once:
        rows = fetch({"limit": 30, "sort": "desc"}, key)
        render(rows, args.since, True)
        return

    try:
        while True:
            rows = fetch({"limit": 30, "sort": "desc"}, key)
            render(rows, args.since, False)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n[exit]")


if __name__ == "__main__":
    main()
