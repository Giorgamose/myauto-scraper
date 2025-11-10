#!/usr/bin/env python3
import sys, os
from dotenv import load_dotenv
load_dotenv('.env.local')

print('[*] Testing Supabase database connection...')
print(f"[*] Using host: {os.getenv('DB_HOST')}")
print(f"[*] Using user: {os.getenv('DB_USER')}")
print(f"[*] Using port: {os.getenv('DB_PORT')}")

from database import DatabaseManager

# DatabaseManager will automatically load from environment variables:
# DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
db = DatabaseManager()

if db.conn:
    result = db._execute('SELECT 1 as test')
    print(f'[OK] Connection successful!')
    print(f'[OK] Query result: {result}')
else:
    print(f'[ERROR] Failed to connect to database')
    sys.exit(1)
