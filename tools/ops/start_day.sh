#!/bin/bash
# start_day.sh — Start of workday session initializer
# Reads context, checks servers, bots, API keys. Run at the beginning of every ZCode/Open Code session.

SESSION_FILE="/Users/igorvasin/freelance-2026/SESSION_LATEST.md"
TASKS_FILE="/Users/igorvasin/freelance-2026/ACTIVE_TASKS.md"
CHP_FILE="/Users/igorvasin/freelance-2026/chp.md"
ENV_FILE="/Users/igorvasin/freelance-2026/.env"
PROJECT_ROOT="/Users/igorvasin/freelance-2026"

echo "══════════════════════════════════════════════"
echo "  START DAY — $(date '+%Y-%m-%d %H:%M')"
echo "══════════════════════════════════════════════"
echo ""

# 1. Last session summary
echo "── Last Session ──"
if [ -f "$SESSION_FILE" ]; then
    tail -20 "$SESSION_FILE"
else
    echo "(no SESSION_LATEST.md yet)"
fi
echo ""

# 2. Active tasks
echo "── Active Tasks ──"
if [ -f "$TASKS_FILE" ]; then
    grep -E "^\- \[.\]" "$TASKS_FILE" | head -10 || echo "(no active tasks)"
else
    echo "(no ACTIVE_TASKS.md)"
fi
echo ""

# 3. Project context
echo "── Project Context (chp.md) ──"
if [ -f "$CHP_FILE" ]; then
    head -30 "$CHP_FILE"
else
    echo "(no chp.md)"
fi
echo ""

# 4. Git status
echo "── Git Status ──"
cd "$PROJECT_ROOT" && git status --short 2>/dev/null || echo "(not a git repo)"
echo ""

# 5. PM2 status (if pm2 available)
echo "── PM2 Status ──"
if command -v pm2 &>/dev/null; then
    pm2 status 2>/dev/null | head -15 || echo "pm2 not returning output"
else
    echo "pm2 not installed"
fi
echo ""

# 6. Key ports check
echo "── Port Check ──"
PORTS=(3000 8080 8000 3001 11434 9200)
for PORT in "${PORTS[@]}"; do
    if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT/" --connect-timeout 2 2>/dev/null | grep -qE "^[0-9]+$"; then
        echo "Port $PORT: listening"
    else
        echo "Port $PORT: not responding"
    fi
done
echo ""

# 7. API keys check
echo "── API Keys Check ──"
if [ -f "$ENV_FILE" ]; then
    grep -E "^(OPENAI|ANTHROPIC|GEMINI|SERPAPI|PERPLEXITY|API_|KEY)" "$ENV_FILE" 2>/dev/null | while IFS= read -r line; do
        key_name=$(echo "$line" | cut -d= -f1)
        key_val=$(echo "$line" | cut -d= -f2)
        if [ ${#key_val} -gt 8 ]; then
            echo "$key_name: ✅ present"
        else
            echo "$key_name: ⚠️  too short or empty"
        fi
    done
else
    echo "(no .env file)"
fi
echo ""

echo "══════════════════════════════════════════════"
echo "  Ready. Next step: check ACTIVE_TASKS.md"
echo "══════════════════════════════════════════════"