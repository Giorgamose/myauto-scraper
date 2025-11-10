#!/usr/bin/env python3
"""
Test script to verify the price extraction fix on listing 119084515
The actual price should be 15,500 USD, not 25,200
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from scraper import MyAutoScraper

def test_price_extraction():
    print("\n" + "="*70)
    print("TESTING PRICE EXTRACTION FIX - LISTING 119084515")
    print("="*70)
    print("\nExpected: 15,500 USD (should pick the lower price)")
    print("Previous error: Was extracting 25,200\n")

    # Create scraper with basic config
    config = {'request_timeout_seconds': 30, 'scraper_settings': {'max_retries': 3, 'delay': 1}}
    scraper = MyAutoScraper(config)

    listing_id = "119084515"

    print(f"Fetching listing details for {listing_id}...")
    print("-" * 70)

    try:
        details = scraper.fetch_listing_details(listing_id)

        if details and 'pricing' in details:
            pricing = details['pricing']
            price = pricing.get('price', 'N/A')
            currency = pricing.get('currency', 'N/A')

            print(f"\n✅ EXTRACTION RESULT:")
            print(f"   Price: {price}")
            print(f"   Currency: {currency}")

            # Validate
            if price == '15500' or price == '15,500':
                print(f"\n✅ SUCCESS! Correctly extracted 15,500 USD")
                print(f"   (The fix is working - picking the lower price as USD)")
            elif price == '25200' or price == '25,200':
                print(f"\n❌ FAILURE! Still extracting 25,200")
                print(f"   The fix may not be applied correctly")
            else:
                print(f"\n⚠️  UNEXPECTED PRICE: {price}")
                print(f"   Expected either 15,500 or 25,200")
        else:
            print("\n❌ Failed to extract pricing information")
            if details:
                print(f"Details structure: {details.keys()}")

        # Also print vehicle info for context
        if details:
            vehicle = details.get('vehicle', {})
            print(f"\n📋 VEHICLE INFO (for context):")
            print(f"   Make: {vehicle.get('make', 'N/A')}")
            print(f"   Model: {vehicle.get('model', 'N/A')}")
            print(f"   Year: {vehicle.get('year', 'N/A')}")

    except Exception as e:
        print(f"\n❌ ERROR during extraction: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.close()

    print("\n" + "="*70)

if __name__ == '__main__':
    test_price_extraction()
