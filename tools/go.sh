#!/usr/bin/env bash
set -euo pipefail

# G0 — универсальный оркестратор freelance-2026
# Использование: ./tools/go.sh <команда> [аргументы...]

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

usage() {
  echo "G0 — оркестратор freelance-2026"
  echo ""
  echo "Команды:"
  echo "  new project <name>             Создать каркас нового проекта"
  echo "  new skill <domain> <name>      Создать foundation-скилл"
  echo "  new agent <agent-id>           Создать foundation-агента"
  echo "  boot                           Boot sequence: пинг API, проверка агентов"
  echo "  help                           Эта справка"
  echo ""
  echo "Примеры:"
  echo "  ./tools/go.sh new project ai-sales-assistant"
  echo "  ./tools/go.sh new skill code telegram-logger"
  echo "  ./tools/go.sh new agent security-auditor"
  echo "  ./tools/go.sh boot"
}

cmd="${1:-help}"
shift 2>/dev/null || true

case "$cmd" in
  new)
    sub="${1:-}"
    shift 2>/dev/null || true
    case "$sub" in
      project)
        exec "$ROOT/tools/new-project.sh" "$@"
        ;;
      skill)
        exec "$ROOT/tools/new-skill.sh" "$@"
        ;;
      agent)
        exec "$ROOT/tools/new-agent.sh" "$@"
        ;;
      *)
        echo "Error: unknown subcommand 'new $sub'"
        echo ""
        usage
        exit 1
        ;;
    esac
    ;;
  boot)
    echo "=== G0 BOOT ==="
    echo ""

    # Пинг API
    if [ -x "$ROOT/tools/stop-tracking.sh" ]; then
      echo "→ Пинг API..."
      bash "$ROOT/tools/stop-tracking.sh" 2>/dev/null || echo "  (скрипт ping_apis не найден, пропускаем)"
    fi

    # Проверка агентов
    echo ""
    echo "→ Foundation-агенты:"
    if [ -d "$ROOT/foundation/agents" ]; then
      for agent in "$ROOT/foundation/agents"/*/; do
        [ -d "$agent" ] || continue
        agent_name=$(basename "$agent")
        if [ -f "$agent/agent.yaml" ]; then
          echo "  ✅ $agent_name — ARMED"
        else
          echo "  ⚠️  $agent_name — нет agent.yaml"
        fi
      done
    else
      echo "  (нет агентов)"
    fi

    # Проверка скиллов
    echo ""
    echo "→ Foundation-скиллы:"
    if [ -f "$ROOT/foundation/skills/MANIFEST.md" ]; then
      skill_count=$(grep -c '^| ' "$ROOT/foundation/skills/MANIFEST.md" 2>/dev/null || echo "?")
      echo "  ✅ MANIFEST.md найден ($skill_count скиллов)"
    else
      echo "  ⚠️  MANIFEST.md не найден — запусти python3 tools/skills_manifest.py"
    fi

    # Чекпоинт
    echo ""
    echo "→ Чекпоинт:"
    if [ -f "$ROOT/chp.md" ]; then
      echo "  ✅ chp.md: $(head -1 "$ROOT/chp.md")"
    else
      echo "  ⚠️  chp.md не найден"
    fi

    echo ""
    echo "=== SESSION: READY ==="
    ;;
  help|--help|-h)
    usage
    ;;
  *)
    echo "Error: unknown command '$cmd'"
    echo ""
    usage
    exit 1
    ;;
esac
