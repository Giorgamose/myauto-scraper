#!/usr/bin/env python3
"""
Test listing detail fetching
"""

import logging
from dotenv import load_dotenv
from scraper import MyAutoScraper
from utils import load_config_file
import json

load_dotenv('.env.local')
load_dotenv('.env')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load config
config = load_config_file('config.json')

# Initialize scraper
scraper = MyAutoScraper(config)

# Test listing ID (real listing from MyAuto.ge)
test_listing_id = "119084515"

print(f"\n{'='*70}")
print(f"Testing listing detail fetch for ID: {test_listing_id}")
print(f"{'='*70}\n")

print(f"[*] Fetching detailed information...")
try:
    details = scraper.fetch_listing_details(test_listing_id)

    if details:
        print(f"[OK] Successfully fetched listing details!")
        print(f"\n[*] Vehicle Information:")

        vehicle = details.get("vehicle", {})
        if vehicle:
            print(f"  Make: {vehicle.get('make')}")
            print(f"  Model: {vehicle.get('model')}")
            print(f"  Year: {vehicle.get('year')}")
            print(f"  Body Type: {vehicle.get('body_type')}")

        engine = details.get("engine", {})
        if engine:
            print(f"\n[*] Engine Information:")
            print(f"  Fuel Type: {engine.get('fuel_type')}")
            print(f"  Transmission: {engine.get('transmission')}")
            print(f"  Power: {engine.get('power_hp')} HP")

        pricing = details.get("pricing", {})
        if pricing:
            print(f"\n[*] Pricing:")
            print(f"  Price: {pricing.get('price')} {pricing.get('currency')}")

        condition = details.get("condition", {})
        if condition:
            print(f"\n[*] Condition:")
            print(f"  Mileage: {condition.get('mileage_km')} km")
            print(f"  Status: {condition.get('status')}")

        seller = details.get("seller", {})
        if seller:
            print(f"\n[*] Seller:")
            print(f"  Name: {seller.get('seller_name')}")
            print(f"  Location: {seller.get('location')}")

        print(f"\n[OK] Detail fetching is working correctly!")
    else:
        print(f"[ERROR] Failed to fetch listing details")
except Exception as e:
    print(f"[ERROR] Exception: {e}")
    import traceback
    traceback.print_exc()
