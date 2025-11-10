#!/usr/bin/env python3
"""
Check database contents
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

print("\n[*] Checking seen_listings...")
response = db._make_request(
    'GET',
    f"{db.base_url}/seen_listings",
    headers=db.headers,
    timeout=10
)

if response.status_code == 200:
    results = response.json()
    print(f"[OK] Found {len(results)} listings")
    for listing in results[:5]:
        print(f"    - ID: {listing.get('id')}")
else:
    print(f"[ERROR] Status: {response.status_code}")

print("\n[*] Checking vehicle_details...")
response = db._make_request(
    'GET',
    f"{db.base_url}/vehicle_details",
    headers=db.headers,
    timeout=10
)

if response.status_code == 200:
    results = response.json()
    print(f"[OK] Found {len(results)} records")
    for record in results[:3]:
        make = record.get('make')
        model = record.get('model')
        print(f"    - Listing {record.get('listing_id')}: {make} {model}")
else:
    print(f"[ERROR] Status: {response.status_code}")

print("\n[OK] Database check complete!")
