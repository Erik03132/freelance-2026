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

echo "── Health Check (external infra) ──"

# A. OmniRoute (localhost:20128)
if curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 "http://127.0.0.1:20128/v1/models" 2>/dev/null | grep -qE "^(200|401)$"; then
    echo "OmniRoute (127.0.0.1:20128): ✅ up"
else
    echo "OmniRoute (127.0.0.1:20128): ❌ DOWN"
fi

# B. Model responds (auto/free-coding via omniroute)
if curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 -X POST "http://127.0.0.1:20128/v1/chat/completions" \
     -H "Content-Type: application/json" -d '{"model":"auto/free-coding-full","messages":[{"role":"user","content":"hi"}],"max_tokens":5}' 2>/dev/null | grep -qE "^(200|401)$"; then
    echo "Model auto/free-coding-full: ✅ responds"
else
    echo "Model auto/free-coding-full: ❌ no response (нужен US-прокси у omniroute?)"
fi

# B2. Ollama local model (127.0.0.1:11434)
if curl -s --connect-timeout 3 "http://127.0.0.1:11434/api/tags" 2>/dev/null | grep -q "qwen2.5"; then
    echo "Ollama (127.0.0.1:11434): ✅ up, qwen2.5 present"
else
    echo "Ollama (127.0.0.1:11434): ❌ down or no qwen2.5 model"
fi

# B3. Nous provider reachable (direct inference API)
if curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "https://inference-api.nousresearch.com/v1/models" 2>/dev/null | grep -qE "^(200|401)$"; then
    echo "Nous provider (inference-api.nousresearch.com): ✅ reachable"
else
    echo "Nous provider (inference-api.nousresearch.com): ❌ unreachable (VPN off? key?)"
fi

# C. VPN status (Telegram needs it in RU)
if curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 "https://api.telegram.org" 2>/dev/null | grep -qE "^[0-9]+$"; then
    echo "Telegram API reachable (VPN likely ON): ✅"
else
    echo "Telegram API blocked (VPN OFF?): ❌ Mustay in TG won't work"
fi

# D. Gateway (batrak) + Telegram token
if hermes --profile batrak gateway status 2>/dev/null | grep -q "running"; then
    echo "Gateway (batrak): ✅ running"
else
    echo "Gateway (batrak): ❌ not running"
fi
if hermes --profile batrak config get gateway.telegram.token 2>/dev/null | grep -q "token:"; then
    echo "Telegram token (batrak): ✅ set"
else
    echo "Telegram token (batrak): ❌ missing"
fi

# E. Cron JobHunter
if hermes --profile batrak cron list 2>/dev/null | grep -q "JobHunter"; then
    echo "Cron JobHunter: ✅ active"
else
    echo "Cron JobHunter: ❌ missing"
fi

# F. VPS (217.149.23.113) — only if reachable
if ping -c 1 -W 2 217.149.23.113 &>/dev/null; then
    echo "VPS (217.149.23.113): ✅ reachable"
    echo "  └ PM2 processes:"
    ssh -i /Users/igorvasin/freelance-2026/.ssh_agent_key -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@217.149.23.113 \
        "pm2 list 2>/dev/null | grep -E 'angela|scheduler|autopilot|bot' | head -10" 2>/dev/null || echo "    (ssh failed)"
    echo "  └ Cron jobs (news/agents):"
    ssh -i /Users/igorvasin/freelance-2026/.ssh_agent_key -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@217.149.23.113 \
        "crontab -l 2>/dev/null | grep -v '^#' | grep -iE 'news|agent|digest|angela' | head -10" 2>/dev/null || echo "    (ssh failed)"
else
    echo "VPS (217.149.23.113): ⚠️  unreachable (VPN on? VPS is RU-host, blocked via VPN)"
fi
echo ""

# G. Mac → VPS bridge (tunnel 9119/8742 + hermes peer) — SSoT: handoff_2026-08-28_remote_control_live.md
echo "── Mac → VPS Bridge ──"
BRIDGE_CHECKER="/Users/igorvasin/freelance-2026/check_bridge.sh"
if [ -x "$BRIDGE_CHECKER" ]; then
    # --with-echo: сквозной тест через hermes peer dm vps (пишет тестовую фразу в VPS-чат)
    "$BRIDGE_CHECKER" --with-echo || echo "  ⚠️  мост упал — см. ❌ выше (SSoT: handoff_2026-08-28_remote_control_live.md)"
else
    echo "check_bridge.sh не найден: $BRIDGE_CHECKER"
fi
echo ""

echo "══════════════════════════════════════════════"
echo "  Ready. Next step: check ACTIVE_TASKS.md"
echo "══════════════════════════════════════════════"