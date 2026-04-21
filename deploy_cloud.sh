#!/bin/bash

SERVER="root@72.56.38.19"

echo "====================================================="
echo "☁️  ДЕПЛОЙ АГЕНТОВ (Анжела) НА ОБЛАКО TIMEWEB"
echo "====================================================="
echo "Осторожно: сейчас терминал попросит тебя ввести пароль"
echo "Пароль SSH лежит у тебя в .credentials_vezemcip.md"
echo "При вводе пароля символы на экране НЕ появляются - это норм, просто жми Enter."
echo "====================================================="

# 1. Копируем всё на сервер (кроме тяжелого мусора и модулей)
echo "📦 Загружаю файлы проекта на сервер..."
rsync -avz --exclude '.git' --exclude 'node_modules' --exclude '.venv' \
      --exclude 'tmp' --exclude '*.dmg' --exclude 'Downloads' \
      --exclude 'agent-lab/.venv' --exclude 'ai-eggs/.venv' \
      /Users/igorvasin/freelance-2026/ $SERVER:/root/antigravity/

# 2. Настраиваем окружение прямо на сервере
echo "⚙️  Синхронизация завершена. Ставлю программы на сервер..."
ssh $SERVER << 'EOF'
  echo "🚀 Подключился к Ubuntu! Обновляю пакеты..."
  apt-get update -y > /dev/null 2>&1

  # Ставим Node.js (если нет)
  if ! command -v npm &> /dev/null; then
      echo "📦 Устанавливаю Node.js..."
      curl -fsSL https://deb.nodesource.com/setup_20.x | bash - > /dev/null 2>&1
      apt-get install -y nodejs > /dev/null 2>&1
  fi
  
  # Ставим PM2 для вечной работы в фоне
  if ! command -v pm2 &> /dev/null; then
      echo "📦 Устанавливаю PM2..."
      npm install -g pm2 > /dev/null 2>&1
  fi

  # Ставим Python 3 VENV
  apt-get install -y python3-venv python3-pip > /dev/null 2>&1

  echo "🐍 Настраиваю Python-мозги (angel-backend)..."
  cd /root/antigravity/angel-backend
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -q -r requirements.txt || echo "Requirements не найдены, пропуск"
  
  echo "💻 Настраиваю Node.js-руки (MCP-серверы)..."
  cd /root/antigravity/freelance-agent
  npm install --silent
  
  echo "====================================================="
  echo "✅ СЕРВЕР ПОЛНОСТЬЮ ГОТОВ К 24/7 РАБОТЕ!"
  echo "Осталось только запустить агентов через PM2."
  echo "====================================================="
EOF
