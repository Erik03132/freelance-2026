#!/usr/bin/env bash
# Фоновый запуск Hermes-бота (@hermes03132).
# ВАЖНО: бот ходит в Telegram через локальный SOCKS5-туннель (127.0.0.1:64468),
# который пробрасывается через VPS 217.149.23.113 (SSH-порт 2222) на US-прокси 172.120.21.141.
# Перед запуском бота ТУННЕЛЬ ДОЛЖЕН БЫТЬ ПОДНЯТ отдельно, например:
#   ssh -N -L 127.0.0.1:64468:172.120.21.141:64468 root@217.149.23.113 -p 2222
set -euo pipefail
cd "$(dirname "$0")"
source .env 2>/dev/null || true
export HERMES03132_BOT_TOKEN="${HERMES03132_BOT_TOKEN:-}"
export HERMES_ADMIN_ID="${HERMES_ADMIN_ID:-176203333}"
export TELEGRAM_PROXY="${TELEGRAM_PROXY:-}"
exec ./.venv/bin/python agent/tg_bot.py
