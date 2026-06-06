#!/usr/bin/env bash
# ============================================================================
# start_day.sh — Старт рабочей сессии OpenCode
# ============================================================================
# Вызывается агентом по команде пользователя "start-day"
#
# ЧТО ДЕЛАЕТ:
#   1. Проверяет, в каком проекте мы находимся
#   2. Выводит сводку: последний коммит, активные задачи
#   3. Указывает, какие файлы прочитать для полного контекста
#
# ИСПОЛЬЗОВАНИЕ (вызывается агентом):
#   bash tools/start_day.sh
# ============================================================================

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$HOME/freelance-2026"
DATE_SHORT=$(date +%Y-%m-%d)

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

# Определяем текущий проект
CWD=$(pwd)
PROJECT=""
if [[ "$CWD" == "$WORKSPACE"* ]]; then
  PROJECT=$(echo "$CWD" | sed "s|$WORKSPACE/||" | cut -d/ -f1)
fi

echo ""
echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${CYAN}  🌅 OPENCODE START-DAY — ${DATE_SHORT}${NC}"
echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [[ -n "$PROJECT" ]]; then
  PROJECT_DIR="$WORKSPACE/$PROJECT"
  LAST_COMMIT=$(cd "$PROJECT_DIR" && git log --oneline -1 2>/dev/null || echo "N/A")
  LAST_TAG=$(cd "$PROJECT_DIR" && git describe --tags --abbrev=0 2>/dev/null || echo "")

  echo -e "  ${BOLD}📁 Проект:${NC} $PROJECT"
  echo -e "  ${BOLD}🔗 Коммит:${NC} $LAST_COMMIT"
  [[ -n "$LAST_TAG" ]] && echo -e "  ${BOLD}🏷️  Тег:${NC} $LAST_TAG"
  echo ""

  if [[ -f "$PROJECT_DIR/SESSION_LATEST.md" ]]; then
    echo -e "  ${BOLD}📋 Последнее состояние:${NC}"
    sed -n '3,10p' "$PROJECT_DIR/SESSION_LATEST.md" | sed 's/^##/ •/'
    echo ""
  fi
else
  echo -e "  ${YELLOW}⚠️  Проект не определён (CWD вне монорепозитория)${NC}"
  echo ""
fi

if [[ -f "$WORKSPACE/chp.md" ]]; then
  echo -e "  ${BOLD}📌 Чекпоинт (chp.md):${NC}"
  head -5 "$WORKSPACE/chp.md"
  echo ""
fi

echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  ${BOLD}👉 Для полного контекста прочитай:${NC}"
echo -e "     ${CYAN}📄 chp.md${NC} — глобальный чекпоинт"
echo -e "     ${CYAN}📄 ${PROJECT:-<project>}/SESSION_LATEST.md${NC} — состояние проекта"
echo -e "     ${CYAN}📄 ${PROJECT:-<project>}/CHRONICLE.md${NC} — хроника проекта"
echo ""
echo -e "  ${BOLD}💬 Команды:${NC}"
echo -e "     start-day  — начать сессию"
echo -e "     finish-day — завершить сессию (коммит + сохранить состояние)"
echo ""
echo -e "  ${BOLD}${YELLOW}👉 Продолжим с того места, где остановились?${NC}"
echo ""
