#!/usr/bin/env bash
# AG-3: Eval gate — прогон eval suite проекта перед мержем/коммитом.
# Провал любого eval → exit 1 (блокировка). Порог: eval обязан проходить
# на 100% (PASSED в выводе). Кейсы с LLM-судьями — отдельные (см. --skip-llm).
#
# Использование:
#   bash tools/eval_gate.sh                 # все eval проектов (медленно)
#   bash tools/eval_gate.sh --project ai-eggs
#   bash tools/eval_gate.sh --quick         # только детерминированные (без LLM)
#   bash tools/eval_gate.sh --list          # список доступных eval
#
# Интеграция в /goal (шаг 4) и в Two-axis Review перед коммитом.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

SKIP_PATTERNS='(voice_exam|eval_levitan)'  # требуют внешние сервисы/венв

KNOWN_EVALS=(
  "$ROOT/tests/eval_trajectory.py"
  "$ROOT/freelance-agent/.agent/agents/ai_defender/tests/eval_ai_defender.py"
  "$ROOT/projects/ai-eggs/tests/eval_angela.py"
  "$ROOT/projects/hh-ai-agent/tests/eval_batrak.py"
  "$ROOT/projects/sinergy/tests/eval_sinergy.py"
  "$ROOT/projects/ai-scout/tests/eval_ai_scout.py"
  "$ROOT/my-project/tests/eval_auto_reels.py"
  "$ROOT/agent-lab/tests/eval_agent_lab.py"
)

list_evals() {
  find "$ROOT" -name "eval_*.py" \
    -not -path "*/node_modules/*" -not -path "*/.git/*" \
    -not -path "*/.venv/*" -not -path "*/site-packages/*" 2>/dev/null
}

run_one() {
  local f="$1"
  local out
  out="$(python3 "$f" 2>&1)"
  local rc=$?
  if [ $rc -eq 0 ] && echo "$out" | grep -qiE "PASSED|OK|все пройдены|✅"; then
    echo "  ✅ $(basename "$f")"
    return 0
  fi
  echo "  ❌ $(basename "$f") (exit=$rc)"
  echo "$out" | tail -5 | sed 's/^/     /'
  return 1
}

main() {
  local mode="all" project=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --list) list_evals; return 0 ;;
      --quick) mode="quick" ;;
      --project) project="$2"; shift ;;
      *) echo "Неизвестный флаг: $1" >&2; return 2 ;;
    esac
    shift
  done

  local files=()
  if [ -n "$project" ]; then
    files=("$ROOT/$project/tests/eval_"*.py)
  elif [ "$mode" = "quick" ]; then
    for f in "${KNOWN_EVALS[@]}"; do [ -f "$f" ] && files+=("$f"); done
  else
    mapfile -t files < <(list_evals)
  fi

  if [ ${#files[@]} -eq 0 ]; then
    echo "Eval suite не найдены (--project '$project'?)" >&2
    return 2
  fi

  echo "Eval gate: ${#files[@]} suite, mode=$mode"
  local failed=0 total=0
  for f in "${files[@]}"; do
    if echo "$f" | grep -qE "$SKIP_PATTERNS"; then
      echo "  ⏭  $(basename "$f") (skip: требует внешние сервисы)"
      continue
    fi
    total=$((total + 1))
    run_one "$f" || failed=$((failed + 1))
  done

  echo "---"
  if [ "$failed" -gt 0 ]; then
    echo "❌ EVAL GATE FAILED: $failed/$total (коммит/мерж ЗАБЛОКИРОВАН)"
    return 1
  fi
  echo "✅ EVAL GATE PASSED: $total/$total"
  return 0
}

main "$@"
