#!/bin/bash
# Запуск на VPS, выводит pm2 list + логи ошибок последних процессов
echo "=== PM2 LIST ==="
pm2 list

echo ""
echo "=== PM2 JLIST (JSON) ==="
pm2 jlist 2>/dev/null | python3 -c "
import sys, json
data = json.load(sys.stdin)
for p in data:
    name = p.get('name','?')
    status = p.get('pm2_env',{}).get('status','?')
    restarts = p.get('pm2_env',{}).get('restart_time',0)
    uptime = p.get('pm2_env',{}).get('pm_uptime',0)
    print(f'  {name}: status={status}, restarts={restarts}, uptime_ms={uptime}')
" 2>/dev/null || echo "(json parse failed)"

echo ""
echo "=== ПОСЛЕДНИЕ ОШИБКИ (по 5 строк) ==="
for logfile in /root/antigravity/ai-eggs/agent/logs/*_error.log; do
    if [ -f "\$logfile" ]; then
        echo "--- \$(basename \$logfile) ---"
        tail -5 "\$logfile"
        echo ""
    fi
done
