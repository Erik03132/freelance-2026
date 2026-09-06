#!/bin/bash
# Start Levitan Webhook Server + Tunnel
# Usage: bash scripts/webhook_start.sh

PORT=8088
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "Starting Levitan Webhook Server..."

# Kill existing
pkill -f "webhook_server.py" 2>/dev/null
pkill -f "localtunnel --port $PORT" 2>/dev/null
sleep 1

# Start webhook server
nohup python3 "$PROJECT_DIR/scripts/webhook_server.py" > /tmp/levitan_webhook.log 2>&1 &
echo "Webhook PID: $!"
sleep 2

# Start tunnel
nohup npx localtunnel --port $PORT > /tmp/localtunnel.log 2>&1 &
LT_PID=$!
echo "Tunnel PID: $LT_PID"
sleep 5

# Get tunnel URL
TUNNEL_URL=$(grep -o 'https://[^ ]*\.loca\.lt' /tmp/localtunnel.log | head -1)
if [ -z "$TUNNEL_URL" ]; then
    echo "Failed to get tunnel URL. Check /tmp/localtunnel.log"
    cat /tmp/localtunnel.log
    exit 1
fi

echo ""
echo "✅ Webhook ready!"
echo "   URL: $TUNNEL_URL"
echo "   Health: $TUNNEL_URL/health"
echo "   Events: $TUNNEL_URL/mango-webhook"
echo ""
echo "📋 Настройка в Mango Office:"
echo "   1. Личный кабинет → Настройки → Уведомления → HTTP"
echo "   2. URL: $TUNNEL_URL/mango-webhook"
echo "   3. Выбрать событие: Речевая аналитика / Конспект (Summary)"
echo "   4. Сохранить"
echo ""
echo "   ИЛИ отправьте боту команду: /set_webhook $TUNNEL_URL"
