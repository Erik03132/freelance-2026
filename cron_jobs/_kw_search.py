#!/usr/bin/env python3
"""Целевой поиск подходящих кворков (сладкий сегмент).

Стратегия (Kwork URL-поиск ?q= игнорируется -> работает только листинг):
1. Собрать дефолтный фид /projects (несколько страниц), дедуп.
2. Предфильтр по заголовкам сладкого сегмента (OUR_SKILLS).
3. Для отобранных ОДНИМ браузером (ретрай на ERR_CONNECTION_REFUSED)
   стянуть РЕАЛЬНОЕ описание + proposals + client.
4. Скоринг через kwork_finder.evaluate (на реальном desc, не на мусоре карточки).
5. Вывести кандидатов A/B; для лучшего A записать черновик.
"""
import os, sys, time, random
for k in ("http_proxy", "https_proxy", "all_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"):
    os.environ.pop(k, None)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kwork_finder as kf

TITLE_HINTS = [
    "бот", "телеграм", "telegram", "aiogram", "парсер", "парсинг", "автоматизац",
    "python", "скрипт", "rag", "llm", "gpt", "нейросет", "битрикс", "bitrix",
    "crm", "api", "интеграц", "выгрузк", "сайт", "лендинг", "данн", "таблиц",
    "чат", "голос", "ттс", "whisper", "транскриб",
]
LIST_PAGES = 4
DETAIL_DELAY = (9, 16)


def fetch_list() -> list[dict]:
    from playwright.sync_api import sync_playwright
    out, seen = [], set()
    launch_args = ["--no-sandbox", "--no-proxy-server", "--disable-dev-shm-usage"]
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=launch_args)
        ctx = b.new_context(user_agent=kf.rand_ua())
        pg = ctx.new_page()
        for page in range(1, LIST_PAGES + 1):
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
                    print(f"  [warn] list p{page} attempt {attempt}: {e}", file=sys.stderr)
                    time.sleep(random.uniform(5, 12))
            if not ok:
                break
            cards = pg.eval_on_selector_all(
                "a[href*='/projects/']",
                "els => els.map(e => { const c=e.closest('[class*=\"card\"],[class*=\"want\"]')||e.parentElement;"
                " return {href:e.getAttribute('href'), title:(e.innerText||'').trim().slice(0,200)}; })")
            for c in cards:
                href = c.get("href") or ""
                if "/projects/" not in href or href in seen:
                    continue
                seen.add(href)
                full = href if href.startswith("http") else "https://kwork.ru" + href
                out.append({"url": full, "title": (c.get("title") or "").strip(), "desc": ""})
            if page < LIST_PAGES:
                time.sleep(random.uniform(20, 40))
        b.close()
    return out


def fetch_details(urls: list[str]) -> dict:
    """Вернуть {url: {budget, desc, proposals, client_info}} с ретраем."""
    from playwright.sync_api import sync_playwright
    launch_args = ["--no-sandbox", "--no-proxy-server", "--disable-dev-shm-usage"]
    result = {}
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=launch_args)
        ctx = b.new_context(user_agent=kf.rand_ua())
        pg = ctx.new_page()
        for u in urls:
            detail = {"budget": None, "desc": "", "proposals": None, "client_info": {}}
            for attempt in range(4):
                try:
                    pg.goto(u, timeout=45000, wait_until="commit")
                    pg.wait_for_timeout(3500)
                    body = pg.inner_text("body")
                    detail["budget"] = kf.extract_budget(body)
                    detail["proposals"] = kf.extract_proposals(body)
                    detail["client_info"] = kf.extract_client_info(body)
                    desc = ""
                    for sel in ("[class*='want']", "[class*='project']", "article", ".description"):
                        try:
                            t = pg.inner_text(sel)
                            if t and len(t) > len(desc):
                                desc = t
                        except Exception:
                            continue
                    if not desc:
                        desc = body
                    for marker in ("Покупатель:", "Заказчик:", "Осталось:", "Предложений:"):
                        idx = desc.find(marker)
                        if idx > 200:
                            desc = desc[:idx]
                            break
                    detail["desc"] = desc.strip()[:1000]
                    break
                except Exception as e:
                    print(f"  [warn] detail {u} attempt {attempt}: {e}", file=sys.stderr)
                    time.sleep(random.uniform(6, 14))
            result[u] = detail
            time.sleep(random.uniform(*DETAIL_DELAY))
        b.close()
    return result


def main():
    print("[*] fetch list...")
    jobs = fetch_list()
    print(f"[*] raw kworks: {len(jobs)}")
    # предфильтр по заголовкам
    cand = [j for j in jobs if any(h in j["title"].lower() for h in TITLE_HINTS)]
    print(f"[*] title-matched: {len(cand)}")
    if not cand:
        print("Ничего по заголовкам не зацепили.")
        return
    details = fetch_details([j["url"] for j in cand])
    cfg = dict(
        min_skill_a=kf.DEFAULTS["min_skill_a"], min_skill_b=kf.DEFAULTS["min_skill_b"],
        max_proposals_x=kf.DEFAULTS["max_proposals_x"], max_proposals_b=kf.DEFAULTS["max_proposals_b"],
        min_budget=kf.DEFAULTS["min_budget"], final_threshold_a=kf.DEFAULTS["final_threshold_a"],
    )
    results = []
    for j in cand:
        merged = {**j, **details.get(j["url"], {})}
        ev = kf.evaluate(merged, cfg)
        results.append((ev["decision"], ev, merged))
    results.sort(key=lambda x: (x[0] != "A", -(x[1]["final"] or 0)))
    print("\n=== КАНДИДАТЫ (A/B) ===")
    best_a = None
    for dec, ev, job in results:
        sm = ev["skill_detail"]
        print(f"\n[{dec}] {job['title']}")
        print(f"  url: {job['url']}")
        print(f"  skill={ev['skill']} comp={ev['competition']} client={ev['client']} "
              f"budget={ev['budget']} final={ev['final']}")
        print(f"  our: {sm['our']} | exclude: {sm['exclude']} | proposals={ev['proposals']}")
        print(f"  client: {kf._client_str(ev['client_info'])}")
        print(f"  reason: {ev['reason']}")
        print(f"  desc[:300]: {(job.get('desc') or '')[:300]}")
        if dec == "A" and best_a is None:
            best_a = (ev, job)
    if best_a:
        ev, job = best_a
        path = kf.write_draft(job, ev)
        print(f"\n[DRAFT WRITTEN] -> {path}")


if __name__ == "__main__":
    main()
