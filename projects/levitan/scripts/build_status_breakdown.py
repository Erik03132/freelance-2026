import csv, re

ROOT = "/Users/igorvasin/freelance-2026/projects/levitan/data/campaigns/csv"
LOG = f"{ROOT}/ping_solo_final.log"
READY = f"{ROOT}/adygea_ping_ready_20260712.csv"
OUT = f"{ROOT}/adygea_status_breakdown_20260712.csv"
SUMMARY = f"{ROOT}/adygea_status_summary_20260712.csv"

# кандидаты: телефон -> (город, имя, описание)
cand = {}
with open(READY, encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f):
        cand[r["Телефоны"]] = (r["Город"], r["Имя"], r["Описание"])

# парсим лог: [N/149] пинг PHONE (DISTRICT)  ->  → STATUS
status = {}
cur = {}
with open(LOG, encoding="utf-8") as f:
    for line in f:
        m = re.match(r"\[(\d+)/\d+\] пинг (\d+) \((.+)\)", line)
        if m:
            cur = {"phone": m.group(2), "log_district": m.group(3)}
            continue
        m2 = re.match(r"\s*→\s*(\w+)", line)
        if m2 and cur:
            status[cur["phone"]] = m2.group(1)
            cur = {}

# собираем итог
rows = []
for phone, (gorod, imya, opis) in cand.items():
    st = status.get(phone, "not_pinged")
    rows.append({"Телефоны": phone, "Город": gorod, "Имя": imya,
                 "Описание": opis, "Статус": st})

rows.sort(key=lambda r: (r["Город"], r["Имя"]))

with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["Телефоны", "Город", "Имя", "Описание", "Статус"])
    w.writeheader()
    w.writerows(rows)

# сводка по районам и статусам
from collections import defaultdict
agg = defaultdict(lambda: defaultdict(int))
for r in rows:
    agg[r["Город"]][r["Статус"]] += 1

order = ["alive", "no_answer", "unreachable", "unknown", "not_pinged"]
with open(SUMMARY, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Город", "alive", "no_answer", "unreachable", "unknown", "not_pinged", "ВСЕГО"])
    tot = defaultdict(int)
    for gorod in sorted(agg):
        counts = agg[gorod]
        row = [gorod] + [counts.get(s, 0) for s in order]
        row.append(sum(counts.values()))
        w.writerow(row)
        for s in order:
            tot[s] += counts.get(s, 0)
    w.writerow(["ВСЕГО"] + [tot[s] for s in order] + [sum(tot.values())])

print(f"Записей: {len(rows)} -> {OUT}")
print(f"Сводка -> {SUMMARY}")
print("alive:", sum(1 for r in rows if r["Статус"] == "alive"))
print("no_answer:", sum(1 for r in rows if r["Статус"] == "no_answer"))
print("unreachable:", sum(1 for r in rows if r["Статус"] == "unreachable"))
print("unknown:", sum(1 for r in rows if r["Статус"] == "unknown"))
