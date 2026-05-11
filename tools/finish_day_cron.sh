#!/bin/bash
# ============================================================
# 🌙 finish_day_cron.sh — Автоматический finish-day для cron
# ============================================================
# Обёртка над finish_day.sh для безопасного запуска из crontab.
#
# Отличия от интерактивного запуска:
#   - Не падает при отсутствии NAS/внешнего диска
#   - Логирует в файл, а не в stdout
#   - Отправляет TG-уведомление о результате
#   - Блокировка повторного запуска (lock-файл)
#
# Crontab: 0 23 * * * bash ~/freelance-2026/tools/finish_day_cron.sh
# ============================================================

WORKSPACE="$HOME/freelance-2026"
LOG_FILE="/tmp/finish_day_cron_$(date +%Y-%m-%d).log"
LOCK_FILE="/tmp/finish_day_$(date +%Y-%m-%d).lock"
DATE=$(date +%Y-%m-%d)
TIME_START=$(date +%H:%M:%S)

# TG конфиг (берём из .env)
if [ -f "$WORKSPACE/ai-eggs/.env" ]; then
    TG_TOKEN=$(grep "^ANGELOCHKA_BOT_TOKEN=" "$WORKSPACE/ai-eggs/.env" | cut -d= -f2 | tr -d '"' | tr -d "'")
    TG_ADMIN=$(grep "^OWNER_CHAT_ID=" "$WORKSPACE/ai-eggs/.env" | cut -d= -f2 | tr -d '"' | tr -d "'" 2>/dev/null || echo "176203333")
    [ -z "$TG_ADMIN" ] && TG_ADMIN="176203333"
fi

log() {
    echo "[$(date +%H:%M:%S)] $*" >> "$LOG_FILE"
}

send_tg() {
    local text="$1"
    if [ -n "${TG_TOKEN:-}" ]; then
        curl -s --max-time 10 -X POST \
            "https://api.telegram.org/bot${TG_TOKEN}/sendMessage" \
            -d "chat_id=${TG_ADMIN}" \
            --data-urlencode "text=${text}" \
            -d "parse_mode=Markdown" > /dev/null 2>&1 || true
    fi
}

# === LOCK ===
if [ -f "$LOCK_FILE" ]; then
    log "⚠️ Уже выполнялся сегодня. Пропускаю."
    exit 0
fi

log "🌙 finish_day_cron стартовал: $DATE $TIME_START"

# === ОСНОВНОЙ СКРИПТ ===
ERRORS=0
PHASES_OK=""

# Фаза 1: Бэкап
log "📦 Фаза 1: Бэкап фундамента..."
if bash "$WORKSPACE/tools/finish_day.sh" >> "$LOG_FILE" 2>&1; then
    PHASES_OK="бэкап✅ чистка✅ git✅"
    log "✅ finish_day.sh завершён успешно"
else
    EXIT_CODE=$?
    ERRORS=$((ERRORS + 1))
    PHASES_OK="finish_day: exit $EXIT_CODE"
    log "⚠️ finish_day.sh завершён с кодом $EXIT_CODE"
fi

# Фаза 2: Дополнительная очистка url_cache (> 24ч)
if [ -f "$WORKSPACE/tools/url_to_markdown.py" ]; then
    python3 "$WORKSPACE/tools/url_to_markdown.py" --clean-cache >> "$LOG_FILE" 2>&1 || true
    log "🧹 url_cache очищен"
fi

# Фаза 3: Ротация хроник (оставляем 30 последних)
CHRONICLE_COUNT=$(find "$WORKSPACE/chronicles" -name "chronicle_*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
if [ "$CHRONICLE_COUNT" -gt 30 ]; then
    EXCESS=$((CHRONICLE_COUNT - 30))
    find "$WORKSPACE/chronicles" -name "chronicle_*.md" -type f | sort | head -n "$EXCESS" | while read -r old; do
        log "🗑️ Удалена старая хроника: $(basename "$old")"
        rm -f "$old" 2>/dev/null
    done
fi

# Фаза 4: Ротация старых lock-файлов
find /tmp -name "finish_day_*.lock" -mtime +7 -delete 2>/dev/null || true
find /tmp -name "night_audit_done_*.lock" -mtime +7 -delete 2>/dev/null || true
find /tmp -name "finish_day_cron_*.log" -mtime +7 -delete 2>/dev/null || true

# === LOCK И ОТЧЁТ ===
TIME_END=$(date +%H:%M:%S)
touch "$LOCK_FILE"

log "✅ finish_day_cron завершён: $TIME_END (ошибок: $ERRORS)"

# TG уведомление
if [ "$ERRORS" -eq 0 ]; then
    TG_ICON="🟢"
else
    TG_ICON="🟡"
fi

send_tg "🌙 *Finish-Day (cron)* — $DATE

$TG_ICON $PHASES_OK

📜 Хроник: $CHRONICLE_COUNT
🕐 $TIME_START → $TIME_END

📄 \`/tmp/finish_day_cron_${DATE}.log\`"

log "📤 TG отправлен"
