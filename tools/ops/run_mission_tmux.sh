#!/usr/bin/env bash
# run_mission_tmux.sh — Запуск долгой автономной миссии Hermes в изолированном tmux
# Usage: ./run_mission_tmux.sh <session_name> <profile> "<prompt>"

SESSION_NAME="${1:-hermes-mission}"
PROFILE="${2:-default}"
PROMPT="${3:-}"

if [ -z "$PROMPT" ]; then
  echo "Ошибка: укажите prompt для миссии."
  echo "Пример: $0 deep-research sherlock 'Сделай детальный аудит репозиториев Nous Research'"
  exit 1
fi

# Проверяем наличие tmux
if ! command -v tmux &> /dev/null; then
  echo "Ошибка: tmux не установлен."
  exit 1
fi

# Убиваем старую сессию с таким же именем, если есть
tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true

# Создаем новую сессию в фоне и запускаем hermes agent
tmux new-session -d -s "$SESSION_NAME" "hermes --profile '$PROFILE' chat -q \"$PROMPT\"; echo '--- MISSION COMPLETED ---'; sleep 60"

echo "✅ Миссия запущена в tmux:"
echo "   Сессия: $SESSION_NAME"
echo "   Профиль: $PROFILE"
echo "   Подключиться: tmux attach -t $SESSION_NAME"
echo "   Логи: tmux capture-pane -pt $SESSION_NAME"
