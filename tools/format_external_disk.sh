#!/usr/bin/env bash
# ============================================================================
# 🗄️  FORMAT EXTERNAL DISK — Подготовка внешнего диска для бэкапов Antigravity
# ============================================================================
# ЗАПУСКАЕТСЯ ОДИН РАЗ при подключении нового диска
#
# ЧТО ДЕЛАЕТ:
#   1. Показывает список всех подключённых дисков
#   2. Предлагает выбрать нужный диск
#   3. Форматирует его в APFS (надёжный для macOS, поддерживает снепшоты)
#   4. Присваивает метку ANTIGRAVITY_BACKUP
#   5. Создаёт структуру папок для бэкапов
#   6. Сохраняет конфиг диска в ~/.antigravity_disk.conf
#
# ИСПОЛЬЗОВАНИЕ:
#   bash ~/freelance-2026/tools/format_external_disk.sh
#
# ⚠️  ВНИМАНИЕ: Форматирование УНИЧТОЖАЕТ все данные на диске!
# ============================================================================

set -euo pipefail

# ─────────────────── Цвета ────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

DISK_LABEL="ANTIGRAVITY_BACKUP"
MOUNT_POINT="/Volumes/$DISK_LABEL"
CONF_FILE="$HOME/.antigravity_disk.conf"

echo ""
echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${CYAN}  🗄️  ANTIGRAVITY EXTERNAL DISK SETUP — $(date '+%d.%m.%Y %H:%M')${NC}"
echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo ""
echo -e "${BOLD}📋 Подключённые диски (внешние):${NC}"
echo ""

# Показываем только внешние диски
diskutil list external

echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${RED}${BOLD}⚠️  ВНИМАНИЕ: Форматирование удалит ВСЕ данные на выбранном диске!${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BOLD}Введите идентификатор диска (например: disk2, disk3):${NC}"
echo -e "${CYAN}Подсказка: смотрите столбец слева (/dev/diskX)${NC}"
echo ""
read -rp "Диск > " DISK_ID

# Валидация
if [[ -z "$DISK_ID" ]]; then
    echo -e "${RED}❌ Диск не указан. Выход.${NC}"
    exit 1
fi

DISK_FULL="/dev/$DISK_ID"

if ! diskutil info "$DISK_FULL" &>/dev/null; then
    echo -e "${RED}❌ Диск $DISK_FULL не найден. Проверьте имя.${NC}"
    exit 1
fi

# Показываем инфо о диске для подтверждения
echo ""
echo -e "${BOLD}📌 Информация о выбранном диске:${NC}"
diskutil info "$DISK_FULL" | grep -E "Device|Volume Name|Disk Size|Media Type"
echo ""

# Финальное подтверждение
echo -e "${RED}${BOLD}‼️  Вы уверены? Введите 'ДА' для подтверждения форматирования:${NC}"
read -rp "> " CONFIRM

if [[ "$CONFIRM" != "ДА" ]]; then
    echo -e "${YELLOW}⏭️  Отмена. Диск не изменён.${NC}"
    exit 0
fi

# ─────────────────── Форматирование ────────────────────
echo ""
echo -e "${BOLD}🔄 Форматирование $DISK_FULL в APFS с меткой '$DISK_LABEL'...${NC}"
echo -e "${CYAN}(Это займёт несколько секунд)${NC}"
echo ""

diskutil eraseDisk APFS "$DISK_LABEL" "$DISK_FULL"

echo ""
echo -e "${GREEN}✅ Диск отформатирован!${NC}"
echo -e "   Метка:      ${BOLD}$DISK_LABEL${NC}"
echo -e "   Формат:     ${BOLD}APFS${NC}"
echo -e "   Точка входа: ${BOLD}$MOUNT_POINT${NC}"

# ─────────────────── Структура папок ────────────────────
echo ""
echo -e "${BOLD}📁 Создаём структуру папок для бэкапов...${NC}"

mkdir -p "$MOUNT_POINT/antigravity-backup"/{brain,skills,knowledge,project-rules,strategy,reports,checkpoints,git-bundles,logs,archives}

echo -e "${GREEN}✅ Структура создана:${NC}"
echo -e "   $MOUNT_POINT/antigravity-backup/"
echo -e "     ├── brain/         (core files, mcp_config)"
echo -e "     ├── skills/        (все скиллы агентов)"
echo -e "     ├── knowledge/     (knowledge base)"
echo -e "     ├── project-rules/ (правила проектов)"
echo -e "     ├── strategy/      (ACTIVE_TASKS, chp.md, ...)"
echo -e "     ├── reports/       (стенограммы сессий)"
echo -e "     ├── checkpoints/   (чекпоинты)"
echo -e "     ├── git-bundles/   (git bundle репозиториев)"
echo -e "     ├── logs/          (логи агентов)"
echo -e "     └── archives/      (tar.gz архивы)"

# ─────────────────── Сохраняем конфиг ────────────────────
echo ""
cat > "$CONF_FILE" <<EOF
# Конфигурация внешнего диска Antigravity
# Создан: $(date '+%Y-%m-%d %H:%M:%S')
EXTERNAL_DISK_LABEL="$DISK_LABEL"
EXTERNAL_DISK_MOUNT="$MOUNT_POINT"
EXTERNAL_DISK_BACKUP_DIR="$MOUNT_POINT/antigravity-backup"
EXTERNAL_DISK_ID="$DISK_FULL"
EOF

echo -e "${GREEN}✅ Конфиг сохранён: $CONF_FILE${NC}"

# ─────────────────── Итог ────────────────────
echo ""
echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${GREEN}  ✅  ВНЕШНИЙ ДИСК ГОТОВ К РАБОТЕ${NC}"
echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  ${BOLD}💾 Диск:${NC}       $DISK_FULL"
echo -e "  ${BOLD}📁 Метка:${NC}      $DISK_LABEL"
echo -e "  ${BOLD}📂 Бэкап:${NC}      $MOUNT_POINT/antigravity-backup/"
echo -e "  ${BOLD}⚙️  Конфиг:${NC}     $CONF_FILE"
echo ""
echo -e "  ${BOLD}${YELLOW}👉 Следующий шаг:${NC}"
echo -e "     bash ~/freelance-2026/tools/sync_to_external.sh"
echo -e "     Или запустить finish-day — диск подхватится автоматически."
echo ""
