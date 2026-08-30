#!/usr/bin/env python3
"""Только сбор заголовков+URL с листинга (без стягивания деталей)."""
import os, sys, time, random
for k in ("http_proxy","https_proxy","all_proxy","HTTP_PROXY","HTTPS_PROXY","ALL_PROXY"):
    os.environ.pop(k, None)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kwork_finder as kf

HINTS = ["бот","телеграм","telegram","aiogram","парсер","парсинг","автоматизац",
         "python","скрипт","rag","llm","gpt","нейросет","битрикс","bitrix","crm",
         "api","интеграц","выгрузк","сайт","лендинг","данн","таблиц","чат","голос",
         "ттс","whisper","транскриб"]
from playwright.sync_api import sync_playwright
out, seen = [], set()
launch_args = ["--no-sandbox","--no-proxy-server","--disable-dev-shm-usage"]
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=launch_args)
    ctx = b.new_context(user_agent=kf.rand_ua())
    pg = ctx.new_page()
    for page in range(1, 4):
        url = "https://kwork.ru/projects" + (f"?page={page}" if page > 1 else "")
        ok = False
        for attempt in range(4):
            try:
                pg.goto(url, timeout=45000, wait_until="commit")
                pg.wait_for_selector("a[href*='/projects/']", timeout=30000)
                pg.wait_for_timeout(2500)
                ok = True
                break
            except Exception as e:
                print(f"  [warn] p{page} a{attempt}: {e}", file=sys.stderr)
                time.sleep(random.uniform(5,12))
        if not ok: break
        cards = pg.eval_on_selector_all(
            "a[href*='/projects/']",
            "els => els.map(e => { const c=e.closest('[class*=\"card\"],[class*=\"want\"]')||e.parentElement;"
            " return {href:e.getAttribute('href'), title:(e.innerText||'').trim().slice(0,200)}; })")
        for c in cards:
            href = c.get("href") or ""
            if "/projects/" not in href or href in seen: continue
            seen.add(href)
            full = href if href.startswith("http") else "https://kwork.ru"+href
            t = (c.get("title") or "").strip()
            out.append((t, full))
        if page < 3: time.sleep(random.uniform(15,30))
    b.close()
print(f"Всего: {len(out)}")
print("=== КАНДИДАТЫ (по заголовкам сладкого сегмента) ===")
for t, u in out:
    if any(h in t.lower() for h in HINTS):
        print(f"- {t}\n  {u}")
