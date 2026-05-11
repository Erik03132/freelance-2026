#!/bin/bash
# =====================================================
# 🔍 waza-audit.sh — Ежедневный аудит скиллов Antigravity
# Запускается вручную или как часть finish-day
# =====================================================

set -uo pipefail

export PATH="$HOME/bin:$PATH"

SKILLS_DIR="$HOME/.gemini/antigravity/skills"
REPORT_DIR="$HOME/freelance-2026/reports/waza"
DATE=$(date +%Y-%m-%d)
REPORT_FILE="$REPORT_DIR/waza-audit_$DATE.md"

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Проверка waza
if ! command -v waza &> /dev/null; then
    echo -e "${RED}❌ waza не установлен. Запусти: curl -fsSL https://raw.githubusercontent.com/microsoft/waza/main/install.sh | bash${NC}"
    exit 1
fi

# Создание директории отчётов
mkdir -p "$REPORT_DIR"

echo -e "${GREEN}🔍 Waza Skill Audit — $DATE${NC}"
echo "================================================"

# ============================================
# 1. Token Count (ТОП-10 самых тяжёлых)
# ============================================
echo ""
echo -e "${YELLOW}📊 Фаза 1: Token Budget${NC}"

TOKEN_OUTPUT=$(waza tokens count "$SKILLS_DIR" --sort tokens 2>&1)
TOTAL_TOKENS=$(echo "$TOKEN_OUTPUT" | grep "^Total" | awk '{print $2}')
FILE_COUNT=$(echo "$TOKEN_OUTPUT" | grep "file(s) scanned" | awk '{print $1}')

echo "   Всего: $TOTAL_TOKENS токенов в $FILE_COUNT файлах"

# ТОП-10 самых тяжёлых SKILL.md
echo ""
echo "   ТОП-10 тяжёлых скиллов:"
echo "$TOKEN_OUTPUT" | grep "SKILL.md" | head -10 | while read line; do
    TOKENS=$(echo "$line" | awk '{print $(NF-2)}')
    NAME=$(echo "$line" | awk -F'/' '{for(i=1;i<=NF;i++) if($i ~ /SKILL.md/) print $(i-1)}')
    if [ "$TOKENS" -gt 3000 ]; then
        echo -e "   ${RED}⚠️  $NAME: $TOKENS токенов${NC}"
    elif [ "$TOKENS" -gt 2000 ]; then
        echo -e "   ${YELLOW}📍 $NAME: $TOKENS токенов${NC}"
    else
        echo "   ✅ $NAME: $TOKENS токенов"
    fi
done

# ============================================
# 2. Compliance Check (все скиллы)
# ============================================
echo ""
echo -e "${YELLOW}📋 Фаза 2: Compliance Check${NC}"

PASS_COUNT=0
WARN_COUNT=0
FAIL_COUNT=0
SKILL_RESULTS=""

for skill_dir in "$SKILLS_DIR"/*/; do
    skill_name=$(basename "$skill_dir")
    
    # Пропустить не-скиллы
    if [ "$skill_name" = "_references" ] || [ ! -f "$skill_dir/SKILL.md" ]; then
        continue
    fi
    
    CHECK_OUTPUT=$(waza check "$skill_dir" 2>&1 || true)
    
    if echo "$CHECK_OUTPUT" | grep -q "ready for submission"; then
        PASS_COUNT=$((PASS_COUNT + 1))
        STATUS="✅ PASS"
    elif echo "$CHECK_OUTPUT" | grep -q "needs some work"; then
        WARN_COUNT=$((WARN_COUNT + 1))
        STATUS="⚠️  WARN"
    else
        FAIL_COUNT=$((FAIL_COUNT + 1))
        STATUS="❌ FAIL"
    fi
    
    # Извлечь compliance score
    COMPLIANCE=$(echo "$CHECK_OUTPUT" | grep "Compliance Score:" | sed 's/.*Score: //' | head -1)
    TOKEN_INFO=$(echo "$CHECK_OUTPUT" | grep "Token Budget:" | sed 's/.*Budget: //' | head -1)
    
    SKILL_RESULTS="$SKILL_RESULTS\n   $STATUS $skill_name — $COMPLIANCE"
done

echo -e "$SKILL_RESULTS"
echo ""
echo "   Итого: ✅ $PASS_COUNT passed | ⚠️  $WARN_COUNT warnings | ❌ $FAIL_COUNT failed"

# ============================================
# 3. Генерация отчёта в Markdown
# ============================================
echo ""
echo -e "${YELLOW}📝 Фаза 3: Генерация отчёта${NC}"

cat > "$REPORT_FILE" << EOF
# 🔍 Waza Skill Audit — $DATE

**Время:** $(date +%H:%M:%S)
**Waza version:** $(waza --version 2>&1 | head -1)
**Skills directory:** $SKILLS_DIR

---

## 📊 Token Budget

| Метрика | Значение |
|---------|----------|
| **Всего файлов** | $FILE_COUNT |
| **Всего токенов** | $TOTAL_TOKENS |
| **Средний размер** | $((TOTAL_TOKENS / FILE_COUNT)) токенов |

### ТОП-10 тяжёлых скиллов (SKILL.md only)

\`\`\`
$(echo "$TOKEN_OUTPUT" | grep "SKILL.md" | head -10)
\`\`\`

---

## 📋 Compliance Summary

| Статус | Кол-во |
|--------|--------|
| ✅ Passed | $PASS_COUNT |
| ⚠️ Warnings | $WARN_COUNT |
| ❌ Failed | $FAIL_COUNT |

### Детализация

$(echo -e "$SKILL_RESULTS" | sed 's/^   /- /')

---

## 🎯 Рекомендации

$(if [ $WARN_COUNT -gt 0 ] || [ $FAIL_COUNT -gt 0 ]; then
echo "1. Запустить \`waza dev <skill-path>\` для скиллов с WARN/FAIL"
echo "2. Запустить \`waza tokens suggest <skill-path>\` для раздутых скиллов"
echo "3. Добавить USE FOR / DO NOT USE FOR секции в скиллы без triggers"
else
echo "✨ Все скиллы в отличном состоянии!"
fi)

---
*Отчёт сгенерирован автоматически: waza-audit.sh*
EOF

echo "   ✅ Отчёт сохранён: $REPORT_FILE"

# ============================================
# Итог
# ============================================
echo ""
echo "================================================"
echo -e "${GREEN}✅ Waza Audit завершён${NC}"
echo "   📊 $TOTAL_TOKENS токенов | $FILE_COUNT файлов"
echo "   📋 $PASS_COUNT ✅ | $WARN_COUNT ⚠️  | $FAIL_COUNT ❌"
echo "   📝 Отчёт: $REPORT_FILE"
echo "================================================"
