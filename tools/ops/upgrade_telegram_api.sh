#!/bin/bash
# Апгрейд Telegram Bot API: aiogram 3.13 -> 3.31, python-telegram-bot 20 -> 21

set -e

echo "=== Тестирование в ai-eggs ==="
PROJECT="projects/ai-eggs"

echo "1. Бэкап requirements.txt"
cp "$PROJECT/requirements.txt" "$PROJECT/requirements.txt.upgrade.bak"

echo "2. Подмена версий"
sed -i.bak 's/aiogram==3.13.1/aiogram==3.31.0/' "$PROJECT/requirements.txt"

echo "3. Установка (dry-run)"
cd "$PROJECT"
pip install -r requirements.txt --dry-run || echo "⚠️ dry-run не прошёл, смотри ошибки выше"

echo "✅ Бэкап: requirements.txt.upgrade.bak"
echo "ℹ️  Для применения: pip install -r requirements.txt"
