#!/bin/bash
# my_ip.sh — показать текущий публичный IP Мака (для дежурного цикла VPS-туннеля).
# SSoT: ACTIVE_TASKS.md → «СИНХРОНИЗАЦИЯ Mac ↔ VPS».
# Когда туннель упал (VPS закрыт из-за смены динамического IP):
#   1. bash ~/freelance-2026/my_ip.sh   → узнать IP
#   2. в ТГ главному боту: «открой <IP> в ufw на VPS»
#   3. LaunchAgent сам ретраит туннель (~10с)
set -u
IP=$(curl -s --noproxy '*' --max-time 8 https://api.ipify.org 2>/dev/null || dig +short myip.opendns.com @resolver1.opendns.com 2>/dev/null)
if [ -z "$IP" ]; then echo "IP не определён (нет сети?)" >&2; exit 1; fi
echo "$IP"
