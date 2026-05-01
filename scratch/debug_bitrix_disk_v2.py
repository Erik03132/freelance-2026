import os
import requests
import json
from dotenv import load_dotenv

def test_disk():
    # Load .env
    env_path = "/Users/igorvasin/freelance-2026/ai-eggs/.env"
    load_dotenv(env_path)
    
    webhook_url = os.getenv("SANDBOX_BITRIX_WEBHOOK_URL") or "https://b24-mjxvhq.bitrix24.ru/rest/1/lqx5kngqbh7k09nx/"
    webhook_url = webhook_url.rstrip('/')
    
    print(f"Webhook URL: {webhook_url}")
    
    # 1. List all storages
    print("\n--- 📂 All Storages ---")
    try:
        res = requests.get(f"{webhook_url}/disk.storage.getlist.json")
        data = res.json()
        storages = data.get('result', [])
        for s in storages:
            print(f"ID: {s['ID']}, Name: {s['NAME']}, Entity: {s['ENTITY_TYPE']}, EntityID: {s['ENTITY_ID']}")
    except Exception as e:
        print(f"Error listing storages: {e}")
        return

    # 2. Try to find Igor's personal storage (user 15 as per code)
    target_user_id = 15
    print(f"\nSearching for Personal Storage of user {target_user_id}...")
    storage_id = None
    for s in storages:
        if s.get('ENTITY_TYPE') == 'user' and str(s.get('ENTITY_ID')) == str(target_user_id):
            print(f"✅ Found! Storage ID: {s['ID']}")
            storage_id = s['ID']
            break
    
    if not storage_id:
        print("❌ Not found. Let's look for ANY user storage.")
        for s in storages:
            if s.get('ENTITY_TYPE') == 'user':
                print(f"Found User Storage: ID {s['ID']} (User {s['ENTITY_ID']})")
                storage_id = s['ID'] # Take first available user storage
                break

    if not storage_id:
        # Check for 'common' storage too
        for s in storages:
            if s.get('ENTITY_TYPE') == 'common':
                print(f"Found Common Storage: ID {s['ID']}")
                storage_id = s['ID']
                break

    if not storage_id:
        print("Final Fallback: ID 28")
        storage_id = 28

    print(f"\nUsing Storage ID: {storage_id}")

    # 3. List children of this storage
    print(f"\n--- 📁 Children of Storage {storage_id} ---")
    try:
        res = requests.get(f"{webhook_url}/disk.storage.getchildren.json", params={"id": storage_id})
        items = res.json().get('result', [])
        found_root = False
        for item in items:
            print(f"[{item['TYPE']}] ID: {item['ID']}, Name: {item['NAME']}")
            if item['NAME'] == "00_CONTENT_MACHINE_EGGS":
                found_root = True
                root_folder_id = item['ID']
        
        if not found_root:
            print("\nCreating root folder '00_CONTENT_MACHINE_EGGS'...")
            res = requests.post(f"{webhook_url}/disk.storage.addfolder.json", json={
                "id": storage_id,
                "data": {"NAME": "00_CONTENT_MACHINE_EGGS"}
            })
            root_folder_id = res.json().get('result', {}).get('ID')
            print(f"Created Root Folder ID: {root_folder_id}")
            if not root_folder_id:
                print(f"Failed to create folder. Response: {res.text}")
        else:
            print(f"\nRoot folder already exists: ID {root_folder_id}")

    except Exception as e:
        print(f"Error handling folders: {e}")

if __name__ == "__main__":
    test_disk()
