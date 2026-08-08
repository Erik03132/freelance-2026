#!/usr/bin/env python3
"""OmniRoute Watchdog — monitors VPS OmniRoute health and auto-recovers.

Deployment: systemd service or cron every 30s.
Checks: HTTP 200 on :20128/v1/models + /v1/chat/completions functional test.
Recovery: PM2 restart → hard restart → system reboot (escalating).

SIGNALS (for notification):
- notify_on_recovery: true → TG message on each recovery
- SMALL_*: short outages (< 5 min)
- LONG_*: outages > 5 min requiring reboot
"""

import os
import sys
import time
import json
import signal
import socket
import urllib.request
import urllib.error
import subprocess
import logging
from datetime import datetime, timezone
from pathlib import Path

# ── config ──────────────────────────────────────────────────
HEALTH_URL = os.environ.get("OMNIROUTE_HEALTH_URL", "http://127.0.0.1:20128/v1/models")
FUNC_URL = os.environ.get("OMNIROUTE_FUNC_URL", "http://127.0.0.1:20128/v1/chat/completions")
CHECK_INTERVAL = int(os.environ.get("OMNIROUTE_WATCHDOG_INTERVAL", "30"))  # seconds
MAX_RESTART_ATTEMPTS = int(os.environ.get("OMNIROUTE_WATCHDOG_MAX_RESTARTS", "3"))
REBOOT_AFTER_MINUTES = int(os.environ.get("OMNIROUTE_WATCHDOG_REBOOT_AFTER", "10"))  # minutes
LOG_DIR = os.environ.get("OMNIROUTE_WATCHDOG_LOG_DIR", "/root/.omniroute/logs")
TG_BOT_TOKEN = os.environ.get("OMNIROUTE_WATCHDOG_TG_TOKEN", "")
TG_CHAT_ID = os.environ.get("OMNIROUTE_WATCHDOG_TG_CHAT_ID", "")

DRY_RUN = os.environ.get("OMNIROUTE_WATCHDOG_DRY_RUN", "0") == "1"
# dummy proxy salvo for no-proxy to localhost
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)

Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "watchdog.log")),
        logging.StreamHandler(sys.stderr),
    ],
)
log = logging.getLogger("omniroute-watchdog")


def tg_send(text: str) -> bool:
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        return False
    try:
        url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
        data = json.dumps({"chat_id": TG_CHAT_ID, "text": text, "disable_web_page_preview": True}).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        resp = urllib.request.urlopen(req, timeout=10)
        return resp.status == 200
    except Exception:
        return False


def check_health() -> bool:
    """Returns True if OmniRoute is healthy."""
    try:
        req = urllib.request.Request(HEALTH_URL, method="GET")
        req.add_header("User-Agent", "omniroute-watchdog/1.0")
        resp = urllib.request.urlopen(req, timeout=10)
        return resp.status == 200
    except Exception:
        return False


def check_functional() -> bool:
    """Returns True if OmniRoute can serve chat completions."""
    try:
        body = json.dumps({
            "model": "auto",
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 10,
        }).encode()
        req = urllib.request.Request(FUNC_URL, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("User-Agent", "omniroute-watchdog/1.0")
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        return "choices" in data
    except Exception:
        return False


def run_pm2(cmd: str) -> tuple[int, str]:
    try:
        r = subprocess.run(f"pm2 {cmd}", shell=True, capture_output=True, text=True, timeout=30)
        return r.returncode, r.stdout.strip() + r.stderr.strip()
    except Exception as e:
        return -1, str(e)


def recovery_cycle(downtime_seconds: float) -> str:
    """Returns recovery action taken."""
    action = "none"

    if DRY_RUN:
        log.warning(f"[DRY-RUN] would recover (downtime={downtime_seconds:.0f}s)")
        return "dry_run"

    # Step 1: PM2 restart
    log.info("Step 1: PM2 restart omniroute")
    rc, out = run_pm2("restart omniroute")
    if rc == 0:
        time.sleep(5)
        if check_health():
            action = "pm2_restart"
            log.info(f"Recovered via PM2 restart (downtime={downtime_seconds:.0f}s)")
            tg_send(f"⬆️ OmniRoute recovered via PM2 restart (down {downtime_seconds:.0f}s)")
            return action

    # Step 2: PM2 stop + killall + start fresh
    log.info("Step 2: PM2 hard restart")
    run_pm2("stop omniroute")
    time.sleep(2)
    subprocess.run("pkill -f omniroute || true", shell=True, timeout=10)
    time.sleep(3)
    subprocess.run("bash /root/start-omniroute.sh &", shell=True, timeout=10)
    time.sleep(20)

    for attempt in range(MAX_RESTART_ATTEMPTS):
        if check_health():
            action = "hard_restart"
            log.info(f"Recovered via hard restart (downtime={downtime_seconds:.0f}s, attempt={attempt+1})")
            tg_send(f"⬆️ OmniRoute recovered via hard restart (down {downtime_seconds:.0f}s)")
            return action
        time.sleep(10)

    # Step 3: SQLite reset + restart
    log.info("Step 3: SQLite reset + restart")
    subprocess.run(
        "sqlite3 /root/.omniroute/storage.sqlite "
        "\"UPDATE provider_connections SET test_status='unknown',error_code=NULL,last_error=NULL,"
        "backoff_level=0,rate_limited_until=NULL,consecutive_use_count=0,updated_at=datetime('now') WHERE 1=1;\"",
        shell=True, timeout=10
    )
    run_pm2("stop omniroute")
    time.sleep(2)
    subprocess.run("bash /root/start-omniroute.sh &", shell=True, timeout=10)
    time.sleep(20)

    if check_health():
        action = "sqlite_reset_restart"
        log.info(f"Recovered via SQLite reset (downtime={downtime_seconds:.0f}s)")
        tg_send(f"⬆️ OmniRoute recovered via SQLite reset + restart (down {downtime_seconds:.0f}s)")
        return action

    # Step 4: Reboot (if downtime > threshold)
    if downtime_seconds > REBOOT_AFTER_MINUTES * 60:
        log.warning(f"Step 4: REBOOT (downtime={downtime_seconds:.0f}s > {REBOOT_AFTER_MINUTES}min)")
        tg_send(f"🔴 OmniRoute DEAD for {downtime_seconds:.0f}s. Attempting REBOOT.")
        if not DRY_RUN:
            subprocess.run("sync && reboot", shell=True, timeout=10)
        action = "reboot"
    else:
        log.warning(f"All recovery steps failed, downtime < {REBOOT_AFTER_MINUTES}min, waiting")
        action = "failed_all"
        tg_send(f"🔴 OmniRoute DOWN {downtime_seconds/60:.1f}min. All recovery steps failed. Awaiting reboot threshold.")

    return action


def status_strip(action: str, downtime: float) -> str:
    """One-line status for the status file (consumed by monitoring)."""
    ts = datetime.now(timezone.utc).isoformat()
    return f"{ts} | action={action} | downtime_s={downtime:.0f} | healthy={int(check_health())}"


def run_forever():
    log.info("OmniRoute Watchdog started")
    tg_send("🟢 OmniRoute Watchdog started")
    first_failure_at: float | None = None
    last_status = "healthy"
    status_file = os.path.join(LOG_DIR, "watchdog.status")

    while True:
        healthy = check_health()

        if healthy:
            if first_failure_at is not None:
                downtime = time.time() - first_failure_at
                log.info(f"Health restored after {downtime:.0f}s downtime")
                first_failure_at = None
            if last_status != "healthy":
                tg_send("✅ OmniRoute HEALTHY")
            last_status = "healthy"
        else:
            functional = check_functional()
            now = time.time()

            if first_failure_at is None:
                first_failure_at = now
                log.warning("Health check FAILED — starting recovery cycle")
                tg_send("🔴 OmniRoute DOWN — starting recovery cycle")

            downtime = now - first_failure_at
            log.warning(f"Still down ({downtime:.0f}s), healthy={healthy}, functional={functional}")

            if functional:
                log.info("Health endpoint failed but functional test passed — treating as healthy")
                first_failure_at = None
                last_status = "healthy"
                tg_send("⚠️ OmniRoute health endpoint failed but functional OK")
            else:
                last_status = "down"
                action = recovery_cycle(downtime)
                # Write status file
                with open(status_file, "w") as f:
                    f.write(status_strip(action, downtime))

        time.sleep(CHECK_INTERVAL)


def main():
    if "--oneshot" in sys.argv:
        healthy = check_health()
        functional = check_functional() if not healthy else True
        print(f"healthy={healthy} functional={functional}")
        if not healthy and not functional:
            action = recovery_cycle(0)
            print(f"recovery_action={action}")
        sys.exit(0 if healthy or functional else 1)

    run_forever()


if __name__ == "__main__":
    main()
