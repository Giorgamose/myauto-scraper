# 🚀 Restart Bot - Quick Guide

**All corrections have been made. The bot now uses Supabase instead of SQLite.**

---

## 🛑 Stop Current Bot

If bot is still running in terminal:

```
Press: Ctrl+C
```

Expected output:
```
[*] Application interrupted by user
[*] Shutting down application...
[*] Stopping scheduler...
[OK] Scheduler stopped
[OK] Application shutdown complete
```

---

## ✅ Verify Setup

Before restarting, make sure:

### 1. Check `.env.local` has Supabase credentials

```bash
# Must have these (from your existing setup):
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_API_KEY=your-api-key-here
TELEGRAM_BOT_TOKEN=your-bot-token-here
```

### 2. Verify Supabase tables exist

Go to: Supabase Dashboard → Table Editor

Should see:
- ✅ `user_subscriptions`
- ✅ `user_seen_listings`
- ✅ `bot_events`

If tables don't exist:
1. Go to SQL Editor
2. Copy: `supabase_schema_telegram_bot.sql`
3. Paste and run
4. Wait for success

---

## 🚀 Start Bot (Corrected)

```bash
python telegram_bot_main.py
```

### Expected Output ✅

```
[*] MyAuto Telegram Bot Backend
[*] Version: 1.0.0
[*] Initializing Telegram Bot Application...
[*] Initializing Supabase database...
[OK] Supabase database initialized
[*] Initializing bot backend...
[OK] Bot backend initialized
[OK] Configuration loaded
[OK] Scraper initialized
[*] Initializing notifications...
[OK] Notifications initialized
[*] Initializing scheduler...
[OK] Scheduler initialized (check interval: 15 minutes)
[*] Starting background scheduler...
[OK] Scheduler started
[*] Starting bot message handler (long polling)...
[*] Bot is now listening for messages...
```

**No threading errors! ✅**

---

## 🧪 Test Bot Works

### In Telegram:

1. **Find your bot** (search by name)
2. **Send:** `/help`
3. **Expected response:**
   ```
   🚗 MyAuto Search Bot

   Available Commands:
   /set <url>
   /list
   /clear
   /status
   /help
   ```

### If no response:

Check logs in terminal for errors. Most common:
- Missing `TELEGRAM_BOT_TOKEN` → Add to `.env.local`
- Supabase tables missing → Run SQL schema
- Network issue → Check internet connection

---

## 📊 Check Logs

While bot is running, you should see:

```
[*] Message from chat XXXXX: /help
[OK] Message sent to chat XXXXX
```

This means it's working! ✅

---

## 🔧 What Changed

**Changed from SQLite → Supabase:**

- ❌ SQLite threading errors - FIXED
- ✅ Uses shared Supabase database
- ✅ No local `telegram_bot.db` file
- ✅ Same database as `main.py`

---

## 🎯 Next Steps

1. **Restart bot** - See above
2. **Test commands** - Send `/help`
3. **Add a search** - Send `/set <MyAuto URL>`
4. **Check it works** - Send `/list`
5. **Keep running** - Leave terminal open

---

## ⚠️ Common Issues

### Issue: "Failed to initialize Supabase database"

**Fix:**
1. Check `.env.local` has `SUPABASE_URL` and `SUPABASE_API_KEY`
2. Verify values are correct (not truncated)
3. Restart bot

### Issue: SSL warnings in logs

**Normal!** Example:
```
[WARN] SSL verification failed, retrying without verification
[WARN] This may indicate a corporate proxy or firewall
[OK] Message sent
```

Bot handles this automatically.

### Issue: "TELEGRAM_BOT_TOKEN not found"

**Fix:**
1. Check `.env.local`
2. Add: `TELEGRAM_BOT_TOKEN=your-token-here`
3. Save file
4. Restart bot

### Issue: Still getting threading errors

**This shouldn't happen!** If you do, it means SQLite is still being used somehow.

**Solution:**
1. Stop bot (Ctrl+C)
2. Open `telegram_bot_main.py`
3. Check line 32 says: `from telegram_bot_database_supabase import TelegramBotDatabaseSupabase`
4. Check line 74 says: `self.database = TelegramBotDatabaseSupabase()`
5. Save
6. Restart bot

---

## ✅ Success Checklist

- [ ] Supabase credentials in `.env.local`
- [ ] Supabase tables created
- [ ] Bot starts without errors
- [ ] Bot responds to `/help`
- [ ] Logs show messages being received
- [ ] No threading errors in logs

---

## 📚 Documentation

If you need more info:
- `SUPABASE_MIGRATION_COMPLETE.md` - What changed
- `LOCAL_TESTING_DEPLOYMENT.md` - Complete testing guide
- `SSL_ERROR_TROUBLESHOOTING.md` - SSL issues

---

## 🎊 You're Ready!

All corrections made. Bot is configured to use Supabase.

Just run:
```bash
python telegram_bot_main.py
```

And test with `/help` in Telegram.

**Good luck! 🚀**
