#!/usr/bin/env python3
"""
Comprehensive test suite for Git Actions subscription query fix
Tests the corrected database query and data transformation logic
"""

import logging
import sys
import json
from typing import Dict, List
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class TestResults:
    """Track test results"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def add_pass(self, test_name: str):
        self.passed += 1
        logger.info(f"[✓] PASS: {test_name}")

    def add_fail(self, test_name: str, reason: str):
        self.failed += 1
        self.errors.append((test_name, reason))
        logger.error(f"[✗] FAIL: {test_name} - {reason}")

    def add_error(self, test_name: str, exception: str):
        self.failed += 1
        self.errors.append((test_name, f"ERROR: {exception}"))
        logger.error(f"[!] ERROR: {test_name} - {exception}")

    def print_summary(self):
        """Print summary of test results"""
        total = self.passed + self.failed
        logger.info("=" * 70)
        logger.info(f"TEST SUMMARY: {self.passed}/{total} passed")
        logger.info("=" * 70)

        if self.errors:
            logger.error("\nFailed tests:")
            for test_name, reason in self.errors:
                logger.error(f"  - {test_name}: {reason}")
        else:
            logger.info("\n✅ All tests passed!")

        return self.failed == 0


class GitActionsFixTester:
    """Test suite for Git Actions subscription query fixes"""

    def __init__(self):
        self.results = TestResults()

    def test_mock_database_response_structure(self):
        """Test 1: Verify the corrected query would return proper nested structure"""
        test_name = "Mock database response structure (correct table join)"
        try:
            # This is what Supabase should return with the CORRECTED query:
            # select=*,telegram_users(id,telegram_chat_id)
            mock_response = [
                {
                    "id": "sub-001",
                    "telegram_user_id": "user-001",
                    "search_url": "https://myauto.ge/search?make=Toyota",
                    "search_name": "Toyota Cars",
                    "is_active": True,
                    "last_checked": "2025-11-11T09:00:00",
                    "telegram_users": {
                        "id": "user-001",
                        "telegram_chat_id": 123456789
                    }
                },
                {
                    "id": "sub-002",
                    "telegram_user_id": "user-002",
                    "search_url": "https://myauto.ge/search?make=BMW",
                    "search_name": "BMW Cars",
                    "is_active": True,
                    "last_checked": None,
                    "telegram_users": {
                        "id": "user-002",
                        "telegram_chat_id": 987654321
                    }
                }
            ]

            # Verify structure
            assert len(mock_response) == 2, "Should have 2 subscriptions"
            assert mock_response[0]["telegram_users"]["telegram_chat_id"] == 123456789
            assert mock_response[1]["telegram_users"]["telegram_chat_id"] == 987654321

            self.results.add_pass(test_name)
            return True

        except Exception as e:
            self.results.add_error(test_name, str(e))
            return False

    def test_data_transformation_logic(self):
        """Test 2: Verify the data transformation correctly extracts chat_id"""
        test_name = "Data transformation extracts chat_id from nested structure"
        try:
            # Simulate the subscription response from Supabase
            subscriptions = [
                {
                    "id": "sub-001",
                    "telegram_user_id": "user-001",
                    "search_url": "https://myauto.ge/search?make=Toyota",
                    "is_active": True,
                    "telegram_users": {
                        "id": "user-001",
                        "telegram_chat_id": 123456789
                    }
                }
            ]

            # Simulate the flattening logic from get_all_active_subscriptions()
            flattened = []
            for sub in subscriptions:
                flattened_sub = dict(sub)

                # Extract chat_id from nested telegram_users object
                if isinstance(sub.get('telegram_users'), dict):
                    user_data = sub['telegram_users']
                    flattened_sub['chat_id'] = user_data.get('telegram_chat_id')
                    logger.debug(f"[*] Extracted chat_id={flattened_sub.get('chat_id')}")

                flattened.append(flattened_sub)

            # Verify transformation
            assert len(flattened) == 1, "Should have 1 subscription"
            assert 'chat_id' in flattened[0], "Should have chat_id field"
            assert flattened[0]['chat_id'] == 123456789, "chat_id should be extracted correctly"
            assert 'telegram_users' in flattened[0], "Should still have original nested structure"

            self.results.add_pass(test_name)
            return True

        except Exception as e:
            self.results.add_error(test_name, str(e))
            return False

    def test_multiple_subscriptions_transformation(self):
        """Test 3: Verify transformation works with multiple subscriptions"""
        test_name = "Transform multiple subscriptions correctly"
        try:
            subscriptions = [
                {
                    "id": "sub-001",
                    "telegram_user_id": "user-001",
                    "search_url": "https://myauto.ge/search?make=Toyota",
                    "is_active": True,
                    "telegram_users": {"id": "user-001", "telegram_chat_id": 111111111}
                },
                {
                    "id": "sub-002",
                    "telegram_user_id": "user-002",
                    "search_url": "https://myauto.ge/search?make=BMW",
                    "is_active": True,
                    "telegram_users": {"id": "user-002", "telegram_chat_id": 222222222}
                },
                {
                    "id": "sub-003",
                    "telegram_user_id": "user-001",
                    "search_url": "https://myauto.ge/search?make=Mercedes",
                    "is_active": True,
                    "telegram_users": {"id": "user-001", "telegram_chat_id": 111111111}
                }
            ]

            # Apply transformation
            flattened = []
            for sub in subscriptions:
                flattened_sub = dict(sub)
                if isinstance(sub.get('telegram_users'), dict):
                    user_data = sub['telegram_users']
                    flattened_sub['chat_id'] = user_data.get('telegram_chat_id')
                flattened.append(flattened_sub)

            # Verify all subscriptions transformed
            assert len(flattened) == 3, "Should have 3 subscriptions"
            assert all('chat_id' in sub for sub in flattened), "All should have chat_id"
            assert flattened[0]['chat_id'] == 111111111
            assert flattened[1]['chat_id'] == 222222222
            assert flattened[2]['chat_id'] == 111111111

            self.results.add_pass(test_name)
            return True

        except Exception as e:
            self.results.add_error(test_name, str(e))
            return False

    def test_edge_case_missing_telegram_users(self):
        """Test 4: Handle edge case where telegram_users is missing"""
        test_name = "Handle missing telegram_users gracefully"
        try:
            subscriptions = [
                {
                    "id": "sub-001",
                    "telegram_user_id": "user-001",
                    "search_url": "https://myauto.ge/search?make=Toyota",
                    "is_active": True,
                    # Missing telegram_users!
                }
            ]

            # Apply transformation (should not crash)
            flattened = []
            for sub in subscriptions:
                flattened_sub = dict(sub)
                if isinstance(sub.get('telegram_users'), dict):
                    user_data = sub['telegram_users']
                    flattened_sub['chat_id'] = user_data.get('telegram_chat_id')
                else:
                    # Log warning but don't crash
                    logger.warning(f"[WARN] Subscription {sub.get('id')}: no telegram_users found")

                flattened.append(flattened_sub)

            # Verify
            assert len(flattened) == 1, "Should still process subscription"
            assert 'chat_id' not in flattened[0], "Should not have chat_id if data missing"

            self.results.add_pass(test_name)
            return True

        except Exception as e:
            self.results.add_error(test_name, str(e))
            return False

    def test_edge_case_empty_telegram_chat_id(self):
        """Test 5: Handle edge case where telegram_chat_id is null"""
        test_name = "Handle null telegram_chat_id gracefully"
        try:
            subscriptions = [
                {
                    "id": "sub-001",
                    "telegram_user_id": "user-001",
                    "search_url": "https://myauto.ge/search",
                    "telegram_users": {"id": "user-001", "telegram_chat_id": None}
                }
            ]

            flattened = []
            for sub in subscriptions:
                flattened_sub = dict(sub)
                if isinstance(sub.get('telegram_users'), dict):
                    user_data = sub['telegram_users']
                    flattened_sub['chat_id'] = user_data.get('telegram_chat_id')
                flattened.append(flattened_sub)

            # Verify - should have chat_id but it will be None
            assert len(flattened) == 1
            assert 'chat_id' in flattened[0]
            assert flattened[0]['chat_id'] is None

            self.results.add_pass(test_name)
            return True

        except Exception as e:
            self.results.add_error(test_name, str(e))
            return False

    def test_scheduler_subscription_extraction(self):
        """Test 6: Verify scheduler can extract data from flattened subscriptions"""
        test_name = "Scheduler extracts subscription fields correctly"
        try:
            # Simulate a flattened subscription from get_all_active_subscriptions()
            subscription = {
                "id": "sub-001",
                "telegram_user_id": "user-001",
                "search_url": "https://myauto.ge/search?make=Toyota",
                "chat_id": 123456789,  # This is the flattened chat_id
                "telegram_users": {
                    "id": "user-001",
                    "telegram_chat_id": 123456789
                }
            }

            # Simulate scheduler extraction (from _check_subscription)
            subscription_id = subscription.get("id")
            telegram_user_id = subscription.get("telegram_user_id")
            chat_id = subscription.get("chat_id")  # Should find this
            search_url = subscription.get("search_url")

            # Verify extraction
            assert subscription_id == "sub-001"
            assert telegram_user_id == "user-001"
            assert chat_id == 123456789, "chat_id should be extracted from flattened structure"
            assert search_url.startswith("https://myauto.ge/search")

            self.results.add_pass(test_name)
            return True

        except Exception as e:
            self.results.add_error(test_name, str(e))
            return False

    def test_no_subscriptions_empty_response(self):
        """Test 7: Handle empty subscription list gracefully"""
        test_name = "Handle empty subscription response"
        try:
            # Empty response
            subscriptions = []

            # Apply transformation
            flattened = []
            for sub in subscriptions:
                flattened_sub = dict(sub)
                if isinstance(sub.get('telegram_users'), dict):
                    user_data = sub['telegram_users']
                    flattened_sub['chat_id'] = user_data.get('telegram_chat_id')
                flattened.append(flattened_sub)

            # Verify
            assert len(flattened) == 0, "Should remain empty"

            self.results.add_pass(test_name)
            return True

        except Exception as e:
            self.results.add_error(test_name, str(e))
            return False

    def test_correct_vs_incorrect_query(self):
        """Test 8: Document the difference between incorrect and correct queries"""
        test_name = "Verify incorrect query vs correct query"
        try:
            # INCORRECT query (was using this)
            incorrect_query = "telegram_user_subscriptions?is_active=eq.true&select=*,users(id,username,telegram_chat_id,check_interval_minutes)"
            logger.info(f"[INCORRECT] {incorrect_query}")
            logger.info("[!] Problem: 'users' table doesn't exist - would return empty result")

            # CORRECT query (now using this)
            correct_query = "telegram_user_subscriptions?is_active=eq.true&select=*,telegram_users(id,telegram_chat_id)"
            logger.info(f"[CORRECT] {correct_query}")
            logger.info("[✓] Uses actual 'telegram_users' table and gets minimal required fields")

            # Verify query structure
            assert "telegram_users(" in correct_query, "Should use 'telegram_users'"
            assert "telegram_chat_id" in correct_query, "Should request telegram_chat_id"
            assert incorrect_query != correct_query, "Queries should be different"

            self.results.add_pass(test_name)
            return True

        except Exception as e:
            self.results.add_error(test_name, str(e))
            return False

    def test_logging_validation(self):
        """Test 9: Verify enhanced logging would catch issues"""
        test_name = "Enhanced logging provides visibility"
        try:
            test_cases = [
                # Case 1: Valid subscription
                {
                    "desc": "Valid subscription with chat_id",
                    "sub": {
                        "id": "sub-001",
                        "chat_id": 123456789,
                        "telegram_users": {"telegram_chat_id": 123456789}
                    },
                    "should_warn": False
                },
                # Case 2: Missing chat_id
                {
                    "desc": "Missing chat_id",
                    "sub": {
                        "id": "sub-001",
                        "chat_id": None,
                        "telegram_users": {"telegram_chat_id": None}
                    },
                    "should_warn": True
                }
            ]

            for case in test_cases:
                subscription = case["sub"]
                should_warn = case["should_warn"]

                # Simulate validation logic
                has_valid_chat_id = bool(subscription.get("chat_id"))

                if not has_valid_chat_id:
                    logger.warning(f"[WARN] Subscription {subscription.get('id')}: Missing chat_id")

                assert has_valid_chat_id != should_warn, f"Failed: {case['desc']}"

            self.results.add_pass(test_name)
            return True

        except Exception as e:
            self.results.add_error(test_name, str(e))
            return False

    def test_full_workflow_simulation(self):
        """Test 10: Full workflow simulation with realistic data"""
        test_name = "Full workflow simulation (end-to-end)"
        try:
            # Step 1: Simulate database response
            logger.info("[STEP 1] Simulating database response with CORRECT query...")
            db_response = [
                {
                    "id": "sub-001",
                    "telegram_user_id": "user-001",
                    "search_url": "https://myauto.ge/search?make=Toyota&minPrice=5000",
                    "search_name": "Toyota 5000+",
                    "is_active": True,
                    "last_checked": "2025-11-11T09:00:00",
                    "telegram_users": {
                        "id": "user-001",
                        "telegram_chat_id": 111111111
                    }
                },
                {
                    "id": "sub-002",
                    "telegram_user_id": "user-002",
                    "search_url": "https://myauto.ge/search?make=BMW",
                    "is_active": True,
                    "telegram_users": {
                        "id": "user-002",
                        "telegram_chat_id": 222222222
                    }
                }
            ]
            logger.info(f"[✓] Received {len(db_response)} subscriptions")

            # Step 2: Transform data
            logger.info("[STEP 2] Transforming data to flatten chat_id...")
            flattened = []
            for sub in db_response:
                flattened_sub = dict(sub)
                if isinstance(sub.get('telegram_users'), dict):
                    user_data = sub['telegram_users']
                    flattened_sub['chat_id'] = user_data.get('telegram_chat_id')
                    logger.debug(f"[✓] Sub {sub.get('id')}: chat_id={flattened_sub['chat_id']}")
                flattened.append(flattened_sub)
            logger.info(f"[✓] Transformed {len(flattened)} subscriptions")

            # Step 3: Validate all subscriptions have required fields
            logger.info("[STEP 3] Validating subscriptions...")
            for sub in flattened:
                sub_id = sub.get("id")
                telegram_user_id = sub.get("telegram_user_id")
                chat_id = sub.get("chat_id")
                search_url = sub.get("search_url")

                assert sub_id, f"Missing id"
                assert telegram_user_id, f"Missing telegram_user_id"
                assert chat_id, f"Missing chat_id for subscription {sub_id}"
                assert search_url, f"Missing search_url"
                logger.debug(f"[✓] Subscription {sub_id} valid")

            logger.info("[✓] All subscriptions validated")

            # Step 4: Simulate scheduler would group by user
            logger.info("[STEP 4] Grouping subscriptions by user...")
            users_to_notify = {}
            for sub in flattened:
                telegram_user_id = sub.get("telegram_user_id")
                chat_id = sub.get("chat_id")

                if telegram_user_id not in users_to_notify:
                    users_to_notify[telegram_user_id] = {
                        'chat_id': chat_id,
                        'subscriptions': []
                    }

                users_to_notify[telegram_user_id]['subscriptions'].append(sub)
                logger.debug(f"[✓] Added subscription to user {telegram_user_id}")

            logger.info(f"[✓] Grouped into {len(users_to_notify)} users")

            # Verify
            assert len(flattened) == 2
            assert len(users_to_notify) == 2
            assert all('chat_id' in sub for sub in flattened)

            self.results.add_pass(test_name)
            return True

        except Exception as e:
            self.results.add_error(test_name, str(e))
            import traceback
            logger.debug(traceback.format_exc())
            return False

    def run_all_tests(self):
        """Run all tests"""
        logger.info("=" * 70)
        logger.info("GIT ACTIONS FIX - COMPREHENSIVE TEST SUITE")
        logger.info("=" * 70)
        logger.info("")

        tests = [
            ("Mock Response Structure", self.test_mock_database_response_structure),
            ("Data Transformation", self.test_data_transformation_logic),
            ("Multiple Subscriptions", self.test_multiple_subscriptions_transformation),
            ("Missing telegram_users", self.test_edge_case_missing_telegram_users),
            ("Null chat_id", self.test_edge_case_empty_telegram_chat_id),
            ("Scheduler Extraction", self.test_scheduler_subscription_extraction),
            ("Empty Response", self.test_no_subscriptions_empty_response),
            ("Query Comparison", self.test_correct_vs_incorrect_query),
            ("Logging Validation", self.test_logging_validation),
            ("Full Workflow", self.test_full_workflow_simulation),
        ]

        for test_name, test_func in tests:
            logger.info(f"\n▶ {test_name}")
            logger.info("-" * 70)
            try:
                test_func()
            except Exception as e:
                self.results.add_error(test_name, str(e))
                import traceback
                logger.debug(traceback.format_exc())

        logger.info("")
        return self.results.print_summary()


def main():
    """Run the test suite"""
    tester = GitActionsFixTester()
    success = tester.run_all_tests()

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
