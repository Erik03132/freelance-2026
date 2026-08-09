#!/bin/bash
# nas_mount.sh — автомонтирование NAS (Synology 192.168.0.102, шара home)
# Пароль берётся из Keychain (nas-smb), не хранится в файлах.
set -u
MOUNT_POINT="$HOME/nas_home"
SHARE="//erik03132@192.168.0.102/home"

if mount | grep -q "$MOUNT_POINT"; then
    exit 0
fi

PASS=$(security find-generic-password -s "nas-smb" -a erik03132 -w 2>/dev/null)
if [ -z "$PASS" ]; then
    echo "NAS: пароль не найден в Keychain" >> /tmp/nas_mount.log
    exit 1
fi

mkdir -p "$MOUNT_POINT"
mount_smbfs "//erik03132:${PASS}@192.168.0.102/home" "$MOUNT_POINT" 2>> /tmp/nas_mount.log
if mount | grep -q "$MOUNT_POINT"; then
    echo "$(date '+%F %T') NAS смонтирован" >> /tmp/nas_mount.log
else
    echo "$(date '+%F %T') NAS: ошибка монтирования" >> /tmp/nas_mount.log
fi
