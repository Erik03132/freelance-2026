#!/usr/bin/env bash
set -u
LOG=/root/omni_fix5.log
exec >"$LOG" 2>&1
echo "=== FIX5 $(date -u) ==="

# Match local Mac setup: keep ONLY openrouter (remove extra hanging providers)
echo "--- provider_connections BEFORE ---"; sqlite3 /root/.omniroute/storage.sqlite "SELECT id,provider,name FROM provider_connections"
sqlite3 /root/.omniroute/storage.sqlite "DELETE FROM provider_connections WHERE provider<>'openrouter';" && echo "removed non-openrouter providers"
echo "--- AFTER ---"; sqlite3 /root/.omniroute/storage.sqlite "SELECT id,provider,name FROM provider_connections"

# Increase systemd TimeoutStartSec so HTTP server has time if healthcheck is slow
mkdir -p /etc/systemd/system/omniroute.service.d
cat > /etc/systemd/system/omniroute.service.d/override.conf <<'EOF'
[Service]
TimeoutStartSec=300
RestartSec=10
EOF
systemctl daemon-reload 2>/dev/null && echo "daemon-reloaded, TimeoutStartSec=300"

# Ensure no resurrectors
( crontab -l 2>/dev/null | grep -v "healthcheck-omniroute" | crontab - ) 2>/dev/null
which pm2 >/dev/null 2>&1 && { pm2 delete omniroute 2>/dev/null; pm2 save 2>/dev/null; } || true

# Stop + kill all
systemctl stop omniroute.service 2>/dev/null || true
sleep 2
pkill -9 -f "omniroute/bin/omniroute.mjs" 2>/dev/null
pkill -9 -f "omniroute (v16" 2>/dev/null
pkill -9 -f "/usr/bin/omniroute" 2>/dev/null
pkill -9 -f "healthcheck-omniroute" 2>/dev/null
fuser -k 20128/tcp 2>/dev/null
sleep 5
ss -ltnp 2>/dev/null | grep -E "2012|2013" || echo "PORTS FREE"

# Start only systemd
systemctl enable omniroute.service 2>/dev/null
systemctl start omniroute.service 2>/dev/null

echo "waiting for port 20128 (up to 280s)..."
up=0
for i in $(seq 1 140); do
  code=$(curl --noproxy "*" -s -o /dev/null -w "%{http_code}" --max-time 4 http://127.0.0.1:20128/ 2>/dev/null)
  if [ -n "$code" ] && [ "$code" != "000" ]; then up=1; echo "ALIVE try=$i code=$code"; break; fi
  sleep 2
done
if [ "$up" = "0" ]; then
  echo "PORT NEVER UP"
  echo "--- last startup log ---"
  journalctl -u omniroute.service --no-pager -n 30 2>/dev/null | grep -iE "server|listen|health|credential|error|timeout|warn" | tail -20
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
