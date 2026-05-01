import os
import requests
import json
from ai_eggs.agent.bitrix_disk_manager import BitrixDiskManager

def test_disk():
    manager = BitrixDiskManager()
    print(f"Webhook URL: {manager.webhook_url}")
    print(f"Storage ID: {manager.storage_id}")
    
    # Check all storages
    print("\nListing all storages:")
    res = requests.get(f"{manager.webhook_url}/disk.storage.getlist.json")
    print(json.dumps(res.json(), indent=2, ensure_ascii=False))
    
    # Check children of current storage
    print(f"\nListing children of storage {manager.storage_id}:")
    res = requests.get(f"{manager.webhook_url}/disk.storage.getchildren.json", params={"id": manager.storage_id})
    print(json.dumps(res.json(), indent=2, ensure_ascii=False))

    root_id = manager.get_or_create_root_folder()
    print(f"\nRoot folder ID ({manager.root_folder_name}): {root_id}")

if __name__ == "__main__":
    test_disk()
