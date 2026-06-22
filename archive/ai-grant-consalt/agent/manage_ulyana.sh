#!/bin/bash

# ============================================================
# Управление Ульяной — AI Grant Consult (порт 8000)
# ============================================================

PROJECT_DIR="/Users/igorvasin/freelance-2026/ai-grant-consalt"
AGENT_DIR="$PROJECT_DIR/agent"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python3"
LOG_DIR="$AGENT_DIR/logs"
PID_FILE_SERVER="$LOG_DIR/server.pid"

mkdir -p "$LOG_DIR"

cleanup() {
    echo "🧹 Завершение процессов Ульяны..."
    
    if [ -f "$PID_FILE_SERVER" ]; then
        PID=$(cat "$PID_FILE_SERVER")
        if pgrep -F "$PID_FILE_SERVER" >/dev/null 2>&1; then
            echo "   Убиваю PID $PID"
            kill -9 "$PID" 2>/dev/null
        fi
        rm -f "$PID_FILE_SERVER"
    fi
    
    pkill -9 -f "ai-grant-consalt/agent/server.py" 2>/dev/null
    sleep 1
    echo "✅ Процессы остановлены."
}

case "$1" in
    start)
        cleanup
        echo ""
        echo "🚀 Запуск Ульяны..."
        cd "$AGENT_DIR"
        
        nohup "$VENV_PYTHON" -u server.py >> "$LOG_DIR/server.log" 2>&1 &
        echo $! > "$PID_FILE_SERVER"
        echo "   Сервер: PID $(cat $PID_FILE_SERVER) → logs/server.log"
        
        echo ""
        echo "====================================="
        echo "👩‍💼 Ульяна работает на порту 8000!"
        echo "   API: http://localhost:8000/api/chat"
        echo "   Проверка: $0 status"
        echo "====================================="
        ;;
    stop)
        cleanup
        ;;
    restart)
        echo "🔄 Перезапуск Ульяны..."
        cleanup
        sleep 1
        exec "$0" start
        ;;
    status)
        echo "📊 Статус Ульяны:"
        echo ""
        
        if [ -f "$PID_FILE_SERVER" ]; then
            PID=$(cat "$PID_FILE_SERVER")
            if pgrep -F "$PID_FILE_SERVER" >/dev/null 2>&1; then
                echo "   🟢 Сервер: РАБОТАЕТ (PID: $PID)"
            else
                echo "   🔴 Сервер: УПАЛ (PID $PID мёртв)"
            fi
        else
            echo "   🔴 Сервер: ОСТАНОВЛЕН (нет PID-файла)"
        fi
        
        echo ""
        echo "   Последние 5 строк лога:"
        tail -5 "$LOG_DIR/server.log" 2>/dev/null | sed 's/^/   │ /'
        ;;
    logs)
        echo "📋 Логи Ульяны (последние 30 строк):"
        echo "─────────────────────────────────"
        tail -30 "$LOG_DIR/server.log" 2>/dev/null
        ;;
    *)
        echo "Использование: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
