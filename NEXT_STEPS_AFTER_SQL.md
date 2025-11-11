# ✅ SQL DEPLOYED - WHAT'S NEXT?

**Status:** SQL Migration ✅ DONE

---

## 📋 REMAINING STEPS (7 more to go)

### STEP 2: Verify Tables Created ⏱️ (5 minutes)

**In Supabase SQL Editor, run this verification query:**

```sql
-- Verify all Telegram tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name LIKE 'telegram_%'
ORDER BY table_name;
```

**Expected result: 6 tables**
- ✅ telegram_bot_events
- ✅ telegram_user_api_tokens
- ✅ telegram_user_search_criteria
- ✅ telegram_user_seen_listings
- ✅ telegram_user_subscriptions
- ✅ telegram_users

If you see all 6 → **PROCEED TO STEP 3**
If you see less → Something went wrong, check error messages

---

### STEP 3: (OPTIONAL) Migrate Existing Data ⏱️ (5 minutes)

**Only if you have existing subscriptions to migrate from old system**

If YES → Run these 4 queries in Supabase SQL Editor (in order):

```sql
-- Query 1: Create Telegram users from existing chat_ids
INSERT INTO telegram_users (telegram_chat_id, telegram_user_id, first_name, last_name)
SELECT DISTINCT
    chat_id,
    NULL,
    'User',
    chat_id::TEXT
FROM (
    SELECT DISTINCT chat_id FROM user_subscriptions_old
    UNION
    SELECT DISTINCT chat_id FROM user_seen_listings_old
    UNION
    SELECT DISTINCT chat_id FROM bot_events_old
) as distinct_chats
WHERE chat_id IS NOT NULL;

-- Verify users created:
SELECT COUNT(*) as telegram_users_created FROM telegram_users;
```

```sql
-- Query 2: Copy subscriptions
INSERT INTO telegram_user_subscriptions (telegram_user_id, search_url, search_name, created_at, last_checked, is_active, chat_id)
SELECT
    tu.id,
    old.search_url,
    old.search_name,
    old.created_at,
    old.last_checked,
    old.is_active,
    old.chat_id
FROM user_subscriptions_old old
JOIN telegram_users tu ON tu.telegram_chat_id = old.chat_id
WHERE old.chat_id IS NOT NULL;

-- Verify subscriptions copied:
SELECT COUNT(*) as subscriptions_copied FROM telegram_user_subscriptions;
```

```sql
-- Query 3: Copy seen listings
INSERT INTO telegram_user_seen_listings (telegram_user_id, listing_id, seen_at, chat_id)
SELECT
    tu.id,
    old.listing_id,
    old.seen_at,
    old.chat_id
FROM user_seen_listings_old old
JOIN telegram_users tu ON tu.telegram_chat_id = old.chat_id
WHERE old.chat_id IS NOT NULL;

-- Verify seen listings copied:
SELECT COUNT(*) as seen_listings_copied FROM telegram_user_seen_listings;
```

```sql
-- Query 4: Copy bot events
INSERT INTO telegram_bot_events (telegram_user_id, event_type, event_data, created_at, chat_id)
SELECT
    tu.id,
    old.event_type,
    old.event_data,
    old.created_at,
    old.chat_id
FROM bot_events_old old
JOIN telegram_users tu ON tu.telegram_chat_id = old.chat_id
WHERE old.chat_id IS NOT NULL;

-- Verify bot events copied:
SELECT COUNT(*) as bot_events_copied FROM telegram_bot_events;
```

If NO existing data → **SKIP TO STEP 4**

---

### STEP 4: Update Python Code ⏱️ (30 minutes)

**File 1: Update `telegram_bot_main.py`**

Find this line:
```python
from telegram_bot_database_supabase import TelegramBotDatabaseSupabase
```

Replace with:
```python
from telegram_bot_database_multiuser import TelegramBotDatabaseMultiUser
```

Find this line:
```python
bot_db = TelegramBotDatabaseSupabase()
```

Replace with:
```python
bot_db = TelegramBotDatabaseMultiUser()
```

**File 2: Update `telegram_bot_scheduler.py`**

Find any references to:
- `user_subscriptions` → change to `telegram_user_subscriptions`
- `user_seen_listings` → change to `telegram_user_seen_listings`
- `bot_events` → change to `telegram_bot_events`
- `chat_id` parameter → change to `telegram_user_id` or `user_id`

**File 3: Update `telegram_bot_backend.py`**

Same replacements as File 2 above.

**Quick Search & Replace:**
- Find: `user_subscriptions` → Replace: `telegram_user_subscriptions`
- Find: `user_seen_listings` → Replace: `telegram_user_seen_listings`
- Find: `bot_events` → Replace: `telegram_bot_events`

---

### STEP 5: Test the Deployment ⏱️ (10 minutes)

**Run this test in Python:**

```python
from database_rest_api import DatabaseManager
from telegram_bot_database_multiuser import TelegramBotDatabaseMultiUser

# Initialize
db = DatabaseManager()
bot_db = TelegramBotDatabaseMultiUser()

# Test 1: Create test Telegram user
print("[*] Test 1: Creating test Telegram user...")
response = db._make_request(
    'POST',
    f"{db.base_url}/telegram_users",
    json={
        "telegram_chat_id": 999999999,  # Test chat ID
        "first_name": "Test",
        "last_name": "User"
    },
    headers=db.headers,
    timeout=10
)

if response.status_code in [200, 201]:
    user = response.json() if isinstance(response.json(), dict) else response.json()[0]
    user_id = user.get("id")
    print(f"[✓] User created: {user_id}")
else:
    print(f"[✗] Failed: {response.status_code}")
    exit(1)

# Test 2: Add subscription
print("[*] Test 2: Adding subscription...")
success, error = bot_db.add_subscription(
    user_id=user_id,
    search_url="https://www.myauto.ge/test",
    search_name="Test Search"
)

if success:
    print("[✓] Subscription added")
else:
    print(f"[✗] Failed: {error}")
    exit(1)

# Test 3: Record seen listing
print("[*] Test 3: Recording seen listing...")
bot_db.record_user_seen_listing(user_id, "test_listing_123")
print("[✓] Listing marked as seen")

# Test 4: Check if seen
print("[*] Test 4: Checking if listing is seen...")
is_seen = bot_db.has_user_seen_listing(user_id, "test_listing_123")
if is_seen:
    print("[✓] Deduplication working correctly")
else:
    print("[✗] Deduplication failed")
    exit(1)

# Test 5: Log event
print("[*] Test 5: Logging event...")
bot_db.log_event(
    user_id=user_id,
    event_type="deployment_test",
    event_data={"test": "success"}
)
print("[✓] Event logged")

print("\n[✅] ALL TESTS PASSED!")
print(f"Test user ID: {user_id}")
```

**Expected output:**
```
[*] Test 1: Creating test Telegram user...
[✓] User created: <uuid>
[*] Test 2: Adding subscription...
[✓] Subscription added
[*] Test 3: Recording seen listing...
[✓] Listing marked as seen
[*] Test 4: Checking if listing is seen...
[✓] Deduplication working correctly
[*] Test 5: Logging event...
[✓] Event logged

[✅] ALL TESTS PASSED!
```

If you see this → **PROCEED TO STEP 6**
If you see errors → Check error messages and see troubleshooting below

---

### STEP 6: Verify Views & Statistics ⏱️ (5 minutes)

**Run these queries in Supabase SQL Editor:**

```sql
-- Check subscription statistics
SELECT * FROM telegram_subscription_stats;
```

Expected result:
| total_active_users | total_active_subscriptions | avg_subscriptions_per_user |
|--------------------|---------------------------|--------------------------|
| 1 (or your count)  | 1 (or your count)         | 1.00                     |

```sql
-- Check active subscriptions per user
SELECT * FROM telegram_user_subscriptions_active;
```

```sql
-- Check recent events
SELECT * FROM telegram_bot_events_recent;
```

If all 3 queries return data → **PROCEED TO STEP 7**

---

### STEP 7: Deploy Updated Bot Code ⏱️ (10 minutes)

**In your terminal:**

```bash
# Commit changes
git add telegram_bot_main.py telegram_bot_scheduler.py telegram_bot_backend.py

git commit -m "feat: Migrate to Telegram multi-user system

- Update imports to use telegram_bot_database_multiuser
- Replace all table name references with telegram_* versions
- Add support for individual user search criteria
- Implement per-user deduplication"

# Push to production
git push origin main
```

**Monitor deployment:**
- Check bot startup logs
- Look for any error messages
- Test `/set` command in Telegram
- Test `/list` command

If no errors → **PROCEED TO STEP 8**

---

### STEP 8: Cleanup (OPTIONAL) ⏱️ (5 minutes)

**Only after you've verified everything is working:**

```sql
-- Drop old tables (BACKUP FIRST!)
DROP TABLE IF EXISTS user_subscriptions_old;
DROP TABLE IF EXISTS user_seen_listings_old;
DROP TABLE IF EXISTS bot_events_old;
```

**Or keep them as backup** (safe to leave)

---

## ✅ FINAL CHECKLIST

After completing all steps:

- [ ] Step 2: Verified 6 Telegram tables exist
- [ ] Step 3: Migrated existing data (optional)
- [ ] Step 4: Updated Python code with new imports
- [ ] Step 5: All tests passed
- [ ] Step 6: Views return correct statistics
- [ ] Step 7: Bot code deployed to production
- [ ] Step 8: Old tables cleaned up (optional)

If all checked → **YOU'RE DONE! 🎉**

---

## 🚨 TROUBLESHOOTING

### Error: "Table doesn't exist"
**Solution:** Run Step 2 verification query. If table doesn't exist, SQL migration failed.

### Error: "Foreign key constraint"
**Solution:** Ensure Step 3 (create users) ran before copying subscriptions.

### Python import error
**Solution:**
```python
# Make sure these files exist:
- telegram_bot_database_multiuser.py
- search_criteria_management.py
```

### Bot not starting
**Solution:**
- Check SUPABASE_URL environment variable
- Check SUPABASE_API_KEY environment variable
- Check Python imports are correct
- Check table names are updated

### No data in views
**Solution:**
```sql
SELECT COUNT(*) FROM telegram_users;
SELECT COUNT(*) FROM telegram_user_subscriptions;
-- If both are 0, you need to create test data or migrate old data
```

---

## ⏱️ TOTAL TIME REMAINING

| Step | Time | Done? |
|------|------|-------|
| Step 2: Verify Tables | 5 min | |
| Step 3: Migrate Data | 5 min | (optional) |
| Step 4: Update Code | 30 min | |
| Step 5: Test | 10 min | |
| Step 6: Verify Stats | 5 min | |
| Step 7: Deploy | 10 min | |
| Step 8: Cleanup | 5 min | (optional) |
| **TOTAL** | **~70 min** | |

---

## 👉 NEXT ACTION

**RIGHT NOW:**

1. Go back to Supabase
2. Run the verification query from **STEP 2** above
3. Confirm you see all 6 telegram_* tables
4. Come back and continue with STEP 3 or STEP 4

**You're doing great! Keep going! 🚀**
