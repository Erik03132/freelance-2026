#!/bin/bash
# nas-tm-backup.sh — automated macOS Time Machine backup to a Synology NAS
# Drive via LaunchAgent (com.igor.nas-tm-backup.plist). Daily at 03:00.
# SAFE: tmutil setdestination does NOT erase existing backups; it only attaches the disk.
# Mount the share ONCE via Finder (Go → Connect → smb://ds720.local → share →
# "Remember in keychain") so macOS keeps it mounted. This script does not mount.

LOG=~/nas-tools/tm-backup.log
NAS_HOST="ds720.local"
SHARE="Time Mashine"            # literal share name on the NAS (typo is real)
USER="erik03132"
MOUNT_POINT="/Volumes/Time Mashine"   # Finder mounts SMB shares under /Volumes/<share>

echo "=== [$(date)] start TM backup to NAS ===" >> "$LOG"

if ! ping -c 1 -W 2000 "$NAS_HOST" >/dev/null 2>&1; then
    echo "[$(date)] NAS $NAS_HOST unreachable — skip" >> "$LOG"
    exit 0
fi
echo "[$(date)] NAS reachable" >> "$LOG"

if ! mount | grep -q "$MOUNT_POINT"; then
    echo "[$(date)] Share NOT mounted. Mount once in Finder: Go → Connect → smb://ds720.local → $SHARE" >> "$LOG"
    exit 1
fi
echo "[$(date)] share mounted: $MOUNT_POINT" >> "$LOG"

if ! tmutil currentdestination 2>/dev/null | grep -q "$MOUNT_POINT"; then
    tmutil setdestination "$MOUNT_POINT" >> "$LOG" 2>&1
    echo "[$(date)] destination attached" >> "$LOG"
fi

tmutil startbackup --block 2>>"$LOG"
echo "[$(date)] backup finished (exit=$?)" >> "$LOG"
