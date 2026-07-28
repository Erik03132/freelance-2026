#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# 🌙 morning_dream.sh — Dreaming-Lite (вдохновлено Claude Managed Agents)
# ═══════════════════════════════════════════════════════════════
#
# Анализирует хроники за последние N дней, извлекает паттерны:
#   - Повторяющиеся ошибки (чтобы не наступать повторно)
#   - Рабочие воркфлоу (что реально работает)
#   - Навыки, которые прокачались
#   - Блокеры и незавершённые задачи
#   - Инсайты для обновления контекста
#
# Результат: dream-файл + обновление patterns.md
#
# Использование:
#   bash tools/morning_dream.sh             # анализ за 3 дня (default)
#   bash tools/morning_dream.sh --days 7    # анализ за неделю
#   bash tools/morning_dream.sh --no-tg     # без уведомления в ТГ
#   bash tools/morning_dream.sh --dry-run   # только вывод, без записи
#
# Cron (каждое утро в 07:00 MSK):
#   0 7 * * * TZ="Europe/Moscow" bash ~/freelance-2026/tools/morning_dream.sh
#
# ═══════════════════════════════════════════════════════════════

set -eu

# PATH для cron-окружения
export PATH="/usr/local/bin:/opt/homebrew/bin:/Users/igorvasin/.npm-global/bin:/Users/igorvasin/Library/Python/3.13/bin:$PATH"

# ============ КОНФИГУРАЦИЯ ============

PROJECT_ROOT="$HOME/freelance-2026"
CHRONICLES_DIR="${PROJECT_ROOT}/chronicles"
REPORTS_DIR="${PROJECT_ROOT}/reports"
DREAMS_DIR="${PROJECT_ROOT}/dreams"
AI_EGGS_DIR="${PROJECT_ROOT}/ai-eggs"
PATTERNS_FILE="${DREAMS_DIR}/patterns.md"

DATE=$(TZ="Europe/Moscow" date +%Y-%m-%d)
TIME_NOW=$(TZ="Europe/Moscow" date +%H:%M)

# Telegram
TG_BOT_TOKEN=$(grep "ANGELOCHKA_BOT_TOKEN" "${AI_EGGS_DIR}/.env" 2>/dev/null | cut -d= -f2 || echo "")
TG_ADMIN_ID="176203333"
TG_PROXY=$(grep "TELEGRAM_PROXY" "${AI_EGGS_DIR}/.env" 2>/dev/null | cut -d= -f2 || echo "")

# API
OPENROUTER_KEY=$(grep "OPENROUTER_API_KEY" "${AI_EGGS_DIR}/.env" 2>/dev/null | cut -d= -f2 || echo "")

# Флаги
DAYS=3
NO_TG=false
DRY_RUN=false

for arg in "$@"; do
    case $arg in
        --days) ;; # следующий аргумент
        --no-tg) NO_TG=true ;;
        --dry-run) DRY_RUN=true ;;
    esac
    if [ "${prev_arg:-}" = "--days" ]; then
        DAYS="$arg"
    fi
    prev_arg="$arg"
done

# ============ УТИЛИТЫ ============

log() {
    echo "[$(TZ='Europe/Moscow' date '+%H:%M:%S')] $1"
}

send_telegram() {
    [ "$NO_TG" = true ] && return
    local text="$1"
    if [ -n "$TG_BOT_TOKEN" ]; then
        if [ -n "${TG_PROXY:-}" ]; then
            curl -s --connect-timeout 5 --max-time 15 --proxy "${TG_PROXY}" -X POST \
                "https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage" \
                -d "chat_id=${TG_ADMIN_ID}" \
                -d "text=${text}" \
                -d "parse_mode=Markdown" \
                > /dev/null 2>&1 && return || true
        fi
        curl -s --connect-timeout 5 --max-time 15 -X POST \
            "https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage" \
            -d "chat_id=${TG_ADMIN_ID}" \
            -d "text=${text}" \
            -d "parse_mode=Markdown" \
            > /dev/null 2>&1 || true
    fi
}

# Вызов LLM через OpenRouter
call_llm() {
    local prompt="$1"
    local max_tokens="${2:-4096}"
    
    if [ -z "$OPENROUTER_KEY" ]; then
        log "❌ OPENROUTER_API_KEY не найден — fallback на локальный анализ"
        return 1
    fi
    
    local escaped_prompt
    escaped_prompt=$(echo "$prompt" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))")
    
    local response
    response=$(curl -s --max-time 120 \
        -H "Authorization: Bearer ${OPENROUTER_KEY}" \
        -H "Content-Type: application/json" \
        -H "HTTP-Referer: https://antigravity.local" \
        -d "{
            \"model\": \"deepseek/deepseek-chat\",
            \"max_tokens\": ${max_tokens},
            \"temperature\": 0.3,
            \"messages\": [{\"role\": \"user\", \"content\": ${escaped_prompt}}]
        }" \
        "https://openrouter.ai/api/v1/chat/completions" 2>/dev/null)
    
    echo "$response" | python3 -c "
import sys, json
try:
    r = json.load(sys.stdin)
    print(r['choices'][0]['message']['content'])
except Exception as e:
    print(f'❌ LLM API Error: {e}')
" 2>/dev/null
}

# ============ СБОР ХРОНИК ============

log "🌙 Morning Dream v1 — анализ за ${DAYS} дней"

mkdir -p "$DREAMS_DIR"

# Собираем хроники за N дней
CHRONICLES_CONTENT=""
CHRONICLE_COUNT=0
for i in $(seq 0 $((DAYS - 1))); do
    check_date=$(date -v-${i}d +%Y-%m-%d 2>/dev/null || date -d "-${i} days" +%Y-%m-%d 2>/dev/null)
    chronicle_file="${CHRONICLES_DIR}/chronicle_${check_date}.md"
    if [ -f "$chronicle_file" ]; then
        CHRONICLES_CONTENT+="
========== ХРОНИКА ${check_date} ==========
$(cat "$chronicle_file")

"
        ((CHRONICLE_COUNT++)) || true
    fi
done

# Собираем последние отчёты ночного аудита
AUDIT_CONTENT=""
for i in $(seq 0 $((DAYS - 1))); do
    check_date=$(date -v-${i}d +%Y-%m-%d 2>/dev/null || date -d "-${i} days" +%Y-%m-%d 2>/dev/null)
    for audit_file in "${REPORTS_DIR}"/night_audit_*_${check_date}.md; do
        if [ -f "$audit_file" ]; then
            AUDIT_CONTENT+="
=== АУДИТ ${check_date} ===
$(head -60 "$audit_file")
"
        fi
    done
done

# Читаем текущие паттерны (если есть)
EXISTING_PATTERNS=""
if [ -f "$PATTERNS_FILE" ]; then
    EXISTING_PATTERNS=$(cat "$PATTERNS_FILE")
fi

# Читаем текущий chp.md
CHP_CONTENT=""
if [ -f "${PROJECT_ROOT}/chp.md" ]; then
    CHP_CONTENT=$(cat "${PROJECT_ROOT}/chp.md")
fi

if [ "$CHRONICLE_COUNT" -eq 0 ]; then
    log "📭 Нет хроник за последние ${DAYS} дней — пропускаем"
    exit 0
fi

log "📚 Найдено хроник: ${CHRONICLE_COUNT}"

# ============ АНАЛИЗ (LLM) ============

DREAM_PROMPT="Ты — Dreaming Engine системы Antigravity. Твоя задача — проанализировать хроники работы за ${DAYS} дней и извлечь паттерны для самоулучшения агентов.

ХРОНИКИ:
${CHRONICLES_CONTENT}

НОЧНЫЕ АУДИТЫ:
${AUDIT_CONTENT}

ТЕКУЩИЕ ПАТТЕРНЫ (если есть — дополни, не перезаписывай):
${EXISTING_PATTERNS}

ТЕКУЩИЙ ЧЕКПОИНТ:
${CHP_CONTENT}

═══ ЗАДАНИЕ ═══

Проанализируй и создай структурированный отчёт:

## 1. 🔁 ПОВТОРЯЮЩИЕСЯ ОШИБКИ
Баги/проблемы, которые возникали БОЛЬШЕ ОДНОГО РАЗА. Для каждой:
- Описание
- Сколько раз встретилась
- Корневая причина
- Как предотвратить навсегда

## 2. ✅ РАБОЧИЕ ВОРКФЛОУ (что реально работает)
Паттерны работы, которые приносили результат:
- Описание
- Почему эффективно
- Как масштабировать

## 3. 📈 НАВЫКИ: что прокачалось
Компетенции, которые выросли за период.

## 4. 🚧 НЕЗАВЕРШЁННЫЕ ЗАДАЧИ
Задачи, которые упоминались но не были закрыты (перетекающие из дня в день).

## 5. 💡 ИНСАЙТЫ ДЛЯ КОНТЕКСТА
Ключевые выводы, которые НУЖНО добавить в chp.md или в правила агентов.
Формат: краткие, конкретные, actionable.

## 6. 📊 МЕТРИКИ ДНЯ (агрегат)
- Багов исправлено за период
- Фич создано
- Файлов изменено
- Критических инцидентов

═══ ПРАВИЛА ═══
- Только РЕАЛЬНЫЕ данные из хроник — никаких выдумок
- Конкретика: файлы, строки, имена, числа
- Если паттерн уже в ТЕКУЩИХ ПАТТЕРНАХ — обнови счётчик, не дублируй
- Ответ на русском языке
- Максимум 150 строк"

DREAM_RESULT=""
if call_llm "$DREAM_PROMPT" 4096 > /tmp/dream_result_${DATE}.md 2>/dev/null; then
    DREAM_RESULT=$(cat /tmp/dream_result_${DATE}.md)
    
    if echo "$DREAM_RESULT" | grep -q "❌"; then
        log "⚠️ LLM вернул ошибку, пробуем fallback..."
        DREAM_RESULT=""
    fi
fi

# Fallback: локальный анализ (grep-based)
if [ -z "$DREAM_RESULT" ]; then
    log "🔄 Fallback: локальный анализ..."
    
    BUGS_FIXED=$(echo "$CHRONICLES_CONTENT" | grep -ci "исправлен\|фикс\|баг\|fix\|bug\|починил" || echo "0")
    DEPLOYS=$(echo "$CHRONICLES_CONTENT" | grep -ci "деплой\|deploy\|pm2 restart\|задеплоен" || echo "0")
    CRITICAL=$(echo "$CHRONICLES_CONTENT" | grep -ci "критич\|critical\|🚨\|🔴" || echo "0")
    TESTS=$(echo "$CHRONICLES_CONTENT" | grep -ci "тест\|test\|✅" || echo "0")
    RECURRING_ISSUES=$(echo "$CHRONICLES_CONTENT" | grep -oiE "(OpenRouter|timezone|webhook|PM2|venv|rank.bm25|RAG|prompt|каскад)" | sort | uniq -c | sort -rn | head -10)
    
    DREAM_RESULT="# 🌙 Dream Report (fallback-mode) — ${DATE}

> Анализ за ${DAYS} дней (${CHRONICLE_COUNT} хроник)
> ⚠️ Локальный анализ (LLM недоступен)

## 📊 Агрегированные метрики
- Багов исправлено: ~${BUGS_FIXED}
- Деплоев: ~${DEPLOYS}
- Критических инцидентов: ~${CRITICAL}
- Тестов/проверок: ~${TESTS}

## 🔁 Частые темы (по упоминаниям)
\`\`\`
${RECURRING_ISSUES}
\`\`\`

## 🚧 Незавершённые задачи (grep: ⚠️/TODO/FIXME)
$(echo "$CHRONICLES_CONTENT" | grep -i "⚠️\|TODO\|FIXME\|нужен\|открыт\|не решен" | head -15)
"
fi

# ============ ЗАПИСЬ РЕЗУЛЬТАТОВ ============

DREAM_FILE="${DREAMS_DIR}/dream_${DATE}.md"

if [ "$DRY_RUN" = true ]; then
    log "📋 DRY RUN — вывод без записи:"
    echo ""
    echo "$DREAM_RESULT"
    exit 0
fi

# Dream report
cat > "$DREAM_FILE" << EOF
# 🌙 Dream Report — ${DATE}

> Сгенерировано: ${TIME_NOW} MSK
> Хроник проанализировано: ${CHRONICLE_COUNT} (за ${DAYS} дней)
> Метод: $([ -n "$OPENROUTER_KEY" ] && echo "DeepSeek LLM + паттерн-анализ" || echo "Локальный grep-анализ (LLM недоступен)")

---

${DREAM_RESULT}

---

> 🤖 Сгенерировано: \`tools/morning_dream.sh v1\` — Dreaming-Lite Engine
EOF

log "📝 Dream: ${DREAM_FILE}"

# ============ ОБНОВЛЕНИЕ patterns.md (кумулятивный файл) ============

# Добавляем новый dream в patterns.md (append с разделителем)
if [ ! -f "$PATTERNS_FILE" ]; then
    cat > "$PATTERNS_FILE" << 'HEADER'
# 🧠 Patterns — Кумулятивная память Antigravity

> Этот файл обновляется автоматически скриптом `morning_dream.sh`.
> Содержит извлечённые паттерны из хроник.
> Читается при boot (IRON_RULES) для быстрого восстановления контекста.

---

HEADER
fi

cat >> "$PATTERNS_FILE" << EOF

## 📅 Dream: ${DATE} (${CHRONICLE_COUNT} хроник, ${DAYS} дней)

$(echo "$DREAM_RESULT" | head -80)

---

EOF

log "📊 Patterns обновлён: ${PATTERNS_FILE}"

# ============ TELEGRAM ============

TG_MSG="🌙 *Morning Dream — ${DATE}*

📚 Хроник: ${CHRONICLE_COUNT} (за ${DAYS} дней)
📄 Отчёт: \`dreams/dream_${DATE}.md\`

$(echo "$DREAM_RESULT" | grep -E "^##|^-" | head -12)"

send_telegram "$TG_MSG"

log "✅ Dreaming завершён"
