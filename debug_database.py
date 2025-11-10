#!/usr/bin/env python3
"""
Debug Database - Check what's actually stored in Supabase
"""

import logging
from dotenv import load_dotenv
from database_rest_api import DatabaseManager

load_dotenv('.env.local')
load_dotenv('.env')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_database():
    """Check database contents"""

    print("\n" + "="*70)
    print("  DATABASE CONTENTS CHECK")
    print("="*70 + "\n")

    db = DatabaseManager()

    if db.connection_failed:
        print("[ERROR] Database connection failed!")
        return

    # Check seen_listings table
    print("[*] Checking seen_listings table...")
    try:
        response = db._make_request(
            'GET',
            f"{db.base_url}/seen_listings?limit=3",
            headers=db.headers,
            timeout=10
        )

        if response.status_code == 200:
            listings = response.json()
            print(f"[OK] Found {len(listings)} listings")
            for listing in listings:
                print(f"  - ID: {listing.get('id')}")
                print(f"    Created: {listing.get('created_at')}")
        else:
            print(f"[ERROR] Status {response.status_code}")
    except Exception as e:
        print(f"[ERROR] {e}")

    # Check vehicle_details table
    print("\n[*] Checking vehicle_details table...")
    try:
        response = db._make_request(
            'GET',
            f"{db.base_url}/vehicle_details?limit=3&select=listing_id,make,model,year,price",
            headers=db.headers,
            timeout=10
        )

        if response.status_code == 200:
            vehicles = response.json()
            print(f"[OK] Found {len(vehicles)} vehicle records")
            for vehicle in vehicles:
                make = vehicle.get('make', 'NULL')
                model = vehicle.get('model', 'NULL')
                year = vehicle.get('year', 'NULL')
                price = vehicle.get('price', 'NULL')
                print(f"  - {year} {make} {model} | {price}")
                if not make or make == "NULL":
                    print(f"    ⚠️ MISSING MAKE/MODEL!")
        else:
            print(f"[ERROR] Status {response.status_code}")
    except Exception as e:
        print(f"[ERROR] {e}")

    # Check search_configurations table
    print("\n[*] Checking search_configurations table...")
    try:
        response = db._make_request(
            'GET',
            f"{db.base_url}/search_configurations?limit=5",
            headers=db.headers,
            timeout=10
        )

        if response.status_code == 200:
            configs = response.json()
            print(f"[OK] Found {len(configs)} search configurations")
            if len(configs) == 0:
                print("    ⚠️ TABLE IS EMPTY - No search configurations stored!")
            else:
                for config in configs:
                    print(f"  - {config.get('name')} (Active: {config.get('is_active')})")
        else:
            print(f"[ERROR] Status {response.status_code}")
    except Exception as e:
        print(f"[ERROR] {e}")

    # Summary
    print("\n" + "="*70)
    print("  ISSUES FOUND:")
    print("="*70)
    print("""
1. Vehicle details missing make/model data
   → Likely issue: Parser not extracting make/model from HTML
   → Solution: Check parser.py parse_listing_summary()

2. Search configurations table is empty
   → Issue: No code populates search_configurations on startup
   → Solution: Add initialization to populate from config.json

3. Listing details not being fetched
   → Issue: fetch_listing_details() not being called
   → Solution: Call fetch_listing_details() for each new listing
    """)

if __name__ == "__main__":
    debug_database()
