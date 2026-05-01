import os
import requests
import json
from dotenv import load_dotenv

def test_common_disk():
    env_path = "/Users/igorvasin/freelance-2026/ai-eggs/.env"
    load_dotenv(env_path)
    webhook_url = os.getenv("SANDBOX_BITRIX_WEBHOOK_URL").rstrip('/')
    
    storage_id = 3 # Common disk
    folder_name = "00_TEST_AGENT_FOLDER"
    
    print(f"Attempting to create folder '{folder_name}' on Common Disk (ID {storage_id})...")
    res = requests.post(f"{webhook_url}/disk.storage.addfolder.json", json={
        "id": storage_id,
        "data": {"NAME": folder_name}
    })
    
    print(f"Response: {json.dumps(res.json(), indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    test_common_disk()
