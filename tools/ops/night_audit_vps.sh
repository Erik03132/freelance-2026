#!/bin/bash
# ============================================================
# 🌙 night_audit_vps.sh — Ночной аудит на VPS (Timeweb)
# ============================================================
# Запуск: crontab → 02:00 MSK
#   Или вручную: bash tools/night_audit_vps.sh
#
# Фаза 1: ruff + grep-секреты
# Фаза 2: Grok 4.5 (OpenRouter) — глубокий код-ревью
# Фаза 3: Отчёт в Telegram Игорю
# ============================================================

set -eu

# ============ КОНФИГ ============
PROJECT_DIR="/opt/levitan/projects/ai-eggs"
AGENT_DIR="${PROJECT_DIR}/agent"
REPORTS_DIR="${PROJECT_DIR}/reports"
VENV="${PROJECT_DIR}/.server_venv/bin/python3"
DATE=$(date +%Y-%m-%d)
REPORT_FILE="${REPORTS_DIR}/night_audit_vps_${DATE}.md"
TG_BOT_TOKEN=$(grep "ANGELOCHKA_BOT_TOKEN" "${PROJECT_DIR}/.env" 2>/dev/null | cut -d= -f2)
OPENROUTER_KEY=$(grep "OPENROUTER_API_KEY" "${PROJECT_DIR}/.env" 2>/dev/null | cut -d= -f2)
TG_ADMIN_ID="176203333"
# OpenRouter из РФ — только через прокси
PROXY_URL="socks5h://Q3NeJXTY:dsBaWh2L@172.120.21.141:64469"

mkdir -p "$REPORTS_DIR"

echo "🌙 Night Audit VPS — ${DATE}"
echo ""

# ─── Фаза 1: ruff + секреты ──────────────────────────────────
echo "⚡ Фаза 1: Машинный анализ"

REPORT_TEXT=""
RUFF_TEXT=""
SECRETS_TEXT=""

if command -v ruff &>/dev/null; then
    RUFF_OUTPUT=$(ruff check "$AGENT_DIR" --select E,F,S,B --output-format concise 2>&1 || true)
    if [ -n "$RUFF_OUTPUT" ]; then
        RUFF_TEXT="🔍 ruff — ${DATE}: $(echo "$RUFF_OUTPUT" | wc -l) предупреждений"
    else
        RUFF_TEXT="✅ ruff — чисто"
    fi
    echo "   $RUFF_TEXT"
else
    RUFF_TEXT="⚠️ ruff не установлен"
    echo "   $RUFF_TEXT"
fi

# Поиск потенциальных секретов
SECRETS_OUTPUT=$(grep -rn 'sk-or-\|AIzaSy\|AKIA\|-----BEGIN.*PRIVATE' "$AGENT_DIR" --include='*.py' --include='*.sh' --exclude='*test*' 2>/dev/null | grep -v '.env' || true)
if [ -n "$SECRETS_OUTPUT" ]; then
    SECRETS_COUNT=$(echo "$SECRETS_OUTPUT" | wc -l)
    SECRETS_TEXT="🔑 Найдено $SECRETS_COUNT потенциальных секретов в коде"
    echo "   ⚠️ $SECRETS_TEXT"
else
    SECRETS_TEXT="✅ Секреты не найдены"
    echo "   ✅ Секретов в коде нет"
fi

# ─── Фаза 2: Сильная LLM (Grok 4.5) ──────────────────────────
echo ""
echo "⚡ Фаза 2: Grok 4.5 — глубокий код-ревью"

LLM_TEXT=""
if [ -n "$OPENROUTER_KEY" ]; then
    # Ключевые файлы для ревью (последние 10 изменённых .py)
    RECENT_FILES=$(find "$AGENT_DIR" -name '*.py' -newer "$AGENT_DIR/../.env" -not -path '*/__pycache__/*' 2>/dev/null | head -10)
    if [ -z "$RECENT_FILES" ]; then
        RECENT_FILES=$(find "$AGENT_DIR" -name '*.py' -not -path '*/__pycache__/*' 2>/dev/null | head -5)
    fi

    AUDIT_PAYLOAD=""
    for f in $RECENT_FILES; do
        rel_path="${f#$AGENT_DIR/}"
        content=$(head -200 "$f" 2>/dev/null)
        AUDIT_PAYLOAD+="\n=== $rel_path ===\n${content}\n"
    done

    LLM_TEXT=$($VENV -c "
import json, os, requests

proxy_url = '${PROXY_URL}'
key = '${OPENROUTER_KEY}'

with open('/dev/stdin', 'r') as f:
    audit_payload = f.read()

prompt = '''Ты — старший разработчик на code-review. Найди в коде:
1. Потенциальные баги (логические ошибки, race conditions, утечки)
2. Проблемы безопасности (секреты, SQL-инъекции, неэкранированный ввод)
3. Проблемы производительности

Файлы проекта (ai-eggs: Bitrix24 CRM бот с AI-каскадом):
''' + audit_payload + '''

ОТВЕТЬ СТРОГО:
### 🔴 Критические
### 🟡 Средние
### 🔵 Замечания
Если всё чисто — напиши: ✅ Критических ошибок нет, всё чисто.'''

try:
    proxies = {'https': proxy_url, 'http': proxy_url} if proxy_url else None
    resp = requests.post(
        'https://openrouter.ai/api/v1/chat/completions',
        headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'},
        json={'model': 'x-ai/grok-4.5', 'messages': [{'role': 'user', 'content': prompt}], 'temperature': 0.1, 'max_tokens': 1500},
        proxies=proxies,
        timeout=60
    )
    if resp.status_code == 200:
        print(resp.json()['choices'][0]['message']['content'])
    else:
        err = resp.json().get('error', {}).get('message', resp.text[:200])
        print(f'⚠️ {err}')
except Exception as e:
    print(f'⚠️ {e}')
" <<< "$AUDIT_PAYLOAD" 2>&1)
    echo "   ✅ Grok 4.5 — ревью завершено"
else
    LLM_TEXT="⚠️ OPENROUTER_KEY не найден"
    echo "   $LLM_TEXT"
fi

# ─── Формирование отчёта ──────────────────────────────────────
cat > "$REPORT_FILE" << EOF
# 🌙 Ночной аудит VPS — ${DATE}

**Начало:** $(date +%H:%M)

---

## ⚡ Фаза 1: Машинный анализ

### 🔍 Ruff
${RUFF_TEXT}

### 🔑 Секреты
${SECRETS_TEXT}

## ⚡ Фаза 2: AI Code Review (Grok 4.5)

${LLM_TEXT}

---

*Audit by night_audit_vps.sh | ${DATE} $(date +%H:%M)*
EOF

echo ""
echo "📄 Отчёт: $REPORT_FILE"

# ─── Telegram ─────────────────────────────────────────────────
if [ -n "$TG_BOT_TOKEN" ]; then
    $VENV -c "
import json, requests
url = 'https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage'
msg = {'chat_id': ${TG_ADMIN_ID}, 'text': '🌙 Night Audit VPS — ${DATE}\nPhase 1:\n• Ruff: ${RUFF_TEXT}\n• Secrets: ${SECRETS_TEXT}\n\nPhase 2: Grok 4.5 — review done\n\nReport: ${REPORT_FILE}'}
r = requests.post(url, json=msg, proxies={'https': '${PROXY_URL}'}, timeout=10)
print('📨 Sent to Telegram' if r.status_code == 200 else f'⚠ TG {r.status_code}')
" 2>&1
fi

echo ""
echo "✅ Аудит завершён"
