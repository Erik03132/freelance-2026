#!/usr/bin/env bash
set -u
LOG=/root/omni_fix13.log
exec >"$LOG" 2>&1
echo "=== FIX13 $(date -u) ==="

systemctl stop omniroute.service 2>/dev/null || true
sleep 2
pkill -9 -f "omniroute/bin/omniroute.mjs" 2>/dev/null
pkill -9 -f "omniroute (v16" 2>/dev/null
pkill -9 -f "/usr/bin/omniroute" 2>/dev/null
fuser -k 20128/tcp 2>/dev/null
sleep 4
ss -ltnp 2>/dev/null | grep -E "2012|2013" || echo "PORTS FREE"

mkdir -p /etc/systemd/system/omniroute.service.d
cat > /etc/systemd/system/omniroute.service.d/override.conf <<'EOF'
[Service]
TimeoutStartSec=300
RestartSec=10
Environment=OMNIROUTE_DISABLE_LOCAL_HEALTHCHECK=true
Environment=NODE_ENV=development
Environment=BASE_URL=
Environment=NEXT_PUBLIC_BASE_URL=
Environment=ENABLE_TLS_FINGERPRINT=false
Environment=ENABLE_SOCKS5_PROXY=false
Environment=NEXT_PUBLIC_ENABLE_SOCKS5_PROXY=false
Environment=HTTPS_PROXY=
Environment=HTTP_PROXY=
Environment=NO_PROXY=127.0.0.1,localhost,::1
EOF
systemctl daemon-reload 2>/dev/null && echo "daemon-reloaded, LOCAL_HEALTHCHECK disabled"

python3 - <<'PY'
import sqlite3, datetime, os
db="/root/.omniroute/storage.sqlite"
bk="/root/.openrouter_key.bak"
key=None
if os.path.exists(bk):
    key=open(bk).read().strip()
if not key:
    try:
        for line in open("/opt/levitan/projects/levitan/.env"):
            if line.startswith("OPENROUTER_API_KEY="):
                key=line.strip().split("=",1)[1]; break
    except Exception: pass
con=sqlite3.connect(db); c=con.cursor()
c.execute("DELETE FROM provider_connections WHERE provider='openrouter'")
c.execute("""INSERT INTO provider_connections
  (id,provider,auth_type,name,email,priority,is_active,display_name,default_model,api_key,created_at,updated_at)
  VALUES ('openrouter-001','openrouter','api_key','OpenRouter','','0',1,'OpenRouter','auto/free-coding',?,datetime('now'),datetime('now'))""", (key,))
con.commit(); con.close()
print("openrouter re-added (key len %d)" % (len(key) if key else 0))
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
if [ "$up" = "0" ]; then echo "PORT NEVER UP"; journalctl -u omniroute.service --no-pager -n 15 2>/dev/null | grep -iE "proxyfetch|ECONNREF|server|listen|error|health" | tail -10; exit 1; fi

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
