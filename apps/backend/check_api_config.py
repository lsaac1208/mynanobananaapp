#!/usr/bin/env python3
import sqlite3
from pathlib import Path
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

from app.services.encryption_service import encryption_service

conn = sqlite3.connect('instance/database.db')
cursor = conn.cursor()
cursor.execute('SELECT id, name, is_active, openai_hk_base_url, openai_hk_api_key_encrypted FROM api_config_groups WHERE is_active = 1')
row = cursor.fetchone()
if row:
    print(f'✅ Active Configuration Found:')
    print(f'  ID: {row[0]}')
    print(f'  Name: {row[1]}')
    print(f'  Base URL: {row[3]}')
    try:
        decrypted = encryption_service.decrypt(row[4])
        print(f'  API Key: {decrypted[:10]}...{decrypted[-6:]} (length: {len(decrypted)})')
    except Exception as e:
        print(f'  ❌ Decryption error: {e}')
else:
    print('❌ No active configuration found')
conn.close()
