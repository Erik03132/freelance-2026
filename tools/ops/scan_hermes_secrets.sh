#!/usr/bin/env bash
# Scan Hermes skills for accidental secret leakage before sync.
set -uo pipefail
cd ~/.hermes 2>/dev/null || { echo "cannot cd ~/.hermes"; exit 1; }

echo '=== scan user-level skills for secrets ==='
grep -rIE '8820559136:|AAGh[0-9A-Za-z]{20,}|sk-[0-9a-zA-Z]{20,}|TELEGRAM_BOT_TOKEN|api_key:\s*["'\''][A-Za-z0-9_-]{20,}' skills 2>/dev/null | grep -v '/\.git/' | head -20 || true
echo '--- scan done ---'

echo
echo '=== presence checks (Mac side) ==='
ls -1 ~/.hermes/skills/infrastructure/ 2>/dev/null || echo 'NO infrastructure/'
ls -la ~/.hermes/skills/expert-council.md 2>/dev/null || echo 'NO expert-council.md'
ls -1d ~/.hermes/skills/jobhunter 2>/dev/null || echo 'NO jobhunter/'
