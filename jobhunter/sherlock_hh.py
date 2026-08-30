#!/usr/bin/env python3
"""Шерлок: парсинг hh.ru (вакансии, Москва, remote/hybrid). Без бана: задержки."""
import json, sys, time, random
from playwright.sync_api import sync_playwright

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

def parse_page(page, tag):
    page.wait_for_load_state("domcontentloaded")
    time.sleep(random.uniform(2.5, 4.0))
    items = page.evaluate("""() => {
      const cards = document.querySelectorAll('[data-qa="vacancy-serp__vacancy"]');
      return Array.from(cards).map(c => {
        const a = c.querySelector('a[data-qa="serp-item__title"]');
        const comp = c.querySelector('[data-qa="vacancy-serp__vacancy-employer"]');
        const salary = c.querySelector('[data-qa="vacancy-serp__vacancy-compensation"]');
        const addr = c.querySelector('[data-qa="vacancy-serp__vacancy-address"]');
        const snippet = c.querySelector('[data-qa="vacancy-serp__vacancy-snippet"]');
        return {
          title: a ? a.textContent.replace(/\\s+/g,' ').trim() : '',
          url: a ? a.href : '',
          company: comp ? comp.textContent.replace(/\\s+/g,' ').trim() : '',
          salary: salary ? salary.textContent.replace(/\\s+/g,' ').trim() : '',
          address: addr ? addr.textContent.replace(/\\s+/g,' ').trim() : '',
          snippet: snippet ? snippet.textContent.replace(/\\s+/g,' ').trim().slice(0,200) : ''
        };
      });
    }""")
    return items

def run():
    query = sys.argv[1] if len(sys.argv) > 1 else "AI инженер"
    out = sys.argv[2] if len(sys.argv) > 2 else "/tmp/hh_out.json"
    urls = [
        f"https://hh.ru/search/vacancy?text={query}&area=1&schedule=remote&items_on_page=50&search_field=name&order_by=relevance",
        f"https://hh.ru/search/vacancy?text={query}&area=1&schedule=hybrid_remote&items_on_page=50&search_field=name&order_by=relevance",
    ]
    all_items = []
    seen = set()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            "--no-sandbox", "--disable-blink-features=AutomationControlled",
            "--window-size=1440,2400"])
        ctx = browser.new_context(
            user_agent=UA, locale="ru-RU",
            viewport={"width": 1440, "height": 2400},
            extra_http_headers={"Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8"})
        page = ctx.new_page()
        for u in urls:
            try:
                page.goto(u, timeout=45000, wait_until="domcontentloaded")
                time.sleep(random.uniform(3.0, 5.0))
                items = parse_page(page, query)
                for it in items:
                    if it["url"] and it["url"] not in seen:
                        seen.add(it["url"])
                        all_items.append(it)
                print(f"[{query}] page1 '{('remote' if 'remote' in u else 'hybrid')}': {len(items)} cards", file=sys.stderr)
            except Exception as e:
                print(f"[{query}] ERROR page: {e}", file=sys.stderr)
            time.sleep(random.uniform(8, 14))
        browser.close()
    with open(out, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=1)
    print(f"TOTAL {len(all_items)} -> {out}")

if __name__ == "__main__":
    run()