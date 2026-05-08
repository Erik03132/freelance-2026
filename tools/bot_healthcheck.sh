#!/bin/bash
# ============================================================
# 🏥 bot_healthcheck.sh — Пинг-мониторинг ботов Заботкиной
# ============================================================
# Cron: */15 * * * * (каждые 15 минут на VPS)
# Проверяет: PM2 + API + LLM каскад + рестарт-шторм
# При сбое: автоперезапуск + алерт в ТГ (heartbeat rules)
# ============================================================

# === КОНФИГ ===
TG_BOT_TOKEN=$(grep "ANGELOCHKA_BOT_TOKEN" /root/antigravity/ai-eggs/.env 2>/dev/null | cut -d= -f2)
TG_ADMIN_ID="176203333"
API_URL="http://localhost:5000"
LOG_FILE="/tmp/bot_healthcheck.log"
HOUR=$(TZ="Europe/Moscow" date +%H)
DATE=$(TZ="Europe/Moscow" date +%Y-%m-%d)
TIME=$(TZ="Europe/Moscow" date +%H:%M:%S)

# === ФУНКЦИИ ===
log() { echo "[$TIME] $1" >> "$LOG_FILE"; }
tg_alert() {
    local level="$1"
    local msg="$2"
    if [ "$level" = "CRITICAL" ] || ([ "$HOUR" -ge 7 ] && [ "$HOUR" -lt 22 ]); then
        curl -s -X POST "https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage" \
            -d "chat_id=${TG_ADMIN_ID}" \
            -d "text=${msg}" > /dev/null 2>&1
        log "📤 ТГ ($level): отправлено"
    else
        log "🤫 Тихие часы, подавлен"
    fi
}

FAILS=0
FIXES=0
REPORT=""

# === ПРОВЕРКА 1: PM2 процессы (через pm2 jlist — надёжный JSON) ===
log "🏥 Healthcheck"

for PROC in angela-bot angela-server angela-vk-bot angela-listener; do
    STATUS=$(pm2 jlist 2>/dev/null | python3 -c "
import sys, json
try:
    procs = json.load(sys.stdin)
    for p in procs:
        if p['name'] == '$PROC':
            print(p['pm2_env']['status'])
            break
    else:
        print('not_found')
except:
    print('error')
" 2>/dev/null)
    
    if [ "$STATUS" != "online" ]; then
        log "❌ $PROC: $STATUS → restart"
        pm2 restart "$PROC" > /dev/null 2>&1
        sleep 5
        NEW=$(pm2 jlist 2>/dev/null | python3 -c "
import sys, json
try:
    for p in json.load(sys.stdin):
        if p['name'] == '$PROC':
            print(p['pm2_env']['status']); break
except: print('error')
" 2>/dev/null)
        if [ "$NEW" = "online" ]; then
            log "✅ $PROC: fixed"
            FIXES=$((FIXES + 1))
            REPORT="${REPORT}
🔧 ${PROC}: упал → починен"
        else
            log "🔴 $PROC: DEAD"
            FAILS=$((FAILS + 1))
            REPORT="${REPORT}
🔴 ${PROC}: МЁРТВ!"
        fi
    else
        log "✅ $PROC: ok"
    fi
done

# === ПРОВЕРКА 2: API сайта ===
HTTP=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "${API_URL}/api/health" 2>/dev/null || echo "000")
if [ "$HTTP" != "200" ]; then
    log "❌ API: HTTP $HTTP → restart"
    pm2 restart angela-server > /dev/null 2>&1
    sleep 8
    HTTP2=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "${API_URL}/api/health" 2>/dev/null || echo "000")
    if [ "$HTTP2" = "200" ]; then
        FIXES=$((FIXES + 1))
        REPORT="${REPORT}
🔧 API: ${HTTP} → 200"
    else
        FAILS=$((FAILS + 1))
        REPORT="${REPORT}
🔴 API: МЁРТВ (HTTP ${HTTP2})"
    fi
else
    log "✅ API: 200"
fi

# === ПРОВЕРКА 3: LLM каскад (раз в час) ===
MIN=$(TZ="Europe/Moscow" date +%M)
if [ "$MIN" -lt 16 ]; then
    RESP=$(curl -s --connect-timeout 15 --max-time 60 -X POST "${API_URL}/api/chat" \
        -H "Content-Type: application/json" \
        -d '{"message": "пинг", "session_id": "healthcheck"}' 2>/dev/null || echo "")
    
    if echo "$RESP" | grep -q "технические неполадки"; then
        log "⚠️ LLM каскад: ВСЕ модели мертвы"
        FAILS=$((FAILS + 1))
        REPORT="${REPORT}
⚠️ LLM: все модели отказали!"
    elif echo "$RESP" | grep -q "response"; then
        log "✅ LLM: отвечает"
    else
        log "⚠️ LLM: нет ответа"
    fi
fi

# === ПРОВЕРКА 4: Рестарт-шторм ===
for PROC in angela-bot angela-server angela-vk-bot; do
    RESTARTS=$(pm2 jlist 2>/dev/null | python3 -c "
import sys, json
try:
    for p in json.load(sys.stdin):
        if p['name'] == '$PROC':
            print(p['pm2_env'].get('restart_time', 0)); break
except: print(0)
" 2>/dev/null)
    if [ -n "$RESTARTS" ] && [ "$RESTARTS" -gt 25 ]; then
        log "🔴 $PROC: $RESTARTS рестартов!"
        FAILS=$((FAILS + 1))
        REPORT="${REPORT}
🔴 ${PROC}: ${RESTARTS} рестартов (шторм)!"
    fi
done

# === ИТОГ ===
if [ "$FAILS" -gt 0 ]; then
    tg_alert "CRITICAL" "🔴 HEALTHCHECK FAIL ($DATE $TIME)
${REPORT}
Сбоев: $FAILS | Починок: $FIXES"
elif [ "$FIXES" -gt 0 ]; then
    tg_alert "WARNING" "🔧 HEALTHCHECK ($DATE $TIME)
${REPORT}
Автофикс: $FIXES"
else
    log "✅ Все ок"
fi

log "--- done: fails=$FAILS fixes=$FIXES ---"
