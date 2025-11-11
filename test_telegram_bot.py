#!/usr/bin/env python3
"""
Comprehensive Telegram Bot Test Suite
Tests all bot commands and functionality
Can be run with: python test_telegram_bot.py
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
TEST_CHAT_ID = 123456789  # Use a test chat ID (won't send real messages)
TEST_SEARCH_URL = "https://www.myauto.ge/ka/s/iyideba-manqanebi-jipi-toyota?vehicleType=0&bargainType=0"
TEST_SEARCH_URL_2 = "https://www.myauto.ge/ka/s/iyideba-manqanebi-sedan-bmw?vehicleType=0&bargainType=0"

# Colors for output (disabled on Windows for compatibility)
class Colors:
    HEADER = ''
    BLUE = ''
    CYAN = ''
    GREEN = ''
    YELLOW = ''
    RED = ''
    BOLD = ''
    UNDERLINE = ''
    END = ''


class TelegramBotTestSuite:
    """Comprehensive test suite for Telegram bot"""

    def __init__(self):
        """Initialize test suite"""
        self.results = []
        self.test_count = 0
        self.passed_count = 0
        self.failed_count = 0
        self.user_id = None
        self.subscription_ids = []
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
                    logger.warning(f"[WARN] Database connection attempt {attempt + 1} failed, retrying...")
                    time.sleep(2)
                else:
                    logger.error(f"[ERROR] Failed to initialize database after {max_retries} attempts: {e}")
                    sys.exit(1)

    def test(self, name: str, condition: bool, details: str = "") -> bool:
        """
        Record a test result

        Args:
            name: Test name
            condition: Test condition (True = pass, False = fail)
            details: Additional details

        Returns:
            Test result
        """
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

    def test_user_creation(self) -> bool:
        """Test 1: User Creation"""
        self.print_section("TEST 1: USER CREATION")

        try:
            # Create or get user with retry
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    self.user_id = self.database.get_or_create_telegram_user(TEST_CHAT_ID)
                    if self.user_id:
                        break
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"[WARN] User creation attempt {attempt + 1} failed, retrying...")
                        time.sleep(3)
                    else:
                        raise

            self.test("User creation/retrieval", self.user_id is not None,
                     f"User ID: {self.user_id[:8]}..." if self.user_id else "Failed to create user (timeout or error)")

            if self.user_id:
                # Verify user exists in database
                subscriptions = self.database.get_subscriptions(self.user_id)
                self.test("User has subscriptions list", isinstance(subscriptions, list),
                         f"Subscriptions: {len(subscriptions)}")
                return True
        except Exception as e:
            self.test("User creation", False, f"Exception: {e}")
            return False

        return False

    def test_set_command(self) -> bool:
        """Test 2: /set Command - Add Subscription"""
        self.print_section("TEST 2: /SET COMMAND (ADD SUBSCRIPTION)")

        if not self.user_id:
            self.test("/set command", False, "User ID not available")
            return False

        try:
            # Add first subscription
            success, sub_id = self.database.add_subscription(
                self.user_id,
                TEST_SEARCH_URL,
                "Toyota Jeep Search"
            )
            self.test("Add first subscription", success and sub_id is not None,
                     f"Subscription ID: {sub_id[:8]}..." if sub_id else "Failed to add")

            if success and sub_id:
                self.subscription_ids.append(sub_id)

            # Add second subscription
            success2, sub_id2 = self.database.add_subscription(
                self.user_id,
                TEST_SEARCH_URL_2,
                "BMW Sedan Search"
            )
            self.test("Add second subscription", success2 and sub_id2 is not None,
                     f"Subscription ID: {sub_id2[:8]}..." if sub_id2 else "Failed to add")

            if success2 and sub_id2:
                self.subscription_ids.append(sub_id2)

            return success and success2

        except Exception as e:
            self.test("/set command", False, f"Exception: {e}")
            return False

    def test_list_command(self) -> bool:
        """Test 3: /list Command - Show Subscriptions"""
        self.print_section("TEST 3: /LIST COMMAND (SHOW SUBSCRIPTIONS)")

        if not self.user_id:
            self.test("/list command", False, "User ID not available")
            return False

        try:
            # Get subscriptions
            subscriptions = self.database.get_subscriptions(self.user_id)
            self.test("Retrieve subscriptions", len(subscriptions) >= 2,
                     f"Found {len(subscriptions)} subscriptions")

            # Check first subscription
            if len(subscriptions) > 0:
                sub1 = subscriptions[0]
                self.test("First subscription has required fields",
                         all(k in sub1 for k in ['id', 'search_url', 'name']),
                         f"Fields: {list(sub1.keys())}")
                self.test("First subscription is active",
                         sub1.get('is_active') == True,
                         f"Active: {sub1.get('is_active')}")

            # Check second subscription
            if len(subscriptions) > 1:
                sub2 = subscriptions[1]
                self.test("Second subscription has required fields",
                         all(k in sub2 for k in ['id', 'search_url', 'name']),
                         f"Fields: {list(sub2.keys())}")

            return len(subscriptions) >= 2

        except Exception as e:
            self.test("/list command", False, f"Exception: {e}")
            return False

    def test_reset_command(self) -> bool:
        """Test 4: /reset Command - Clear Tracking"""
        self.print_section("TEST 4: /RESET COMMAND (CLEAR TRACKING)")

        if not self.user_id or len(self.subscription_ids) == 0:
            self.test("/reset command", False, "No subscriptions to reset")
            return False

        try:
            sub_id = self.subscription_ids[0]

            # Mark some listings as seen
            test_listing_ids = ["LIST001", "LIST002", "LIST003"]
            for listing_id in test_listing_ids:
                self.database.mark_listing_seen(self.user_id, listing_id)

            # Verify listings are marked as seen
            seen_count = 0
            for listing_id in test_listing_ids:
                if self.database.has_user_seen_listing(self.user_id, listing_id):
                    seen_count += 1

            self.test("Mark listings as seen", seen_count == len(test_listing_ids),
                     f"Marked {seen_count}/{len(test_listing_ids)} listings")

            # Reset subscription (by updating last_checked to force fresh check)
            reset_success = self.database.update_subscription_check_time(
                sub_id,
                "1970-01-01T00:00:00Z"  # Reset to epoch
            )

            self.test("Reset subscription check time", reset_success,
                     f"Last check reset for subscription {sub_id[:8]}...")

            return reset_success

        except Exception as e:
            self.test("/reset command", False, f"Exception: {e}")
            return False

    def test_clear_command(self) -> bool:
        """Test 5: /clear Command - Remove Subscription"""
        self.print_section("TEST 5: /CLEAR COMMAND (REMOVE SUBSCRIPTION)")

        if not self.user_id or len(self.subscription_ids) < 2:
            self.test("/clear command", False, "Not enough subscriptions to test")
            return False

        try:
            # Get current subscription count
            subs_before = self.database.get_subscriptions(self.user_id)
            count_before = len(subs_before)

            # Remove second subscription
            sub_id_to_remove = self.subscription_ids[1]
            remove_success = self.database.remove_subscription(self.user_id, sub_id_to_remove)

            self.test("Remove subscription", remove_success,
                     f"Removed subscription {sub_id_to_remove[:8]}...")

            # Verify count decreased
            subs_after = self.database.get_subscriptions(self.user_id)
            count_after = len(subs_after)

            self.test("Subscription count decreased", count_after == count_before - 1,
                     f"Before: {count_before}, After: {count_after}")

            # Verify removed subscription is gone
            remaining_ids = [s['id'] for s in subs_after]
            not_found = sub_id_to_remove not in remaining_ids

            self.test("Removed subscription not in list", not_found,
                     f"Remaining subscriptions: {len(remaining_ids)}")

            return remove_success and not_found

        except Exception as e:
            self.test("/clear command", False, f"Exception: {e}")
            return False

    def test_run_command(self) -> bool:
        """Test 6: /run Command - Immediate Check"""
        self.print_section("TEST 6: /RUN COMMAND (IMMEDIATE CHECK)")

        if not self.user_id or len(self.subscription_ids) == 0:
            self.test("/run command", False, "No subscriptions to test")
            return False

        try:
            # Import scraper for testing
            from scraper import MyAutoScraper
            from utils import load_config_file, get_config_path

            config = load_config_file(get_config_path())
            if not config:
                self.test("/run command - Load config", False, "Could not load config")
                return False

            # Create scraper
            scraper = MyAutoScraper(config)
            self.test("/run command - Create scraper", scraper is not None,
                     "Scraper initialized")

            # Fetch listings from test URL
            search_config = {
                "base_url": TEST_SEARCH_URL,
                "parameters": {}
            }

            logger.info("[*] Fetching listings... this may take a moment")
            listings = scraper.fetch_search_results(search_config)

            self.test("/run command - Fetch listings", listings is not None and len(listings) > 0,
                     f"Found {len(listings) if listings else 0} listings")

            if listings and len(listings) > 0:
                # Verify listing structure
                first_listing = listings[0]
                required_fields = ['listing_id', 'title', 'price', 'mileage_km']
                has_fields = all(k in first_listing for k in required_fields)

                self.test("/run command - Listing has required fields", has_fields,
                         f"Fields: {list(first_listing.keys())}")

                # Test deduplication
                listing_id = first_listing.get('listing_id')
                if listing_id:
                    # Mark as seen
                    self.database.mark_listing_seen(self.user_id, listing_id)
                    is_seen = self.database.has_user_seen_listing(self.user_id, listing_id)

                    self.test("/run command - Deduplication tracking", is_seen,
                             f"Listing {listing_id[:8]}... marked as seen")

            return listings is not None and len(listings) > 0

        except Exception as e:
            self.test("/run command", False, f"Exception: {e}")
            return False

    def test_data_persistence(self) -> bool:
        """Test 7: Data Persistence"""
        self.print_section("TEST 7: DATA PERSISTENCE")

        if not self.user_id:
            self.test("Data persistence", False, "User ID not available")
            return False

        try:
            # Re-fetch user data to verify persistence
            re_fetched_subs = self.database.get_subscriptions(self.user_id)

            self.test("Subscriptions persist across calls", len(re_fetched_subs) > 0,
                     f"Found {len(re_fetched_subs)} subscriptions")

            # Verify subscription details
            if len(re_fetched_subs) > 0:
                sub = re_fetched_subs[0]
                self.test("Subscription details are correct",
                         sub.get('search_url') == TEST_SEARCH_URL and sub.get('name') == "Toyota Jeep Search",
                         f"URL: {sub.get('search_url')[:40]}...")

            return len(re_fetched_subs) > 0

        except Exception as e:
            self.test("Data persistence", False, f"Exception: {e}")
            return False

    def test_error_handling(self) -> bool:
        """Test 8: Error Handling"""
        self.print_section("TEST 8: ERROR HANDLING")

        try:
            # Test invalid user ID
            invalid_subs = self.database.get_subscriptions("invalid-uuid")
            self.test("Handle invalid user ID gracefully", invalid_subs is not None,
                     f"Result type: {type(invalid_subs)}")

            # Test empty subscription URL
            success, sub_id = self.database.add_subscription(
                self.user_id,
                "",
                "Empty URL Test"
            )
            # This should either fail gracefully or not add
            self.test("Handle empty URL", success == False or sub_id is None,
                     "Empty URL rejected or warning issued")

            # Test duplicate subscription (if supported)
            if len(self.subscription_ids) > 0:
                dup_success, _ = self.database.add_subscription(
                    self.user_id,
                    TEST_SEARCH_URL,
                    "Duplicate Test"
                )
                # May or may not allow duplicates - just verify it doesn't crash
                self.test("Handle duplicate URL", True,
                         f"Duplicate result: {dup_success}")

            return True

        except Exception as e:
            self.test("Error handling", False, f"Unexpected exception: {e}")
            return False

    def generate_report(self):
        """Generate final test report"""
        self.print_section("FINAL TEST REPORT")

        elapsed = datetime.now() - self.start_time

        print(f"Test Summary:")
        print(f"  Total Tests:  {self.test_count}")
        print(f"  Passed:       {self.passed_count}")
        print(f"  Failed:       {self.failed_count}")
        print(f"  Success Rate: {(self.passed_count/self.test_count*100):.1f}%")
        print(f"  Duration:     {elapsed.total_seconds():.2f}s")

        if self.failed_count == 0:
            print(f"\n*** ALL TESTS PASSED! ***")
            status = "PASS"
        else:
            print(f"\n*** {self.failed_count} TEST(S) FAILED ***")
            status = "FAIL"

        # Detailed results
        print(f"\nDetailed Results:")
        for i, result in enumerate(self.results, 1):
            status_icon = "[PASS]" if result['passed'] else "[FAIL]"
            print(f"{i}. {status_icon} {result['name']}")
            if result['details']:
                print(f"   -> {result['details']}")

        # Save report to file
        report_path = "test_report.txt"
        try:
            with open(report_path, 'w') as f:
                f.write(f"TELEGRAM BOT TEST REPORT\n")
                f.write(f"{'='*70}\n")
                f.write(f"Timestamp: {self.start_time}\n")
                f.write(f"Duration: {elapsed.total_seconds():.2f}s\n\n")
                f.write(f"Summary:\n")
                f.write(f"  Total:  {self.test_count}\n")
                f.write(f"  Passed: {self.passed_count}\n")
                f.write(f"  Failed: {self.failed_count}\n")
                f.write(f"  Success: {(self.passed_count/self.test_count*100):.1f}%\n\n")
                f.write(f"Details:\n")
                f.write(f"{'-'*70}\n")
                for i, result in enumerate(self.results, 1):
                    status = "PASS" if result['passed'] else "FAIL"
                    f.write(f"{i}. [{status}] {result['name']}\n")
                    if result['details']:
                        f.write(f"   {result['details']}\n")

            logger.info(f"[OK] Report saved to {report_path}")
        except Exception as e:
            logger.warning(f"[WARN] Could not save report: {e}")

        return self.failed_count == 0

    def run_all_tests(self) -> bool:
        """Run all tests"""
        print(f"\n")
        print("""
        ========================================================

             TELEGRAM BOT COMPREHENSIVE TEST SUITE

          Testing: /list, /set, /reset, /clear, /run

        ========================================================
        """)
        print(f"\n")

        # Run all tests
        results = [
            self.test_user_creation(),
            self.test_set_command(),
            self.test_list_command(),
            self.test_reset_command(),
            self.test_clear_command(),
            self.test_run_command(),
            self.test_data_persistence(),
            self.test_error_handling(),
        ]

        # Generate report
        all_passed = self.generate_report()

        return all_passed


def main():
    """Main test execution"""
    try:
        suite = TelegramBotTestSuite()
        all_passed = suite.run_all_tests()

        # Exit with appropriate code
        sys.exit(0 if all_passed else 1)

    except Exception as e:
        logger.error(f"[ERROR] Test suite failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
