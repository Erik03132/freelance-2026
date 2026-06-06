#!/usr/bin/env bash
# ============================================================================
# save_session_state.sh — Сохраняет состояние сессии OpenCode
# ============================================================================
# Использование:
#   bash tools/save_session_state.sh <project-name>
#
# Что делает:
#   1. Обновляет SESSION_LATEST.md в проекте (git log + CHRONICLE.md)
#   2. Дописывает блок в chp.md (секция 🟦 OpenCode Session)
#
# Вызывается агентом в конце сессии (или вручную).
# На старте агент читает: chp.md → SESSION_LATEST.md → CHRONICLE.md
# ============================================================================

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$HOME/freelance-2026"
DATE_SHORT=$(date +%Y-%m-%d)
TIME_NOW=$(date '+%H:%M')

# Определяем проект
if [[ -n "$1" ]]; then
  PROJECT="$1"
else
  CWD=$(pwd)
  if [[ "$CWD" == "$WORKSPACE"* ]]; then
    PROJECT="$(basename "$CWD")"
  fi
fi

if [[ -z "$PROJECT" ]]; then
  echo "Usage: $0 <project-name>"
  echo "       $0  (запуск из проекта)"
  exit 1
fi

PROJECT_DIR="$WORKSPACE/$PROJECT"
CHRONICLE="$PROJECT_DIR/CHRONICLE.md"
SESSION_FILE="$PROJECT_DIR/SESSION_LATEST.md"
CHP_FILE="$WORKSPACE/chp.md"

if [[ ! -f "$CHRONICLE" ]]; then
  echo "❌ CHRONICLE.md не найден в $PROJECT_DIR"
  exit 1
fi

# ─── Обновляем SESSION_LATEST.md ──────────────────────────────────────

LAST_COMMIT=$(cd "$PROJECT_DIR" && git log --oneline -1 2>/dev/null || echo "N/A")

IN_PROGRESS=$(sed -n '/^### In Progress/,/^### /p' "$CHRONICLE" | grep '^-' | sed 's/^- /1. /' || echo "—")
NEXT_STEPS=$(sed -n '/^## Next Steps/,/^## /p' "$CHRONICLE" | grep '^[0-9]' || echo "—")
DONE=$(sed -n '/^### Done/,/^### /p' "$CHRONICLE" | grep '^-' | sed 's/^- /* /' || echo "—")

cat > "$SESSION_FILE" << EOF
# SESSION_LATEST — ${DATE_SHORT}

## Project
${PROJECT}

## Last Commit
\`${LAST_COMMIT}\`

## In Progress
${IN_PROGRESS}

## Next Steps
${NEXT_STEPS}

## Last Session Summary
${DONE}

## Generated
${DATE_SHORT} ${TIME_NOW} by \`save_session_state.sh\`
EOF

echo "✅ SESSION_LATEST.md сохранён: $SESSION_FILE"

# ─── Дописываем блок в chp.md ─────────────────────────────────────────

CHP_BLOCK=$(cat << EOF

---

## 🟦 OpenCode Session: ${PROJECT} (${DATE_SHORT} ${TIME_NOW})

Последний коммит: \`${LAST_COMMIT}\`

### Что сделано
${DONE}

### Следующие шаги
${NEXT_STEPS}

---

EOF
)

if [[ -f "$CHP_FILE" ]]; then
  echo "$CHP_BLOCK" >> "$CHP_FILE"
  echo "✅ chp.md дописан с блоком [${PROJECT}]"
else
  # Если chp.md нет — создаём
  cat > "$CHP_FILE" << EOF
# 🏁 ЧЕКПОИНТ: ${DATE_SHORT} ${TIME_NOW} MSK
${CHP_BLOCK}
EOF
  echo "✅ chp.md создан с блоком [${PROJECT}]"
fi
