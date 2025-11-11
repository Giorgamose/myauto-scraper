# Quick Test Guide - Run & Verify Everything Works

## 30-Second Quick Start

```bash
# Navigate to bot directory
cd "c:\Users\gmaevski\Documents\MyAuto Listening Scrapper"

# Run the test suite
python test_telegram_bot.py

# Check results
cat test_report.txt
```

## What Happens

The test suite automatically:
1. ✅ Creates a test user
2. ✅ Adds two subscriptions
3. ✅ Lists subscriptions
4. ✅ Resets tracking history
5. ✅ Removes a subscription
6. ✅ Fetches real listings
7. ✅ Verifies data persistence
8. ✅ Tests error handling

## Expected Output

```
========================================================

     TELEGRAM BOT COMPREHENSIVE TEST SUITE

  Testing: /list, /set, /reset, /clear, /run

========================================================

======================================================================
                TEST 1: USER CREATION
======================================================================

[PASS] User creation/retrieval
        User ID: a1b2c3d4...
[PASS] User has subscriptions list
        Subscriptions: 0

======================================================================
             TEST 2: /SET COMMAND (ADD SUBSCRIPTION)
======================================================================

[PASS] Add first subscription
        Subscription ID: xyz...
[PASS] Add second subscription
        Subscription ID: abc...

... more tests ...

======================================================================
                      FINAL TEST REPORT
======================================================================

Test Summary:
  Total Tests:  9
  Passed:       9
  Failed:       0
  Success Rate: 100.0%
  Duration:     25.34s

*** ALL TESTS PASSED! ***
```

## Interpreting Results

### ✅ All Tests Passed
```
*** ALL TESTS PASSED! ***
Success Rate: 100.0%
```
**Status:** Everything working! Deploy with confidence.

### ❌ Some Tests Failed
```
*** 3 TEST(S) FAILED ***
[FAIL] User creation/retrieval
[FAIL] /set command
```
**Status:** Fix issues before deploying. Check logs.

### ⏱️ Network Timeout
```
[WARN] Database connection attempt 1 failed, retrying...
```
**Status:** Usually transient. Tests retry automatically. Run again if persistent issues.

## Test Breakdown

### Test 1: User Creation (1-2 sec)
Creates test account
```
[PASS] User creation/retrieval
[PASS] User has subscriptions list
```

### Test 2: /set Command (1 sec)
Adds subscriptions
```
[PASS] Add first subscription
[PASS] Add second subscription
```

### Test 3: /list Command (1 sec)
Shows subscriptions
```
[PASS] Retrieve subscriptions
[PASS] First subscription has required fields
[PASS] Second subscription has required fields
```

### Test 4: /reset Command (2 sec)
Clears tracking
```
[PASS] Mark listings as seen
[PASS] Reset subscription check time
```

### Test 5: /clear Command (1 sec)
Removes subscriptions
```
[PASS] Remove subscription
[PASS] Subscription count decreased
[PASS] Removed subscription not in list
```

### Test 6: /run Command (10-15 sec)
Fetches real listings (slowest test)
```
[PASS] Create scraper
[PASS] Fetch listings (found 30)
[PASS] Listing has required fields
[PASS] Deduplication tracking
```

### Test 7: Data Persistence (1 sec)
Verifies data survives
```
[PASS] Subscriptions persist across calls
[PASS] Subscription details are correct
```

### Test 8: Error Handling (2 sec)
Tests error scenarios
```
[PASS] Handle invalid user ID gracefully
[PASS] Handle empty URL
[PASS] Handle duplicate URL
```

## Common Issues & Solutions

### Issue: "Failed to connect to Supabase"
```
[ERROR] Failed to initialize database
```
**Solution:**
1. Check .env.local exists
2. Verify SUPABASE_URL is set
3. Verify SUPABASE_API_KEY is set
4. Check internet connection
5. Verify firewall allows Supabase

### Issue: "Read timed out"
```
[WARN] Database connection attempt 1 failed, retrying...
```
**Solution:**
- Tests retry automatically (wait 20 seconds)
- If persistent, check internet
- Check Supabase status: https://status.supabase.io

### Issue: "/run command failed to fetch listings"
```
[FAIL] /run command - Fetch listings
       Found 0 listings
```
**Solution:**
- MyAuto.ge may be rate limiting (wait an hour)
- Check internet connection
- Verify test URLs are valid
- Try again later

### Issue: "Duplicate URL" or "Empty URL" errors
```
[FAIL] Handle empty URL
```
**Solution:**
- These are expected error tests
- Tests verify error handling works
- If other tests fail, investigate

## Running Specific Tests

Want to test just the /run command?

Edit `test_telegram_bot.py`, change `run_all_tests()` method:

```python
def run_all_tests(self) -> bool:
    results = [
        self.test_user_creation(),       # Need this
        self.test_set_command(),         # Need this
        # Skip other tests
        # ...
        self.test_run_command(),         # Run this
        # Skip rest
    ]
```

## Before & After Deployment

### Before Every Code Change
```bash
python test_telegram_bot.py
# Verify all tests still pass
# If any fail, don't commit
```

### After Making Changes
```bash
python test_telegram_bot.py
# Ensure no regressions introduced
# Prevents breaking existing features
```

### Before Production Deployment
```bash
python test_telegram_bot.py
# All tests must pass
# Check test_report.txt
# Review any [WARN] entries
```

## Test Report File

The `test_report.txt` file contains:
- Timestamp of test run
- Total duration
- Pass/fail count
- Individual test results
- Detailed notes for each test

Example:
```
TELEGRAM BOT TEST REPORT
======================================================================
Timestamp: 2025-11-11 12:46:49.189000
Duration: 25.34s

Summary:
  Total:  8
  Passed: 8
  Failed: 0
  Success: 100.0%

Details:
1. [PASS] User creation/retrieval
   User ID: a1b2c3d4...
2. [PASS] Add first subscription
   Subscription ID: x...
...
```

## Continuous Testing

Set up automated testing:

### Windows Task Scheduler
```
Program: python
Arguments: test_telegram_bot.py
Location: C:\Users\...\MyAuto Listening Scrapper
Schedule: Daily at 00:00
```

### Linux Cron
```bash
# Add to crontab
0 0 * * * cd /path/to/bot && python test_telegram_bot.py >> test_results.log 2>&1
```

## Success Metrics

| Metric | Good | Acceptable | Bad |
|--------|------|-----------|-----|
| Pass Rate | 100% | 90%+ | <90% |
| Duration | <30s | <45s | >45s |
| Errors | 0 | 0 | >0 |
| Warnings | 0 | <2 | >2 |

## Troubleshooting Checklist

- [ ] Run `python test_telegram_bot.py`
- [ ] Wait for tests to complete (20-30 seconds)
- [ ] Check console output for [PASS] or [FAIL]
- [ ] Review test_report.txt for details
- [ ] If failures:
  - [ ] Check .env.local configuration
  - [ ] Verify Supabase connectivity
  - [ ] Check internet connection
  - [ ] Review logs for [ERROR] entries
  - [ ] Run tests again
- [ ] If 100% pass:
  - [ ] Ready to deploy
  - [ ] Commit code
  - [ ] Update version

## Quick Reference

```bash
# Run tests
python test_telegram_bot.py

# View results
cat test_report.txt

# View recent errors
python test_telegram_bot.py 2>&1 | grep ERROR

# View all warnings
python test_telegram_bot.py 2>&1 | grep WARN

# Just see final report
python test_telegram_bot.py 2>&1 | tail -20
```

## Summary

The test suite is designed to be:
- ✅ **Simple** - Run one command
- ✅ **Fast** - Complete in 30 seconds
- ✅ **Comprehensive** - Tests all features
- ✅ **Reliable** - Detects regressions
- ✅ **Actionable** - Clear pass/fail results

**Run tests before every deployment to prevent bugs!**
