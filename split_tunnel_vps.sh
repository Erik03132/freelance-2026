#!/usr/bin/env bash
# split_tunnel_vps.sh — пустить VPS (217.149.23.113) напрямую, мимо VPN.
# Цель: при ВКЛЮЧЁННОМ VPN мост Mac→VPS (SSH 22, туннели 9119/8742) не падает,
#       т.к. VPS видит реальный исходящий IP Мака из whitelist-igor.
#
# SSoT: handoff_2026-08-28_remote_control_live.md
# Правило Игоря: сеть менять только с явного согласия + откат. Этот скрипт ИДЕМПОТЕНТЕН
#               и умеет себя откатывать (--undo). Бэкап таблицы маршрутов снимается.
#
# Флаги:
#   (без флагов)   применить split-tunnel (добавить хост-маршрут до VPS напрямую)
#   --undo         удалить хост-маршрут (откат)
#   --status       показать текущий маршрут до VPS
#   --help         это сообщение
#
# Требует root (sudo). Запускай: sudo bash ~/freelance-2026/split_tunnel_vps.sh

set -u
VPS="217.149.23.113"
# Шлюз берём ДИНАМИЧЕСКИ из текущего default-маршрута (меняется при смене сети/Wi-Fi).
# Если не удалось определить — fallback на хотспот.
LOCAL_GW=$(netstat -rn -f inet 2>/dev/null | awk '/^default/{print $2; exit}')
[ -z "$LOCAL_GW" ] && LOCAL_GW="172.20.10.1"
IFACE="en0"

ACTION="apply"
[ "${1:-}" = "--undo" ]   && ACTION="undo"
[ "${1:-}" = "--status" ] && ACTION="status"
[ "${1:-}" = "--help" ]   && { sed -n '2,16p' "$0"; exit 0; }

case "$ACTION" in
  status)
    echo "Маршрут до VPS ($VPS):"
    route get "$VPS" 2>/dev/null | grep -E "gateway|interface" || echo "(нет маршрута)"
    exit 0 ;;
  undo)
    echo "Откат: удаляем хост-маршрут $VPS"
    sudo route delete -host "$VPS" 2>/dev/null && echo "удалён" || echo "уже нет / не удалён"
    exit 0 ;;
esac

# APPLY
echo "Бэкап таблицы маршрутов -> /tmp/routes_backup_$(date +%s).txt"
netstat -rn -f inet > /tmp/routes_backup_$(date +%s).txt 2>/dev/null

# Если маршрут уже на local gw — ничего не делаем (идемпотентность)
CUR=$(route get "$VPS" 2>/dev/null | awk '/gateway:/{print $2}')
if [ "$CUR" = "$LOCAL_GW" ]; then
  echo "✅ Маршрут до $VPS уже напрямую через $LOCAL_GW — не трогаем."
  exit 0
fi

echo "Добавляем хост-маршрут: $VPS -> $LOCAL_GW ($IFACE)"
sudo route add -host "$VPS" "$LOCAL_GW" 2>&1
if [ $? -eq 0 ]; then
  echo "✅ Готово. Проверь: route get $VPS (должен показать gateway: $LOCAL_GW)"
  echo "   Теперь при ВКЛ VPN трафик до VPS пойдёт мимо туннеля."
else
  echo "❌ Не удалось добавить маршрут (см. ошибку выше)." >&2
  exit 1
fi
