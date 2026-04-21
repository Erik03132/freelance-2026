#!/bin/bash

SERVER="root@72.56.38.19"
DIR="/Users/igorvasin/freelance-2026/ai-senat"

echo "====================================================="
echo "🏛️  ДЕПЛОЙ МУСТАЯ (Senator AI) НА ОБЛАКО TIMEWEB"
echo "====================================================="
echo "Осторожно: сейчас терминал попросит тебя ввести пароль 2 раза"
echo "Пароль: eHC1ejU@zWqRKW"
echo "Вставляй вслепую и жми Enter."
echo "====================================================="

echo "📦 Загружаю файлы Мустая на сервер..."
rsync -avz --exclude '.git' --exclude 'venv' --exclude '__pycache__' \
      $DIR/ $SERVER:/root/ai-senat/

echo "⚙️  Настраиваю окружение на сервере..."
ssh $SERVER << 'EOF'
cd /root/ai-senat

# Обновляем пакеты для Мустая
python3 -m pip install -r requirements.txt --break-system-packages

# Удаляем старые процессы если есть
pm2 delete mustai-bot 2>/dev/null
pm2 delete mustai-scheduler 2>/dev/null

# Запускаем через PM2 (чтобы он сам перезапускался при падениях)
pm2 start agent/tg_bot.py --interpreter python3 --name "mustai-bot"
pm2 start agent/scheduler.py --interpreter python3 --name "mustai-scheduler"
pm2 save

echo "====================================================="
echo "✅ МУСТАЙ УСПЕШНО РАЗВЕРНУТ В ОБЛАКЕ!"
echo "Он работает 24/7. Команда для просмотра логов: pm2 logs mustai-bot"
echo "====================================================="
EOF
