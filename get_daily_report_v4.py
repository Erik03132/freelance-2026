#!/usr/bin/env python3
"""v4: Правильный фильтр по дате + проверка реальных дат"""
import urllib.request
import json
from collections import defaultdict

WH = "https://incubird.bitrix24.ru/rest/41624/w2b11s24upbycolk/"

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

# Маппинг пользователей
users = {
    "1": "Андрей", "22": "Олег Мосин", "124": "Татьяна",
    "1528": "Аня", "1586": "Менеджер", "4388": "Эльзара",
    "40318": "Марина Е", "40994": "Ольга М.", "41624": "Анжелочка"
}

# === ПРОВЕРКА: что реально возвращает фильтр ===
print("🔍 ДИАГНОСТИКА: проверяю фильтр по дате для сделок...")

# Попробуем POST запрос вместо GET — Битрикс лучше работает с POST для фильтров
import urllib.parse

def post_api(method, payload):
    url = f"{WH}{method}"
    all_results = []
    start = 0
    while True:
        payload["start"] = start
        data_bytes = urllib.parse.urlencode(payload, doseq=True).encode('utf-8')
        try:
            req = urllib.request.Request(url, data=data_bytes, method='POST')
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                results = data.get('result', [])
                total = data.get('total', 0)
                if not results:
                    break
                all_results.extend(results)
                nxt = data.get('next')
                if not nxt or len(all_results) >= 500:
                    break
                start = nxt
        except Exception as e:
            print(f"  POST API error ({method}): {e}")
            break
    return all_results, total if 'total' in dir() else 0

# === СДЕЛКИ за сегодня через POST ===
print("\n💰 Сделки за 21 апреля (POST)...")
deals, total_deals = post_api("crm.deal.list.json", {
    "filter[>=DATE_CREATE]": "2026-04-21T00:00:00+03:00",
    "filter[<=DATE_CREATE]": "2026-04-21T23:59:59+03:00",
    "select[]": ["ID", "TITLE", "OPPORTUNITY", "ASSIGNED_BY_ID", "DATE_CREATE", "STAGE_ID", "CONTACT_ID"],
    "order[DATE_CREATE]": "DESC"
})
print(f"   Всего сделок сегодня: {total_deals} (получено: {len(deals)})")

# Проверяем реальные даты
if deals:
    print(f"   Первая: ID={deals[0].get('ID')} дата={deals[0].get('DATE_CREATE')}")
    print(f"   Последняя: ID={deals[-1].get('ID')} дата={deals[-1].get('DATE_CREATE')}")

# Группируем по менеджерам
mgr_deals = defaultdict(list)
total_sum = 0
for d in deals:
    mgr_id = str(d.get("ASSIGNED_BY_ID", ""))
    mgr_name = users.get(mgr_id, f"ID:{mgr_id}")
    opp = float(d.get("OPPORTUNITY", 0) or 0)
    total_sum += opp
    mgr_deals[mgr_name].append(d)

print(f"\n   Общая сумма: {total_sum:,.0f} ₽")
print(f"   Средний чек: {total_sum/max(len(deals),1):,.0f} ₽")
print("\n   По менеджерам:")
for name, dlist in sorted(mgr_deals.items(), key=lambda x: -sum(float(d.get("OPPORTUNITY",0) or 0) for d in x[1])):
    s = sum(float(d.get("OPPORTUNITY",0) or 0) for d in dlist)
    print(f"     {name}: {len(dlist)} сделок, {s:,.0f} ₽")

# ТОП-10 сделок
print("\n💰 ТОП-10 СДЕЛОК:")
deals_sorted = sorted(deals, key=lambda x: float(x.get("OPPORTUNITY", 0) or 0), reverse=True)
for i, d in enumerate(deals_sorted[:10]):
    mgr_name = users.get(str(d.get("ASSIGNED_BY_ID","")), "?")
    opp = float(d.get("OPPORTUNITY", 0) or 0)
    title = d.get("TITLE", "")
    dt = d.get("DATE_CREATE", "")
    time_short = dt.split("T")[1][:5] if "T" in dt else ""
    print(f"  {i+1}. {opp:,.0f} ₽ — {mgr_name} ({time_short}) [{title}]")

# === ЛИДЫ за сегодня ===
print("\n📋 Лиды за 21 апреля (POST)...")
leads, total_leads = post_api("crm.lead.list.json", {
    "filter[>=DATE_CREATE]": "2026-04-21T00:00:00+03:00",
    "filter[<=DATE_CREATE]": "2026-04-21T23:59:59+03:00",
    "select[]": ["ID", "TITLE", "ASSIGNED_BY_ID", "SOURCE_ID", "NAME", "LAST_NAME"],
    "order[DATE_CREATE]": "DESC"
})
print(f"   Всего лидов сегодня: {total_leads} (получено: {len(leads)})")

lead_by_mgr = defaultdict(int)
lead_by_src = defaultdict(int)
for l in leads:
    mgr_id = str(l.get("ASSIGNED_BY_ID", ""))
    mgr_name = users.get(mgr_id, f"ID:{mgr_id}")
    lead_by_mgr[mgr_name] += 1
    src = l.get("SOURCE_ID", "?")
    lead_by_src[src] += 1

print("   По менеджерам:")
for name, cnt in sorted(lead_by_mgr.items(), key=lambda x: -x[1]):
    print(f"     {name}: {cnt}")
print("   По источникам:")
for src, cnt in sorted(lead_by_src.items(), key=lambda x: -x[1]):
    label = {"CALL": "📞 Звонки", "2|OPENLINE": "💬 Чаты", "EMAIL": "📧 Email",
             "2|VK": "📱 VK", "WEBFORM": "🌐 Сайт", "2|FACEBOOK": "FB"}.get(src, src)
    print(f"     {label}: {cnt}")

# === ЗВОНКИ за сегодня ===
print("\n📞 Звонки за 21 апреля...")
calls, total_calls = post_api("crm.activity.list.json", {
    "filter[>=CREATED]": "2026-04-21T00:00:00+03:00",
    "filter[<=CREATED]": "2026-04-21T23:59:59+03:00",
    "filter[TYPE_ID]": "2",
    "select[]": ["ID", "SUBJECT", "RESPONSIBLE_ID", "DIRECTION", "CREATED", "DESCRIPTION"],
    "order[CREATED]": "DESC"
})
print(f"   Всего звонков сегодня: {total_calls}")

calls_by_mgr = defaultdict(int)
for c in calls:
    resp_id = str(c.get("RESPONSIBLE_ID", ""))
    resp_name = users.get(resp_id, f"ID:{resp_id}")
    calls_by_mgr[resp_name] += 1
print("   По менеджерам:")
for name, cnt in sorted(calls_by_mgr.items(), key=lambda x: -x[1]):
    print(f"     {name}: {cnt}")

# Примеры звонков
print("\n   Примеры звонков (последние 15):")
for c in calls[:15]:
    subj = c.get("SUBJECT", "")
    resp = users.get(str(c.get("RESPONSIBLE_ID","")), "?")
    direction = "📥 Вх" if str(c.get("DIRECTION")) == "1" else "📤 Исх"
    dt = c.get("CREATED", "")
    time_short = dt.split("T")[1][:5] if "T" in dt else ""
    desc = (c.get("DESCRIPTION") or "")[:80]
    print(f"     {direction} {time_short} | {resp} | {subj}")
    if desc:
        print(f"        💬 {desc}")

# Примеры лидов с названиями
print("\n📋 Примеры лидов (последние 20):")
for l in leads[:20]:
    title = l.get("TITLE", "")
    mgr_id = str(l.get("ASSIGNED_BY_ID", ""))
    mgr_name = users.get(mgr_id, f"ID:{mgr_id}")
    print(f"     [{title}] → {mgr_name}")

print("\n✅ Готово!")
