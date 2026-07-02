#!/bin/bash
# ============================================================
# 🌙 night_audit_vps.sh — Ночной аудит (VPS fallback)
# ============================================================
# КАСКАД: Мак (02:00) → VPS (02:05, если Мак не сработал)
# Проверяет lock-файл: если Мак уже отправил аудит → не дублируем
#
# Запуск: crontab → 02:05 каждую ночь на VPS
# ============================================================

set -e

# ============ КОНФИГУРАЦИЯ ============

PROJECT_ROOT="/root/antigravity"
AI_EGGS_DIR="${PROJECT_ROOT}/ai-eggs"
AGENT_DIR="${AI_EGGS_DIR}/agent"
REPORTS_DIR="${PROJECT_ROOT}/reports"

DATE=$(TZ="Europe/Moscow" date +%Y-%m-%d)
TIME_START=$(TZ="Europe/Moscow" date +%H:%M:%S)
LOG_FILE="/tmp/night_audit_vps_${DATE}.log"
REPORT_FILE="${REPORTS_DIR}/night_audit_vps_${DATE}.md"
LOCK_FILE="/tmp/night_audit_done_${DATE}.lock"

# Telegram
TG_BOT_TOKEN=$(grep "ANGELOCHKA_BOT_TOKEN" "${AI_EGGS_DIR}/.env" 2>/dev/null | cut -d= -f2)
TG_ADMIN_ID="176203333"
TG_PROXY=$(grep "TELEGRAM_PROXY" "${AI_EGGS_DIR}/.env" 2>/dev/null | cut -d= -f2 || echo "")

# OpenRouter мёртв с 09.05 — используем Gemini через прокси USA
# OPENROUTER_KEY не нужен

# ============ УТИЛИТЫ ============

log() {
    local msg="[$(date '+%H:%M:%S')] $1"
    echo "$msg" | tee -a "$LOG_FILE"
}

send_telegram() {
    local text="$1"
    if [ -n "$TG_BOT_TOKEN" ]; then
        # Попытка 1: прямое соединение (без прокси)
        local result
        result=$(curl -s --max-time 15 -X POST \
            "https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage" \
            -d "chat_id=${TG_ADMIN_ID}" \
            --data-urlencode "text=${text}" \
            -d "parse_mode=Markdown" 2>&1)
        
        if echo "$result" | grep -q '"ok":true'; then
            log "📤 TG отправлен"
            return 0
        fi
        
        # Попытка 2: через прокси
        if [ -n "${TG_PROXY:-}" ]; then
            result=$(curl -s --max-time 15 --proxy "${TG_PROXY}" -X POST \
                "https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage" \
                -d "chat_id=${TG_ADMIN_ID}" \
                --data-urlencode "text=${text}" \
                -d "parse_mode=Markdown" 2>&1)
            
            if echo "$result" | grep -q '"ok":true'; then
                log "📤 TG отправлен (через прокси)"
                return 0
            fi
        fi
        
        # Попытка 3: без Markdown (на случай спецсимволов)
        result=$(curl -s --max-time 15 -X POST \
            "https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage" \
            -d "chat_id=${TG_ADMIN_ID}" \
            --data-urlencode "text=${text}" 2>&1)
        
        if echo "$result" | grep -q '"ok":true'; then
            log "📤 TG отправлен (без Markdown)"
            return 0
        fi
        
        log "⚠️ TG отправка не удалась: $result"
    fi
}

# ============ ПРОВЕРКА: Мак уже сделал аудит? ============

# Проверяем — если в TG уже пришло сообщение с аудитом за сегодня
# (простая проверка по lock-файлу, Мак создаёт его при успешной отправке)
if [ -f "$LOCK_FILE" ]; then
    log "⏭️ Мак уже выполнил аудит за ${DATE} — пропускаем"
    exit 0
fi

# ============ ИНИЦИАЛИЗАЦИЯ ============

mkdir -p "$REPORTS_DIR"
: > "$LOG_FILE"

log "🌙 VPS Fallback аудит стартовал: ${DATE} ${TIME_START}"

# Проверяем наличие директории
if [ ! -d "$AGENT_DIR" ]; then
    log "❌ Директория не найдена: $AGENT_DIR"
    send_telegram "🌙 ❌ *VPS Ночной аудит — ${DATE}*
Директория ${AGENT_DIR} не найдена!"
    exit 1
fi

# Подсчёт файлов
TOTAL_PY=$(find "$AGENT_DIR" -name "*.py" \
    -not -path "*/venv/*" -not -path "*/.venv/*" \
    -not -path "*/node_modules/*" -not -path "*/__pycache__/*" \
    2>/dev/null | wc -l | tr -d ' ')

# ============ ФАЗА 1: RUFF ============

log "⚡ Фаза 1: ruff..."

RUFF_ERRORS=0
RUFF_OUTPUT=""
if command -v ruff &> /dev/null; then
    RUFF_OUTPUT=$(ruff check "$AGENT_DIR" --select E,F,S,B --output-format concise 2>&1 || true)
    RUFF_ERRORS=$(echo "$RUFF_OUTPUT" | grep -oE 'Found [0-9]+' | head -1 | grep -oE '[0-9]+' || echo "0")
    [ -z "$RUFF_ERRORS" ] && RUFF_ERRORS=0
    log "  ruff: ${RUFF_ERRORS} ошибок"
else
    log "  ⚠️ ruff не установлен"
fi

# ============ ФАЗА 1b: СЕКРЕТЫ ============

SECRET_HITS=0
SECRET_FILES=""
while IFS= read -r pyfile; do
    [ -z "$pyfile" ] && continue
    hits=$(grep -nE "(api_key|secret|password|token|key)\s*=\s*['\"][a-zA-Z0-9]{15,}" "$pyfile" 2>/dev/null | \
           grep -v "os\.getenv\|os\.environ\|\.env\|#\s*\|example\|test\|mock\|test_\|TEMPLATE\|SAMPLE" || true)
    if [ -n "$hits" ]; then
        ((SECRET_HITS++)) || true
        SECRET_FILES="${SECRET_FILES}
$pyfile:
$hits"
    fi
done < <(find "$AGENT_DIR" -name "*.py" \
    -not -path "*/venv/*" -not -path "*/.venv/*" \
    -not -path "*/node_modules/*" -not -path "*/__pycache__/*")

log "  Секреты: ${SECRET_HITS}"
if [ "$SECRET_HITS" -gt 0 ]; then
    log "  Файлы с секретами:${SECRET_FILES}"
fi

# ============ ФАЗА 1.5: Обучение Заботкиной ============
log "📚 Фаза 1.5: call_learner (обучение на звонках)..."
LEARNER_VENV="/root/antigravity/ai-eggs/venv/bin/python3"
LEARNER_SCRIPT="/root/antigravity/ai-eggs/agent/call_learner.py"
if [ -f "$LEARNER_SCRIPT" ]; then
    LEARNER_OUT=$(cd /root/antigravity/ai-eggs/agent && $LEARNER_VENV $LEARNER_SCRIPT --days 1 2>&1 | tail -5)
    LEARNER_FACTS=$(echo "$LEARNER_OUT" | grep -oP 'Фактов извлечено: \K[0-9]+' || echo "0")
    LEARNER_TRANSCRIPTS=$(echo "$LEARNER_OUT" | grep -oP 'Транскриптов обработано: \K[0-9]+' || echo "0")
    log "  📞 Транскриптов: $LEARNER_TRANSCRIPTS, фактов: $LEARNER_FACTS"
else
    log "  ⚠️ call_learner.py не найден"
    LEARNER_TRANSCRIPTS=0
    LEARNER_FACTS=0
fi

# ============ ФАЗА 2: Gemini code review (через прокси USA) ============

CLAUDE_CRITICAL=0
CLAUDE_IMPORTANT=0
CLAUDE_MINOR=0

GEMINI_KEY=$(grep "GEMINI_API_KEY" "${AI_EGGS_DIR}/.env" 2>/dev/null | head -1 | cut -d= -f2)
US_PROXY=$(grep "TELEGRAM_PROXY" "${AI_EGGS_DIR}/.env" 2>/dev/null | head -1 | cut -d= -f2 || echo "")

if [ -n "$GEMINI_KEY" ]; then
    log "🧠 Фаза 2: Gemini cross-review (через прокси USA)..."

    # Собираем ТОП-5 файлов для ревью
    TOP_FILES="angelochka_core.py tg_bot.py bitrix_intelligence.py chat_listener.py sales_logic.py"
    CODE_SAMPLE=""
    for f in $TOP_FILES; do
        fpath="${AGENT_DIR}/${f}"
        if [ -f "$fpath" ]; then
            CODE_SAMPLE+="
=== ${f} (first 60 lines) ===
$(head -60 "$fpath")
--- truncated ---
"
        fi
    done

    # Обрезаем
    CODE_SAMPLE=$(echo "$CODE_SAMPLE" | head -250)

    REVIEW_PROMPT="Ты — ночной код-аудитор. Кратко проверь Python-код AI-агента для птицефабрики.

ФОКУС:
1. Логические баги
2. Безопасность (ключи, инъекции)
3. Async-проблемы
4. Потенциальные крэши

\`\`\`python
${CODE_SAMPLE}
\`\`\`

Ответь КРАТКО (макс 30 строк). Для каждого бага: файл:строка, критичность (CRITICAL/IMPORTANT/MINOR), исправление.
Если код чист — скажи 'Код чист'."

    escaped_prompt=$(echo "$REVIEW_PROMPT" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))")

    CLAUDE_RESPONSE=$(curl -s --max-time 120 --proxy "${US_PROXY}" \
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${GEMINI_KEY}" \
        -H "Content-Type: application/json" \
        -d "{\"contents\":[{\"parts\":[{\"text\": ${escaped_prompt}}]}]}" 2>/dev/null | \
        python3 -c "
import sys, json
try:
    r = json.load(sys.stdin)
    print(r['candidates'][0]['content']['parts'][0]['text'])
except Exception as e:
    print(f'ERR Gemini API: {e}')
" 2>/dev/null || echo "ERR Gemini недоступен")

    if echo "$CLAUDE_RESPONSE" | grep -q "ERR"; then
        log "  ⚠️ Gemini API ошибка"
    else
        CLAUDE_CRITICAL=$(echo "$CLAUDE_RESPONSE" | grep -ci "critical" 2>/dev/null | head -1 || echo "0")
        CLAUDE_CRITICAL=$(echo "$CLAUDE_CRITICAL" | tr -d '[:space:]')
        CLAUDE_IMPORTANT=$(echo "$CLAUDE_RESPONSE" | grep -ci "important" 2>/dev/null | head -1 || echo "0")
        CLAUDE_IMPORTANT=$(echo "$CLAUDE_IMPORTANT" | tr -d '[:space:]')
        CLAUDE_MINOR=$(echo "$CLAUDE_RESPONSE" | grep -ci "minor" 2>/dev/null | head -1 || echo "0")
        CLAUDE_MINOR=$(echo "$CLAUDE_MINOR" | tr -d '[:space:]')
        [ -z "$CLAUDE_CRITICAL" ] && CLAUDE_CRITICAL=0
        [ -z "$CLAUDE_IMPORTANT" ] && CLAUDE_IMPORTANT=0
        [ -z "$CLAUDE_MINOR" ] && CLAUDE_MINOR=0
        log "  Gemini: 🔴${CLAUDE_CRITICAL} 🟡${CLAUDE_IMPORTANT} 🟢${CLAUDE_MINOR}"
    fi
else
    log "  ⚠️ Нет GEMINI_API_KEY — code review пропущен"
    CLAUDE_RESPONSE="⚠️ GEMINI_API_KEY не найден"
fi

# ============ ОТЧЁТ ============

cat > "$REPORT_FILE" << EOF
# 🌙 Ночной аудит (VPS Fallback) — ${DATE}

> **Время:** ${TIME_START}
> **Сервер:** VPS Timeweb (72.56.38.19)
> **Python файлов:** ${TOTAL_PY}

## ⚡ Фаза 1: ruff
\`\`\`
$(echo "$RUFF_OUTPUT" | head -30)
\`\`\`
**Ошибок ruff:** ${RUFF_ERRORS}
**Секретов:** ${SECRET_HITS}

## 🧠 Фаза 2: Claude
${CLAUDE_RESPONSE}

## 📋 Итоги

| Метрика | Значение |
|---------|----------|
| ⚡ ruff | ${RUFF_ERRORS} |
| 🔐 Секреты | ${SECRET_HITS} |
| 🔴 Критичных | ${CLAUDE_CRITICAL} |
| 🟡 Важных | ${CLAUDE_IMPORTANT} |
| 🟢 Минорных | ${CLAUDE_MINOR} |

> 🤖 VPS Fallback — сработал потому что Мак не выполнил аудит в 02:00
EOF

log "📄 Отчёт: ${REPORT_FILE}"

# ============ TELEGRAM ============

set +e  # отключаем -e — integer comparisons дают false positives

_CC=${CLAUDE_CRITICAL:-0}; _CC=$(echo "$_CC" | tr -d '[:space:]')
[ -z "$_CC" ] && _CC=0
_RE=${RUFF_ERRORS:-0}; _RE=$(echo "$_RE" | tr -d '[:space:]')
[ -z "$_RE" ] && _RE=0
_SH=${SECRET_HITS:-0}; _SH=$(echo "$_SH" | tr -d '[:space:]')
[ -z "$_SH" ] && _SH=0

if [ "$_SH" -gt 0 ] 2>/dev/null; then
    SEVERITY="🔴 КРИТИЧНО — hardcoded секреты!"
elif [ "$_CC" -gt 0 ] 2>/dev/null; then
    SEVERITY="🔴 Gemini: ${CLAUDE_CRITICAL} критичных"
elif [ "$_RE" -gt 20 ] 2>/dev/null; then
    SEVERITY="🟡 ruff: ${RUFF_ERRORS} ошибок"
else
    SEVERITY="🟢 Код чист"
fi

TG_MSG="🌙 *Ночной аудит (VPS)* — ${DATE}

${SEVERITY}

📊 ruff: ${RUFF_ERRORS} | секреты: ${SECRET_HITS}
🧠 Claude: 🔴${CLAUDE_CRITICAL} 🟡${CLAUDE_IMPORTANT} 🟢${CLAUDE_MINOR}
📁 Файлов: ${TOTAL_PY}
📚 Обучение: ${LEARNER_TRANSCRIPTS:-0} звонков, ${LEARNER_FACTS:-0} фактов

📄 \`reports/night_audit_vps_${DATE}.md\`"

send_telegram "$TG_MSG"
log "📤 TG отправлен"

# Lock — чтобы при повторном запуске не дублировать
touch "$LOCK_FILE"

TIME_END=$(date +%H:%M:%S)
log "✅ VPS аудит завершён: ${TIME_END}"
