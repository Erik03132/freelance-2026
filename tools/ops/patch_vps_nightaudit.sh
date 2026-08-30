#!/usr/bin/env bash
# PATCH for VPS (run in Console panel as root). Fixes:
# 1. Night audit: replace PAYING Grok 4.5 with a FREE OpenRouter model
#    (z-ai/glm-5.2:free; на аккаунте лежат деньги — Грок не тратим).
# 2. Disable SSH password auth (keep key only) — stops bruteforce
# 3. (Info) list gateway systemd units
set -e

FREE_MODEL="z-ai/glm-5.2:free"

echo "=== [1] Night audit: replace Grok 4.5 (paid) with free model ==="
AUDIT_FILES=$(grep -rl -iE 'grok' /opt/levitan/projects/ai-eggs/ 2>/dev/null | grep -E '\.(py|sh|yaml|json)$' || true)
echo "Found files referencing grok:"
echo "$AUDIT_FILES"

for f in $AUDIT_FILES; do
  echo "--- patching $f ---"
  # 1a. Точная замена id модели OpenRouter (самое важное)
  sed -i -E "s#x-ai/grok-4\.5#${FREE_MODEL}#gi" "$f"
  # 1b. Очистка человекочитаемых упоминаний Grok в echo/комментариях
  sed -i -E 's/Grok 4\.5/FREE LLM (glm-5.2:free)/gi' "$f"
  sed -i -E 's/\bGrok\b/FREE LLM/gi' "$f"
done
echo "Grok replaced with $FREE_MODEL in: $AUDIT_FILES"

echo ""
echo "=== [2] Disable SSH password auth ==="
# ⚠️ ПЕРЕД ЭТИМ убедись, что /root/.ssh/authorized_keys на месте (см. CONSOLE_COMMANDS.md)
sed -i 's/^#*PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
grep -i PasswordAuthentication /etc/ssh/sshd_config | grep -v '^#'
systemctl restart ssh || service ssh restart
echo "SSH restarted, password auth disabled (key only)."

echo ""
echo "=== [3] Gateway systemd units ==="
systemctl list-units --type=service | grep -iE 'hermes|gateway|batrak|bridge|personal|angela|levitan' || echo "no hermes-gateway units found"

echo ""
echo "DONE. Night audit now uses $FREE_MODEL (free). SSH key-only."
