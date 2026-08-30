#!/bin/bash
# Автономный фикс OmniRoute на VPS через launchd-туннель (2222->VPS:22)
# Ждёт восстановления туннеля, потом чинит OmniRoute и ботов.
# Результат пишет в /Users/igorvasin/freelance-2026/fix_vps_report.txt

REPORT=/Users/igorvasin/freelance-2026/fix_vps_report.txt
KEY=/Users/igorvasin/freelance-2026/.ssh_agent_key
echo "=== START $(date) ===" > "$REPORT"

# Ждём, пока туннель 2222 оживёт (после отключения VPN Мак выходит как 95.154.153.47)
for i in $(seq 1 60); do
  if ssh -o ConnectTimeout=4 -o StrictHostKeyChecking=no -i "$KEY" -p 2222 root@127.0.0.1 "echo OK" 2>/dev/null; then
    echo "Туннель 2222 жив на итерации $i" >> "$REPORT"
    break
  fi
  sleep 5
done

# Проверяем, что зашли
if ! ssh -o ConnectTimeout=4 -o StrictHostKeyChecking=no -i "$KEY" -p 2222 root@127.0.0.1 "echo OK" 2>/dev/null; then
  echo "ТУННЕЛЬ НЕ ПОДНЯЛСЯ за 5 мин — выход" >> "$REPORT"
  exit 1
fi

# Что на VPS
ssh -o StrictHostKeyChecking=no -i "$KEY" -p 2222 root@127.0.0.1 <<'EOSSH' >> "$REPORT" 2>&1
echo "=== SSH на VPS OK ==="
echo "--- systemctl omni/hermes ---"
systemctl is-active omniroute hermes-gateway hermes-serve pm2-root 2>&1
echo "--- порт 20128 ---"
ss -tlnp | grep 20128 || echo "20128 НЕ слушается"
echo "--- curl localhost:20128/v1/models ---"
curl -s --max-time 8 http://127.0.0.1:20128/v1/models 2>&1 | python3 -c "import sys,json;d=json.load(sys.stdin);print('Моделей:',len(d.get('data',[])))" 2>&1 || echo "CURL FAILED"
echo "--- curl chat test ---"
curl -s --max-time 8 -X POST http://127.0.0.1:20128/v1/chat/completions -H "Content-Type: application/json" -d '{"model":"auto/free-coding-full","messages":[{"role":"user","content":"Hi"}],"max_tokens":5}' 2>&1 | head -c 300
echo
echo "--- journalctl omni errors (10 min) ---"
journalctl -u omniroute --no-pager --since "10 min ago" 2>&1 | grep -iE 'error|fail|timeout|unreach|400' | tail -8
EOSSH

echo "=== END $(date) ===" >> "$REPORT"
