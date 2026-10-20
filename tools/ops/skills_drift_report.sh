#!/usr/bin/env bash
# skills_drift_report.sh — drift-отчёт: скиллы OpenCode vs Hermes.
# Цель: 0 смысловых дублей между системами (drift-аудит 2026-10-10).
# Read-only, идемпотентен, exit 0.
#
# Использование:
#   skills_drift_report.sh [--out FILE]

set -euo pipefail

OUT="$(git -C "$HOME/freelance-2026" rev-parse --show-toplevel 2>/dev/null || echo "$HOME/freelance-2026")/logs/skills_drift_latest.md"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --out) OUT="$2"; shift 2 ;;
    --help|-h)
      echo "skills_drift_report.sh [--out FILE] — сравнение скиллов OpenCode и Hermes"
      echo "Пример: skills_drift_report.sh --out ~/Desktop/drift.md"
      exit 0 ;;
    *) echo "Неизвестный аргумент: $1" >&2; exit 1 ;;
  esac
done

OC="$HOME/.config/opencode/skills"
HERMES="$HOME/.hermes/skills"
WRAPPERS="$HOME/.hermes/skills" # обёртки не считаем дублями

mkdir -p "$(dirname "$OUT")"

list_oc() {
  for d in "$OC"/*/; do
    if [ -f "$d/SKILL.md" ]; then basename "$d"; fi
  done
  for d in "$OC"/*/*/; do
    if [ -f "$d/SKILL.md" ]; then basename "$d"; fi
  done
}
list_hermes() { find "$HERMES" -name SKILL.md -not -path "*/.archive/*" -not -name "*.bak-*" | xargs -n1 dirname | xargs -n1 basename; }

find_wrapper_dirs() {
  grep -rl "Обёртка: мастер перенесён" "$HERMES" --include=SKILL.md 2>/dev/null | xargs -n1 dirname | xargs -n1 basename
}

list_oc | sort -u > /tmp/_oc_skills.txt
list_hermes | sort -u > /tmp/_hermes_skills.txt
find_wrapper_dirs | sort -u > /tmp/_wrappers.txt

dup=$(comm -12 /tmp/_oc_skills.txt /tmp/_hermes_skills.txt | comm -23 - /tmp/_wrappers.txt || true)
hermes_only=$(comm -23 /tmp/_hermes_skills.txt /tmp/_oc_skills.txt)
oc_only=$(comm -13 /tmp/_hermes_skills.txt /tmp/_oc_skills.txt)

{
  echo "# Skills drift report — $(date '+%Y-%m-%d %H:%M')"
  echo
  echo "OpenCode: $(wc -l < /tmp/_oc_skills.txt | tr -d ' ') · Hermes: $(wc -l < /tmp/_hermes_skills.txt | tr -d ' ') · обёрток: $(wc -l < /tmp/_wrappers.txt | tr -d ' ')"
  echo
  echo "## ⚠️ Дубли (одинаковое имя в обеих системах, не обёртки)"
  if [ -n "$dup" ]; then echo "$dup" | sed 's/^/- /'; else echo "Нет ✅"; fi
  echo
  echo "## 📥 Только в Hermes — кандидаты на импорт в OpenCode"
  if [ -n "$hermes_only" ]; then echo "$hermes_only" | sed 's/^/- /'; else echo "Нет"; fi
  echo
  echo "## 🆕 Только в OpenCode — проверить, не нужен ли в Hermes"
  if [ -n "$oc_only" ]; then echo "$oc_only" | head -40 | sed 's/^/- /'; else echo "Нет"; fi
  echo
  echo "---"
  echo "Генератор: tools/ops/skills_drift_report.sh · запуск: воскресный expert-skills-updater"
} > "$OUT"

echo "OK -> $OUT"
exit 0
