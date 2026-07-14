#!/usr/bin/env python3
"""
Ping Adygea numbers from adygea_ping_ready_<date>.csv (never + no_answer).
Waits ~55s for client to pick up (per-minute billing).
Saves alive numbers incrementally to data/campaigns/csv/adygea_alive_50_<date>.csv
"""
import csv
import os
import re
import signal
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ping_checker as pc

BASE = pc.BASE_DIR
CSV_DIR = pc.CSV_DIR
TARGET = 999
BATCH = 50
pc.PING_OPERATOR_WAIT = 5   # baresip отвечает <1 сек локально
pc.PING_CLIENT_WAIT = 55   # ждём клиента почти минуту (тарификация поминутная)
pc.PING_BETWEEN_CALLS = 2


def norm(n):
    d = re.sub(r"\D", "", n or "")
    if len(d) == 11 and d.startswith("8"):
        d = "7" + d[1:]
    elif len(d) == 10:
        d = "7" + d
    return d[-10:] if d else None





def load_ready():
    """Load candidates from adygea_ping_ready_<date>.csv (never + no_answer)."""
    today = datetime.now().strftime("%Y%m%d")
    fn = CSV_DIR / f"adygea_ping_ready_{today}.csv"
    if not fn.exists():
        print(f"Файл не найден: {fn}", file=sys.stderr)
        sys.exit(1)
    all_n = {}
    with open(fn, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            raw = (r.get("Телефоны") or "")
            nums = re.findall(r"\d+", raw)
            if nums:
                d = norm("".join(nums))
                if d:
                    all_n[d] = {
                        "district": (r.get("Город") or "").replace("район", "").strip().rstrip(",").strip(),
                        "city": (r.get("Город") or "").strip(),
                        "name": (r.get("Имя") or "").strip(),
                        "culture": (r.get("Описание") or "").strip(),
                    }
    return all_n


def main():
    pc.load_env()
    all_n = load_ready()

    # Координация параллельных агентов: PING_DISTRICTS=подстроки Город через запятую.
    # Оставляем только кандидатов из указанных районов; пишем в отдельный файл,
    # чтобы не перезаписывать adygea_alive_50_<date>.csv другого агента.
    scope = os.getenv("PING_DISTRICTS")
    scope_tag = ""
    if scope:
        allowed = [s.strip() for s in scope.split(",") if s.strip()]
        all_n = {d: m for d, m in all_n.items() if any(a in m["city"] for a in allowed)}
        scope_tag = "_" + "_".join(a.replace(" ", "_") for a in allowed)
        print(f"SCOPE (PING_DISTRICTS): {allowed} | кандидатов: {len(all_n)}", file=sys.stderr)

    candidates = list(all_n.keys())
    print(f"Загружено кандидатов из ready-файла: {len(candidates)}", file=sys.stderr)

    today = datetime.now().strftime("%Y%m%d")
    out_csv = CSV_DIR / f"adygea_alive{scope_tag}_{today}.csv"
    fieldnames = ["Название", "Описание", "Регион", "Город", "Имя", "Телефоны"]

    alive_records = []

    bridge = pc.PingBridge()
    if not bridge.start():
        print("BARESIP НЕ ЗАРЕГИСТРИРОВАЛСЯ — выход", file=sys.stderr)
        sys.exit(1)

    def save():
        with open(out_csv, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in alive_records:
                w.writerow(r)
        # Статус-файл для общего дедупа (prepare_ping_list glob'ает ping_*.csv)
        if scope_tag:
            status_csv = CSV_DIR / f"ping_alive{scope_tag}_{today}.csv"
            with open(status_csv, "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames)
                w.writeheader()
                for r in alive_records:
                    w.writerow(r)

    stopped = False

    def sig(s, f):
        nonlocal stopped
        stopped = True

    signal.signal(signal.SIGINT, sig)
    signal.signal(signal.SIGTERM, sig)

    try:
        for idx, d in enumerate(candidates, 1):
            if stopped:
                break
            if len(alive_records) >= TARGET:
                break
            m = all_n[d]
            phone = "7" + d
            print(f"[{idx}/{len(candidates)}] пинг {phone} ({m['district']})", file=sys.stderr)
            try:
                res = bridge.ping(phone)
            except Exception as e:
                print(f"  err: {e}", file=sys.stderr)
                res = {"status": "unknown"}
            st = res.get("status", "unknown")
            print(f"  → {st}", file=sys.stderr)
            if st == "alive":
                alive_records.append({"Название": "", "Описание": m["culture"],
                                      "Регион": "Республика Адыгея", "Город": m["city"],
                                      "Имя": m["name"], "Телефоны": phone})
                save()
                print(f"  ✅ ALIVE {len(alive_records)}/{TARGET}", file=sys.stderr)
            if idx % BATCH == 0:
                save()
                print(f"  --- батч {idx}, alive={len(alive_records)} ---", file=sys.stderr)
            time.sleep(pc.PING_BETWEEN_CALLS)
    finally:
        bridge.stop()
        save()

    print(f"\nИТОГО alive: {len(alive_records)}/{TARGET}", file=sys.stderr)
    print(f"Сохранено → {out_csv}", file=sys.stderr)


if __name__ == "__main__":
    main()
