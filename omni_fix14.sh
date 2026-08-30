#!/usr/bin/env bash
# omni_fix14.sh — обход deadlock OmniRoute (self-fetch до listen)
#
# КОНТЕКСТ (из хендоффа):
#   OmniRoute при старте делает self-fetch на localhost:${PORT} ДО listen -> ECONNREFUSED
#   -> crash-loop. Пакетный .env (/usr/lib/node_modules/omniroute/.env) ПРИОРИТЕТНЕЕ
#   systemd drop-in. Поэтому правим ИМЕННО пакетный .env, а не только drop-in.
#
# СТРАТЕГИЯ:
#   1. Поднимаем mock-HTTP на 20128 (systemd, Restart=always) — отвечает 200 на всё.
#   2. В пакетном .env: PORT=20129, BASE_URL=http://localhost:20128, прокси/TLS/SOCKS off.
#      (если self-fetch берёт BASE_URL -> идёт на mock 20128 -> 200 -> OmniRoute слушает 20129)
#   3. ДИАГНОСТИКА бинарника: какой URL реально использует self-fetch (BASE_URL vs PORT vs хардкод).
#   4. Если 20129 не поднялся -> значит self-fetch = localhost:${PORT} (не BASE_URL),
#      mock не поможет -> нужен патч бинарника (выводим найденный код).
set -u
LOG=/root/omni_fix14.log
exec >"$LOG" 2>&1
echo "=== FIX14 $(date -u) ==="

# --- 1. Mock health на 20128 ---
cat > /root/mock_health.py <<'PYEOF'
import http.server, socketserver
class H(http.server.BaseHTTPRequestHandler):
    def _ok(self):
        body=b'{"ok":true,"mock":true}'
        self.send_response(200); self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):  self._ok()
    def do_POST(self): self._ok()
    def log_message(self,*a): pass
with socketserver.TCPServer(("127.0.0.1",20128), H) as s:
    s.serve_forever()
PYEOF
cat > /etc/systemd/system/mock-health.service <<'EOF'
[Unit]
Description=Mock health server for OmniRoute self-fetch (20128)
After=network.target
[Service]
Type=simple
User=root
ExecStart=/usr/bin/python3 /root/mock_health.py
Restart=always
RestartSec=3
[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload 2>/dev/null
systemctl enable mock-health.service 2>/dev/null
systemctl restart mock-health.service 2>/dev/null
sleep 2
echo "mock (20128) check:"; curl --noproxy "*" -s -o /dev/null -w "  mock_http=%{http_code}\n" --max-time 4 http://127.0.0.1:20128/ || echo "  mock DOWN"

# --- 2. Stop + kill omniroute ---
systemctl stop omniroute.service 2>/dev/null || true
sleep 2
pkill -9 -f "omniroute/bin/omniroute.mjs" 2>/dev/null
pkill -9 -f "omniroute (v16" 2>/dev/null
pkill -9 -f "/usr/bin/omniroute" 2>/dev/null
fuser -k 20128/tcp 20129/tcp 2>/dev/null
sleep 3
ss -ltnp 2>/dev/null | grep -E "2012|2013" || echo "PORTS FREE"

# --- 3. Правим ПРИОРИТЕТНЫЙ пакетный .env (и корневой тоже) ---
# Известные пути + fallback find, чтобы точно попасть в приоритетный.
KNOWN="/usr/lib/node_modules/omniroute/.env /root/.omniroute/.env"
FOUND=$(for f in $KNOWN; do [ -f "$f" ] && echo "$f"; done)
FOUND="$FOUND $(find /opt /usr /srv /root -maxdepth 4 -name '.env' -path '*omniroute*' 2>/dev/null | sort -u)"
# убрать дубли
SEEN=""; ENV_FILES=""
for f in $FOUND; do
  case "$SEEN" in *"|$f|"*) ;; *) SEEN="$SEEN|$f|"; ENV_FILES="$ENV_FILES $f";; esac
done
echo "=== .env files to patch: $ENV_FILES ==="
for EF in $ENV_FILES; do
  [ -f "$EF" ] || continue
  cp -f "$EF" "${EF}.fix14.bak" 2>/dev/null && echo "backed up $EF"
  # PORT -> 20129 (OmniRoute слушает 20129; mock занимает 20128)
  grep -q '^PORT=' "$EF" && sed -i -E 's/^[[:space:]]*PORT=.*/PORT=20129/' "$EF" \
                  || echo 'PORT=20129' >> "$EF"
  # BASE_URL -> mock на 20128 (self-fetch пойдёт туда)
  grep -q '^BASE_URL=' "$EF" && sed -i -E 's#^[[:space:]]*BASE_URL=.*#BASE_URL=http://localhost:20128#' "$EF" \
                     || echo 'BASE_URL=http://localhost:20128' >> "$EF"
  grep -q '^NEXT_PUBLIC_BASE_URL=' "$EF" && sed -i -E 's#^[[:space:]]*NEXT_PUBLIC_BASE_URL=.*#NEXT_PUBLIC_BASE_URL=http://localhost:20128#' "$EF" \
                     || echo 'NEXT_PUBLIC_BASE_URL=http://localhost:20128' >> "$EF"
  sed -i -E 's/^[[:space:]]*ENABLE_TLS_FINGERPRINT=.*/ENABLE_TLS_FINGERPRINT=false/' "$EF"
  sed -i -E 's/^[[:space:]]*ENABLE_SOCKS5_PROXY=.*/ENABLE_SOCKS5_PROXY=false/' "$EF"
  sed -i -E 's/^[[:space:]]*NEXT_PUBLIC_ENABLE_SOCKS5_PROXY=.*/NEXT_PUBLIC_ENABLE_SOCKS5_PROXY=false/' "$EF"
  sed -i -E 's/^[[:space:]]*HTTPS_PROXY=.*/HTTPS_PROXY=/' "$EF"
  sed -i -E 's/^[[:space:]]*HTTP_PROXY=.*/HTTP_PROXY=/' "$EF"
  grep -q '^NO_PROXY=' "$EF" || echo 'NO_PROXY=127.0.0.1,localhost,::1' >> "$EF"
  echo "--- patched $EF ---"
  grep -iE '^(PORT|BASE_URL|ENABLE_TLS_FINGERPRINT|ENABLE_SOCKS5_PROXY|HTTPS_PROXY|NO_PROXY)=' "$EF" | sed -E 's/(KEY|TOKEN|SECRET|PASSWORD)=.*/\1=***/'
done

# --- 4. systemd drop-in (на всякий, дублирует .env) ---
mkdir -p /etc/systemd/system/omniroute.service.d
cat > /etc/systemd/system/omniroute.service.d/override.conf <<'EOF'
[Service]
TimeoutStartSec=300
RestartSec=10
Environment=PORT=20129
Environment=BASE_URL=http://localhost:20128
Environment=NEXT_PUBLIC_BASE_URL=http://localhost:20128
Environment=OMNIROUTE_DISABLE_LOCAL_HEALTHCHECK=true
Environment=NODE_ENV=development
Environment=ENABLE_TLS_FINGERPRINT=false
Environment=ENABLE_SOCKS5_PROXY=false
Environment=NEXT_PUBLIC_ENABLE_SOCKS5_PROXY=false
Environment=HTTPS_PROXY=
Environment=HTTP_PROXY=
Environment=NO_PROXY=127.0.0.1,localhost,::1
EOF
systemctl daemon-reload 2>/dev/null && echo "daemon-reloaded"

# --- 5. ДИАГНОСТИКА бинарника: какой URL self-fetch? ---
BIN=$(find /usr/lib/node_modules/omniroute -name 'omniroute.mjs' 2>/dev/null | head -1)
echo "=== BINARY: $BIN ==="
if [ -n "$BIN" ]; then
  echo "--- строки вокруг '20128' ---"
  grep -n -E "20128" "$BIN" | head -20
  echo "--- паттерны self/health/localhost fetch ---"
  grep -n -E "self[-_]?fetch|localhost:|BASE_URL|health|/health|fetch\(" "$BIN" | head -30
fi

# --- 6. Re-add openrouter ---
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

# --- 7. Start OmniRoute на 20129 ---
systemctl enable omniroute.service 2>/dev/null
systemctl start omniroute.service 2>/dev/null
echo "waiting for port 20129 (300s)..."
up=0
for i in $(seq 1 150); do
  code=$(curl --noproxy "*" -s -o /dev/null -w "%{http_code}" --max-time 4 http://127.0.0.1:20129/ 2>/dev/null)
  if [ -n "$code" ] && [ "$code" != "000" ]; then up=1; echo "ALIVE try=$i code=$code"; break; fi
  sleep 2
done

echo "=== DIAGNOSTICS ==="
echo "mock (20128):"; curl --noproxy "*" -s -o /dev/null -w "  mock=%{http_code}\n" --max-time 4 http://127.0.0.1:20128/
echo "omniroute (20129):"; curl --noproxy "*" -s -o /dev/null -w "  omni=%{http_code}\n" --max-time 4 http://127.0.0.1:20129/
echo "listening:"; ss -ltnp 2>/dev/null | grep -E "2012|2013" || echo "  NONE"
echo "journal tail:"; journalctl -u omniroute.service --no-pager -n 30 2>/dev/null | grep -iE "proxyfetch|ECONNREF|listen|server|error|ready|dashboard|20128|20129" | tail -15

if [ "$up" = "0" ]; then
  echo "==================================================================="
  echo "PORT 20129 НЕ ПОДНЯЛСЯ."
  echo "Скорее всего self-fetch берёт localhost:\${PORT} (20129), а не BASE_URL."
  echo "Mock на 20128 в этом случае НЕ помогает -> нужен ПАТЧ БИНАРНИКА."
  echo "Выше (=== BINARY ===) показан код формирования self-fetch URL."
  echo "==================================================================="
  echo "=== END $(date -u) ==="
  exit 1
fi

KEY=$(python3 -c "import sqlite3;print(sqlite3.connect('/root/.omniroute/storage.sqlite').execute(\"SELECT key FROM api_keys WHERE name='Hermes'\").fetchone()[0] or '')")
echo "omni_key_present=$([ -n "$KEY" ] && echo yes || echo NO)"
echo "=== TEST /v1/chat auto/free-coding on 20129 ==="
curl --noproxy "*" -s -w "\nHTTP=%{http_code}\n" --max-time 120 -X POST http://127.0.0.1:20129/v1/chat/completions \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"model":"auto/free-coding","messages":[{"role":"user","content":"ping"}],"max_tokens":60}' | head -c 1500
echo
echo "=== END $(date -u) ==="
