#!/usr/bin/env bash
# split_tunnel_vps_launchd.sh — враппер для launchd.
# Запускается при подъёме сети (Network/ уведомление от launchd).
# Просто делегирует основному скрипту. Сам по себе НЕ требует прав —
# права (sudo route add) даются через sudoers NOPASSWD на этот путь.
#
# Установка (см. split_tunnel_install.md):
#   sudo bash -c 'echo "%admin ALL=(root) NOPASSWD: /Users/igorvasin/freelance-2026/split_tunnel_vps.sh" > /etc/sudoers.d/split_tunnel'
#   launchctl load ~/Library/LaunchAgents/com.user.split-tunnel-vps.plist

LOGFILE="/tmp/split_tunnel_launchd.log"
exec sudo bash /Users/igorvasin/freelance-2026/split_tunnel_vps.sh >>"$LOGFILE" 2>&1
