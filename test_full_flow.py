#!/usr/bin/env python3
"""
Test the full scraping and database storage flow
"""

import logging
import sys
import os
from dotenv import load_dotenv

# Fix encoding
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv('.env.local')
load_dotenv('.env')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

from scraper import MyAutoScraper
from database_rest_api import DatabaseManager
from utils import load_config_file

def test_full_flow():
    """Test the complete flow: search -> fetch details -> store -> verify"""

    logger.info("="*70)
    logger.info("TESTING FULL SCRAPING & STORAGE FLOW")
    logger.info("="*70)

    # Load configuration
    config = load_config_file('config.json')

    # Initialize components
    scraper = MyAutoScraper(config)
    database = DatabaseManager()

    if database.connection_failed:
        logger.error("[ERROR] Database connection failed!")
        return False

    # Get first search configuration
    search_configs = config.get("search_configurations", [])
    if not search_configs:
        logger.error("[ERROR] No search configurations found")
        return False

    search_config = search_configs[0]
    logger.info(f"\n[*] Testing with search: {search_config.get('name')}")

    # Step 1: Fetch search results
    logger.info("\n[STEP 1] Fetching search results...")
    listings = scraper.fetch_search_results(search_config)

    if not listings:
        logger.error("[ERROR] No listings found in search results")
        return False

    logger.info(f"[OK] Found {len(listings)} listings")

    # Step 2: Process first 3 listings
    processed_count = 0
    stored_count = 0

    for listing in listings[:3]:  # Test with first 3 listings
        listing_id = listing.get("listing_id")
        logger.info(f"\n[STEP 2] Processing listing: {listing_id}")

        # Check if already seen
        if database.has_seen_listing(listing_id):
            logger.info(f"    Already seen, skipping")
            continue

        # Fetch detailed information
        logger.info(f"    Fetching details...")
        details = scraper.fetch_listing_details(listing_id)

        if not details:
            logger.warning(f"    Could not fetch details")
            continue

        processed_count += 1

        # Check what data we got
        vehicle = details.get("vehicle", {})
        pricing = details.get("pricing", {})
        condition = details.get("condition", {})

        logger.info(f"    Vehicle: {vehicle.get('make')} {vehicle.get('model')} ({vehicle.get('year')})")
        logger.info(f"    Price: {pricing.get('price')} {pricing.get('currency')}")
        logger.info(f"    Mileage: {condition.get('mileage_km')} km")

        # Store in database
        logger.info(f"    Storing in database...")
        if database.store_listing(details):
            stored_count += 1
            logger.info(f"    [OK] Stored successfully")
        else:
            logger.error(f"    [ERROR] Failed to store")

    logger.info(f"\n[RESULTS]")
    logger.info(f"  Processed: {processed_count}")
    logger.info(f"  Stored: {stored_count}")

    # Step 3: Verify database contents
    logger.info(f"\n[STEP 3] Verifying database contents...")
    stats = database.get_statistics()
    logger.info(f"  Total listings: {stats.get('total_listings', 0)}")
    logger.info(f"  Recent (24h): {stats.get('recent_listings_24h', 0)}")

    scraper.close()
    database.close()

    return stored_count > 0

if __name__ == "__main__":
    try:
        success = test_full_flow()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
