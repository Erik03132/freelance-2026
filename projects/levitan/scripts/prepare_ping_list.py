#!/usr/bin/env python3
"""Prepare Adygea ping candidate list: not-covered + no_answer (didn't pick up)."""
import csv
import glob
import os
import re
from collections import defaultdict, Counter
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_DIR = os.path.join(BASE, "data", "campaigns", "csv")


def norm(n):
    d = re.sub(r"\D", "", n or "")
    if len(d) == 11 and d.startswith("8"):
        d = "7" + d[1:]
    elif len(d) == 10:
        d = "7" + d
    return d[-10:] if d else None


# Все 9 районов Адыгеи (файлы grain-CSV сгенерированы extract_all_adygea_districts.py)
DISTRICT_FILES = {
    "Гиагинский": "data/campaigns/csv/adygea_grain_Гиагинский_район.csv",
    "Кошехабльский": "data/campaigns/csv/adygea_grain_Кошехабльский_2025.csv",
    "Красногвардейский": "data/campaigns/csv/adygea_grain_Красногвардейский_2025.csv",
    "Тахтамукайский": "data/campaigns/csv/adygea_grain_Тахтамукайский_район.csv",
    "Теучежский": "data/campaigns/csv/adygea_grain_Теучежский_район.csv",
    "Майкопский": "data/campaigns/csv/adygea_grain_Майкопский_район.csv",
    "Шовгеновский": "data/campaigns/csv/adygea_grain_Шовгеновский_район.csv",
    "Майкоп": "data/campaigns/csv/adygea_grain_Майкоп_г.csv",
    "Адыгейск": "data/campaigns/csv/adygea_grain_Адыгейск_г.csv",
}


def load_all():
    files = DISTRICT_FILES
    all_n = {}
    for dist, fn in files.items():
        with open(os.path.join(BASE, fn), encoding="utf-8") as f:
            for r in csv.DictReader(f):
                raw = (r.get("Телефоны") or "")
                nums = re.findall(r"\d+", raw)
                if nums:
                    d = norm("".join(nums))
                    if d:
                        all_n[d] = {
                            "district": dist,
                            "city": (r.get("Город") or "").strip() or dist,
                            "name": (r.get("Имя") or r.get("Название") or "").strip(),
                            "culture": (r.get("Описание") or "").strip(),
                        }
    return all_n


def load_statuses():
    status = defaultdict(list)
    for fn in glob.glob(os.path.join(CSV_DIR, "ping_*.csv")) + \
             glob.glob(os.path.join(CSV_DIR, "_ping*.csv")) + \
             glob.glob(os.path.join(CSV_DIR, "adygea_grain_*pinged*.csv")):
        base = os.path.basename(fn)
        st = base.split("_")[1] if "_" in base else "unknown"
        if st not in ("alive", "no_answer", "dead", "unreachable", "unknown"):
            continue
        try:
            with open(fn, encoding="utf-8") as f:
                for r in csv.DictReader(f):
                    for col in ("Телефоны", "phone"):
                        v = r.get(col)
                        if v:
                            d = norm(v)
                            if d:
                                status[st].append(d)
        except Exception:
            pass
    best = {}
    order = {"alive": 3, "no_answer": 2, "unreachable": 1, "dead": 1, "unknown": 0}
    for st, lst in status.items():
        for d in lst:
            if d not in best or order[st] > order[best[d]]:
                best[d] = st
    return best


def main():
    all_n = load_all()
    best = load_statuses()

    never = [d for d in all_n if d not in best]
    no_answer = [d for d in all_n if best.get(d) == "no_answer"]
    unknown = [d for d in all_n if best.get(d) == "unknown"]
    alive = [d for d in all_n if best.get(d) == "alive"]
    dead = [d for d in all_n if best.get(d) in ("dead", "unreachable")]

    # Primary candidates per user request: not-covered + no_answer
    candidates = sorted(set(never) | set(no_answer))
    # Optionally include unknown
    candidates_with_unknown = sorted(set(candidates) | set(unknown))

    print("=" * 50)
    print(f"Всего номеров Адыгеи: {len(all_n)}")
    print(f"  ✅ Уже alive (брать не надо): {len(alive)}")
    print(f"  💀 dead/unreachable (не звоним): {len(dead)}")
    print(f"  ❓ unknown (пингали, неясно): {len(unknown)}")
    print(f"  ⚪ не охвачены (никогда не звонили): {len(never)}")
    print(f"  🔴 не взяли трубку (no_answer): {len(no_answer)}")
    print("-" * 50)
    print(f"КАНДИДАТЫ НА ПИНГ (неохваченные + no_answer): {len(candidates)}")
    print(f"  (+ с unknown для полноты): {len(candidates_with_unknown)}")
    by_dist = Counter(all_n[d]["district"] for d in candidates)
    print("  По районам:", dict(by_dist))

    # Save prepared CSV (never + no_answer)
    today = datetime.now().strftime("%Y%m%d")
    out = os.path.join(CSV_DIR, f"adygea_ping_ready_{today}.csv")
    fieldnames = ["Название", "Описание", "Регион", "Город", "Имя", "Телефоны", "ping_reason"]
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for d in candidates:
            m = all_n[d]
            reason = "never" if d in never else "no_answer"
            w.writerow({
                "Название": "", "Описание": m["culture"], "Регион": "Республика Адыгея",
                "Город": m["city"], "Имя": m["name"],
                "Телефоны": "7" + d, "ping_reason": reason,
            })
    print(f"\nГотовый список сохранён → {out}")
    print(f"Ждём окончания обзвона сотрудника, потом: python3 scripts/ping_adygea_alive.py")


if __name__ == "__main__":
    main()
