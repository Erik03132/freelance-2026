#!/bin/bash
# Универсальный pre-commit hook: авто-прогон eval suite проекта
# Использование: bash scripts/install-eval-hook.sh <project-dir>
# Пример: bash scripts/install-eval-hook.sh projects/ai-eggs

PROJECT="$1"
if [ -z "$PROJECT" ]; then
    echo "Usage: $0 <project-dir>"
    echo "Example: $0 projects/ai-eggs"
    exit 1
fi

EVAL_SCRIPT="${PROJECT}/tests/eval_$(basename $PROJECT).py"
if [ ! -f "$EVAL_SCRIPT" ]; then
    echo "❌ Eval script not found: $EVAL_SCRIPT"
    echo "   Create it first: tests/eval_<project>.py"
    exit 1
fi

cat > "$(git rev-parse --show-toplevel 2>/dev/null)/.git/hooks/pre-commit" << HOOK
#!/bin/bash
# Auto-generated: прогон eval suite при изменении ключевых файлов проекта
CHANGED=\$(git diff --cached --name-only | grep -E "^${PROJECT}/" | head -1)
if [ -z "\$CHANGED" ]; then
    exit 0
fi
echo "🔄 \$(basename $PROJECT) files changed — running eval suite..."
cd "\$(git rev-parse --show-toplevel)"
python3 ${EVAL_SCRIPT}
RESULT=\$?
if [ \$RESULT -ne 0 ]; then
    echo ""
    echo "❌ Eval suite FAILED. Fix or commit with --no-verify."
    exit 1
fi
echo "✅ Eval suite passed."
HOOK

chmod +x "$(git rev-parse --show-toplevel 2>/dev/null)/.git/hooks/pre-commit"
echo "✅ Pre-commit hook installed for $PROJECT"
echo "   Прогоняет: python3 $EVAL_SCRIPT при изменении файлов в $PROJECT/"
