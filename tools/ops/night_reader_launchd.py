#!/usr/bin/env python3
"""
Launchd-обёртка ночного читателя.

Зачем: launchd-запущенный /bin/bash не имеет доступа к iCloud-контейнеру Obsidian
(«01. Входящие») из-за TCC (Operation not permitted). Обёртка делает TCC-ключом
процесса python3 (homebrew) — ему достаточно один раз выдать Full Disk Access:
Системные настройки → Конфиденциальность и безопасность → Полный доступ к диску
→ «+» → Cmd+Shift+G → /opt/homebrew/bin/python3 → Открыть.

Запуск: launchd com.antigravity.nightreader → 02:30 (см. plist).
"""

import subprocess
import sys

NIGHT_READER = "/Users/igorvasin/freelance-2026/tools/ops/night_reader.sh"

if __name__ == "__main__":
    rc = subprocess.run(["/bin/bash", NIGHT_READER, *sys.argv[1:]], check=False)
    sys.exit(rc.returncode)
