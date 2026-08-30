#!/usr/bin/env python3
"""Шерлок: читает карточки вакансий hh.ru (описание, требования, зарплата)."""
import json, sys, time, random
from playwright.sync_api import sync_playwright

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

def run():
    urls_file = sys.argv[1]
    out_file = sys.argv[2]
    with open(urls_file, encoding="utf-8") as f:
        urls = [l.strip() for l in f if l.strip()]
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            "--no-sandbox", "--disable-blink-features=AutomationControlled"])
        ctx = browser.new_context(user_agent=UA, locale="ru-RU",
                                  viewport={"width": 1440, "height": 2000})
        page = ctx.new_page()
        for u in urls:
            try:
                page.goto(u, timeout=45000, wait_until="domcontentloaded")
                time.sleep(random.uniform(2.0, 4.0))
                data = page.evaluate("""() => {
                  const g = (sel) => { const el = document.querySelector(sel); return el ? el.textContent.replace(/\\s+/g,' ').trim() : ''; };
                  const title = g('[data-qa="vacancy-title"]');
                  const comp = g('[data-qa="vacancy-view-employer-name"]') || g('[data-qa="bloko-header-2"]');
                  const sal = g('[data-qa="vacancy-view-employment-mode"]') || '';
                  const salary = document.querySelector('[data-qa="vacancy-view-salary-compensation-type-net"]') ||
                                document.querySelector('[data-qa="vacancy-view-salary-compensation-type-gross"]') ||
                                document.querySelector('[data-qa="vacancy-view-salary-compensation"]');
                  const body = g('[data-qa="vacancy-view-rich-text"]') || g('[data-qa="vacancy-description"]');
                  return {
                    title, comp,
                    salary: salary ? salary.textContent.replace(/\\s+/g,' ').trim() : '',
                    body: body.slice(0, 3500)
                  };
                }""")
                results.append({"url": u, **data})
                print(f"OK {u} -> {data['title'][:60]}", file=sys.stderr)
            except Exception as e:
                results.append({"url": u, "error": str(e)})
                print(f"ERR {u}: {e}", file=sys.stderr)
            time.sleep(random.uniform(6, 10))
        browser.close()
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print(f"TOTAL {len(results)} -> {out_file}")

if __name__ == "__main__":
    run()