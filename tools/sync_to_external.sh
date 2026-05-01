#!/usr/bin/env bash
# ============================================================================
# 💾  SYNC TO EXTERNAL DISK — Синхронизация с внешним диском Antigravity
# ============================================================================
# Третий уровень резервирования (после GitHub и NAS)
# Используется когда нет интернета И нет связи с NAS
#
# УРОВНИ РЕЗЕРВИРОВАНИЯ:
#   🌐 Уровень 1: GitHub        (есть интернет)
#   🏠 Уровень 2: NAS DS720     (есть Wi-Fi дома)
#   💾 Уровень 3: Внешний диск  (автономный, всегда работает)
#
# ИСПОЛЬЗОВАНИЕ:
#   bash ~/freelance-2026/tools/sync_to_external.sh
#   bash ~/freelance-2026/tools/sync_to_external.sh --force  # даже если NAS был доступен
#
# КОНФИГ ДИСКА:
#   Сначала запустите format_external_disk.sh для подготовки диска.
#   Конфиг хранится в ~/.antigravity_disk.conf
# ============================================================================

set -euo pipefail

# ─────────────────── Конфигурация ────────────────────
CONF_FILE="$HOME/freelance-2026/.antigravity_disk.conf"
WORKSPACE="$HOME/freelance-2026"
ANTIGRAVITY="$HOME/.gemini/antigravity"
TIMESTAMP=$(date +%Y%m%d_%H%M)
FORCE="${1:-}"

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${CYAN}  💾  SYNC TO EXTERNAL DISK — $(date '+%d.%m.%Y %H:%M')${NC}"
echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# ─────────────────── Загружаем конфиг диска ────────────────────
if [[ ! -f "$CONF_FILE" ]]; then
    echo -e "${YELLOW}⚠️  Конфиг диска не найден: $CONF_FILE${NC}"
    echo -e "   Запустите сначала: bash ~/freelance-2026/tools/format_external_disk.sh"
    echo ""
    # Пробуем автоопределение по стандартной метке
    EXTERNAL_DISK_MOUNT="/Volumes/ANTIGRAVITY_BACKUP"
    EXTERNAL_DISK_BACKUP_DIR="$EXTERNAL_DISK_MOUNT/antigravity-backup"
    echo -e "${CYAN}ℹ️  Пробуем автоопределение: $EXTERNAL_DISK_MOUNT${NC}"
else
    # shellcheck source=/dev/null
    source "$CONF_FILE"
fi

# ─────────────────── Проверка доступности диска ────────────────────
if [[ ! -d "${EXTERNAL_DISK_MOUNT:-/Volumes/ANTIGRAVITY_BACKUP}" ]]; then
    echo -e "${RED}❌ Внешний диск не подключён.${NC}"
    echo -e "${YELLOW}   Ожидаемая точка монтирования: ${EXTERNAL_DISK_MOUNT:-/Volumes/ANTIGRAVITY_BACKUP}${NC}"
    echo ""
    echo -e "${CYAN}📋 Подключённые тома:${NC}"
    ls /Volumes/ 2>/dev/null || echo "   (нет данных)"
    echo ""
    echo -e "${YELLOW}👉 Подключите внешний диск и повторите.${NC}"
    exit 1
fi

BACKUP_DIR="${EXTERNAL_DISK_BACKUP_DIR:-$EXTERNAL_DISK_MOUNT/antigravity-backup}"

echo -e "${GREEN}✅ Внешний диск доступен: $EXTERNAL_DISK_MOUNT${NC}"

# Создаём структуру если её нет
mkdir -p "$BACKUP_DIR"/{brain,skills,knowledge,project-rules,strategy,reports,checkpoints,git-bundles,logs,archives}

# ─────────────────── Функции бэкапа ────────────────────
sync_dir() {
    local src="$1" dest="$2" label="$3"
    if [[ -d "$src" ]]; then
        mkdir -p "$dest"
        rsync -a --delete \
              --exclude='node_modules' \
              --exclude='.git' \
              --exclude='venv' \
              --exclude='__pycache__' \
              --exclude='.DS_Store' \
              --exclude='*.pyc' \
              "$src/" "$dest/" 2>/dev/null
        echo -e "  ${GREEN}✅ $label${NC}"
    else
        echo -e "  ${YELLOW}⏭️  Пропущен (нет папки): $label${NC}"
    fi
}

sync_file() {
    local src="$1" dest="$2" label="$3"
    if [[ -f "$src" ]]; then
        mkdir -p "$(dirname "$dest")"
        cp "$src" "$dest"
        echo -e "  ${GREEN}✅ $label${NC}"
    else
        echo -e "  ${YELLOW}⏭️  Пропущен (нет файла): $label${NC}"
    fi
}

# ─────────────────── Синхронизация ────────────────────

echo ""
echo -e "  ${BOLD}🧠 ФАЗА 1: Ядро Antigravity...${NC}"

# Core файлы
sync_file "$ANTIGRAVITY/COLD_START.md"             "$BACKUP_DIR/brain/COLD_START.md"             "COLD_START.md"
sync_file "$ANTIGRAVITY/GLOBAL_CORE_STANDARDS.md"  "$BACKUP_DIR/brain/GLOBAL_CORE_STANDARDS.md"  "GLOBAL_CORE_STANDARDS.md"
sync_file "$ANTIGRAVITY/GLOBAL_STATUS_MANIFEST.md" "$BACKUP_DIR/brain/GLOBAL_STATUS_MANIFEST.md" "GLOBAL_STATUS_MANIFEST.md"
sync_file "$ANTIGRAVITY/mcp_config.json"           "$BACKUP_DIR/brain/mcp_config.json"           "mcp_config.json"

echo ""
echo -e "  ${BOLD}🎯 ФАЗА 2: Скиллы и Knowledge...${NC}"

sync_dir "$ANTIGRAVITY/skills"    "$BACKUP_DIR/skills"    "Skills (все агенты)"
sync_dir "$ANTIGRAVITY/knowledge" "$BACKUP_DIR/knowledge" "Knowledge Base"
sync_dir "$ANTIGRAVITY/shared"    "$BACKUP_DIR/brain/shared" "Shared Logic"

echo ""
echo -e "  ${BOLD}📐 ФАЗА 3: Проектные правила...${NC}"

for proj in ai-eggs ai-grant-consalt angel-backend freelance-agent; do
    if [[ -d "$WORKSPACE/$proj/.agent" ]]; then
        sync_dir "$WORKSPACE/$proj/.agent" "$BACKUP_DIR/project-rules/$proj" "Rules: $proj"
    fi
done
sync_dir "$WORKSPACE/.agent" "$BACKUP_DIR/project-rules/_workspace" "Rules: workspace root"

echo ""
echo -e "  ${BOLD}📋 ФАЗА 4: Стратегия и документы...${NC}"

for doc in STRATEGY_2026.md ACTIVE_TASKS.md chp.md DOOMSDAY_PROTOCOL.md AGENT_SKILL_ROADMAP.md AGENT_EVOLUTION_ROADMAP.md; do
    sync_file "$WORKSPACE/$doc" "$BACKUP_DIR/strategy/$doc" "$doc"
done

echo ""
echo -e "  ${BOLD}📝 ФАЗА 5: Отчёты и чекпоинты...${NC}"

sync_dir "$WORKSPACE/reports"     "$BACKUP_DIR/reports"     "Стенограммы сессий"
sync_dir "$WORKSPACE/checkpoints" "$BACKUP_DIR/checkpoints" "Чекпоинты"

echo ""
echo -e "  ${BOLD}📦 ФАЗА 6: Git bundles...${NC}"

# ai-eggs bundle
if [[ -d "$WORKSPACE/ai-eggs/.git" ]]; then
    echo -ne "  📦 Git bundle (ai-eggs)... "
    (cd "$WORKSPACE/ai-eggs" && git bundle create "$BACKUP_DIR/git-bundles/ai-eggs_${TIMESTAMP}.bundle" --all 2>/dev/null) \
        && echo -e "${GREEN}✅${NC}" \
        || echo -e "${YELLOW}⏭️ пропущен${NC}"
fi

# freelance-2026 bundle (корневой репо)
if [[ -d "$WORKSPACE/.git" ]]; then
    echo -ne "  📦 Git bundle (freelance-2026)... "
    (cd "$WORKSPACE" && git bundle create "$BACKUP_DIR/git-bundles/freelance-2026_${TIMESTAMP}.bundle" --all 2>/dev/null) \
        && echo -e "${GREEN}✅${NC}" \
        || echo -e "${YELLOW}⏭️ пропущен${NC}"
fi

# Ротация git bundles (оставляем 3 последних)
for pattern in "ai-eggs_*.bundle" "freelance-2026_*.bundle"; do
    BUNDLE_COUNT=$(find "$BACKUP_DIR/git-bundles" -name "$pattern" -type f 2>/dev/null | wc -l | tr -d ' ')
    if (( BUNDLE_COUNT > 3 )); then
        EXCESS=$((BUNDLE_COUNT - 3))
        find "$BACKUP_DIR/git-bundles" -name "$pattern" -type f | sort | head -n "$EXCESS" | while read -r old; do
            rm -f "$old" 2>/dev/null
        done
        echo -e "  ${YELLOW}♻️  Ротация ($pattern): удалено $EXCESS старых${NC}"
    fi
done

echo ""
echo -e "  ${BOLD}🗜️  ФАЗА 7: Финальный архив...${NC}"

ARCHIVE="$BACKUP_DIR/archives/antigravity_full_${TIMESTAMP}.tar.gz"
tar -czf "$ARCHIVE" \
    -C "$BACKUP_DIR" \
    brain skills knowledge project-rules strategy \
    2>/dev/null
ARCHIVE_SIZE=$(du -sh "$ARCHIVE" 2>/dev/null | cut -f1)
echo -e "  ${GREEN}✅ Архив: $(basename "$ARCHIVE") ($ARCHIVE_SIZE)${NC}"

# Ротация архивов (оставляем 3)
ARCH_COUNT=$(find "$BACKUP_DIR/archives" -name "antigravity_full_*.tar.gz" -type f 2>/dev/null | wc -l | tr -d ' ')
if (( ARCH_COUNT > 3 )); then
    EXCESS=$((ARCH_COUNT - 3))
    find "$BACKUP_DIR/archives" -name "antigravity_full_*.tar.gz" -type f | sort | head -n "$EXCESS" | while read -r old; do
        rm -f "$old" 2>/dev/null
    done
    echo -e "  ${YELLOW}♻️  Ротация архивов: удалено $EXCESS старых${NC}"
fi

# ─────────────────── Статистика ────────────────────
DISK_USED=$(df -h "$EXTERNAL_DISK_MOUNT" 2>/dev/null | awk 'NR==2{print $3}')
DISK_FREE=$(df -h "$EXTERNAL_DISK_MOUNT" 2>/dev/null | awk 'NR==2{print $4}')
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)

# Пишем лог последнего бэкапа
cat > "$BACKUP_DIR/.last_sync.txt" <<EOF
Последняя синхронизация: $(date '+%Y-%m-%d %H:%M:%S')
Хост: $(hostname)
Размер бэкапа: $BACKUP_SIZE
Свободно на диске: $DISK_FREE
Архив: $(basename "$ARCHIVE")
EOF

# ─────────────────── Итог ────────────────────
echo ""
echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${GREEN}  ✅  SYNC TO EXTERNAL DISK ЗАВЕРШЁН${NC}"
echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  ${BOLD}💾 Диск:${NC}        $EXTERNAL_DISK_MOUNT"
echo -e "  ${BOLD}📁 Бэкап:${NC}       $BACKUP_DIR"
echo -e "  ${BOLD}📦 Размер:${NC}      $BACKUP_SIZE"
echo -e "  ${BOLD}🆓 Свободно:${NC}    $DISK_FREE (занято: $DISK_USED)"
echo -e "  ${BOLD}🕐 Время:${NC}       $(date '+%H:%M:%S')"
echo ""
echo -e "  ${BOLD}${YELLOW}👉 Диск можно безопасно отключить.${NC}"
echo ""
