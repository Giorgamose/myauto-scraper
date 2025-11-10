#!/usr/bin/env python3
import sys, os
from dotenv import load_dotenv
load_dotenv('.env.local')

print('[*] Testing database connection...')
from database import DatabaseManager
db = DatabaseManager(os.getenv('TURSO_DATABASE_URL'), os.getenv('TURSO_AUTH_TOKEN'))
result = db.client.execute('SELECT 1 as test')
print(f'[OK] Success: {result}')
