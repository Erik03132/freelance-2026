#!/bin/zsh
# Вотчдог: единоличный пингер. Убивает конкурирующие ping_adygea и чужие baresip,
# мержит общий adygea_alive_20260712.csv в adygea_alive_FINAL_20260712.csv.
MYPID=$1
ROOT=/Users/igorvasin/freelance-2026/projects/levitan
cd "$ROOT"
echo "watchdog start: MYPID=$MYPID"
while kill -0 "$MYPID" 2>/dev/null; do
  # убить конкурирующие прогоны ping_adygea
  for p in $(pgrep -f "ping_adygea_alive.py"); do
    if [ "$p" != "$MYPID" ]; then
      echo "$(date +%H:%M:%S) kill competitor ping_adygea pid=$p"
      kill -9 "$p" 2>/dev/null
    fi
  done
  # убить baresip, не принадлежащий моему прогону
  for bp in $(pgrep -f baresip); do
    ppid=$(ps -o ppid= -p "$bp" 2>/dev/null | tr -d ' ')
    if [ "$ppid" != "$MYPID" ]; then
      echo "$(date +%H:%M:%S) kill orphan baresip pid=$bp (ppid=$ppid)"
      kill -9 "$bp" 2>/dev/null
    fi
  done
  # мерж общий файл -> FINAL
  python3 scripts/merge_alive.py
  sleep 15
done
echo "watchdog stop: MYPID=$MYPID завершён"
