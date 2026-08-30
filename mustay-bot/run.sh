#!/usr/bin/env bash
# Фоновый запуск Mustay/Hermes-бота (чистый, без сенаторской темы).
set -euo pipefail
cd "$(dirname "$0")"
source .env 2>/dev/null || true
export MUSTAY_BOT_TOKEN="${MUSTAY_BOT_TOKEN:-}"
export MUSTAY_ADMIN_ID="${MUSTAY_ADMIN_ID:-176203333}"
# TELEGRAM_PROXY берём из .env (в РФ нужен для доступа к Telegram API).
export TELEGRAM_PROXY="${TELEGRAM_PROXY:-}"
exec ./.venv/bin/python agent/tg_bot.py
