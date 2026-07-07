#!/usr/bin/env python3
"""
Levitan Campaign Runner — 100-call baseline script.
====================================================

Запускает N звонков (по умолчанию 100) с паузой между звонками.
После завершения выводит метрики: connect_rate, lead_percent, avg_duration, calls_per_hour.

Запуск:
    python3 scripts/campaign_runner.py [--calls 100] [--csv path/to/file.csv] [--ext 22]

Зависимости: requests, httpx
"""

import argparse
import csv
import hashlib
import json
import logging
import os
import sys
import time
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("campaign-runner")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = DATA_DIR / "call_results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# .env
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

# Config
MANGO_API_KEY = os.getenv("MANGO_VPBX_API_KEY", "")
MANGO_API_SALT = os.getenv("MANGO_VPBX_API_SALT", "")
MANGO_API_BASE = "https://app.mango-office.ru/vpbx/"
MANGO_FROM_EXTENSION = os.getenv("MANGO_FROM_EXTENSION", "22")
CALL_INTERVAL = int(os.getenv("CALL_INTERVAL", "5"))


def norm_phone(num: str) -> str:
    import re
    d = re.sub(r"\D", "", num or "")
    if len(d) == 11 and d.startswith("8"):
        d = "7" + d[1:]
    elif len(d) == 10:
        d = "7" + d
    return d


def is_valid_phone(num: str) -> bool:
    n = norm_phone(num)
    return len(n) == 11 and n.startswith("7")


def mango_callback(client_phone: str, from_ext: Optional[str] = None) -> dict:
    ext = from_ext or MANGO_FROM_EXTENSION
    command_id = f"cmp_{uuid.uuid4().hex[:8]}"
    payload = {
        "command_id": command_id,
        "from": {"extension": ext},
        "to_number": norm_phone(client_phone),
        "timeout": 30,
    }
    j = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    sign = hashlib.sha256((MANGO_API_KEY + j + MANGO_API_SALT).encode()).hexdigest()
    try:
        import requests
        r = requests.post(
            f"{MANGO_API_BASE}commands/callback",
            data={"vpbx_api_key": MANGO_API_KEY, "json": j, "sign": sign},
            timeout=20,
        )
        return r.json()
    except Exception as e:
        log.error("Callback error: %s", e)
        return {"error": str(e)}


def load_contacts(csv_path: str) -> list[dict]:
    contacts = []
    path = Path(csv_path)
    if not path.exists():
        log.error("CSV not found: %s", csv_path)
        return contacts
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            phones = row.get("Телефоны", row.get("phone", "")) or ""
            import re
            phone_list = re.findall(r"[\d\-\(\)\+\s]{7,}", phones)
            for phone in phone_list:
                normalized = norm_phone(phone)
                if is_valid_phone(normalized):
                    contacts.append({
                        "name": row.get("Название", row.get("company_name", row.get("company", ""))).strip(),
                        "phone": normalized,
                    })
                    break
    return contacts


def run_campaign(csv_path: str, max_calls: int = 100, from_ext: Optional[str] = None) -> dict:
    contacts = load_contacts(csv_path)
    if not contacts:
        log.error("No valid contacts found in %s", csv_path)
        return {}

    log.info("Loaded %d contacts from %s", len(contacts), csv_path)
    log.info("Making up to %d calls with interval %d sec", max_calls, CALL_INTERVAL)

    results: list[dict] = []
    start_time = time.time()

    for i, contact in enumerate(contacts[:max_calls]):
        call_start = time.time()
        log.info("[%d/%d] Calling %s (%s)", i + 1, min(max_calls, len(contacts)),
                 contact["phone"], contact["name"][:30])

        result = mango_callback(contact["phone"], from_ext)
        call_result = result.get("result")
        call_duration = round(time.time() - call_start)

        entry = {
            "call_id": i + 1,
            "phone": contact["phone"],
            "company": contact["name"],
            "call_start": datetime.fromtimestamp(call_start).isoformat(),
            "duration_sec": call_duration,
            "mango_result": call_result,
            "error": result.get("error", ""),
        }

        # Определяем статус ответа
        if call_result in (1000, "1000"):
            entry["answer_status"] = "connected"
        elif "error" in result:
            entry["answer_status"] = "error"
            entry["notes"] = result.get("error", "unknown error")
        else:
            entry["answer_status"] = "no_answer"

        results.append(entry)
        log.info("  → result=%s, duration=%ds", entry["answer_status"], call_duration)

        # Пауза между звонками (кроме последнего)
        if i < len(contacts[:max_calls]) - 1:
            time.sleep(CALL_INTERVAL)

    total_time = time.time() - start_time
    hours = total_time / 3600
    total_calls = len(results)
    connected = sum(1 for r in results if r["answer_status"] == "connected")

    summary = {
        "timestamp": datetime.now().isoformat(),
        "campaign_csv": csv_path,
        "total_calls": total_calls,
        "total_time_sec": round(total_time, 1),
        "total_time_hours": round(hours, 2),
        "connected": connected,
        "no_answer": sum(1 for r in results if r["answer_status"] == "no_answer"),
        "errors": sum(1 for r in results if r["answer_status"] == "error"),
        "connect_rate": round(connected / total_calls * 100, 1) if total_calls else 0,
        # lead_percent будет обновлён после LLM-обработки, пока placeholder
        "lead_percent_placeholder": 0,
        "avg_duration_sec": round(
            sum(r["duration_sec"] for r in results if r["answer_status"] == "connected") / connected, 1
        ) if connected else 0,
        "calls_per_hour": round(total_calls / hours, 1) if hours > 0 else total_calls,
    }

    # Сохраняем результаты
    today = datetime.now().strftime("%Y-%m-%d")
    results_path = RESULTS_DIR / f"campaign_results_{today}.json"
    results_path.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    log.info("Results saved: %s", results_path)

    # Сохраняем сводку
    summary_path = RESULTS_DIR / "campaign_summary.csv"
    summary_exists = summary_path.exists()
    with open(summary_path, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary.keys()))
        if not summary_exists:
            writer.writeheader()
        writer.writerow(summary)
    log.info("Summary saved: %s", summary_path)

    return summary


def main():
    parser = argparse.ArgumentParser(description="Levitan Campaign Runner")
    parser.add_argument("--calls", type=int, default=100, help="Number of calls (default: 100)")
    parser.add_argument("--csv", type=str, default=None,
                        help="Path to CSV contact file")
    parser.add_argument("--ext", type=str, default=MANGO_FROM_EXTENSION,
                        help="Mango extension (default: %(default)s)")
    args = parser.parse_args()

    if args.csv:
        csv_path = args.csv
    else:
        # Авто-поиск CSV
        csv_dir = DATA_DIR / "campaigns" / "csv"
        csv_files = sorted(csv_dir.glob("*.csv"))
        if not csv_files:
            log.error("No CSV files found. Use --csv to specify.")
            sys.exit(1)
        csv_path = str(csv_files[-1])
        log.info("Auto-selected CSV: %s", csv_path)

    if not MANGO_API_KEY or not MANGO_API_SALT:
        log.error("MANGO_VPBX_API_KEY and MANGO_VPBX_API_SALT must be set in .env")
        sys.exit(1)

    log.info("=== Campaign Runner ===")
    log.info("Calls: %d", args.calls)
    log.info("CSV: %s", csv_path)
    log.info("Ext: %s", args.ext)

    summary = run_campaign(csv_path, max_calls=args.calls, from_ext=args.ext)

    if summary:
        print()
        print("=" * 50)
        print("CAMPAIGN SUMMARY")
        print("=" * 50)
        print(f"  Total calls:  {summary['total_calls']}")
        print(f"  Connected:    {summary['connected']} ({summary['connect_rate']}%)")
        print(f"  No answer:    {summary['no_answer']}")
        print(f"  Errors:       {summary['errors']}")
        print(f"  Avg duration: {summary['avg_duration_sec']}s")
        print(f"  Calls/hour:   {summary['calls_per_hour']}")
        print(f"  Total time:   {summary['total_time_hours']}h")
        print("=" * 50)


if __name__ == "__main__":
    main()
