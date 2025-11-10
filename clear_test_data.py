#!/usr/bin/env python3
"""
Clear test data from database
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

print("[*] Clearing test data...")

# Delete all seen_listings (this will cascade delete vehicle_details)
response = db._make_request(
    'DELETE',
    f"{db.base_url}/seen_listings",
    headers=db.headers,
    timeout=10
)

if response.status_code in [200, 204]:
    print("[OK] Cleared seen_listings and vehicle_details")
else:
    print(f"[ERROR] Failed: {response.status_code}")

print("[OK] Database cleared. Next run will fetch all listings as 'new'")
