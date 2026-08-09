#!/usr/bin/env python3
"""notebooklm_scan.py — ночное сканирование блокнотов NotebookLM.

Для каждого блокнота из конфига получает список источников, находит новые
(по state-файлу updated_at), выгружает их контент в outdir.
Использует CLI nlm (notebooklm-mcp-cli) с US-прокси:
  1) локальный форвард http://127.0.0.1:64468 (VPS → US-прокси, без VPN)
  2) прямой US-прокси http://172.120.21.141:64468 (если VPN включён)

Usage:
  python3 notebooklm_scan.py [--outdir DIR] [--limit N] [--init-state]
                             [--notebooks "id1,id2"] [--verbose]
"""

import json
import os
import subprocess
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NLM = os.path.expanduser("~/.local/bin/nlm")
STATE_FILE = os.path.join(SCRIPT_DIR, "notebooklm_state.json")
PROXIES = [
    "http://Q3NeJXTY:dsBaWh2L@127.0.0.1:64468",
    "http://Q3NeJXTY:dsBaWh2L@172.120.21.141:64468",
]
CONF_FILE = os.path.join(SCRIPT_DIR, "notebooklm_scan.json")
DEFAULT_CONF = {
    "notebooks": [],  # пусто = все (кроме skip)
    "skip": ["e312ae55-ff5d-4f5d-a0c2-149bde"],  # Pastilla ТЕСТ
    "max_sources_per_notebook": 50,
}


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", file=sys.stderr, flush=True)


def load_config():
    conf = dict(DEFAULT_CONF)
    if os.path.exists(CONF_FILE):
        try:
            with open(CONF_FILE) as f:
                conf.update(json.load(f))
        except Exception as e:
            log(f"⚠️ Конфиг {CONF_FILE} не прочитан: {e}")
    return conf


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_state(state):
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=1, ensure_ascii=False)
    os.replace(tmp, STATE_FILE)


def pick_proxy():
    for p in PROXIES:
        try:
            r = subprocess.run(
                [
                    "curl",
                    "-s",
                    "--max-time",
                    "6",
                    "-x",
                    p,
                    "-o",
                    "/dev/null",
                    "-w",
                    "%{http_code}",
                    "https://example.com",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if r.returncode == 0 and r.stdout.strip() == "200":
                return p
        except Exception:
            continue
    return None


def nlm(args, proxy, timeout=180):
    env = os.environ.copy()
    env["HTTP_PROXY"] = proxy
    env["HTTPS_PROXY"] = proxy
    env["NO_PROXY"] = "localhost,127.0.0.1"
    env["PATH"] = os.path.expanduser("~/.local/bin") + ":" + env.get("PATH", "")
    r = subprocess.run([NLM] + args, capture_output=True, text=True, env=env, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(
            f"nlm {' '.join(args)} → rc={r.returncode}: " f"{r.stderr.strip()[-300:]}"
        )
    return r.stdout


def safe_name(s, maxlen=60):
    s = "".join(c if c.isalnum() or c in "-_ " else "_" for c in s)
    s = " ".join(s.split()).strip()
    return s[:maxlen] or "source"


def parse_updated(src):
    v = src.get("updated_at") or src.get("last_updated") or ""
    if isinstance(v, str) and v:
        try:
            v = v.replace("Z", "+00:00")
            return datetime.fromisoformat(v).timestamp()
        except Exception:
            return 0
    return 0


def main():
    args = sys.argv[1:]
    outdir = None
    limit = None
    init_state = "--init-state" in args
    verbose = "--verbose" in args
    only = None
    for a in args:
        if a.startswith("--outdir="):
            outdir = a.split("=", 1)[1]
        elif a.startswith("--limit="):
            limit = int(a.split("=", 1)[1])
        elif a.startswith("--notebooks="):
            only = a.split("=", 1)[1].split(",")

    if not outdir:
        outdir = "/tmp/notebooklm_scan"
    os.makedirs(outdir, exist_ok=True)

    proxy = pick_proxy()
    if not proxy:
        log(
            "❌ Прокси недоступны (127.0.0.1:64468 и 172.120.21.141:64468) — "
            "пропускаю сканирование NotebookLM"
        )
        return 1

    conf = load_config()
    state = load_state()
    log(f"🔍 Прокси: {proxy}")

    raw = nlm(["notebook", "list", "--json"], proxy)
    notebooks = json.loads(raw)
    if isinstance(notebooks, dict):
        notebooks = notebooks.get("notebooks", notebooks.get("data", []))
    if only:
        notebooks = [n for n in notebooks if (n.get("id") or "") in only]
    else:
        notebooks = [n for n in notebooks if (n.get("id") or "") not in conf["skip"]]
    log(f"📒 Блокнотов для сканирования: {len(notebooks)}")

    new_sources = []
    total_checked = 0

    for nb in notebooks:
        nb_id = nb.get("id")
        nb_title = nb.get("title") or nb.get("display_name") or nb_id
        nb_state = state.get(nb_id, {})
        try:
            raw = nlm(["source", "list", nb_id, "--json"], proxy)
            sources = json.loads(raw)
            if isinstance(sources, dict):
                sources = sources.get("sources", sources.get("data", []))
            sources = sources[: conf.get("max_sources_per_notebook", 50)]
        except Exception as e:
            log(f"  ⚠️ {nb_title}: не получен список источников ({e})")
            continue

        for src in sources:
            src_id = src.get("id")
            if not src_id:
                continue
            total_checked += 1
            ts = parse_updated(src)
            prev = nb_state.get(src_id)
            if prev is not None and (not ts or prev >= ts):
                continue
            title = src.get("display_name") or src.get("title") or src_id
            kind = src.get("kind") or src.get("source_type") or ""
            new_sources.append(
                {
                    "nb_id": nb_id,
                    "nb_title": nb_title,
                    "src_id": src_id,
                    "title": title,
                    "kind": kind,
                    "updated": ts or 0,
                }
            )

    new_sources.sort(key=lambda s: s["updated"])
    if limit:
        new_sources = new_sources[:limit]

    if init_state:
        for s in new_sources:
            state.setdefault(s["nb_id"], {})[s["src_id"]] = s["updated"]
        save_state(state)
        log(
            f"💾 Инициализирован state: {len(new_sources)} источников "
            f"(проверено {total_checked}). Новые будут читаться со следующего "
            f"добавления."
        )
        return 0

    log(f"🆕 Новых источников: {len(new_sources)}")
    files = []
    for s in new_sources:
        base = (
            f"{datetime.now().strftime('%Y%m%d')}_nblm_{safe_name(s['nb_title'])}"
            f"_{safe_name(s['title'])}.md"
        )
        path = os.path.join(outdir, base)
        try:
            nlm(["content", "source", s["src_id"], "--output", path], proxy, timeout=300)
            if os.path.exists(path) and os.path.getsize(path) > 0:
                files.append(path)
                state.setdefault(s["nb_id"], {})[s["src_id"]] = s["updated"]
                if verbose:
                    log(
                        f"  ✅ {s['nb_title']} / {s['title'][:50]} "
                        f"({os.path.getsize(path)//1024} KB)"
                    )
            else:
                log(f"  ⚠️ {s['nb_title']} / {s['title'][:50]}: пустой контент")
        except Exception as e:
            log(f"  ❌ {s['nb_title']} / {s['title'][:50]}: {str(e)[-150:]}")

    save_state(state)
    print("\n".join(files), flush=True)
    log(f"🎯 Выгружено файлов: {len(files)}")
    return 0 if files else 0


if __name__ == "__main__":
    sys.exit(main())
