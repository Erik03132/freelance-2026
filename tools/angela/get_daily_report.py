#!/usr/bin/env python3
"""Полный отчёт за день из Битрикс24 через входящий вебхук"""
import urllib.request
import json
import sys
from collections import defaultdict

WH = "https://incubird.bitrix24.ru/rest/41624/w2b11s24upbycolk/"
TODAY = "2026-04-21"

def call_api(method, params=""):
    """Вызов Битрикс API с пагинацией (до 250 записей)"""
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
                if not nxt or len(all_results) >= 250:
                    break
                start = nxt
        except Exception as e:
            print(f"  API error ({method}): {e}")
            break
    return all_results

# === 1. Менеджеры (имена) ===
print("👤 Загружаю список менеджеров...")
users_raw = call_api("user.get.json", "ACTIVE=true")
users = {}
for u in users_raw:
    uid = u.get("ID")
    name = f"{u.get('NAME','')} {u.get('LAST_NAME','')}".strip()
    users[str(uid)] = name if name else f"ID:{uid}"

# === 2. Лиды за сегодня ===
print("📋 Загружаю лиды за сегодня...")
leads = call_api("crm.lead.list.json",
    f"filter[>=DATE_CREATE]={TODAY}T00:00:00%2B03:00"
    f"&select[]=ID&select[]=TITLE&select[]=ASSIGNED_BY_ID&select[]=SOURCE_ID&select[]=STATUS_ID")
print(f"   Найдено лидов: {len(leads)}")

# === 3. Сделки за сегодня (созданные) ===
print("💰 Загружаю сделки за сегодня...")
deals = call_api("crm.deal.list.json",
    f"filter[>=DATE_CREATE]={TODAY}T00:00:00%2B03:00"
    f"&select[]=ID&select[]=TITLE&select[]=OPPORTUNITY&select[]=ASSIGNED_BY_ID"
    f"&select[]=DATE_CREATE&select[]=STAGE_ID&select[]=SOURCE_ID"
    f"&select[]=CONTACT_ID&select[]=COMMENTS")
print(f"   Найдено сделок: {len(deals)}")

# === 4. Звонки/активности за сегодня ===
print("📞 Загружаю звонки за сегодня...")
calls = call_api("crm.activity.list.json",
    f"filter[>=CREATED]={TODAY}T00:00:00%2B03:00"
    f"&filter[TYPE_ID]=2"  # TYPE_ID=2 это звонки
    f"&select[]=ID&select[]=SUBJECT&select[]=RESPONSIBLE_ID&select[]=DIRECTION"
    f"&select[]=CREATED&select[]=COMPLETED")
print(f"   Найдено звонков: {len(calls)}")

# Все активности (для подсчёта чатов и других источников)
print("💬 Загружаю все активности...")
all_activities = call_api("crm.activity.list.json",
    f"filter[>=CREATED]={TODAY}T00:00:00%2B03:00"
    f"&select[]=ID&select[]=TYPE_ID&select[]=PROVIDER_ID&select[]=SUBJECT&select[]=RESPONSIBLE_ID")
print(f"   Найдено активностей: {len(all_activities)}")

# === АНАЛИТИКА ===
print("\n" + "="*60)
print(f"📊 ОТЧЁТ CRM — {TODAY}")
print("="*60)

# --- Лиды по источникам ---
lead_sources = defaultdict(int)
for l in leads:
    src = l.get("SOURCE_ID", "UNKNOWN")
    lead_sources[src] += 1

# --- Сделки по менеджерам ---
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
    })

# --- Активности по типам ---
act_types = defaultdict(int)
for a in all_activities:
    provider = a.get("PROVIDER_ID", "unknown")
    act_types[provider] += 1

# === ВЫВОД ===
print(f"\n🔑 КЛЮЧЕВЫЕ ЦИФРЫ ДНЯ")
print(f"▫️ Лиды: {len(leads)}")
print(f"▫️ Сделки: {len(deals)}")
print(f"▫️ Общая сумма: {total_sum:,.0f} ₽")
if deals:
    avg = total_sum / len(deals)
    print(f"▫️ Средний чек: {avg:,.0f} ₽")

# Топ сделка
if deals:
    top = max(deals, key=lambda x: float(x.get("OPPORTUNITY", 0) or 0))
    top_mgr = users.get(str(top.get("ASSIGNED_BY_ID","")), "?")
    print(f"▫️ Крупнейшая: {float(top.get('OPPORTUNITY',0)):,.0f} ₽ ({top_mgr})")

print(f"\n👩‍💼 МЕНЕДЖЕРЫ")
# Сортируем по общей сумме
mgr_sorted = sorted(mgr_deals.items(), key=lambda x: sum(d["sum"] for d in x[1]), reverse=True)
medals = ["🥇", "🥈", "🥉"]
for i, (name, deal_list) in enumerate(mgr_sorted):
    medal = medals[i] if i < 3 else "▫️"
    mgr_sum = sum(d["sum"] for d in deal_list)
    print(f"{medal} {name} — {mgr_sum:,.0f} ₽ (~{len(deal_list)} сделок)")

print(f"\n📞 ИСТОЧНИКИ / АКТИВНОСТИ")
for prov, cnt in sorted(act_types.items(), key=lambda x: -x[1]):
    print(f"  {prov}: {cnt}")

print(f"\n💰 ТОП-10 СДЕЛОК")
deals_sorted = sorted(deals, key=lambda x: float(x.get("OPPORTUNITY", 0) or 0), reverse=True)
for i, d in enumerate(deals_sorted[:10]):
    mgr_name = users.get(str(d.get("ASSIGNED_BY_ID","")), "?")
    opp = float(d.get("OPPORTUNITY", 0) or 0)
    title = d.get("TITLE", "")
    time_str = d.get("DATE_CREATE", "")
    # Извлекаем только время
    if "T" in time_str:
        time_short = time_str.split("T")[1][:5]
    else:
        time_short = ""
    print(f"  {i+1}. {opp:,.0f} ₽ — {mgr_name} ({time_short}) [{title}]")

print(f"\n📞 ЗВОНКИ ({len(calls)} шт)")
for c in calls[:15]:
    subj = c.get("SUBJECT", "")
    resp = users.get(str(c.get("RESPONSIBLE_ID","")), "?")
    direction = "📥" if str(c.get("DIRECTION")) == "1" else "📤"
    print(f"  {direction} {resp}: {subj}")

# Конверсия
if leads:
    conv = len(deals) / len(leads) * 100
    print(f"\n📊 Конверсия лид→сделка: {conv:.0f}%")

print(f"\nОтчёт сформирован Анжелочкой 🐣")
