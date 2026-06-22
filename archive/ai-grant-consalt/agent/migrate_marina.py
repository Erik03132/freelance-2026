import os
import json
from vector_db import MarinaVectorDB

def run_migration():
    vdb = MarinaVectorDB()
    if not vdb.enabled:
        print("❌ Ошибка: Neon DB не настроен для Ульяны. Проверь .env")
        return

    # Загружаем ноу-хау Ульяны
    knowhow_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'internal_knowhow.json')
    
    if not os.path.exists(knowhow_path):
        print(f"❌ Файл {knowhow_path} не найден.")
        return

    with open(knowhow_path, 'r', encoding='utf-8') as f:
        knowhow = json.load(f)

    print(f"🚀 Начинаю миграцию {len(knowhow)} блоков экспертных знаний Ульяны в Neon DB...")
    
    for i, item in enumerate(knowhow):
        # Превращаем объект в текст
        content = f"Тема: {item['topic']}. Ключевые слова: {', '.join(item['keywords'])}. Внутренний регламент: {item['internal_rule']}"
        print(f"[{i+1}/{len(knowhow)}] Индексирую: {item['topic']}...")
        vdb.add_knowledge(content, {"topic": item['topic'], "type": "expert_knowhow"})
        import time
        time.sleep(1.0) # Задержка для обхода лимитов API

    print("✨ Миграция успешно завершена! Ульяна теперь в облаке.")

if __name__ == "__main__":
    run_migration()
