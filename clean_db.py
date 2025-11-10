#!/usr/bin/env python3
"""
Clean database
"""

import logging
from dotenv import load_dotenv
from database_rest_api import DatabaseManager

load_dotenv('.env.local')
load_dotenv('.env')

logging.basicConfig(level=logging.INFO)

db = DatabaseManager()

if db.connection_failed:
    print("[ERROR] Database connection failed!")
    exit(1)

print("\n[*] Deleting all seen_listings...")
# Use a filter that matches all rows (created_at is never NULL)
response = db._make_request(
    'DELETE',
    f"{db.base_url}/seen_listings?created_at=gte.1970-01-01T00:00:00Z",
    headers=db.headers,
    timeout=10
)

if response.status_code in [200, 204]:
    print(f"[OK] Deleted (status: {response.status_code})")
else:
    print(f"[ERROR] Status: {response.status_code}")
    print(f"    Response: {response.text}")

db.close()
print("[OK] Done!")
