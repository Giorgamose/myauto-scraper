# ✅ Pre-Restart Checklist

**Before restarting the bot, verify everything is correct.**

---

## 1️⃣ Environment Variables

### Check `.env.local`

Open the file and verify these exist (copy exact values from your Supabase project):

```bash
# Existing - you should have these
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_API_KEY=your-api-key-here
TELEGRAM_BOT_TOKEN=your-bot-token-here

# Optional - with defaults if missing
BOT_CHECK_INTERVAL_MINUTES=15
BOT_ENABLED=true
```

**Verification:**
- [ ] SUPABASE_URL looks like: `https://xxxxx.supabase.co`
- [ ] SUPABASE_API_KEY is not empty
- [ ] TELEGRAM_BOT_TOKEN is not empty
- [ ] No typos in variable names

---

## 2️⃣ Supabase Database Tables

### Go to Supabase Dashboard

1. Open: https://app.supabase.com
2. Select your project
3. Click "Table Editor" in left sidebar

### Verify 3 tables exist:

- [ ] `user_subscriptions` exists
- [ ] `user_seen_listings` exists
- [ ] `bot_events` exists

**If tables don't exist:**

1. Go to SQL Editor
2. Copy: `supabase_schema_telegram_bot.sql`
3. Paste in SQL Editor
4. Click "Run"
5. Wait for success message

---

## 3️⃣ Python Files Verified

### All bot files are present:

- [ ] `telegram_bot_main.py` exists
- [ ] `telegram_bot_backend.py` exists
- [ ] `telegram_bot_scheduler.py` exists
- [ ] `telegram_bot_database_supabase.py` exists

### All existing modules are present:

- [ ] `scraper.py` exists
- [ ] `parser.py` exists
- [ ] `notifications.py` exists
- [ ] `utils.py` exists
- [ ] `database_rest_api.py` exists
- [ ] `config.json` exists

---

## 4️⃣ Code Updates Verified

### Check `telegram_bot_main.py` was updated

Open file and verify:

**Line ~32 should have:**
```python
from telegram_bot_database_supabase import TelegramBotDatabaseSupabase
```

- [ ] Import uses `_supabase` version (not just `TelegramBotDatabase`)

**Line ~74-75 should have:**
```python
self.database = TelegramBotDatabaseSupabase()
```

- [ ] Initialization uses `TelegramBotDatabaseSupabase()`
- [ ] Does NOT use `TelegramBotDatabase(db_path)`

---

## 5️⃣ Internet Connection

### Verify network access:

```bash
# Test Telegram API
ping api.telegram.org

# Test Supabase
ping your-project.supabase.co
```

- [ ] Telegram API is reachable
- [ ] Supabase is reachable
- [ ] No firewall blocking (SSL warnings are OK)

---

## 6️⃣ Python Dependencies

### Required packages installed:

```bash
pip list | grep -E "requests|python-dotenv"
```

Should see:
- [ ] `requests` is installed
- [ ] `python-dotenv` is installed

**If missing:**
```bash
pip install requests python-dotenv
```

---

## 7️⃣ No Conflicting Processes

### Make sure nothing else is using port/resources:

```bash
# Windows - check for running python
tasklist | find "python"

# Mac/Linux - check for running python
ps aux | grep python
```

- [ ] No other `telegram_bot_main.py` running
- [ ] No other `main.py` running (or that's OK if you want both)

**If anything is running:**

Stop it first (find the terminal window and Ctrl+C)

---

## 8️⃣ File Permissions

### Ensure files are readable:

```bash
# On Windows, this usually just works
# On Mac/Linux:
chmod +x telegram_bot_main.py
chmod +x telegram_bot_backend.py
chmod +x telegram_bot_scheduler.py
```

- [ ] All files are readable/executable

---

## 9️⃣ Bot Token Verification

### Verify Telegram bot token is valid

```bash
# This will test if token works
python -c "
import requests
token = 'your-token-here'
response = requests.post(f'https://api.telegram.org/bot{token}/getMe')
if response.json().get('ok'):
    print('✅ Token is valid')
else:
    print('❌ Token is invalid')
"
```

Replace `your-token-here` with your actual token.

- [ ] Token is valid (or you'll see ✅)

---

## 🔟 Final Verification

### Run syntax check:

```bash
python -m py_compile telegram_bot_main.py
python -m py_compile telegram_bot_backend.py
python -m py_compile telegram_bot_scheduler.py
python -m py_compile telegram_bot_database_supabase.py
```

Should see no errors.

- [ ] All files have valid Python syntax

---

## ✅ Ready to Restart?

If all checkboxes are checked ✅, you're ready!

### Final Restart:

1. **Stop any running bot:**
   ```
   Ctrl+C in terminal
   ```

2. **Start fresh:**
   ```bash
   python telegram_bot_main.py
   ```

3. **Expected output:**
   ```
   [*] MyAuto Telegram Bot Backend
   [*] Initializing Telegram Bot Application...
   [*] Initializing Supabase database...
   [OK] Supabase database initialized
   [OK] Scheduler initialized
   [*] Bot is now listening for messages...
   ```

4. **No threading errors!** ✅

---

## 🧪 Quick Test

Once bot is running:

1. **Find your bot in Telegram**
2. **Send:** `/help`
3. **Expect:** Bot menu with commands

**If it works, you're done!** 🎉

---

## ❌ Something's Not Right?

**Before restarting, go through this list in order:**

1. Check all checkboxes above are done
2. Review error messages carefully
3. Check `.env.local` values match Supabase
4. Verify database tables exist in Supabase
5. Verify `telegram_bot_main.py` was updated correctly

---

## 📚 Reference Documents

- `RESTART_BOT.md` - How to restart
- `SUPABASE_MIGRATION_COMPLETE.md` - What changed
- `LOCAL_TESTING_DEPLOYMENT.md` - Full testing guide
- `BOT_FILES_COMPLETE_GUIDE.md` - What each file does

---

**Once all checks pass, you're ready to restart the bot!** 🚀
