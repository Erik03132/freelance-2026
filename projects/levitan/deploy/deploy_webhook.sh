#!/bin/bash
# Deploy Levitan Webhook (FastAPI) to VPS
# Usage: bash deploy/deploy_webhook.sh

VPS_HOST="72.56.38.19"
VPS_USER="root"
VPS_PASS="zE4qDJb-+Y+rv+"

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "🚀 Deploying Levitan Webhook (FastAPI) to $VPS_HOST..."

# 1. Upload webhook script
echo "📤 Uploading webhook_server.py..."
sshpass -p "$VPS_PASS" scp -o StrictHostKeyChecking=no \
    "$PROJECT_DIR/scripts/webhook_server.py" \
    ${VPS_USER}@${VPS_HOST}:/opt/levitan_webhook.py

# 2. Upload contacts CSV for lead matching
echo "📤 Uploading contacts CSV..."
sshpass -p "$VPS_PASS" scp -o StrictHostKeyChecking=no \
    "$PROJECT_DIR/data/campaigns/csv/all_contacts_2026.csv" \
    ${VPS_USER}@${VPS_HOST}:/opt/all_contacts_2026.csv

# 3. Setup environment and start
sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_HOST} << 'ENDSSH'
echo "📝 Setting up environment..."

# Create env file
cat > /opt/.env.levitan << 'EOF'
MANGO_VPBX_API_KEY=k0ockrwsafuf7tfpuk7fkqtps4nl77o8
MANGO_VPBX_API_SALT=9g1go1lj1zxkyc0v9j9c7fsyy12erqcw
TELEGRAM_BOT_TOKEN=8776258870:AAEvEAQNRL4N8sLmn0eUnARQ8-6BOl6rEM8
TELEGRAM_CHAT_ID=176203333
LEVITAN_WEBHOOK_PORT=8087
EOF

# Install deps
pip3 install fastapi uvicorn requests 2>/dev/null || true

# Create dirs
mkdir -p /var/log/levitan /opt/data/call_results /opt/data/webhook_logs

# Symlink contacts
ln -sf /opt/all_contacts_2026.csv /opt/data/all_contacts_2026.csv 2>/dev/null || true

# Stop existing
if pm2 list 2>/dev/null | grep -q "levitan-webhook"; then
    pm2 stop levitan-webhook
    pm2 delete levitan-webhook
fi

# Start with PM2
echo "🚀 Starting levitan-webhook..."
pm2 start /opt/levitan_webhook.py \
    --name levitan-webhook \
    --interpreter python3 \
    --env-file /opt/.env.levitan

pm2 save

echo ""
echo "✅ Webhook deployed!"
echo "   URL: http://$VPS_HOST:8087"
echo "   Health: http://$VPS_HOST:8087/health"
echo "   Events: http://$VPS_HOST:8087/mango-webhook"
echo ""
echo "📋 Настройка в Mango Office:"
echo "   1. Личный кабинет → Настройки → Уведомления → HTTP"
echo "   2. URL: http://$VPS_HOST:8087/mango-webhook"
echo "   3. Выбрать событие: Речевая аналитика / Конспект (Summary)"
echo "   4. Сохранить"
ENDSSH

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment complete!"
else
    echo ""
    echo "❌ Deployment failed - VPS unreachable"
    echo "   Retry when VPS is back: bash deploy/deploy_webhook.sh"
fi
