#!/bin/bash
# nas_backup.sh — ночной бэкап vault + freelance-2026 на NAS
set -u
MOUNT_POINT="$HOME/nas_home"
[ -d "$MOUNT_POINT/Backup" ] || exit 1

echo "=== $(date '+%F %T') NAS backup start ===" >> /tmp/nas_backup.log

rsync -a --delete --exclude='node_modules' --exclude='.venv' --exclude='.git' \
    "$HOME/freelance-2026/vault/" "$MOUNT_POINT/Backup/vault/" 2>> /tmp/nas_backup.log

rsync -a --delete --exclude='node_modules' --exclude='.venv' --exclude='.git' \
    --exclude='checkpoints' --exclude='reports' \
    "$HOME/freelance-2026/" "$MOUNT_POINT/Backup/freelance-2026/" 2>> /tmp/nas_backup.log

echo "=== $(date '+%F %T') NAS backup done ===" >> /tmp/nas_backup.log
