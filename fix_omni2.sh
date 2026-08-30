#!/usr/bin/env bash
set -u
LOG=/root/omni_fix2.log
exec > "$LOG" 2>&1
echo "=== FIX2 START $(date -u) ==="
OR_KEY=""
if [ -r /opt/levitan/projects/levitan/.env ]; then
  OR_KEY=$(grep -E "^OPENROUTER_API_KEY=" /opt/levitan/projects/levitan/.env | head -1 | cut -d= -f2-)
fi
echo "OR_KEY len: ${#OR_KEY}"

# Stop ALL managers that can respawn omniroute
systemctl stop omniroute.service 2>/dev/null || true
systemctl disable omniroute.service 2>/dev/null || true
# pm2?
which pm2 >/dev/null 2>&1 && (pm2 stop omniroute 2>/dev/null; pm2 delete omniroute 2>/dev/null) || true
# healthcheck script
pkill -9 -f "healthcheck-omniroute" 2>/dev/null || true
# kill all omniroute node procs
pkill -9 -f "omniroute/bin/omniroute.mjs" 2>/dev/null || true
pkill -9 -f "omniroute (v16" 2>/dev/null || true
pkill -9 -f "/usr/bin/omniroute" 2>/dev/null || true
sleep 4

# verify port free
free=1
for i in $(seq 1 10); do
  if (ss -ltnp 2>/dev/null | grep -qE "2012|2013"); then free=0; echo "PORT STILL BUSY try $i"; sleep 2; else free=1; break; fi
done
[ "$free" = "0" ] && { echo "FATAL: port still busy, aborting"; exit 9; }
echo "PORT FREE confirmed"

# Write DB
python3 - <<PY
import sqlite3, json, datetime
db="/root/.omniroute/storage.sqlite"
OR_KEY = open("/dev/stdin").read().strip() if False else None
PY
# pass OR_KEY via env to python
OR_KEY_LEN=${#OR_KEY}
python3 /root/apply_db.py "$OR_KEY" || { echo "apply_db failed"; }
echo "--- re-enable + start ---"
systemctl enable omniroute.service 2>/dev/null || true
systemctl start omniroute.service 2>/dev/null || true
# wait port
up=0
for i in $(seq 1 50); do
  code=$(curl --noproxy "*" -s -o /dev/null -w "%{http_code}" --max-time 4 http://127.0.0.1:20128/ 2>/dev/null)
  if [ -n "$code" ] && [ "$code" != "000" ]; then up=1; echo "PORT ALIVE try=$i code=$code"; break; fi
  sleep 2
done
[ "$up" = "0" ] && echo "PORT NEVER CAME UP"

KEY=$(python3 -c "import sqlite3;print(sqlite3.connect('/root/.omniroute/storage.sqlite').execute(\"SELECT key FROM api_keys WHERE name='Hermes'\").fetchone()[0] or '')" 2>/dev/null)
echo "omni_key_present=$([ -n "$KEY" ] && echo yes || echo NO)"
echo "=== TEST /v1/chat auto/free-coding ==="
curl --noproxy "*" -s -w "\nHTTP=%{http_code}\n" --max-time 120 -X POST http://127.0.0.1:20128/v1/chat/completions \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"model":"auto/free-coding","messages":[{"role":"user","content":"ping hello"}],"max_tokens":60}' | head -c 2000
echo
echo "=== TEST /v1/models ==="
curl --noproxy "*" -s -o /dev/null -w "models_http=%{http_code}\n" --max-time 20 -H "Authorization: Bearer $KEY" http://127.0.0.1:20128/v1/models
echo "=== FIX2 END $(date -u) ==="
