#!/bin/bash
# Check for secrets in staged changes.
# Primary: gitleaks protect --staged (быстро, только staged diff)
# Fallback: наивный grep-скан, если gitleaks не установлен
# Whitelist строки: добавьте в конец строки комментарий  # gitleaks:allow

if ! git rev-parse --git-dir >/dev/null 2>&1; then
    exit 0
fi

if ! git diff --cached --name-only | grep -q .; then
    exit 0
fi

if command -v gitleaks >/dev/null 2>&1; then
    if ! gitleaks protect --staged --redact --no-banner --exit-code 1 --timeout 120 2>&1; then
        echo ""
        echo "ERROR: gitleaks нашёл потенциальный секрет в staged-изменениях."
        echo "  Решение 1: ротируйте ключ и уберите его из кода."
        echo "  Решение 2: строка намеренная (фикстура/тест) — добавьте в конец строки:  # gitleaks:allow"
        exit 1
    fi
    exit 0
fi

# Fallback: grep-скан (если gitleaks недоступен)
FILES=$(git diff --cached --name-only | grep -vE "(test|spec|example|mock)\.(py|js|ts)$")
if [ -n "$FILES" ]; then
    echo "$FILES" | xargs git diff --cached | grep -iE "(api[_-]?key|secret|password|token)\s*=\s*[\"'][a-zA-Z0-9]{16,}" && {
        echo "ERROR: Possible secret in diff"
        exit 1
    }
fi
exit 0
