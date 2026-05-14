#!/usr/bin/env python3
"""Тест доступа к Avito API."""
import os
import requests
from dotenv import load_dotenv

load_dotenv('ai-eggs/.env', override=True)

CLIENT_ID = os.getenv('AVITO_CLIENT_ID')
CLIENT_SECRET = os.getenv('AVITO_CLIENT_SECRET')

print(f"AVITO_CLIENT_ID: {CLIENT_ID[:20]}...")
print(f"AVITO_CLIENT_SECRET: {CLIENT_SECRET[:20]}...")

if CLIENT_ID and CLIENT_SECRET:
    resp = requests.post('https://api.avito.ru/token/', data={
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }, timeout=10)
    
    if resp.status_code == 200:
        token_data = resp.json()
        print(f"\n✅ Токен получен!")
        print(f"   expires_in: {token_data.get('expires_in', '?')} сек")
    else:
        print(f"\n❌ Ошибка: {resp.status_code}")
        print(f"   {resp.text[:200]}")
else:
    print("\n❌ Ключи не найдены")
