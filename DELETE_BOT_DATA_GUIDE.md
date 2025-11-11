# 🗑️ Delete Telegram Bot Data - Complete Guide

Delete or reset bot data in Supabase database.

---

## ⚠️ Before You Start

**BACKUP YOUR DATA!**
- This operation **cannot be undone**
- Always test in non-production first
- Keep a backup of important data

---

## 📍 Where to Run SQL

1. Go to **Supabase Dashboard:** https://supabase.com/dashboard
2. Select your **project**
3. Click **SQL Editor** (left sidebar)
4. Click **New Query**
5. Copy & paste the SQL script
6. Click **Run** (blue button)

---

## 🎯 Quick Use Cases

### Use Case 1: Clear All Seen Listings (Most Common)

**What it does:** Bot will re-notify about listings it already notified about

**When to use:**
- You want fresh notifications
- Testing the bot
- Starting over

**SQL:**
```sql
DELETE FROM user_seen_listings;
```

---

### Use Case 2: Clear Data for One User

**What it does:** Remove all tracking for a specific Telegram chat

**When to use:**
- User wants to start over
- Debugging one user
- Remove a user's data

**SQL:**
```sql
DELETE FROM user_seen_listings
WHERE chat_id = 6366712840;
```

Replace `6366712840` with actual chat ID.

---

### Use Case 3: Delete All Subscriptions

**What it does:** Mark all searches as inactive

**When to use:**
- Reset all user searches
- Stop all monitoring
- Clean up

**SQL:**
```sql
UPDATE user_subscriptions
SET is_active = false;
```

---

### Use Case 4: Complete Reset (Delete Everything)

**What it does:** Remove all bot data

**When to use:**
- Starting completely fresh
- Production cleanup

**SQL:**
```sql
DELETE FROM user_seen_listings;
DELETE FROM bot_events;
DELETE FROM user_subscriptions;
```

---

## 📋 Table Reference

### `user_subscriptions` Table
- Stores saved searches
- Columns: `id`, `chat_id`, `search_url`, `is_active`, `created_at`, `last_checked`
- Delete = removes searches

### `user_seen_listings` Table
- Tracks which listings user has seen
- Columns: `id`, `chat_id`, `listing_id`, `seen_at`
- Delete = bot treats all listings as new

### `bot_events` Table
- Event log/history
- Columns: `id`, `chat_id`, `event_type`, `event_data`, `created_at`
- Delete = removes history

---

## 🔍 View Data Before Deleting

**See all subscriptions:**
```sql
SELECT * FROM user_subscriptions;
```

**Count listings seen by user:**
```sql
SELECT chat_id, COUNT(*) as "Listings seen"
FROM user_seen_listings
GROUP BY chat_id;
```

**See recent events:**
```sql
SELECT * FROM bot_events
ORDER BY created_at DESC
LIMIT 20;
```

---

## 🛡️ Safe Deletion Steps

### Step 1: View the Data
```sql
SELECT COUNT(*) FROM user_seen_listings;
```

### Step 2: Run the DELETE
```sql
DELETE FROM user_seen_listings;
```

### Step 3: Verify
```sql
SELECT COUNT(*) FROM user_seen_listings;
```

Should return `0` if successful.

---

## 🔄 Transactional Delete (Safest)

If you're not sure, use a **transaction**:

```sql
BEGIN;

-- Your delete statement here
DELETE FROM user_seen_listings;

-- If happy with result: COMMIT;
-- If want to undo: ROLLBACK;

COMMIT;
```

---

## 🚨 Common Mistakes

### ❌ Mistake 1: DELETE without WHERE clause
```sql
DELETE FROM user_subscriptions;  -- Deletes EVERYTHING!
```

✅ Better:
```sql
DELETE FROM user_subscriptions
WHERE is_active = false;  -- Only old subscriptions
```

### ❌ Mistake 2: Forgetting to specify which chat
```sql
DELETE FROM user_seen_listings;  -- Deletes ALL users' listings!
```

✅ Better:
```sql
DELETE FROM user_seen_listings
WHERE chat_id = 6366712840;  -- Only this user
```

---

## ✅ After Deletion

### Test the Bot

1. **Send `/list`** - Verify no searches show up (if you deleted subscriptions)
2. **Send `/run 1`** - Should say no searches exist
3. **Send `/set <url>`** - Add a new search
4. **Send `/run 1`** - Should show listings (possibly old ones now marked as new)

---

## 📊 Data Sizes to Delete

Check before deleting:

```sql
-- See how much data you're deleting

SELECT
  (SELECT COUNT(*) FROM user_subscriptions) as subscriptions,
  (SELECT COUNT(*) FROM user_seen_listings) as seen_listings,
  (SELECT COUNT(*) FROM bot_events) as events;
```

Example output:
```
subscriptions: 5
seen_listings: 2,341
events: 15,670
```

---

## 🔧 Restore from Backup

If you deleted by accident:

1. **Check Supabase backups** (Settings → Backups)
2. **Contact Supabase support** for recovery (within retention period)
3. **Use your own backup** if you have one

---

## 📋 Recipes

### Reset Bot Completely
```sql
-- Delete all data
DELETE FROM user_seen_listings;
DELETE FROM bot_events;
UPDATE user_subscriptions SET is_active = false;

-- Or completely remove subscriptions:
DELETE FROM user_subscriptions;
```

### Clear Old Data (30+ days)
```sql
DELETE FROM user_seen_listings
WHERE seen_at < NOW() - INTERVAL '30 days';

DELETE FROM bot_events
WHERE created_at < NOW() - INTERVAL '30 days';
```

### Reset Last Checked Time
```sql
UPDATE user_subscriptions
SET last_checked = NULL
WHERE is_active = true;
```

Then bot will check immediately on next cycle.

### Deactivate All Searches
```sql
UPDATE user_subscriptions
SET is_active = false;
```

Bot won't check these until reactivated.

---

## 🆘 Troubleshooting

### "No rows affected"
- Data might already be deleted
- Check with: `SELECT COUNT(*) FROM table_name;`

### "Permission denied"
- Your Supabase role doesn't have delete permission
- Contact project admin

### "Syntax error"
- Copy the exact SQL from `sql_delete_bot_data.sql`
- Check for typos

---

## 📞 Need Help?

Share:
1. Which table you're deleting from
2. How many rows are in it
3. What you're trying to accomplish

---

## ✨ Summary

| Task | SQL |
|------|-----|
| Clear all seen listings | `DELETE FROM user_seen_listings;` |
| Clear user's listings | `DELETE FROM user_seen_listings WHERE chat_id = XXX;` |
| Deactivate all searches | `UPDATE user_subscriptions SET is_active = false;` |
| Delete all data | `DELETE FROM user_seen_listings; DELETE FROM bot_events; DELETE FROM user_subscriptions;` |
| View subscriptions | `SELECT * FROM user_subscriptions;` |
| Count seen listings | `SELECT COUNT(*) FROM user_seen_listings;` |

---

**That's it!** You now have full control over your bot data. 🎉
