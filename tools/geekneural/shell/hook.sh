#!/usr/bin/env bash
# GeekNeural shell-hook (уровень 1)
# ===================================================================
# Обёртка чтения файлов через движок дедупликации.
# Работает в bash и zsh.
# Источниките:  source /path/to/shell/hook.sh
# Использование:
#   gn read path/to/file.py        # дедуп-чтение (как cat, но с кешем)
#   gn read path/to/file.py --force
#   gn stats                        # экономия токенов в сессии
#   gn clear                        # сброс кеша
#   gn cat  path/to/file.py         # алиас для read
# ===================================================================

# --- портативное определение каталога скрипта (bash + zsh) ---
if [ -n "${BASH_VERSION:-}" ]; then
  _gn_src="${BASH_SOURCE[0]}"
elif [ -n "${ZSH_VERSION:-}" ]; then
  _gn_src="$0"
else
  _gn_src="$0"
fi
_gn_here="$(cd "$(dirname "$_gn_src")" 2>/dev/null && pwd)"
# Корень проекта — папка, содержащая core/dedup.py (устойчиво к глубине).
if [ -z "${GEEKNEURAL_ROOT:-}" ]; then
  _gn_dir="$_gn_here"
  while [ ! -f "$_gn_dir/core/dedup.py" ] && [ "$_gn_dir" != "/" ]; do
    _gn_dir="$(dirname "$_gn_dir")"
  done
  export GEEKNEURAL_ROOT="$_gn_dir"
fi
unset _gn_src _gn_here _gn_dir

# Если сессия не задана — создаём по терминалу (tty) или оболочке.
if [ -z "${GEEKNEURAL_SESSION:-}" ]; then
  export GEEKNEURAL_SESSION="shell-${TTY:-$$}"
fi

_gn_cli() {
  PYTHONPATH="$GEEKNEURAL_ROOT" python3 "$GEEKNEURAL_ROOT/core/cli.py" "$@"
}

gn() {
  local cmd="${1:-}"
  shift || true
  case "$cmd" in
    read|read-text|stats|clear)
      _gn_cli "$cmd" "$@"
      ;;
    cat)
      _gn_cli read "$@"
      ;;
    *)
      echo "GeekNeural: неизвестная команда '$cmd'" >&2
      echo "Доступно: gn read|cat|stats|clear" >&2
      return 1
      ;;
  esac
}

# bash-preexec-хук: перехватывает `cat <file>` и заменяет на дедуп-чтение.
# Включается опционально, чтобы не ломать пайплайны.
gn_intercept_on() {
  cat() {
    if [ "$#" -eq 1 ] && [ -f "$1" ]; then
      _gn_cli read "$1"
    else
      command cat "$@"
    fi
  }
}

# Автодополнение (только bash)
if [ -n "${BASH_VERSION:-}" ]; then
  _gen_gn_completions() {
    local cur="${COMP_WORDS[COMP_CWORD]}"
    COMPREPLY=( $(compgen -W "read cat stats clear" -- "$cur") )
  }
  complete -F _gen_gn_completions gn
fi
