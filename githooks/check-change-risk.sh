#!/bin/bash
# RW-3: pre-commit gate «оценка риска изменений» (repowise get_change_risk).
# Опциональный хук: если repowise установлен и инициализирован (.repowise/ есть) —
# прогоняет get_change_risk по staged-файлам и блокирует коммит при high-risk.
# Без repowise — пропускает (не блокирует workflow).

set -euo pipefail

if ! command -v repowise >/dev/null 2>&1; then
    exit 0
fi

if [ ! -d ".repowise" ]; then
    echo "ℹ️  [rw-3] repowise не инициализирован (нет .repowise/) — пропуск"
    exit 0
fi

CHANGED=$(git diff --cached --name-only --diff-filter=ACM | tr '\n' ' ')
if [ -z "$CHANGED" ]; then
    exit 0
fi

echo "🔍 [rw-3] Оценка риска изменений (repowise get_change_risk)..."
RISK=$(repowise get_change_risk "$CHANGED" 2>/dev/null || echo "")

if echo "$RISK" | grep -qiE '"risk"\s*:\s*"high"|high risk|score.*[89][0-9]'; then
    echo "❌ [rw-3] HIGH RISK — изменения требуют ревью:"
    echo "$RISK" | head -20
    echo "   → Запусти /code-review перед коммитом."
    exit 1
fi

echo "✅ [rw-3] риск приемлем"
exit 0
