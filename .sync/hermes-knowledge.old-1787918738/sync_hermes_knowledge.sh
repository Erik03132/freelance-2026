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
PROFILES=(personal sherlock batrak bridge defender english-tutor femida financier health marketer default)
RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'

log(){ echo -e "${CYAN}»${NC} $*"; }
ok(){ echo -e "${GREEN}✓${NC} $*"; }
err(){ echo -e "${RED}✗${NC} $*"; }

ensure_sync_dir(){
    if [[ ! -d "$SYNC_DIR/.git" ]]; then
        mkdir -p "$(dirname "$SYNC_DIR")"
        git clone "$REPO_URL" "$SYNC_DIR" 2>&1 | sed 's/^/  /' || {
            err "Не удалось клонировать $REPO_URL (нужен доступ/токен)"
            return 1
        }
    fi
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

cmd="${1:-status}"

case "$cmd" in
    push)
        ensure_sync_dir || exit 1
        ( cd "$SYNC_DIR" && git pull --rebase --autostash 2>&1 | sed 's/^/  /' )
        collect
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
        ok "Pull выполнен"
        ;;
    status)
        ensure_sync_dir || exit 1
        collect >/dev/null
        ( cd "$SYNC_DIR" && git add -A && git status --short && git reset -q )
        ;;
    dry-run)
        ensure_sync_dir || exit 1
        collect >/dev/null
        ( cd "$SYNC_DIR" && git add -A && git diff --cached --stat && git reset -q )
        ;;
    *)
        echo "Использование: $0 {push|pull|status|dry-run}"
        exit 2
        ;;
esac
