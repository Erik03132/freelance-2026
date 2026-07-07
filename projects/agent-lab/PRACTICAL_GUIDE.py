"""
ПРАКТИЧЕСКОЕ ПРИМЕНЕНИЕ ContentCombine Pipeline
Пошаговый гайд по запуску и использованию
"""

# ============================================================
# ШАГ 1: СОЗДАТЬ TELEGRAM БОТА
# ============================================================

"""
1. Откройте Telegram и найдите @BotFather
2. Отправьте /start
3. Отправьте /newbot
4. Следуйте инструкциям:
   - Введите имя бота (например: "Habr Digest Bot")
   - Введите username (например: @habr_digest_bot)
5. BotFather вернет TOKEN

Пример токена:
  123456789:ABCdefGHIjklmnoPQRstuvWXYZ1234567890

6. Создайте канал или чат для вывода
   - Создайте приватный канал (например: @my_digest_channel)
   - Добавьте бота в канал как администратора
   - Получите chat_id (начинается с -)

Пример chat_id:
  -1001234567890
"""

# ============================================================
# ШАГ 2: НАСТРОИТЬ CONFIG.JSON
# ============================================================

import json

config = {
    # ИСТОЧНИКИ КОНТЕНТА
    "habr": {
        "enabled": True
        # Habr не требует credentials - парсим HTML
    },
    
    "medium": {
        "enabled": False,  # Включите когда будете готовы
        "usernames": [
            # "username1",
            # "username2",
        ]
    },
    
    "twitter": {
        "enabled": False,  # Включите когда будете готовы
        "bearer_token": "",  # Получить на https://developer.twitter.com
        "query": "AI OR machine learning"
    },
    
    "telegram": {
        "enabled": False,  # Включите когда будете готовы
        "bot_token": "",  # Получить от @BotFather
        "channel_id": ""  # Канал для парсинга
    },
    
    # TELEGRAM ВЫВОД (ОБЯЗАТЕЛЬНО)
    "telegram_bot_token": "123456789:ABCdefGHIjklmnoPQRstuvWXYZ1234567890",  # ВАШ ТОКЕН
    "telegram_chat_id": "-1001234567890",  # ВАШ CHAT_ID
    
    # ОБРАБОТКА
    "min_score": 40,        # Минимальный score для digest
    "max_items": 100,       # Макс. статей за раз
    "dedup_threshold": 0.85 # Порог дедупликации
}

# Сохраните в /Users/igorvasin/freelance-2026/projects/agent-lab/config.json
with open('config.json', 'w') as f:
    json.dump(config, f, indent=2)

print("✓ config.json создан")

# ============================================================
# ШАГ 3: ЗАПУСТИТЬ PIPELINE ВРУЧНУЮ
# ============================================================

"""
# В терминале:

cd /Users/igorvasin/freelance-2026/projects/agent-lab
source venv/bin/activate

# Запустить pipeline
python3 pipeline_integration.py --config config.json

# Вы должны увидеть:
#   [pipeline] STEP 1: Fetching content from all sources...
#   [normalizer] Fetching Habr articles...
#   [normalizer] Fetched 20 items from Habr
#   [pipeline] Fetched 20 items total
#   [pipeline] STEP 2: Content already normalized
#   [pipeline] STEP 3: Scoring content...
#   [pipeline] Scored 20 items
#   [pipeline] STEP 4: Deduplicating...
#   [pipeline] Deduplicated: 20 → 20
#   [pipeline] STEP 5: Clustering...
#   [pipeline] Created 1 clusters
#   [pipeline] STEP 6: Generating outputs...
#   [pipeline] Generated: X alerts, Y digest, Z trending
#   [pipeline] STEP 7: Exporting to Telegram...
#   [pipeline] Sent N messages to Telegram

# Проверьте Telegram канал - должны прийти сообщения!
"""

# ============================================================
# ШАГ 4: НАСТРОИТЬ SCHEDULING
# ============================================================

# ВАРИАНТ A: CRON (Linux/Mac)
"""
# Откройте crontab:
crontab -e

# Добавьте строки:

# Каждый час
0 * * * * cd /Users/igorvasin/freelance-2026/projects/agent-lab && source venv/bin/activate && python3 pipeline_integration.py --config config.json >> /tmp/pipeline.log 2>&1

# Каждые 6 часов
0 */6 * * * cd /Users/igorvasin/freelance-2026/projects/agent-lab && source venv/bin/activate && python3 pipeline_integration.py --config config.json >> /tmp/pipeline.log 2>&1

# Каждый день в 9:00
0 9 * * * cd /Users/igorvasin/freelance-2026/projects/agent-lab && source venv/bin/activate && python3 pipeline_integration.py --config config.json >> /tmp/pipeline.log 2>&1

# Сохраните (Ctrl+X, Y, Enter)
# Проверьте:
crontab -l
"""

# ВАРИАНТ B: APScheduler (Python)
"""
# Установите:
pip install apscheduler

# Создайте scheduler.py:
"""

from apscheduler.schedulers.background import BackgroundScheduler
from pipeline_integration import ContentCombinePipeline
import asyncio
import json

def run_pipeline():
    """Запустить pipeline"""
    with open('config.json') as f:
        config = json.load(f)
    
    pipeline = ContentCombinePipeline.__new__(ContentCombinePipeline)
    pipeline.config = config
    
    from normalizer import Normalizer
    pipeline.normalizer = Normalizer()
    
    # Импортируем TelegramExporter если нужен
    if config.get('telegram_bot_token'):
        from telegram_exporter import TelegramExporter
        pipeline.telegram_exporter = TelegramExporter(config['telegram_bot_token'])
    
    # Запустим pipeline
    asyncio.run(pipeline.run())

# Создайте scheduler
scheduler = BackgroundScheduler()

# Добавьте jobs
scheduler.add_job(run_pipeline, 'interval', hours=1, id='habr_digest')  # Каждый час
# scheduler.add_job(run_pipeline, 'cron', hour=9, minute=0, id='daily_digest')  # Каждый день в 9:00
# scheduler.add_job(run_pipeline, 'cron', hour='*/6', minute=0, id='every_6h')  # Каждые 6 часов

# Запустите
scheduler.start()

print("Scheduler запущен. Нажмите Ctrl+C для остановки.")

try:
    # Держим процесс живым
    import time
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    scheduler.shutdown()
    print("Scheduler остановлен")

"""
# Запуск:
python3 scheduler.py

# Или в фоне:
nohup python3 scheduler.py > scheduler.log 2>&1 &
"""

# ============================================================
# ШАГ 5: ИСПОЛЬЗОВАНИЕ С РАЗНЫМИ ИСТОЧНИКАМИ
# ============================================================

"""
HABR ТОЛЬКО (текущая конфигурация)
==================================
Используйте как есть. Работает сразу без credentials.

HABR + MEDIUM
=============
1. Найдите Medium авторов, которых хотите отслеживать
2. Обновите config.json:
   "medium": {
       "enabled": true,
       "usernames": [
           "username1",
           "username2",
           "username3"
       ]
   }
3. Запустите pipeline

HABR + MEDIUM + TWITTER
=======================
1. Создайте Twitter Developer Account на https://developer.twitter.com
2. Создайте приложение
3. Получите Bearer Token
4. Обновите config.json:
   "twitter": {
       "enabled": true,
       "bearer_token": "YOUR_BEARER_TOKEN",
       "query": "AI OR machine learning OR python"
   }
5. Запустите pipeline

HABR + MEDIUM + TWITTER + TELEGRAM
===================================
1. Найдите Telegram канал с интересным контентом
2. Добавьте бота в канал
3. Обновите config.json:
   "telegram": {
       "enabled": true,
       "bot_token": "YOUR_BOT_TOKEN",
       "channel_id": "@channel_username"
   }
4. Запустите pipeline
"""

# ============================================================
# ШАГ 6: ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ
# ============================================================

"""
ПРИМЕР 1: Дневной дайджест Habr
================================
Каждый день в 9:00 утра получаете топ-10 статей Habr за ночь

config.json:
  "habr": {"enabled": true}
  "min_score": 30
  "max_items": 50

crontab:
  0 9 * * * cd /path && python3 pipeline_integration.py --config config.json

Результат в Telegram:
  📊 SUMMARY
  📰 DIGEST (10 items)
  🔥 TRENDING (1 topic)


ПРИМЕР 2: Мониторинг критических проблем
==========================================
Каждый час проверяете Habr, Medium, Twitter на критические баги

config.json:
  "habr": {"enabled": true}
  "medium": {"enabled": true, "usernames": ["dev_blog"]}
  "twitter": {"enabled": true, "query": "bug OR error OR critical"}
  "min_score": 50

crontab:
  0 * * * * cd /path && python3 pipeline_integration.py --config config.json

Результат в Telegram:
  🚨 ALERTS (только критические)
  📰 DIGEST (high priority)


ПРИМЕР 3: Отслеживание тренда в AI
====================================
Каждые 6 часов собираете все про AI из всех источников

config.json:
  "habr": {"enabled": true}
  "medium": {"enabled": true, "usernames": ["ai_researcher", "ml_engineer"]}
  "twitter": {"enabled": true, "query": "AI OR artificial intelligence"}
  "telegram": {"enabled": true, "channel_id": "@ai_news"}
  "min_score": 20

crontab:
  0 */6 * * * cd /path && python3 pipeline_integration.py --config config.json

Результат в Telegram:
  📊 SUMMARY (статистика за 6 часов)
  🔥 TRENDING (топ-5 тем)
  📰 DIGEST (все релевантные статьи)
"""

# ============================================================
# ШАГ 7: МОНИТОРИНГ И ОТЛАДКА
# ============================================================

"""
ЛОГИРОВАНИЕ
===========

# Просмотр логов:
tail -f /tmp/pipeline.log

# Очистка логов:
> /tmp/pipeline.log

# Логирование с датой:
0 * * * * cd /path && python3 pipeline_integration.py --config config.json >> /var/log/pipeline/$(date +\%Y-\%m-\%d).log 2>&1


ПРОВЕРКА СТАТУСА
================

# Проверить, работает ли cron:
log stream --predicate 'process == "cron"' --level debug

# Проверить Telegram логи:
curl https://api.telegram.org/botYOUR_TOKEN/getUpdates | python3 -m json.tool

# Проверить последнее сообщение:
curl https://api.telegram.org/botYOUR_TOKEN/getMe


ОШИБКИ И РЕШЕНИЯ
=================

Ошибка: "ModuleNotFoundError: No module named 'normalizer'"
Решение: Убедитесь, что находитесь в правильной директории и venv активирован

Ошибка: "Telegram messages not sending"
Решение: 
  - Проверьте token: curl https://api.telegram.org/botYOUR_TOKEN/getMe
  - Проверьте chat_id: убедитесь что бот добавлен в чат/канал
  - Проверьте права бота: должен быть администратором в канале

Ошибка: "Score too low, no digest items"
Решение: Снизьте min_score в config.json (например с 50 на 30)

Ошибка: "Habr returns 0 items"
Решение:
  - Проверьте интернет соединение
  - Попробуйте вручную: https://habr.com/ru/articles/
  - User-Agent может быть заблокирован
"""

# ============================================================
# ШАГ 8: МЕТРИКИ И АНАЛИТИКА
# ============================================================

"""
ОТСЛЕЖИВАЙТЕ
============

1. Количество статей за период
2. Распределение scores
3. Какие источники наиболее релевантны
4. Какие теги появляются чаще всего
5. Время обработки pipeline

ПРИМЕР: Добавьте в pipeline_integration.py
"""

import time
from datetime import datetime

def run_with_metrics():
    """Pipeline с метриками"""
    start_time = time.time()
    
    # ... запустить pipeline ...
    
    elapsed = time.time() - start_time
    
    metrics = {
        'timestamp': datetime.now().isoformat(),
        'total_items': 20,
        'alerts': 2,
        'digest': 15,
        'trending': 3,
        'avg_score': 45.2,
        'processing_time_sec': elapsed,
        'items_per_second': 20 / elapsed
    }
    
    # Сохраните в файл
    with open('metrics.jsonl', 'a') as f:
        f.write(json.dumps(metrics) + '\n')
    
    print(f"✓ Pipeline completed in {elapsed:.2f}s")
    print(f"  Items/sec: {metrics['items_per_second']:.1f}")

# ============================================================
# ШАГ 9: ИНТЕГРАЦИЯ С ДРУГИМИ СИСТЕМАМИ
# ============================================================

"""
ИНТЕГРАЦИЯ С DISCORD
====================
Вместо Telegram отправлять в Discord

# Установите:
pip install discord.py

# Обновите telegram_exporter.py чтобы поддерживал Discord
"""

"""
ИНТЕГРАЦИЯ С SLACK
==================
Отправлять дайджест в Slack канал

# Установите:
pip install slack-sdk

# Используйте Slack Webhook URL
"""

"""
ИНТЕГРАЦИЯ С БД
===============
Сохранять все обработанные статьи в PostgreSQL

# Установите:
pip install psycopg2-binary

# Добавьте в pipeline:
import psycopg2
conn = psycopg2.connect("dbname=digest user=postgres")
cur = conn.cursor()
cur.execute("INSERT INTO articles (title, score, source) VALUES (%s, %s, %s)", 
            (item['title'], item['score'], item['source']))
conn.commit()
"""

"""
ИНТЕГРАЦИЯ С WEBHOOK
====================
Получать события из других систем и добавлять в pipeline

# Создайте Flask приложение:
from flask import Flask, request
app = Flask(__name__)

@app.route('/add-content', methods=['POST'])
def add_content():
    data = request.json
    # Добавьте content в pipeline
    return {'status': 'ok'}

app.run(port=5000)
"""

# ============================================================
# БЫСТРЫЙ СТАРТ (3 МИНУТЫ)
# ============================================================

"""
1. Создайте бота в Telegram (@BotFather)
   - Получите TOKEN и CHAT_ID

2. Отредактируйте config.json:
   - telegram_bot_token: "YOUR_TOKEN"
   - telegram_chat_id: "YOUR_CHAT_ID"

3. Запустите:
   cd /Users/igorvasin/freelance-2026/projects/agent-lab
   source venv/bin/activate
   python3 pipeline_integration.py --config config.json

4. Проверьте Telegram - должны прийти сообщения!

5. Добавьте в crontab для автоматизации:
   0 * * * * cd /path && source venv/bin/activate && python3 pipeline_integration.py --config config.json

ГОТОВО! 🎉
"""
