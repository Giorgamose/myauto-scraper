#!/usr/bin/env python3
import sys, os
from dotenv import load_dotenv
load_dotenv('.env.local')

print('[*] Testing Supabase database connection...')
from database import DatabaseManager
db = DatabaseManager(os.getenv('DATABASE_URL'))
if db.conn:
    result = db._execute('SELECT 1 as test')
    print(f'[OK] Connection successful: {result}')
else:
    print(f'[ERROR] Failed to connect to database')
    sys.exit(1)
