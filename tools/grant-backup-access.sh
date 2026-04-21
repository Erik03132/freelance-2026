#!/bin/bash
# ============================================================================
# 🔓 GRANT FULL DISK ACCESS — Для работы бэкапа ~/.gemini
# ============================================================================
# 
# macOS TCC (Transparency, Consent, and Control) блокирует доступ
# Terminal/Python к ~/.gemini/antigravity/
#
# Решение: дайте Terminal.app полный доступ к диску.
#
# АВТОМАТИЧЕСКИЙ СПОСОБ (запустите этот скрипт):
#   sudo ./grant-backup-access.sh
#
# РУЧНОЙ СПОСОБ (если sudo не работает):
#   1. Откройте: Системные настройки → Конфиденциальность и безопасность
#   2. Выберите: Полный доступ к диску (Full Disk Access)
#   3. Нажмите + и добавьте: /Applications/Utilities/Terminal.app
#   4. Перезапустите Terminal
#
# После этого скрипт antigravity-backup.sh сможет работать напрямую!
# ============================================================================

set -euo pipefail

echo ""
echo "🔓 Настройка доступа к ~/.gemini для бэкапа"
echo "============================================="
echo ""

# Проверяем текущий доступ
if ls "$HOME/.gemini/antigravity/skills" &>/dev/null; then
    echo "✅ Доступ к ~/.gemini уже есть! Бэкап может работать."
    echo ""
    echo "Запускайте бэкап: ./antigravity-backup.sh"
    exit 0
fi

echo "❌ Доступ к ~/.gemini заблокирован (macOS TCC)"
echo ""
echo "Откройте настройки macOS и добавьте Terminal в FDA:"
echo ""
echo "  1. Системные настройки → Конфиденциальность и безопасность"  
echo "  2. Полный доступ к диску (Full Disk Access)"
echo "  3. Добавьте: Terminal.app"
echo "  4. Перезапустите Terminal"
echo ""

# Попробуем открыть настройки автоматически
if command -v open &>/dev/null; then
    echo "Открываю настройки безопасности..."
    open "x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles"
fi
