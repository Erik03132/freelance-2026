#!/usr/bin/env bash
# ============================================================================
# 🔄 Hermes Knowledge Sync — Mac <-> VPS (git-backed, secrets excluded)
# ============================================================================
# Синхронизирует ТОЛЬКО текстовые знания:
#   - user-level skills:   ~/.hermes/skills/**
#   - profile SOUL.md/USER.md/skills/memories
# НЕ трогает: config.yaml, auth.json, *.db, cache/, logs/, lsp/ (исключены .gitignore)
#
# Режимы:
#   push       собрать локальные знания -> репо -> commit -> push
#   pull       pull --rebase -> применить из репо в ~/.hermes
#   status     что расходится (без записи)
#   dry-run    что изменится при pull (без записи)
#
# Локальный checkout репо: $HERMES_SYNC_DIR (по умолчанию см. ниже).
# ============================================================================

set -uo pipefail

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
HOST="$(uname -s)"
if [[ "$HOST" == "Darwin" ]]; then
    SYNC_DIR="${HERMES_SYNC_DIR:-$HOME/freelance-2026/.sync/hermes-knowledge}"
else
    SYNC_DIR="${HERMES_SYNC_DIR:-/root/hermes-sync}"
fi
REPO_URL="${HERMES_SYNC_REPO:-https://github.com/Erik03132/hermes-knowledge-sync.git}"
PROFILES=(personal chief sherlock batrak bridge defender english-tutor femida financier health marketer default)
# Файлы СОСТОЯНИЯ проекта (SSoT задач), которые раньше выпадали из синхронизации.
# ARCH-002-fix: теперь они тоже ездят Mac<->VPS через тот же git-репо.
if [[ "$(uname -s)" == "Darwin" ]]; then
    WORKSPACE="${HERMES_SYNC_WORKSPACE:-$HOME/freelance-2026}"
else
    WORKSPACE="${HERMES_SYNC_WORKSPACE:-/root/freelance-2026}"
fi
STATE_FILES=(ACTIVE_TASKS.md SESSION_LATEST.md chp.md)
RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'

log(){ echo -e "${CYAN}»${NC} $*"; }
ok(){ echo -e "${GREEN}✓${NC} $*"; }
err(){ echo -e "${RED}✗${NC} $*"; }

ensure_sync_dir(){
    if [[ -d "$SYNC_DIR/.git" ]]; then
        return 0
    fi
    if [[ -e "$SYNC_DIR" ]]; then
        # Старая копия без .git — архивируем и клонируем заново (содержимое
        # всё равно пересобирается collect-ом из HERMES_HOME/WORKSPACE).
        local bak="$SYNC_DIR.old-$(date +%s)"
        log "Папка sync без .git — архивирую в $bak и клонирую"
        mv "$SYNC_DIR" "$bak" || { err "Не удалось переименовать $SYNC_DIR"; return 1; }
    fi
    mkdir -p "$(dirname "$SYNC_DIR")"
    git clone "$REPO_URL" "$SYNC_DIR" 2>&1 | sed 's/^/  /' || {
        err "Не удалось клонировать $REPO_URL (нужен доступ/токен)"
        return 1
    }
    return 0
}

# Копируем БЕЗОПАСНЫЙ снимок из Hermes -> репо (push-сторона)
collect(){
    log "Сбор безопасного снимка из $HERMES_HOME"
    rm -rf "$SYNC_DIR/skills" "$SYNC_DIR/profiles"
    mkdir -p "$SYNC_DIR/skills" "$SYNC_DIR/profiles"
    # Копируем СОДЕРЖИМОЕ skills/*, а не саму папку (иначе skills/skills/...)
    cp -R "$HERMES_HOME/skills/." "$SYNC_DIR/skills/" 2>/dev/null || true
    for p in "${PROFILES[@]}"; do
        src="$HERMES_HOME/profiles/$p"
        [[ -d "$src" ]] || continue
        dst="$SYNC_DIR/profiles/$p"
        mkdir -p "$dst"
        [[ -f "$src/SOUL.md" ]]   && cp "$src/SOUL.md"   "$dst/"
        [[ -f "$src/USER.md" ]]   && cp "$src/USER.md"   "$dst/"
        [[ -d "$src/skills" ]]    && { mkdir -p "$dst/skills"; cp -R "$src/skills/." "$dst/skills/" 2>/dev/null || true; }
        [[ -d "$src/memories" ]]  && { mkdir -p "$dst/memories"; cp -R "$src/memories/." "$dst/memories/" 2>/dev/null || true; }
    done
    ok "Снимок собран в $SYNC_DIR"
}

# Применяем из репо -> Hermes (pull-сторона). Не перезаписывает исключённое.
apply(){
    log "Применение снимка в $HERMES_HOME"
    # user-level skills — дополняем (merge), не удаляем лишнее
    [[ -d "$SYNC_DIR/skills" ]] && cp -R "$SYNC_DIR/skills/." "$HERMES_HOME/skills/" 2>/dev/null || true
    for p in "${PROFILES[@]}"; do
        src="$SYNC_DIR/profiles/$p"
        [[ -d "$src" ]] || continue
        dst="$HERMES_HOME/profiles/$p"
        mkdir -p "$dst"
        [[ -f "$src/SOUL.md" ]]   && cp "$src/SOUL.md"   "$dst/"
        [[ -f "$src/USER.md" ]]   && cp "$src/USER.md"   "$dst/"
        [[ -d "$src/skills" ]]    && mkdir -p "$dst/skills" && cp -R "$src/skills/." "$dst/skills/" 2>/dev/null || true
        [[ -d "$src/memories" ]]  && mkdir -p "$dst/memories" && cp -R "$src/memories/." "$dst/memories/" 2>/dev/null || true
    done
    ok "Применено в $HERMES_HOME"
}

# === ARCH-002-fix: синхронизация файлов состояния проекта (SSoT задач) ===
# Собираем STATE_FILES из WORKSPACE -> репо (push-сторона).
collect_statefiles(){
    log "Сбор файлов состояния из $WORKSPACE"
    mkdir -p "$SYNC_DIR/state"
    for f in "${STATE_FILES[@]}"; do
        src="$WORKSPACE/$f"
        [[ -f "$src" ]] && cp "$src" "$SYNC_DIR/state/$f" 2>/dev/null || true
    done
    ok "Файлы состояния собраны в $SYNC_DIR/state"
}

# Применяем STATE_FILES из репо -> WORKSPACE (pull-сторона). Мёрж по секциям
# не делаем — каноничная копия = та, что в репо (последний push побеждает).
# Это безопасно, т.к. push вызывается при /finish-day и на VPS по cron.
apply_statefiles(){
    log "Применение файлов состояния в $WORKSPACE"
    for f in "${STATE_FILES[@]}"; do
        src="$SYNC_DIR/state/$f"
        [[ -f "$src" ]] || continue
        cp "$src" "$WORKSPACE/$f" 2>/dev/null || true
    done
    ok "Файлы состояния применены в $WORKSPACE"
}

cmd="${1:-status}"

case "$cmd" in
    push)
        ensure_sync_dir || exit 1
        ( cd "$SYNC_DIR" && git pull --rebase --autostash 2>&1 | sed 's/^/  /' )
        collect
        collect_statefiles
        ( cd "$SYNC_DIR"
          git add -A
          if git diff --cached --quiet; then
              log "Нет изменений для push"
          else
              git -c user.email=hermes@local -c user.name=Hermes \
                  commit -q -m "Sync $(date '+%Y-%m-%d %H:%M')"
              git push 2>&1 | sed 's/^/  /' && ok "Push выполнен"
          fi
        )
        ;;
    pull)
        ensure_sync_dir || exit 1
        ( cd "$SYNC_DIR" && git pull --rebase 2>&1 | sed 's/^/  /' ) || exit 1
        apply
        apply_statefiles
        ok "Pull выполнен"
        ;;
    status)
        ensure_sync_dir || exit 1
        collect >/dev/null
        collect_statefiles >/dev/null
        ( cd "$SYNC_DIR" && git add -A && git status --short && git reset -q )
        ;;
    dry-run)
        ensure_sync_dir || exit 1
        collect >/dev/null
        collect_statefiles >/dev/null
        ( cd "$SYNC_DIR" && git add -A && git diff --cached --stat && git reset -q )
        ;;
    *)
        echo "Использование: $0 {push|pull|status|dry-run}"
        exit 2
        ;;
esac
