#!/bin/bash
# ═══════════════════════════════════════════════════════════
# 📜 ХРОНИКА ДНЯ — chronicle.sh
# Добавляет запись в хронику текущего дня.
# Все сессии дня пишут в один файл.
# ═══════════════════════════════════════════════════════════
#
# Использование:
#   bash ~/freelance-2026/tools/chronicle.sh "Что было сделано"
#   bash ~/freelance-2026/tools/chronicle.sh "Что сделано" "session-id-123"
#   bash ~/freelance-2026/tools/chronicle.sh --init "session-id-123"
#   bash ~/freelance-2026/tools/chronicle.sh --status
#
# Примеры:
#   chronicle.sh "✅ Опубликован пост #1 в Своё Подворье (post_id=3)"
#   chronicle.sh "🔧 Создан vk_podvorye_poster.py — скрипт автопостинга VK"
#   chronicle.sh --init "eb7143e3-..."
#

CHRONICLES_DIR="$HOME/freelance-2026/chronicles"
TODAY=$(date +%Y-%m-%d)
CHRONICLE_FILE="${CHRONICLES_DIR}/chronicle_${TODAY}.md"
TIME_NOW=$(date +%H:%M)

mkdir -p "$CHRONICLES_DIR"

# --- Инициализация файла дня (если не существует) ---
init_chronicle() {
    local session_id="${1:-unknown}"
    if [ ! -f "$CHRONICLE_FILE" ]; then
        cat > "$CHRONICLE_FILE" << EOF
# 📜 ХРОНИКА ДНЯ: $(date +%d.%m.%Y) ($(LC_TIME=ru_RU.UTF-8 date +%A 2>/dev/null || date +%A))

> Автоматическая хроника всех сессий за день.
> Каждая сессия дописывает сюда свои действия в реальном времени.

---

## 🕐 Сессия ${TIME_NOW} | \`${session_id:0:8}\`

EOF
        echo "📜 Хроника дня создана: $CHRONICLE_FILE"
    else
        # Файл существует — добавляем новую сессию
        cat >> "$CHRONICLE_FILE" << EOF

---

## 🕐 Сессия ${TIME_NOW} | \`${session_id:0:8}\`

EOF
        echo "📜 Новая сессия добавлена в хронику"
    fi
}

# --- Добавить запись ---
add_entry() {
    local message="$1"
    
    # Если файл не существует — создаём
    if [ ! -f "$CHRONICLE_FILE" ]; then
        init_chronicle "auto"
    fi
    
    echo "- **${TIME_NOW}** — ${message}" >> "$CHRONICLE_FILE"
    echo "📝 Записано в хронику: ${message:0:60}..."
}

# --- Показать статус ---
show_status() {
    if [ -f "$CHRONICLE_FILE" ]; then
        echo "📜 Хроника дня: $CHRONICLE_FILE"
        echo "Записей: $(grep -c '^\- \*\*' "$CHRONICLE_FILE" 2>/dev/null || echo 0)"
        echo "Сессий: $(grep -c '^## 🕐' "$CHRONICLE_FILE" 2>/dev/null || echo 0)"
        echo ""
        tail -10 "$CHRONICLE_FILE"
    else
        echo "📜 Хроника за сегодня не создана"
    fi
}

# --- Main ---
case "$1" in
    --init)
        init_chronicle "$2"
        ;;
    --status)
        show_status
        ;;
    "")
        echo "Usage: chronicle.sh \"Что сделано\" [session-id]"
        echo "       chronicle.sh --init [session-id]"
        echo "       chronicle.sh --status"
        ;;
    *)
        add_entry "$1"
        ;;
esac
