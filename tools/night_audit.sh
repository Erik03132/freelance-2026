#!/bin/bash
# ============================================================
# 🌙 night_audit.sh — Ночной код-аудитор Antigravity v2
# ============================================================
# ПРИНЦИП: Cross-Model Peer Review
#   Код пишет Gemini 2.5 Pro → Проверяет Claude (через OpenRouter)
#   Два профессора из разных школ = максимум найденных багов
#
# Архитектура:
#   Фаза 1: ruff + секреты + git diff (машина, 100% точность)
#   Фаза 2: Gemini CLI 2.5 Pro — глубокий аудит (бесплатно)
#   Фаза 3: Claude через OpenRouter — cross-model ревью
#   Fallback: Gemma 4 через Ollama (если нет интернета)
#
# Использование:
#   bash tools/night_audit.sh                     # ai-eggs, только отчёт
#   bash tools/night_audit.sh --project vezemcip  # сайт vezemcip
#   bash tools/night_audit.sh --fix               # авто-исправление в ветке
#   bash tools/night_audit.sh --phase1-only       # только ruff, без AI
#
# Запуск: crontab → 02:00 каждую ночь
# Или вручную: bash tools/night_audit.sh [--phase1-only] [--no-tg]
# ============================================================

set -eu

# PATH для cron-окружения
export PATH="/usr/local/bin:/opt/homebrew/bin:/Users/igorvasin/.npm-global/bin:/Users/igorvasin/Library/Python/3.13/bin:$PATH"

# ============ КОНФИГУРАЦИЯ ============

PROJECT_ROOT="/Users/igorvasin/freelance-2026"
AI_EGGS_DIR="${PROJECT_ROOT}/ai-eggs"
REPORTS_DIR="${PROJECT_ROOT}/reports"

DATE=$(date +%Y-%m-%d)
TIME_START=$(date +%H:%M:%S)
LOG_FILE="/tmp/night_audit_${DATE}.log"

# Telegram
TG_BOT_TOKEN=$(grep "ANGELOCHKA_BOT_TOKEN" "${AI_EGGS_DIR}/.env" 2>/dev/null | cut -d= -f2)
TG_ADMIN_ID="176203333"
TG_PROXY=$(grep "TELEGRAM_PROXY" "${AI_EGGS_DIR}/.env" 2>/dev/null | cut -d= -f2 || echo "")

# API ключи
OPENROUTER_KEY=$(grep "OPENROUTER_API_KEY" "${AI_EGGS_DIR}/.env" 2>/dev/null | cut -d= -f2)

# Модели
GEMINI_CLI=$(which gemini 2>/dev/null || echo "")
OLLAMA_MODEL="gemma4:e2b"  # Fallback только

# Флаги запуска
PHASE1_ONLY=false
NO_TG=false
AUTO_FIX=false
TARGET_PROJECT="ai-eggs"  # По умолчанию

for arg in "$@"; do
    case $arg in
        --phase1-only) PHASE1_ONLY=true ;;
        --no-tg) NO_TG=true ;;
        --fix) AUTO_FIX=true ;;
        --project=*) TARGET_PROJECT="${arg#*=}" ;;
        --project) ;; # следующий аргумент
    esac
    # --project <name> (два аргумента)
    if [ "${prev_arg:-}" = "--project" ]; then
        TARGET_PROJECT="$arg"
    fi
    prev_arg="$arg"
done

# Определяем директорию проекта для аудита
case $TARGET_PROJECT in
    ai-eggs|eggs)
        AUDIT_DIR="${AI_EGGS_DIR}/agent"
        AUDIT_NAME="AI-Eggs (Анжелочка)"
        ;;
    vezemcip|site)
        AUDIT_DIR="${PROJECT_ROOT}/vezemcip"
        AUDIT_NAME="VezemCip (сайт)"
        ;;
    mustai)
        AUDIT_DIR="${PROJECT_ROOT}/mustai"
        AUDIT_NAME="Mustai (сенатор)"
        ;;
    all)
        AUDIT_DIR="${PROJECT_ROOT}"
        AUDIT_NAME="Весь проект"
        ;;
    *)
        AUDIT_DIR="${PROJECT_ROOT}/${TARGET_PROJECT}"
        AUDIT_NAME="${TARGET_PROJECT}"
        ;;
esac

REPORT_FILE="${REPORTS_DIR}/night_audit_${TARGET_PROJECT}_${DATE}.md"

if [ ! -d "$AUDIT_DIR" ]; then
    echo "❌ Директория не найдена: $AUDIT_DIR"
    echo "Доступные проекты: ai-eggs, vezemcip, mustai, all"
    exit 1
fi

# ============ УТИЛИТЫ ============

log() {
    local msg="[$(date '+%H:%M:%S')] $1"
    echo "$msg" | tee -a "$LOG_FILE"
}

send_telegram() {
    [ "$NO_TG" = true ] && return
    local text="$1"
    if [ -n "$TG_BOT_TOKEN" ]; then
        # Попытка 1: с прокси (5с connect, 15с total)
        if [ -n "${TG_PROXY:-}" ]; then
            curl -s --connect-timeout 5 --max-time 15 --proxy "${TG_PROXY}" -X POST \
                "https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage" \
                -d "chat_id=${TG_ADMIN_ID}" \
                -d "text=${text}" \
                -d "parse_mode=Markdown" \
                > /dev/null 2>&1 && return || true
        fi
        # Попытка 2: напрямую (5с connect, 15с total)
        curl -s --connect-timeout 5 --max-time 15 -X POST \
            "https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage" \
            -d "chat_id=${TG_ADMIN_ID}" \
            -d "text=${text}" \
            -d "parse_mode=Markdown" \
            > /dev/null 2>&1 || true
    fi
}

# Вызов Claude через OpenRouter API
call_claude() {
    local prompt="$1"
    local max_tokens="${2:-4096}"
    
    if [ -z "$OPENROUTER_KEY" ]; then
        echo "❌ OPENROUTER_API_KEY не найден"
        return 1
    fi
    
    # Экранируем prompt для JSON
    local escaped_prompt
    escaped_prompt=$(echo "$prompt" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))")
    
    local response
    response=$(curl -s --max-time 120 \
        -H "Authorization: Bearer ${OPENROUTER_KEY}" \
        -H "Content-Type: application/json" \
        -H "HTTP-Referer: https://antigravity.local" \
        -d "{
            \"model\": \"anthropic/claude-sonnet-4\",
            \"max_tokens\": ${max_tokens},
            \"messages\": [{\"role\": \"user\", \"content\": ${escaped_prompt}}]
        }" \
        "https://openrouter.ai/api/v1/chat/completions" 2>/dev/null)
    
    # Извлекаем текст ответа
    echo "$response" | python3 -c "
import sys, json
try:
    r = json.load(sys.stdin)
    print(r['choices'][0]['message']['content'])
except Exception as e:
    print(f'❌ Ошибка Claude API: {e}')
" 2>/dev/null
}

# ============ ИНИЦИАЛИЗАЦИЯ ============

mkdir -p "$REPORTS_DIR"
: > "$LOG_FILE"

log "🌙 Ночной аудит v2 стартовал: ${DATE} ${TIME_START}"
log "📁 Проект: ${AUDIT_NAME} (${AUDIT_DIR})"
log "🔧 Режим: $([ "$AUTO_FIX" = true ] && echo 'AUTO-FIX' || echo 'АУДИТ')"

# Подсчёт файлов
TOTAL_PY=$(find "$AUDIT_DIR" -name "*.py" \
    -not -path "*/venv/*" -not -path "*/.venv/*" \
    -not -path "*/node_modules/*" -not -path "*/__pycache__/*" \
    2>/dev/null | wc -l | tr -d ' ')

# Получаем дифф за день (КЛЮЧЕВОЕ — проверяем только ИЗМЕНЕНИЯ)
cd "$PROJECT_ROOT"
CHANGED_PY=$(git diff --name-only HEAD~1 2>/dev/null | grep '\.py$' || true)
if [ -z "$CHANGED_PY" ]; then
    CHANGED_COUNT=0
else
    CHANGED_COUNT=$(echo "$CHANGED_PY" | wc -l | tr -d ' ')
fi

# Если нет диффа — берём ТОП-5 критических файлов
if [ "$CHANGED_COUNT" -eq 0 ] || [ -z "$CHANGED_PY" ]; then
    CHANGED_PY="ai-eggs/agent/angelochka_core.py
ai-eggs/agent/tg_bot.py
ai-eggs/agent/bitrix_intelligence.py
ai-eggs/agent/chat_listener.py
ai-eggs/agent/bitrix_scanner.py"
    CHANGED_COUNT=5
    DIFF_SOURCE="ТОП-5 критических файлов (нет git diff)"
else
    DIFF_SOURCE="git diff HEAD~1 (${CHANGED_COUNT} файлов)"
fi

log "📊 Python: ${TOTAL_PY} всего, ${CHANGED_COUNT} изменено"

# ============ НАЧАЛО ОТЧЁТА ============

cat > "$REPORT_FILE" << EOF
# 🌙 Ночной аудит кода — ${DATE}

> **Проект:** ${AUDIT_NAME}  
> **Время:** ${TIME_START}  
> **Метод:** Cross-Model Peer Review  
> **Режим:** $([ "$AUTO_FIX" = true ] && echo '🔧 AUTO-FIX' || echo '📋 Только отчёт')  
> **Python файлов:** ${TOTAL_PY} (проверяем: ${CHANGED_COUNT})  
> **Источник:** ${DIFF_SOURCE}

---

EOF

# ============================================================
# ФАЗА 1: МАШИННЫЙ АНАЛИЗ (100% точность, 0% галлюцинаций)
# ============================================================

log "⚡ Фаза 1: Машинный анализ..."

echo "## ⚡ Фаза 1: Машинный анализ" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# --- 1a. ruff ---
RUFF_ERRORS=0
RUFF_FIXED=0
if command -v ruff &> /dev/null; then
    echo "### 🔍 ruff — lint" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    RUFF_OUTPUT=$(ruff check "$AUDIT_DIR" --select E,F,S,B --output-format concise 2>&1 || true)
    echo "$RUFF_OUTPUT" | head -50 >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    RUFF_ERRORS=$(echo "$RUFF_OUTPUT" | grep -oE 'Found [0-9]+' | head -1 | grep -oE '[0-9]+' || echo "0")
    [ -z "$RUFF_ERRORS" ] && RUFF_ERRORS=0

    # AUTO-FIX: ruff --fix (безопасные исправления)
    if [ "$AUTO_FIX" = true ] && [ "$RUFF_ERRORS" -gt 0 ]; then
        log "  🔧 ruff --fix: исправляю безопасные ошибки..."
        # Создаём ветку для исправлений
        cd "$PROJECT_ROOT"
        FIX_BRANCH="auto-fix/night-audit-${DATE}"
        git checkout -b "$FIX_BRANCH" 2>/dev/null || git checkout "$FIX_BRANCH" 2>/dev/null || true
        
        BEFORE=$RUFF_ERRORS
        ruff check "$AUDIT_DIR" --select E,F,I --fix 2>/dev/null || true
        AFTER_OUTPUT=$(ruff check "$AUDIT_DIR" --select E,F,S,B 2>&1 || true)
        AFTER=$(echo "$AFTER_OUTPUT" | grep -oE 'Found [0-9]+' | head -1 | grep -oE '[0-9]+' || echo "0")
        [ -z "$AFTER" ] && AFTER=0
        RUFF_FIXED=$((BEFORE - AFTER))
        
        if [ "$RUFF_FIXED" -gt 0 ]; then
            git add -A 2>/dev/null || true
            git commit -m "🤖 night-audit: ruff --fix (${RUFF_FIXED} исправлений)" 2>/dev/null || true
            log "  ✅ ruff исправил ${RUFF_FIXED} ошибок (ветка: ${FIX_BRANCH})"
        fi
        echo "" >> "$REPORT_FILE"
        echo "🔧 **ruff --fix:** ${RUFF_FIXED} ошибок исправлено автоматически (ветка: \'${FIX_BRANCH}\')" >> "$REPORT_FILE"
    fi

    echo "" >> "$REPORT_FILE"
    echo "**Критических ошибок ruff (E,F,S,B):** ${RUFF_ERRORS}" >> "$REPORT_FILE"
    log "  ruff: ${RUFF_ERRORS} ошибок"
else
    echo "⚠️ ruff не установлен" >> "$REPORT_FILE"
    # Fallback: py_compile
    SYNTAX_ERRORS=0
    while IFS= read -r pyfile; do
        [ -z "$pyfile" ] && continue
        result=$(python3 -m py_compile "$pyfile" 2>&1) || true
        if [ -n "$result" ]; then
            ((SYNTAX_ERRORS++)) || true
        fi
    done < <(find "$AGENT_DIR" -name "*.py" -not -path "*/__pycache__/*")
    RUFF_ERRORS=$SYNTAX_ERRORS
fi

# --- 1b. Hardcoded секреты ---
echo "" >> "$REPORT_FILE"
echo "### 🔐 Hardcoded секреты" >> "$REPORT_FILE"

SECRET_HITS=0
SECRET_DETAILS=""
while IFS= read -r pyfile; do
    [ -z "$pyfile" ] && continue
    hits=$(grep -nE "(api_key|secret|password|token)\s*=\s*['\"][a-zA-Z0-9]{20,}" "$pyfile" 2>/dev/null | \
           grep -v "os\.getenv\|os\.environ\|\.env\|#\s*\|example\|test\|mock" || true)
    if [ -n "$hits" ]; then
        SECRET_DETAILS+="⚠️ $(basename "$pyfile"): $hits\n"
        ((SECRET_HITS++)) || true
    fi
done < <(find "$AUDIT_DIR" -name "*.py" \
    -not -path "*/venv/*" -not -path "*/.venv/*" \
    -not -path "*/node_modules/*" -not -path "*/__pycache__/*")

if [ "$SECRET_HITS" -eq 0 ]; then
    echo "✅ Не найдено" >> "$REPORT_FILE"
else
    echo '```' >> "$REPORT_FILE"
    echo -e "$SECRET_DETAILS" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
fi
log "  Секреты: ${SECRET_HITS}"

# --- 1c. Git diff ---
echo "" >> "$REPORT_FILE"
echo "### 📝 Изменения за день" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
git diff --stat HEAD~1 2>/dev/null | tail -10 >> "$REPORT_FILE" || echo "Git недоступен" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
GIT_FILES_CHANGED=$(git diff --name-only HEAD~1 2>/dev/null | wc -l | tr -d ' ' || echo "0")

# --- 1d. Собираем дифф кода для AI-ревью ---
echo "" >> "$REPORT_FILE"

# Собираем РЕАЛЬНЫЙ дифф (только .py, до 8000 символов)
CODE_DIFF=$(git diff HEAD~1 -- '*.py' 2>/dev/null | head -400 || echo "")
if [ -z "$CODE_DIFF" ]; then
    # Если нет диффа — собираем содержимое ТОП файлов (урезанно)
    CODE_DIFF=""
    while IFS= read -r pyfile; do
        [ -z "$pyfile" ] && continue
        [ ! -f "$PROJECT_ROOT/$pyfile" ] && continue
        CODE_DIFF+="
=== FILE: ${pyfile} ===
$(head -100 "$PROJECT_ROOT/$pyfile")
--- (truncated) ---
"
    done <<< "$CHANGED_PY"
fi

# Обрезаем до 8000 символов (лимит контекста)
CODE_DIFF=$(echo "$CODE_DIFF" | head -300)

log "  Фаза 1 завершена"

# Если --phase1-only, пропускаем AI
if [ "$PHASE1_ONLY" = true ]; then
    log "  ⏭️ --phase1-only: пропускаем AI фазы"
    echo "---" >> "$REPORT_FILE"
    echo "⏭️ AI-фазы пропущены (--phase1-only)" >> "$REPORT_FILE"
    # Прыгаем к итогам
    GEMINI_FOUND=0
    CLAUDE_FOUND=0
else

# ============================================================
# ФАЗА 2: GEMINI CLI — ГЛУБОКИЙ АУДИТ (бесплатно)
# ============================================================

echo "---" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "## 🔬 Фаза 2: Gemini 2.5 Pro — Глубокий аудит" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

GEMINI_FOUND=0
if [ -n "$GEMINI_CLI" ]; then
    log "🔬 Фаза 2: Gemini CLI..."

    GEMINI_PROMPT="Ты — ночной код-аудитор проекта Antigravity (AI-агент для птицефабрики).

КОНТЕКСТ: Код писали Gemini 2.5 Pro и Claude Opus. Ты проверяешь их работу.

ИЗМЕНЁННЫЕ ФАЙЛЫ:
$(echo "$CHANGED_PY" | tr '\n' ', ')

ЗАДАЧА — проверь ТОЛЬКО изменённые файлы. Для каждого:
1. 🐛 БАГИ — реальные ошибки в логике (не стиль!)
2. 🔒 БЕЗОПАСНОСТЬ — утечки ключей, инъекции, незащищённые эндпоинты
3. ⚡ ПРОИЗВОДИТЕЛЬНОСТЬ — блокирующие вызовы в async, memory leaks, N+1
4. 🏗️ АРХИТЕКТУРА — мёртвый код, дубли, нарушения DRY
5. 💡 ТОП-3 РЕКОМЕНДАЦИИ — самые ценные улучшения

ФОРМАТ: Краткий markdown (не больше 100 строк).
$([ "$AUTO_FIX" = true ] && echo 'РЕЖИМ: Исправляй найденные баги прямо в файлах! Коммить каждое исправление.' || echo 'ПРАВИЛО: НЕ ИЗМЕНЯЙ файлы! Только читай и анализируй.')
Запиши результат в конец файла ${REPORT_FILE} (append)."

    GEMINI_MODE=$([ "$AUTO_FIX" = true ] && echo "yolo" || echo "auto_edit")
    timeout 600 "$GEMINI_CLI" \
        --prompt "$GEMINI_PROMPT" \
        --approval-mode "$GEMINI_MODE" \
        2>>"$LOG_FILE" && GEMINI_FOUND=1 || {
        log "  ⚠️ Gemini CLI: ошибка или таймаут"
        echo "⚠️ Gemini CLI недоступен — фаза пропущена" >> "$REPORT_FILE"
    }

    log "  Фаза 2 завершена (Gemini)"
else
    echo "⚠️ Gemini CLI не установлен — фаза пропущена" >> "$REPORT_FILE"
    log "  Фаза 2 пропущена (нет gemini)"
fi

# ============================================================
# ФАЗА 3: CLAUDE — CROSS-MODEL REVIEW (ключевая!)
# ============================================================

echo "" >> "$REPORT_FILE"
echo "---" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "## 🧠 Фаза 3: Claude — Cross-Model Peer Review" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

CLAUDE_FOUND=0
if [ -n "$OPENROUTER_KEY" ]; then
    log "🧠 Фаза 3: Claude cross-model review..."

    CLAUDE_PROMPT="Ты — независимый код-аудитор. Другой AI (Gemini) написал этот код. Твоя задача — найти ошибки, которые Gemini мог пропустить.

ПРОЕКТ: AI-агент «Анжелочка» для птицефабрики (Python, aiogram, Bitrix24 CRM, Ollama/Gemini API).
VPS: Timeweb, PM2, Node.js + Python.

ВОТ ДИФФ КОДА ЗА ДЕНЬ:

\`\`\`diff
${CODE_DIFF}
\`\`\`

ФОКУС (ищи именно это):
1. 🐛 Логические баги — неправильные условия, off-by-one, необработанные edge cases
2. 🔒 Безопасность — ключи в коде, path traversal, unsanitized input в SQL/API
3. ⚡ Async-проблемы — блокирующие вызовы в async, незакрытые соединения, race conditions
4. 🧟 Мёртвый код — импорты без использования, закомментированные блоки, TODO забытые
5. 💣 Потенциальные крэши — необработанные исключения, None.attribute, деление на 0

ФОРМАТ ОТВЕТА:
Для каждого найденного бага:
- **Файл:строка** — описание проблемы
- **Критичность:** 🔴 Критично / 🟡 Важно / 🟢 Минорно
- **Исправление:** конкретная рекомендация

Если код чист — честно скажи «✅ Код чист, серьёзных проблем не обнаружено».
НЕ ПРИДУМЫВАЙ проблемы если их нет. Только реальные."

    CLAUDE_RESPONSE=$(call_claude "$CLAUDE_PROMPT" 4096)

    if [ -n "$CLAUDE_RESPONSE" ] && ! echo "$CLAUDE_RESPONSE" | grep -q "❌ Ошибка"; then
        echo "$CLAUDE_RESPONSE" >> "$REPORT_FILE"
        CLAUDE_FOUND=1
        
        # Считаем найденные баги
        CLAUDE_CRITICAL=$(echo "$CLAUDE_RESPONSE" | grep -c "🔴" || echo "0")
        CLAUDE_IMPORTANT=$(echo "$CLAUDE_RESPONSE" | grep -c "🟡" || echo "0")
        CLAUDE_MINOR=$(echo "$CLAUDE_RESPONSE" | grep -c "🟢" || echo "0")
        
        log "  Claude нашёл: 🔴${CLAUDE_CRITICAL} 🟡${CLAUDE_IMPORTANT} 🟢${CLAUDE_MINOR}"
    else
        echo "⚠️ Claude API недоступен: ${CLAUDE_RESPONSE}" >> "$REPORT_FILE"
        CLAUDE_CRITICAL=0; CLAUDE_IMPORTANT=0; CLAUDE_MINOR=0
        log "  ⚠️ Claude API ошибка"
        
        # === FALLBACK: Gemma 4 ===
        if command -v ollama &> /dev/null && ollama list 2>/dev/null | grep -q "$OLLAMA_MODEL"; then
            log "  🔄 Fallback: Gemma 4..."
            echo "" >> "$REPORT_FILE"
            echo "### 🔄 Fallback: Gemma 4 (локальная)" >> "$REPORT_FILE"
            
            GEMMA_PROMPT="Кратко проанализируй дифф Python-кода. Найди баги, проблемы безопасности, неоптимальный код. Ответь на русском, макс 30 строк.

\`\`\`diff
$(echo "$CODE_DIFF" | head -150)
\`\`\`"
            
            GEMMA_RESPONSE=$(timeout 180 ollama run "$OLLAMA_MODEL" "$GEMMA_PROMPT" 2>/dev/null || echo "⏰ Таймаут Gemma 4")
            echo "$GEMMA_RESPONSE" >> "$REPORT_FILE"
            log "  Fallback Gemma завершён"
        fi
    fi
else
    echo "⚠️ OPENROUTER_API_KEY не найден — Claude-ревью пропущено" >> "$REPORT_FILE"
    CLAUDE_CRITICAL=0; CLAUDE_IMPORTANT=0; CLAUDE_MINOR=0
    log "  Фаза 3 пропущена (нет ключа)"
fi

fi  # конец проверки --phase1-only

# ============================================================
# ИТОГОВЫЙ ОТЧЁТ
# ============================================================

TIME_END=$(date +%H:%M:%S)

echo "" >> "$REPORT_FILE"
echo "---" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
cat >> "$REPORT_FILE" << EOF
## 📋 Итоговая сводка

| Метрика | Значение |
|---------|----------|
| 📅 Дата | ${DATE} |
| ⏰ Время | ${TIME_START} → ${TIME_END} |
| 📁 Python файлов | ${TOTAL_PY} |
| 📝 Изменено за день | ${GIT_FILES_CHANGED:-0} |
| ⚡ ruff ошибок (E,F,S,B) | ${RUFF_ERRORS:-0} |
| 🔐 Hardcoded секретов | ${SECRET_HITS:-0} |
| 🔬 Gemini аудит | $([ "${GEMINI_FOUND:-0}" -eq 1 ] && echo "✅" || echo "⏭️") |
| 🧠 Claude cross-review | $([ "${CLAUDE_FOUND:-0}" -eq 1 ] && echo "✅" || echo "⏭️") |
| 🔴 Критичных (Claude) | ${CLAUDE_CRITICAL:-0} |
| 🟡 Важных (Claude) | ${CLAUDE_IMPORTANT:-0} |
| 🟢 Минорных (Claude) | ${CLAUDE_MINOR:-0} |

### Метод аудита
\`\`\`
Код писали: Gemini 2.5 Pro + Claude Opus (через Antigravity)
Проверяли:
  Фаза 1: ruff 0.15 (машина, 100% точность)
  Фаза 2: Gemini CLI 2.5 Pro (глубокий анализ, бесплатно)
  Фаза 3: Claude Sonnet 4 (cross-model review, OpenRouter)
  
Cross-Model Peer Review: два профессора из разных школ
проверяют код друг друга → максимум найденных багов
\`\`\`

---

> 🤖 Сгенерировано: \`tools/night_audit.sh v2\` — Cross-Model Peer Review
EOF

log "✅ Ночной аудит завершён: ${TIME_END}"
log "📄 Отчёт: ${REPORT_FILE}"

# ============ TELEGRAM ============

# Определяем критичность
TOTAL_ISSUES=$((${CLAUDE_CRITICAL:-0} + ${CLAUDE_IMPORTANT:-0}))
if [ "${SECRET_HITS:-0}" -gt 0 ]; then
    SEVERITY="🔴 КРИТИЧНО — hardcoded секреты!"
elif [ "${CLAUDE_CRITICAL:-0}" -gt 0 ]; then
    SEVERITY="🔴 Claude нашёл ${CLAUDE_CRITICAL} критичных багов!"
elif [ "${CLAUDE_IMPORTANT:-0}" -gt 0 ]; then
    SEVERITY="🟡 Claude нашёл ${CLAUDE_IMPORTANT} важных замечаний"
elif [ "${RUFF_ERRORS:-0}" -gt 20 ]; then
    SEVERITY="🟡 ruff: ${RUFF_ERRORS} ошибок"
else
    SEVERITY="🟢 Код чист"
fi

TG_MSG="🌙 *Ночной аудит — ${DATE}*

${SEVERITY}

📊 Результаты:
• ruff: ${RUFF_ERRORS:-0} ошибок
• Секретов: ${SECRET_HITS:-0}
• Gemini: $([ "${GEMINI_FOUND:-0}" -eq 1 ] && echo "✅" || echo "⏭️")
• Claude: 🔴${CLAUDE_CRITICAL:-0} 🟡${CLAUDE_IMPORTANT:-0} 🟢${CLAUDE_MINOR:-0}
• Файлов проверено: ${CHANGED_COUNT}

📄 \`reports/night_audit_${DATE}.md\`"

send_telegram "$TG_MSG"
log "📤 Telegram отправлен"

# Lock-файл для каскада: создаём на VPS, чтобы VPS fallback не дублировал
LOCK_FILE="/tmp/night_audit_done_${DATE}.lock"
touch "$LOCK_FILE"
# Отправляем lock на VPS
SSH_KEY="/Users/igorvasin/freelance-2026/.ssh_agent_key"
if [ -f "$SSH_KEY" ]; then
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no -o ConnectTimeout=5 \
        root@72.56.38.19 "touch $LOCK_FILE" 2>/dev/null || true
    log "🔒 Lock создан: локально + VPS"
else
    log "🔒 Lock создан: только локально (нет SSH ключа)"
fi
