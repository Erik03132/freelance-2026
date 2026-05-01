#!/bin/zsh
# =============================================================
# 🔄 Antigravity Skill Evolution Scanner
# Сканирует ECC Library на обновления
# Запуск: zsh .agent/skill-evolution.sh
# =============================================================

ECC_DIR="$HOME/freelance-2026/.ecc-library"

echo "╔══════════════════════════════════════════════╗"
echo "║   🔄 Antigravity Skill Evolution Scanner     ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# === Шаг 1: Обновить ECC Library ===
echo "[1/3] Обновление ECC Library..."
if [ -d "$ECC_DIR/.git" ]; then
    cd "$ECC_DIR"
    OLD_HASH=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
    git pull --quiet 2>/dev/null || echo "  ⚠ git pull failed (offline?)"
    NEW_HASH=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
    
    if [ "$OLD_HASH" = "$NEW_HASH" ]; then
        echo "  ✓ Библиотека актуальна"
    else
        CHANGES=$(git log --oneline "$OLD_HASH..$NEW_HASH" 2>/dev/null | wc -l | tr -d ' ')
        echo "  ✓ Обновлено! +${CHANGES} коммитов"
    fi
else
    echo "  ✗ ECC Library не найдена: $ECC_DIR"
    exit 1
fi

# === Шаг 2: Подсчёт ===
echo ""
echo "[2/3] Инвентаризация..."
TOTAL_ECC=$(ls -d "$ECC_DIR/skills"/*/ 2>/dev/null | wc -l | tr -d ' ')
echo "  📚 Скиллов в ECC: $TOTAL_ECC"

# === Шаг 3: Поиск по доменам ===
echo ""
echo "[3/3] Поиск скиллов по доменам агентов..."
echo ""

scan_domain() {
    local domain_name=$1
    local pattern=$2
    local found=0
    
    echo "  📦 $domain_name:"
    
    for skill_path in "$ECC_DIR/skills"/*/; do
        skill_name=$(basename "$skill_path")
        
        if echo "$skill_name" | grep -qiE "$pattern"; then
            desc=$(grep "description:" "$skill_path/SKILL.md" 2>/dev/null | head -1 | sed 's/description: //' | tr -d '"' | cut -c1-75)
            echo "    ⚡ $skill_name"
            echo "       $desc"
            found=$((found + 1))
        fi
    done
    
    if [ $found -eq 0 ]; then
        echo "    (нет совпадений)"
    fi
    echo ""
    return $found
}

TOTAL=0

scan_domain "🧠 Игорёк (оркестрация)" "agentic|orchestrat|planner|architect|autonomous|continuous-learning"
TOTAL=$((TOTAL + $?))

scan_domain "🔧 Кулибин (инженерия)" "deploy|docker|security|performance|cost|infra|devops|monitoring|observability|terraform|nginx"
TOTAL=$((TOTAL + $?))

scan_domain "⚡ Артемий (фронтенд)" "frontend|react|nextjs|astro|css|tailwind|accessibility|component|animation|vite"
TOTAL=$((TOTAL + $?))

scan_domain "🤖 Ботмэн (боты)" "bot|telegram|agent-harness|chat|webhook|api-connect|messaging|discord"
TOTAL=$((TOTAL + $?))

scan_domain "✍️ Шекспир (контент)" "content|article|writing|brand-voice|copy|newsletter|editorial"
TOTAL=$((TOTAL + $?))

scan_domain "🔍 Шерл (разведка)" "research|market|competitor|analysis|intel|scraping|monitor|benchmark"
TOTAL=$((TOTAL + $?))

scan_domain "📊 Маркетолог (стратегия)" "seo|marketing|analytics|dashboard|growth|click-path|link"
TOTAL=$((TOTAL + $?))

scan_domain "🎨 Рембрандт (дизайн)" "design|figma|color|typography|icon|image|visual|brand-identity"
TOTAL=$((TOTAL + $?))

echo "──────────────────────────────────────────────"
echo "  Скажи: «Поставь [скилл] для [агент]»"
echo "  Или:   «Обнови скиллы Кулибина»"
echo "──────────────────────────────────────────────"
