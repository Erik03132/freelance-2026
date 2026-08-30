#!/usr/bin/env bash
set -u
LOG=/root/omni_debug.log
# stop systemd so it doesn't fight us
systemctl stop omniroute.service 2>/dev/null || true
sleep 2
pkill -9 -f "omniroute/bin/omniroute.mjs" 2>/dev/null
pkill -9 -f "omniroute (v16" 2>/dev/null
pkill -9 -f "/usr/bin/omniroute" 2>/dev/null
fuser -k 20128/tcp 2>/dev/null
sleep 4
# Run omniroute manually in foreground, capture ALL output for 70s
cd /root/.omniroute
echo "=== MANUAL RUN START $(date -u) ===" > "$LOG"
timeout 75 node /usr/lib/node_modules/omniroute/bin/omniroute.mjs >> "$LOG" 2>&1
echo "=== MANUAL RUN EXIT rc=$? at $(date -u) ===" >> "$LOG"
echo "=== final 40 lines ===" >> "$LOG"
tail -40 "$LOG" >> "$LOG"
echo "=== port after manual run ===" >> "$LOG"
(ss -ltnp 2>/dev/null | grep 20128 || echo "no 20128") >> "$LOG"
