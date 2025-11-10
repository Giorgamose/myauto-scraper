#!/usr/bin/env python3
"""Test Supabase REST API connection"""
import sys
import os
from dotenv import load_dotenv

load_dotenv('.env.local')
load_dotenv('.env')

print('[*] Testing Supabase REST API connection...')
print(f"[*] Using Supabase URL: {os.getenv('SUPABASE_URL')}")
print(f"[*] Using API Key: {os.getenv('SUPABASE_API_KEY')[:20]}...")

from database_rest_api import DatabaseManager

# DatabaseManager will automatically load from environment variables:
# SUPABASE_URL, SUPABASE_API_KEY
db = DatabaseManager()

if db.connection_failed:
    print('[ERROR] Failed to connect to Supabase REST API')
    sys.exit(1)

# Test basic connectivity
try:
    stats = db.get_statistics()
    print('[OK] Connection successful!')
    print(f'[OK] Database Statistics: {stats}')
except Exception as e:
    print(f'[ERROR] Failed to query database: {e}')
    sys.exit(1)
