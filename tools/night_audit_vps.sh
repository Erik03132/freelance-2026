#!/bin/bash
# ============================================================
# 🌙 night_audit_vps.sh — Ночной аудит (VPS fallback)
# ============================================================
# КАСКАД: Мак (02:00) → VPS (02:05, если Мак не сработал)
# Проверяет lock-файл: если Мак уже отправил аудит → не дублируем
#
# Запуск: crontab → 02:05 каждую ночь на VPS
# ============================================================

set -eu

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

# OpenRouter
OPENROUTER_KEY=$(grep "OPENROUTER_API_KEY" "${AI_EGGS_DIR}/.env" 2>/dev/null | cut -d= -f2 || echo "")

# ============ УТИЛИТЫ ============

log() {
    local msg="[$(date '+%H:%M:%S')] $1"
    echo "$msg" | tee -a "$LOG_FILE"
}

send_telegram() {
    local text="$1"
    if [ -n "$TG_BOT_TOKEN" ]; then
        local proxy_flag=""
        if [ -n "${TG_PROXY:-}" ]; then
            proxy_flag="--proxy ${TG_PROXY}"
        fi
        curl -s --max-time 15 $proxy_flag -X POST \
            "https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage" \
            -d "chat_id=${TG_ADMIN_ID}" \
            -d "text=${text}" \
            -d "parse_mode=Markdown" \
            > /dev/null 2>&1 || {
            # Retry without proxy
            curl -s --max-time 15 -X POST \
                "https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage" \
                -d "chat_id=${TG_ADMIN_ID}" \
                -d "text=${text}" \
                -d "parse_mode=Markdown" \
                > /dev/null 2>&1 || true
        }
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
while IFS= read -r pyfile; do
    [ -z "$pyfile" ] && continue
    hits=$(grep -nE "(api_key|secret|password|token)\s*=\s*['\"][a-zA-Z0-9]{20,}" "$pyfile" 2>/dev/null | \
           grep -v "os\.getenv\|os\.environ\|\.env\|#\s*\|example\|test\|mock" || true)
    if [ -n "$hits" ]; then
        ((SECRET_HITS++)) || true
    fi
done < <(find "$AGENT_DIR" -name "*.py" \
    -not -path "*/venv/*" -not -path "*/.venv/*" \
    -not -path "*/node_modules/*" -not -path "*/__pycache__/*")

log "  Секреты: ${SECRET_HITS}"

# ============ ФАЗА 2: Claude (через OpenRouter) ============

CLAUDE_CRITICAL=0
CLAUDE_IMPORTANT=0
CLAUDE_MINOR=0

if [ -n "$OPENROUTER_KEY" ]; then
    log "🧠 Фаза 2: Claude cross-review..."

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

    CLAUDE_PROMPT="Ты — ночной код-аудитор. Кратко проверь Python-код AI-агента для птицефабрики.

ФОКУС:
1. 🐛 Логические баги
2. 🔒 Безопасность (ключи, инъекции)
3. ⚡ Async-проблемы
4. 💣 Потенциальные крэши

\`\`\`python
${CODE_SAMPLE}
\`\`\`

Ответь КРАТКО (макс 30 строк). Для каждого бага: файл:строка, критичность (🔴/🟡/🟢), исправление.
Если код чист — скажи '✅ Код чист'."

    escaped_prompt=$(echo "$CLAUDE_PROMPT" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))")

    CLAUDE_RESPONSE=$(curl -s --max-time 120 \
        -H "Authorization: Bearer ${OPENROUTER_KEY}" \
        -H "Content-Type: application/json" \
        -d "{
            \"model\": \"anthropic/claude-sonnet-4\",
            \"max_tokens\": 2048,
            \"messages\": [{\"role\": \"user\", \"content\": ${escaped_prompt}}]
        }" \
        "https://openrouter.ai/api/v1/chat/completions" 2>/dev/null | \
        python3 -c "
import sys, json
try:
    r = json.load(sys.stdin)
    print(r['choices'][0]['message']['content'])
except Exception as e:
    print(f'❌ Ошибка Claude API: {e}')
" 2>/dev/null || echo "❌ Claude недоступен")

    if echo "$CLAUDE_RESPONSE" | grep -q "❌"; then
        log "  ⚠️ Claude API ошибка"
    else
        CLAUDE_CRITICAL=$(echo "$CLAUDE_RESPONSE" | grep -c "🔴" || echo "0")
        CLAUDE_IMPORTANT=$(echo "$CLAUDE_RESPONSE" | grep -c "🟡" || echo "0")
        CLAUDE_MINOR=$(echo "$CLAUDE_RESPONSE" | grep -c "🟢" || echo "0")
        log "  Claude: 🔴${CLAUDE_CRITICAL} 🟡${CLAUDE_IMPORTANT} 🟢${CLAUDE_MINOR}"
    fi
else
    log "  ⚠️ Нет OPENROUTER_KEY — Claude пропущен"
    CLAUDE_RESPONSE="⚠️ OPENROUTER_API_KEY не найден"
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

if [ "${SECRET_HITS:-0}" -gt 0 ]; then
    SEVERITY="🔴 КРИТИЧНО — hardcoded секреты!"
elif [ "${CLAUDE_CRITICAL:-0}" -gt 0 ]; then
    SEVERITY="🔴 Claude: ${CLAUDE_CRITICAL} критичных"
elif [ "${RUFF_ERRORS:-0}" -gt 20 ]; then
    SEVERITY="🟡 ruff: ${RUFF_ERRORS} ошибок"
else
    SEVERITY="🟢 Код чист"
fi

TG_MSG="🌙 *Ночной аудит (VPS)* — ${DATE}

${SEVERITY}

📊 ruff: ${RUFF_ERRORS} | секреты: ${SECRET_HITS}
🧠 Claude: 🔴${CLAUDE_CRITICAL} 🟡${CLAUDE_IMPORTANT} 🟢${CLAUDE_MINOR}
📁 Файлов: ${TOTAL_PY}

📄 \`reports/night_audit_vps_${DATE}.md\`"

send_telegram "$TG_MSG"
log "📤 TG отправлен"

# Lock — чтобы при повторном запуске не дублировать
touch "$LOCK_FILE"

TIME_END=$(date +%H:%M:%S)
log "✅ VPS аудит завершён: ${TIME_END}"
