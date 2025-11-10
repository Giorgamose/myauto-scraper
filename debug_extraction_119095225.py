#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug extraction for specific listing 119095225
"""

import sys
import io
from scraper import MyAutoScraper

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

config = {'scraper_settings': {'max_retries': 3, 'delay': 1, 'timeout': 30}}
scraper = MyAutoScraper(config)

listing_id = "119095225"

print("\n" + "="*60)
print("DEBUGGING LISTING: " + listing_id)
print("="*60)

details = scraper.fetch_listing_details(listing_id)

if details:
    print("\n1. VEHICLE INFO:")
    vehicle = details.get('vehicle', {})
    for key, val in vehicle.items():
        val_str = str(val)[:100] if val else None
        print(f"   {key}: {val_str}")

    print("\n2. ENGINE INFO:")
    engine = details.get('engine', {})
    for key, val in engine.items():
        print(f"   {key}: {val}")

    print("\n3. PRICING INFO:")
    pricing = details.get('pricing', {})
    for key, val in pricing.items():
        print(f"   {key}: {val}")

    print("\n4. SELLER INFO:")
    seller = details.get('seller', {})
    for key, val in seller.items():
        print(f"   {key}: {val}")

    print("\n5. CONDITION INFO:")
    condition = details.get('condition', {})
    for key, val in condition.items():
        print(f"   {key}: {val}")

    print("\n6. DESCRIPTION:")
    description = details.get('description')
    print(f"   Type: {type(description)}")
    if isinstance(description, dict):
        for key, val in description.items():
            val_str = str(val)[:200] if val else None
            print(f"   {key}: {val_str}")
    else:
        print(f"   Value: {description}")

else:
    print("Failed to fetch details")

scraper.close()
