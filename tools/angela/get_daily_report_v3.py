#!/usr/bin/env python3
"""v3: Находим ID:22 и ID:1586, достаём продукты из сделок и контакты"""
import urllib.request
import json
from collections import defaultdict

WH = "https://incubird.bitrix24.ru/rest/41624/w2b11s24upbycolk/"
TODAY = "2026-04-21"

def call_api(method, params=""):
    all_results = []
    start = 0
    while True:
        sep = "&" if params else ""
        url = f"{WH}{method}?{params}{sep}start={start}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                results = data.get('result', [])
                if isinstance(results, dict):
                    return results
                if not results:
                    break
                all_results.extend(results)
                nxt = data.get('next')
                if not nxt or len(all_results) >= 500:
                    break
                start = nxt
        except Exception as e:
            print(f"  API error ({method}): {e}")
            break
    return all_results

# === 1. Ищем кто такие ID:22 и ID:1586 ===
print("🔍 Ищем пользователя ID:22...")
u22 = call_api("user.get.json", "ID=22")
if u22:
    for u in (u22 if isinstance(u22, list) else [u22]):
        print(f"   ID:22 = {u.get('NAME','')} {u.get('LAST_NAME','')} | Active: {u.get('ACTIVE')} | Pos: {u.get('WORK_POSITION','')}")

print("🔍 Ищем пользователя ID:1586...")
u1586 = call_api("user.get.json", "ID=1586")
if u1586:
    for u in (u1586 if isinstance(u1586, list) else [u1586]):
        print(f"   ID:1586 = {u.get('NAME','')} {u.get('LAST_NAME','')} | Active: {u.get('ACTIVE')} | Pos: {u.get('WORK_POSITION','')}")

# Полный список пользователей (включая неактивных)
print("\n👤 Загружаю ВСЕХ пользователей (вкл. неактивных)...")
all_users = call_api("user.get.json", "")
users = {}
for u in (all_users if isinstance(all_users, list) else []):
    uid = str(u.get("ID"))
    name = f"{u.get('NAME','')} {u.get('LAST_NAME','')}".strip()
    users[uid] = name if name else f"ID:{uid}"

print(f"   Всего пользователей: {len(users)}")
for uid, name in sorted(users.items(), key=lambda x: int(x[0])):
    print(f"   {uid}: {name}")

# === 2. Сделки за сегодня — ВСЕ с контактами ===
print("\n💰 Загружаю сделки за сегодня...")
deals = call_api("crm.deal.list.json",
    f"filter[>=DATE_CREATE]={TODAY}T00:00:00%2B03:00"
    f"&select[]=ID&select[]=TITLE&select[]=OPPORTUNITY&select[]=ASSIGNED_BY_ID"
    f"&select[]=DATE_CREATE&select[]=STAGE_ID&select[]=COMMENTS&select[]=CONTACT_ID")
print(f"   Найдено сделок: {len(deals)}")

# Распределение сделок по менеджерам
mgr_deals = defaultdict(list)
total_sum = 0
for d in deals:
    mgr_id = str(d.get("ASSIGNED_BY_ID", ""))
    mgr_name = users.get(mgr_id, f"ID:{mgr_id}")
    opp = float(d.get("OPPORTUNITY", 0) or 0)
    total_sum += opp
    mgr_deals[mgr_name].append(d)

print("\n   --- Сделки по менеджерам ---")
for name, dlist in sorted(mgr_deals.items(), key=lambda x: -sum(float(d.get("OPPORTUNITY",0) or 0) for d in x[1])):
    s = sum(float(d.get("OPPORTUNITY",0) or 0) for d in dlist)
    print(f"   {name}: {len(dlist)} сделок, {s:,.0f} ₽")

# === 3. Продукты из ТОП-5 сделок ===
print("\n📦 Загружаю товарные позиции из ТОП сделок...")
deals_sorted = sorted(deals, key=lambda x: float(x.get("OPPORTUNITY", 0) or 0), reverse=True)
for d in deals_sorted[:5]:
    did = d.get("ID")
    title = d.get("TITLE", "")
    opp = float(d.get("OPPORTUNITY", 0) or 0)
    print(f"\n   Сделка #{did} [{title}] — {opp:,.0f} ₽")
    
    products = call_api("crm.deal.productrows.list.json", f"id={did}")
    if products:
        for p in (products if isinstance(products, list) else []):
            pname = p.get("PRODUCT_NAME", "?")
            qty = p.get("QUANTITY", 0)
            price = p.get("PRICE", 0)
            print(f"      • {pname} x{qty} @ {price} ₽")
    else:
        print(f"      (нет товарных позиций)")
    
    # Комментарии сделки
    comments = d.get("COMMENTS", "")
    if comments:
        print(f"      💬 Комментарий: {comments[:200]}")

    # Контакт
    contact_id = d.get("CONTACT_ID")
    if contact_id:
        contact = call_api("crm.contact.get.json", f"ID={contact_id}")
        if contact and isinstance(contact, dict):
            cname = f"{contact.get('NAME','')} {contact.get('LAST_NAME','')}".strip()
            phones = contact.get("PHONE", [])
            phone_str = phones[0].get("VALUE","") if phones else ""
            addr = contact.get("ADDRESS", "")
            print(f"      👤 Контакт: {cname} | Тел: {phone_str} | Адрес: {addr}")

# === 4. Лиды — детальнее ===
print("\n📋 Загружаю лиды за сегодня (детали)...")
leads = call_api("crm.lead.list.json",
    f"filter[>=DATE_CREATE]={TODAY}T00:00:00%2B03:00"
    f"&select[]=ID&select[]=TITLE&select[]=ASSIGNED_BY_ID&select[]=SOURCE_ID"
    f"&select[]=NAME&select[]=LAST_NAME&select[]=COMMENTS")

lead_by_mgr = defaultdict(int)
lead_by_src = defaultdict(int)
for l in leads:
    mgr_id = str(l.get("ASSIGNED_BY_ID", ""))
    mgr_name = users.get(mgr_id, f"ID:{mgr_id}")
    lead_by_mgr[mgr_name] += 1
    src = l.get("SOURCE_ID", "?")
    lead_by_src[src] += 1

print(f"   Лидов: {len(leads)}")
print("   По менеджерам:")
for name, cnt in sorted(lead_by_mgr.items(), key=lambda x: -x[1]):
    print(f"     {name}: {cnt}")
print("   По источникам:")
for src, cnt in sorted(lead_by_src.items(), key=lambda x: -x[1]):
    print(f"     {src}: {cnt}")

# === 5. Примеры лидов с именами клиентов ===
print("\n📋 Примеры лидов (первые 15):")
for l in leads[:15]:
    title = l.get("TITLE", "")
    name = f"{l.get('NAME','')} {l.get('LAST_NAME','')}".strip()
    mgr_id = str(l.get("ASSIGNED_BY_ID", ""))
    mgr_name = users.get(mgr_id, f"ID:{mgr_id}")
    comments = (l.get("COMMENTS") or "")[:100]
    print(f"   [{title}] | Клиент: {name} | Менеджер: {mgr_name}")
    if comments:
        print(f"      💬 {comments}")

print("\n✅ Сбор данных завершён!")
