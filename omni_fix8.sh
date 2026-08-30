#!/usr/bin/env bash
set -u
LOG=/root/omni_fix8.log
exec >"$LOG" 2>&1
echo "=== FIX8 $(date -u) ==="

systemctl stop omniroute.service 2>/dev/null || true
sleep 2
pkill -9 -f "omniroute/bin/omniroute.mjs" 2>/dev/null
pkill -9 -f "omniroute (v16" 2>/dev/null
pkill -9 -f "/usr/bin/omniroute" 2>/dev/null
fuser -k 20128/tcp 2>/dev/null
sleep 4
ss -ltnp 2>/dev/null | grep -E "2012|2013" || echo "PORTS FREE"

# Disable TLS_FINGERPRINT (it routes ALL egress incl loopback via proxy -> breaks self-fetch)
# and ensure no HTTPS_PROXY hidden in .env
sed -i -E 's/^[[:space:]]*ENABLE_TLS_FINGERPRINT=.*/#DISABLED_ENABLE_TLS_FINGERPRINT=disabled/' /root/.omniroute/.env
sed -i -E 's/^[[:space:]]*HTTPS_PROXY=.*/#&/' /root/.omniroute/.env
sed -i -E 's/^[[:space:]]*HTTP_PROXY=.*/#&/' /root/.omniroute/.env
echo "--- .env proxy/tls lines now ---"; grep -iE "TLS_FINGERPRINT|HTTPS_PROXY|HTTP_PROXY" /root/.omniroute/.env || echo "(none active)"

# drop-in: no global proxy, but protect loopback via NO_PROXY
mkdir -p /etc/systemd/system/omniroute.service.d
cat > /etc/systemd/system/omniroute.service.d/override.conf <<'EOF'
[Service]
TimeoutStartSec=300
RestartSec=10
Environment=HTTP_PROXY=
Environment=HTTPS_PROXY=
Environment=NO_PROXY=127.0.0.1,localhost,::1
EOF
systemctl daemon-reload 2>/dev/null && echo "daemon-reloaded"

# re-add openrouter (fixed: no broken heredoc)
OR_KEY=$(cat /root/.openrouter_key.bak 2>/dev/null || grep -E "^OPENROUTER_API_KEY=" /opt/levitan/projects/levitan/.env | head -1 | cut -d= -f2-)
echo "OR_KEY len: ${#OR_KEY}"
python3 - <<PY
import sqlite3, datetime, sys
db="/root/.omniroute/storage.sqlite"
OR_KEY = sys.argv[1]
con=sqlite3.connect(db); c=con.cursor()
c.execute("SELECT id FROM provider_connections WHERE provider='openrouter'")
if not c.fetchone():
    c.execute("""INSERT INTO provider_connections
      (id,provider,auth_type,name,email,priority,is_active,display_name,default_model,api_key,created_at,updated_at)
      VALUES ('openrouter-001','openrouter','api_key','OpenRouter','','0',1,'OpenRouter','auto/free-coding',?,datetime('now'),datetime('now'))""", (OR_KEY,))
    print("openrouter re-added")
else:
    print("openrouter present")
con.commit(); con.close()
PY
echo "--- provider_connections ---"; sqlite3 /root/.omniroute/storage.sqlite "SELECT id,provider,name FROM provider_connections"

systemctl enable omniroute.service 2>/dev/null
systemctl start omniroute.service 2>/dev/null
echo "waiting for port 20128 (240s)..."
up=0
for i in $(seq 1 120); do
  code=$(curl --noproxy "*" -s -o /dev/null -w "%{http_code}" --max-time 4 http://127.0.0.1:20128/ 2>/dev/null)
  if [ -n "$code" ] && [ "$code" != "000" ]; then up=1; echo "ALIVE try=$i code=$code"; break; fi
  sleep 2
done
if [ "$up" = "0" ]; then echo "PORT NEVER UP"; journalctl -u omniroute.service --no-pager -n 15 2>/dev/null | grep -iE "proxyfetch|ECONNREF|server|listen|error" | tail -10; exit 1; fi

KEY=$(python3 -c "import sqlite3;print(sqlite3.connect('/root/.omniroute/storage.sqlite').execute(\"SELECT key FROM api_keys WHERE name='Hermes'\").fetchone()[0] or '')")
echo "omni_key_present=$([ -n "$KEY" ] && echo yes || echo NO)"
echo "=== TEST /v1/chat auto/free-coding ==="
curl --noproxy "*" -s -w "\nHTTP=%{http_code}\n" --max-time 120 -X POST http://127.0.0.1:20128/v1/chat/completions \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"model":"auto/free-coding","messages":[{"role":"user","content":"ping"}],"max_tokens":60}' | head -c 1500
echo
echo "=== TEST /v1/models ==="
curl --noproxy "*" -s -o /dev/null -w "models_http=%{http_code}\n" --max-time 20 -H "Authorization: Bearer $KEY" http://127.0.0.1:20128/v1/models
echo "=== END $(date -u) ==="
