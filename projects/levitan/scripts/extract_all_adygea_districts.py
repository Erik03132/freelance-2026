#!/usr/bin/env python3
"""
Extract Adygea grain leads for ALL districts from the full source xlsx.

Replaces the old 3-district-only grain CSVs with a uniform grain-keyword
filter applied across every district, and rebuilds adygea_grain_all.csv.

Grain filter: keep a row if its `Описание` (lowercased) contains any grain
culture keyword. Junk rows (empty city / "добавлено..." in city column) are dropped.
"""
import csv
import os
import re
import sys

import openpyxl

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_DIR = os.path.join(BASE, "data", "campaigns", "csv")
SRC = "/Users/igorvasin/Downloads/Республика Адыгея 2025.xlsx"

# district_key -> (csv_filename, exact city value in xlsx `Город` column)
DISTRICTS = {
    "Гиагинский":       ("adygea_grain_Гиагинский_район.csv",       "Гиагинский район"),
    "Кошехабльский":    ("adygea_grain_Кошехабльский_2025.csv",      "Кошехабльский район"),
    "Красногвардейский": ("adygea_grain_Красногвардейский_2025.csv", "Красногвардейский район"),
    "Тахтамукайский":   ("adygea_grain_Тахтамукайский_район.csv",    "Тахтамукайский район"),
    "Теучежский":       ("adygea_grain_Теучежский_район.csv",        "Теучежский район"),
    "Майкопский":       ("adygea_grain_Майкопский_район.csv",        "Майкопский район"),
    "Шовгеновский":     ("adygea_grain_Шовгеновский_район.csv",      "Шовгеновский район"),
    "Майкоп":           ("adygea_grain_Майкоп_г.csv",                "Майкоп г."),
    "Адыгейск":         ("adygea_grain_Адыгейск_г.csv",              "Адыгейск г."),
}

GRAIN_KW = [
    "пшеница", "ячмень", "подсолнечник", "подсол", "кукуруза", "соя", "рапс",
    "овёс", "овес", "горох", "нут", "чечевица", "рис", "гречиха", "просо",
    "зернов", "зернобобов", "маслич", "технич",
]

OUT_COLS = ["Название", "Описание", "Регион", "Город", "Имя", "Телефоны"]


def is_grain(desc):
    d = (desc or "").lower()
    return any(kw in d for kw in GRAIN_KW)


def valid_city(city):
    c = (city or "").strip()
    if not c:
        return False
    if "добавлено" in c.lower():
        return False
    return True


def main():
    wb = openpyxl.load_workbook(SRC, read_only=True)
    ws = wb.active
    rows = [r for r in ws.iter_rows(min_row=2, values_only=True)]
    wb.close()

    # index rows by city
    by_city = {}
    for r in rows:
        if len(r) < 9:
            continue
        city = r[3]
        if not valid_city(city):
            continue
        by_city.setdefault(city, []).append(r)

    total_written = 0
    all_rows = []
    print(f"{'Район':<22} {'в xlsx':>7} {'grain':>7}")
    print("-" * 40)
    for key, (fname, city) in DISTRICTS.items():
        src = by_city.get(city, [])
        grain = [r for r in src if is_grain(r[1])]
        out = []
        for r in grain:
            out.append({
                "Название": (r[0] or "").strip(),
                "Описание": (r[1] or "").strip(),
                "Регион": (r[2] or "").strip() or "Республика Адыгея",
                "Город": (r[3] or "").strip(),
                "Имя": (r[4] or "").strip(),
                "Телефоны": (r[7] or "").strip(),
            })
        path = os.path.join(CSV_DIR, fname)
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=OUT_COLS)
            w.writeheader()
            w.writerows(out)
        all_rows.extend(out)
        total_written += len(out)
        print(f"{key:<22} {len(src):>7} {len(out):>7}")

    # combined file
    combined = os.path.join(CSV_DIR, "adygea_grain_all.csv")
    with open(combined, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=OUT_COLS)
        w.writeheader()
        w.writerows(all_rows)
    print("-" * 40)
    print(f"ИТОГО grain-строк: {total_written} | combined → {combined}")


if __name__ == "__main__":
    main()
