#!/usr/bin/env python3
"""
freelance_ru_finder.py — ночной скрайпер freelance.ru (SPA, DDoS-Guard).
Переиспользует фильтр калибровки и запись из kwork_finder (SSoT).

Режим: только поиск + черновик. НИКАКОЙ auto-send (анти-бан).
"""
from __future__ import annotations
import os, sys, re, json, sqlite3, argparse, random, time
from datetime import datetime, timezone

# переиспользуем логику из kwork_finder (SSoT: фильтр, дедуп, запись)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kwork_finder as KF

ROOT = KF.ROOT
OUTBOX = KF.OUTBOX
LEADS = KF.LEADS
DB = KF.DB
UA = KF.UA

# freelance.ru специфика: cookie могут понадобиться для обхода DDoS-Guard
COOKIES = os.path.join(ROOT, "freelance-agent", "data", "cookies", "freelance_ru.json")

def fetch_projects(limit_pages: int = 5, use_cookies: bool = True,
                   delay=(6, 18)) -> list[dict]:
    """Рендерим freelance.ru/projects через headless chromium."""
    from playwright.sync_api import sync_playwright
    out = []
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = b.new_context(user_agent=UA)
        if use_cookies and os.path.exists(COOKIES):
            try:
                with open(COOKIES) as f:
                    ctx.add_cookies(json.load(f))
            except Exception as e:
                print(f"[warn] cookies load: {e}", file=sys.stderr)
        pg = ctx.new_page()
        for page in range(1, limit_pages + 1):
            url = "https://freelance.ru/projects" + (f"?page={page}" if page > 1 else "")
            try:
                pg.goto(url, timeout=60000, wait_until="domcontentloaded")
                pg.wait_for_selector("a[href*='/projects/']", timeout=25000)
            except Exception as e:
                print(f"[warn] page {page}: {e}", file=sys.stderr)
                break
            cards = pg.eval_on_selector_all(
                "a[href*='/projects/']",
                """els => els.map(e => {
                    const card = e.closest('[class*=\"card\"], [class*=\"project\"], article') || e.parentElement;
                    return {
                        href: e.getAttribute('href'),
                        title: e.innerText.trim().slice(0,200),
                        cardText: (card ? card.innerText : '').slice(0,1200)
                    };
                })"""
            )
            seen = set()
            for c in cards:
                href = c.get("href") or ""
                if "/projects/" not in href:
                    continue
                if href in seen:
                    continue
                seen.add(href)
                full = href if href.startswith("http") else "https://freelance.ru" + href
                text = (c.get("title", "") + " " + c.get("cardText", "")).strip()
                out.append({
                    "url": full,
                    "title": c.get("title", "").strip(),
                    "budget": KF.extract_budget(text),
                    "desc": text,
                    "client": "",
                    "proposals": None,
                })
            if page < limit_pages:
                time.sleep(random.uniform(*delay))
        b.close()
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pages", type=int, default=5)
    ap.add_argument("--no-cookies", action="store_true")
    args = ap.parse_args()

    print("[*] freelance.ru fetch...")
    # сброс прокси (мертвый socks5 ломает headless)
    for k in ("http_proxy", "https_proxy", "all_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"):
        os.environ.pop(k, None)
    jobs = fetch_projects(limit_pages=args.pages, use_cookies=not args.no_cookies)
    print(f"[*] raw cards: {len(jobs)}")

    known = KF.seen_ids()
    new, drafted = 0, 0
    for job in jobs:
        if job["url"] in known:
            continue
        kind = KF.classify(job)
        if kind == "X":
            continue
        new += 1
        if args.dry_run:
            print(f"  [{kind}] {job['title'][:60]} | {job['url']}")
            continue
        path = KF.write_draft(job, kind)
        KF.mark_seen(job["url"])
        drafted += 1
        print(f"  [{kind}] draft -> {path}")
    print(f"[*] new qualifying: {new}, drafted: {drafted}"
          + (" (DRY-RUN)" if args.dry_run else ""))

if __name__ == "__main__":
    main()
