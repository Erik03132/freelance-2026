#!/usr/bin/env python3
"""
Быстрый старт ContentCombine Pipeline
Пошаговый интерактивный гайд
"""

import json
import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_step(num, text):
    print(f"\n[ШАГ {num}] {text}")
    print("-"*70)

def input_with_default(prompt, default):
    """Input с default значением"""
    user_input = input(f"{prompt} [{default}]: ").strip()
    return user_input if user_input else default

def setup_telegram():
    """Интерактивная настройка Telegram"""
    print_step(1, "НАСТРОЙКА TELEGRAM")
    
    print("""
Вам нужны два значения:
  1. BOT_TOKEN - получить от @BotFather
  2. CHAT_ID - ID вашего канала/чата

Инструкция:
  1. Откройте Telegram и найдите @BotFather
  2. Отправьте /newbot
  3. Следуйте инструкциям (имя, username)
  4. Скопируйте полученный TOKEN
  5. Создайте канал и добавьте туда бота
  6. Отправьте в чат: /getid (если установлен бот для получения ID)
     или просто используйте @channel_username
    """)
    
    bot_token = input_with_default("Введите BOT_TOKEN", "")
    chat_id = input_with_default("Введите CHAT_ID", "")
    
    if not bot_token or not chat_id:
        print("\n⚠️  Telegram не настроен. Можете пропустить и настроить позже.")
        return None, None
    
    return bot_token, chat_id

def setup_sources():
    """Интерактивная настройка источников"""
    print_step(2, "ВЫБОР ИСТОЧНИКОВ")
    
    sources = {
        "habr": True,  # Habr включен по умолчанию
        "medium": False,
        "twitter": False,
        "telegram": False,
    }
    
    print("\nДоступные источники:")
    print("  1. Habr (✓ включен по умолчанию, не требует credentials)")
    print("  2. Medium (требует RSS, можно добавить авторов)")
    print("  3. Twitter (требует Bearer Token)")
    print("  4. Telegram (требует Bot Token и Channel ID)")
    
    # Medium
    if input("\nДобавить Medium авторов? (y/n) [n]: ").lower() == 'y':
        sources["medium"] = True
        usernames = input("Введите usernames через запятую: ").split(',')
        sources["medium_usernames"] = [u.strip() for u in usernames]
    
    # Twitter
    if input("\nДобавить Twitter? (y/n) [n]: ").lower() == 'y':
        sources["twitter"] = True
        token = input("Введите Bearer Token: ").strip()
        query = input_with_default("Введите search query", "AI OR machine learning")
        sources["twitter_token"] = token
        sources["twitter_query"] = query
    
    # Telegram
    if input("\nПарсить Telegram канал? (y/n) [n]: ").lower() == 'y':
        sources["telegram"] = True
        token = input("Введите Bot Token для парсинга: ").strip()
        channel = input("Введите Channel ID: ").strip()
        sources["telegram_token"] = token
        sources["telegram_channel"] = channel
    
    return sources

def create_config(bot_token, chat_id, sources):
    """Создать config.json"""
    print_step(3, "СОЗДАНИЕ КОНФИГУРАЦИИ")
    
    config = {
        "habr": {"enabled": sources.get("habr", True)},
        "medium": {
            "enabled": sources.get("medium", False),
            "usernames": sources.get("medium_usernames", [])
        },
        "twitter": {
            "enabled": sources.get("twitter", False),
            "bearer_token": sources.get("twitter_token", ""),
            "query": sources.get("twitter_query", "AI")
        },
        "telegram": {
            "enabled": sources.get("telegram", False),
            "bot_token": sources.get("telegram_token", ""),
            "channel_id": sources.get("telegram_channel", "")
        },
        "telegram_bot_token": bot_token or "",
        "telegram_chat_id": chat_id or "",
        "min_score": 40,
        "max_items": 100,
        "dedup_threshold": 0.85
    }
    
    config_path = Path("/Users/igorvasin/freelance-2026/projects/agent-lab/config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Config сохранен: {config_path}")
    return config

def test_pipeline():
    """Тестовый запуск pipeline"""
    print_step(4, "ТЕСТОВЫЙ ЗАПУСК")
    
    print("\nЗапускаю pipeline...")
    print("(Это может занять 10-15 секунд)\n")
    
    try:
        result = subprocess.run([
            "python3", "pipeline_integration.py", 
            "--config", "config.json"
        ], cwd="/Users/igorvasin/freelance-2026/projects/agent-lab", 
           capture_output=True, text=True, timeout=60)
        
        print(result.stdout)
        
        if result.returncode == 0:
            print("\n✓ Pipeline выполнен успешно!")
            return True
        else:
            print(f"\n✗ Ошибка: {result.stderr}")
            return False
    
    except subprocess.TimeoutExpired:
        print("✗ Pipeline timeout (>60 сек)")
        return False
    except Exception as e:
        print(f"✗ Ошибка запуска: {e}")
        return False

def setup_cron():
    """Настройка автоматического запуска"""
    print_step(5, "АВТОМАТИЧЕСКИЙ ЗАПУСК (CRON)")
    
    print("\nВыберите расписание:")
    print("  1. Каждый час")
    print("  2. Каждые 6 часов")
    print("  3. Каждый день в 9:00")
    print("  4. Пропустить")
    
    choice = input("\nВыбор [4]: ").strip() or "4"
    
    if choice == "4":
        print("Cron не настроен. Можете настроить позже вручную.")
        return
    
    cron_expressions = {
        "1": "0 * * * * ",
        "2": "0 */6 * * * ",
        "3": "0 9 * * * ",
    }
    
    if choice not in cron_expressions:
        print("Неверный выбор")
        return
    
    cron_expr = cron_expressions[choice]
    cmd = "cd /Users/igorvasin/freelance-2026/projects/agent-lab && source venv/bin/activate && python3 pipeline_integration.py --config config.json >> /tmp/pipeline.log 2>&1"
    
    cron_line = cron_expr + cmd
    
    print(f"\nCron строка:")
    print(f"  {cron_line}")
    
    if input("\nДобавить в crontab? (y/n) [y]: ").lower() != 'n':
        try:
            # Получить текущий crontab
            result = subprocess.run(["crontab", "-l"], 
                                  capture_output=True, text=True)
            current_crontab = result.stdout if result.returncode == 0 else ""
            
            # Добавить новую строку
            new_crontab = current_crontab + "\n" + cron_line + "\n"
            
            # Установить обновленный crontab
            process = subprocess.Popen(["crontab", "-"], 
                                     stdin=subprocess.PIPE, text=True)
            process.communicate(new_crontab)
            
            print("✓ Cron добавлен!")
            print("  Проверить: crontab -l")
        except Exception as e:
            print(f"✗ Ошибка добавления cron: {e}")
            print("  Добавьте вручную:")
            print(f"  crontab -e")
            print(f"  {cron_line}")

def print_summary(config):
    """Вывести итоговую информацию"""
    print_header("ИТОГОВАЯ КОНФИГУРАЦИЯ")
    
    print("\nИсточники:")
    print(f"  ✓ Habr: {config['habr']['enabled']}")
    print(f"  {'✓' if config['medium']['enabled'] else '✗'} Medium: {config['medium']['enabled']}")
    print(f"  {'✓' if config['twitter']['enabled'] else '✗'} Twitter: {config['twitter']['enabled']}")
    print(f"  {'✓' if config['telegram']['enabled'] else '✗'} Telegram: {config['telegram']['enabled']}")
    
    print(f"\nВывод:")
    if config['telegram_bot_token']:
        print(f"  ✓ Telegram: {config['telegram_chat_id']}")
    else:
        print(f"  ✗ Telegram не настроен")
    
    print(f"\nОбработка:")
    print(f"  Min score: {config['min_score']}")
    print(f"  Max items: {config['max_items']}")
    print(f"  Dedup threshold: {config['dedup_threshold']}")

def print_next_steps():
    """Следующие шаги"""
    print_header("СЛЕДУЮЩИЕ ШАГИ")
    
    print("""
1. Проверьте Telegram канал - должны прийти сообщения

2. Запустите вручную когда угодно:
   cd /Users/igorvasin/freelance-2026/projects/agent-lab
   source venv/bin/activate
   python3 pipeline_integration.py --config config.json

3. Проверьте логи:
   tail -f /tmp/pipeline.log

4. Добавьте другие источники в config.json и перезапустите

5. Отредактируйте scoring в pipeline_integration.py если нужны другие keywords

6. Разверните на сервере/VPS для 24/7 работы

Документация:
  - README_PIPELINE.md - полное руководство
  - PROJECT_SUMMARY.md - архитектура и возможности
  - PRACTICAL_GUIDE.py - примеры использования
    """)

def main():
    print_header("ContentCombine Pipeline - Быстрый старт")
    
    print("\nЭтот скрипт поможет вам настроить и запустить pipeline за 5 минут.")
    
    # Проверка окружения
    agent_lab_path = Path("/Users/igorvasin/freelance-2026/projects/agent-lab")
    if not agent_lab_path.exists():
        print(f"✗ Ошибка: {agent_lab_path} не найден")
        return 1
    
    # Шаг 1: Telegram
    bot_token, chat_id = setup_telegram()
    
    # Шаг 2: Источники
    sources = setup_sources()
    
    # Шаг 3: Config
    config = create_config(bot_token, chat_id, sources)
    
    # Шаг 4: Тест
    if input("\nЗапустить тестовый pipeline? (y/n) [y]: ").lower() != 'n':
        if test_pipeline():
            print("\n✓ Тест пройден! Pipeline работает.")
        else:
            print("\n⚠️  Тест не прошел. Проверьте config и попробуйте снова.")
    
    # Шаг 5: Cron
    if input("\nНастроить автоматический запуск? (y/n) [y]: ").lower() != 'n':
        setup_cron()
    
    # Итоги
    print_summary(config)
    print_next_steps()
    
    print_header("ГОТОВО! 🎉")
    print("\nPipeline настроен и готов к работе.")
    print("Проверьте Telegram канал на наличие сообщений.")
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n✗ Отменено пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
