#!/bin/bash
# Управление ботом Мустай (Senator AI)
# Использование: bash manage_mustai.sh {start|stop|status|pipeline}

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_DIR="$SCRIPT_DIR/agent"
LOG_DIR="$AGENT_DIR/logs"
VENV="$SCRIPT_DIR/venv/bin/python3"
mkdir -p "$LOG_DIR"

# Фоллбэк на системный python если venv нет
if [ ! -f "$VENV" ]; then
    VENV=$(which python3)
fi

case "$1" in
    start)
        echo "🏛️ Запуск Мустая..."
        
        # Проверяем, не запущен ли уже
        if pgrep -f "tg_bot.py" > /dev/null 2>&1; then
            echo "⚠️ Бот уже запущен!"
            pgrep -af "tg_bot.py"
            exit 1
        fi
        
        # Запуск бота
        echo "  🤖 Запуск Telegram-бота..."
        nohup $VENV "$AGENT_DIR/tg_bot.py" > "$LOG_DIR/bot.log" 2>&1 &
        BOT_PID=$!
        echo "  ✅ Бот запущен (PID: $BOT_PID)"
        
        # Запуск планировщика
        echo "  🕐 Запуск планировщика..."
        nohup $VENV "$AGENT_DIR/scheduler.py" > "$LOG_DIR/scheduler.log" 2>&1 &
        SCHED_PID=$!
        echo "  ✅ Планировщик запущен (PID: $SCHED_PID)"
        
        echo ""
        echo "🏛️ Мустай работает!"
        echo "   Бот:          PID $BOT_PID"
        echo "   Планировщик:  PID $SCHED_PID"
        echo "   Логи бота:    $LOG_DIR/bot.log"
        echo "   Логи планир.: $LOG_DIR/scheduler.log"
        ;;
        
    stop)
        echo "🛑 Остановка Мустая..."
        pkill -f "tg_bot.py" 2>/dev/null && echo "  ✅ Бот остановлен" || echo "  ⚠️ Бот не был запущен"
        pkill -f "scheduler.py" 2>/dev/null && echo "  ✅ Планировщик остановлен" || echo "  ⚠️ Планировщик не был запущен"
        rm -f "$AGENT_DIR/logs/bot.lock" 2>/dev/null
        echo "🏛️ Мустай остановлен."
        ;;
        
    status)
        echo "📊 Статус Мустая:"
        echo ""
        
        if pgrep -f "tg_bot.py" > /dev/null 2>&1; then
            echo "  🤖 Бот:          ✅ РАБОТАЕТ"
            pgrep -af "tg_bot.py" | head -1
        else
            echo "  🤖 Бот:          ❌ НЕ ЗАПУЩЕН"
        fi
        
        if pgrep -f "scheduler.py" > /dev/null 2>&1; then
            echo "  🕐 Планировщик:  ✅ РАБОТАЕТ"
            pgrep -af "scheduler.py" | head -1
        else
            echo "  🕐 Планировщик:  ❌ НЕ ЗАПУЩЕН"
        fi
        
        echo ""
        echo "  📁 Логи:"
        if [ -f "$LOG_DIR/bot.log" ]; then
            echo "     Бот (последние строки):"
            tail -3 "$LOG_DIR/bot.log" | sed 's/^/     /'
        fi
        if [ -f "$LOG_DIR/scheduler.log" ]; then
            echo "     Планировщик (последние строки):"
            tail -3 "$LOG_DIR/scheduler.log" | sed 's/^/     /'
        fi
        ;;
        
    pipeline)
        echo "⚙️ Ручной запуск pipeline..."
        $VENV "$AGENT_DIR/senator_core.py" --pipeline
        ;;
        
    restart)
        echo "🔄 Перезапуск Мустая..."
        $0 stop
        sleep 2
        $0 start
        ;;
        
    *)
        echo "🏛️ Мустай — AI-помощник сенатора"
        echo ""
        echo "Использование: bash $0 {start|stop|status|pipeline|restart}"
        echo ""
        echo "  start     — Запустить бота и планировщик"
        echo "  stop      — Остановить всё"
        echo "  status    — Проверить статус"
        echo "  pipeline  — Ручной запуск генерации инициативы"
        echo "  restart   — Перезапуск"
        ;;
esac
