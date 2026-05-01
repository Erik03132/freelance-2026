import os
import requests
import json
from dotenv import load_dotenv

def check_folder_contents():
    env_path = "/Users/igorvasin/freelance-2026/ai-eggs/.env"
    load_dotenv(env_path)
    webhook_url = os.getenv("SANDBOX_BITRIX_WEBHOOK_URL").rstrip('/')
    folder_id = 118
    
    print(f"Checking contents of folder ID: {folder_id}...")
    res = requests.get(f"{webhook_url}/disk.folder.getchildren.json", params={"id": folder_id})
    print(json.dumps(res.json(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    check_folder_contents()
