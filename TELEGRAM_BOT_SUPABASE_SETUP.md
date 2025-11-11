# Telegram Bot - Supabase Database Setup

## Overview

The Telegram bot now uses **your existing Supabase database** instead of a separate SQLite file. This means:

✅ All data in one place (main monitoring + bot data)
✅ No separate databases to manage
✅ Better integration and data consistency
✅ Easier to query across both systems
✅ Cloud-based backup (via Supabase)

## Step 1: Create Tables in Supabase

### Option A: Using SQL Editor (Recommended)

1. **Open Supabase Dashboard**
   - Go to: https://app.supabase.com
   - Select your project

2. **Navigate to SQL Editor**
   - Click "SQL Editor" in left sidebar
   - Click "New query"

3. **Copy & Paste SQL**
   - Open file: `supabase_schema_telegram_bot.sql`
   - Copy all content
   - Paste into Supabase SQL Editor

4. **Execute**
   - Click "Run" button (or Cmd+Enter)
   - Wait for "Success" message

5. **Verify**
   - Should see 3 new tables:
     - `user_subscriptions`
     - `user_seen_listings`
     - `bot_events`

### Option B: Manual Table Creation

If you prefer, create each table individually:

**Table 1: user_subscriptions**
```sql
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id BIGSERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    search_url TEXT NOT NULL,
    search_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_checked TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(chat_id, search_url)
);

CREATE INDEX idx_user_subscriptions_chat_id ON user_subscriptions(chat_id);
CREATE INDEX idx_user_subscriptions_is_active ON user_subscriptions(is_active);
```

**Table 2: user_seen_listings**
```sql
CREATE TABLE IF NOT EXISTS user_seen_listings (
    id BIGSERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    listing_id TEXT NOT NULL,
    seen_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(chat_id, listing_id)
);

CREATE INDEX idx_user_seen_listings_chat_id ON user_seen_listings(chat_id);
```

**Table 3: bot_events**
```sql
CREATE TABLE IF NOT EXISTS bot_events (
    id BIGSERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    event_type TEXT NOT NULL,
    event_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_bot_events_chat_id ON bot_events(chat_id);
```

## Step 2: Verify Tables Exist

### In Supabase UI

1. Go to "Table Editor" in left sidebar
2. Look for these 3 new tables:
   - ✅ `user_subscriptions`
   - ✅ `user_seen_listings`
   - ✅ `bot_events`

### Via SQL Query

Run this in SQL Editor to verify:
```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('user_subscriptions', 'user_seen_listings', 'bot_events')
ORDER BY table_name;
```

Expected output:
```
user_events
user_seen_listings
user_subscriptions
```

## Step 3: Update Bot Configuration

Your `.env.local` should already have Supabase credentials:

```bash
# Existing Supabase config (should already be there)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_API_KEY=your-api-key-here

# Bot config (add if not present)
TELEGRAM_BOT_TOKEN=your-bot-token
BOT_CHECK_INTERVAL_MINUTES=15
BOT_ENABLED=true
```

## Step 4: Update Bot to Use Supabase

Choose which database module to use:

### Option A: Use Supabase (Recommended)

Update `telegram_bot_main.py` line where database is imported:

**Change from:**
```python
from telegram_bot_database import TelegramBotDatabase
db = TelegramBotDatabase()  # SQLite
```

**Change to:**
```python
from telegram_bot_database_supabase import TelegramBotDatabaseSupabase
db = TelegramBotDatabaseSupabase()  # Supabase
```

### Option B: Keep SQLite

Keep using the original `telegram_bot_database.py` (local file-based).

## Recommended: Use Supabase Version

We recommend using `telegram_bot_database_supabase.py` because:

✅ **Unified Database** - All data in Supabase
✅ **Better Integration** - Can query across main system + bot data
✅ **Cloud Backup** - Automatic backups via Supabase
✅ **Scalability** - PostgreSQL scales better than SQLite
✅ **Shared Access** - Main app and bot can access same data
✅ **Advanced Features** - Full PostgreSQL capabilities

## Database Schema Overview

### user_subscriptions
```
id (PK)          - Auto-incrementing ID
chat_id          - Telegram user's chat ID
search_url       - MyAuto.ge URL to monitor
search_name      - Optional friendly name
created_at       - When subscription was added
last_checked     - Last time this URL was checked
is_active        - Soft delete flag (false = deleted)
```

### user_seen_listings
```
id (PK)          - Auto-incrementing ID
chat_id          - Telegram user's chat ID
listing_id       - MyAuto listing ID
seen_at          - When user last saw this listing
```

### bot_events
```
id (PK)          - Auto-incrementing ID
chat_id          - Telegram user's chat ID
event_type       - Event type (e.g., "subscription_added")
event_data       - Additional data as JSON
created_at       - When event occurred
```

## Data Size Estimates

With typical usage:

| Table | Data per User | For 100 Users |
|-------|---|---|
| user_subscriptions | ~100 bytes/subscription | ~50 KB |
| user_seen_listings | ~50 bytes/listing | ~5-50 MB |
| bot_events | ~200 bytes/event | ~2-5 MB |
| **Total** | | **~7-55 MB** |

Supabase free tier includes 500 MB database, so plenty of room.

## Coexistence with Main System

Both systems use the **same Supabase database**:

```
Main System (main.py)
├─ Tables:
│  ├─ seen_listings (main system tracking)
│  ├─ vehicle_details (main system data)
│  ├─ search_configurations (predefined searches)
│  └─ notifications_sent (notification history)
│
Bot System (telegram_bot_main.py)
├─ Tables:
│  ├─ user_subscriptions (bot: user searches)
│  ├─ user_seen_listings (bot: deduplication)
│  └─ bot_events (bot: logging)
│
Both share:
└─ Supabase REST API access
```

## Querying Bot Data

### View all user subscriptions

```sql
SELECT chat_id, search_url, created_at, last_checked
FROM user_subscriptions
WHERE is_active = TRUE
ORDER BY chat_id, created_at;
```

### Check seen listings for specific user

```sql
SELECT chat_id, COUNT(*) as seen_count
FROM user_seen_listings
GROUP BY chat_id
ORDER BY chat_id;
```

### Bot events

```sql
SELECT chat_id, event_type, event_data, created_at
FROM bot_events
ORDER BY created_at DESC
LIMIT 50;
```

## Maintenance Tasks

### Automatic Cleanup (Optional)

The bot automatically:
- Removes seen listings older than 30 days
- Marks subscriptions inactive if not checked for 90 days

### Manual Cleanup (Optional)

If you want to clean up manually via Supabase:

```sql
-- Remove seen listings older than 30 days
DELETE FROM user_seen_listings
WHERE seen_at < NOW() - INTERVAL '30 days';

-- Mark subscriptions inactive if not checked for 90 days
UPDATE user_subscriptions
SET is_active = FALSE
WHERE is_active = TRUE
AND last_checked IS NOT NULL
AND last_checked < NOW() - INTERVAL '90 days';
```

## Row Level Security (Optional)

For extra security, you can enable RLS:

```sql
ALTER TABLE user_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_seen_listings ENABLE ROW LEVEL SECURITY;
ALTER TABLE bot_events ENABLE ROW LEVEL SECURITY;
```

Then create policies to restrict access (optional).

## Monitoring Bot Activity

### Quick Statistics

```sql
-- Active users and subscriptions
SELECT
    COUNT(DISTINCT chat_id) as total_users,
    COUNT(*) as total_subscriptions,
    MAX(last_checked) as most_recent_check
FROM user_subscriptions
WHERE is_active = TRUE;
```

### Recent Events

```sql
-- Recent bot activity (last 24 hours)
SELECT chat_id, event_type, COUNT(*) as count
FROM bot_events
WHERE created_at > NOW() - INTERVAL '1 day'
GROUP BY chat_id, event_type
ORDER BY chat_id, count DESC;
```

### Unused Subscriptions

```sql
-- Subscriptions never checked
SELECT chat_id, search_url, created_at
FROM user_subscriptions
WHERE is_active = TRUE
AND last_checked IS NULL
ORDER BY created_at;
```

## Troubleshooting

### Tables don't appear

1. Check SQL ran without errors in SQL Editor
2. Go to "Table Editor" and refresh
3. Make sure you're in correct Supabase project
4. Check `SUPABASE_URL` in .env.local

### Permission denied errors

1. Ensure API key is correct in .env.local
2. Check API key has database access
3. In Supabase → Settings → API, verify key has correct permissions

### Data not appearing

1. Ensure bot is running: `python telegram_bot_main.py`
2. Send a command like `/set <url>` to bot
3. Check Supabase "Table Editor" for `user_subscriptions`
4. Look at `bot_events` table for any errors

### Slow queries

1. Check indexes exist (automatically created by SQL script)
2. Limit queries with WHERE conditions
3. Use Supabase Query Performance analyzer

## Migration from SQLite to Supabase

If you were using SQLite before:

1. Export data from `telegram_bot.db` (optional)
2. Create tables in Supabase (this guide)
3. Update `telegram_bot_main.py` to use Supabase version
4. Restart bot
5. You can delete old `telegram_bot.db` file

## Performance Characteristics

| Metric | SQLite | Supabase |
|--------|--------|----------|
| Query speed | Fast (local) | Fast (optimized) |
| Concurrent users | Limited | 1000+ |
| Automatic backup | No | Yes (daily) |
| Data limit | Filesystem | 500 MB (free tier) |
| Scaling | Manual | Automatic |
| Access from multiple apps | Hard | Easy (REST API) |

## Free Tier Limits

Supabase free tier includes:

- ✅ 500 MB database
- ✅ 2 GB bandwidth/month
- ✅ 50,000 monthly active users
- ✅ Automatic daily backups
- ✅ Community support

More than enough for telegram bot!

## Next Steps

1. ✅ Create tables using `supabase_schema_telegram_bot.sql`
2. ✅ Verify tables in Supabase UI
3. ✅ Update bot to use `telegram_bot_database_supabase.py`
4. ✅ Restart bot: `python telegram_bot_main.py`
5. ✅ Test with `/help` command

## Summary

- **Database**: Shared Supabase instance
- **Tables**: 3 new tables (user_subscriptions, user_seen_listings, bot_events)
- **Setup Time**: ~5 minutes
- **Maintenance**: Automatic cleanup built-in
- **Benefits**: Unified data, better scalability, cloud backup

Both your main monitoring system and telegram bot now share the same database!
