# Telegram Bot Test Suite - Complete Guide

## Overview

The `test_telegram_bot.py` is a comprehensive automated test suite that validates all Telegram bot functionality. It tests the core commands: `/list`, `/set`, `/reset`, `/clear`, and `/run`.

## Quick Start

```bash
# Run all tests
python test_telegram_bot.py

# Tests will output to console and save detailed report
```

## What Gets Tested

### Test 1: User Creation
- Verifies user account creation from Telegram chat ID
- Creates a test user in the database
- Validates user ID is properly generated

### Test 2: /set Command
- Adds first subscription (Toyota Jeep search)
- Adds second subscription (BMW Sedan search)
- Validates subscription IDs are returned
- Confirms subscriptions are stored in database

### Test 3: /list Command
- Retrieves all user subscriptions
- Validates subscription structure
- Confirms required fields present (id, search_url, name)
- Verifies subscriptions are marked as active

### Test 4: /reset Command
- Marks test listings as "seen"
- Confirms they're tracked
- Resets subscription tracking history
- Validates reset was successful

### Test 5: /clear Command
- Removes a subscription from the user's list
- Verifies subscription count decreased
- Confirms removed subscription is not in remaining list

### Test 6: /run Command
- Creates scraper instance
- Fetches actual listings from MyAuto.ge
- Validates listing structure
- Tests deduplication tracking

### Test 7: Data Persistence
- Verifies data survives across multiple calls
- Re-fetches subscriptions to confirm persistence
- Validates subscription details match original

### Test 8: Error Handling
- Tests invalid user ID handling
- Tests empty URL rejection
- Tests duplicate subscription handling

## Test Output

### Console Output
```
======================================================================
                TEST 1: USER CREATION
======================================================================

[PASS] User creation/retrieval
        User ID: 2a3b4c5d...
[PASS] User has subscriptions list
        Subscriptions: 0
```

### Report File: test_report.txt
```
Test Summary:
  Total Tests:  9
  Passed:       9
  Failed:       0
  Success Rate: 100.0%
  Duration:     45.23s

Detailed Results:
1. [PASS] User creation/retrieval
   -> User ID: 2a3b4c5d...
```

## Success Criteria

**All tests pass when:**
- ✅ User can be created/retrieved
- ✅ Subscriptions can be added
- ✅ Subscriptions can be listed
- ✅ Tracking history can be reset
- ✅ Subscriptions can be removed
- ✅ Real listings can be fetched
- ✅ Data persists across calls
- ✅ Errors are handled gracefully

## Running Tests in CI/CD

The test suite is designed to be run automatically during deployment:

```bash
#!/bin/bash
# Example CI/CD script

echo "Running Telegram Bot Tests..."
python test_telegram_bot.py

if [ $? -eq 0 ]; then
    echo "SUCCESS: All tests passed"
    exit 0
else
    echo "FAILURE: Some tests failed"
    exit 1
fi
```

## Troubleshooting

### Test Timeouts
If tests timeout connecting to Supabase:
- Check internet connection
- Verify Supabase credentials in .env.local
- Check firewall/proxy settings
- Tests include retry logic for transient issues

### Database Connection Issues
```
[ERROR] Failed to connect to Supabase REST API
```
Solution:
- Verify SUPABASE_URL in .env.local
- Verify SUPABASE_API_KEY in .env.local
- Check database tables exist (telegram_users, telegram_user_subscriptions)
- Verify network connectivity

### Scraper Issues
```
[ERROR] Failed to fetch listings from MyAuto.ge
```
Solution:
- MyAuto.ge might be rate limiting
- Test URL might not have listings
- Check internet connectivity
- Verify Playwright is installed: `pip install playwright`

## Test Configuration

Edit `test_telegram_bot.py` to customize:

```python
# Test chat ID (use unique number for testing)
TEST_CHAT_ID = 123456789

# Search URLs to test
TEST_SEARCH_URL = "https://www.myauto.ge/ka/s/..."
TEST_SEARCH_URL_2 = "https://www.myauto.ge/ka/s/..."
```

## Integration with Development

### Before Committing Code
```bash
# Run tests to verify no regressions
python test_telegram_bot.py

# Check if test_report.txt shows 100% success
```

### After Merging Changes
```bash
# Run full test suite on main branch
python test_telegram_bot.py

# Verify all tests still pass
```

## Test Results Interpretation

### Success Rate 100%
```
*** ALL TESTS PASSED! ***
```
- All functionality working correctly
- Safe to deploy
- No known issues

### Partial Failures (< 100%)
```
*** 2 TEST(S) FAILED ***

[FAIL] /set command
[FAIL] /run command
```
- Specific features affected
- Review logs to identify issue
- Do not deploy until fixed

### Network Issues
```
[WARN] Database connection attempt 1 failed, retrying...
```
- Tests have retry logic
- Usually transient
- If persistent, check infrastructure

## Performance

Typical test run times:
- User creation: 1-2 seconds
- /set command: 0.5 seconds
- /list command: 0.5 seconds
- /reset command: 1 second
- /clear command: 0.5 seconds
- /run command: 8-15 seconds (includes network call to MyAuto.ge)
- Data persistence: 0.5 seconds
- Error handling: 1 second

**Total expected time: 15-25 seconds**

## Advanced Usage

### Running Individual Tests
Modify `test_telegram_bot.py` to comment out tests you don't want to run:

```python
def run_all_tests(self) -> bool:
    """Run all tests"""

    results = [
        self.test_user_creation(),           # Run this
        # self.test_set_command(),           # Skip this
        self.test_list_command(),            # Run this
        # self.test_reset_command(),         # Skip this
        # ...
    ]
```

### Continuous Monitoring
Set up scheduled test runs:

```bash
# crontab -e
# Run tests every hour
0 * * * * cd /path/to/bot && python test_telegram_bot.py > test_results.log 2>&1
```

## Reporting Issues

If tests fail:
1. Run test again to verify not transient
2. Check test_report.txt for details
3. Review bot logs for exceptions
4. Verify environment (.env.local)
5. Check database connectivity

## Maintenance

Update tests when:
- Adding new bot commands
- Changing database schema
- Modifying subscription structure
- Altering user workflow

Example: Adding new /unset command test

```python
def test_unset_command(self) -> bool:
    """Test /unset Command - Remove single subscription"""
    self.print_section("TEST X: /UNSET COMMAND")

    # Test implementation...
    return success
```

## Summary

The test suite provides:
- ✅ Automated validation of all core features
- ✅ Early detection of regressions
- ✅ Confidence in deployments
- ✅ Documentation of expected behavior
- ✅ Easy integration with CI/CD pipelines

Run tests after any changes to ensure nothing breaks!
