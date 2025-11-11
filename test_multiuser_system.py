#!/usr/bin/env python3
"""
Comprehensive tests for Multi-User System
Tests user management, search criteria, and subscriptions
"""

import logging
import sys
from typing import Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

try:
    from database_rest_api import DatabaseManager
    from user_management import UserManager
    from search_criteria_management import SearchCriteriaManager
    from telegram_bot_database_multiuser import TelegramBotDatabaseMultiUser
except ImportError as e:
    logger.error(f"[ERROR] Failed to import modules: {e}")
    sys.exit(1)


class TestResults:
    """Track test results"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def add_pass(self, test_name: str):
        self.passed += 1
        print(f"[✓] PASS: {test_name}")

    def add_fail(self, test_name: str, reason: str):
        self.failed += 1
        self.errors.append((test_name, reason))
        print(f"[✗] FAIL: {test_name} - {reason}")

    def add_error(self, test_name: str, exception: str):
        self.failed += 1
        self.errors.append((test_name, f"ERROR: {exception}"))
        print(f"[!] ERROR: {test_name} - {exception}")

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'=' * 70}")
        print(f"TEST SUMMARY: {self.passed}/{total} passed, {self.failed} failed")
        print(f"{'=' * 70}")

        if self.errors:
            print("\nFailed Tests:")
            for test_name, reason in self.errors:
                print(f"  - {test_name}: {reason}")

        return self.failed == 0


# ============================================================================
# TESTS: User Management
# ============================================================================

class TestUserManagement:
    """Test user management functionality"""

    def __init__(self):
        self.results = TestResults()
        self.db = DatabaseManager()
        self.manager = UserManager(self.db)
        self.test_users = []

    def run_all(self):
        """Run all user management tests"""
        print("\n" + "=" * 70)
        print("TESTING: USER MANAGEMENT")
        print("=" * 70)

        self.test_user_registration()
        self.test_user_authentication()
        self.test_api_token_creation()
        self.test_api_token_verification()
        self.test_duplicate_username()
        self.test_duplicate_email()

        return self.results

    def test_user_registration(self):
        """Test user registration"""
        try:
            username = f"testuser_{datetime.now().timestamp()}".replace(".", "_")
            email = f"test_{datetime.now().timestamp()}@example.com"
            password = "TestPassword123!"

            success, error, user = self.manager.register_user(
                username=username,
                email=email,
                password=password,
                first_name="Test",
                last_name="User"
            )

            if success and user:
                self.test_users.append(user)
                self.results.add_pass("User Registration")
            else:
                self.results.add_fail("User Registration", error or "Unknown error")

        except Exception as e:
            self.results.add_error("User Registration", str(e))

    def test_user_authentication(self):
        """Test user authentication"""
        try:
            if not self.test_users:
                self.results.add_fail("User Authentication", "No test user available")
                return

            user = self.test_users[0]
            username = user.get("username")

            # Test with correct password
            success, result = self.manager.authenticate_user(username, "TestPassword123!")
            if success and result:
                self.results.add_pass("User Authentication (Correct Password)")
            else:
                self.results.add_fail("User Authentication", result or "Unknown error")

            # Test with incorrect password
            success, result = self.manager.authenticate_user(username, "WrongPassword")
            if not success:
                self.results.add_pass("User Authentication (Wrong Password Rejected)")
            else:
                self.results.add_fail("User Authentication", "Wrong password was accepted")

        except Exception as e:
            self.results.add_error("User Authentication", str(e))

    def test_api_token_creation(self):
        """Test API token creation"""
        try:
            if not self.test_users:
                self.results.add_fail("API Token Creation", "No test user available")
                return

            user_id = self.test_users[0].get("id")

            success, token, token_id = self.manager.create_api_token(
                user_id=user_id,
                token_name="test_token"
            )

            if success and token and token_id:
                self.test_users[0]["api_token"] = token
                self.results.add_pass("API Token Creation")
            else:
                self.results.add_fail("API Token Creation", "Failed to create token")

        except Exception as e:
            self.results.add_error("API Token Creation", str(e))

    def test_api_token_verification(self):
        """Test API token verification"""
        try:
            user = self.test_users[0]
            if "api_token" not in user:
                self.results.add_fail("API Token Verification", "No API token available")
                return

            user_id = user.get("id")
            token = user.get("api_token")

            success = self.manager.verify_api_token(user_id, token)

            if success:
                self.results.add_pass("API Token Verification")
            else:
                self.results.add_fail("API Token Verification", "Token verification failed")

        except Exception as e:
            self.results.add_error("API Token Verification", str(e))

    def test_duplicate_username(self):
        """Test duplicate username prevention"""
        try:
            if not self.test_users:
                self.results.add_fail("Duplicate Username Prevention", "No test user available")
                return

            username = self.test_users[0].get("username")

            success, error, _ = self.manager.register_user(
                username=username,
                email="different@example.com",
                password="DifferentPassword123!"
            )

            if not success and "already exists" in (error or "").lower():
                self.results.add_pass("Duplicate Username Prevention")
            else:
                self.results.add_fail("Duplicate Username Prevention", "Duplicate username was allowed")

        except Exception as e:
            self.results.add_error("Duplicate Username Prevention", str(e))

    def test_duplicate_email(self):
        """Test duplicate email prevention"""
        try:
            if not self.test_users:
                self.results.add_fail("Duplicate Email Prevention", "No test user available")
                return

            email = self.test_users[0].get("email")

            success, error, _ = self.manager.register_user(
                username=f"different_user_{datetime.now().timestamp()}".replace(".", "_"),
                email=email,
                password="DifferentPassword123!"
            )

            if not success and "already" in (error or "").lower():
                self.results.add_pass("Duplicate Email Prevention")
            else:
                self.results.add_fail("Duplicate Email Prevention", "Duplicate email was allowed")

        except Exception as e:
            self.results.add_error("Duplicate Email Prevention", str(e))


# ============================================================================
# TESTS: Search Criteria Management
# ============================================================================

class TestSearchCriteria:
    """Test search criteria management"""

    def __init__(self, user_id: str):
        self.results = TestResults()
        self.db = DatabaseManager()
        self.manager = SearchCriteriaManager(self.db)
        self.user_id = user_id
        self.test_criteria = None

    def run_all(self):
        """Run all search criteria tests"""
        print("\n" + "=" * 70)
        print("TESTING: SEARCH CRITERIA MANAGEMENT")
        print("=" * 70)

        self.test_create_criteria()
        self.test_get_criteria()
        self.test_update_criteria()
        self.test_duplicate_criteria_name()
        self.test_validate_parameters()

        return self.results

    def test_create_criteria(self):
        """Test search criteria creation"""
        try:
            success, error, criteria = self.manager.create_criteria(
                user_id=self.user_id,
                criteria_name="Test Criteria",
                search_parameters={
                    "vehicleType": 0,
                    "priceFrom": 5000,
                    "priceTo": 50000,
                    "yearFrom": 2015,
                    "yearTo": 2024
                },
                description="Test search criteria"
            )

            if success and criteria:
                self.test_criteria = criteria
                self.results.add_pass("Search Criteria Creation")
            else:
                self.results.add_fail("Search Criteria Creation", error or "Unknown error")

        except Exception as e:
            self.results.add_error("Search Criteria Creation", str(e))

    def test_get_criteria(self):
        """Test retrieving search criteria"""
        try:
            if not self.test_criteria:
                self.results.add_fail("Search Criteria Retrieval", "No test criteria available")
                return

            criteria_id = self.test_criteria.get("id")
            retrieved = self.manager.get_criteria_by_id(criteria_id, self.user_id)

            if retrieved and retrieved.get("criteria_name") == "Test Criteria":
                self.results.add_pass("Search Criteria Retrieval")
            else:
                self.results.add_fail("Search Criteria Retrieval", "Failed to retrieve criteria")

        except Exception as e:
            self.results.add_error("Search Criteria Retrieval", str(e))

    def test_update_criteria(self):
        """Test updating search criteria"""
        try:
            if not self.test_criteria:
                self.results.add_fail("Search Criteria Update", "No test criteria available")
                return

            criteria_id = self.test_criteria.get("id")

            success, error = self.manager.update_criteria(
                criteria_id=criteria_id,
                user_id=self.user_id,
                updates={
                    "description": "Updated description",
                    "notification_enabled": False
                }
            )

            if success:
                self.results.add_pass("Search Criteria Update")
            else:
                self.results.add_fail("Search Criteria Update", error or "Unknown error")

        except Exception as e:
            self.results.add_error("Search Criteria Update", str(e))

    def test_duplicate_criteria_name(self):
        """Test duplicate criteria name prevention"""
        try:
            success, error, _ = self.manager.create_criteria(
                user_id=self.user_id,
                criteria_name="Test Criteria",
                search_parameters={
                    "vehicleType": 0,
                    "priceFrom": 10000,
                    "priceTo": 100000
                }
            )

            if not success and "already exists" in (error or "").lower():
                self.results.add_pass("Duplicate Criteria Name Prevention")
            else:
                self.results.add_fail("Duplicate Criteria Name Prevention", "Duplicate name was allowed")

        except Exception as e:
            self.results.add_error("Duplicate Criteria Name Prevention", str(e))

    def test_validate_parameters(self):
        """Test search parameter validation"""
        try:
            valid, error = self.manager.validate_search_parameters({
                "vehicleType": 0,
                "priceFrom": 5000,
                "priceTo": 50000
            })

            if valid:
                self.results.add_pass("Search Parameter Validation (Valid)")
            else:
                self.results.add_fail("Search Parameter Validation", error or "Validation failed")

            # Test invalid parameter
            valid, error = self.manager.validate_search_parameters({
                "invalidParam": "value"
            })

            if not valid:
                self.results.add_pass("Search Parameter Validation (Invalid Rejected)")
            else:
                self.results.add_fail("Search Parameter Validation", "Invalid parameter was accepted")

        except Exception as e:
            self.results.add_error("Search Parameter Validation", str(e))


# ============================================================================
# TESTS: Telegram Bot Database (Multi-User)
# ============================================================================

class TestTelegramBotDatabase:
    """Test telegram bot database multi-user functionality"""

    def __init__(self, user_id: str):
        self.results = TestResults()
        self.db = DatabaseManager()
        self.bot_db = TelegramBotDatabaseMultiUser(self.db)
        self.user_id = user_id
        self.test_subscription = None

    def run_all(self):
        """Run all telegram bot database tests"""
        print("\n" + "=" * 70)
        print("TESTING: TELEGRAM BOT DATABASE (MULTI-USER)")
        print("=" * 70)

        self.test_add_subscription()
        self.test_get_subscriptions()
        self.test_record_seen_listing()
        self.test_check_seen_listing()
        self.test_log_event()
        self.test_duplicate_subscription()

        return self.results

    def test_add_subscription(self):
        """Test adding subscription"""
        try:
            search_url = f"https://www.myauto.ge/test_{datetime.now().timestamp()}"

            success, error = self.bot_db.add_subscription(
                user_id=self.user_id,
                search_url=search_url,
                search_name="Test Subscription"
            )

            if success:
                self.test_subscription = search_url
                self.results.add_pass("Add Subscription")
            else:
                self.results.add_fail("Add Subscription", error or "Unknown error")

        except Exception as e:
            self.results.add_error("Add Subscription", str(e))

    def test_get_subscriptions(self):
        """Test retrieving subscriptions"""
        try:
            subscriptions = self.bot_db.get_subscriptions(self.user_id)

            if isinstance(subscriptions, list) and len(subscriptions) > 0:
                self.results.add_pass("Get Subscriptions")
            else:
                self.results.add_fail("Get Subscriptions", "Failed to retrieve subscriptions")

        except Exception as e:
            self.results.add_error("Get Subscriptions", str(e))

    def test_record_seen_listing(self):
        """Test recording seen listing"""
        try:
            listing_id = f"listing_{datetime.now().timestamp()}".replace(".", "_")

            success = self.bot_db.record_user_seen_listing(
                user_id=self.user_id,
                listing_id=listing_id
            )

            if success:
                self.results.add_pass("Record Seen Listing")
            else:
                self.results.add_fail("Record Seen Listing", "Failed to record")

        except Exception as e:
            self.results.add_error("Record Seen Listing", str(e))

    def test_check_seen_listing(self):
        """Test checking if listing was seen"""
        try:
            listing_id = f"listing_{datetime.now().timestamp()}".replace(".", "_")

            # Record listing
            self.bot_db.record_user_seen_listing(self.user_id, listing_id)

            # Check if seen
            has_seen = self.bot_db.has_user_seen_listing(self.user_id, listing_id)

            if has_seen:
                self.results.add_pass("Check Seen Listing")
            else:
                self.results.add_fail("Check Seen Listing", "Listing not found as seen")

        except Exception as e:
            self.results.add_error("Check Seen Listing", str(e))

    def test_log_event(self):
        """Test event logging"""
        try:
            success = self.bot_db.log_event(
                user_id=self.user_id,
                event_type="test_event",
                event_data={"test": "data"}
            )

            if success:
                self.results.add_pass("Event Logging")
            else:
                self.results.add_fail("Event Logging", "Failed to log event")

        except Exception as e:
            self.results.add_error("Event Logging", str(e))

    def test_duplicate_subscription(self):
        """Test duplicate subscription prevention"""
        try:
            if not self.test_subscription:
                self.results.add_fail("Duplicate Subscription Prevention", "No test subscription")
                return

            success, error = self.bot_db.add_subscription(
                user_id=self.user_id,
                search_url=self.test_subscription
            )

            if not success and "already exists" in (error or "").lower():
                self.results.add_pass("Duplicate Subscription Prevention")
            else:
                self.results.add_fail("Duplicate Subscription Prevention", "Duplicate was allowed")

        except Exception as e:
            self.results.add_error("Duplicate Subscription Prevention", str(e))


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("MULTI-USER SYSTEM - COMPREHENSIVE TESTS")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 70)

    all_results = TestResults()

    # Test User Management
    user_tests = TestUserManagement()
    user_results = user_tests.run_all()
    all_results.passed += user_results.passed
    all_results.failed += user_results.failed
    all_results.errors.extend(user_results.errors)

    # Get a test user for other tests
    if user_tests.test_users:
        test_user = user_tests.test_users[0]
        user_id = test_user.get("id")

        # Test Search Criteria
        criteria_tests = TestSearchCriteria(user_id)
        criteria_results = criteria_tests.run_all()
        all_results.passed += criteria_results.passed
        all_results.failed += criteria_results.failed
        all_results.errors.extend(criteria_results.errors)

        # Test Telegram Bot Database
        bot_tests = TestTelegramBotDatabase(user_id)
        bot_results = bot_tests.run_all()
        all_results.passed += bot_results.passed
        all_results.failed += bot_results.failed
        all_results.errors.extend(bot_results.errors)

    # Print summary
    all_results.summary()

    print(f"Completed: {datetime.now().isoformat()}")
    print("=" * 70 + "\n")

    return all_results.failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
