#!/bin/bash
# ============================================================
# 🔄 sync_inbox.sh — мост VPS→Mac: тянет /opt/vault_inbox → vault/00-Inbox
# ============================================================
# Запуск: launchd com.antigravity.inbox-sync (каждые 30 мин)
# Вручную: bash tools/sync_inbox.sh
# ============================================================

set -eu

PROJECT_ROOT="/Users/igorvasin/freelance-2026"
INBOX_DIR="${PROJECT_ROOT}/vault/00-Inbox"
ENV_FILE="${PROJECT_ROOT}/projects/ai-eggs/.env"
LOG_FILE="/tmp/inbox_sync.log"

mkdir -p "$INBOX_DIR"

VPS_HOST=$(grep "^VPS_HOST=" "$ENV_FILE" 2>/dev/null | cut -d= -f2)
VPS_USER=$(grep "^VPS_USER=" "$ENV_FILE" 2>/dev/null | cut -d= -f2)
VPS_KEY=$(grep "^VPS_SSH_KEY=" "$ENV_FILE" 2>/dev/null | cut -d= -f2)
[ -z "$VPS_HOST" ] && VPS_HOST="217.149.23.113"
[ -z "$VPS_USER" ] && VPS_USER="root"
[ -z "$VPS_KEY" ] && VPS_KEY="$PROJECT_ROOT/.ssh_agent_key"

# SSH-туннель (соседняя сессия): ssh -p 22001 root@127.0.0.1
TUNNEL_HOST="127.0.0.1"
TUNNEL_PORT="22001"

log() { echo "[$(date '+%H:%M:%S')] $1" >> "$LOG_FILE"; }

if [ ! -f "$VPS_KEY" ]; then
    log "⚠️ SSH ключ не найден: $VPS_KEY"
    exit 1
fi

SSH_CMD="ssh -i '${VPS_KEY}' -o StrictHostKeyChecking=no -o ConnectTimeout=10"

# Попытка 1: через туннель
log "🔄 sync: root@${TUNNEL_HOST}:${TUNNEL_PORT}:/opt/vault_inbox → ${INBOX_DIR}"
if rsync -az --timeout=20 --exclude="*.lock" \
    -e "${SSH_CMD} -p ${TUNNEL_PORT}" \
    "root@${TUNNEL_HOST}:/opt/vault_inbox/" "$INBOX_DIR/" 2>>"$LOG_FILE"; then
    SYNCED=1
# Попытка 2: прямой хост
elif rsync -az --timeout=20 --exclude="*.lock" \
    -e "${SSH_CMD}" \
    "${VPS_USER}@${VPS_HOST}:/opt/vault_inbox/" "$INBOX_DIR/" 2>>"$LOG_FILE"; then
    SYNCED=1
    log "  (через прямой хост ${VPS_HOST})"
else
    SYNCED=0
    log "❌ Sync FAILED (туннель и прямой хост недоступны)"
    exit 1
fi

if [ "$SYNCED" = 1 ]; then
    COUNT=$(find "$INBOX_DIR" -maxdepth 1 -type f -mmin -1 2>/dev/null | wc -l | tr -d ' ')
    if [ "$COUNT" -gt 0 ]; then
        log "✅ Sync OK, новых файлов: ${COUNT}"
    else
        log "✅ Sync OK (новых нет)"
    fi
fi
