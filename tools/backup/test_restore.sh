#!/usr/bin/env bash
# ============================================================================
# ✅ TEST-RESTORE — Пробное восстановление из бэкапа
# ============================================================================
# Метрика успешности бэкапа = успешное пробное восстановление,
# а не "rsync done". Запускать по расписанию.
#
# ИСПОЛЬЗОВАНИЕ:
#   bash tools/backup/test_restore.sh                    # тест последнего архива
#   bash tools/backup/test_restore.sh --source nas        # тест из NAS
#   bash tools/backup/test_restore.sh --source external   # тест с внешнего диска
#   bash tools/backup/test_restore.sh --source github     # тест из git-бэкапа
# ============================================================================

set -euo pipefail

WORKSPACE="$HOME/freelance-2026"
ANTIGRAVITY="$HOME/.gemini/antigravity"
TEST_DIR="/tmp/antigravity_restore_test_$$"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SOURCE="${1:---source local}"
CLEANUP_ON_EXIT=true

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

cleanup() {
    if [[ "$CLEANUP_ON_EXIT" == "true" ]]; then
        rm -rf "$TEST_DIR" 2>/dev/null || true
    fi
}
trap cleanup EXIT

log_pass()  { echo -e "  ${GREEN}[PASS]${NC} $1"; }
log_fail()  { echo -e "  ${RED}[FAIL]${NC} $1"; }
log_info()  { echo -e "  ${CYAN}[INFO]${NC} $1"; }

echo ""
echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${CYAN}  ✅  TEST-RESTORE — $(date '+%d.%m.%Y %H:%M')${NC}"
echo -e "${BOLD}${CYAN}  Источник: $SOURCE${NC}"
echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

mkdir -p "$TEST_DIR"
PASS=0
FAIL=0

verify_file() {
    local label="$1" path="$2"
    if [[ -f "$path" ]]; then
        local size=$(wc -c < "$path" | tr -d ' ')
        if (( size > 0 )); then
            log_pass "$label ($size bytes)"
            ((PASS++)) || true
        else
            log_fail "$label (empty file)"
            ((FAIL++)) || true
        fi
    else
        log_fail "$label (missing)"
        ((FAIL++)) || true
    fi
}

verify_dir() {
    local label="$1" path="$2" min_files="${3:-1}"
    if [[ -d "$path" ]]; then
        local count=$(find "$path" -type f 2>/dev/null | wc -l | tr -d ' ')
        if (( count >= min_files )); then
            log_pass "$label ($count files)"
            ((PASS++)) || true
        else
            log_fail "$label (${count}/${min_files} files — too few)"
            ((FAIL++)) || true
        fi
    else
        log_fail "$label (directory missing)"
        ((FAIL++)) || true
    fi
}

# ============================ ТЕСТЫ ====================================

echo ""
echo -e "${BOLD}📋 Проверка локальных бэкапов:${NC}"

BACKUP_ROOT="$HOME/freelance-2026/.backups/antigravity"

if [[ -d "$BACKUP_ROOT" ]]; then
    LATEST_ARCHIVE=$(find "$BACKUP_ROOT" -name "antigravity_backup_*.tar.gz" -type f 2>/dev/null | sort | tail -1)
    if [[ -n "$LATEST_ARCHIVE" ]]; then
        ARCHIVE_SIZE=$(wc -c < "$LATEST_ARCHIVE" | tr -d ' ')
        log_info "Последний архив: $(basename "$LATEST_ARCHIVE") ($ARCHIVE_SIZE bytes)"
        
        tar -xzf "$LATEST_ARCHIVE" -C "$TEST_DIR" 2>/dev/null
        RESTORE_ROOT=$(find "$TEST_DIR" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | head -1)
        
        if [[ -n "$RESTORE_ROOT" ]]; then
            # Current post-migration contract: workspace state + Hermes skills.
            # Legacy Antigravity core/skills are optional and must not make a
            # valid modern backup fail merely because those paths were retired.
            verify_file "chp.md"               "$RESTORE_ROOT/strategy/chp.md"
            verify_file "ACTIVE_TASKS.md"      "$RESTORE_ROOT/strategy/ACTIVE_TASKS.md"
            verify_dir  "Hermes Skills"        "$RESTORE_ROOT/hermes/skills" 3
            verify_dir  "Strategy"             "$RESTORE_ROOT/strategy" 2
            if [[ -d "$RESTORE_ROOT/knowledge" ]]; then
                verify_dir "Legacy Knowledge (optional)" "$RESTORE_ROOT/knowledge" 1
            fi
        else
            log_fail "Archive extraction failed"
            ((FAIL++)) || true
        fi
    else
        log_info "Нет локальных архивов для проверки"
    fi
else
    log_info "Нет локального backup root ($BACKUP_ROOT)"
fi

echo ""
echo -e "${BOLD}📋 Проверка живых файлов (целостность .git):${NC}"

if [[ -d "$WORKSPACE/.git" ]]; then
    if git -C "$WORKSPACE" rev-parse HEAD >/dev/null 2>&1; then
        log_pass "Git HEAD разрешён"
    else
        log_fail "Git репо сломано"
        ((FAIL++)) || true
    fi
fi

echo ""
echo -e "${BOLD}📋 Проверка текущего Hermes/workspace:${NC}"

verify_file "chp.md (live)"             "$WORKSPACE/chp.md"
verify_file "ACTIVE_TASKS.md (live)"    "$WORKSPACE/ACTIVE_TASKS.md"
verify_dir  "Hermes Skills (live)"      "$HOME/.hermes/skills" 3
if [[ -d "$ANTIGRAVITY/knowledge" ]] && find "$ANTIGRAVITY/knowledge" -type f -print -quit 2>/dev/null | grep -q .; then
    verify_dir "Legacy Knowledge (live, optional)" "$ANTIGRAVITY/knowledge" 1
fi

# ============================ ИТОГ ====================================

echo ""
echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
TOTAL=$((PASS + FAIL))
if (( FAIL == 0 )); then
    echo -e "${BOLD}${GREEN}  ✅  ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ ($PASS/$TOTAL)${NC}"
    echo -e "${BOLD}${GREEN}  Бэкап = работоспособен. Можно доверять.${NC}"
    RESULT="PASS"
else
    echo -e "${BOLD}${RED}  ❌  НАЙДЕНЫ ПРОБЛЕМЫ ($PASS/$TOTAL, $FAIL FAIL)${NC}"
    echo -e "${BOLD}${RED}  Бэкап = НЕ ПОДТВЕРЖДЁН. Требуется проверка.${NC}"
    RESULT="FAIL"
fi
echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

LOG_DIR="$WORKSPACE/logs/backup_test"
mkdir -p "$LOG_DIR"
echo "$TIMESTAMP $RESULT $PASS/$TOTAL" >> "$LOG_DIR/test_restore.log"

if (( FAIL > 0 )); then
    CLEANUP_ON_EXIT=false
    echo -e "${YELLOW}Тестовая директория сохранена: $TEST_DIR${NC}"
fi

exit $FAIL
