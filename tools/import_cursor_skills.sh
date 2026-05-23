#!/usr/bin/env bash
# import_cursor_skills.sh — Импорт скиллов из Cursor обратно в Antigravity
#
# Использование:
#   ./tools/import_cursor_skills.sh           # импорт всех новых из project/
#   ./tools/import_cursor_skills.sh my-skill  # конкретный файл из project/
#
# Логика:
#   .cursor/rules/project/*.mdc  →  ~/.gemini/config/skills/<name>/SKILL.md
#   .cursor/rules/global/        →  НЕ трогаем (они уже из Antigravity)

set -euo pipefail

CURSOR_PROJECT="/Users/igorvasin/freelance-2026/.cursor/rules/project"
SKILLS_DIR="/Users/igorvasin/.gemini/config/skills"
SINGLE="${1:-}"

log() { echo "[import_cursor] $*"; }

# Файл для которого явно указано имя
if [ -n "$SINGLE" ]; then
    src="$CURSOR_PROJECT/${SINGLE}.mdc"
    [ -f "$src" ] || src="$CURSOR_PROJECT/$SINGLE"
    [ -f "$src" ] || { log "❌ Файл не найден: $src"; exit 1; }
    files=("$src")
else
    # Все .mdc в project/ кроме freelance_2026.mdc (проектный, не скилл)
    mapfile -t files < <(find "$CURSOR_PROJECT" -name "*.mdc" ! -name "freelance_2026.mdc" 2>/dev/null)
fi

if [ ${#files[@]} -eq 0 ]; then
    log "ℹ️  Нет новых скиллов в .cursor/rules/project/ для импорта"
    log "   Создай .mdc файл в .cursor/rules/project/ и запусти снова"
    exit 0
fi

imported=0
for src in "${files[@]}"; do
    [ -f "$src" ] || continue

    # Имя скилла из имени файла
    skill_name=$(basename "$src" .mdc)
    skill_dir="$SKILLS_DIR/$skill_name"
    dst="$skill_dir/SKILL.md"

    # Проверяем — это уже существующий глобальный скилл?
    if [ -f "$SKILLS_DIR/$skill_name/SKILL.md" ]; then
        log "⚠️  $skill_name уже существует в Antigravity — пропускаю (обнови вручную)"
        continue
    fi

    log "📥 Импортирую: $skill_name"
    mkdir -p "$skill_dir"

    # Убираем Cursor-специфичный frontmatter, оставляем Antigravity-формат
    python3 - "$src" "$dst" << 'PYEOF'
import sys, re

src, dst = sys.argv[1], sys.argv[2]
with open(src, encoding='utf-8') as f:
    content = f.read()

# Убираем Cursor frontmatter (--- description: ... alwaysApply: ... ---)
content = re.sub(r'^---\ndescription:.*?alwaysApply:.*?---\n\n?', '', content, flags=re.DOTALL)

# Убираем метку "синхронизировано из Antigravity" если она была
content = re.sub(r'\n> _Синхронизировано из Antigravity.*', '', content)

# Добавляем Antigravity YAML frontmatter если его нет
if not content.startswith('---\nname:'):
    skill_name = dst.split('/')[-2]
    # Ищем description в тексте
    desc_m = re.search(r'(?m)^# (.+)', content)
    desc = desc_m.group(1) if desc_m else skill_name
    header = f'---\nname: {skill_name}\ndescription: "{desc}"\n---\n\n'
    content = header + content

with open(dst, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"  ✅ Записан: {dst}")
PYEOF

    imported=$((imported + 1))
done

echo ""
log "📊 Импортировано скиллов: $imported"
if [ $imported -gt 0 ]; then
    log ""
    log "🔄 Следующий шаг — добавь скилл в MANIFEST.md:"
    log "   ~/.gemini/antigravity/skills/MANIFEST.md"
    log ""
    log "💡 Затем синхронизируй обратно в Cursor:"
    log "   ./tools/sync_cursor_rules.sh --skill $skill_name"
fi
