#!/bin/bash
# Deploy Levitan Анжелла (FAQ-агент) на VPS
# Usage: bash deploy/deploy_angel.sh
# Требует: sshpass, доступ к VPS (IP/пароль в .env LEVITAN_VPS_*)

set -e
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
source "$PROJECT_DIR/.env" 2>/dev/null || true

VPS_HOST="${LEVITAN_VPS_HOST:-72.56.38.19}"
VPS_USER="${LEVITAN_VPS_USER:-root}"
VPS_PASS="${LEVITAN_VPS_PASS:-zE4qDJb-+Y+rv+}"

echo "🚀 Deploying Анжелла (FAQ-агент) → $VPS_HOST"

# 1. Синхронизация кода
echo "📤 Rsync deploy/ + docs/ + .env"
sshpass -p "$VPS_PASS" rsync -avz --delete \
    -e "ssh -o StrictHostKeyChecking=no" \
    --exclude '__pycache__' --exclude '*.pyc' \
    "$PROJECT_DIR/deploy/" "$VPS_USER@$VPS_HOST:/opt/levitan/deploy/" 
sshpass -p "$VPS_PASS" rsync -avz \
    -e "ssh -o StrictHostKeyChecking=no" \
    "$PROJECT_DIR/docs/ANGELLA_BROILERS_FAQ_CACHE.json" "$VPS_USER@$VPS_HOST:/opt/levitan/docs/"
sshpass -p "$VPS_PASS" rsync -avz \
    -e "ssh -o StrictHostKeyChecking=no" \
    "$PROJECT_DIR/.env" "$VPS_USER@$VPS_HOST:/opt/levitan/.env"

# 2. Установка на VPS
sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_HOST} << 'ENDSSH'
set -e
echo "📦 Installing deps..."
python3 -m venv /opt/levitan/.venv || true
source /opt/levitan/.venv/bin/activate
pip install -q --upgrade pip
pip install -q -r /opt/levitan/deploy/../requirements.txt 2>/dev/null || \
  pip install -q requests edge-tts faster-whisper python-dotenv yandex-speechkit ffmpeg-python 2>/dev/null || true

# baresip
which baresip || (apt-get update -y && apt-get install -y baresip ffmpeg 2>/dev/null) || true

# 3. Конфиг baresip (aufile: /tmp/levitan_play.wav)
mkdir -p /root/.baresip
cat > /root/.baresip/config 2>/dev/null << 'BACONF'
# Levitan baresip config
audio_path         /tmp
# aufile модуль проигрывает WAV при входящем/исходящем
module            aufile.so
aufile_play_file   /tmp/levitan_play.wav
BACONF

# 4. systemd units
cat > /etc/systemd/system/levitan-webhook.service << 'U1'
[Unit]
Description=Levitan Webhook (Mango events)
After=network.target
[Service]
WorkingDirectory=/opt/levitan/deploy
ExecStartPre=/bin/bash -c 'source /opt/levitan/.venv/bin/activate && python3 /opt/levitan/deploy/levitan_greeting.py'
ExecStart=/opt/levitan/.venv/bin/python3 /opt/levitan/deploy/levitan_webhook.py
Restart=always
User=root
[Install]
WantedBy=multi-user.target
U1

cat > /etc/systemd/system/levitan-angel.service << 'U2'
[Unit]
Description=Levitan Анжелла (FAQ-агент)
After=network.target levitan-webhook.service
[Service]
WorkingDirectory=/opt/levitan/deploy
ExecStart=/opt/levitan/.venv/bin/python3 /opt/levitan/deploy/levitan_faq_agent.py
Restart=always
User=root
[Install]
WantedBy=multi-user.target
U2

systemctl daemon-reload
systemctl enable levitan-webhook levitan-angel
systemctl restart levitan-webhook
systemctl restart levitan-angel
sleep 2
systemctl status levitan-webhook --no-pager | head -5
systemctl status levitan-angel --no-pager | head -5
echo "✅ Deploy done. Logs: journalctl -u levitan-angel -f"
ENDSSH
