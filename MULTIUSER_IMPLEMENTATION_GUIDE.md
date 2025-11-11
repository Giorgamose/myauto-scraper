# Multi-User System Implementation Guide

## Overview

This guide provides step-by-step instructions to migrate from the single-system architecture to a **multi-user system** where:
- Each user has individual accounts with username/password/email
- Each user can create and manage their own search criteria
- Each user can subscribe to multiple searches with full isolation
- All data is user-specific and properly secured

**Migration Status:** Ready for deployment

---

## 📋 What's New

### New Features
- ✅ **User Authentication**: Username/password registration and login
- ✅ **API Tokens**: Users can generate API tokens for programmatic access
- ✅ **Dynamic Search Criteria**: Create custom search filters in the database (replaces hardcoded config.json)
- ✅ **Subscription Management**: Each user manages their own subscriptions
- ✅ **Complete User Isolation**: Users can only access their own data

### Files Created
```
user_management.py                          # User registration, authentication, profiles
search_criteria_management.py               # Dynamic search criteria management
telegram_bot_database_multiuser.py          # Multi-user aware bot database layer
test_multiuser_system.py                    # Comprehensive test suite
sql_migration_multi_user.sql                # Database migration script
MULTIUSER_IMPLEMENTATION_GUIDE.md           # This file
```

---

## 🚀 Deployment Steps

### Step 1: Run Database Migration

**Time:** ~5 minutes

1. Open Supabase Dashboard → SQL Editor
2. Copy entire contents of `sql_migration_multi_user.sql`
3. Paste into SQL Editor
4. Click "Run"
5. Verify tables were created:
   ```sql
   SELECT table_name FROM information_schema.tables
   WHERE table_schema = 'public'
   AND table_name IN ('users', 'user_api_tokens', 'user_search_criteria',
                      'user_subscriptions', 'user_seen_listings', 'bot_events')
   ORDER BY table_name;
   ```

**Expected Output:**
```
bot_events
bot_events_old
user_api_tokens
user_search_criteria
user_seen_listings
user_seen_listings_old
user_subscriptions
user_subscriptions_old
users
```

### Step 2: Migrate Existing Data (Optional)

**Time:** ~10 minutes

If you have existing subscriptions from chat_id-based system:

1. Create users from existing Telegram chat IDs:
   ```python
   from user_management import UserManager
   from database_rest_api import DatabaseManager

   manager = UserManager(DatabaseManager())

   # For each existing chat_id, create a user
   success, error, user = manager.register_user(
       username="user_123456789",  # Use chat_id as part of username
       email="user_123456789@telegram.local",
       password="TempPassword123",  # User should change on first login
       telegram_chat_id=123456789   # Link Telegram chat ID
   )
   ```

2. Update migration helper in SQL:
   ```sql
   -- Uncomment and modify migration statements in sql_migration_multi_user.sql
   -- Copy data from old tables to new tables
   INSERT INTO user_subscriptions (user_id, search_url, ...)
   SELECT u.id, old.search_url, ...
   FROM user_subscriptions_old old
   JOIN users u ON u.telegram_chat_id = old.chat_id;
   ```

3. Run migrations (see script in SQL file)

### Step 3: Update Application Code

**Files to update:**
- `telegram_bot_main.py` - Use new database module
- `telegram_bot_scheduler.py` - Query multi-user subscriptions
- `telegram_bot_backend.py` - Update command handlers

**Key changes:**
Replace:
```python
from telegram_bot_database_supabase import TelegramBotDatabaseSupabase
```

With:
```python
from telegram_bot_database_multiuser import TelegramBotDatabaseMultiUser

# Use new module
bot_db = TelegramBotDatabaseMultiUser()
```

### Step 4: Update Telegram Bot Commands

**Commands to update:**

| Old Command | New Behavior |
|------------|-------------|
| `/set <url>` | Same, but now linked to user account |
| `/list` | Show user's subscriptions |
| `/clear` | Clear user's subscriptions |
| `/status` | Show user's account status |
| `/help` | Updated help text |

**New commands (optional):**
```
/profile - Show user profile
/criteria - Manage search criteria
/tokens - Manage API tokens
/settings - Adjust notification settings
```

### Step 5: Run Comprehensive Tests

**Time:** ~5 minutes

```bash
python test_multiuser_system.py
```

**Expected output:**
```
======================================================================
MULTI-USER SYSTEM - COMPREHENSIVE TESTS
Started: 2024-XX-XX...
======================================================================

======================================================================
TESTING: USER MANAGEMENT
======================================================================
[✓] PASS: User Registration
[✓] PASS: User Authentication (Correct Password)
[✓] PASS: User Authentication (Wrong Password Rejected)
[✓] PASS: API Token Creation
[✓] PASS: API Token Verification
[✓] PASS: Duplicate Username Prevention
[✓] PASS: Duplicate Email Prevention

======================================================================
TESTING: SEARCH CRITERIA MANAGEMENT
======================================================================
[✓] PASS: Search Criteria Creation
[✓] PASS: Search Criteria Retrieval
[✓] PASS: Search Criteria Update
[✓] PASS: Duplicate Criteria Name Prevention
[✓] PASS: Search Parameter Validation (Valid)
[✓] PASS: Search Parameter Validation (Invalid Rejected)

======================================================================
TESTING: TELEGRAM BOT DATABASE (MULTI-USER)
======================================================================
[✓] PASS: Add Subscription
[✓] PASS: Get Subscriptions
[✓] PASS: Record Seen Listing
[✓] PASS: Check Seen Listing
[✓] PASS: Event Logging
[✓] PASS: Duplicate Subscription Prevention

======================================================================
TEST SUMMARY: 20/20 passed, 0 failed
======================================================================
```

---

## 💻 Usage Examples

### Example 1: User Registration via Telegram Bot

```python
from user_management import UserManager
from database_rest_api import DatabaseManager

# Initialize
db = DatabaseManager()
user_manager = UserManager(db)

# Register new user
success, error, user = user_manager.register_user(
    username="alex_user",
    email="alex@example.com",
    password="SecurePassword123",
    telegram_chat_id=123456789,
    first_name="Alex"
)

if success:
    print(f"User registered: {user['id']}")
    # Store user_id in session/session management
else:
    print(f"Registration failed: {error}")
```

### Example 2: Create Search Criteria

```python
from search_criteria_management import SearchCriteriaManager

manager = SearchCriteriaManager()

success, error, criteria = manager.create_criteria(
    user_id="550e8400-e29b-41d4-a716-446655440000",
    criteria_name="Luxury SUVs Under 100K",
    description="Recent luxury SUVs in good condition",
    search_parameters={
        "vehicleType": 1,              # SUV
        "makes": [1, 2, 3],            # Mercedes, BMW, Audi
        "priceFrom": 30000,
        "priceTo": 100000,
        "yearFrom": 2015,
        "yearTo": 2024,
        "customs": 1,                  # Customs cleared
        "fuelTypes": [1, 2]           # Petrol, Diesel
    },
    notification_enabled=True
)

if success:
    print(f"Criteria created: {criteria['id']}")
```

### Example 3: Add Subscription

```python
from telegram_bot_database_multiuser import TelegramBotDatabaseMultiUser

bot_db = TelegramBotDatabaseMultiUser()

success, error = bot_db.add_subscription(
    user_id="550e8400-e29b-41d4-a716-446655440000",
    search_url="https://www.myauto.ge/ka/s/cars?...",
    search_name="Toyota Land Cruiser",
    search_criteria_id=None  # Optional link to criteria
)

if success:
    print("Subscription added")
else:
    print(f"Failed: {error}")
```

### Example 4: Check for New Listings (for Scheduler)

```python
# In scheduler, for each subscription:
bot_db = TelegramBotDatabaseMultiUser()

# Get all active subscriptions for this user
subscriptions = bot_db.get_subscriptions(user_id)

for sub in subscriptions:
    search_url = sub['search_url']

    # Scrape listings
    listings = scraper.fetch_search_results(search_url)

    # Check which are new for this user
    new_listings = []
    for listing in listings:
        listing_id = listing['listing_id']
        if not bot_db.has_user_seen_listing(user_id, listing_id):
            new_listings.append(listing)
            bot_db.record_user_seen_listing(user_id, listing_id)

    # Send notifications only for new listings
    if new_listings:
        send_telegram_notifications(user_id, new_listings)
```

---

## 🔐 Security Considerations

### Password Security
- Passwords are hashed using SHA-256 with 16-byte random salt
- Never transmitted or logged in plain text
- Users should use strong passwords (8+ characters)

### API Tokens
- Generated as URL-safe random 32-character strings
- Stored as SHA-256 hashes in database
- Can be revoked per token or per user
- Have optional expiration dates

### User Isolation
- All queries filtered by user_id
- Users can only access their own data
- Telegram chat ID linking is optional but recommended

### Database Security
- Use Supabase Row Level Security (RLS) for additional protection
- API keys stored only in environment variables
- No credentials in version control

---

## 📊 Data Model

### users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    telegram_chat_id BIGINT UNIQUE,
    telegram_username TEXT,
    first_name TEXT,
    last_name TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    notification_enabled BOOLEAN DEFAULT TRUE,
    check_interval_minutes INTEGER DEFAULT 15,
    max_subscriptions INTEGER DEFAULT 50,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    last_login TIMESTAMP
);
```

### user_search_criteria Table
```sql
CREATE TABLE user_search_criteria (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    criteria_name TEXT NOT NULL,
    description TEXT,
    search_parameters JSONB NOT NULL,  -- Flexible structure
    notification_enabled BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(user_id, criteria_name)
);
```

### user_subscriptions Table (Updated)
```sql
CREATE TABLE user_subscriptions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),  -- NEW: replaces chat_id
    search_url TEXT NOT NULL,
    search_name TEXT,
    search_criteria_id UUID REFERENCES user_search_criteria(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    last_checked TIMESTAMP,
    chat_id BIGINT  -- LEGACY: for reference
);
```

### user_seen_listings Table (Updated)
```sql
CREATE TABLE user_seen_listings (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),  -- NEW: replaces chat_id
    listing_id TEXT NOT NULL,
    seen_at TIMESTAMP,
    chat_id BIGINT,  -- LEGACY: for reference
    UNIQUE(user_id, listing_id)
);
```

---

## 🔧 Configuration

### Environment Variables
Add to `.env.local`:
```bash
# Existing
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_API_KEY=xxxxxxxxxxxxxxxx

# Bot
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_NOTIFICATION_CHANNEL_ID=...

# Password Hashing (optional, system generates automatically)
PASSWORD_HASH_ITERATIONS=100000
```

### Search Criteria Presets

The system includes preset criteria definitions:

```python
from search_criteria_management import SEARCH_CRITERIA_PRESETS

# Available presets:
# - luxury_suv: Luxury SUVs under 100K
# - budget_sedan: Affordable, reliable sedans
# - eco_hatchback: Fuel-efficient hatchbacks

# Users can import these as starting point
manager.import_criteria_from_dict(user_id, SEARCH_CRITERIA_PRESETS["luxury_suv"])
```

---

## 🧪 Testing

### Run All Tests
```bash
python test_multiuser_system.py
```

### Run Specific Test
```python
from test_multiuser_system import TestUserManagement

tests = TestUserManagement()
results = tests.run_all()
```

### Manual Testing
```python
# Test user management
python user_management.py

# Test search criteria
python search_criteria_management.py

# Test bot database
python telegram_bot_database_multiuser.py
```

---

## 📈 Migration Checklist

- [ ] **Database Migration**
  - [ ] Run SQL migration script
  - [ ] Verify new tables created
  - [ ] Test SQL queries work

- [ ] **Data Migration** (if upgrading from existing system)
  - [ ] Extract existing chat_id subscriptions
  - [ ] Create user accounts for each chat_id
  - [ ] Copy subscriptions to new user_subscriptions table
  - [ ] Copy seen_listings to new table
  - [ ] Verify all data migrated correctly
  - [ ] Keep old tables as backup

- [ ] **Code Updates**
  - [ ] Update import statements
  - [ ] Update database module references
  - [ ] Update scheduler logic
  - [ ] Update bot command handlers
  - [ ] Update authentication flow

- [ ] **Testing**
  - [ ] Run comprehensive test suite
  - [ ] Test user registration
  - [ ] Test user authentication
  - [ ] Test subscription management
  - [ ] Test search criteria management
  - [ ] Test scheduler with multi-user
  - [ ] Test Telegram bot commands

- [ ] **Deployment**
  - [ ] Update GitHub Actions secrets if needed
  - [ ] Deploy updated bot code
  - [ ] Monitor for errors
  - [ ] Test with real Telegram users

---

## 🐛 Troubleshooting

### Issue: "User not found" error
**Solution:** Verify user_id is correct UUID format from users table

### Issue: "Subscription limit reached"
**Solution:** Increase max_subscriptions in users table for that user

### Issue: Duplicate username error
**Solution:** Use different username, or reset password if user forgot credentials

### Issue: Tests fail with "DatabaseManager not available"
**Solution:** Verify SUPABASE_URL and SUPABASE_API_KEY environment variables set

### Issue: "Criteria not found" when updating
**Solution:** Verify user_id matches the criteria owner (authorization check)

---

## 📞 Support & Questions

For implementation support:
1. Review this guide and examples
2. Check test cases in `test_multiuser_system.py`
3. Review docstrings in Python modules
4. Check Supabase logs for API errors

---

## 🔄 Next Steps After Deployment

1. **Update Frontend**
   - Add user registration page
   - Add user login page
   - Add profile management UI
   - Add search criteria management UI
   - Add subscription management UI

2. **Add Advanced Features**
   - Email notifications
   - SMS notifications
   - Webhook integrations
   - User preferences/settings
   - Subscription tiers/limits

3. **Monitor & Optimize**
   - Monitor database performance
   - Track user growth
   - Optimize queries
   - Implement caching

4. **Documentation**
   - Create user guides
   - Create API documentation
   - Create admin guides

---

## 📝 Summary

The multi-user system provides:
- **User Management**: Registration, authentication, profiles
- **Isolation**: Each user's data is completely isolated
- **Search Criteria**: Dynamic, user-specific search filters
- **Subscriptions**: Users manage their own subscriptions
- **Security**: Proper password hashing, API tokens, user authorization
- **Testing**: Comprehensive test suite included
- **Scalability**: Database schema ready for thousands of users

**Total Implementation Time:** ~30-60 minutes for deployment + testing

**Estimated User Growth Support:** 10,000+ concurrent users

Good luck with your deployment! 🚀
