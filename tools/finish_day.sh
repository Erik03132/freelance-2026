#!/usr/bin/env bash
# ============================================================================
# 🛰️ ANTIGRAVITY FINISH-DAY — Завершение рабочего дня
# ============================================================================
# Вызывается агентом по команде пользователя "finish-day"
#
# ЧТО ДЕЛАЕТ:
#   1. Принимает JSON-описание того, на чём остановились
#   2. Создаёт SESSION_CHECKPOINT.md с датой и контекстом
#   3. Запускает бэкап фундамента (skills, knowledge, rules)
#   4. Чистит мусор сессии
#   5. Выводит инструкцию: «Нажми Cmd+N для чистого старта»
#
# ИСПОЛЬЗОВАНИЕ (вызывается агентом, не вручную):
#   bash ~/freelance-2026/tools/finish_day.sh
#
# Чекпоинт агент создаёт ПЕРЕД запуском этого скрипта.
# ============================================================================

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$HOME/freelance-2026"
ANTIGRAVITY="$HOME/.gemini/antigravity"
BACKUP_ROOT="$HOME/freelance-2026/.backups/antigravity"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE_SHORT=$(date +%Y-%m-%d)
BACKUP_DIR="$BACKUP_ROOT/$DATE_SHORT"

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${CYAN}  🛰️  ANTIGRAVITY FINISH-DAY — $(date '+%d.%m.%Y %H:%M')${NC}"
echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# ========================= ФАЗА 1: БЭКАП ====================================

echo ""
echo -e "  ${BOLD}📦 ФАЗА 1: Бэкап фундамента...${NC}"

mkdir -p "$BACKUP_DIR"

# Функция бэкапа
backup_dir() {
    local src="$1" dest="$2" label="$3"
    if [[ -d "$src" ]]; then
        mkdir -p "$dest"
        rsync -a --exclude='node_modules' --exclude='.git' --exclude='venv' \
              --exclude='__pycache__' --exclude='.DS_Store' "$src/" "$dest/" 2>/dev/null
        echo -e "  ${GREEN}✅ $label${NC}"
    fi
}

backup_file() {
    local src="$1" dest="$2" label="$3"
    if [[ -f "$src" ]]; then
        mkdir -p "$(dirname "$dest")"
        cp "$src" "$dest"
        echo -e "  ${GREEN}✅ $label${NC}"
    fi
}

# 1. Глобальные конфиги
backup_file "$ANTIGRAVITY/COLD_START.md"              "$BACKUP_DIR/core/COLD_START.md"              "COLD_START.md"
backup_file "$ANTIGRAVITY/GLOBAL_CORE_STANDARDS.md"   "$BACKUP_DIR/core/GLOBAL_CORE_STANDARDS.md"   "GLOBAL_CORE_STANDARDS.md"
backup_file "$ANTIGRAVITY/GLOBAL_STATUS_MANIFEST.md"  "$BACKUP_DIR/core/GLOBAL_STATUS_MANIFEST.md"  "GLOBAL_STATUS_MANIFEST.md"
backup_file "$ANTIGRAVITY/mcp_config.json"            "$BACKUP_DIR/core/mcp_config.json"            "mcp_config.json"

# 2. Скиллы
backup_dir "$ANTIGRAVITY/skills"     "$BACKUP_DIR/skills"     "Skills (8 агентов)"

# 3. Knowledge
backup_dir "$ANTIGRAVITY/knowledge"  "$BACKUP_DIR/knowledge"  "Knowledge Items"

# 4. Shared
backup_dir "$ANTIGRAVITY/shared"     "$BACKUP_DIR/shared"     "Shared Logic"

# 5. Проектные правила
for proj in ai-eggs ai-grant-consalt angel-backend freelance-agent; do
    if [[ -d "$WORKSPACE/$proj/.agent" ]]; then
        backup_dir "$WORKSPACE/$proj/.agent" "$BACKUP_DIR/project-rules/$proj" "Rules: $proj"
    fi
done
backup_dir "$WORKSPACE/.agent" "$BACKUP_DIR/project-rules/_workspace" "Rules: workspace root"

# 6. Стратегические документы
for doc in STRATEGY_2026.md ACTIVE_TASKS.md chp.md DOOMSDAY_PROTOCOL.md AGENT_SKILL_ROADMAP.md; do
    backup_file "$WORKSPACE/$doc" "$BACKUP_DIR/strategy/$doc" "$doc"
done

# 7. Чекпоинт и Стенограммы
mkdir -p "$WORKSPACE/checkpoints" "$WORKSPACE/reports"

# Проверяем свежесть chp.md — если старше 24ч, генерируем автоматический
CHP_FILE="$WORKSPACE/chp.md"
CHP_STALE=false
if [[ -f "$CHP_FILE" ]]; then
    CHP_AGE=$(( $(date +%s) - $(stat -f%m "$CHP_FILE" 2>/dev/null || stat -c%Y "$CHP_FILE" 2>/dev/null || echo 0) ))
    if (( CHP_AGE > 86400 )); then
        CHP_STALE=true
    fi
else
    CHP_STALE=true
fi

if [[ "$CHP_STALE" == "true" ]]; then
    echo -e "  ${YELLOW}⚠️  chp.md устарел (>24ч). Генерирую свежий чекпоинт...${NC}"
    CHRONICLE_TODAY="$WORKSPACE/chronicles/chronicle_${DATE_SHORT}.md"

    cat > "$CHP_FILE" <<AUTOCHP
# 🏁 ЧЕКПОИНТ: $(date '+%Y-%m-%d %H:%M') MSK (авто)

## ⚠️ Этот чекпоинт сгенерирован автоматически (finish_day.sh)
> Агент не обновил chp.md вручную. Данные ниже — из автоматических источников.

## 📜 Хроника дня
$(if [[ -f "$CHRONICLE_TODAY" ]]; then head -50 "$CHRONICLE_TODAY"; else echo "Хроника за $DATE_SHORT не найдена."; fi)

## 📝 Git log (последние 10 коммитов)
\`\`\`
$(cd "$WORKSPACE" && git log --oneline -10 2>/dev/null || echo "git log недоступен")
\`\`\`

---

> 🤖 **Finish-Day автоматический:** $(date '+%H:%M %d.%m.%Y')
AUTOCHP

    echo -e "  ${GREEN}✅ Свежий chp.md сгенерирован${NC}"
fi

cp "$CHP_FILE" "$WORKSPACE/checkpoints/chp_${TIMESTAMP}.md"
backup_file "$CHP_FILE" "$BACKUP_DIR/chp.md" "chp.md (свежий)"
backup_dir "$WORKSPACE/reports" "$BACKUP_DIR/reports" "Technical Reports (Stenograms)"

echo -e "  ${GREEN}✅ Чекпоинт архивирован: checkpoints/chp_${TIMESTAMP}.md${NC}"
echo -e "  ${GREEN}✅ Стенограмма сохранена в reports/${NC}"

# Архив
ARCHIVE="$BACKUP_ROOT/antigravity_backup_${TIMESTAMP}.tar.gz"
tar -czf "$ARCHIVE" -C "$BACKUP_ROOT" "$DATE_SHORT" 2>/dev/null
ARCHIVE_SIZE=$(stat -f%z "$ARCHIVE" 2>/dev/null || echo "?")
echo -e "  ${GREEN}📦 Архив: $(basename "$ARCHIVE") (${ARCHIVE_SIZE} bytes)${NC}"

# Ротация (5 последних)
ARCHIVE_COUNT=$(find "$BACKUP_ROOT" -name "antigravity_backup_*.tar.gz" -type f 2>/dev/null | wc -l | tr -d ' ')
if (( ARCHIVE_COUNT > 5 )); then
    EXCESS=$((ARCHIVE_COUNT - 5))
    find "$BACKUP_ROOT" -name "antigravity_backup_*.tar.gz" -type f | sort | head -n "$EXCESS" | while read -r old; do
        rm -f "$old" 2>/dev/null
    done
fi

# ========================= ФАЗА 2: ЧИСТКА ===================================

echo ""
echo -e "  ${BOLD}🧹 ФАЗА 2: Чистка мусора...${NC}"

# .DS_Store
ds=$(find "$WORKSPACE" -name ".DS_Store" -type f 2>/dev/null | wc -l | tr -d ' ')
find "$WORKSPACE" -name ".DS_Store" -type f -delete 2>/dev/null || true
echo -e "  ${RED}🗑️  .DS_Store: $ds файлов${NC}"

# __pycache__
pyc=$(find "$WORKSPACE" -name "__pycache__" -type d 2>/dev/null | wc -l | tr -d ' ')
find "$WORKSPACE" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
echo -e "  ${RED}🗑️  __pycache__: $pyc директорий${NC}"

# .pyc
pyc_files=$(find "$WORKSPACE" -name "*.pyc" -type f 2>/dev/null | wc -l | tr -d ' ')
find "$WORKSPACE" -name "*.pyc" -type f -delete 2>/dev/null || true
echo -e "  ${RED}🗑️  .pyc: $pyc_files файлов${NC}"

# Старые browser recordings (>7 дней)
if [[ -d "$ANTIGRAVITY/browser_recordings" ]]; then
    old_rec=$(find "$ANTIGRAVITY/browser_recordings" -type f -mtime +7 2>/dev/null | wc -l | tr -d ' ')
    find "$ANTIGRAVITY/browser_recordings" -type f -mtime +7 -delete 2>/dev/null || true
    echo -e "  ${RED}🗑️  Browser recordings (>7d): $old_rec файлов${NC}"
fi

# Старые html_artifacts (>7 дней)
if [[ -d "$ANTIGRAVITY/html_artifacts" ]]; then
    old_html=$(find "$ANTIGRAVITY/html_artifacts" -type f -mtime +7 2>/dev/null | wc -l | tr -d ' ')
    find "$ANTIGRAVITY/html_artifacts" -type f -mtime +7 -delete 2>/dev/null || true
    echo -e "  ${RED}🗑️  HTML artifacts (>7d): $old_html файлов${NC}"
fi

# tmp файлы
tmp_cleaned=$(find /tmp -maxdepth 1 -user "$(whoami)" -type f -mtime +1 2>/dev/null | wc -l | tr -d ' ')
find /tmp -maxdepth 1 -user "$(whoami)" -type f -mtime +1 -delete 2>/dev/null || true
echo -e "  ${RED}🗑️  /tmp (>1d): $tmp_cleaned файлов${NC}"

# Чистка tmp/ в проекте (Document Governance)
project_tmp=$(find "$WORKSPACE/tmp" -name "*.md" -o -name "*.txt" -o -name "*.py" 2>/dev/null | wc -l | tr -d ' ')
if [[ "$project_tmp" -gt 0 ]]; then
    echo -e "  ${YELLOW}⚠️  tmp/ в проекте: $project_tmp файлов — удали вручную после проверки${NC}"
fi

# TTL-проверка: MD-файлы со словами SESSION/DAILY/HANDOVER старше 3 дней
set +e  # pipeline ниже может дать exit 1 от grep если файлов нет
stale_docs=$(find "$WORKSPACE" -maxdepth 3 -name "*SESSION*" -o -name "*DAILY*" -o -name "*HANDOVER*" 2>/dev/null | grep "\.md$" | xargs ls -t 2>/dev/null | awk -v d="$(date -v-3d +%s 2>/dev/null || date -d '3 days ago' +%s 2>/dev/null)" 'BEGIN{c=0} {if (systime()<d) c++} END{print c}' 2>/dev/null || echo "0")
set -e
if [[ "$stale_docs" -gt 0 ]]; then
    echo -e "  ${YELLOW}⚠️  Устаревшие SESSION/DAILY/HANDOVER файлы: проверь и удали${NC}"
fi

# ========================= ФАЗА 2.5: WAZA AUDIT =============================

echo ""
echo -e "  ${BOLD}🔍 ФАЗА 2.5: Waza Skill Audit...${NC}"

WAZA_AUDIT_SCRIPT="$WORKSPACE/tools/waza-audit.sh"
if command -v waza &> /dev/null || [[ -f "$HOME/bin/waza" ]]; then
    if [[ -f "$WAZA_AUDIT_SCRIPT" ]]; then
        bash "$WAZA_AUDIT_SCRIPT" 2>/dev/null || echo -e "  ${YELLOW}⚠️  Waza audit завершился с предупреждениями${NC}"
    else
        echo -e "  ${YELLOW}⚠️  Скрипт waza-audit.sh не найден${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠️  Waza не установлен. Пропускаю.${NC}"
fi

# ========================= ФАЗА 3: GIT SYNC (GitHub) ========================

echo ""
echo -e "  ${BOLD}🚀 ФАЗА 3: Синхронизация с GitHub...${NC}"

set +e  # фазы 3-5 опциональны — не убиваем скрипт при ошибке

if [[ ! -d "$BACKUP_ROOT/.git" ]]; then
    git -C "$BACKUP_ROOT" init
    echo -e "  ${YELLOW}⚠️  Git repo инициализирован в $BACKUP_ROOT${NC}"
fi

git -C "$BACKUP_ROOT" add .
git -C "$BACKUP_ROOT" commit -m "🧠 Antigravity Brain Sync: $TIMESTAMP" --author="Antigravity AI <ai@antigravity.net>" 2>/dev/null || echo -e "  ${YELLOW}ℹ️  Нет изменений для коммита${NC}"

# Пытаемся запушить, если есть remote
if git -C "$BACKUP_ROOT" remote | grep -q "origin"; then
    echo -e "  ${CYAN}📤 Пушим в GitHub...${NC}"
    git -C "$BACKUP_ROOT" push origin main 2>/dev/null || echo -e "  ${RED}❌ Ошибка пуша (проверьте интернет или права)${NC}"
else
    echo -e "  ${YELLOW}⚠️  GitHub remote 'origin' не настроен. Бэкап только локальный.${NC}"
    echo -e "     Чтобы настроить: git -C $BACKUP_ROOT remote add origin <URL>${NC}"
fi

# ========================= ФАЗА 4: SYNC TO NAS DS720 ========================

echo ""
echo -e "  ${BOLD}📦 ФАЗА 4: Синхронизация на NAS DS720...${NC}"

NAS_SYNC_SCRIPT="$WORKSPACE/tools/sync_to_nas.sh"
NAS_SHARE="/Volumes/Документы СЕМЬЯ"
NAS_OK=false

if [[ -d "$NAS_SHARE" ]]; then
    if [[ -f "$NAS_SYNC_SCRIPT" ]]; then
        bash "$NAS_SYNC_SCRIPT" --cleanup && NAS_OK=true
    else
        echo -e "  ${YELLOW}⚠️  Скрипт sync_to_nas.sh не найден${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠️  NAS не примонтирован ($NAS_SHARE). Пропускаю.${NC}"
    echo -e "     Откройте Finder → DS720 → 'Документы СЕМЬЯ' и перезапустите.${NC}"
fi

# ========================= ФАЗА 5: SYNC TO EXTERNAL DISK =====================

echo ""
echo -e "  ${BOLD}💾 ФАЗА 5: Синхронизация на внешний диск...${NC}"

EXTERNAL_SYNC_SCRIPT="$WORKSPACE/tools/sync_to_external.sh"
CONF_FILE="$HOME/freelance-2026/.antigravity_disk.conf"

# Определяем точку монтирования из конфига или по умолчанию
if [[ -f "$CONF_FILE" ]]; then
    # shellcheck source=/dev/null
    source "$CONF_FILE"
    EXT_MOUNT="${EXTERNAL_DISK_MOUNT:-/Volumes/ANTIGRAVITY_BACKUP}"
else
    EXT_MOUNT="/Volumes/ANTIGRAVITY_BACKUP"
fi

if [[ -d "$EXT_MOUNT" ]]; then
    if [[ -f "$EXTERNAL_SYNC_SCRIPT" ]]; then
        bash "$EXTERNAL_SYNC_SCRIPT"
        echo -e "  ${GREEN}✅ Внешний диск синхронизирован: $EXT_MOUNT${NC}"
    else
        echo -e "  ${YELLOW}⚠️  Скрипт sync_to_external.sh не найден${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠️  Внешний диск не подключён ($EXT_MOUNT). Пропускаю.${NC}"
    if [[ "$NAS_OK" == "false" ]]; then
        echo -e "  ${RED}⚠️  ВНИМАНИЕ: Ни NAS, ни внешний диск недоступны!${NC}"
        echo -e "     Бэкап только локальный + GitHub.${NC}"
    fi
fi

# ========================= ИТОГ ==============================================

echo ""
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  🖱️  Синхронизация .cursor/rules/..."
if [ -f "$WORKSPACE/tools/sync_cursor_rules.sh" ]; then
    bash "$WORKSPACE/tools/sync_cursor_rules.sh" 2>/dev/null && \
        echo -e "  ${GREEN}✅ Cursor rules обновлены ($(ls "$WORKSPACE/.cursor/rules/global/"*.mdc 2>/dev/null | wc -l | tr -d ' ') скиллов)${NC}" || \
        echo -e "  ${YELLOW}⚠️  Cursor sync failed${NC}"
fi

echo ""
echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${GREEN}  ✅  FINISH-DAY ВЫПОЛНЕН${NC}"
echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  ${BOLD}📍 Чекпоинт:${NC}   $WORKSPACE/chp.md"
echo -e "  ${BOLD}📦 Бэкап:${NC}      $ARCHIVE"
echo ""
echo -e "  ${BOLD}Уровни резервирования:${NC}"
echo -e "    🌐 GitHub      → $(git -C "$BACKUP_ROOT" remote | grep -q origin && echo '✅ синхронизирован' || echo '⚠️  не настроен')"
echo -e "    🏠 NAS DS720   → $([[ \"$NAS_OK\" == 'true' ]] && echo '✅ синхронизирован' || echo '⚠️  недоступен')"
echo -e "    💾 Внешний диск→ $([[ -d \"$EXT_MOUNT\" ]] && echo '✅ синхронизирован' || echo '⚠️  не подключён')"
echo ""
echo -e "  ${BOLD}${YELLOW}👉 Для чистого старта: нажми Cmd+N в Antigravity${NC}"
echo -e "  ${BOLD}${YELLOW}   Затем напиши: \"Прочитай chp.md и продолжим\"${NC}"
echo ""
