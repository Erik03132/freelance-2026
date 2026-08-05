#!/usr/bin/env bash
# OmniRoute VPS Recovery Script
# Секреты НЕ хранятся в репо — подтягиваются из tools/omni-auto-router/.env (gitignored).
#
# Локальная подготовка (один раз):
#   cp tools/omni-auto-router/.env.example tools/omni-auto-router/.env
#   # вписать реальные JWT_SECRET / API_KEY_SECRET / INITIAL_PASSWORD / прокси
#
# Запуск с VPS:
#   scp tools/omni-auto-router/.env root@217.149.23.113:/root/.omniroute/.env.secrets
#   ssh root@217.149.23.113 'OMNIR_SECRETS=/root/.omniroute/.env.secrets bash -s' < omniroute-recover.sh
# Альтернатива: OMNIR_SECRETS=<путь> bash omniroute-recover.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || echo '.')"
SECRETS_FILE="${OMNIR_SECRETS:-${SCRIPT_DIR}/.env}"
if [ -f "$SECRETS_FILE" ]; then
    set -a
    . "$SECRETS_FILE"
    set +a
fi

OMNIR_DIR="${OMNIR_DIR:-$HOME/.omniroute}"
OPENROUTER_KEY="${OPENROUTER_KEY:-}"

: "${JWT_SECRET:?JWT_SECRET не задан (см. $SECRETS_FILE или .env.example)}"
: "${API_KEY_SECRET:?API_KEY_SECRET не задан (см. $SECRETS_FILE или .env.example)}"
: "${INITIAL_PASSWORD:?INITIAL_PASSWORD не задан (см. $SECRETS_FILE или .env.example)}"

echo "=== OmniRoute VPS Recovery ==="

# 1. Install/update Node.js
if ! command -v node &>/dev/null; then
    echo "Installing Node.js 22 LTS..."
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
    apt-get install -y nodejs
fi
echo "Node: $(node -v)"

# 2. Install OmniRoute
if ! command -v npx &>/dev/null || ! npx omniroute --version &>/dev/null; then
    echo "Installing OmniRoute..."
    npm install -g omniroute
fi
echo "OmniRoute: $(npx omniroute --version 2>/dev/null || echo 'installed')"

# 3. Create .env
mkdir -p "$OMNIR_DIR"
cat > "$OMNIR_DIR/.env" << ENV
JWT_SECRET=${JWT_SECRET}
API_KEY_SECRET=${API_KEY_SECRET}
INITIAL_PASSWORD=${INITIAL_PASSWORD}
PORT=20128
NODE_ENV=production
ENABLE_SOCKS5_PROXY=false
ENABLE_TLS_FINGERPRINT=true
OMNIROUTE_MEMORY_MB=384
APP_LOG_LEVEL=info
APP_LOG_TO_FILE=true
CALL_LOG_RETENTION_DAYS=3
REQUIRE_API_KEY=false
HTTP_PROXY=${HTTP_PROXY}
HTTPS_PROXY=${HTTPS_PROXY}
NO_PROXY=localhost,127.0.0.1,::1
ENV

# Append OpenRouter key
echo "" >> "$OMNIR_DIR/.env"
echo "# OpenRouter API key" >> "$OMNIR_DIR/.env"
echo "OPENROUTER_API_KEY=${OPENROUTER_KEY:-YOUR_OPENROUTER_KEY_HERE}" >> "$OMNIR_DIR/.env"

echo ".env created at $OMNIR_DIR/.env"

# 4. Start via PM2
if ! command -v pm2 &>/dev/null; then
    echo "Installing PM2..."
    npm install -g pm2
fi

pm2 delete omniroute 2>/dev/null || true

# Create start script with proxy env vars
cat > /root/start-omniroute.sh << STARTEOF
#!/bin/bash
export HTTP_PROXY=${HTTP_PROXY}
export HTTPS_PROXY=${HTTPS_PROXY}
export NO_PROXY=localhost,127.0.0.1,::1,217.149.23.113
export OPENROUTER_API_KEY=${OPENROUTER_KEY:-YOUR_OPENROUTER_KEY_HERE}
sqlite3 /root/.omniroute/storage.sqlite "UPDATE provider_connections SET test_status='unknown',error_code=NULL,last_error=NULL,last_error_at=NULL,last_error_type=NULL,last_error_source=NULL,backoff_level=0,rate_limited_until=NULL,consecutive_use_count=0,updated_at=datetime('now') WHERE 1=1;"
exec /usr/bin/omniroute
STARTEOF
chmod +x /root/start-omniroute.sh

pm2 start /root/start-omniroute.sh --name omniroute
pm2 save
pm2 startup systemd -u root --hp /root 2>/dev/null || true

# 5. Healthcheck cron (every 5 min)
cat > /root/healthcheck-omniroute.sh << 'HCEOF'
#!/bin/bash
HEALTH=$(curl -sf -o /dev/null -w "%{http_code}" http://127.0.0.1:20128/v1/models 2>/dev/null)
if [ "$HEALTH" != "200" ]; then
    echo "[$(date)] OmniRoute down (HTTP $HEALTH). Restarting..."
    pm2 restart omniroute 2>/dev/null
    sleep 3
    HEALTH2=$(curl -sf -o /dev/null -w "%{http_code}" http://127.0.0.1:20128/v1/models 2>/dev/null)
    if [ "$HEALTH2" != "200" ]; then
        echo "[$(date)] Still down. Hard reset..."
        pm2 stop omniroute 2>/dev/null
        sleep 1
        pm2 start /root/start-omniroute.sh --name omniroute 2>/dev/null
    fi
fi
HCEOF
chmod +x /root/healthcheck-omniroute.sh
(crontab -l 2>/dev/null | grep -v healthcheck-omniroute; echo "*/5 * * * * /root/healthcheck-omniroute.sh >> /root/.pm2/logs/healthcheck.log 2>&1") | crontab -

echo ""
echo "=== Recovery complete ==="
echo "OmniRoute should be running on port 20128"
echo "Check: curl http://localhost:20128/v1/models"
echo "Create API key via dashboard: http://217.149.23.113:20128"
echo "Password: ${INITIAL_PASSWORD}"
echo "Then add OpenRouter provider and configure combo 'free-cascade'"
echo ""
echo "Healthcheck cron installed (every 5 min)"
