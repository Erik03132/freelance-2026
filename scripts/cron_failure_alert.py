#!/usr/bin/env python3
"""
ES-23: Явный failure-сигнал для cron-задач (не «тихий» режим).
Читает ~/.hermes/cron/executions.db, находит свежие FAILED / зависшие
(running/claimed старше stall_min) выполнения и пишет ЯВНЫЙ алерт:
  - в локальный лог ~/.hermes/cron/failure_alerts.log
  - (опц.) отправляет в Telegram-origin, если задан --notify и доступен tg-cli
Алерт НЕ маскирует сбой: статус FAIL/STALL пишется явно, с именем джобы.

Обратимо: только чтение БД + запись лога. Сами джобы не трогает.
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta, UTC

CRON_DIR = os.path.expanduser("~/.hermes/cron")
DB = os.path.join(CRON_DIR, "executions.db")
ALERT_LOG = os.path.join(CRON_DIR, "failure_alerts.log")
JOBS_JSON = os.path.join(CRON_DIR, "jobs.json")


def load_job_names():
    try:
        d = json.load(open(JOBS_JSON))
        return {j["id"]: j.get("name", j["id"]) for j in d.get("jobs", [])}
    except Exception:
        return {}


def parse_ts(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--lookback-min", type=int, default=1440, help="окно анализа, мин (по умолч. 24ч)"
    )
    ap.add_argument(
        "--stall-min", type=int, default=30, help="порог зависания для running/claimed, мин"
    )
    ap.add_argument(
        "--notify", action="store_true", help="пытаться отправить в Telegram-origin (если доступно)"
    )
    args = ap.parse_args()

    if not os.path.exists(DB):
        print("DB не найдена:", DB, file=sys.stderr)
        return 2

    names = load_job_names()
    now = datetime.now(UTC)
    cutoff = now - timedelta(minutes=args.lookback_min)
    alerts = []

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT job_id, status, finished_at, claimed_at, started_at, error "
        "FROM executions ORDER BY claimed_at DESC"
    ).fetchall()
    conn.close()

    for r in rows:
        claimed = parse_ts(r["claimed_at"])
        if claimed and claimed < cutoff:
            continue
        job_name = names.get(r["job_id"], r["job_id"])
        status = r["status"]
        if status == "failed":
            alerts.append(
                f"FAIL | {job_name} | {r['finished_at'] or r['claimed_at']} | "
                f"{ (r['error'] or '')[:160] }"
            )
        elif status in ("running", "claimed"):
            started = parse_ts(r["started_at"]) or parse_ts(r["claimed_at"])
            if started and (now - started) > timedelta(minutes=args.stall_min):
                alerts.append(
                    f"STALL | {job_name} | статус={status} с {started.isoformat()} "
                    f"(>{args.stall_min}мин) — возможно зависло"
                )

    if not alerts:
        print("OK: свежих сбоев/зависаний не найдено.")
        return 0

    # Явный алерт — пишем в локальный лог с меткой
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    block = [f"=== CRON FAILURE ALERT @ {ts} ({len(alerts)} сигналов) ==="]
    block += alerts
    block.append("")
    with open(ALERT_LOG, "a", encoding="utf-8") as f:
        f.write("\n".join(block))

    print("ОБНАРУЖЕНЫ СБОИ (явный алерт записан в failure_alerts.log):")
    for a in alerts:
        print("  -", a)

    if args.notify:
        # TODO(ES-23): интеграция с tg-cli при наличии; пока заглушка
        print("  [notify] Telegram-уведомление не настроено (заглушка).")

    return 1  # ненулевой код = есть алерты (для cron notify_on_complete)


if __name__ == "__main__":
    sys.exit(main())
