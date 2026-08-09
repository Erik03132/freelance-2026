#!/bin/bash
# ============================================================
# 📚 night_reader.sh — Ночной читатель (по аналогии с night_audit.sh)
# ============================================================
# ПРИНЦИП: Разбор инбокса + AI-чтение книг на free-моделях
#
# Архитектура:
#   Фаза 0: sync инбокса с VPS (rsync, если доступен)
#   Фаза 1: конвертация (pandoc/pdftotext) + классификация
#   Фаза 2: book_digest.py — чтение книг (free-каскад OpenRouter)
#   Фаза 3: _catalog.md + отчёт + Telegram
#
# Использование:
#   bash tools/ops/night_reader.sh                  # полный прогон
#   bash tools/ops/night_reader.sh --phase1-only    # только конвертация
#   bash tools/ops/night_reader.sh --no-tg          # без Telegram
#   bash tools/ops/night_reader.sh --dry-run        # ничего не менять
#
# Запуск: launchd com.antigravity.nightreader → 02:30
# ============================================================

set -eu

export PATH="/usr/local/bin:/opt/homebrew/bin:/Users/igorvasin/.npm-global/bin:/Users/igorvasin/Library/Python/3.13/bin:$PATH"

# ============ КОНФИГУРАЦИЯ ============

PROJECT_ROOT="/Users/igorvasin/freelance-2026"
VAULT_DIR="${PROJECT_ROOT}/vault"
INBOX_DIR="${VAULT_DIR}/00-Inbox"
LIBRARY_DIR="${VAULT_DIR}/06-Library"
REPORTS_DIR="${PROJECT_ROOT}/reports"
BOOK_DIGEST="${PROJECT_ROOT}/tools/book_digest.py"
# US-прокси для OpenRouter (локальный форвард через VPS; без него free-модели 403)
BOOK_PROXY="http://Q3NeJXTY:dsBaWh2L@127.0.0.1:64468"

# Личный инбокс Obsidian (iCloud)
PERSONAL_BASE="/Users/igorvasin/Library/Mobile Documents/iCloud~md~obsidian/Documents/Личное"
PERSONAL_INBOX="${PERSONAL_BASE}/01. Входящие"

DATE=$(date +%Y-%m-%d)
TIME_START=$(date +%H:%M:%S)
LOG_FILE="/tmp/night_reader_${DATE}.log"
REPORT_FILE="${REPORTS_DIR}/night_reader_${DATE}.md"

# Telegram (тот же бот, что и ночной аудит)
ENV_FILE="${PROJECT_ROOT}/projects/ai-eggs/.env"
[ -f "${PROJECT_ROOT}/ai-eggs/.env" ] && ENV_FILE="${PROJECT_ROOT}/ai-eggs/.env"  # fallback на старое место
TG_BOT_TOKEN=$(grep "ANGELOCHKA_BOT_TOKEN" "$ENV_FILE" 2>/dev/null | cut -d= -f2)
TG_ADMIN_ID="176203333"
TG_PROXY=$(grep "TELEGRAM_PROXY" "$ENV_FILE" 2>/dev/null | cut -d= -f2 || echo "")

# VPS-инбокс (мост)
VPS_INBOX="/opt/vault_inbox"
VPS_HOST=""
VPS_USER=""
VPS_KEY=""
if [ -f "$ENV_FILE" ]; then
    VPS_HOST=$(grep "^VPS_HOST=" "$ENV_FILE" | cut -d= -f2)
    VPS_USER=$(grep "^VPS_USER=" "$ENV_FILE" | cut -d= -f2)
    VPS_KEY=$(grep "^VPS_SSH_KEY=" "$ENV_FILE" | cut -d= -f2)
    [ -z "$VPS_HOST" ] && VPS_HOST="72.56.38.19"
    [ -z "$VPS_USER" ] && VPS_USER="root"
fi

# Флаги
PHASE1_ONLY=false
NO_TG=false
DRY_RUN=false
NO_SYNC=false
SYNC_OK=0

prev_arg=""
for arg in "$@"; do
    case $arg in
        --phase1-only) PHASE1_ONLY=true ;;
        --no-tg) NO_TG=true ;;
        --dry-run) DRY_RUN=true ;;
        --no-sync) NO_SYNC=true ;;
    esac
done

mkdir -p "$REPORTS_DIR" "$INBOX_DIR"
: > "$LOG_FILE"

# ============ УТИЛИТЫ ============

log() {
    local msg="[$(date '+%H:%M:%S')] $1"
    echo "$msg" | tee -a "$LOG_FILE"
}

send_telegram() {
    [ "$NO_TG" = true ] && return
    local text="$1"
    if [ -n "$TG_BOT_TOKEN" ]; then
        if [ -n "${TG_PROXY:-}" ]; then
            curl -s --connect-timeout 5 --max-time 15 --proxy "${TG_PROXY}" -X POST \
                "https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage" \
                -d "chat_id=${TG_ADMIN_ID}" \
                -d "text=${text}" \
                -d "parse_mode=Markdown" \
                > /dev/null 2>&1 && return || true
        fi
        curl -s --connect-timeout 5 --max-time 15 -X POST \
            "https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage" \
            -d "chat_id=${TG_ADMIN_ID}" \
            -d "text=${text}" \
            -d "parse_mode=Markdown" \
            > /dev/null 2>&1 || true
    fi
}

# ============ НАЧАЛО ============

log "📚 Ночной читатель стартовал: ${DATE} ${TIME_START}"
echo "📚 Ночной читатель — ${DATE}" > "$REPORT_FILE"

# ============================================================
# ФАЗА 0: SYNC ИНБОКСА С VPS
# ============================================================

if [ "$NO_SYNC" = true ]; then
    log "⏭️ --no-sync: пропускаем синхронизацию"
else
    log "🔄 Фаза 0: sync инбокса с VPS..."
    SYNC_OK=0
    TUNNEL_HOST="127.0.0.1"
    TUNNEL_PORT="22001"
    if [ -n "$VPS_HOST" ] && command -v rsync &> /dev/null; then
        # Попытка 1: через SSH-туннель (127.0.0.1:22001)
        if rsync -az --timeout=15 --exclude="*.lock" \
            -e "ssh -i '${VPS_KEY:-~/.ssh/id_rsa}' -o StrictHostKeyChecking=no -o ConnectTimeout=8 -p ${TUNNEL_PORT}" \
            "root@${TUNNEL_HOST}:${VPS_INBOX}/" "$INBOX_DIR/" 2>>"$LOG_FILE"; then
            SYNC_OK=1
            log "  ✅ rsync через туннель (${TUNNEL_HOST}:${TUNNEL_PORT}) → ${INBOX_DIR}"
        # Попытка 2: прямой хост
        elif rsync -az --timeout=15 --exclude="*.lock" \
            -e "ssh -i '${VPS_KEY:-~/.ssh/id_rsa}' -o StrictHostKeyChecking=no -o ConnectTimeout=8" \
            "${VPS_USER}@${VPS_HOST}:${VPS_INBOX}/" "$INBOX_DIR/" 2>>"$LOG_FILE"; then
            SYNC_OK=1
            log "  ✅ rsync прямой (${VPS_USER}@${VPS_HOST}) → ${INBOX_DIR}"
        else
            log "  ⚠️ rsync не удался (туннель и VPS недоступны?) — работаем с локальным инбоксом"
            echo "⚠️ VPS sync не удался — только локальный инбокс" >> "$REPORT_FILE"
        fi
    else
        log "  ⏭️ VPS не настроен — только локальный инбокс"
    fi
fi

# ============================================================
# ФАЗА 1: КОНВЕРТАЦИЯ + КЛАССИФИКАЦИЯ
# ============================================================

echo "" >> "$REPORT_FILE"
echo "## ⚡ Фаза 1: Конвертация и классификация" >> "$REPORT_FILE"

CONVERTED=0
FAILED=0

# Конвертация файлов инбокса в md (на месте)
convert_inbox() {
    local inbox_dir="$1"
    [ -d "$inbox_dir" ] || return
    if [ ! -r "$inbox_dir" ]; then
        log "  ⚠️ НЕТ ДОСТУПА к ${inbox_dir} (TCC?) — проверьте Full Disk Access для launchd-процесса"
        echo "• НЕТ ДОСТУПА (TCC?): ${inbox_dir}" >> "$REPORT_FILE"
        return
    fi
    local tmp_list
    tmp_list=$(mktemp /tmp/night_reader_files_$$.XXXXXX)
    find "$inbox_dir" -maxdepth 1 -type f \( -iname "*.doc" -o -iname "*.docx" -o -iname "*.pdf" -o -iname "*.epub" -o -iname "*.txt" -o -iname "*.html" \) 2>/dev/null | sort > "$tmp_list"
    if [ ! -s "$tmp_list" ]; then
        log "  (${inbox_dir}) нет файлов на конвертацию"
        rm -f "$tmp_list"
        return
    fi
    while IFS= read -r f; do
        base=$(basename "$f")
        ext="${base##*.}"
        case "$ext" in
            docx)
                if command -v pandoc &> /dev/null; then
                    if [ "$DRY_RUN" = true ]; then
                        log "  (dry-run) pandoc: $base"; CONVERTED=$((CONVERTED+1))
                    else
                        pandoc "$f" -t markdown -o "${f%.docx}.md" 2>>"$LOG_FILE" && CONVERTED=$((CONVERTED+1)) && rm -f "$f" || { log "  ❌ pandoc: $base"; FAILED=$((FAILED+1)); }
                    fi
                fi
                ;;
            doc)
                if command -v textutil &> /dev/null; then
                    if [ "$DRY_RUN" = true ]; then
                        log "  (dry-run) textutil: $base"; CONVERTED=$((CONVERTED+1))
                    else
                        textutil -convert txt "$f" -output "${f%.doc}.txt" 2>>"$LOG_FILE" && CONVERTED=$((CONVERTED+1)) && rm -f "$f" || { log "  ❌ textutil: $base"; FAILED=$((FAILED+1)); }
                    fi
                fi
                ;;
            pdf)
                if command -v pdftotext &> /dev/null; then
                    if [ "$DRY_RUN" = true ]; then
                        log "  (dry-run) pdftotext: $base"; CONVERTED=$((CONVERTED+1))
                    else
                        pdftotext "$f" "${f%.pdf}.md" 2>>"$LOG_FILE" && CONVERTED=$((CONVERTED+1)) && rm -f "$f" || { log "  ❌ pdftotext: $base"; FAILED=$((FAILED+1)); }
                    fi
                fi
                ;;
            epub)
                if command -v pandoc &> /dev/null; then
                    if [ "$DRY_RUN" = true ]; then
                        log "  (dry-run) pandoc epub: $base"; CONVERTED=$((CONVERTED+1))
                    else
                        pandoc "$f" -t markdown -o "${f%.epub}.md" 2>>"$LOG_FILE" && CONVERTED=$((CONVERTED+1)) && rm -f "$f" || { log "  ❌ pandoc epub: $base"; FAILED=$((FAILED+1)); }
                    fi
                fi
                ;;
            txt|html)
                if [ "$DRY_RUN" = true ]; then
                    log "  (dry-run) mv: $base"; CONVERTED=$((CONVERTED+1))
                else
                    mv "$f" "${f%.$ext}.md" 2>>"$LOG_FILE" && CONVERTED=$((CONVERTED+1)) || { log "  ❌ mv: $base"; FAILED=$((FAILED+1)); }
                fi
                ;;
        esac
    done < "$tmp_list"
    rm -f "$tmp_list"
}

log "  📥 Агентский инбокс:"
convert_inbox "$INBOX_DIR"
log "  📥 Личный инбокс (Obsidian):"
convert_inbox "$PERSONAL_INBOX"

log "  Конвертировано: ${CONVERTED}, ошибок: ${FAILED}"
echo "• Конвертировано: ${CONVERTED}" >> "$REPORT_FILE"

# ============================================================
# ФАЗА 1b: РАСКЛАДКА ЛИЧНЫХ ЗАМЕТОК ПО ПОЛОЧКАМ (Obsidian)
# ============================================================

SORTED=0
SORT_FAILED=0
SORT_CANDIDATES=0

if [ -d "$PERSONAL_INBOX" ]; then
    if [ ! -r "$PERSONAL_INBOX" ]; then
        log "  ⚠️ НЕТ ДОСТУПА к ${PERSONAL_INBOX} (TCC?) — пропускаю раскладку личных заметок"
        echo "• НЕТ ДОСТУПА (TCC?): ${PERSONAL_INBOX} — раскладка личных заметок пропущена" >> "$REPORT_FILE"
    else
    log "🗂️ Фаза 1b: раскладка личного инбокса ($(find "$PERSONAL_INBOX" -maxdepth 1 -name '*.md' | wc -l | tr -d ' ') md-заметок)..."

    # Мусор: временные файлы (*.base, ~$*) — удаляем
    GARBAGE=$(find "$PERSONAL_INBOX" -maxdepth 1 -type f \( -name "*.base" -o -name "~\$*" \) 2>/dev/null | wc -l | tr -d ' ')
    if [ "$GARBAGE" -gt 0 ]; then
        if [ "$DRY_RUN" = true ]; then
            log "  (dry-run) мусор к удалению: ${GARBAGE} файлов"
        else
            find "$PERSONAL_INBOX" -maxdepth 1 -type f \( -name "*.base" -o -name "~\$*" \) -delete 2>>"$LOG_FILE"
            log "  🧹 Мусор удалён: ${GARBAGE} файлов"
            echo "• Мусор удалён: ${GARBAGE}" >> "$REPORT_FILE"
        fi
    fi

    # Простые правила классификации по имени файла (регистронезависимо)
    sort_by_name() {
        local f="$1"
        local base base_lower
        base=$(basename "$f")
        # iCloud хранит имена в NFD — нормализуем в NFC, чтобы кириллические паттерны матчились
        base_lower=$(echo "$base" | tr '[:upper:]' '[:lower:]' | python3 -c "import sys,unicodedata; print(unicodedata.normalize('NFC', sys.stdin.read()), end='')")
        case "$base_lower" in
            *рецепт*|*суп*|*борщ*|*капуст*|*картофел*|*морков*|*лук*|*шаурм*|*гречк*|*майонез*|*бизе*|*сок*|*треска*|*чечевиц*|*авокад*|*салат*|*рыб*|*кабачк*|*свекл*|*печен*|*запечен*|*солить*|*каша*|*кухн*|*водк*)
                echo "Кухня" ;;
            *гантел*|*спорт*|*тренир*|*бег*|*приседа*)
                echo "СПОРТ" ;;
            *нейросет*|*нейронк*|*ии*|*искусственн*|*промпт*|*monica*|*make*|*gpt*|*озон*|*маркетплейс*|*wb*|*wildberries*)
                echo "Знания" ;;
            *цитат*|*высказыван*|*мысл*|*одиночеств*|*секс*|*философ*)
                echo "Хочу все знать" ;;
            *здоров*|*массаж*|*косметик*|*уход*|*лиц*)
                echo "Здоровье" ;;
            *книг*|*роман*|*произведен*|*book*|*books*)
                echo "КНИГИ" ;;
            *кино*|*фильм*|*сериал*|*боевик*|*нетфликс*|*netflix*|*сезон*)
                echo "Кино" ;;
            *банк*|*кредит*|*вклад*|*деньг*|*налог*)
                echo "Банки" ;;
            *автомобил*|*машин*|*авто*|*ослик*)
                echo "Автомобили" ;;
            *)
                echo "" ;;
        esac
    }

    while IFS= read -r f; do
        base=$(basename "$f")
        case "$base" in
            "Вложенные файлы"|*.png|*.jpg|*.jpeg|*.gif|*.pdf|*.docx|*.epub)
                continue ;;
        esac
        [ -f "$f" ] || continue
        # Большие файлы (>30KB) — книги: их не раскладываем, их читает Фаза 2
        size=$(stat -f%z "$f" 2>/dev/null || echo 0)
        if [ "$size" -gt 30720 ]; then
            log "  📖 ${base} — книга (${size} bytes), оставляю для Фазы 2"
            continue
        fi
        # Daily-заметки (имя = дата YYYY-MM-DD.md) → в корень Личного, рядом с остальными
        if [[ "$base" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}\.md$ ]]; then
            if [ "$DRY_RUN" = true ]; then
                log "  (dry-run) ${base} → корень Личного (daily)"
            else
                mv "$f" "${PERSONAL_BASE}/" 2>>"$LOG_FILE" && log "  🗂️ ${base} → корень (daily)" && SORTED=$((SORTED+1))
            fi
            continue
        fi
        target=$(sort_by_name "$f")
        if [ -n "$target" ]; then
            SORT_CANDIDATES=$((SORT_CANDIDATES+1))
            dest="${PERSONAL_BASE}/${target}"
            mkdir -p "$dest"
            if [ "$DRY_RUN" = true ]; then
                log "  (dry-run) $base → ${target}/"
            else
                if mv "$f" "$dest/" 2>>"$LOG_FILE"; then
                    SORTED=$((SORTED+1))
                    log "  🗂️ ${base} → ${target}/"
                else
                    SORT_FAILED=$((SORT_FAILED+1))
                    log "  ❌ не удалось переместить: ${base}"
                fi
            fi
        fi
    done < <(find "$PERSONAL_INBOX" -maxdepth 1 -type f 2>/dev/null | sort)

    log "  Разложено: ${SORTED} (кандидатов: ${SORT_CANDIDATES}), ошибок: ${SORT_FAILED}"
    echo "• Личные заметки разложено: ${SORTED} / ${SORT_CANDIDATES}" >> "$REPORT_FILE"

    # Проверяем необработанные заметки (не разложены по правилам)
    UNSORTED=$(find "$PERSONAL_INBOX" -maxdepth 1 -type f -name "*.md" ! -name ".*" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$UNSORTED" -gt 0 ]; then
        log "  ⚠️ Осталось без категории: ${UNSORTED}"
        echo "• Без категории (осталось во Входящих): ${UNSORTED}" >> "$REPORT_FILE"
        find "$PERSONAL_INBOX" -maxdepth 1 -type f -name "*.md" ! -name ".*" -exec basename {} \; 2>/dev/null | sed 's/^/  - /' >> "$REPORT_FILE"
    fi
    fi  # конец else (нет доступа к личному инбоксу)
else
    log "  ⏭️ Личный инбокс не найден: ${PERSONAL_INBOX}"
fi

# ============================================================
# ФАЗА 2: ЧТЕНИЕ (BOOK_DIGEST)
# ============================================================

echo "" >> "$REPORT_FILE"
echo "## 📖 Фаза 2: Чтение" >> "$REPORT_FILE"

BOOKS_READ=0
BOOKS_FAILED=0

if [ "$PHASE1_ONLY" = true ]; then
    log "⏭️ --phase1-only: пропускаем чтение"
    echo "⏭️ Фаза чтения пропущена (--phase1-only)" >> "$REPORT_FILE"
else
    # Книги = свежие md-файлы в инбоксе (не обработанные сегодня)
    find "$INBOX_DIR" -maxdepth 1 -type f -name "*.md" -newer /tmp/night_reader_marker 2>/dev/null | sort > /tmp/night_reader_books_$$.txt || true
    # Fallback: если маркер не существует — берём все md старше 1 мин (не только что созданные)
    if [ ! -s /tmp/night_reader_books_$$.txt ] || [ ! -f /tmp/night_reader_marker ]; then
        find "$INBOX_DIR" -maxdepth 1 -type f -name "*.md" -mmin +1 2>/dev/null | sort > /tmp/night_reader_books_$$.txt || true
    fi

    while IFS= read -r f; do
        base=$(basename "$f" .md)
        slug=$(echo "$base" | tr '[:upper:]' '[:lower:]' | tr ' /' '--' | tr -cd 'a-z0-9_-')
        [ -z "$slug" ] && slug="material-$(date +%s)"
        # Пропускаем уже прочитанные
        if [ -f "${LIBRARY_DIR}/books/${slug}/digest.md" ]; then
            log "  ⏭️ Уже прочитано: ${base}"
            continue
        fi
        log "  📖 Читаю: ${base}..."
        if [ "$DRY_RUN" = true ]; then
            log "  (dry-run: пропуск)"
            continue
        fi
        if OPENROUTER_API_KEY="${OPENROUTER_API_KEY:-$(grep '^OPENROUTER_API_KEY=' "${PROJECT_ROOT}/.env" 2>/dev/null | cut -d= -f2)}" BOOK_DIGEST_PROXY="$BOOK_PROXY" \
            python3 "$BOOK_DIGEST" --input "$f" --slug "$slug" --title "$base" 2>>"$LOG_FILE"; then
            BOOKS_READ=$((BOOKS_READ+1))
            rm -f "$f"
        else
            log "  ❌ Ошибка чтения: ${base}"
            BOOKS_FAILED=$((BOOKS_FAILED+1))
        fi
    done < /tmp/night_reader_books_$$.txt
    rm -f /tmp/night_reader_books_$$.txt

    # ---- Личные книги (Obsidian): большие md во Входящих → КНИГИ/<slug>/digest.md ----
    if [ -d "$PERSONAL_INBOX" ]; then
        find "$PERSONAL_INBOX" -maxdepth 1 -type f -name "*.md" -size +30k 2>/dev/null | sort > /tmp/night_reader_pbooks_$$.txt
        while IFS= read -r f; do
            base=$(basename "$f" .md)
            slug=$(echo "$base" | tr '[:upper:]' '[:lower:]' | tr ' /' '--' | tr -cd 'a-z0-9_-')
            [ -z "$slug" ] && slug="material-$(date +%s)"
            if [ -f "${PERSONAL_BASE}/КНИГИ/${slug}/digest.md" ]; then
                log "  ⏭️ Уже прочитана личная книга: ${base}"
                continue
            fi
            log "  📖 Личная книга: ${base}..."
            if [ "$DRY_RUN" = true ]; then
                log "  (dry-run: пропуск)"
                continue
            fi
            if OPENROUTER_API_KEY="${OPENROUTER_API_KEY:-$(grep '^OPENROUTER_API_KEY=' "${PROJECT_ROOT}/.env" 2>/dev/null | cut -d= -f2)}" BOOK_DIGEST_PROXY="$BOOK_PROXY" \
                python3 "$BOOK_DIGEST" --input "$f" --slug "$slug" --title "$base" \
                --out "${PERSONAL_BASE}/КНИГИ/${slug}" 2>>"$LOG_FILE"; then
                BOOKS_READ=$((BOOKS_READ+1))
                rm -f "$f"
            else
                log "  ❌ Ошибка чтения личной книги: ${base}"
                BOOKS_FAILED=$((BOOKS_FAILED+1))
            fi
        done < /tmp/night_reader_pbooks_$$.txt
        rm -f /tmp/night_reader_pbooks_$$.txt
    fi

    if [ "$BOOKS_READ" -eq 0 ] && [ "$BOOKS_FAILED" -eq 0 ]; then
        log "  Инбокс пуст — книги отсутствуют"
        echo "• Книг на прочтение: нет (инбокс пуст)" >> "$REPORT_FILE"
    fi
fi

# ============================================================
# ФАЗА 3: КАТАЛОГ + ОТЧЁТ
# ============================================================

echo "" >> "$REPORT_FILE"
echo "## 📇 Фаза 3: Каталог" >> "$REPORT_FILE"

# Обновляем _catalog.md
CATALOG="${LIBRARY_DIR}/_catalog.md"
{
    echo "# Каталог библиотеки"
    echo ""
    echo "Автообновлён: ${DATE}. Структура: \`Название | Раздел | Slug | Форматы | Статус\`."
    echo ""
    echo "## Книги (books/)"
    for d in "${LIBRARY_DIR}"/books/*/; do
        [ -d "$d" ] || continue
        name=$(basename "$d")
        if [ -f "${d}digest.md" ]; then
            echo "- ${name} | books | digest ✅"
        else
            echo "- ${name} | books | digest ⏳"
        fi
    done
    echo ""
    echo "## Художественная литература (fiction/)"
    for d in "${LIBRARY_DIR}"/fiction/*/; do
        [ -d "$d" ] || continue
        echo "- $(basename "$d")"
    done
    echo ""
    echo "## Медиа (media/)"
    for d in "${LIBRARY_DIR}"/media/*/; do
        [ -d "$d" ] || continue
        echo "- $(basename "$d")"
    done
} > "$CATALOG"

log "✅ Каталог обновлён: ${CATALOG}"

# ============================================================
# ФАЗА 4: NOTEBOOKLM (сканирование блокнотов)
# ============================================================

NB_READ=0
NB_FAILED=0
NB_SCAN_DIR="/tmp/notebooklm_scan"
NB_SCAN_SCRIPT="${PROJECT_ROOT}/tools/ops/notebooklm_scan.py"
NB_LLM_KEY="${OPENROUTER_API_KEY:-$(grep '^OPENROUTER_API_KEY=' "${PROJECT_ROOT}/.env" 2>/dev/null | cut -d= -f2)}"

echo "" >> "$REPORT_FILE"
echo "## 🧠 Фаза 4: NotebookLM" >> "$REPORT_FILE"

if [ "$PHASE1_ONLY" = true ] || [ "$DRY_RUN" = true ]; then
    log "⏭️ Сканирование NotebookLM пропущено"
    echo "⏭️ Сканирование NotebookLM пропущено" >> "$REPORT_FILE"
else
    rm -rf "$NB_SCAN_DIR"
    mkdir -p "$NB_SCAN_DIR"
    log "🔍 Фаза 4: сканирование блокнотов NotebookLM..."
    NB_FILES=$(python3 "$NB_SCAN_SCRIPT" --outdir "$NB_SCAN_DIR" 2>>"$LOG_FILE" || true)
    if [ -z "$NB_FILES" ]; then
        log "  ⏭️ Новых источников нет (или прокси недоступны)"
        echo "• NotebookLM: новых источников нет" >> "$REPORT_FILE"
    else
        while IFS= read -r f; do
            [ -f "$f" ] || continue
            base=$(basename "$f" .md)
            slug=$(echo "$base" | tr '[:upper:]' '[:lower:]' | tr ' /' '--' | tr -cd 'a-z0-9_-')
            [ -z "$slug" ] && slug="nblm-$(date +%s)"
            log "  📖 Читаю из NotebookLM: ${base}..."
            if OPENROUTER_API_KEY="$NB_LLM_KEY" BOOK_DIGEST_PROXY="$BOOK_PROXY" \
                python3 "$BOOK_DIGEST" --input "$f" --slug "$slug" --title "$base" \
                --out "${LIBRARY_DIR}/books/${slug}" 2>>"$LOG_FILE"; then
                NB_READ=$((NB_READ+1))
                rm -f "$f"
            else
                log "  ❌ Ошибка чтения: ${base}"
                NB_FAILED=$((NB_FAILED+1))
            fi
        done <<< "$NB_FILES"
        log "✅ NotebookLM: прочитано ${NB_READ}, ошибок ${NB_FAILED}"
        echo "• NotebookLM: прочитано ${NB_READ}, ошибок ${NB_FAILED}" >> "$REPORT_FILE"
    fi
    rm -rf "$NB_SCAN_DIR"
fi

TIME_END=$(date +%H:%M:%S)

cat >> "$REPORT_FILE" << EOF

---

## 📋 Итоговая сводка

| Метрика | Значение |
|---------|----------|
| 📅 Дата | ${DATE} |
| ⏰ Время | ${TIME_START} → ${TIME_END} |
| 🔄 VPS sync | $([ "$SYNC_OK" = 1 ] && echo "✅" || echo "⏭️") |
| ⚡ Конвертировано | ${CONVERTED} |
| ❌ Ошибок конвертации | ${FAILED} |
| 📖 Книг прочитано | ${BOOKS_READ} |
| 🧠 NotebookLM | ${NB_READ} |
| ❌ Ошибок чтения | ${BOOKS_FAILED} |

> 🤖 Сгенерировано: \`tools/ops/night_reader.sh\` (по аналогии с night_audit.sh)
EOF

log "✅ Ночной читатель завершён: ${TIME_END}"
log "📄 Отчёт: ${REPORT_FILE}"

# ============ TELEGRAM ============

if [ "${BOOKS_READ}" -gt 0 ]; then
    TG_MSG="📚 *Ночной читатель — ${DATE}*

📖 Прочитано книг: *${BOOKS_READ}*
🧠 Из NotebookLM: *${NB_READ}*
⚡ Конвертировано: ${CONVERTED}
❌ Ошибок: $((FAILED + BOOKS_FAILED + NB_FAILED))

📄 \`reports/night_reader_${DATE}.md\`"
else
    TG_MSG="📚 *Ночной читатель — ${DATE}*

⏳ Книг не было (инбокс пуст)
🧠 Из NotebookLM: *${NB_READ}*
⚡ Конвертировано: ${CONVERTED}
❌ Ошибок: $((FAILED + BOOKS_FAILED + NB_FAILED))"
fi

send_telegram "$TG_MSG"
log "📤 Telegram отправлен"
