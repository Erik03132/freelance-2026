#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# ☁️  DEPLOY v2.0 — Деплой ВСЕХ агентов на Timeweb VDS
# ═══════════════════════════════════════════════════════════════
# VPS: root@72.56.38.19 (Timeweb Cloud)
# 
# ЧТО ДЕЛАЕТ:
#   1. rsync кода (БЕЗ venv/node_modules — они собираются на сервере!)
#   2. Пересоздание venv на сервере (Linux-native, не маковские симлинки)
#   3. Перезапуск ВСЕХ PM2 процессов через ecosystem.config.cjs
#   4. Health-check всех сервисов
#
# ИСПОЛЬЗОВАНИЕ: bash deploy_cloud.sh
# ═══════════════════════════════════════════════════════════════

SERVER="root@72.56.38.19"

echo "====================================================="
echo "☁️  ДЕПЛОЙ АГЕНТОВ v2.0 НА ОБЛАКО TIMEWEB"
echo "====================================================="
echo "Пароль SSH: см. .credentials_vezemcip.md"
echo "При вводе пароля символы НЕ появляются — это норм."
echo "====================================================="

# ═══════════════════════════════════════════════
# ШАГ 1: Синхронизируем КОД (без venv и тяжёлых файлов)
# ═══════════════════════════════════════════════
echo ""
echo "📦 ШАГ 1: Загружаю файлы проекта на сервер..."
rsync -avz \
      --exclude '.git' \
      --exclude 'node_modules' \
      --exclude '.venv' \
      --exclude 'venv' \
      --exclude '.server_venv' \
      --exclude '__pycache__' \
      --exclude '*.pyc' \
      --exclude 'tmp' \
      --exclude '*.dmg' \
      --exclude 'Downloads' \
      --exclude 'logs/' \
      --exclude '*.pt' \
      --exclude '*.aiff' \
      --exclude 'data/bitrix_scans/' \
      --exclude 'data/sandbox_scans/' \
      /Users/igorvasin/freelance-2026/ $SERVER:/root/antigravity/

# ═══════════════════════════════════════════════
# ШАГ 2: Настраиваем окружение НА СЕРВЕРЕ
# ═══════════════════════════════════════════════
echo ""
echo "⚙️  ШАГ 2: Настраиваю окружение на сервере..."
ssh $SERVER << 'EOF'
  set -e
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

  # ─────────────────────────────────────────────
  # 🐍 angel-backend: venv (основной бэкенд)
  # ─────────────────────────────────────────────
  echo "🐍 [1/3] Настраиваю angel-backend venv..."
  cd /root/antigravity/angel-backend
  if [ ! -f ".venv/bin/python" ] || [ -L ".venv/bin/python" ] && [ ! -e ".venv/bin/python" ]; then
      echo "  → Пересоздаю .venv (битый или отсутствует)..."
      rm -rf .venv
      python3 -m venv .venv
  fi
  .venv/bin/pip install -q -r requirements.txt 2>/dev/null || echo "  ⚠️ requirements.txt не найден, пропуск"

  # ─────────────────────────────────────────────
  # 🐍 ai-senat: venv (Мустай)
  # ─────────────────────────────────────────────
  echo "🐍 [2/3] Настраиваю ai-senat venv..."
  cd /root/antigravity/ai-senat
  if [ ! -f "venv/bin/python3" ] || [ -L "venv/bin/python3" ] && [ ! -e "venv/bin/python3" ]; then
      echo "  → Пересоздаю venv (битый или отсутствует)..."
      rm -rf venv
      python3 -m venv venv
  fi
  venv/bin/pip install -q aiogram python-dotenv httpx requests google-generativeai 2>/dev/null

  # ─────────────────────────────────────────────
  # 🐍 ai-eggs: .server_venv (Анжела бот + автопилот)
  # ─────────────────────────────────────────────
  echo "🐍 [3/3] Настраиваю ai-eggs .server_venv..."
  cd /root/antigravity/ai-eggs
  if [ ! -f ".server_venv/bin/python3" ] || [ -L ".server_venv/bin/python3" ] && [ ! -e ".server_venv/bin/python3" ]; then
      echo "  → Пересоздаю .server_venv (битый или отсутствует)..."
      rm -rf .server_venv
      python3 -m venv .server_venv
  fi
  if [ -f "requirements.txt" ]; then
      .server_venv/bin/pip install -q -r requirements.txt 2>/dev/null
  else
      .server_venv/bin/pip install -q aiogram python-dotenv httpx requests psycopg2-binary 2>/dev/null
  fi

  # ─────────────────────────────────────────────
  # 💻 Node.js проекты
  # ─────────────────────────────────────────────
  echo "💻 Настраиваю Node.js зависимости..."
  cd /root/antigravity/freelance-agent && npm install --silent 2>/dev/null
  cd /root/antigravity/ai-eggs/vezem && npm install --silent 2>/dev/null

  # ─────────────────────────────────────────────
  # 🔄 Перезапуск PM2 с новым ecosystem.config.cjs
  # ─────────────────────────────────────────────
  echo ""
  echo "🔄 Перезапускаю все PM2 процессы..."
  cd /root/antigravity
  pm2 delete all 2>/dev/null || true
  pm2 start ecosystem.config.cjs
  pm2 save

  echo ""
  echo "====================================================="
  echo "✅ ДЕПЛОЙ v2.0 ЗАВЕРШЁН!"
  echo "====================================================="
  echo ""

  # ─────────────────────────────────────────────
  # 🏥 Финальный health-check
  # ─────────────────────────────────────────────
  echo "🏥 HEALTH CHECK:"
  pm2 list
  echo ""
  echo -n "  angela-server: "; curl -s http://localhost:5000/api/health 2>/dev/null || echo "❌ не отвечает"
  echo ""
  echo -n "  vezem-web:     "; curl -s -o /dev/null -w "HTTP %{http_code}" http://localhost:4321/ 2>/dev/null || echo "❌ не отвечает"
  echo ""
  echo "====================================================="
EOF
