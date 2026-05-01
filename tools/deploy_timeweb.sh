#!/usr/bin/env bash
# Deploy AI‑EGGS agent to Timeweb VDS
# Adjust the following variables to your environment
TIMEWEB_USER="erik03132"
TIMEWEB_HOST="your-timeweb-host.com"
REMOTE_DIR="/home/${TIMEWEB_USER}/ai-eggs"
LOCAL_DIR="$(pwd)"
SSH_OPTIONS="-o StrictHostKeyChecking=no"

# 1. Sync code to remote server (rsync)
rsync -avz --exclude='.git/' --exclude='__pycache__/' \
    -e "ssh ${SSH_OPTIONS}" \
    "${LOCAL_DIR}/" "${TIMEWEB_USER}@${TIMEWEB_HOST}:${REMOTE_DIR}/"

# 2. Remote setup – install dependencies, create venv, configure services
ssh ${SSH_OPTIONS} ${TIMEWEB_USER}@${TIMEWEB_HOST} <<'EOF'
  set -e
  cd "${REMOTE_DIR}"

  # create virtual environment if not exists
  if [ ! -d "venv" ]; then
    echo "Creating virtualenv..."
    python3 -m venv venv
  fi
  source venv/bin/activate

  # upgrade pip and install requirements
  pip install --upgrade pip
  if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
  else
    echo "No requirements.txt found – skipping pip install"
  fi

  # ensure .env exists – copy from local backup if needed
  if [ ! -f ".env" ]; then
    echo "WARNING: .env missing on remote. Create it manually with required secrets."
  fi

  # Install pm2 for Node‑based tools (optional) – we use systemd for python
  # sudo npm install -g pm2

  # Deploy systemd service for scheduler
  SERVICE_FILE="/etc/systemd/system/ai-eggs-scheduler.service"
  sudo bash -c "cat > \${SERVICE_FILE}" <<EOL
[Unit]
Description=AI‑EGGS Scheduler (Angelochka)
After=network.target

[Service]
Type=simple
User=${TIMEWEB_USER}
WorkingDirectory=${REMOTE_DIR}/ai-eggs/agent
ExecStart=${REMOTE_DIR}/ai-eggs/agent/venv/bin/python scheduler.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

  sudo systemctl daemon-reload
  sudo systemctl enable ai-eggs-scheduler.service
  sudo systemctl restart ai-eggs-scheduler.service
  echo "Deployment complete – scheduler service is running."
EOF
