#!/bin/bash
# ==============================================================
# SYNC TO NAS DS720 — Выгрузка тяжёлых файлов на Synology
# ==============================================================
# NAS: DS720 (192.168.0.107) — Synology DS720+
# Шара: "Документы СЕМЬЯ" → /Volumes/Документы СЕМЬЯ
# Папка бэкапа: AI/antigravity-backup/
#
# Что синхронизируем:
#   1. Логи агентов (55 MB+)
#   2. Бэкапы Antigravity
#   3. Данные shadow_learning
#   4. Git-пакеты (736 MB)
#   5. Тяжёлые модели (v4_ru.pt и т.д.)
#
# Использование:
#   bash ~/freelance-2026/tools/sync_to_nas.sh
#   bash ~/freelance-2026/tools/sync_to_nas.sh --cleanup  # с очисткой логов
# ==============================================================

set -euo pipefail

# ─────────────────── Конфигурация ────────────────────
NAS_SHARE="/Volumes/Документы СЕМЬЯ"
BACKUP_DIR="$NAS_SHARE/AI/antigravity-backup"
WORKSPACE="$HOME/freelance-2026"
TIMESTAMP=$(date +%Y%m%d_%H%M)
CLEANUP="${1:-}"

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${CYAN}  📦  SYNC TO NAS DS720 — $(date '+%d.%m.%Y %H:%M')${NC}"
echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# ─────────────────── Проверка NAS ────────────────────
if [[ ! -d "$NAS_SHARE" ]]; then
    echo -e "${RED}❌ NAS не примонтирован: $NAS_SHARE${NC}"
    echo -e "${YELLOW}   Откройте Finder → DS720 → 'Документы СЕМЬЯ'${NC}"
    echo -e "${YELLOW}   Или: open 'smb://erik03132@192.168.0.107/Документы СЕМЬЯ'${NC}"
    exit 1
fi

# Создаём структуру на NAS
mkdir -p "$BACKUP_DIR"/{logs,brain,data,models,git-bundles,reports,checkpoints}
echo -e "${GREEN}✅ NAS доступен: $NAS_SHARE${NC}"

# ─────────────────── Синхронизация ────────────────────

echo ""
echo -e "  ${BOLD}📋 ФАЗА 1: Синхронизация данных...${NC}"

# 1. Логи агентов (55 MB+)
if [[ -d "$WORKSPACE/ai-eggs/agent/logs" ]]; then
    echo -ne "  📝 Логи агентов... "
    rsync -ah --progress "$WORKSPACE/ai-eggs/agent/logs/" "$BACKUP_DIR/logs/" 2>/dev/null
    echo -e "${GREEN}✅${NC}"
fi

# 2. Бэкапы Antigravity
if [[ -d "$WORKSPACE/.backups/antigravity" ]]; then
    echo -ne "  🧠 Бэкапы Antigravity... "
    rsync -ah --progress "$WORKSPACE/.backups/antigravity/" "$BACKUP_DIR/brain/backups/" 2>/dev/null
    echo -e "${GREEN}✅${NC}"
fi

# 3. Knowledge Base
if [[ -d "$HOME/.gemini/antigravity/knowledge" ]]; then
    echo -ne "  📚 Knowledge Base... "
    rsync -ah "$HOME/.gemini/antigravity/knowledge/" "$BACKUP_DIR/brain/knowledge/" 2>/dev/null
    echo -e "${GREEN}✅${NC}"
fi

# 4. Skills
if [[ -d "$HOME/.gemini/antigravity/skills" ]]; then
    echo -ne "  🎯 Skills... "
    rsync -ah "$HOME/.gemini/antigravity/skills/" "$BACKUP_DIR/brain/skills/" 2>/dev/null
    echo -e "${GREEN}✅${NC}"
fi

# 5. Shadow Learning данные
if [[ -d "$WORKSPACE/ai-eggs/data/shadow_learning" ]]; then
    echo -ne "  🔍 Shadow Learning... "
    rsync -ah "$WORKSPACE/ai-eggs/data/shadow_learning/" "$BACKUP_DIR/data/shadow_learning/" 2>/dev/null
    echo -e "${GREEN}✅${NC}"
fi

# 6. CRM-сканы
if [[ -d "$WORKSPACE/ai-eggs/data/bitrix_scans" ]]; then
    echo -ne "  📊 CRM-сканы... "
    rsync -ah "$WORKSPACE/ai-eggs/data/bitrix_scans/" "$BACKUP_DIR/data/bitrix_scans/" 2>/dev/null
    echo -e "${GREEN}✅${NC}"
fi

# 7. Отчёты и чекпоинты
if [[ -d "$WORKSPACE/reports" ]]; then
    echo -ne "  📝 Отчёты... "
    rsync -ah "$WORKSPACE/reports/" "$BACKUP_DIR/reports/" 2>/dev/null
    echo -e "${GREEN}✅${NC}"
fi
if [[ -d "$WORKSPACE/checkpoints" ]]; then
    echo -ne "  📍 Чекпоинты... "
    rsync -ah "$WORKSPACE/checkpoints/" "$BACKUP_DIR/checkpoints/" 2>/dev/null
    echo -e "${GREEN}✅${NC}"
fi

# 8. Тяжёлые модели (если есть)
for model in "$WORKSPACE/ai-eggs/agent/v4_ru.pt"; do
    if [[ -f "$model" ]]; then
        echo -ne "  🤖 Модель $(basename "$model")... "
        rsync -ah "$model" "$BACKUP_DIR/models/" 2>/dev/null
        echo -e "${GREEN}✅${NC}"
    fi
done

# 9. Git bundle (полная копия репо без .git overhead)
echo -ne "  📦 Git bundle (ai-eggs)... "
(cd "$WORKSPACE/ai-eggs" && git bundle create "$BACKUP_DIR/git-bundles/ai-eggs_${TIMESTAMP}.bundle" --all 2>/dev/null) && echo -e "${GREEN}✅${NC}" || echo -e "${YELLOW}⏭️ пропущен${NC}"

# Ротация git bundles (оставляем 5 последних)
BUNDLE_COUNT=$(find "$BACKUP_DIR/git-bundles" -name "ai-eggs_*.bundle" -type f 2>/dev/null | wc -l | tr -d ' ')
if (( BUNDLE_COUNT > 5 )); then
    EXCESS=$((BUNDLE_COUNT - 5))
    find "$BACKUP_DIR/git-bundles" -name "ai-eggs_*.bundle" -type f | sort | head -n "$EXCESS" | while read -r old; do
        rm -f "$old" 2>/dev/null
    done
    echo -e "  ${YELLOW}♻️  Ротация: удалено $EXCESS старых bundle${NC}"
fi

# ─────────────────── Очистка (опционально) ────────────────────

if [[ "$CLEANUP" == "--cleanup" ]]; then
    echo ""
    echo -e "  ${BOLD}🧹 ФАЗА 2: Очистка тяжёлых файлов на SSD...${NC}"
    
    # Очищаем старые логи (>7 дней, оставляем свежие)
    OLD_LOGS=$(find "$WORKSPACE/ai-eggs/agent/logs" -type f -name "*.log" -mtime +7 2>/dev/null | wc -l | tr -d ' ')
    find "$WORKSPACE/ai-eggs/agent/logs" -type f -name "*.log" -mtime +7 -delete 2>/dev/null || true
    echo -e "  ${RED}🗑️  Старые логи (>7д): $OLD_LOGS файлов${NC}"
    
    # Очищаем старые CRM-сканы (>14 дней)
    OLD_SCANS=$(find "$WORKSPACE/ai-eggs/data/bitrix_scans" -type f -mtime +14 2>/dev/null | wc -l | tr -d ' ')
    find "$WORKSPACE/ai-eggs/data/bitrix_scans" -type f -mtime +14 -delete 2>/dev/null || true
    echo -e "  ${RED}🗑️  Старые CRM-сканы (>14д): $OLD_SCANS файлов${NC}"
fi

# ─────────────────── Итог ────────────────────

NAS_USED=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
echo ""
echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${GREEN}  ✅  SYNC TO NAS ЗАВЕРШЁН${NC}"
echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  ${BOLD}📦 NAS:${NC}      $BACKUP_DIR"
echo -e "  ${BOLD}💾 Занято:${NC}   $NAS_USED"
echo -e "  ${BOLD}🕐 Время:${NC}   $(date '+%H:%M:%S')"
echo ""
