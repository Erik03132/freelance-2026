#!/usr/bin/env bash
set -u
LOG=/root/omni_noproxy.log
exec >"$LOG" 2>&1
echo "=== NO-PROXY TEST $(date -u) ==="
systemctl stop omniroute.service 2>/dev/null || true
sleep 2
pkill -9 -f "omniroute/bin/omniroute.mjs" 2>/dev/null
pkill -9 -f "omniroute (v16" 2>/dev/null
pkill -9 -f "/usr/bin/omniroute" 2>/dev/null
fuser -k 20128/tcp 2>/dev/null
sleep 4
# re-add openrouter so we test real config but WITHOUT proxy env
OR_KEY=$(cat /root/.openrouter_key.bak 2>/dev/null || grep -E "^OPENROUTER_API_KEY=" /opt/levitan/projects/levitan/.env | head -1 | cut -d= -f2-)
sqlite3 /root/.omniroute/storage.sqlite "DELETE FROM provider_connections;"
sqlite3 /root/.omniroute/storage.sqlite "INSERT INTO provider_connections (id,provider,auth_type,name,email,priority,is_active,display_name,default_model,api_key) VALUES ('openrouter-001','openrouter','api_key','OpenRouter','','0',1,'OpenRouter','auto/free-coding','$OR_KEY');"
echo "provider re-added, starting WITHOUT proxy env"
cd /root/.omniroute
# run WITHOUT HTTP(S)_PROXY to test if localhost self-fetch was the blocker
nohup env -u HTTP_PROXY -u HTTPS_PROXY -u http_proxy -u https_proxy node /usr/lib/node_modules/omniroute/bin/omniroute.mjs >/root/omni_noproxy_run.log 2>&1 &
NPID=$!
echo "node pid=$NPID"
# poll port 20128 for 70s
up=0
for i in $(seq 1 35); do
  code=$(curl --noproxy "*" -s -o /dev/null -w "%{http_code}" --max-time 4 http://127.0.0.1:20128/ 2>/dev/null)
  ssout=$(ss -ltnp 2>/dev/null | grep 20128 | head -1)
  echo "t=$i code=$code ss='$ssout'"
  if [ -n "$code" ] && [ "$code" != "000" ]; then up=1; echo "ALIVE at t=$i code=$code"; break; fi
  sleep 2
done
echo "RESULT up=$up"
echo "=== tail run log ==="
tail -25 /root/omni_noproxy_run.log 2>/dev/null
# leave it running if up, else kill
if [ "$up" = "1" ]; then
  echo "SERVER UP - leaving running for chat test"
  KEY=$(python3 -c "import sqlite3;print(sqlite3.connect('/root/.omniroute/storage.sqlite').execute(\"SELECT key FROM api_keys WHERE name='Hermes'\").fetchone()[0] or '')")
  echo "=== TEST /v1/chat auto/free-coding ==="
  curl --noproxy "*" -s -w "\nHTTP=%{http_code}\n" --max-time 120 -X POST http://127.0.0.1:20128/v1/chat/completions -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" -d '{"model":"auto/free-coding","messages":[{"role":"user","content":"ping"}],"max_tokens":60}' | head -c 1500
  echo
else
  echo "STILL DOWN - killing node"
  kill -9 $NPID 2>/dev/null
fi
echo "=== END $(date -u) ==="
