#!/usr/bin/env python3
"""Стянуть РЕАЛЬНОЕ ТЗ только для заданных URL (по одному, с паузой)."""
import os, sys, time, random
for k in ("http_proxy","https_proxy","all_proxy","HTTP_PROXY","HTTPS_PROXY","ALL_PROXY"):
    os.environ.pop(k, None)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kwork_finder as kf

URLS = [
    "https://kwork.ru/projects/3243570",  # Python-скрипт парсинга сайтов
    "https://kwork.ru/projects/3243591",  # Веб-сервис управления финансами
]
from playwright.sync_api import sync_playwright
launch_args = ["--no-sandbox","--no-proxy-server","--disable-dev-shm-usage"]
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=launch_args)
    ctx = b.new_context(user_agent=kf.rand_ua())
    pg = ctx.new_page()
    for u in URLS:
        for attempt in range(5):
            try:
                pg.goto(u, timeout=45000, wait_until="commit")
                pg.wait_for_timeout(4000)
                body = pg.inner_text("body")
                budget = kf.extract_budget(body)
                proposals = kf.extract_proposals(body)
                client = kf.extract_client_info(body)
                desc = ""
                for sel in ("[class*='want']","[class*='project']","article",".description"):
                    try:
                        t = pg.inner_text(sel)
                        if t and len(t) > len(desc): desc = t
                    except Exception: continue
                if not desc: desc = body
                for marker in ("Покупатель:","Заказчик:","Осталось:","Предложений:"):
                    idx = desc.find(marker)
                    if idx > 200:
                        desc = desc[:idx]; break
                desc = desc.strip()[:1200]
                job = {"url": u, "title": u.split("/")[-1], "desc": desc,
                       "budget": budget, "proposals": proposals, "client_info": client}
                ev = kf.evaluate(job, kf.DEFAULTS)
                print("="*72)
                print(f"URL: {u}")
                print(f"budget={budget} proposals={proposals} client={kf._client_str(client)}")
                print(f"DECISION: {ev['decision']} | skill={ev['skill']} final={ev['final']}")
                print(f"our: {ev['skill_detail']['our']} | exclude: {ev['skill_detail']['exclude']}")
                print(f"reason: {ev['reason']}")
                print(f"DESC[:600]:\n{desc[:600]}")
                break
            except Exception as e:
                print(f"  [warn] {u} a{attempt}: {e}", file=sys.stderr)
                time.sleep(random.uniform(10, 20))
        time.sleep(random.uniform(25, 40))  # пауза между кворками (анти-бан)
    b.close()
