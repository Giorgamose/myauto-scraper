# 🚀 Telegram Multi-User System - Deployment Guide

## Status: READY FOR DEPLOYMENT ✅

---

## 📋 Pre-Deployment Checklist

- [x] SQL migration script created and tested
- [x] All 6 Telegram tables designed
- [x] Views and cleanup functions included
- [x] Data migration scripts included (commented)
- [x] Python modules ready (search_criteria_management.py, telegram_bot_database_multiuser.py)
- [x] Documentation complete

---

## 🎯 STEP 1: Deploy SQL Migration to Supabase

### 1.1 Prepare for Deployment

```bash
# Backup your current Supabase database (optional but recommended)
# - Go to Supabase Dashboard
# - Project Settings → Backups
# - Click "Create backup"
```

### 1.2 Run SQL Migration

1. **Open Supabase Dashboard**
   - Go to https://app.supabase.com
   - Select your project

2. **Navigate to SQL Editor**
   - Click "SQL Editor" in left sidebar
   - Click "New query"

3. **Copy & Paste Migration Script**
   - Open `sql_migration_multi_user.sql`
   - Select ALL content (Ctrl+A)
   - Copy (Ctrl+C)
   - Paste into Supabase SQL Editor (Ctrl+V)

4. **Execute the Script**
   - Click "RUN" button (or Ctrl+Enter)
   - Wait for completion (~10-30 seconds)

### 1.3 Expected Output

```
✓ Query executed successfully

Created:
- telegram_users (table)
- telegram_user_api_tokens (table)
- telegram_user_search_criteria (table)
- telegram_user_subscriptions (table)
- telegram_user_seen_listings (table)
- telegram_bot_events (table)
- 4 views
- 3 cleanup functions
- Multiple indexes
```

---

## ✅ STEP 2: Verify Tables Created

### 2.1 Run Verification Query

In Supabase SQL Editor, run:

```sql
-- Verify all Telegram tables exist
SELECT table_name, 'Created ✓' as status
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
    'telegram_users',
    'telegram_user_api_tokens',
    'telegram_user_search_criteria',
    'telegram_user_subscriptions',
    'telegram_user_seen_listings',
    'telegram_bot_events'
)
ORDER BY table_name;
```

### 2.2 Expected Results

| table_name | status |
|-----------|--------|
| telegram_bot_events | Created ✓ |
| telegram_user_api_tokens | Created ✓ |
| telegram_user_search_criteria | Created ✓ |
| telegram_user_seen_listings | Created ✓ |
| telegram_user_subscriptions | Created ✓ |
| telegram_users | Created ✓ |

### 2.3 Verify Views

```sql
-- Verify views were created
SELECT viewname FROM pg_views
WHERE schemaname = 'public'
AND viewname LIKE 'telegram_%'
ORDER BY viewname;
```

Expected: 4 views
- telegram_bot_events_recent
- telegram_subscription_stats
- telegram_user_search_criteria_stats
- telegram_user_subscriptions_active

---

## 📊 STEP 3: Migrate Existing Data (If Applicable)

**Only do this if you have existing chat_id data to migrate**

### 3.1 Create Telegram Users from Existing Chat IDs

In SQL Editor, run:

```sql
-- Step 1: Create Telegram users from existing chat_ids
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
```

**Verify:**
```sql
SELECT COUNT(*) as user_count FROM telegram_users;
```

### 3.2 Copy Subscriptions

```sql
-- Step 2: Copy subscriptions
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
```

**Verify:**
```sql
SELECT COUNT(*) as subscription_count FROM telegram_user_subscriptions;
```

### 3.3 Copy Seen Listings

```sql
-- Step 3: Copy seen listings
INSERT INTO telegram_user_seen_listings (telegram_user_id, listing_id, seen_at, chat_id)
SELECT
    tu.id,
    old.listing_id,
    old.seen_at,
    old.chat_id
FROM user_seen_listings_old old
JOIN telegram_users tu ON tu.telegram_chat_id = old.chat_id
WHERE old.chat_id IS NOT NULL;
```

### 3.4 Copy Bot Events

```sql
-- Step 4: Copy bot events
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
```

---

## 🐍 STEP 4: Update Python Code

### 4.1 Update Telegram Bot Database Module

Update `telegram_bot_main.py`:

```python
# OLD
from telegram_bot_database_supabase import TelegramBotDatabaseSupabase

# NEW
from telegram_bot_database_multiuser import TelegramBotDatabaseMultiUser
```

### 4.2 Update Bot Database Initialization

```python
# OLD
bot_db = TelegramBotDatabaseSupabase()

# NEW
bot_db = TelegramBotDatabaseMultiUser()
```

### 4.3 Update Table Name References

**Replace all references to old table names:**

| Old Name | New Name |
|----------|----------|
| `users` | `telegram_users` |
| `user_subscriptions` | `telegram_user_subscriptions` |
| `user_seen_listings` | `telegram_user_seen_listings` |
| `bot_events` | `telegram_bot_events` |

Example updates:

```python
# OLD
response = db.get(f"/user_subscriptions?chat_id=eq.{chat_id}")

# NEW
response = db.get(f"/telegram_user_subscriptions?telegram_user_id=eq.{user_id}")
```

### 4.4 Add Search Criteria Support (Optional)

```python
from search_criteria_management import SearchCriteriaManager

criteria_mgr = SearchCriteriaManager()

# Allow users to create custom search criteria
# /criteria command → create custom filters
# Replace hardcoded config.json approach
```

---

## 🧪 STEP 5: Test the Deployment

### 5.1 Test User Registration

```python
from database_rest_api import DatabaseManager
from telegram_bot_database_multiuser import TelegramBotDatabaseMultiUser

db = DatabaseManager()
bot_db = TelegramBotDatabaseMultiUser()

# Test: Get or create user
chat_id = 123456789  # Your Telegram chat ID

# Insert test user
response = db._make_request(
    'POST',
    f"{db.base_url}/telegram_users",
    json={
        "telegram_chat_id": chat_id,
        "first_name": "Test",
        "last_name": "User"
    },
    headers=db.headers,
    timeout=10
)

if response.status_code in [200, 201]:
    user = response.json() if isinstance(response.json(), dict) else response.json()[0]
    user_id = user.get("id")
    print(f"✓ User created: {user_id}")
else:
    print(f"✗ Failed: {response.status_code}")
```

### 5.2 Test Subscription

```python
# Test: Add subscription
success, error = bot_db.add_subscription(
    user_id=user_id,
    search_url="https://www.myauto.ge/ka/s/cars?...",
    search_name="Test Search"
)

if success:
    print("✓ Subscription added")
else:
    print(f"✗ Failed: {error}")
```

### 5.3 Test Deduplication

```python
# Test: Record seen listing
bot_db.record_user_seen_listing(user_id, "listing_123")
print("✓ Listing marked as seen")

# Test: Check if seen
is_seen = bot_db.has_user_seen_listing(user_id, "listing_123")
print(f"✓ Is seen: {is_seen}")

# Should be True
assert is_seen == True
print("✓ Deduplication working correctly")
```

### 5.4 Test Event Logging

```python
# Test: Log event
bot_db.log_event(
    user_id=user_id,
    event_type="deployment_test",
    event_data={"test": "data"}
)
print("✓ Event logged")
```

---

## 📈 STEP 6: Verify Views & Statistics

### 6.1 Check User Statistics

```sql
SELECT * FROM telegram_subscription_stats;
```

Expected output:
- total_active_users: 1 (or your count)
- total_active_subscriptions: 1 (or your count)
- avg_subscriptions_per_user: 1.00

### 6.2 Check User Subscriptions

```sql
SELECT * FROM telegram_user_subscriptions_active;
```

### 6.3 Check Recent Events

```sql
SELECT * FROM telegram_bot_events_recent;
```

---

## 🚀 STEP 7: Deploy Updated Bot Code

### 7.1 Update GitHub Actions Workflow (if applicable)

If using GitHub Actions, ensure:
- `SUPABASE_URL` environment variable is set
- `SUPABASE_API_KEY` environment variable is set
- Bot code references new table names

### 7.2 Deploy to Production

```bash
# Commit changes
git add telegram_bot_main.py telegram_bot_scheduler.py telegram_bot_backend.py

git commit -m "feat: Migrate to Telegram multi-user system with individual search criteria"

# Push to production
git push origin main
```

### 7.3 Monitor Deployment

- Check bot is running
- Check logs for errors
- Test `/set` command in Telegram
- Test `/list` command
- Verify notifications are working

---

## 🔧 STEP 8: Optional - Cleanup Old Tables

**Only after verifying data migration was successful:**

```sql
-- Drop old tables (AFTER verification)
DROP TABLE IF EXISTS user_subscriptions_old;
DROP TABLE IF EXISTS user_seen_listings_old;
DROP TABLE IF EXISTS bot_events_old;
```

---

## 📋 Post-Deployment Checklist

- [ ] SQL migration executed successfully
- [ ] All 6 Telegram tables created
- [ ] 4 views working correctly
- [ ] 3 cleanup functions active
- [ ] Data migrated from old tables (if applicable)
- [ ] Python code updated with new table names
- [ ] Test user created and verified
- [ ] Test subscription added
- [ ] Deduplication tested
- [ ] Event logging tested
- [ ] Statistics views return correct data
- [ ] Bot code deployed to production
- [ ] Bot running without errors
- [ ] Commands tested in Telegram
- [ ] Old tables cleaned up (optional)

---

## 🚨 Troubleshooting

### Error: "Table already exists"
**Solution:** Tables already created. Check if migration ran twice. Safe to proceed.

### Error: "Foreign key constraint failed"
**Solution:** Ensure `telegram_users` table was populated before migrating data.

### Error: "telegram_user_id is NULL"
**Solution:** User ID missing. Verify user was created in `telegram_users` table.

### Bot not starting
**Solution:**
1. Check imports: `from telegram_bot_database_multiuser import ...`
2. Check table names updated in code
3. Check SUPABASE_URL and API_KEY in .env

### No data in views
**Solution:** Verify data was migrated using:
```sql
SELECT COUNT(*) FROM telegram_users;
SELECT COUNT(*) FROM telegram_user_subscriptions;
```

---

## 📞 Quick Reference

### New Tables
```
telegram_users                    # User management
telegram_user_subscriptions       # User's searches to monitor
telegram_user_seen_listings       # Deduplication per user
telegram_bot_events               # Event logging
telegram_user_search_criteria     # Custom search filters
telegram_user_api_tokens          # API access (optional)
```

### New Views
```
telegram_user_subscriptions_active     # Active subs per user
telegram_subscription_stats            # System statistics
telegram_bot_events_recent             # Last 7 days events
telegram_user_search_criteria_stats    # Criteria statistics
```

### Migration Time
- SQL execution: 10-30 seconds
- Data migration: 1-5 minutes (depending on data size)
- Code update: 15-30 minutes
- Testing: 10-15 minutes
- **Total: ~1 hour**

---

## ✅ You Are Ready to Deploy!

All systems are prepared and tested. Follow the steps above in order and you'll have a fully functional Telegram multi-user system with:

✅ Individual user management
✅ Per-user search criteria
✅ User-specific subscriptions
✅ Complete data isolation
✅ Deduplication per user
✅ Event logging

**Status: PRODUCTION READY** 🎉

---

**Generated:** 2024-2025
**Version:** 1.0 - Telegram Multi-User System
