#!/usr/bin/env bash
set -u
LOG=/root/omni_fix4.log
exec >"$LOG" 2>&1
echo "=== FIX4 $(date -u) ==="

# 1. Remove the resurrecting cron job
( crontab -l 2>/dev/null | grep -v "healthcheck-omniroute" | crontab - ) 2>/dev/null && echo "cron healthcheck removed" || echo "crontab update rc=$?"
echo "--- remaining cron ---"; (crontab -l 2>/dev/null | grep -iE "omniroute") || echo "no omniroute cron left"

# 2. Stop pm2 omniroute + disable pm2 resurrection
which pm2 >/dev/null 2>&1 && { pm2 delete omniroute 2>/dev/null; pm2 save 2>/dev/null; } || true

# 3. Stop systemd (so we can kill everything cleanly)
systemctl stop omniroute.service 2>/dev/null || true
sleep 2

# 4. Kill ALL omniroute procs (incl. ones spawned by healthcheck/cron)
pkill -9 -f "omniroute/bin/omniroute.mjs" 2>/dev/null; echo "kill mjs rc=$?"
pkill -9 -f "omniroute (v16" 2>/dev/null; echo "kill worker rc=$?"
pkill -9 -f "/usr/bin/omniroute" 2>/dev/null; echo "kill bin rc=$?"
pkill -9 -f "healthcheck-omniroute" 2>/dev/null; echo "kill hc rc=$?"
fuser -k 20128/tcp 2>/dev/null; echo "fuser rc=$?"
sleep 5

echo "--- ss AFTER kill ---"; ss -ltnp 2>/dev/null | grep -E "2012|2013" || echo "PORTS FREE"
echo "--- procs AFTER kill ---"; ps -eo pid,ppid,cmd | grep -iE "omniroute" | grep -v grep || echo "NONE"

# 5. Start ONLY systemd
systemctl enable omniroute.service 2>/dev/null
systemctl start omniroute.service 2>/dev/null
echo "waiting for port 20128 (150s)..."
up=0
for i in $(seq 1 75); do
  code=$(curl --noproxy "*" -s -o /dev/null -w "%{http_code}" --max-time 4 http://127.0.0.1:20128/ 2>/dev/null)
  if [ -n "$code" ] && [ "$code" != "000" ]; then up=1; echo "ALIVE try=$i code=$code"; break; fi
  sleep 2
done
if [ "$up" = "0" ]; then
  echo "PORT NEVER UP"; ss -ltnp 2>/dev/null | grep 20128 || echo "nobody holds 20128"
  journalctl -u omniroute.service --no-pager -n 20 2>/dev/null | grep -iE "error|EADDR|listen|crash" | tail
  exit 1
fi

KEY=$(python3 -c "import sqlite3;print(sqlite3.connect('/root/.omniroute/storage.sqlite').execute(\"SELECT key FROM api_keys WHERE name='Hermes'\").fetchone()[0] or '')")
echo "omni_key_present=$([ -n "$KEY" ] && echo yes || echo NO)"
echo "=== combos ==="; sqlite3 /root/.omniroute/storage.sqlite "SELECT name FROM combos"
echo "=== TEST /v1/chat auto/free-coding ==="
curl --noproxy "*" -s -w "\nHTTP=%{http_code}\n" --max-time 120 -X POST http://127.0.0.1:20128/v1/chat/completions \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"model":"auto/free-coding","messages":[{"role":"user","content":"ping"}],"max_tokens":60}' | head -c 2000
echo
echo "=== TEST /v1/models ==="
curl --noproxy "*" -s -o /dev/null -w "models_http=%{http_code}\n" --max-time 20 -H "Authorization: Bearer $KEY" http://127.0.0.1:20128/v1/models
echo "=== END $(date -u) ==="
