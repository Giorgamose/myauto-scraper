#!/usr/bin/env python3
"""
Complete End-to-End Flow Test
Tests the entire scraper pipeline: search → fetch → extract → flatten → format
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import logging
from scraper import MyAutoScraper
from notifications_telegram import TelegramNotificationManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_complete_flow():
    """Test the complete scraper flow"""

    config = {
        'scraper_settings': {
            'max_retries': 1,
            'delay': 0.5,
            'timeout': 30
        }
    }

    scraper = MyAutoScraper(config)

    print("\n" + "="*70)
    print("COMPLETE END-TO-END FLOW TEST")
    print("="*70)

    # Test listing IDs
    test_listings = [
        '119095225',  # Toyota Land Cruiser Prado - should have description
        '119084515',  # Another listing for comparison
    ]

    results = []

    for listing_id in test_listings:
        print(f"\n{'='*70}")
        print(f"Testing Listing: {listing_id}")
        print(f"{'='*70}")

        try:
            # Step 1: Fetch listing details
            print(f"\n[STEP 1] Fetching listing details...")
            details = scraper.fetch_listing_details(listing_id)

            if not details:
                print(f"❌ Failed to fetch listing {listing_id}")
                continue

            print(f"✅ Successfully fetched listing")

            # Step 2: Extract and verify fields
            print(f"\n[STEP 2] Extracted fields:")

            vehicle = details.get('vehicle', {})
            engine = details.get('engine', {})
            pricing = details.get('pricing', {})
            seller = details.get('seller', {})
            condition = details.get('condition', {})
            description = details.get('description')

            # Create extraction report
            extraction = {
                'listing_id': listing_id,
                'url': details.get('url'),
                'vehicle': vehicle,
                'engine': engine,
                'pricing': pricing,
                'seller': seller,
                'condition': condition,
                'description': description,
            }

            # Display what was extracted
            print(f"  Vehicle: {vehicle.get('make')} {vehicle.get('model')} {vehicle.get('year')}")
            print(f"  Fuel: {engine.get('fuel_type') or 'N/A'}")
            print(f"  Transmission: {engine.get('transmission') or 'N/A'}")
            print(f"  Mileage: {condition.get('mileage_km') or 'N/A'}")
            print(f"  Location: {seller.get('location') or 'N/A'}")
            print(f"  Price: {pricing.get('price') or 'N/A'}")
            print(f"  Description: {'Present (' + str(len(str(description))) + ' chars)' if description else 'N/A'}")

            # Step 3: Format notification
            print(f"\n[STEP 3] Formatting Telegram notification...")

            # Flatten data for notification
            flattened = {
                'listing_id': listing_id,
                'url': details.get('url', ''),
                'title': f"{vehicle.get('make', '')} {vehicle.get('model', '')} {vehicle.get('year', '')}".strip(),
                'make': vehicle.get('make'),
                'model': vehicle.get('model'),
                'year': vehicle.get('year'),
                'price': pricing.get('price'),
                'currency': pricing.get('currency'),
                'location': seller.get('location'),
                'mileage_km': condition.get('mileage_km'),
                'fuel_type': engine.get('fuel_type'),
                'transmission': engine.get('transmission'),
                'drive_type': vehicle.get('drive_type'),
                'displacement_liters': engine.get('displacement_liters'),
                'seller_name': seller.get('seller_name'),
                'customs_cleared': condition.get('customs_cleared'),
                'posted_date': details.get('posted_date'),
                'description': description,
            }

            # Format message
            message = TelegramNotificationManager._format_new_listing(flattened)

            print(f"✅ Notification formatted successfully")
            print(f"\n[TELEGRAM MESSAGE PREVIEW]")
            print(f"{'-'*70}")
            print(message)
            print(f"{'-'*70}")

            # Step 4: Verify critical fields
            print(f"\n[STEP 4] Field Verification:")

            verification = {
                'Vehicle Title': '✅' if flattened['make'] and flattened['model'] else '❌',
                'Fuel Type': '✅' if engine.get('fuel_type') else '❌',
                'Transmission': '✅' if engine.get('transmission') else '❌',
                'Mileage': '✅' if condition.get('mileage_km') else '❌',
                'Location': '✅' if seller.get('location') else '⚠️ (optional)',
                'Price': '✅' if pricing.get('price') else '⚠️ (optional)',
                'Description': '✅' if description else '⚠️ (optional)',
            }

            for field, status in verification.items():
                print(f"  {field}: {status}")

            results.append({
                'listing_id': listing_id,
                'success': True,
                'extraction': extraction,
                'message': message,
                'verification': verification
            })

        except Exception as e:
            print(f"❌ Error testing listing {listing_id}: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                'listing_id': listing_id,
                'success': False,
                'error': str(e)
            })

    # Summary
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}")

    successful = sum(1 for r in results if r.get('success'))
    total = len(results)

    print(f"\nTotal tests: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")

    if successful == total:
        print("\n✅ ALL TESTS PASSED!")
    else:
        print(f"\n⚠️ {total - successful} test(s) failed")

    scraper.close()

    return successful == total

if __name__ == "__main__":
    success = test_complete_flow()
    sys.exit(0 if success else 1)
