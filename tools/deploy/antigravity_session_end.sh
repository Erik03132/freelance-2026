#!/usr/bin/env bash
# ============================================================================
# 🛰️ ANTIGRAVITY SESSION END — Скрипт завершения рабочей сессии
# ============================================================================
# Автор: Antigravity AI / Igor Vasin
# Дата:  23.04.2026
#
# ЧТО ДЕЛАЕТ:
#   1. BACKUP  — Бэкапит фундаментальные скиллы, knowledge, правила, конфиги
#   2. CLEANUP — Подметает мусор сессии (логи, кэши, temp-файлы)
#   3. REPORT  — Показывает сводку: что забэкаплено, что удалено, сколько места
#
# ИСПОЛЬЗОВАНИЕ:
#   bash ~/freelance-2026/tools/antigravity_session_end.sh          # Safe mode
#   bash ~/freelance-2026/tools/antigravity_session_end.sh --deep   # Deep cleanup
#   bash ~/freelance-2026/tools/antigravity_session_end.sh --backup-only  # Только бэкап
#   bash ~/freelance-2026/tools/antigravity_session_end.sh --clean-only   # Только чистка
#
# БЕЗОПАСНОСТЬ:
#   - Никаких sudo, rm -rf /, chmod 777
#   - Бэкап ВСЕГДА делается ДО чистки
#   - Deep cleanup запрашивает подтверждение
# ============================================================================

set -euo pipefail

# ========================= КОНФИГУРАЦИЯ =====================================

# Базовые пути
HOME_DIR="$HOME"
ANTIGRAVITY_DIR="$HOME_DIR/.gemini/antigravity"
WORKSPACE_DIR="$HOME_DIR/freelance-2026"
BACKUP_ROOT="$HOME_DIR/Antigravity_Backups"

# Текущая дата для имени бэкапа
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE_SHORT=$(date +%Y-%m-%d)
BACKUP_DIR="$BACKUP_ROOT/$DATE_SHORT"

# Лог
LOG_FILE="/tmp/antigravity_session_end_${TIMESTAMP}.log"

# Флаги
DO_BACKUP=true
DO_CLEANUP=true
DEEP_CLEANUP=false

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Счётчики
BACKED_UP_COUNT=0
CLEANED_COUNT=0
FREED_BYTES=0

# ========================= УТИЛИТЫ ==========================================

log() {
    local msg="[$(date '+%H:%M:%S')] $1"
    echo -e "$msg" | tee -a "$LOG_FILE"
}

header() {
    echo ""
    echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${CYAN}  $1${NC}"
    echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

success() { echo -e "  ${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"; }
warn()    { echo -e "  ${YELLOW}⚠️  $1${NC}" | tee -a "$LOG_FILE"; }
info()    { echo -e "  ${BLUE}📦 $1${NC}" | tee -a "$LOG_FILE"; }
skip()    { echo -e "  ${MAGENTA}⏭️  $1${NC}" | tee -a "$LOG_FILE"; }
danger()  { echo -e "  ${RED}🗑️  $1${NC}" | tee -a "$LOG_FILE"; }

human_size() {
    local bytes=$1
    if (( bytes >= 1073741824 )); then
        echo "$(echo "scale=1; $bytes / 1073741824" | bc) GB"
    elif (( bytes >= 1048576 )); then
        echo "$(echo "scale=1; $bytes / 1048576" | bc) MB"
    elif (( bytes >= 1024 )); then
        echo "$(echo "scale=1; $bytes / 1024" | bc) KB"
    else
        echo "${bytes} B"
    fi
}

# Безопасное копирование директории
safe_backup_dir() {
    local src="$1"
    local dest="$2"
    local label="$3"

    if [[ -d "$src" ]]; then
        mkdir -p "$dest"
        rsync -a --exclude='node_modules' --exclude='.git' --exclude='venv' --exclude='__pycache__' --exclude='.DS_Store' "$src/" "$dest/" 2>/dev/null
        local count
        count=$(find "$dest" -type f 2>/dev/null | wc -l | tr -d ' ')
        success "$label → $count файлов"
        BACKED_UP_COUNT=$((BACKED_UP_COUNT + count))
    else
        skip "$label — не найдена ($src)"
    fi
}

# Безопасное копирование файла
safe_backup_file() {
    local src="$1"
    local dest="$2"
    local label="$3"

    if [[ -f "$src" ]]; then
        mkdir -p "$(dirname "$dest")"
        cp "$src" "$dest"
        success "$label"
        BACKED_UP_COUNT=$((BACKED_UP_COUNT + 1))
    else
        skip "$label — файл не найден"
    fi
}

# Безопасное удаление с подсчётом
safe_clean() {
    local target="$1"
    local label="$2"

    if [[ -e "$target" ]]; then
        local size
        size=$(du -sk "$target" 2>/dev/null | awk '{print $1 * 1024}' || echo 0)
        rm -rf "$target" 2>/dev/null || true
        FREED_BYTES=$((FREED_BYTES + size))
        CLEANED_COUNT=$((CLEANED_COUNT + 1))
        danger "$label — удалено ($(human_size "$size"))"
    fi
}

# ========================= ПАРСИНГ АРГУМЕНТОВ ===============================

for arg in "$@"; do
    case "$arg" in
        --deep)        DEEP_CLEANUP=true ;;
        --backup-only) DO_CLEANUP=false ;;
        --clean-only)  DO_BACKUP=false ;;
        --help|-h)
            echo "Использование: $0 [--deep] [--backup-only] [--clean-only]"
            echo ""
            echo "  (без флагов)    Safe backup + Safe cleanup"
            echo "  --deep          Safe backup + Deep cleanup (с подтверждением)"
            echo "  --backup-only   Только бэкап, без чистки"
            echo "  --clean-only    Только чистка, без бэкапа"
            exit 0
            ;;
    esac
done

# ========================= СТАРТ ============================================

header "🛰️  ANTIGRAVITY SESSION END — $DATE_SHORT"
log "Скрипт запущен. Режим: backup=$DO_BACKUP, cleanup=$DO_CLEANUP, deep=$DEEP_CLEANUP"

# ========================= ФАЗА 1: БЭКАП ====================================

if $DO_BACKUP; then
    header "📦  ФАЗА 1: БЭКАП ФУНДАМЕНТА"

    mkdir -p "$BACKUP_DIR"
    log "Директория бэкапа: $BACKUP_DIR"

    # ---------- 1.1 Глобальные конфиги Antigravity ----------
    echo ""
    echo -e "  ${BOLD}[1/6] Глобальные конфиги Antigravity${NC}"

    safe_backup_file "$ANTIGRAVITY_DIR/COLD_START.md" \
        "$BACKUP_DIR/antigravity-core/COLD_START.md" \
        "COLD_START.md (точка входа)"

    safe_backup_file "$ANTIGRAVITY_DIR/GLOBAL_CORE_STANDARDS.md" \
        "$BACKUP_DIR/antigravity-core/GLOBAL_CORE_STANDARDS.md" \
        "GLOBAL_CORE_STANDARDS.md (11 правил)"

    safe_backup_file "$ANTIGRAVITY_DIR/GLOBAL_STATUS_MANIFEST.md" \
        "$BACKUP_DIR/antigravity-core/GLOBAL_STATUS_MANIFEST.md" \
        "GLOBAL_STATUS_MANIFEST.md (статус проектов)"

    safe_backup_file "$ANTIGRAVITY_DIR/mcp_config.json" \
        "$BACKUP_DIR/antigravity-core/mcp_config.json" \
        "mcp_config.json (MCP серверы)"

    safe_backup_file "$ANTIGRAVITY_DIR/installation_id" \
        "$BACKUP_DIR/antigravity-core/installation_id" \
        "installation_id"

    # ---------- 1.2 Скиллы агентов ----------
    echo ""
    echo -e "  ${BOLD}[2/6] Скиллы агентов (8 скиллов)${NC}"

    safe_backup_dir "$ANTIGRAVITY_DIR/skills" \
        "$BACKUP_DIR/skills" \
        "Skills (artemiy, botman, igorek, kulibin, marketer, rembrandt, shakespeare, sherl)"

    # ---------- 1.3 Knowledge Items ----------
    echo ""
    echo -e "  ${BOLD}[3/6] Knowledge Items (память агентов)${NC}"

    safe_backup_dir "$ANTIGRAVITY_DIR/knowledge" \
        "$BACKUP_DIR/knowledge" \
        "Knowledge (agent-memory, angelochka, cloud, gbp, mustai, pricing, vezemcip)"

    # ---------- 1.4 Shared Logic ----------
    echo ""
    echo -e "  ${BOLD}[4/6] Shared Logic (переиспользуемый код)${NC}"

    safe_backup_dir "$ANTIGRAVITY_DIR/shared" \
        "$BACKUP_DIR/shared" \
        "Shared Logic (db_pool, faq_engine)"

    # ---------- 1.5 Проектные правила (.agent/rules) ----------
    echo ""
    echo -e "  ${BOLD}[5/6] Проектные правила и скиллы${NC}"

    # Корневые правила workspace
    safe_backup_dir "$WORKSPACE_DIR/.agent" \
        "$BACKUP_DIR/project-rules/workspace-root" \
        "Workspace root rules (ECC, skill-evolution)"

    # Правила по проектам
    local_projects=("ai-eggs" "ai-grant-consalt" "angel-backend" "freelance-agent")
    for proj in "${local_projects[@]}"; do
        if [[ -d "$WORKSPACE_DIR/$proj/.agent" ]]; then
            safe_backup_dir "$WORKSPACE_DIR/$proj/.agent" \
                "$BACKUP_DIR/project-rules/$proj" \
                "Project: $proj"
        fi
    done

    # ---------- 1.6 Ключевые документы проектов ----------
    echo ""
    echo -e "  ${BOLD}[6/6] Стратегические документы${NC}"

    KEY_DOCS=(
        "$WORKSPACE_DIR/STRATEGY_2026.md"
        "$WORKSPACE_DIR/AGENT_SKILL_ROADMAP.md"
        "$WORKSPACE_DIR/ACTIVE_TASKS.md"
        "$WORKSPACE_DIR/SESSION_CHECKPOINT.md"
        "$WORKSPACE_DIR/DOOMSDAY_PROTOCOL.md"
        "$WORKSPACE_DIR/.credentials_vezemcip.md"
    )

    for doc in "${KEY_DOCS[@]}"; do
        local basename
        basename=$(basename "$doc")
        safe_backup_file "$doc" \
            "$BACKUP_DIR/strategy-docs/$basename" \
            "$basename"
    done

    # ---------- Архив бэкапа ----------
    echo ""
    info "Создание архива..."
    ARCHIVE_NAME="antigravity_backup_${TIMESTAMP}.tar.gz"
    tar -czf "$BACKUP_ROOT/$ARCHIVE_NAME" -C "$BACKUP_ROOT" "$DATE_SHORT" 2>/dev/null
    ARCHIVE_SIZE=$(stat -f%z "$BACKUP_ROOT/$ARCHIVE_NAME" 2>/dev/null || echo "0")
    success "Архив: $BACKUP_ROOT/$ARCHIVE_NAME ($(human_size "$ARCHIVE_SIZE"))"

    # Ротация: оставляем только 5 последних архивов
    ARCHIVE_COUNT=$(find "$BACKUP_ROOT" -name "antigravity_backup_*.tar.gz" -type f | wc -l | tr -d ' ')
    if (( ARCHIVE_COUNT > 5 )); then
        EXCESS=$((ARCHIVE_COUNT - 5))
        find "$BACKUP_ROOT" -name "antigravity_backup_*.tar.gz" -type f | sort | head -n "$EXCESS" | while read -r old; do
            rm -f "$old"
            warn "Ротация: удалён старый архив $(basename "$old")"
        done
    fi
fi

# ========================= ФАЗА 2: SAFE CLEANUP =============================

if $DO_CLEANUP; then
    header "🧹  ФАЗА 2: SAFE CLEANUP (без sudo)"

    # ---------- 2.1 Antigravity temp/ephemeral ----------
    echo ""
    echo -e "  ${BOLD}[1/5] Antigravity — эфемерные данные${NC}"

    # Старые browser recordings (старше 7 дней)
    if [[ -d "$ANTIGRAVITY_DIR/browser_recordings" ]]; then
        old_recordings=$(find "$ANTIGRAVITY_DIR/browser_recordings" -type f -mtime +7 2>/dev/null | wc -l | tr -d ' ')
        if (( old_recordings > 0 )); then
            find "$ANTIGRAVITY_DIR/browser_recordings" -type f -mtime +7 -delete 2>/dev/null || true
            danger "Browser recordings старше 7 дней — $old_recordings файлов"
        else
            skip "Browser recordings — всё свежее"
        fi
    fi

    # Логи Antigravity
    if [[ -d "$ANTIGRAVITY_DIR/logs" ]]; then
        log_size=$(du -sk "$ANTIGRAVITY_DIR/logs" 2>/dev/null | awk '{print $1 * 1024}' || echo 0)
        if (( log_size > 10485760 )); then  # >10MB
            find "$ANTIGRAVITY_DIR/logs" -type f -mtime +3 -delete 2>/dev/null || true
            danger "Antigravity logs старше 3 дней — удалены (>10MB)"
        else
            skip "Antigravity logs — в норме ($(human_size "$log_size"))"
        fi
    fi

    # html_artifacts (старше 7 дней)
    if [[ -d "$ANTIGRAVITY_DIR/html_artifacts" ]]; then
        old_html=$(find "$ANTIGRAVITY_DIR/html_artifacts" -type f -mtime +7 2>/dev/null | wc -l | tr -d ' ')
        if (( old_html > 0 )); then
            find "$ANTIGRAVITY_DIR/html_artifacts" -type f -mtime +7 -delete 2>/dev/null || true
            danger "HTML artifacts старше 7 дней — $old_html файлов"
        fi
    fi

    # tempmediaStorage в brain
    if [[ -d "$ANTIGRAVITY_DIR/brain/tempmediaStorage" ]]; then
        safe_clean "$ANTIGRAVITY_DIR/brain/tempmediaStorage" "brain/tempmediaStorage"
    fi

    # ---------- 2.2 Системные кэши пользователя ----------
    echo ""
    echo -e "  ${BOLD}[2/5] Пользовательские кэши${NC}"

    # Кэши npm/yarn
    for cache_dir in "$HOME_DIR/.npm/_cacache" "$HOME_DIR/.yarn/cache"; do
        if [[ -d "$cache_dir" ]]; then
            cache_size=$(du -sk "$cache_dir" 2>/dev/null | awk '{print $1 * 1024}' || echo 0)
            if (( cache_size > 104857600 )); then  # >100MB
                safe_clean "$cache_dir" "$(basename "$(dirname "$cache_dir")")/$(basename "$cache_dir") — $(human_size "$cache_size")"
            else
                skip "$(basename "$cache_dir") — в норме"
            fi
        fi
    done

    # pip кэш
    if [[ -d "$HOME_DIR/Library/Caches/pip" ]]; then
        pip_size=$(du -sk "$HOME_DIR/Library/Caches/pip" 2>/dev/null | awk '{print $1 * 1024}' || echo 0)
        if (( pip_size > 52428800 )); then  # >50MB
            safe_clean "$HOME_DIR/Library/Caches/pip" "pip cache — $(human_size "$pip_size")"
        else
            skip "pip cache — в норме"
        fi
    fi

    # ---------- 2.3 Проектный мусор ----------
    echo ""
    echo -e "  ${BOLD}[3/5] Проектный мусор${NC}"

    # .DS_Store файлы в workspace
    ds_count=$(find "$WORKSPACE_DIR" -name ".DS_Store" -type f 2>/dev/null | wc -l | tr -d ' ')
    if (( ds_count > 0 )); then
        find "$WORKSPACE_DIR" -name ".DS_Store" -type f -delete 2>/dev/null || true
        danger ".DS_Store — $ds_count файлов удалено"
    fi

    # __pycache__ директории
    pycache_count=$(find "$WORKSPACE_DIR" -name "__pycache__" -type d 2>/dev/null | wc -l | tr -d ' ')
    if (( pycache_count > 0 )); then
        find "$WORKSPACE_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
        danger "__pycache__ — $pycache_count директорий удалено"
    fi

    # .pyc файлы
    pyc_count=$(find "$WORKSPACE_DIR" -name "*.pyc" -type f 2>/dev/null | wc -l | tr -d ' ')
    if (( pyc_count > 0 )); then
        find "$WORKSPACE_DIR" -name "*.pyc" -type f -delete 2>/dev/null || true
        danger ".pyc — $pyc_count файлов удалено"
    fi

    # ---------- 2.4 Временные файлы системы ----------
    echo ""
    echo -e "  ${BOLD}[4/5] Временные файлы (старше 1 дня)${NC}"

    # /tmp файлы текущего пользователя старше 1 дня
    tmp_cleaned=0
    for tmpdir in /tmp /private/tmp; do
        if [[ -d "$tmpdir" ]]; then
            cleaned=$(find "$tmpdir" -maxdepth 1 -user "$(whoami)" -type f -mtime +1 2>/dev/null | wc -l | tr -d ' ')
            find "$tmpdir" -maxdepth 1 -user "$(whoami)" -type f -mtime +1 -delete 2>/dev/null || true
            tmp_cleaned=$((tmp_cleaned + cleaned))
        fi
    done
    if (( tmp_cleaned > 0 )); then
        danger "/tmp — $tmp_cleaned старых файлов удалено"
    else
        skip "/tmp — чисто"
    fi

    # ---------- 2.5 Старые логи сессий ----------
    echo ""
    echo -e "  ${BOLD}[5/5] Логи предыдущих сессий${NC}"

    old_logs=$(find /tmp -name "antigravity_session_end_*.log" -type f -mtime +7 2>/dev/null | wc -l | tr -d ' ')
    if (( old_logs > 0 )); then
        find /tmp -name "antigravity_session_end_*.log" -type f -mtime +7 -delete 2>/dev/null || true
        danger "Старые логи сессий — $old_logs файлов"
    fi

    # =================== DEEP CLEANUP (по запросу) ===========================

    if $DEEP_CLEANUP; then
        header "🔥  ФАЗА 3: DEEP CLEANUP (расширенная)"
        echo ""
        echo -e "${YELLOW}  ⚠️  Deep cleanup удаляет: user caches, brew cache, Xcode DerivedData${NC}"
        echo -e "${YELLOW}  ⚠️  Это безопасно, но приложения могут работать чуть медленнее при первом запуске${NC}"
        echo ""
        read -rp "  Продолжить deep cleanup? [y/N]: " confirm
        if [[ "$confirm" =~ ^[Yy]$ ]]; then

            # Пользовательские кэши (полная очистка)
            echo ""
            echo -e "  ${BOLD}[Deep 1/4] Library/Caches${NC}"
            if [[ -d "$HOME_DIR/Library/Caches" ]]; then
                cache_total=$(du -sk "$HOME_DIR/Library/Caches" 2>/dev/null | awk '{print $1 * 1024}' || echo 0)
                # Удаляем содержимое, но не сами папки приложений
                find "$HOME_DIR/Library/Caches" -mindepth 2 -type f -mtime +7 -delete 2>/dev/null || true
                danger "Library/Caches (файлы старше 7 дней) — было $(human_size "$cache_total")"
            fi

            # Пользовательские логи
            echo ""
            echo -e "  ${BOLD}[Deep 2/4] Library/Logs${NC}"
            if [[ -d "$HOME_DIR/Library/Logs" ]]; then
                find "$HOME_DIR/Library/Logs" -type f -mtime +14 -delete 2>/dev/null || true
                danger "Library/Logs (старше 14 дней) — очищено"
            fi

            # Xcode DerivedData
            echo ""
            echo -e "  ${BOLD}[Deep 3/4] Xcode DerivedData${NC}"
            if [[ -d "$HOME_DIR/Library/Developer/Xcode/DerivedData" ]]; then
                xcode_size=$(du -sk "$HOME_DIR/Library/Developer/Xcode/DerivedData" 2>/dev/null | awk '{print $1 * 1024}' || echo 0)
                safe_clean "$HOME_DIR/Library/Developer/Xcode/DerivedData" \
                    "Xcode DerivedData — $(human_size "$xcode_size")"
            else
                skip "Xcode DerivedData — не найден"
            fi

            # Homebrew cleanup
            echo ""
            echo -e "  ${BOLD}[Deep 4/4] Homebrew cleanup${NC}"
            if command -v brew &>/dev/null; then
                brew cleanup --prune=7 2>/dev/null || true
                success "brew cleanup --prune=7 — выполнено"
            else
                skip "Homebrew не установлен"
            fi

        else
            warn "Deep cleanup пропущен пользователем"
        fi
    fi
fi

# ========================= ФАЗА 3: ОТЧЁТ ====================================

header "📊  ИТОГОВЫЙ ОТЧЁТ"

echo ""
echo -e "  ${BOLD}Дата:${NC}           $DATE_SHORT $(date '+%H:%M')"
echo -e "  ${BOLD}Режим:${NC}          $(if $DEEP_CLEANUP; then echo "🔥 DEEP"; else echo "🟢 SAFE"; fi)"

if $DO_BACKUP; then
    echo ""
    echo -e "  ${GREEN}${BOLD}📦 БЭКАП:${NC}"
    echo -e "  ${GREEN}   Файлов забэкаплено:  $BACKED_UP_COUNT${NC}"
    echo -e "  ${GREEN}   Архив:               $BACKUP_ROOT/$ARCHIVE_NAME${NC}"
    echo -e "  ${GREEN}   Размер архива:       $(human_size "$ARCHIVE_SIZE")${NC}"
fi

if $DO_CLEANUP; then
    echo ""
    echo -e "  ${RED}${BOLD}🧹 ЧИСТКА:${NC}"
    echo -e "  ${RED}   Объектов удалено:    $CLEANED_COUNT${NC}"
    echo -e "  ${RED}   Освобождено:         $(human_size "$FREED_BYTES")${NC}"
fi

echo ""
echo -e "  ${BOLD}Лог сессии:${NC}     $LOG_FILE"

# Структура бэкапа
if $DO_BACKUP; then
    echo ""
    echo -e "  ${BOLD}${CYAN}Структура бэкапа:${NC}"
    echo -e "  ${CYAN}  $BACKUP_DIR/${NC}"
    echo -e "  ${CYAN}  ├── antigravity-core/   (COLD_START, STANDARDS, MCP)${NC}"
    echo -e "  ${CYAN}  ├── skills/             (8 агентских скиллов)${NC}"
    echo -e "  ${CYAN}  ├── knowledge/          (8 Knowledge Items)${NC}"
    echo -e "  ${CYAN}  ├── shared/             (переиспользуемая логика)${NC}"
    echo -e "  ${CYAN}  ├── project-rules/      (правила по проектам)${NC}"
    echo -e "  ${CYAN}  └── strategy-docs/      (стратегия, задачи, чекпоинт)${NC}"
fi

echo ""
echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${GREEN}  ✅  СЕССИЯ ЗАВЕРШЕНА. СИСТЕМА В ПОРЯДКЕ.${NC}"
echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  💡 Для восстановления из бэкапа:"
echo -e "     tar -xzf $BACKUP_ROOT/$ARCHIVE_NAME -C /tmp/"
echo -e "     # Затем скопировать нужные папки обратно в ~/.gemini/antigravity/"
echo ""
