import csv

FINAL = "data/campaigns/csv/adygea_alive_FINAL_20260712.csv"
SRC = "data/campaigns/csv/adygea_alive_20260712.csv"
FIELDS = ["Название", "Описание", "Регион", "Город", "Имя", "Телефоны"]


def load(path):
    rows = []
    try:
        with open(path, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                rows.append(row)
    except FileNotFoundError:
        pass
    return rows


existing = set()
rows = load(FINAL)
for r in rows:
    existing.add(r.get("Телефоны"))

added = 0
for r in load(SRC):
    p = r.get("Телефоны")
    if p and p not in existing:
        existing.add(p)
        rows.append(r)
        added += 1

with open(FINAL, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS)
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in FIELDS})

if added:
    print(f"merged {added} new -> FINAL now {len(rows)} rows")
else:
    print(f"FINAL {len(rows)} rows (no new)")
