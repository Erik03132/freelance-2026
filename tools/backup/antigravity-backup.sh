#!/bin/bash
# ============================================================================
# 🛡️ ANTIGRAVITY BRAIN BACKUP
# ============================================================================
# Копирует уже подготовленную папку-снапшот в архив.
#
# ВАЖНО: Этот скрипт НЕ может напрямую читать ~/.gemini/antigravity из-за
# macOS TCC (Full Disk Access). Папку-снапшот готовит Antigravity-агент
# через свои инструменты (у него есть доступ к .gemini).
#
# Workflow:
#   1. Antigravity копирует данные → /Users/igorvasin/freelance-2026/tools/.backup-staging/
#   2. Этот скрипт архивирует staging → бэкап-архив
#   3. Архив хранится локально в ~/antigravity-backups/ (можно скопировать в облако)
#
# Восстановление:
#   ./antigravity-backup.sh --restore <путь_к_архиву>
# ============================================================================

set -euo pipefail

# ─── КОНФИГУРАЦИЯ ────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
STAGING_DIR="$SCRIPT_DIR/.backup-staging"
BACKUP_DIR="$HOME/antigravity-backups"
BACKUP_NAME="antigravity-brain"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
ARCHIVE_NAME="${BACKUP_NAME}_${TIMESTAMP}.tar.gz"
MAX_BACKUPS=30

ANTIGRAVITY_DIR="$HOME/.gemini/antigravity"

# ─── ЦВЕТА ───────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[✓]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }
log_step()  { echo -e "${BLUE}[→]${NC} $1"; }

# ─── РЕЖИМ ВОССТАНОВЛЕНИЯ ───────────────────────────────────────────────────
if [ "${1:-}" = "--restore" ]; then
    ARCHIVE_PATH="${2:-}"
    
    if [ -z "$ARCHIVE_PATH" ]; then
        echo ""
        echo -e "${CYAN}🔄 РЕЖИМ ВОССТАНОВЛЕНИЯ${NC}"
        echo "========================"
        echo ""
        echo "Использование: $0 --restore <путь_к_архиву>"
        echo ""
        echo "Доступные бэкапы:"
        if [ -d "$BACKUP_DIR" ]; then
            ls -lahtr "$BACKUP_DIR"/${BACKUP_NAME}_*.tar.gz 2>/dev/null || echo "  (нет бэкапов в $BACKUP_DIR)"
        else
            echo "  (директория $BACKUP_DIR не найдена)"
        fi
        echo ""
        echo -e "${YELLOW}Куда восстанавливать:${NC} $ANTIGRAVITY_DIR"
        echo ""
        echo "Шаги восстановления:"
        echo "  1. Установите/переустановите Antigravity"
        echo "  2. Запустите: $0 --restore ~/antigravity-backups/<архив>.tar.gz"
        echo "  3. Перезапустите Antigravity"
        exit 0
    fi

    if [ ! -f "$ARCHIVE_PATH" ]; then
        log_error "Файл не найден: $ARCHIVE_PATH"
        exit 1
    fi

    echo ""
    echo -e "${CYAN}🔄 ВОССТАНОВЛЕНИЕ ANTIGRAVITY BRAIN${NC}"
    echo "======================================="
    echo ""
    echo "  📦 Архив: $ARCHIVE_PATH"
    echo "  📂 Цель:  $ANTIGRAVITY_DIR"
    echo ""

    # Бэкап текущего состояния
    if [ -d "$ANTIGRAVITY_DIR" ]; then
        PRE_RESTORE="${ANTIGRAVITY_DIR}.pre-restore.$(date +%s)"
        log_warn "Текущие данные будут сохранены в: $PRE_RESTORE"
        cp -R "$ANTIGRAVITY_DIR" "$PRE_RESTORE" 2>/dev/null || true
    fi

    read -p "Продолжить восстановление? (y/N): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        log_warn "Отменено."
        exit 0
    fi

    log_step "Распаковка архива..."
    TEMP_DIR=$(mktemp -d)
    tar -xzf "$ARCHIVE_PATH" -C "$TEMP_DIR"

    EXTRACTED_DIR="$TEMP_DIR/antigravity-brain"
    if [ ! -d "$EXTRACTED_DIR" ]; then
        log_error "Неверный формат архива (нет antigravity-brain/)"
        rm -rf "$TEMP_DIR"
        exit 1
    fi

    mkdir -p "$ANTIGRAVITY_DIR"

    # Восстанавливаем по компонентам
    for item in skills knowledge implicit shared annotations prompting \
                GLOBAL_CORE_STANDARDS.md GLOBAL_STATUS_MANIFEST.md \
                mcp_config.json installation_id; do
        if [ -e "$EXTRACTED_DIR/$item" ]; then
            log_step "Восстановление: $item"
            rm -rf "${ANTIGRAVITY_DIR:?}/$item"
            cp -R "$EXTRACTED_DIR/$item" "$ANTIGRAVITY_DIR/$item"
            log_info "  → $item ✓"
        fi
    done

    # Brain — опционально
    if [ -d "$EXTRACTED_DIR/brain" ]; then
        read -p "Восстановить логи разговоров (brain/)? Это может быть большой объём. (y/N): " restore_brain
        if [ "$restore_brain" = "y" ] || [ "$restore_brain" = "Y" ]; then
            log_step "Восстановление: brain/"
            cp -R "$EXTRACTED_DIR/brain" "$ANTIGRAVITY_DIR/brain"
            log_info "  → brain/ ✓"
        fi
    fi

    rm -rf "$TEMP_DIR"

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "ВОССТАНОВЛЕНИЕ ЗАВЕРШЕНО!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "⚠️  Перезапустите Antigravity для применения изменений."
    echo ""
    exit 0
fi

# ─── РЕЖИМ БЭКАПА (архивация staging) ────────────────────────────────────────
echo ""
echo -e "${CYAN}🛡️  ANTIGRAVITY BRAIN BACKUP${NC}"
echo "=============================="
echo "📅 $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Проверяем что staging подготовлен
if [ ! -d "$STAGING_DIR" ]; then
    log_error "Staging-директория не найдена: $STAGING_DIR"
    echo ""
    echo "Чтобы создать бэкап, попросите Antigravity-агент:"
    echo '  "Сделай бэкап мозга"'
    echo ""
    echo "Агент подготовит staging, а затем запустит этот скрипт."
    exit 1
fi

# Проверяем что staging не пустой
if [ -z "$(ls -A "$STAGING_DIR" 2>/dev/null)" ]; then
    log_error "Staging-директория пуста"
    exit 1
fi

# Показываем что будет архивировано
log_step "Содержимое staging:"
for item in "$STAGING_DIR"/*/; do
    [ -d "$item" ] && echo "  📁 $(basename "$item")/"
done
for item in "$STAGING_DIR"/*; do
    [ -f "$item" ] && echo "  📄 $(basename "$item")"
done
echo ""

# Создаём директорию для бэкапов
mkdir -p "$BACKUP_DIR"

# Архивируем
log_step "Создание архива..."
ARCHIVE_PATH="$BACKUP_DIR/$ARCHIVE_NAME"
tar -czf "$ARCHIVE_PATH" -C "$STAGING_DIR/.." "$(basename "$STAGING_DIR")"

ARCHIVE_SIZE=$(ls -lh "$ARCHIVE_PATH" | awk '{print $5}')

# Очищаем staging
log_step "Очистка staging..."
rm -rf "$STAGING_DIR"

# Ротация старых бэкапов
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/${BACKUP_NAME}_*.tar.gz 2>/dev/null | wc -l | xargs)
if [ "$BACKUP_COUNT" -gt "$MAX_BACKUPS" ]; then
    REMOVE_COUNT=$((BACKUP_COUNT - MAX_BACKUPS))
    log_step "Ротация: удаление $REMOVE_COUNT старых бэкапов..."
    ls -1t "$BACKUP_DIR"/${BACKUP_NAME}_*.tar.gz | tail -n "$REMOVE_COUNT" | xargs rm -f
fi

# Итог
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "БЭКАП ЗАВЕРШЁН!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📦 Архив:    $ARCHIVE_PATH"
echo "  📏 Размер:   $ARCHIVE_SIZE"
echo "  🗄️  Всего:    $BACKUP_COUNT/$MAX_BACKUPS бэкапов"
echo ""
echo "💡 Рекомендация: скопируйте архив в облако:"
echo "   cp \"$ARCHIVE_PATH\" ~/Google\\ Drive/Backups/"
echo "   # или"
echo "   cp \"$ARCHIVE_PATH\" ~/Yandex.Disk/Backups/"
echo ""
