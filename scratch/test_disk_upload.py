import os
import sys

# Добавляем ai-eggs/agent в PATH
AGENT_DIR = os.path.abspath("/Users/igorvasin/freelance-2026/ai-eggs/agent")
sys.path.insert(0, AGENT_DIR)

from bitrix_disk_manager import BitrixDiskManager

def main():
    print("Инициализация BitrixDiskManager...")
    manager = BitrixDiskManager()
    
    print(f"Выбран ID хранилища: {manager.storage_id}")
    if manager.storage_id == 3:
        print("✅ УСПЕХ: Выбран Общий диск (ID 3)")
    else:
        print(f"⚠️ ВНИМАНИЕ: Выбран другой диск (ID {manager.storage_id})")
        
    print(f"Попытка получить/создать корневую папку '{manager.root_folder_name}'...")
    root_id = manager.get_or_create_root_folder()
    print(f"ID корневой папки: {root_id}")
    
    if root_id:
        print("Тестовая загрузка файла...")
        file_id = manager.upload_file(
            folder_id=root_id,
            filename="Test_from_Antigravity.txt",
            content="Привет! Это тестовый файл от агента Antigravity. Если ты это читаешь, значит загрузка на Общий диск работает успешно!"
        )
        print(f"ID загруженного файла: {file_id}")
        if file_id:
            print("✅ Файл успешно загружен!")
        else:
            print("❌ Ошибка при загрузке файла.")

if __name__ == "__main__":
    main()
