# Comprehensive Test Suite - Complete Guide

## Overview

The `test_telegram_bot_comprehensive.py` is an advanced test suite that covers edge cases, batch scenarios, and real-world conditions.

**15 critical test scenarios** ensuring production readiness.

## Quick Start

```bash
# Run comprehensive tests
python test_telegram_bot_comprehensive.py

# View detailed report
cat test_comprehensive_report.txt
```

## Test Groups & Coverage

### Group 1: Basic Operations (3 tests)

#### Test 1: User Creation
- Creates test user from Telegram chat ID
- Verifies user ID generation
- Validates user account setup

```
[PASS] User creation
[PASS] User has subscriptions list
```

#### Test 2: Add Subscriptions
- Adds small search (Toyota Jeep)
- Adds medium search (BMW Sedan)
- Adds large search (All cars)
- Verifies subscription IDs returned

```
[PASS] Add small search subscription
[PASS] Add medium search subscription
[PASS] Add large search subscription
```

#### Test 3: List Subscriptions
- Retrieves all user subscriptions
- Validates subscription structure
- Confirms required fields present

```
[PASS] List subscriptions - Retrieve
[PASS] List subscriptions - Sub 1 fields
```

---

### Group 2: Listing Edge Cases (5 tests)

#### Test 4: Single Listing Scenario
**Scenario:** User's search returns only 1 result

Expected behavior:
- Message fits in single Telegram message
- No batching needed
- Proper formatting applied

```
[PASS] Single listing - Format
[PASS] Single listing - Message size (2100 chars)
```

**Why this matters:**
- Ensures system handles minimum case
- Validates single message formatting
- Tests message size calculation

---

#### Test 5: Batch Boundary - 10 Listings
**Scenario:** Search returns exactly 10 listings (exact batch size)

Expected behavior:
- Creates exactly 1 batch
- All 10 listings in one message
- No overflow to second batch

```
[PASS] Batch boundary - Have 10 listings
[PASS] Batch boundary - Should be 1 batch
[PASS] Batch boundary - Message fits in 4096
```

**Why this matters:**
- Tests batch boundary condition
- Ensures no unnecessary splitting
- Validates batch size algorithm

---

#### Test 6: Batch Boundary - 11 Listings
**Scenario:** Search returns 11 listings (triggers 2-batch split)

Expected behavior:
- Creates exactly 2 batches
- First batch: 10 listings
- Second batch: 1 listing
- Both messages under 4096 chars
- Shows "Batch 1 of 2" and "Batch 2 of 2"

```
[PASS] Batch split - Have 11 listings
[PASS] Batch split - Should be 2 batches
[PASS] Batch split - First batch size (10)
[PASS] Batch split - Second batch size (1)
[PASS] Batch split - Batch 1 message size
[PASS] Batch split - Batch 2 message size
```

**Why this matters:**
- **CRITICAL:** Tests batch boundary at edge
- Ensures proper splitting at 11 (>10)
- Verifies batch headers show correct numbering

---

#### Test 7: Multiple Batches - 20 Listings
**Scenario:** Search returns 20 listings

Expected behavior:
- Creates exactly 2 batches
- First batch: 10 listings
- Second batch: 10 listings
- Both under size limit
- Batch headers working

```
[PASS] 20 listings - Have 20 listings
[PASS] 20 listings - Should be 2 batches
[PASS] 20 listings - First batch has 10
[PASS] 20 listings - Second batch has 10
```

**Why this matters:**
- Tests typical "full page" of results
- Ensures even distribution
- Validates 2-batch scenario

---

#### Test 8: Many Batches - 30 Listings
**Scenario:** Search returns 30 listings (user runs /run on large search)

Expected behavior:
- Creates exactly 3 batches
- Each batch: 10 listings
- All batches under 4096 chars
- Headers show "Batch X of 3"

```
[PASS] 30 listings - Have 30 listings
[PASS] 30 listings - Should be 3 batches
[PASS] 30 listings - Batch 1 size (10)
[PASS] 30 listings - Batch 2 size (10)
[PASS] 30 listings - Batch 3 size (10)
[PASS] 30 listings - Batch 1 has header
[PASS] 30 listings - Batch 2 has header
[PASS] 30 listings - Batch 3 has header
```

**Why this matters:**
- **MOST IMPORTANT:** User runs /run and gets 30 results
- Tests real-world scenario (max 100 results)
- Ensures all 3 batches delivered
- Validates "Batch X of Y" headers

---

### Group 3: Deduplication (3 tests)

#### Test 9: Deduplication Tracking
**Scenario:** Mark listings as seen, verify tracking

Expected behavior:
- Listings can be marked as seen
- System remembers which listings seen
- Prevents duplicates in notifications

```
[PASS] Deduplication - Mark listings as seen
[PASS] Deduplication - New listings identified
```

**Why this matters:**
- Core feature: Don't notify about same car twice
- Tests database tracking
- Validates dedup across calls

---

#### Test 10: Mixed Seen and New
**Scenario:** Some listings already seen, some new

Expected behavior:
- System distinguishes seen vs new
- Only sends new in notifications
- Properly handles mixed sets

```
[PASS] Mixed - Seen vs new distinction
```

**Why this matters:**
- Real-world scenario: /run on search checked before
- Should show only new results
- Tests dedup in list filtering

---

#### Test 11: Deduplication Across Sessions
Implicit in Test 9-10
- Marks listings seen in one call
- Subsequent calls show as already seen
- Data persists in database

---

### Group 4: Price Formatting (1 test)

#### Test 12: Price Formatting Edge Cases
**Scenarios tested:**

| Price | Format | Description |
|-------|--------|-------------|
| 1,000 | ₾1,000 | Small price |
| 10,000 | ₾10,000 | 5-digit |
| 100,000 | ₾100,000 | 6-digit |
| 1,234,567 | ₾1,234,567 | 7-digit |
| 59,500 | ₾59,500 | Real example |

```
[PASS] Price format - Small price (1000)
[PASS] Price format - 5-digit price (10000)
[PASS] Price format - 6-digit price (100000)
[PASS] Price format - 7-digit price (1234567)
[PASS] Price format - Real example (59500)
```

**Why this matters:**
- **CRITICAL BUG FIX:** Was extracting "59,500" as "22,000"
- Now verifies all comma-separated prices work
- Ensures ₾ symbol appears correctly
- Tests the fix is working

---

### Group 5: Message Size Validation (1 test)

#### Test 13: Message Size Limits
**Scenario:** Verify all messages stay under 4096 character limit

Expected behavior:
- Single batch messages < 4096
- Multi-batch messages < 4096 each
- Shows percentage of limit used

```
[PASS] Message size - Batch 1 (3200/4096 chars - 78.1%)
[PASS] Message size - Batch 2 (3100/4096 chars - 75.6%)
[PASS] Message size - Batch 3 (2950/4096 chars - 72.0%)
```

**Why this matters:**
- Telegram hard limit: 4096 characters per message
- Messages over limit get truncated/rejected
- Test ensures system respects this limit
- Validates batching strategy works

---

### Group 6: Subscription Management (2 tests)

#### Test 14: List All Subscriptions
- Retrieves user's subscriptions
- Validates structure
- Confirms fields present

```
[PASS] List subscriptions - Retrieve
[PASS] List subscriptions - Sub 1 fields
[PASS] List subscriptions - Sub 2 fields
[PASS] List subscriptions - Sub 3 fields
```

---

#### Test 15: Remove and Verify
**Scenario:** Remove subscription, verify it's gone

Expected behavior:
- Deletion successful
- Subscription count decreases
- Removed subscription not in list
- Data persists

```
[PASS] Remove subscription - Deletion
[PASS] Remove subscription - Count decreased
[PASS] Remove subscription - Not in list
```

---

### Group 7: Error Handling (2 tests)

#### Test 16: Comprehensive Error Handling
**Scenarios:**

1. Invalid User ID
```
[PASS] Error handling - Invalid user ID
       Handled gracefully
```

2. Empty URL
```
[PASS] Error handling - Empty URL
       Rejected empty URL
```

3. None/Null URL
```
[PASS] Error handling - None URL
       Rejected None URL
```

4. Very Long URL
```
[PASS] Error handling - Very long URL
       Handled long URL
```

**Why this matters:**
- System shouldn't crash on bad input
- Should reject invalid data
- Should handle edge cases gracefully

---

#### Test 17: Special Characters in Data
**Scenario:** Subscription names with special characters

Test examples:
- "Search #1 (BMW 3-Series) - €Test"
- Names with accents, symbols, emoji

```
[PASS] Special characters - Add with special chars
[PASS] Special characters - Retrieve correctly
```

**Why this matters:**
- Real users might use special chars
- Data should round-trip correctly
- No corruption or loss

---

## Test Summary Table

| # | Test | Category | Edge Case | Critical |
|---|------|----------|-----------|----------|
| 1 | User Creation | Basic | Standard | ✅ |
| 2 | Add Subscriptions | Basic | Standard | ✅ |
| 3 | List Subscriptions | Basic | Standard | ✅ |
| 4 | Single Listing | Batching | Min case | ✅ |
| 5 | Batch 10 | Batching | Boundary | ✅ |
| 6 | Batch 11 | Batching | Boundary | ✅✅ |
| 7 | Batch 20 | Batching | Normal | ✅ |
| 8 | Batch 30 | Batching | Real-world | ✅✅ |
| 9 | Dedup Track | Dedup | Core feature | ✅ |
| 10 | Mixed Seen | Dedup | Edge case | ✅ |
| 11 | Price Format | Formatting | Critical bug fix | ✅✅ |
| 12 | Message Size | Validation | Hard limit | ✅ |
| 13 | List Subscriptions | Management | Standard | ✅ |
| 14 | Remove Verify | Management | Standard | ✅ |
| 15 | Error Handling | Robustness | Edge cases | ✅ |
| 16 | Special Chars | Robustness | Unicode | ✅ |

## Expected Results

### Perfect Run (100% Pass)
```
Test Summary:
  Total Tests:  16
  Passed:       16
  Failed:       0
  Success Rate: 100.0%
  Duration:     45.32s

*** ALL TESTS PASSED! ***
```

### Typical Issues & Solutions

#### Issue: "Batch split - Should be 2 batches"
Failed when expecting 2 batches from 11 listings
```
[FAIL] Batch split - Should be 2 batches
       Batches: 1
```
**Solution:**
- Check batch splitting logic
- Verify max_listings_per_batch = 10
- Check if listings are being filtered

#### Issue: "Price format tests failed"
Some prices not formatting correctly
```
[FAIL] Price format - 7-digit price (1234567)
       Expected: ₾1,234,567, Found: False
```
**Solution:**
- Check price extraction code
- Verify comma handling in parser.py
- Test the fix: `extract_number("1,234,567")` should return `1234567`

#### Issue: "Message size exceeds limit"
Batch message over 4096 chars
```
[FAIL] Message size - Batch 1
       Size: 4200/4096 chars (102.4%)
```
**Solution:**
- Reduce items per batch (from 10 to 8)
- Shorten listing format
- Check for extremely long car titles

#### Issue: Network timeouts
```
[WARN] Database connection attempt 1 failed, retrying...
```
**Solution:**
- Tests retry automatically
- Wait 30 seconds for retry
- Check internet connection
- Verify Supabase status

## Running Specific Test Groups

Edit `test_telegram_bot_comprehensive.py` to skip groups:

```python
def run_all_tests(self) -> bool:
    results = [
        self.test_01_user_creation(),           # Run
        self.test_02_add_subscriptions(),       # Run
        self.test_03_single_listing_scenario(), # Run
        # self.test_04_batch_boundary_10_listings(),  # Skip
        # self.test_05_batch_boundary_11_listings(),  # Skip
        # ... skip others
    ]
```

## Performance Expectations

| Test | Time | Why |
|------|------|-----|
| Tests 1-3 | 5 sec | Database operations |
| Tests 4-8 | 20-30 sec | Web scraping (slow) |
| Tests 9-10 | 5 sec | Database operations |
| Test 11 | <1 sec | Local formatting |
| Test 12 | 10-15 sec | Web scraping |
| Tests 13-16 | 5 sec | Database operations |
| **Total** | **45-50 sec** | Realistic run time |

## Continuous Integration

For CI/CD pipelines:

```bash
#!/bin/bash
echo "Running comprehensive tests..."
python test_telegram_bot_comprehensive.py

if [ $? -eq 0 ]; then
    echo "PASS: All comprehensive tests passed"
    exit 0
else
    echo "FAIL: Some tests failed"
    cat test_comprehensive_report.txt
    exit 1
fi
```

## Deployment Checklist

- [ ] Run `python test_telegram_bot_comprehensive.py`
- [ ] All 16 tests pass
- [ ] Check test_comprehensive_report.txt
- [ ] Review any [WARN] entries
- [ ] Verify message sizes
- [ ] Confirm batch counts
- [ ] Check price formatting
- [ ] Ready to deploy!

## Summary

This comprehensive test suite ensures:

✅ **Batching Works Correctly**
- Single results handled
- Batch boundaries correct (10 items)
- Multiple batches split properly
- All messages under Telegram limit

✅ **Deduplication Works**
- Listings tracked as seen
- Duplicates prevented
- Mixed scenarios handled

✅ **Formatting Correct**
- Prices formatted with ₾
- Comma separation works
- All data types handled

✅ **Error Handling Robust**
- Invalid input rejected
- Special characters work
- System doesn't crash

✅ **Production Ready**
- 16 critical scenarios tested
- Edge cases covered
- Real-world usage validated

**Run these tests before every deployment!**
