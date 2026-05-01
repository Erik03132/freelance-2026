#!/bin/bash
# ==============================================================
# CLEANUP NAS DS720 — Удаление мусора, дубликатов и пустых папок
# ==============================================================
# NAS: DS720 (192.168.0.107)
# Шара: "Документы СЕМЬЯ" → /Volumes/Документы СЕМЬЯ
#
# Использование:
#   bash ~/freelance-2026/tools/cleanup_nas.sh          # только отчёт (dry-run)
#   bash ~/freelance-2026/tools/cleanup_nas.sh --clean   # реальное удаление
# ==============================================================

set -euo pipefail

NAS_SHARE="/Volumes/Документы СЕМЬЯ"
MODE="${1:---dry-run}"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${CYAN}  🧹  CLEANUP NAS DS720 — $(date '+%d.%m.%Y %H:%M')${NC}"
echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Проверка монтирования
if [[ ! -d "$NAS_SHARE" ]]; then
    echo -e "${RED}❌ NAS не примонтирован: $NAS_SHARE${NC}"
    echo -e "${YELLOW}   Откройте Finder → DS720 → 'Документы СЕМЬЯ'${NC}"
    exit 1
fi

if [[ "$MODE" == "--dry-run" ]]; then
    echo -e "${YELLOW}  ⚠️  РЕЖИМ: DRY-RUN (только отчёт, ничего не удаляется)${NC}"
    echo -e "${YELLOW}     Для реального удаления: $0 --clean${NC}"
else
    echo -e "${RED}  🔴 РЕЖИМ: CLEAN (файлы будут удалены!)${NC}"
fi
echo ""

TOTAL_FREED=0

# ─────────────────── 1. .DS_Store ────────────────────
echo -e "  ${BOLD}1. Файлы .DS_Store${NC}"
DS_COUNT=$(find "$NAS_SHARE" -name ".DS_Store" -type f 2>/dev/null | wc -l | tr -d ' ')
DS_SIZE=$(find "$NAS_SHARE" -name ".DS_Store" -type f -exec du -ch {} + 2>/dev/null | tail -1 | cut -f1)
echo -e "     Найдено: ${YELLOW}$DS_COUNT${NC} файлов ($DS_SIZE)"
if [[ "$MODE" == "--clean" && "$DS_COUNT" -gt 0 ]]; then
    find "$NAS_SHARE" -name ".DS_Store" -type f -delete 2>/dev/null
    echo -e "     ${GREEN}✅ Удалены${NC}"
fi

# ─────────────────── 2. Thumbs.db (Windows) ────────────────────
echo -e "  ${BOLD}2. Thumbs.db (Windows мусор)${NC}"
THUMBS_COUNT=$(find "$NAS_SHARE" -name "Thumbs.db" -o -name "thumbs.db" -o -name "desktop.ini" 2>/dev/null | wc -l | tr -d ' ')
echo -e "     Найдено: ${YELLOW}$THUMBS_COUNT${NC} файлов"
if [[ "$MODE" == "--clean" && "$THUMBS_COUNT" -gt 0 ]]; then
    find "$NAS_SHARE" \( -name "Thumbs.db" -o -name "thumbs.db" -o -name "desktop.ini" \) -type f -delete 2>/dev/null
    echo -e "     ${GREEN}✅ Удалены${NC}"
fi

# ─────────────────── 3. @eaDir (Synology служебные) ────────────────────
echo -e "  ${BOLD}3. @eaDir (Synology служебные папки)${NC}"
EA_COUNT=$(find "$NAS_SHARE" -name "@eaDir" -type d 2>/dev/null | wc -l | tr -d ' ')
EA_SIZE=$(du -sh $(find "$NAS_SHARE" -name "@eaDir" -type d 2>/dev/null) 2>/dev/null | awk '{total+=$1} END {print total"M"}' 2>/dev/null || echo "?")
echo -e "     Найдено: ${YELLOW}$EA_COUNT${NC} директорий"
if [[ "$MODE" == "--clean" && "$EA_COUNT" -gt 0 ]]; then
    find "$NAS_SHARE" -name "@eaDir" -type d -exec rm -rf {} + 2>/dev/null || true
    echo -e "     ${GREEN}✅ Удалены${NC}"
fi

# ─────────────────── 4. #recycle (Корзина Synology) ────────────────────
echo -e "  ${BOLD}4. #recycle (Корзина Synology)${NC}"
if [[ -d "$NAS_SHARE/#recycle" ]]; then
    RECYCLE_SIZE=$(du -sh "$NAS_SHARE/#recycle" 2>/dev/null | cut -f1)
    RECYCLE_COUNT=$(find "$NAS_SHARE/#recycle" -type f 2>/dev/null | wc -l | tr -d ' ')
    echo -e "     Найдено: ${YELLOW}$RECYCLE_COUNT${NC} файлов ($RECYCLE_SIZE)"
    if [[ "$MODE" == "--clean" ]]; then
        rm -rf "$NAS_SHARE/#recycle"/* 2>/dev/null || true
        echo -e "     ${GREEN}✅ Корзина очищена${NC}"
    fi
else
    echo -e "     ${GREEN}Пусто${NC}"
fi

# ─────────────────── 5. ._* файлы (macOS resource forks) ────────────────────
echo -e "  ${BOLD}5. ._* файлы (macOS resource forks)${NC}"
FORKS_COUNT=$(find "$NAS_SHARE" -name "._*" -type f 2>/dev/null | wc -l | tr -d ' ')
echo -e "     Найдено: ${YELLOW}$FORKS_COUNT${NC} файлов"
if [[ "$MODE" == "--clean" && "$FORKS_COUNT" -gt 0 ]]; then
    find "$NAS_SHARE" -name "._*" -type f -delete 2>/dev/null
    echo -e "     ${GREEN}✅ Удалены${NC}"
fi

# ─────────────────── 6. Пустые папки ────────────────────
echo -e "  ${BOLD}6. Пустые папки${NC}"
EMPTY_COUNT=$(find "$NAS_SHARE" -type d -empty 2>/dev/null | wc -l | tr -d ' ')
echo -e "     Найдено: ${YELLOW}$EMPTY_COUNT${NC} пустых директорий"
if [[ "$MODE" == "--clean" && "$EMPTY_COUNT" -gt 0 ]]; then
    find "$NAS_SHARE" -type d -empty -delete 2>/dev/null || true
    echo -e "     ${GREEN}✅ Удалены${NC}"
fi

# ─────────────────── 7. Дубликаты (по имени в пределах одной папки) ────────────────────
echo -e "  ${BOLD}7. Возможные дубликаты (файлы с суффиксом ' (1)', ' (2)', 'копия')${NC}"
DUPES=$(find "$NAS_SHARE" -type f \( -name "* (1)*" -o -name "* (2)*" -o -name "* (3)*" -o -name "*копия*" -o -name "*copy*" \) 2>/dev/null)
DUPE_COUNT=$(echo "$DUPES" | grep -c . 2>/dev/null || echo "0")
if [[ "$DUPE_COUNT" -gt 0 && -n "$DUPES" ]]; then
    echo -e "     Найдено: ${YELLOW}$DUPE_COUNT${NC} возможных дубликатов:"
    echo "$DUPES" | head -10 | while read -r f; do
        echo -e "       ${YELLOW}→ $(basename "$f")${NC}"
    done
    if [[ "$DUPE_COUNT" -gt 10 ]]; then
        echo -e "       ${YELLOW}... и ещё $((DUPE_COUNT - 10))${NC}"
    fi
    # Дубликаты НЕ удаляем автоматически — опасно!
    echo -e "     ${YELLOW}⚠️  Дубликаты не удаляются автоматически (проверьте вручную)${NC}"
else
    echo -e "     ${GREEN}Не найдены${NC}"
fi

# ─────────────────── Итог ────────────────────
echo ""
NAS_TOTAL=$(df -h "$NAS_SHARE" 2>/dev/null | tail -1 | awk '{print $2}')
NAS_USED=$(df -h "$NAS_SHARE" 2>/dev/null | tail -1 | awk '{print $3}')
NAS_FREE=$(df -h "$NAS_SHARE" 2>/dev/null | tail -1 | awk '{print $4}')

echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${GREEN}  ✅  CLEANUP NAS ЗАВЕРШЁН${NC}"
echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  ${BOLD}💾 NAS:${NC}       $NAS_TOTAL total / $NAS_USED used / $NAS_FREE free"
echo ""
if [[ "$MODE" == "--dry-run" ]]; then
    echo -e "  ${BOLD}${YELLOW}👉 Для реального удаления: bash $0 --clean${NC}"
fi
echo ""
