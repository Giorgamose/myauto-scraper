# SQL Files Guide - Telegram Bot Database Setup

## Overview

Four SQL files are available for creating the Telegram bot tables in Supabase. Choose whichever suits your workflow.

## Available SQL Files

### Option 1: Combined (All 3 Tables in One File) ⭐ RECOMMENDED

**File:** `supabase_schema_telegram_bot.sql`

**Use when:** You want to create everything at once

**What it includes:**
- ✅ All 3 tables
- ✅ All indexes
- ✅ Optional views
- ✅ Optional cleanup functions
- ✅ Comments and instructions

**How to use:**
1. Open Supabase SQL Editor
2. Copy entire file content
3. Paste into SQL Editor
4. Click "Run"
5. All tables created instantly

**Advantages:**
- Simple, one-click setup
- All indexes created
- Comments explain everything
- Optional views included

**Disadvantages:**
- Large file
- All-or-nothing approach

---

### Option 2: Individual Files (Separate Table Creation)

Create each table independently if you prefer more control.

#### File 2A: `sql_create_user_subscriptions.sql`

**Purpose:** Create the `user_subscriptions` table

**Contains:**
- Table definition
- 3 indexes
- Verification query

**Creates table:**
```
user_subscriptions
├─ id (PK)
├─ chat_id
├─ search_url
├─ search_name
├─ created_at
├─ last_checked
└─ is_active
```

**Run 1st** if using individual files.

---

#### File 2B: `sql_create_user_seen_listings.sql`

**Purpose:** Create the `user_seen_listings` table

**Contains:**
- Table definition
- 3 indexes
- Verification query

**Creates table:**
```
user_seen_listings
├─ id (PK)
├─ chat_id
├─ listing_id
└─ seen_at
```

**Run 2nd** if using individual files.

---

#### File 2C: `sql_create_bot_events.sql`

**Purpose:** Create the `bot_events` table

**Contains:**
- Table definition
- 3 indexes
- Verification query

**Creates table:**
```
bot_events
├─ id (PK)
├─ chat_id
├─ event_type
├─ event_data
└─ created_at
```

**Run 3rd** if using individual files.

---

## Comparison

| Aspect | Combined File | Individual Files |
|--------|---|---|
| Setup time | 5 minutes | 5-10 minutes |
| Number of queries | 1 | 3+ |
| Ease | Very easy | Easy |
| Control | Low | High |
| Error recovery | All or nothing | Can skip failed table |
| Comments | Extensive | Basic |
| Views included | Yes | No |
| Functions included | Yes | No |

---

## Step-by-Step Setup

### Option 1: Using Combined File (Easiest)

1. **Open Supabase Dashboard**
   - Go to https://app.supabase.com
   - Select your project

2. **Go to SQL Editor**
   - Click "SQL Editor" in sidebar
   - Click "New query"

3. **Open SQL File**
   - Open: `supabase_schema_telegram_bot.sql`

4. **Copy Content**
   - Select all (Ctrl+A)
   - Copy (Ctrl+C)

5. **Paste in Supabase**
   - Click in SQL Editor
   - Paste (Ctrl+V)

6. **Execute**
   - Click "Run" button
   - Wait for success message

7. **Verify**
   - Go to "Table Editor"
   - Should see 3 tables:
     - ✅ user_subscriptions
     - ✅ user_seen_listings
     - ✅ bot_events

### Option 2: Using Individual Files

Follow the same steps 1-5 above, but:
- **Step 3:** Open `sql_create_user_subscriptions.sql` (run first)
- **Repeat steps 4-6** with `sql_create_user_seen_listings.sql` (run second)
- **Repeat steps 4-6** with `sql_create_bot_events.sql` (run third)

Then verify in Step 7.

---

## Quick Copy-Paste Commands

### All Three Tables at Once

If you prefer copy-paste without files:

```sql
-- 1. USER SUBSCRIPTIONS TABLE
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

CREATE INDEX IF NOT EXISTS idx_user_subscriptions_chat_id ON user_subscriptions(chat_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_is_active ON user_subscriptions(is_active);

-- 2. USER SEEN LISTINGS TABLE
CREATE TABLE IF NOT EXISTS user_seen_listings (
    id BIGSERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    listing_id TEXT NOT NULL,
    seen_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(chat_id, listing_id)
);

CREATE INDEX IF NOT EXISTS idx_user_seen_listings_chat_id ON user_seen_listings(chat_id);

-- 3. BOT EVENTS TABLE
CREATE TABLE IF NOT EXISTS bot_events (
    id BIGSERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    event_type TEXT NOT NULL,
    event_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_bot_events_chat_id ON bot_events(chat_id);
```

---

## Troubleshooting

### Table Already Exists

**Error:** `Error: relation "user_subscriptions" already exists`

**Solution:**
- Table already created ✓
- Continue with next table or bot

### Permission Denied

**Error:** `ERROR: Permission denied for schema public`

**Solution:**
1. Check API key in `.env.local`
2. Verify key has database access
3. In Supabase Settings → API → Check key permissions

### Syntax Error

**Error:** `Syntax error at position XXX`

**Solution:**
1. Check you copied the entire file
2. No missing quotes or parentheses
3. Try running file-by-file instead of combined

### Table Exists, Different Schema

**Error:** Table created but can't access via Python

**Solution:**
- Verify table is in `public` schema
- In Supabase Table Editor, check table visibility

---

## Verification Queries

After creating tables, run these to verify:

### Check All Tables Exist
```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('user_subscriptions', 'user_seen_listings', 'bot_events')
ORDER BY table_name;
```

Expected output:
```
bot_events
user_seen_listings
user_subscriptions
```

### Check Indexes
```sql
SELECT indexname, tablename
FROM pg_indexes
WHERE tablename IN ('user_subscriptions', 'user_seen_listings', 'bot_events')
ORDER BY tablename;
```

Expected output:
```
idx_bot_events_chat_id          | bot_events
idx_user_seen_listings_chat_id  | user_seen_listings
idx_user_subscriptions_chat_id  | user_subscriptions
idx_user_subscriptions_is_active| user_subscriptions
```

### Test Inserts
```sql
-- Test insert in user_subscriptions
INSERT INTO user_subscriptions (chat_id, search_url)
VALUES (123456, 'https://www.myauto.ge/ka/search?test=1');

-- Check it was inserted
SELECT * FROM user_subscriptions WHERE chat_id = 123456;

-- Delete test data
DELETE FROM user_subscriptions WHERE chat_id = 123456;
```

---

## Files Summary

| File | Size | Tables | Indexes | Functions |
|------|------|--------|---------|-----------|
| `supabase_schema_telegram_bot.sql` | Large | 3 | Yes | Yes |
| `sql_create_user_subscriptions.sql` | Small | 1 | Yes | No |
| `sql_create_user_seen_listings.sql` | Small | 1 | Yes | No |
| `sql_create_bot_events.sql` | Small | 1 | Yes | No |

---

## Recommendation

**For most users:** Use `supabase_schema_telegram_bot.sql` (combined file)

**For advanced users:** Use individual files for more control

Both approaches work equally well.

---

## Next Steps

1. ✅ Choose which SQL file to use
2. ✅ Copy content
3. ✅ Paste in Supabase SQL Editor
4. ✅ Click Run
5. ✅ Verify tables created
6. ✅ Start telegram bot: `python telegram_bot_main.py`

---

## Support

If tables don't create:
1. Check error message
2. Try individual files instead
3. Verify API key permissions
4. Check Supabase status page

If bot can't access tables:
1. Verify `SUPABASE_URL` in .env.local
2. Verify `SUPABASE_API_KEY` in .env.local
3. Run verification query above
4. Check table is in `public` schema
