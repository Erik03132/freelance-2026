#!/usr/bin/env bash
set -u
LOG=/root/omni_restart.log
exec > "$LOG" 2>&1
echo "=== RESTART $(date -u) ==="
systemctl restart omniroute.service 2>/dev/null || true
echo "waiting for port 20128 (up to 120s)..."
up=0
for i in $(seq 1 60); do
  code=$(curl --noproxy "*" -s -o /dev/null -w "%{http_code}" --max-time 4 http://127.0.0.1:20128/ 2>/dev/null)
  if [ -n "$code" ] && [ "$code" != "000" ]; then up=1; echo "PORT ALIVE try=$i code=$code"; break; fi
  sleep 2
done
[ "$up" = "0" ] && { echo "PORT NEVER CAME UP"; journalctl -u omniroute.service --no-pager -n 40 2>/dev/null | grep -iE "error|listen|crash|EADDR|refused|fatal" | tail -15; exit 1; }
KEY=$(python3 -c "import sqlite3;print(sqlite3.connect('/root/.omniroute/storage.sqlite').execute(\"SELECT key FROM api_keys WHERE name='Hermes'\").fetchone()[0] or '')" 2>/dev/null)
echo "omni_key_present=$([ -n "$KEY" ] && echo yes || echo NO)"
echo "=== combos in db ==="; sqlite3 /root/.omniroute/storage.sqlite "SELECT name,length(data) FROM combos"
echo "=== TEST /v1/chat auto/free-coding ==="
curl --noproxy "*" -s -w "\nHTTP=%{http_code}\n" --max-time 120 -X POST http://127.0.0.1:20128/v1/chat/completions \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"model":"auto/free-coding","messages":[{"role":"user","content":"ping hello"}],"max_tokens":60}' | head -c 2000
echo
echo "=== TEST /v1/models ==="
curl --noproxy "*" -s -o /dev/null -w "models_http=%{http_code}\n" --max-time 20 -H "Authorization: Bearer $KEY" http://127.0.0.1:20128/v1/models
echo "=== END $(date -u) ==="
