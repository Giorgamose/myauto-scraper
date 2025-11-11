# Local Testing & Deployment Guide

**Goal:** Get the Telegram bot running locally, test it, then deploy it for continuous operation.

---

## Phase 1: Pre-Testing Checklist ✅

### 1. Verify Database Tables Exist

**Check 1: Open Supabase Dashboard**
- Go to: https://app.supabase.com
- Select your project
- Click "Table Editor" in left sidebar
- Look for these 3 tables:
  - ✅ `user_subscriptions`
  - ✅ `user_seen_listings`
  - ✅ `bot_events`

**If tables don't exist:**
```
1. Go to SQL Editor
2. Open: supabase_schema_telegram_bot.sql
3. Copy all content
4. Paste in SQL Editor
5. Click "Run"
6. Wait for success
```

### 2. Verify Environment Variables

**Check 2: Verify `.env.local` has all settings**

Open `.env.local` and confirm these exist:

```bash
# Required - Existing (you should have these)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_API_KEY=your-api-key-here

# Required - New (add if missing)
TELEGRAM_BOT_TOKEN=your-bot-token-here

# Optional - Bot config (add if missing)
BOT_CHECK_INTERVAL_MINUTES=15
BOT_DATABASE_PATH=./telegram_bot.db    # Only needed if using SQLite
BOT_ENABLED=true
BOT_ALLOWED_CHATS=                     # Leave empty for now
```

**Get Bot Token:**
```
1. Open Telegram
2. Search: @BotFather
3. Send: /newbot
4. Follow prompts
5. Copy the HTTP API token
6. Paste in .env.local as TELEGRAM_BOT_TOKEN
```

### 3. Verify All Files Exist

**Check 3: Verify all required files are present**

```bash
# Python modules
ls telegram_bot_backend.py
ls telegram_bot_scheduler.py
ls telegram_bot_main.py
ls telegram_bot_database_supabase.py

# Existing modules (should already exist)
ls scraper.py
ls parser.py
ls notifications.py
ls utils.py
ls database_rest_api.py
```

All should exist ✅

---

## Phase 2: Local Testing (First Time)

### Step 1: Open Terminal/Command Prompt

**Windows:**
```
Start → cmd (or PowerShell)
```

**Mac/Linux:**
```
Open Terminal application
```

### Step 2: Navigate to Project Directory

```bash
cd "C:\Users\gmaevski\Documents\MyAuto Listening Scrapper"
```

**Verify you're in correct directory:**
```bash
ls telegram_bot_main.py
# Should show the file exists
```

### Step 3: Start the Bot

```bash
python telegram_bot_main.py
```

**Expected Output (First Run):**
```
[*] MyAuto Telegram Bot Backend
[*] Version: 1.0.0
[*] Initializing Telegram Bot Application...
[*] Initializing database...
[OK] Database connected: telegram_bot.db
[OK] Database schema initialized
[*] Initializing bot backend...
[OK] Bot backend initialized
[OK] Scheduler initialized (check interval: 15 minutes)
[*] Starting background scheduler...
[OK] Scheduler started
[*] Starting bot message handler (long polling)...
[*] Bot is now listening for messages...
```

**If you see errors:**
→ See "Troubleshooting" section below

### Step 4: Test in Telegram

**While bot is running in terminal:**

1. **Open Telegram**
2. **Find your bot** (search by name you gave @BotFather)
3. **Send: `/help`**

**Expected Response:**
```
🚗 MyAuto Search Bot

Available Commands:

/set <url>
  Save a MyAuto search URL to monitor

/list
  Show all your saved searches

/clear
  Remove all your saved searches

/status
  Show bot statistics

/help
  Show this help message
```

### Step 5: Test Each Command

#### Test 1: `/status`

```
Send: /status

Expected Response:
📊 Bot Statistics

Your Status:
• Active searches: 0

Overall Statistics:
• Active users: 0
• Total searches: 0
• Listings tracked: 0

Server Status: ✅ Online and monitoring
```

#### Test 2: `/set` Command

```
Send: /set https://www.myauto.ge/ka/search?make_id=1&price_from=5000&price_to=20000

Expected Response:
✅ Search criteria saved!

URL: https://www.myauto.ge/ka/search?...

I'll check this search periodically and notify you when new listings appear. 🔔

Use /list to see all your saved searches.
```

#### Test 3: `/list` Command

```
Send: /list

Expected Response:
📋 Your saved searches:

1. https://www.myauto.ge/ka/search?make_id=1&...
   Added: 2024-11-10 15:30:45
   Last checked: Never

Total: 1 search(es)

To remove a search, send: /clear
```

#### Test 4: `/clear` Command

```
Send: /clear

Expected Response:
✅ All searches cleared!

Removed 1 search(es) from monitoring.

To add new searches:
/set <MyAuto.ge URL>
```

### Step 6: Check Logs

While bot is running, you should see logs like:

```
[*] Message from chat 123456789: /set https://www.myauto.ge/ka/search?...
[+] Subscription added: chat_id=123456789, url=https://...
[OK] Message sent to chat 123456789
[*] Next check in 900 seconds
```

### Step 7: Stop the Bot

```
Press: Ctrl+C

Expected:
[*] Application interrupted by user
[*] Shutting down application...
[*] Stopping scheduler...
[OK] Scheduler stopped
[*] Closing database...
[OK] Database closed
[OK] Application shutdown complete
```

---

## Phase 3: Running Both Systems Together (Local)

### Goal
Run both `main.py` (predefined searches) and `telegram_bot_main.py` (user commands) simultaneously.

### Option A: Two Terminal Windows (Easiest)

**Terminal 1 - Main System:**
```bash
cd "C:\Users\gmaevski\Documents\MyAuto Listening Scrapper"
python main.py
```

**Terminal 2 - Bot System:**
```bash
cd "C:\Users\gmaevski\Documents\MyAuto Listening Scrapper"
python telegram_bot_main.py
```

Both systems run independently.

### Option B: Using Helper Script

**Windows:**
```bash
run_both_systems.bat
```

**Linux/Mac:**
```bash
chmod +x run_both_systems.sh
./run_both_systems.sh
```

Both systems start in separate windows/processes.

### Verify Both Systems Running

**In Telegram bot:**
```
Send: /status

Should show:
• Active users: 1 (or more)
• Total searches: N (from bot)
+ Plus notifications from main.py
```

---

## Phase 4: Local Deployment (Continuous Running)

### Option A: Keep Terminal Open (Development)

**Simple but requires leaving terminal open:**

```bash
python telegram_bot_main.py
```

Terminal must stay open 24/7. If you close it, bot stops.

**Use this for:**
- Testing
- Development
- Short-term deployment

### Option B: Background Process (Windows)

**Run bot in background without terminal window:**

**Method 1: Create Batch File**

Create file: `start_bot.bat`

```batch
@echo off
REM Start bot in background
start "" /B python telegram_bot_main.py
echo Bot started in background
pause
```

Run:
```bash
start_bot.bat
```

Bot runs in background, terminal closes.

**Method 2: PowerShell**

```powershell
Start-Process -WindowStyle Hidden -FilePath "python" -ArgumentList "telegram_bot_main.py"
```

### Option C: Windows Task Scheduler (Always Running)

**Setup automatic restart if bot crashes:**

1. **Open Task Scheduler**
   - Press: Windows Key + R
   - Type: `tasksched.msc`
   - Press: Enter

2. **Create New Task**
   - Right-click "Task Scheduler Library"
   - Click "Create Task"

3. **General Tab**
   - Name: `Telegram Bot Monitor`
   - Check: "Run whether user is logged in or not"
   - Check: "Run with highest privileges"

4. **Triggers Tab**
   - Click: "New..."
   - Begin task: "At startup"
   - Check: "Enabled"
   - Click: "OK"

5. **Actions Tab**
   - Click: "New..."
   - Action: "Start a program"
   - Program: `python`
   - Arguments: `telegram_bot_main.py`
   - Start in: `C:\Users\gmaevski\Documents\MyAuto Listening Scrapper`
   - Click: "OK"

6. **Conditions Tab**
   - Uncheck: "Stop if computer is on battery"

7. **Settings Tab**
   - Check: "Run task as soon as possible after a scheduled start is missed"
   - Check: "If the task fails, restart every: 5 minutes"
   - Check: "Repeat task every: [never]"

8. **Click: "OK"**

Bot now starts automatically on boot and restarts if it crashes!

### Option D: Linux/Mac - systemd Service

**Setup bot as system service:**

Create file: `/etc/systemd/system/telegram-bot.service`

```ini
[Unit]
Description=MyAuto Telegram Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/MyAuto Listening Scrapper
ExecStart=/usr/bin/python3 telegram_bot_main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

Check status:
```bash
sudo systemctl status telegram-bot
```

### Option E: Docker (Advanced)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "telegram_bot_main.py"]
```

Build and run:
```bash
docker build -t telegram-bot .
docker run -d --name telegram-bot \
  -e SUPABASE_URL=your-url \
  -e SUPABASE_API_KEY=your-key \
  -e TELEGRAM_BOT_TOKEN=your-token \
  telegram-bot
```

---

## Phase 5: Monitoring & Maintenance

### Check Bot is Running

**Windows:**
```bash
tasklist | find "python.exe"
```

**Linux/Mac:**
```bash
ps aux | grep telegram_bot
```

Should see: `python telegram_bot_main.py`

### View Logs

**If running in terminal:**
- Logs display in real-time

**If running in background:**

Create monitoring script: `check_bot_status.py`

```python
from telegram_bot_database_supabase import TelegramBotDatabaseSupabase

db = TelegramBotDatabaseSupabase()
stats = db.get_statistics()

print(f"Active users: {stats['total_users']}")
print(f"Total subscriptions: {stats['total_subscriptions']}")
print(f"Total seen listings: {stats['total_seen_listings']}")

# View recent events
events = db.get_events(limit=20)
for event in events:
    print(f"{event['created_at']} - {event['event_type']}: {event['event_data']}")
```

Run:
```bash
python check_bot_status.py
```

### Stop Bot

**If in terminal:**
- Press: `Ctrl+C`

**If in background (Windows):**
```bash
taskkill /IM python.exe /FI "WINDOWTITLE eq telegram_bot_main.py"
```

**If as service (Linux):**
```bash
sudo systemctl stop telegram-bot
```

---

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'requests'"

**Solution:**
```bash
pip install requests python-dotenv
```

### Error: "TELEGRAM_BOT_TOKEN not found"

**Solution:**
1. Check `.env.local` has `TELEGRAM_BOT_TOKEN=your-token`
2. Verify token from @BotFather is correct
3. Ensure no spaces before/after token

### Error: "Failed to connect to Supabase"

**Solution:**
1. Verify `SUPABASE_URL` in `.env.local`
2. Verify `SUPABASE_API_KEY` in `.env.local`
3. Check Supabase project is still active
4. Check internet connection

### Error: "Tables don't exist"

**Solution:**
1. Go to Supabase SQL Editor
2. Run: `supabase_schema_telegram_bot.sql`
3. Verify 3 tables created in Table Editor

### Bot Not Responding to Commands

**Solution:**
1. Check bot is still running (see "Check Bot is Running")
2. Verify bot token is correct (ask @BotFather for new token if needed)
3. Check logs for errors
4. Try sending `/help` again
5. Restart bot: `Ctrl+C` then `python telegram_bot_main.py`

### No Notifications Received

**Solution:**
1. Verify subscription added: Send `/list`
2. Wait for check interval (default 15 minutes)
3. Check logs for scheduler activity
4. Verify scraper can fetch listings
5. Check Supabase for data in `user_subscriptions` table

---

## Testing Checklist

- [ ] Database tables created in Supabase
- [ ] `.env.local` has all required variables
- [ ] All Python files present
- [ ] Bot starts without errors: `python telegram_bot_main.py`
- [ ] Bot responds to `/help`
- [ ] Bot responds to `/status`
- [ ] Can add subscription with `/set`
- [ ] Can view subscriptions with `/list`
- [ ] Can clear subscriptions with `/clear`
- [ ] Both systems work together (main.py + telegram_bot_main.py)
- [ ] Logs show activity

---

## Next: GitHub Actions Setup

Once local testing is complete and bot runs reliably:

1. Add GitHub Secrets:
   - SUPABASE_URL
   - SUPABASE_API_KEY
   - TELEGRAM_BOT_TOKEN
   - BOT_CHECK_INTERVAL_MINUTES

2. Keep bot running locally (or use deployment method above)

3. Later: Create GitHub Actions workflow file

See: `GITHUB_ACTIONS_SETUP.md` (to be created)

---

## Summary

| Phase | Status | Time |
|-------|--------|------|
| Setup database tables | ✅ Complete | 5 min |
| Test locally | 👈 **You are here** | 10 min |
| Deploy continuously | Next | 5 min |
| GitHub Actions | Later | 15 min |

**Next Step:** Start bot locally!

```bash
python telegram_bot_main.py
```

Then send `/help` in Telegram to verify it works.

**Good luck! 🚀**
