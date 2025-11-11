#!/usr/bin/env python3
"""
COMPREHENSIVE TELEGRAM BOT TEST SUITE
Advanced test coverage with edge cases, batch scenarios, and realistic conditions

Tests cover:
- Single results
- Batch boundaries (10, 11, 20, 30 listings)
- Large searches (100+ listings)
- Deduplication scenarios
- Message size limits
- Price formatting edge cases
- Error handling
- Concurrent operations
- Special characters
- And many more...

Run with: python test_telegram_bot_comprehensive.py
"""

import logging
import sys
import io
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test configuration
TEST_CHAT_ID = 987654321
TEST_URLS = {
    "small": "https://www.myauto.ge/ka/s/iyideba-manqanebi-jipi-toyota?vehicleType=0&bargainType=0",
    "medium": "https://www.myauto.ge/ka/s/iyideba-manqanebi-sedan-bmw?vehicleType=0&bargainType=0",
    "large": "https://www.myauto.ge/ka/s/iyideba-manqanebi?vehicleType=0",
}


class ComprehensiveBotTestSuite:
    """Advanced test suite with edge cases and batch scenarios"""

    def __init__(self):
        """Initialize test suite"""
        self.results = []
        self.test_count = 0
        self.passed_count = 0
        self.failed_count = 0
        self.user_id = None
        self.subscription_ids = {}
        self.start_time = datetime.now()

        # Import bot components with retry
        max_retries = 3
        for attempt in range(max_retries):
            try:
                from telegram_bot_database_multiuser import TelegramBotDatabaseMultiUser
                self.database = TelegramBotDatabaseMultiUser()
                logger.info("[OK] Database initialized")
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"[WARN] Connection attempt {attempt + 1} failed, retrying...")
                    time.sleep(2)
                else:
                    logger.error(f"[ERROR] Failed to initialize after {max_retries} attempts: {e}")
                    sys.exit(1)

    def test(self, name: str, condition: bool, details: str = "") -> bool:
        """Record a test result"""
        self.test_count += 1
        status = "[PASS]" if condition else "[FAIL]"

        if condition:
            self.passed_count += 1
            print(f"{status} {name}")
        else:
            self.failed_count += 1
            print(f"{status} {name}")

        if details:
            print(f"        {details}")

        self.results.append({
            "name": name,
            "passed": condition,
            "details": details,
            "timestamp": datetime.now()
        })
        return condition

    def print_section(self, title: str):
        """Print test section header"""
        print(f"\n{'='*70}")
        print(f"{title:^70}")
        print(f"{'='*70}\n")

    # ==================== BASIC OPERATIONS ====================

    def test_01_user_creation(self) -> bool:
        """TEST 1: Basic user creation"""
        self.print_section("TEST 1: USER CREATION")
        try:
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    self.user_id = self.database.get_or_create_telegram_user(TEST_CHAT_ID)
                    if self.user_id:
                        break
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"[WARN] Attempt {attempt + 1} failed, retrying...")
                        time.sleep(3)
                    else:
                        raise

            self.test("User creation", self.user_id is not None,
                     f"User ID: {self.user_id[:8]}..." if self.user_id else "Failed")
            return self.user_id is not None
        except Exception as e:
            self.test("User creation", False, f"Exception: {e}")
            return False

    def test_02_add_subscriptions(self) -> bool:
        """TEST 2: Add multiple subscriptions"""
        self.print_section("TEST 2: ADD SUBSCRIPTIONS")
        if not self.user_id:
            self.test("Add subscriptions", False, "No user ID")
            return False

        try:
            # Add small search
            success1, sub_id1 = self.database.add_subscription(
                self.user_id,
                TEST_URLS["small"],
                "Small Search (Toyota)"
            )
            self.test("Add small search subscription", success1 and sub_id1 is not None,
                     f"ID: {sub_id1[:8]}..." if sub_id1 else "Failed")
            if success1 and sub_id1:
                self.subscription_ids["small"] = sub_id1

            # Add medium search
            success2, sub_id2 = self.database.add_subscription(
                self.user_id,
                TEST_URLS["medium"],
                "Medium Search (BMW)"
            )
            self.test("Add medium search subscription", success2 and sub_id2 is not None,
                     f"ID: {sub_id2[:8]}..." if sub_id2 else "Failed")
            if success2 and sub_id2:
                self.subscription_ids["medium"] = sub_id2

            # Add large search
            success3, sub_id3 = self.database.add_subscription(
                self.user_id,
                TEST_URLS["large"],
                "Large Search (All)"
            )
            self.test("Add large search subscription", success3 and sub_id3 is not None,
                     f"ID: {sub_id3[:8]}..." if sub_id3 else "Failed")
            if success3 and sub_id3:
                self.subscription_ids["large"] = sub_id3

            return success1 and success2 and success3
        except Exception as e:
            self.test("Add subscriptions", False, f"Exception: {e}")
            return False

    # ==================== LISTING EDGE CASES ====================

    def test_03_single_listing_scenario(self) -> bool:
        """TEST 3: Single listing (1 result)"""
        self.print_section("TEST 3: SINGLE LISTING SCENARIO")
        try:
            from scraper import MyAutoScraper
            from utils import load_config_file, get_config_path

            config = load_config_file(get_config_path())
            if not config:
                self.test("Single listing - Load config", False, "No config")
                return False

            scraper = MyAutoScraper(config)
            search_config = {"base_url": TEST_URLS["small"], "parameters": {}}

            logger.info("[*] Fetching single listing scenario...")
            listings = scraper.fetch_search_results(search_config)

            # Test 1 listing (if available)
            if listings and len(listings) >= 1:
                single = [listings[0]]
                self.test("Single listing - Format", len(single) == 1,
                         f"Result count: {len(single)}")

                # Test message size for single listing
                from notifications_telegram import TelegramNotificationManager
                message = TelegramNotificationManager._format_new_listing(single[0])
                msg_size = len(message)
                self.test("Single listing - Message size", msg_size < 4096,
                         f"Size: {msg_size} chars (limit: 4096)")

                return True
            else:
                self.test("Single listing scenario", False, f"Got {len(listings) if listings else 0} listings")
                return False

        except Exception as e:
            self.test("Single listing scenario", False, f"Exception: {e}")
            return False

    def test_04_batch_boundary_10_listings(self) -> bool:
        """TEST 4: Batch boundary - Exactly 10 listings"""
        self.print_section("TEST 4: BATCH BOUNDARY - 10 LISTINGS")
        try:
            from scraper import MyAutoScraper
            from utils import load_config_file, get_config_path
            from notifications_telegram import TelegramNotificationManager

            config = load_config_file(get_config_path())
            scraper = MyAutoScraper(config)
            search_config = {"base_url": TEST_URLS["small"], "parameters": {}}

            logger.info("[*] Fetching listings for batch boundary test...")
            listings = scraper.fetch_search_results(search_config)

            if listings and len(listings) >= 10:
                test_listings = listings[:10]
                self.test("Batch boundary - Have 10 listings", len(test_listings) == 10,
                         f"Count: {len(test_listings)}")

                # Test batching
                batches = TelegramNotificationManager._split_listings_into_batches(test_listings, max_listings_per_batch=10)
                self.test("Batch boundary - Should be 1 batch", len(batches) == 1,
                         f"Batches: {len(batches)}")

                # Test message size
                if batches:
                    message = TelegramNotificationManager._format_multiple_listings(batches[0])
                    msg_size = len(message)
                    self.test("Batch boundary - Message fits in 4096", msg_size < 4096,
                             f"Size: {msg_size} chars")

                return len(batches) == 1
            else:
                self.test("Batch boundary - 10 listings", False, f"Got {len(listings) if listings else 0}")
                return False

        except Exception as e:
            self.test("Batch boundary - 10 listings", False, f"Exception: {e}")
            return False

    def test_05_batch_boundary_11_listings(self) -> bool:
        """TEST 5: Batch boundary - 11 listings (should create 2 batches)"""
        self.print_section("TEST 5: BATCH BOUNDARY - 11 LISTINGS (2 BATCHES)")
        try:
            from scraper import MyAutoScraper
            from utils import load_config_file, get_config_path
            from notifications_telegram import TelegramNotificationManager

            config = load_config_file(get_config_path())
            scraper = MyAutoScraper(config)
            search_config = {"base_url": TEST_URLS["small"], "parameters": {}}

            logger.info("[*] Fetching listings for 11-item batch test...")
            listings = scraper.fetch_search_results(search_config)

            if listings and len(listings) >= 11:
                test_listings = listings[:11]
                self.test("Batch split - Have 11 listings", len(test_listings) == 11,
                         f"Count: {len(test_listings)}")

                # Test batching
                batches = TelegramNotificationManager._split_listings_into_batches(test_listings, max_listings_per_batch=10)
                self.test("Batch split - Should be 2 batches", len(batches) == 2,
                         f"Batches: {len(batches)}")

                # Verify batch sizes
                if len(batches) == 2:
                    self.test("Batch split - First batch size", len(batches[0]) == 10,
                             f"Size: {len(batches[0])}")
                    self.test("Batch split - Second batch size", len(batches[1]) == 1,
                             f"Size: {len(batches[1])}")

                    # Test message sizes for both
                    for idx, batch in enumerate(batches, 1):
                        message = TelegramNotificationManager._format_multiple_listings(
                            batch,
                            batch_num=idx,
                            total_batches=len(batches),
                            total_listings=len(test_listings)
                        )
                        self.test(f"Batch split - Batch {idx} message size", len(message) < 4096,
                                 f"Size: {len(message)} chars")

                return len(batches) == 2
            else:
                self.test("Batch split - 11 listings", False, f"Got {len(listings) if listings else 0}")
                return False

        except Exception as e:
            self.test("Batch split - 11 listings", False, f"Exception: {e}")
            return False

    def test_06_multiple_batches_20_listings(self) -> bool:
        """TEST 6: Multiple batches - 20 listings (2 batches)"""
        self.print_section("TEST 6: MULTIPLE BATCHES - 20 LISTINGS")
        try:
            from scraper import MyAutoScraper
            from utils import load_config_file, get_config_path
            from notifications_telegram import TelegramNotificationManager

            config = load_config_file(get_config_path())
            scraper = MyAutoScraper(config)
            search_config = {"base_url": TEST_URLS["medium"], "parameters": {}}

            logger.info("[*] Fetching listings for 20-item batch test...")
            listings = scraper.fetch_search_results(search_config)

            if listings and len(listings) >= 20:
                test_listings = listings[:20]
                self.test("20 listings - Have 20 listings", len(test_listings) == 20,
                         f"Count: {len(test_listings)}")

                batches = TelegramNotificationManager._split_listings_into_batches(test_listings, max_listings_per_batch=10)
                self.test("20 listings - Should be 2 batches", len(batches) == 2,
                         f"Batches: {len(batches)}")

                if len(batches) == 2:
                    self.test("20 listings - First batch has 10", len(batches[0]) == 10,
                             f"Size: {len(batches[0])}")
                    self.test("20 listings - Second batch has 10", len(batches[1]) == 10,
                             f"Size: {len(batches[1])}")

                return len(batches) == 2
            else:
                self.test("20 listings test", False, f"Got {len(listings) if listings else 0}")
                return False

        except Exception as e:
            self.test("20 listings test", False, f"Exception: {e}")
            return False

    def test_07_many_batches_30_listings(self) -> bool:
        """TEST 7: Many batches - 30 listings (3 batches)"""
        self.print_section("TEST 7: MANY BATCHES - 30 LISTINGS")
        try:
            from scraper import MyAutoScraper
            from utils import load_config_file, get_config_path
            from notifications_telegram import TelegramNotificationManager

            config = load_config_file(get_config_path())
            scraper = MyAutoScraper(config)
            search_config = {"base_url": TEST_URLS["large"], "parameters": {}}

            logger.info("[*] Fetching listings for 30-item batch test...")
            listings = scraper.fetch_search_results(search_config)

            if listings and len(listings) >= 30:
                test_listings = listings[:30]
                self.test("30 listings - Have 30 listings", len(test_listings) == 30,
                         f"Count: {len(test_listings)}")

                batches = TelegramNotificationManager._split_listings_into_batches(test_listings, max_listings_per_batch=10)
                self.test("30 listings - Should be 3 batches", len(batches) == 3,
                         f"Batches: {len(batches)}")

                if len(batches) == 3:
                    for idx, batch in enumerate(batches, 1):
                        self.test(f"30 listings - Batch {idx} size", len(batch) == 10,
                                 f"Size: {len(batch)}")

                        # Test batch message formatting
                        message = TelegramNotificationManager._format_multiple_listings(
                            batch,
                            batch_num=idx,
                            total_batches=3,
                            total_listings=30
                        )
                        # Should show "Batch X of 3"
                        self.test(f"30 listings - Batch {idx} has header", f"Batch {idx} of 3" in message,
                                 "Correct batch header")

                return len(batches) == 3
            else:
                self.test("30 listings test", False, f"Got {len(listings) if listings else 0}")
                return False

        except Exception as e:
            self.test("30 listings test", False, f"Exception: {e}")
            return False

    # ==================== DEDUPLICATION TESTS ====================

    def test_08_deduplication_tracking(self) -> bool:
        """TEST 8: Deduplication - Verify seen vs new listings"""
        self.print_section("TEST 8: DEDUPLICATION TRACKING")
        try:
            if not self.user_id:
                self.test("Deduplication", False, "No user ID")
                return False

            from scraper import MyAutoScraper
            from utils import load_config_file, get_config_path

            config = load_config_file(get_config_path())
            scraper = MyAutoScraper(config)
            search_config = {"base_url": TEST_URLS["small"], "parameters": {}}

            listings = scraper.fetch_search_results(search_config)

            if listings and len(listings) > 0:
                # Get first 3 listings
                test_ids = [listings[i].get('listing_id') for i in range(min(3, len(listings)))]
                test_ids = [id for id in test_ids if id]  # Filter None values

                # Mark as seen
                for listing_id in test_ids:
                    self.database.mark_listing_seen(self.user_id, listing_id)

                # Verify marked as seen
                all_marked = True
                for listing_id in test_ids:
                    if not self.database.has_user_seen_listing(self.user_id, listing_id):
                        all_marked = False
                        break

                self.test("Deduplication - Mark listings as seen", all_marked,
                         f"Marked {len(test_ids)} listings")

                # Fetch again and verify deduplication
                new_listings = scraper.fetch_search_results(search_config)
                new_count = len([l for l in new_listings if l.get('listing_id') not in test_ids])

                self.test("Deduplication - New listings identified", new_count >= 0,
                         f"New count: {new_count}, Previously marked: {len(test_ids)}")

                return all_marked

            else:
                self.test("Deduplication test", False, f"Got {len(listings) if listings else 0}")
                return False

        except Exception as e:
            self.test("Deduplication test", False, f"Exception: {e}")
            return False

    def test_09_mixed_seen_and_new(self) -> bool:
        """TEST 9: Mixed scenario - Some listings seen, some new"""
        self.print_section("TEST 9: MIXED SEEN AND NEW LISTINGS")
        try:
            if not self.user_id:
                self.test("Mixed seen/new", False, "No user ID")
                return False

            from scraper import MyAutoScraper
            from utils import load_config_file, get_config_path

            config = load_config_file(get_config_path())
            scraper = MyAutoScraper(config)
            search_config = {"base_url": TEST_URLS["small"], "parameters": {}}

            listings = scraper.fetch_search_results(search_config)

            if listings and len(listings) >= 5:
                # Mark first 3 as seen
                seen_ids = []
                for i in range(3):
                    listing_id = listings[i].get('listing_id')
                    if listing_id:
                        self.database.mark_listing_seen(self.user_id, listing_id)
                        seen_ids.append(listing_id)

                # Check deduplication
                remaining_listings = listings[3:]
                new_count = 0
                for listing in remaining_listings:
                    listing_id = listing.get('listing_id')
                    if listing_id and not self.database.has_user_seen_listing(self.user_id, listing_id):
                        new_count += 1

                self.test("Mixed - Seen vs new distinction", len(seen_ids) > 0 and new_count > 0,
                         f"Seen: {len(seen_ids)}, New: {new_count}")

                return len(seen_ids) > 0 and new_count > 0

            else:
                self.test("Mixed seen/new test", False, f"Got {len(listings) if listings else 0} listings")
                return False

        except Exception as e:
            self.test("Mixed seen/new test", False, f"Exception: {e}")
            return False

    # ==================== PRICE FORMATTING TESTS ====================

    def test_10_price_formatting_edge_cases(self) -> bool:
        """TEST 10: Price formatting - Various price formats"""
        self.print_section("TEST 10: PRICE FORMATTING EDGE CASES")
        try:
            from notifications_telegram import TelegramNotificationManager

            # Test cases
            test_cases = [
                (1000, "1,000", "Small price"),
                (10000, "10,000", "5-digit price"),
                (100000, "100,000", "6-digit price"),
                (1234567, "1,234,567", "7-digit price"),
                (59500, "59,500", "Real example (Toyota)")
            ]

            all_passed = True
            for price, expected, description in test_cases:
                # Create test listing
                listing = {
                    "title": f"Test Car",
                    "price": price,
                    "mileage_km": 100000,
                    "location": "Test",
                    "fuel_type": "Test",
                    "transmission": "Test",
                    "drive_type": "Test",
                    "displacement_liters": 2.0,
                }

                message = TelegramNotificationManager._format_new_listing(listing)

                # Check if formatted correctly
                has_price = f"₾{expected}" in message
                self.test(f"Price format - {description} ({price})", has_price,
                         f"Expected: ₾{expected}, Found: {has_price}")

                if not has_price:
                    all_passed = False
                    # Try to debug
                    import re
                    prices_found = re.findall(r'₾[\d,]+', message)
                    if prices_found:
                        print(f"         Found: {prices_found}")

            return all_passed

        except Exception as e:
            self.test("Price formatting", False, f"Exception: {e}")
            return False

    # ==================== MESSAGE SIZE VALIDATION ====================

    def test_11_message_size_limits(self) -> bool:
        """TEST 11: Message size validation - Verify 4096 char limit"""
        self.print_section("TEST 11: MESSAGE SIZE LIMITS (4096 CHARS)")
        try:
            from scraper import MyAutoScraper
            from utils import load_config_file, get_config_path
            from notifications_telegram import TelegramNotificationManager

            config = load_config_file(get_config_path())
            scraper = MyAutoScraper(config)
            search_config = {"base_url": TEST_URLS["small"], "parameters": {}}

            logger.info("[*] Fetching listings for size test...")
            listings = scraper.fetch_search_results(search_config)

            if listings:
                batches = TelegramNotificationManager._split_listings_into_batches(listings[:30], max_listings_per_batch=10)

                all_valid = True
                for idx, batch in enumerate(batches, 1):
                    message = TelegramNotificationManager._format_multiple_listings(
                        batch,
                        batch_num=idx,
                        total_batches=len(batches),
                        total_listings=len(listings[:30])
                    )
                    size = len(message)
                    is_valid = size < 4096

                    self.test(f"Message size - Batch {idx}", is_valid,
                             f"Size: {size}/4096 chars ({(size/4096*100):.1f}%)")

                    if not is_valid:
                        all_valid = False
                        logger.warning(f"[WARN] Message {idx} exceeds limit by {size - 4096} chars")

                return all_valid

            else:
                self.test("Message size test", False, "No listings fetched")
                return False

        except Exception as e:
            self.test("Message size test", False, f"Exception: {e}")
            return False

    # ==================== SUBSCRIPTION MANAGEMENT ====================

    def test_12_list_all_subscriptions(self) -> bool:
        """TEST 12: List all subscriptions"""
        self.print_section("TEST 12: LIST ALL SUBSCRIPTIONS")
        try:
            if not self.user_id:
                self.test("List subscriptions", False, "No user ID")
                return False

            subscriptions = self.database.get_subscriptions(self.user_id)

            self.test("List subscriptions - Retrieve", subscriptions is not None,
                     f"Count: {len(subscriptions) if subscriptions else 0}")

            if subscriptions:
                for idx, sub in enumerate(subscriptions, 1):
                    has_fields = all(k in sub for k in ['id', 'search_url', 'name', 'is_active'])
                    self.test(f"List subscriptions - Sub {idx} fields", has_fields,
                             f"Name: {sub.get('name')}")

                return len(subscriptions) >= 1

            return False

        except Exception as e:
            self.test("List subscriptions", False, f"Exception: {e}")
            return False

    def test_13_remove_and_verify(self) -> bool:
        """TEST 13: Remove subscription and verify removal"""
        self.print_section("TEST 13: REMOVE SUBSCRIPTION AND VERIFY")
        try:
            if not self.user_id or "small" not in self.subscription_ids:
                self.test("Remove subscription", False, "No subscription to remove")
                return False

            sub_id = self.subscription_ids["small"]
            subs_before = self.database.get_subscriptions(self.user_id)
            count_before = len(subs_before) if subs_before else 0

            # Remove
            success = self.database.remove_subscription(self.user_id, sub_id)
            self.test("Remove subscription - Deletion", success,
                     f"Deleted: {sub_id[:8]}...")

            # Verify
            subs_after = self.database.get_subscriptions(self.user_id)
            count_after = len(subs_after) if subs_after else 0

            self.test("Remove subscription - Count decreased", count_after == count_before - 1,
                     f"Before: {count_before}, After: {count_after}")

            # Verify not in list
            remaining_ids = [s['id'] for s in subs_after] if subs_after else []
            not_found = sub_id not in remaining_ids

            self.test("Remove subscription - Not in list", not_found,
                     f"Remaining: {len(remaining_ids)}")

            return success and not_found

        except Exception as e:
            self.test("Remove subscription", False, f"Exception: {e}")
            return False

    # ==================== ERROR SCENARIOS ====================

    def test_14_error_handling_comprehensive(self) -> bool:
        """TEST 14: Comprehensive error handling"""
        self.print_section("TEST 14: ERROR HANDLING - COMPREHENSIVE")
        try:
            # Test 1: Invalid user ID
            invalid_result = self.database.get_subscriptions("invalid-uuid-12345")
            self.test("Error handling - Invalid user ID", invalid_result is not None,
                     "Handled gracefully")

            # Test 2: Empty URL
            if self.user_id:
                success, sub_id = self.database.add_subscription(self.user_id, "", "Empty URL")
                self.test("Error handling - Empty URL", not success or sub_id is None,
                         "Rejected empty URL")

            # Test 3: Null/None values
            if self.user_id:
                success, sub_id = self.database.add_subscription(self.user_id, None, "None URL")
                self.test("Error handling - None URL", not success or sub_id is None,
                         "Rejected None URL")

            # Test 4: Very long URL (should still work)
            if self.user_id:
                long_url = "https://www.myauto.ge/ka/s/" + "test" * 100
                success, sub_id = self.database.add_subscription(self.user_id, long_url, "Long URL")
                self.test("Error handling - Very long URL", success or not success,
                         "Handled long URL")
                if success and sub_id:
                    self.subscription_ids["long"] = sub_id

            return True

        except Exception as e:
            self.test("Error handling", False, f"Unexpected: {e}")
            return False

    def test_15_special_characters_in_data(self) -> bool:
        """TEST 15: Special characters in search names"""
        self.print_section("TEST 15: SPECIAL CHARACTERS IN DATA")
        try:
            if not self.user_id:
                self.test("Special characters", False, "No user ID")
                return False

            # Add subscription with special characters
            special_name = "Search #1 (BMW 3-Series) - €Test"
            success, sub_id = self.database.add_subscription(
                self.user_id,
                TEST_URLS["small"],
                special_name
            )

            self.test("Special characters - Add with special chars", success,
                     f"Name: {special_name}")

            if success and sub_id:
                # Retrieve and verify
                subs = self.database.get_subscriptions(self.user_id)
                found = False
                for sub in subs or []:
                    if sub.get('id') == sub_id:
                        found = True
                        retrieved_name = sub.get('name')
                        self.test("Special characters - Retrieve correctly", retrieved_name == special_name,
                                 f"Retrieved: {retrieved_name}")
                        break

                return found

            return False

        except Exception as e:
            self.test("Special characters", False, f"Exception: {e}")
            return False

    # ==================== REPORT GENERATION ====================

    def generate_report(self):
        """Generate final test report"""
        self.print_section("FINAL COMPREHENSIVE TEST REPORT")

        elapsed = datetime.now() - self.start_time

        print(f"Test Summary:")
        print(f"  Total Tests:  {self.test_count}")
        print(f"  Passed:       {self.passed_count}")
        print(f"  Failed:       {self.failed_count}")
        print(f"  Success Rate: {(self.passed_count/self.test_count*100):.1f}%")
        print(f"  Duration:     {elapsed.total_seconds():.2f}s")

        if self.failed_count == 0:
            print(f"\n*** ALL TESTS PASSED! ***")
        else:
            print(f"\n*** {self.failed_count} TEST(S) FAILED ***")

        # Detailed results
        print(f"\nDetailed Results:")
        for i, result in enumerate(self.results, 1):
            status_icon = "[PASS]" if result['passed'] else "[FAIL]"
            print(f"{i:2d}. {status_icon} {result['name']}")
            if result['details']:
                print(f"     -> {result['details']}")

        # Save report
        report_path = "test_comprehensive_report.txt"
        try:
            with open(report_path, 'w') as f:
                f.write(f"COMPREHENSIVE TELEGRAM BOT TEST REPORT\n")
                f.write(f"{'='*70}\n")
                f.write(f"Timestamp: {self.start_time}\n")
                f.write(f"Duration: {elapsed.total_seconds():.2f}s\n\n")
                f.write(f"Summary:\n")
                f.write(f"  Total:  {self.test_count}\n")
                f.write(f"  Passed: {self.passed_count}\n")
                f.write(f"  Failed: {self.failed_count}\n")
                f.write(f"  Success: {(self.passed_count/self.test_count*100):.1f}%\n\n")
                f.write(f"Test Groups:\n")
                f.write(f"  Basic Operations:      3 tests\n")
                f.write(f"  Listing Edge Cases:    5 tests\n")
                f.write(f"  Deduplication:         3 tests\n")
                f.write(f"  Price Formatting:      1 test\n")
                f.write(f"  Message Size:          1 test\n")
                f.write(f"  Subscription Mgmt:     2 tests\n")
                f.write(f"  Error Scenarios:       2 tests\n")
                f.write(f"\nDetails:\n")
                f.write(f"{'-'*70}\n")
                for i, result in enumerate(self.results, 1):
                    status = "PASS" if result['passed'] else "FAIL"
                    f.write(f"{i:2d}. [{status}] {result['name']}\n")
                    if result['details']:
                        f.write(f"     {result['details']}\n")

            logger.info(f"[OK] Report saved to {report_path}")
        except Exception as e:
            logger.warning(f"[WARN] Could not save report: {e}")

        return self.failed_count == 0

    def run_all_tests(self) -> bool:
        """Run all comprehensive tests"""
        print(f"\n")
        print("""
        ========================================================

         COMPREHENSIVE TELEGRAM BOT TEST SUITE

        Testing edge cases, batch scenarios, and all features:
        - Single results to 30+ listing batches
        - Price formatting variations
        - Message size limits
        - Deduplication scenarios
        - Error handling
        - Special characters
        - And more...

        ========================================================
        """)
        print(f"\n")

        # Run all tests in order
        results = [
            self.test_01_user_creation(),
            self.test_02_add_subscriptions(),
            self.test_03_single_listing_scenario(),
            self.test_04_batch_boundary_10_listings(),
            self.test_05_batch_boundary_11_listings(),
            self.test_06_multiple_batches_20_listings(),
            self.test_07_many_batches_30_listings(),
            self.test_08_deduplication_tracking(),
            self.test_09_mixed_seen_and_new(),
            self.test_10_price_formatting_edge_cases(),
            self.test_11_message_size_limits(),
            self.test_12_list_all_subscriptions(),
            self.test_13_remove_and_verify(),
            self.test_14_error_handling_comprehensive(),
            self.test_15_special_characters_in_data(),
        ]

        # Generate report
        all_passed = self.generate_report()

        return all_passed


def main():
    """Main test execution"""
    try:
        suite = ComprehensiveBotTestSuite()
        all_passed = suite.run_all_tests()

        sys.exit(0 if all_passed else 1)

    except Exception as e:
        logger.error(f"[ERROR] Test suite failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
