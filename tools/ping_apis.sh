#!/bin/bash
# ============================================================
# 🔌 PING ALL APIs — Проверка доступности всех API каскадов
# Запуск: bash ~/freelance-2026/tools/ping_apis.sh
# 
# ЖЕЛЕЗНОЕ ПРАВИЛО: Все внешние запросы через US SOCKS5 прокси!
# Прокси берётся из ai-eggs/.env (HTTPS_PROXY)
# ============================================================

set +e  # Не падать при ошибках (grep может не найти ключ)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$ROOT_DIR/ai-eggs/.env"

# --- Загрузка .env ---
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Файл $ENV_FILE не найден!"
    exit 1
fi

# Парсим .env (без export, без комментариев)
PROXY=$(grep -E '^HTTPS_PROXY=' "$ENV_FILE" 2>/dev/null | head -1 | cut -d'=' -f2- || echo "")
GEMINI_KEY=$(grep -E '^GEMINI_API_KEY=' "$ENV_FILE" 2>/dev/null | head -1 | cut -d'=' -f2- || echo "")
OPENROUTER_KEY=$(grep -E '^OPENROUTER_API_KEY=' "$ENV_FILE" 2>/dev/null | head -1 | cut -d'=' -f2- || echo "")
TAVILY_KEY=$(grep -E '^TAVILY_API_KEY=' "$ENV_FILE" 2>/dev/null | head -1 | cut -d'=' -f2- || echo "")
PERPLEXITY_KEY=$(grep -E '^PERPLEXITY_API_KEY=' "$ENV_FILE" 2>/dev/null | head -1 | cut -d'=' -f2- || echo "")

if [ -z "$PROXY" ]; then
    echo "❌ HTTPS_PROXY не найден в $ENV_FILE!"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🔌 API PING — $(date '+%d.%m.%Y %H:%M:%S')"
echo "  🌐 Прокси: ${PROXY%%@*}@***"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

TOTAL=0
OK=0
FAIL=0

# Функция вывода результата
show_result() {
    local name="$1"
    local code="$2"
    local time="$3"
    
    TOTAL=$((TOTAL + 1))
    
    local status_icon
    case "$code" in
        200|201|202) status_icon="✅"; OK=$((OK + 1)) ;;
        401)         status_icon="🔑"; OK=$((OK + 1)) ;;
        403)         status_icon="🚫"; FAIL=$((FAIL + 1)) ;;
        000)         status_icon="💀"; FAIL=$((FAIL + 1)) ;;
        *)           status_icon="⚠️"; FAIL=$((FAIL + 1)) ;;
    esac
    
    printf "  %s %-20s  HTTP %-3s  (%ss)\n" "$status_icon" "$name" "$code" "$time"
}

show_skip() {
    local name="$1"
    local reason="$2"
    TOTAL=$((TOTAL + 1))
    printf "  ⏭️  %-20s  SKIP (%s)\n" "$name" "$reason"
}

# ============================================================
# 📡 LLM КАСКАД
# ============================================================
echo "  📡 LLM КАСКАД"
echo "  ─────────────────────────────────────────────"

# 1. OpenRouter
result=$(curl -s -o /dev/null -w "%{http_code}|%{time_total}" \
    --connect-timeout 10 --max-time 15 \
    --proxy "$PROXY" \
    "https://openrouter.ai/api/v1/models" 2>/dev/null || echo "000|0")
show_result "OpenRouter" "$(echo "$result" | cut -d'|' -f1)" "$(echo "$result" | cut -d'|' -f2)"

# 2. Gemini Direct
if [ -n "$GEMINI_KEY" ]; then
    result=$(curl -s -o /dev/null -w "%{http_code}|%{time_total}" \
        --connect-timeout 10 --max-time 15 \
        --proxy "$PROXY" \
        "https://generativelanguage.googleapis.com/v1beta/models?key=${GEMINI_KEY}" 2>/dev/null || echo "000|0")
    show_result "Gemini Direct" "$(echo "$result" | cut -d'|' -f1)" "$(echo "$result" | cut -d'|' -f2)"
else
    show_skip "Gemini Direct" "нет ключа"
fi

# 3. Ollama (локальный, без прокси)
result=$(curl -s -o /dev/null -w "%{http_code}|%{time_total}" \
    --connect-timeout 5 --max-time 10 \
    "http://localhost:11434/api/tags" 2>/dev/null || echo "000|0")
show_result "Ollama (local)" "$(echo "$result" | cut -d'|' -f1)" "$(echo "$result" | cut -d'|' -f2)"

echo ""

# ============================================================
# 🔍 ПОИСКОВЫЙ КАСКАД
# ============================================================
echo "  🔍 ПОИСКОВЫЙ КАСКАД"
echo "  ─────────────────────────────────────────────"

# 4. Tavily
if [ -n "$TAVILY_KEY" ]; then
    result=$(curl -s -o /dev/null -w "%{http_code}|%{time_total}" \
        --connect-timeout 10 --max-time 15 \
        --proxy "$PROXY" \
        -X POST \
        -H "Content-Type: application/json" \
        -d "{\"api_key\":\"${TAVILY_KEY}\",\"query\":\"ping\",\"max_results\":1}" \
        "https://api.tavily.com/search" 2>/dev/null || echo "000|0")
    show_result "Tavily" "$(echo "$result" | cut -d'|' -f1)" "$(echo "$result" | cut -d'|' -f2)"
else
    show_skip "Tavily" "нет ключа"
fi

# 5. Perplexity Sonar (через OpenRouter — обход квоты прямого API)
if [ -n "$OPENROUTER_KEY" ]; then
    result=$(curl -s -o /dev/null -w "%{http_code}|%{time_total}" \
        --connect-timeout 10 --max-time 15 \
        --proxy "$PROXY" \
        -X POST \
        -H "Authorization: Bearer ${OPENROUTER_KEY}" \
        -H "Content-Type: application/json" \
        -d '{"model":"perplexity/sonar","messages":[{"role":"user","content":"ping"}],"max_tokens":5}' \
        "https://openrouter.ai/api/v1/chat/completions" 2>/dev/null || echo "000|0")
    show_result "Perplexity (OR)" "$(echo "$result" | cut -d'|' -f1)" "$(echo "$result" | cut -d'|' -f2)"
else
    show_skip "Perplexity (OR)" "нет OpenRouter ключа"
fi

# 6. DuckDuckGo
result=$(curl -s -o /dev/null -w "%{http_code}|%{time_total}" \
    --connect-timeout 10 --max-time 15 \
    --proxy "$PROXY" \
    "https://api.duckduckgo.com/?q=test&format=json&no_html=1" 2>/dev/null || echo "000|0")
show_result "DuckDuckGo" "$(echo "$result" | cut -d'|' -f1)" "$(echo "$result" | cut -d'|' -f2)"

echo ""

# ============================================================
# 🖼️ ФОТО КАСКАД
# ============================================================
echo "  🖼️  ФОТО КАСКАД"
echo "  ─────────────────────────────────────────────"

# 7. Unsplash
result=$(curl -s -o /dev/null -w "%{http_code}|%{time_total}" \
    --connect-timeout 10 --max-time 15 \
    --proxy "$PROXY" \
    "https://api.unsplash.com/photos/random" 2>/dev/null || echo "000|0")
show_result "Unsplash" "$(echo "$result" | cut -d'|' -f1)" "$(echo "$result" | cut -d'|' -f2)"

# 8. Pexels
result=$(curl -s -o /dev/null -w "%{http_code}|%{time_total}" \
    --connect-timeout 10 --max-time 15 \
    --proxy "$PROXY" \
    "https://api.pexels.com/v1/search?query=test&per_page=1" 2>/dev/null || echo "000|0")
show_result "Pexels" "$(echo "$result" | cut -d'|' -f1)" "$(echo "$result" | cut -d'|' -f2)"

# 9. Pixabay
result=$(curl -s -o /dev/null -w "%{http_code}|%{time_total}" \
    --connect-timeout 10 --max-time 15 \
    --proxy "$PROXY" \
    "https://pixabay.com/api/?key=test&q=test&per_page=3" 2>/dev/null || echo "000|0")
show_result "Pixabay" "$(echo "$result" | cut -d'|' -f1)" "$(echo "$result" | cut -d'|' -f2)"

# 10. Google Imagen 4 Fast
if [ -n "$GEMINI_KEY" ]; then
    result=$(curl -s -o /dev/null -w "%{http_code}|%{time_total}" \
        --connect-timeout 10 --max-time 15 \
        --proxy "$PROXY" \
        "https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-fast-generate-001?key=${GEMINI_KEY}" 2>/dev/null || echo "000|0")
    show_result "Imagen 4 Fast" "$(echo "$result" | cut -d'|' -f1)" "$(echo "$result" | cut -d'|' -f2)"
else
    show_skip "Imagen 4 Fast" "нет ключа"
fi

echo ""

# ============================================================
# 🖥️ ИНФРАСТРУКТУРА
# ============================================================
echo "  🖥️  ИНФРАСТРУКТУРА"
echo "  ─────────────────────────────────────────────"

SSH_KEY="$ROOT_DIR/.ssh_agent_key"
if [ -f "$SSH_KEY" ]; then
    VPS_STATUS=$(ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@72.56.38.19 'echo OK' 2>/dev/null || echo "FAIL")
    TOTAL=$((TOTAL + 1))
    if [ "$VPS_STATUS" = "OK" ]; then
        printf "  ✅ %-20s  SSH OK\n" "VPS Timeweb"
        OK=$((OK + 1))
    else
        printf "  💀 %-20s  SSH FAIL\n" "VPS Timeweb"
        FAIL=$((FAIL + 1))
    fi
else
    show_skip "VPS Timeweb" "нет SSH-ключа"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
printf "  ИТОГО: %d/%d OK" "$OK" "$TOTAL"
if [ "$FAIL" -gt 0 ]; then
    printf "  |  ❌ %d FAIL" "$FAIL"
fi
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Легенда: ✅ OK | 🔑 Ключ/квота | 🚫 Заблокирован | 💀 Недоступен | ⏭️ Пропущен"
echo ""
