# Complete Testing Plan

## 🎯 Testing Overview

This document covers all testing phases from local development through production monitoring.

---

## Phase 1: Local Environment Testing (Before Deployment)

### 1.1 Environment Setup Validation

**Test**: Verify Python and dependencies are installed
```bash
# Check Python version
python --version
# Expected: Python 3.7 or higher

# Check pip
pip --version
# Expected: pip version X.X.X

# Check virtual environment (if using one)
python -m venv --version
```

**Test**: Install all dependencies
```bash
pip install -r requirements.txt

# Check specific critical packages
pip show libsql-client
pip show requests
pip show python-telegram-bot
```

Expected output: All packages successfully installed

---

### 1.2 Configuration Validation

**Test**: Verify config.json is properly formatted
```bash
# Test JSON syntax
python -c "import json; json.load(open('config.json'))"
# Expected: No error (valid JSON)
```

**Test**: Verify config content
```python
import json

with open('config.json') as f:
    config = json.load(f)

# Check required keys
assert 'search_criteria' in config
assert 'notification_config' in config
assert config['search_criteria']['make'] == 'Toyota'
assert config['search_criteria']['model'] == 'Land Cruiser Prado'

print("✓ Config validation passed")
```

Expected: All assertions pass

---

### 1.3 Database Connection Testing (Local)

**Test**: Run connection validator
```bash
# Set environment variables
$env:TURSO_DATABASE_URL = "libsql://your-db.turso.io"
$env:TURSO_AUTH_TOKEN = "your-token"

# Run test
python test_db_connection.py
```

Expected output:
```
[OK] TURSO_DATABASE_URL is set
[OK] TURSO_AUTH_TOKEN is set
[OK] libsql_client is installed
[OK] Connected to Turso database
[OK] Query successful
    Records in database: X (or 0 if empty)

SUCCESS! YOUR SETUP IS CORRECT
```

---

### 1.4 Module Import Testing

**Test**: Verify all modules can be imported
```bash
python -c "
import main
import scraper
import parser
import database
import notifications
import notifications_telegram
import utils

print('✓ All modules imported successfully')
"
```

Expected: All imports succeed without errors

---

### 1.5 Scraper Module Testing

**Test**: Test scraper URL generation
```bash
python -c "
from scraper import MyAutoScraper
import json

with open('config.json') as f:
    config = json.load(f)

scraper = MyAutoScraper(config)
url = scraper.build_search_url()

print(f'✓ Search URL: {url}')
assert 'Toyota' in url or 'toyota' in url.lower()
assert 'Prado' in url or 'prado' in url.lower()
print('✓ URL contains search criteria')
"
```

Expected: URL is valid and contains search terms

---

### 1.6 Parser Module Testing

**Test**: Test data extraction (use sample HTML if available)
```bash
python -c "
from parser import MyAutoParser
import json

with open('config.json') as f:
    config = json.load(f)

parser = MyAutoParser(config)
print(f'✓ Parser initialized')
print(f'✓ Parser has {len(parser.field_mappings)} field mappings')
"
```

Expected: Parser initializes with correct field mappings

---

### 1.7 Database Module Testing

**Test**: Database operations
```bash
# Set environment variables
$env:TURSO_DATABASE_URL = "your-url"
$env:TURSO_AUTH_TOKEN = "your-token"

python -c "
from database import TursoDatabase
import os

db = TursoDatabase(
    url=os.getenv('TURSO_DATABASE_URL'),
    token=os.getenv('TURSO_AUTH_TOKEN')
)

# Test connection
result = db.get_record_count()
print(f'✓ Connected to database')
print(f'✓ Current record count: {result}')
"
```

Expected: Connection succeeds and returns record count

---

### 1.8 Notification Module Testing

**Test**: Verify notification templates load
```bash
python -c "
from notifications import NotificationManager
import json

with open('config.json') as f:
    config = json.load(f)

notif = NotificationManager(config)
print('✓ Notification manager initialized')
print(f'✓ Templates loaded: {len(notif.templates)} templates')
"
```

Expected: Notification manager initializes successfully

---

### 1.9 Telegram Module Testing

**Test**: Verify Telegram bot connection (if credentials available)
```bash
# Set Telegram credentials
$env:TELEGRAM_BOT_TOKEN = "your-token"
$env:TELEGRAM_CHAT_ID = "your-chat-id"

python -c "
from notifications_telegram import TelegramNotifier
import os

telegram = TelegramNotifier(
    bot_token=os.getenv('TELEGRAM_BOT_TOKEN'),
    chat_id=os.getenv('TELEGRAM_CHAT_ID')
)

# Test connection (doesn't send message, just verifies setup)
print('✓ Telegram notifier initialized')
print('✓ Ready to send notifications')
"
```

Expected: Telegram notifier initializes successfully

---

## Phase 2: Integration Testing (Local)

### 2.1 End-to-End Dry Run

**Test**: Run complete workflow without notifications
```bash
# Set all environment variables
$env:TURSO_DATABASE_URL = "your-url"
$env:TURSO_AUTH_TOKEN = "your-token"
$env:TELEGRAM_BOT_TOKEN = "your-token"
$env:TELEGRAM_CHAT_ID = "your-chat-id"

# Run with logging
python main.py

# Expected output:
# [INFO] Loading configuration...
# [INFO] Initializing scraper...
# [INFO] Starting scrape cycle...
# [INFO] Fetching listings...
# [INFO] Processing listings...
# [INFO] X records processed
# [INFO] Y new records added
# [INFO] Z duplicates skipped
```

---

### 2.2 Database Verification After Run

**Test**: Check if data was added to database
```bash
python view_database.py

# Verify:
# - Total records increased
# - New records show correct fields
# - Dates are current
# - Price/year/fuel match search criteria
```

---

### 2.3 Telegram Notification Test

**Test**: Send test notification to verify Telegram integration
```bash
python -c "
from notifications_telegram import TelegramNotifier
import os

telegram = TelegramNotifier(
    bot_token=os.getenv('TELEGRAM_BOT_TOKEN'),
    chat_id=os.getenv('TELEGRAM_CHAT_ID')
)

# Create test message
test_listing = {
    'title': 'TEST: Toyota Land Cruiser Prado 2005',
    'price': 15500,
    'currency': 'GEL',
    'year': 2005,
    'mileage': 145000,
    'fuel_type': 'Diesel',
    'transmission': 'Manual',
    'seller_phone': '+995 591 234 567',
    'listing_id': 'TEST123'
}

result = telegram.send_listing_notification(test_listing)
print(f'✓ Notification sent: {result}')
"
```

Expected: Message received in Telegram chat with test listing details

---

### 2.4 Database Query Tools Testing

**Test**: Run all query tools
```bash
# Test overview
python view_database.py
# Expected: Shows statistics and latest records

# Test table view
python db_table_view.py
# Expected: Shows clean table of 50 latest records

# Test interactive query
python query_database.py
# Try each option:
# 1) View all
# 2) Toyota Prado
# 3) Price filter (11000-15000)
# 4) Year range (2000-2008)
# 5) Make filter (Toyota)
# 6) Last N days (1)
# 7) Lookup by ID
# 8) Show all
# 9) Export CSV
```

Expected: All tools run without errors

---

## Phase 3: GitHub Actions Testing

### 3.1 Workflow File Validation

**Test**: Check GitHub Actions workflow file
```bash
# GitHub will validate automatically on push
# Check at: GitHub → Actions → Workflows

# Manual validation (optional):
# The file should be at: .github/workflows/scrape.yml
```

Expected: No validation errors

---

### 3.2 Secrets Configuration

**Test**: Verify all 4 secrets are set
Go to: Settings → Secrets and Variables → Actions

Verify 4 secrets exist:
- ✅ TURSO_DATABASE_URL
- ✅ TURSO_AUTH_TOKEN
- ✅ TELEGRAM_BOT_TOKEN
- ✅ TELEGRAM_CHAT_ID

All secrets should be non-empty.

---

### 3.3 Manual Workflow Trigger

**Test**: Trigger workflow manually
```
1. Go to: GitHub → Your Repo → Actions
2. Select: "MyAuto Car Listing Monitor"
3. Click: "Run workflow" → "Run workflow"
4. Wait 1-2 minutes
5. Check logs
```

Expected output in logs:
```
[*] Starting monitoring cycle at [date]
...
[OK] Scrape completed
[*] Processing X records
[*] Y new records added
[*] Sending notifications
[*] Monitoring cycle completed with exit code: 0
```

---

### 3.4 First Automated Run

**Test**: Wait for automatic 10-minute run
```
1. GitHub Actions runs every 10 minutes
2. Wait or manually trigger
3. Check Actions tab for latest run
4. Verify: Passed (green checkmark)
```

Expected: Workflow completes successfully

---

### 3.5 Error Notification Test

**Test**: Verify error notifications work
```
1. Temporarily modify config to cause an error
2. Push to GitHub
3. Wait for next scheduled run
4. Check Telegram for error notification
5. Revert changes
```

Expected: Error message received in Telegram

---

## Phase 4: Production Monitoring

### 4.1 First 10 Minutes
After deploying to GitHub Actions:

**Checklist:**
- [ ] GitHub Actions started first run (check Actions tab)
- [ ] Run completed in ~1-2 minutes
- [ ] No errors in logs
- [ ] Check database for new records:
  ```bash
  python view_database.py
  ```

Expected: 1-3 new records added

---

### 4.2 First Hour
After 6 automated cycles:

**Checklist:**
- [ ] All 6 runs completed successfully
- [ ] Database shows 6-18 records
- [ ] No pattern of failures
- [ ] Telegram received notifications (if records matched)

---

### 4.3 First Day
After ~144 automated cycles:

**Checklist:**
- [ ] Database has 10-20 Toyota Prado records
- [ ] Latest records show today's date
- [ ] Price range is correct (11,000-18,000 GEL)
- [ ] All records are Diesel + Manual
- [ ] Telegram notifications came through
- [ ] No error notifications received

**Test queries:**
```bash
python query_database.py
# Option 2: Toyota Prado records
# Expected: 10-20 records

# Option 3: Price range 11000-18000
# Expected: Matches your search criteria
```

---

### 4.4 First Week
After ~500 automated cycles:

**Checklist:**
- [ ] Database has 40-70 Toyota Prado listings
- [ ] Listing variety: Different years, sellers, conditions
- [ ] No major error patterns
- [ ] Telegram notifications still working
- [ ] Some duplicate sellers (normal - same cars relisted)

**Export and analyze:**
```bash
python query_database.py
# Option 9: Export to CSV

# Open in Excel and analyze:
# - Average price
# - Most common year
# - Price distribution
# - Seller frequency
```

---

### 4.5 Ongoing Monitoring

**Daily:**
```bash
python view_database.py
# Check: New records count, latest additions
```

**Weekly:**
```bash
python query_database.py
# Option 3: Price filter (11000-18000)
# Find best deals
```

**Monthly:**
```bash
python query_database.py
# Option 9: Export to CSV
# Analyze trends, price changes, new listings
```

---

## Test Cases Summary

| Phase | Test | Status | Notes |
|-------|------|--------|-------|
| **Local** | Python/Pip installed | Pre-Deploy | Must pass before push |
| **Local** | config.json valid | Pre-Deploy | Must pass before push |
| **Local** | Database connection | Pre-Deploy | Must pass before push |
| **Local** | Module imports | Pre-Deploy | Must pass before push |
| **Local** | Scraper URL generation | Pre-Deploy | Validates search logic |
| **Local** | Parser initialization | Pre-Deploy | Validates extraction |
| **Local** | Database operations | Pre-Deploy | Validates Turso |
| **Local** | Notifications setup | Pre-Deploy | Validates templates |
| **Local** | Telegram connection | Pre-Deploy | Validates bot token |
| **Integration** | End-to-end dry run | Pre-Deploy | Full workflow test |
| **Integration** | Database after run | Post-Deploy | Validates persistence |
| **Integration** | Telegram notification | Post-Deploy | Validates messaging |
| **Integration** | Query tools | Post-Deploy | Validates viewing |
| **GitHub** | Workflow validation | Pre-Deploy | GitHub auto-validates |
| **GitHub** | Secrets configured | Deploy-Time | 4 secrets required |
| **GitHub** | Manual trigger | Day 1 | First test run |
| **GitHub** | Automated run | Day 1 | Scheduled execution |
| **GitHub** | Error notification | Day 1 | Error handling |
| **Production** | First 10 minutes | Day 1 | Quick verification |
| **Production** | First hour | Day 1 | 6 cycles complete |
| **Production** | First day | Day 1 | 144 cycles data |
| **Production** | First week | Day 7 | 40-70 listings |
| **Production** | Ongoing | Daily | Continuous monitoring |

---

## Success Criteria

✅ **Successful Deployment** = All of:
1. GitHub Actions workflow runs every 10 minutes
2. Each run completes in <2 minutes
3. No error notifications sent
4. Database grows steadily (10+ records/day)
5. Records match search criteria (Diesel, Manual, 11-18k GEL)
6. Telegram notifications delivered for matches
7. Query tools show data correctly

❌ **Issues to Watch For**:
- Workflow times out (>10 min)
- Consistent failures (red X on Actions)
- Duplicate data not being filtered
- Database not growing
- Telegram messages not received
- Wrong records being scraped (wrong make/model)

---

## Rollback Plan

If something goes wrong:

### Option 1: Disable Workflow (Quick Fix)
```
Settings → Actions → Disable this workflow
```
Stops automatic runs, data preserved.

### Option 2: Fix and Redeploy
1. Make code/config changes locally
2. Test with: `python main.py`
3. Commit and push to GitHub
4. Re-enable workflow
5. Test again

### Option 3: Reset Database
If corrupted:
1. Go to https://app.turso.tech
2. Delete database
3. Create new database
4. Update TURSO_DATABASE_URL in GitHub Secrets
5. Restart workflow

---

## Performance Benchmarks

Expected performance metrics:

| Metric | Expected | Acceptable Range |
|--------|----------|------------------|
| Scrape time | 30-60 sec | <120 sec |
| Parse time | 5-15 sec | <30 sec |
| DB insert | 5-10 sec | <20 sec |
| Total run | <2 min | <10 min |
| Success rate | 99%+ | >90% |
| Records/day | 10-20 | >5 |

---

## Debugging Guide

### Check Workflow Logs
Go to: Actions → Latest Run → Click each step

### Common Error Messages

**"TURSO_DATABASE_URL is not set"**
- Fix: Add secret in GitHub Settings

**"Connection timeout"**
- Fix: Check internet, try again, temporary issue usually

**"SyntaxError in main.py"**
- Fix: Check for typos, test locally first

**"Telegram: Invalid bot token"**
- Fix: Regenerate token from @BotFather

---

**Version**: 1.0.0
**Last Updated**: November 9, 2025
**Status**: Ready for Production Testing
