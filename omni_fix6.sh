#!/usr/bin/env bash
set -u
LOG=/root/omni_fix6.log
exec >"$LOG" 2>&1
echo "=== FIX6 $(date -u) ==="
OR_KEY=$(grep -E "^OPENROUTER_API_KEY=" /opt/levitan/projects/levitan/.env | head -1 | cut -d= -f2-)
echo "OR_KEY len: ${#OR_KEY}"

# 1. stop + kill
systemctl stop omniroute.service 2>/dev/null || true
sleep 2
pkill -9 -f "omniroute/bin/omniroute.mjs" 2>/dev/null
pkill -9 -f "omniroute (v16" 2>/dev/null
pkill -9 -f "/usr/bin/omniroute" 2>/dev/null
fuser -k 20128/tcp 2>/dev/null
sleep 4
ss -ltnp 2>/dev/null | grep -E "2012|2013" || echo "PORTS FREE"

# 2. TEMPORARILY remove openrouter so CredentialHealth = 0/0 at startup
sqlite3 /root/.omniroute/storage.sqlite "DELETE FROM provider_connections;" && echo "all provider_connections removed (startup will have 0)"
# keep a backup of the key
echo "$OR_KEY" > /root/.openrouter_key.bak
chmod 600 /root/.openrouter_key.bak

# 3. start with 0 providers -> HTTP should come up fast
systemctl enable omniroute.service 2>/dev/null
systemctl start omniroute.service 2>/dev/null
echo "waiting for port 20128 (180s) with 0 providers..."
up=0
for i in $(seq 1 90); do
  code=$(curl --noproxy "*" -s -o /dev/null -w "%{http_code}" --max-time 4 http://127.0.0.1:20128/ 2>/dev/null)
  if [ -n "$code" ] && [ "$code" != "000" ]; then up=1; echo "ALIVE try=$i code=$code"; break; fi
  sleep 2
done
if [ "$up" = "0" ]; then
  echo "PORT NEVER UP even with 0 providers!"
  journalctl -u omniroute.service --no-pager -n 25 2>/dev/null | tail -20
  exit 1
fi
echo ">>> HTTP server is UP with 0 providers"

# 4. re-add openrouter via hot-reload (CredentialHealth will hang in bg, but HTTP stays up)
python3 - <<PY
import sqlite3, datetime
db="/root/.omniroute/storage.sqlite"
OR_KEY = open("/root/.openrouter_key.bak").read().strip()
con=sqlite3.connect(db); c=con.cursor()
c.execute("""INSERT INTO provider_connections (id,provider,auth_type,name,email,priority,is_active,display_name,default_model,api_key)
             VALUES ('openrouter-001','openrouter','api_key','OpenRouter','','0',1,'OpenRouter','auto/free-coding',?)""", (OR_KEY,))
con.commit(); con.close()
print("openrouter re-added (hot-reload will pick up)")
PY
sleep 8
echo "=== combos ==="; sqlite3 /root/.omniroute/storage.sqlite "SELECT name FROM combos"

KEY=$(python3 -c "import sqlite3;print(sqlite3.connect('/root/.omniroute/storage.sqlite').execute(\"SELECT key FROM api_keys WHERE name='Hermes'\").fetchone()[0] or '')")
echo "omni_key_present=$([ -n "$KEY" ] && echo yes || echo NO)"
echo "=== port still up? ==="; curl --noproxy "*" -s -o /dev/null -w "root=%{http_code}\n" --max-time 5 http://127.0.0.1:20128/
echo "=== TEST /v1/chat auto/free-coding ==="
curl --noproxy "*" -s -w "\nHTTP=%{http_code}\n" --max-time 120 -X POST http://127.0.0.1:20128/v1/chat/completions \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"model":"auto/free-coding","messages":[{"role":"user","content":"ping"}],"max_tokens":60}' | head -c 2000
echo
echo "=== TEST /v1/models ==="
curl --noproxy "*" -s -o /dev/null -w "models_http=%{http_code}\n" --max-time 20 -H "Authorization: Bearer $KEY" http://127.0.0.1:20128/v1/models
echo "=== END $(date -u) ==="
