#!/usr/bin/env bash
# OmniRoute VPS Recovery Script
# Секреты НЕ хранятся в репо — подтягиваются из tools/omni-auto-router/.env (gitignored).
#
# Локальная подготовка (один раз):
#   cp tools/omni-auto-router/.env.example tools/omni-auto-router/.env
#   # вписать реальные JWT_SECRET / API_KEY_SECRET / INITIAL_PASSWORD / прокси
#
# Запуск с VPS:
#   scp tools/omni-auto-router/.env root@217.149.23.113:/root/.omniroute/.env.secrets
#   ssh root@217.149.23.113 'OMNIR_SECRETS=/root/.omniroute/.env.secrets bash -s' < omniroute-recover.sh
# Альтернатива: OMNIR_SECRETS=<путь> bash omniroute-recover.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || echo '.')"
SECRETS_FILE="${OMNIR_SECRETS:-${SCRIPT_DIR}/.env}"
if [ -f "$SECRETS_FILE" ]; then
    set -a
    . "$SECRETS_FILE"
    set +a
fi

OMNIR_DIR="${OMNIR_DIR:-$HOME/.omniroute}"
OPENROUTER_KEY="${OPENROUTER_KEY:-}"

: "${JWT_SECRET:?JWT_SECRET не задан (см. $SECRETS_FILE или .env.example)}"
: "${API_KEY_SECRET:?API_KEY_SECRET не задан (см. $SECRETS_FILE или .env.example)}"
: "${INITIAL_PASSWORD:?INITIAL_PASSWORD не задан (см. $SECRETS_FILE или .env.example)}"

echo "=== OmniRoute VPS Recovery ==="

# 1. Install/update Node.js
if ! command -v node &>/dev/null; then
    echo "Installing Node.js 22 LTS..."
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
    apt-get install -y nodejs
fi
echo "Node: $(node -v)"

# 2. Install OmniRoute
if ! command -v npx &>/dev/null || ! npx omniroute --version &>/dev/null; then
    echo "Installing OmniRoute..."
    npm install -g omniroute
fi
echo "OmniRoute: $(npx omniroute --version 2>/dev/null || echo 'installed')"

# 3. Create .env
mkdir -p "$OMNIR_DIR"
cat > "$OMNIR_DIR/.env" << ENV
JWT_SECRET=${JWT_SECRET}
API_KEY_SECRET=${API_KEY_SECRET}
INITIAL_PASSWORD=${INITIAL_PASSWORD}
PORT=20128
NODE_ENV=production
ENABLE_SOCKS5_PROXY=false
ENABLE_TLS_FINGERPRINT=true
OMNIROUTE_MEMORY_MB=384
APP_LOG_LEVEL=info
APP_LOG_TO_FILE=true
CALL_LOG_RETENTION_DAYS=3
REQUIRE_API_KEY=false
HTTP_PROXY=${HTTP_PROXY}
HTTPS_PROXY=${HTTPS_PROXY}
NO_PROXY=localhost,127.0.0.1,::1
ENV

# Append OpenRouter key
echo "" >> "$OMNIR_DIR/.env"
echo "# OpenRouter API key" >> "$OMNIR_DIR/.env"
echo "OPENROUTER_API_KEY=${OPENROUTER_KEY:-YOUR_OPENROUTER_KEY_HERE}" >> "$OMNIR_DIR/.env"

echo ".env created at $OMNIR_DIR/.env"

# 4. Start via PM2
if ! command -v pm2 &>/dev/null; then
    echo "Installing PM2..."
    npm install -g pm2
fi

pm2 delete omniroute 2>/dev/null || true

# Create start script with proxy env vars
cat > /root/start-omniroute.sh << STARTEOF
#!/bin/bash
export HTTP_PROXY=${HTTP_PROXY}
export HTTPS_PROXY=${HTTPS_PROXY}
export NO_PROXY=localhost,127.0.0.1,::1,217.149.23.113
export OPENROUTER_API_KEY=${OPENROUTER_KEY:-YOUR_OPENROUTER_KEY_HERE}
sqlite3 /root/.omniroute/storage.sqlite "UPDATE provider_connections SET test_status='unknown',error_code=NULL,last_error=NULL,last_error_at=NULL,last_error_type=NULL,last_error_source=NULL,backoff_level=0,rate_limited_until=NULL,consecutive_use_count=0,updated_at=datetime('now') WHERE 1=1;"
exec /usr/bin/omniroute
STARTEOF
chmod +x /root/start-omniroute.sh

pm2 start /root/start-omniroute.sh --name omniroute
pm2 save
pm2 startup systemd -u root --hp /root 2>/dev/null || true

# 5. Install Python3 (for watchdog)
if ! command -v python3 &>/dev/null; then
    echo "Installing Python3..."
    apt-get install -y python3
fi

# 6. Watchdog systemd service
mkdir -p /root/.omniroute/logs

cat > /etc/systemd/system/omniroute-watchdog.service << WDSVC
[Unit]
Description=OmniRoute Watchdog
After=network.target
Before=omniroute.service

[Service]
Type=simple
ExecStart=/usr/bin/python3 /root/omniroute-watchdog.py
Restart=always
RestartSec=10
StandardOutput=append:/root/.omniroute/logs/watchdog.log
StandardError=append:/root/.omniroute/logs/watchdog.log

[Install]
WantedBy=multi-user.target
WDSVC

systemctl daemon-reload
systemctl enable omniroute-watchdog.service
systemctl restart omniroute-watchdog.service 2>/dev/null || true

echo "Watchdog systemd service installed and started"

# 7. Old healthcheck cron replaced by watchdog — remove
crontab -l 2>/dev/null | grep -v healthcheck-omniroute | crontab - 2>/dev/null || true
echo "Old healthcheck cron removed (watchdog takes over)"

# 8. Deploy watchdog script to VPS
cat > /root/omniroute-watchdog.py << 'WDOGEOF'
#!/usr/bin/env python3
import os, sys, time, json, logging, subprocess, urllib.request, urllib.error
from pathlib import Path

HEALTH_URL    = "http://127.0.0.1:20128/v1/models"
CHECK_INTERVAL = 30
REBOOT_AFTER   = 600
LOG_DIR        = "/root/.omniroute/logs"
TG_TOKEN       = os.environ.get("OMNIROUTE_WATCHDOG_TG_TOKEN", "")
TG_CHAT        = os.environ.get("OMNIROUTE_WATCHDOG_TG_CHAT_ID", "")

for k in list(os.environ):
    if k.endswith("_PROXY") or k.endswith("_proxy"): os.environ.pop(k, None)

Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(os.path.join(LOG_DIR, "watchdog.log")), logging.StreamHandler()])
log = logging.getLogger("wd")

def tg(msg):
    if not TG_TOKEN or not TG_CHAT: return
    try:
        u = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        r = urllib.request.Request(u, data=json.dumps({"chat_id":TG_CHAT,"text":msg}).encode(), method="POST")
        r.add_header("Content-Type","application/json")
        urllib.request.urlopen(r, timeout=10)
    except: pass

def healthy():
    try:
        r = urllib.request.urlopen(urllib.request.Request(HEALTH_URL), timeout=10)
        return r.status == 200
    except: return False

def recover(fail_s):
    log.info(f"Step 1: PM2 restart (fail={fail_s:.0f}s)")
    subprocess.run("pm2 restart omniroute", shell=True, timeout=30)
    time.sleep(5)
    if healthy():
        log.info("OK: pm2_restart")
        tg(f"\u2b06\ufe0f OmniRoute UP (pm2 restart, down {fail_s:.0f}s)")
        return "pm2_restart"
    log.info("Step 2: hard restart")
    subprocess.run("pm2 stop omniroute; pkill -f omniroute || true", shell=True, timeout=15)
    time.sleep(3)
    subprocess.run("bash /root/start-omniroute.sh &", shell=True, timeout=10)
    time.sleep(20)
    for _ in range(3):
        if healthy():
            log.info("OK: hard_restart")
            tg(f"\u2b06\ufe0f OmniRoute UP (hard restart)")
            return "hard_restart"
        time.sleep(10)
    log.info("Step 3: SQLite reset")
    subprocess.run("sqlite3 /root/.omniroute/storage.sqlite \"UPDATE provider_connections SET test_status='unknown',error_code=NULL,last_error=NULL,backoff_level=0,rate_limited_until=NULL WHERE 1=1;\"", shell=True, timeout=10)
    subprocess.run("pm2 stop omniroute; pkill -f omniroute || true", shell=True, timeout=15)
    time.sleep(3)
    subprocess.run("bash /root/start-omniroute.sh &", shell=True, timeout=10)
    time.sleep(20)
    if healthy():
        log.info("OK: sqlite_reset")
        tg(f"\u2b06\ufe0f OmniRoute UP (SQLite reset)")
        return "sqlite_reset"
    if fail_s > REBOOT_AFTER:
        log.warning("REBOOT")
        tg(f"\U0001f534 OmniRoute DEAD {fail_s:.0f}s — REBOOT")
        subprocess.run("sync && reboot", shell=True, timeout=10)
        return "reboot"
    log.warning(f"All failed, waiting (fail={fail_s:.0f}s < {REBOOT_AFTER}s)")
    tg(f"\U0001f534 OmniRoute DOWN {fail_s/60:.1f}min")
    return "waiting"

def main():
    log.info("Watchdog started"); tg("\U0001f7e2 Watchdog started")
    first_fail = None
    while True:
        if healthy():
            first_fail = None; time.sleep(CHECK_INTERVAL); continue
        now = time.time()
        if first_fail is None:
            first_fail = now
            log.warning("DOWN"); tg("\U0001f534 OmniRoute DOWN — recovering")
        recover(now - first_fail)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
WDOGEOF
chmod +x /root/omniroute-watchdog.py
echo "Watchdog deployed to /root/omniroute-watchdog.py"

echo ""
echo "=== Recovery complete ==="
echo "OmniRoute should be running on port 20128"
echo "Watchdog: systemd omniroute-watchdog.service (every 30s)"
echo "Check: curl http://localhost:20128/v1/models"
echo "Create API key via dashboard: http://217.149.23.113:20128"
echo "Password: ${INITIAL_PASSWORD}"
echo ""
echo "After login, add OpenRouter provider and create 'free-cascade' combo:"
echo "  Strategy: priority, Models: 14 free OpenRouter models"
echo "  Glitch tip: if models dropped by context filter, set 'context-optimized' strategy"
echo ""
