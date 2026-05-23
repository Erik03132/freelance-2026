#!/usr/bin/env bash
# sync_cursor_rules.sh — Синхронизация скиллов Antigravity → Cursor .cursor/rules/
#
# Использование:
#   ./tools/sync_cursor_rules.sh           # полная синхронизация
#   ./tools/sync_cursor_rules.sh --dry-run # показать что изменится
#   ./tools/sync_cursor_rules.sh --skill rag-master  # один скилл
#
# Что делает:
#   1. Конвертирует IRON_RULES.md + document-governance.md → .cursor/rules/global/iron_rules.mdc
#   2. Конвертирует каждый SKILL.md → .cursor/rules/global/<name>.mdc
#   3. Проверяет .cursor/rules/project/ — проектные правила (не трогает, только INFO)

set -euo pipefail

SKILLS_DIR="/Users/igorvasin/.gemini/config/skills"
AGENT_RULES_DIR="/Users/igorvasin/freelance-2026/.agent/rules"
CURSOR_GLOBAL="/Users/igorvasin/freelance-2026/.cursor/rules/global"
CURSOR_PROJECT="/Users/igorvasin/freelance-2026/.cursor/rules/project"
DRY_RUN=false
SINGLE_SKILL=""

for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=true ;;
        --skill) SINGLE_SKILL="${2:-}" ;;
    esac
done

log() { echo "[sync_cursor] $*"; }

# ─── Утилита: SKILL.md → .mdc ───────────────────────────────────────────────

convert_skill_to_mdc() {
    local skill_dir="$1"
    local skill_name
    skill_name=$(basename "$skill_dir")
    local src="$skill_dir/SKILL.md"
    local dst="$CURSOR_GLOBAL/${skill_name}.mdc"

    [ -f "$src" ] || return 0

    # Извлекаем description из YAML frontmatter
    local description
    description=$(python3 -c "
import re, sys
with open('$src') as f:
    content = f.read()
m = re.search(r'^description:\s*[>\|]?\s*\n?(.*?)(?=\n\w|\Z)', content, re.DOTALL | re.MULTILINE)
if m:
    desc = re.sub(r'\s+', ' ', m.group(1).strip()).strip('\"')
    print(desc[:200])
else:
    print('${skill_name} skill')
" 2>/dev/null || echo "${skill_name} skill")

    # Формируем .mdc
    local mdc_content="---
description: ${description}
alwaysApply: false
---

$(cat "$src")

> _Синхронизировано из Antigravity: \`${src}\`_
> _Обновить: \`./tools/sync_cursor_rules.sh --skill ${skill_name}\`_
"

    if [ "$DRY_RUN" = true ]; then
        log "  [DRY] Would write: $dst"
        return 0
    fi

    echo "$mdc_content" > "$dst"
    log "  ✅ ${skill_name} → $(basename "$dst")"
}

# ─── 1. Глобальные правила агента (IRON_RULES + governance) ──────────────────

log "📐 Конвертируем правила агента..."

if [ "$DRY_RUN" = false ]; then
cat > "$CURSOR_GLOBAL/00_iron_rules.mdc" << 'MDC'
---
description: Железные правила Antigravity — SSH, структура, SSoT, протоколы. Читать при каждом старте.
alwaysApply: true
---

MDC

cat "$AGENT_RULES_DIR/IRON_RULES.md" >> "$CURSOR_GLOBAL/00_iron_rules.mdc" 2>/dev/null || true
cat "$AGENT_RULES_DIR/document-governance.md" >> "$CURSOR_GLOBAL/00_iron_rules.mdc" 2>/dev/null || true
echo "" >> "$CURSOR_GLOBAL/00_iron_rules.mdc"
echo "> _Синхронизировано из: \`.agent/rules/IRON_RULES.md\` + \`document-governance.md\`_" >> "$CURSOR_GLOBAL/00_iron_rules.mdc"
log "  ✅ IRON_RULES + document-governance → 00_iron_rules.mdc"
else
    log "  [DRY] Would write: 00_iron_rules.mdc"
fi

# Две Анжелы — архитектурная карта
if [ "$DRY_RUN" = false ]; then
cat > "$CURSOR_GLOBAL/01_angela_map.mdc" << 'MDC'
---
description: Карта агентов Antigravity — Анжела, Птенчикова, архитектура, heartbeat правила.
alwaysApply: false
---

MDC
cat "$AGENT_RULES_DIR/two-angelas-map.md" >> "$CURSOR_GLOBAL/01_angela_map.mdc" 2>/dev/null || true
echo "" >> "$CURSOR_GLOBAL/01_angela_map.mdc"
echo "> _Синхронизировано из: \`.agent/rules/two-angelas-map.md\`_" >> "$CURSOR_GLOBAL/01_angela_map.mdc"
log "  ✅ two-angelas-map → 01_angela_map.mdc"
fi

# ─── 2. Скиллы Antigravity ────────────────────────────────────────────────────

log ""
log "🧠 Конвертируем скиллы..."

if [ -n "$SINGLE_SKILL" ]; then
    # Один конкретный скилл
    skill_dir="$SKILLS_DIR/$SINGLE_SKILL"
    if [ -d "$skill_dir" ]; then
        convert_skill_to_mdc "$skill_dir"
    else
        log "  ❌ Скилл не найден: $SINGLE_SKILL"
        exit 1
    fi
else
    # Все скиллы
    for skill_dir in "$SKILLS_DIR"/*/; do
        [ -d "$skill_dir" ] || continue
        convert_skill_to_mdc "$skill_dir"
    done
fi

# ─── 3. Отчёт ────────────────────────────────────────────────────────────────

log ""
log "📊 Итог:"
log "  Global rules: $(ls "$CURSOR_GLOBAL"/*.mdc 2>/dev/null | wc -l | tr -d ' ') файлов"
log "  Project rules: $(ls "$CURSOR_PROJECT"/*.mdc 2>/dev/null | wc -l | tr -d ' ') файлов"
log ""
log "📁 Структура .cursor/rules/:"
log "  global/  — скиллы Antigravity + железные правила (НЕ редактировать вручную)"
log "  project/ — проектные правила (редактировать здесь)"
log ""

if [ "$DRY_RUN" = false ]; then
    log "✅ Синхронизация завершена"
    log "💡 Следующий запуск: ./tools/sync_cursor_rules.sh"
fi
