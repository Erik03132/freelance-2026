#!/usr/bin/env python3
"""Полный отчёт за день — v2: ищем ВСЕХ менеджеров и детали звонков"""
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
                if not results:
                    break
                all_results.extend(results)
                nxt = data.get('next')
                if not nxt or len(all_results) >= 500:
                    break
                start = nxt
        except Exception as e:
            print(f"  API error ({method} start={start}): {e}")
            break
    return all_results

# === 1. ВСЕ пользователи — найдём менеджеров ===
print("👤 Загружаю ВСЕХ пользователей Битрикс24...")
users_raw = call_api("user.get.json", "ACTIVE=true")
users = {}
print(f"   Найдено пользователей: {len(users_raw)}")
print("   --- Полный список ---")
for u in users_raw:
    uid = str(u.get("ID"))
    name = f"{u.get('NAME','')} {u.get('LAST_NAME','')}".strip()
    dept = u.get("UF_DEPARTMENT", [])
    pos = u.get("WORK_POSITION", "")
    users[uid] = name if name else f"ID:{uid}"
    print(f"   ID:{uid} | {name} | Должность: {pos} | Отдел: {dept}")

# === 2. Лиды за сегодня ===
print("\n📋 Загружаю лиды за сегодня...")
leads = call_api("crm.lead.list.json",
    f"filter[>=DATE_CREATE]={TODAY}T00:00:00%2B03:00"
    f"&select[]=ID&select[]=TITLE&select[]=ASSIGNED_BY_ID&select[]=SOURCE_ID"
    f"&select[]=NAME&select[]=LAST_NAME&select[]=PHONE&select[]=COMMENTS")
print(f"   Найдено лидов: {len(leads)}")

# Лиды по менеджерам
lead_by_mgr = defaultdict(int)
for l in leads:
    mgr_id = str(l.get("ASSIGNED_BY_ID", ""))
    mgr_name = users.get(mgr_id, f"ID:{mgr_id}")
    lead_by_mgr[mgr_name] += 1

print("   --- Лиды по менеджерам ---")
for name, cnt in sorted(lead_by_mgr.items(), key=lambda x: -x[1]):
    print(f"   {name}: {cnt} лидов")

# Лиды по источникам
lead_src = defaultdict(int)
for l in leads:
    src = l.get("SOURCE_ID", "?")
    lead_src[src] += 1
print("   --- Лиды по источникам ---")
for src, cnt in sorted(lead_src.items(), key=lambda x: -x[1]):
    print(f"   {src}: {cnt}")

# === 3. Сделки за сегодня ===
print("\n💰 Загружаю сделки за сегодня...")
deals = call_api("crm.deal.list.json",
    f"filter[>=DATE_CREATE]={TODAY}T00:00:00%2B03:00"
    f"&select[]=ID&select[]=TITLE&select[]=OPPORTUNITY&select[]=ASSIGNED_BY_ID"
    f"&select[]=DATE_CREATE&select[]=STAGE_ID&select[]=COMMENTS&select[]=CONTACT_ID")
print(f"   Найдено сделок: {len(deals)}")

# Сделки по менеджерам
mgr_deals = defaultdict(list)
total_sum = 0
for d in deals:
    mgr_id = str(d.get("ASSIGNED_BY_ID", ""))
    mgr_name = users.get(mgr_id, f"ID:{mgr_id}")
    opp = float(d.get("OPPORTUNITY", 0) or 0)
    total_sum += opp
    mgr_deals[mgr_name].append({
        "id": d.get("ID"),
        "title": d.get("TITLE", ""),
        "sum": opp,
        "time": d.get("DATE_CREATE", ""),
        "stage": d.get("STAGE_ID", ""),
        "comments": d.get("COMMENTS", ""),
    })

# === 4. Звонки — с деталями ===
print("\n📞 Загружаю звонки за сегодня (с деталями)...")
calls = call_api("crm.activity.list.json",
    f"filter[>=CREATED]={TODAY}T00:00:00%2B03:00"
    f"&filter[TYPE_ID]=2"
    f"&select[]=ID&select[]=SUBJECT&select[]=RESPONSIBLE_ID&select[]=DIRECTION"
    f"&select[]=CREATED&select[]=DESCRIPTION&select[]=COMMUNICATIONS")
print(f"   Найдено звонков: {len(calls)}")

# Звонки по менеджерам
calls_by_mgr = defaultdict(int)
for c in calls:
    resp_id = str(c.get("RESPONSIBLE_ID", ""))
    resp_name = users.get(resp_id, f"ID:{resp_id}")
    calls_by_mgr[resp_name] += 1

print("   --- Звонки по менеджерам ---")
for name, cnt in sorted(calls_by_mgr.items(), key=lambda x: -x[1]):
    print(f"   {name}: {cnt} звонков")

# === ФОРМИРУЕМ КРАСИВЫЙ ОТЧЁТ ===
print("\n" + "="*60)
print(f"📊 ОТЧЁТ CRM — 21 АПРЕЛЯ 2026")
print("━"*40)

print(f"\n🔑 КЛЮЧЕВЫЕ ЦИФРЫ ДНЯ\n")
print(f"▫️ Лиды: {len(leads)}")
print(f"▫️ Сделки: {len(deals)}")
print(f"▫️ Общая сумма: {total_sum:,.0f} ₽")
if deals:
    avg = total_sum / len(deals)
    print(f"▫️ Средний чек: {avg:,.0f} ₽")
    top = max(deals, key=lambda x: float(x.get("OPPORTUNITY", 0) or 0))
    top_mgr = users.get(str(top.get("ASSIGNED_BY_ID","")), "?")
    print(f"▫️ Крупнейшая: {float(top.get('OPPORTUNITY',0)):,.0f} ₽ ({top_mgr})")

print(f"\n👩‍💼 МЕНЕДЖЕРЫ\n")
mgr_sorted = sorted(mgr_deals.items(), key=lambda x: sum(d["sum"] for d in x[1]), reverse=True)
medals = ["🥇", "🥈", "🥉"]
for i, (name, deal_list) in enumerate(mgr_sorted):
    medal = medals[i] if i < 3 else "▫️"
    mgr_sum = sum(d["sum"] for d in deal_list)
    print(f"{medal} {name} — {mgr_sum:,.0f} ₽ (~{len(deal_list)} сделок)")

print(f"\n📞 ИСТОЧНИКИ\n")
for src, cnt in sorted(lead_src.items(), key=lambda x: -x[1]):
    label = {"CALL": "📞 Звонки", "CALLBACK": "📞 Обратные звонки", 
             "WEB": "🌐 Сайт", "EMAIL": "📧 Email", "SELF": "✏️ Вручную",
             "UC_AVITO": "📱 Авито", "1": "📞 Звонки", "CRM_FORM": "📋 Форма"}.get(src, src)
    print(f"{label}: {cnt} ({cnt*100//len(leads)}%)")

print(f"\n💰 ТОП-10 СДЕЛОК\n")
deals_sorted = sorted(deals, key=lambda x: float(x.get("OPPORTUNITY", 0) or 0), reverse=True)
for i, d in enumerate(deals_sorted[:10]):
    mgr_name = users.get(str(d.get("ASSIGNED_BY_ID","")), "?")
    opp = float(d.get("OPPORTUNITY", 0) or 0)
    title = d.get("TITLE", "")
    time_str = d.get("DATE_CREATE", "")
    time_short = time_str.split("T")[1][:5] if "T" in time_str else ""
    print(f"  {i+1}. {opp:,.0f} ₽ — {mgr_name} ({time_short}) [{title}]")

# Детали ключевых звонков — берём первые 20
print(f"\n📞 КЛЮЧЕВЫЕ ЗВОНКИ\n")
for c in calls[:20]:
    subj = c.get("SUBJECT", "")
    resp = users.get(str(c.get("RESPONSIBLE_ID","")), "?")
    direction = "📥" if str(c.get("DIRECTION")) == "1" else "📤"
    created = c.get("CREATED", "")
    time_short = created.split("T")[1][:5] if "T" in created else ""
    desc = (c.get("DESCRIPTION") or "")[:100]
    # Пытаемся извлечь номер телефона из COMMUNICATIONS
    comms = c.get("COMMUNICATIONS", [])
    phone = ""
    if comms and isinstance(comms, list):
        phone = comms[0].get("VALUE", "") if isinstance(comms[0], dict) else ""
    print(f"  {direction} {time_short} | {resp} | {subj} | {phone}")
    if desc:
        print(f"     💬 {desc}")

print(f"\n📊 Конверсия лид→сделка: {len(deals)*100//max(len(leads),1)}%")
print(f"\nОтчёт сформирован Анжелочкой 🐣")
