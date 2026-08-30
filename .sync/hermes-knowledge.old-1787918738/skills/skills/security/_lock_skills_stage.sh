#!/usr/bin/env bash
# lock_skills.sh — write-protect active skills от самоизменения агентом (ES-22)
# Защищает ТОЛЬКО локальные объекты в skills (не симлинки на .agents/skills).
# Симлинки не трогаем: chmod на симлинк меняет цель (общий shared skill) — опасно.
# skill_manage (человек-в-петле) вызывает unlock перед правкой и lock после.
set -euo pipefail

MODE="${1:-lock}"   # lock | unlock
TARGETS=( "$HOME/.config/opencode/skills" "$HOME/.hermes/skills" )

for base in "${TARGETS[@]}"; do
  [ -d "$base" ] || { echo "skip (нет): $base"; continue; }
  echo "== $base =="
  cnt=0
  # 1) топ-уровневые standalone .md (не-симлинк) — защищаем сам файл
  for f in "$base"/*.md; do
    [ -e "$f" ] || continue
    [ -L "$f" ] && { echo "  symlink (пропуск): $f"; continue; }
    if [ "$MODE" = "unlock" ]; then
      chmod u+w "$f"; echo "  UNLOCK: $f"
    else
      chmod a-w "$f"; echo "  LOCK:   $f (444)"; cnt=$((cnt+1))
    fi
  done
  # 2) локальные поддиректории (не симлинки)
  for d in "$base"/*/; do
    [ -d "$d" ] || continue
    if [ -L "${d%/}" ]; then
      echo "  symlink (пропуск, цель защищается отдельно): $(readlink "${d%/}")"
      continue
    fi
    if [ "$MODE" = "unlock" ]; then
      chmod -R u+w "$d"
      echo "  UNLOCK: $d"
    else
      # Блокируем и ФАЙЛЫ, и САМУ ДИРЕКТОРИЮ (a-w).
      # Файл 444 мешает overwrite, но rm требует write-бита ДИРЕКТОРИИ —
      # поэтому папку тоже ставим 555, иначе агент может `rm` и затереть скилл.
      # Любая правка теперь требует осознанного `chmod u+w` (unlock) -> HITL.
      chmod -R a-w "$d"
      echo "  LOCK:   $d (files 444, dir 555)"; cnt=$((cnt+1))
    fi
  done
  echo "  защищено объектов: $cnt"
done
echo "done ($MODE)"
