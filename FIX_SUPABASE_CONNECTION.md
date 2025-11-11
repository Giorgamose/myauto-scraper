# 🔧 Fix Supabase Connection Error

**Error:** `[ERROR] Failed to connect to Supabase`

**Solution:** Check and fix your environment variables

---

## 🔍 Step 1: Run Diagnostic

```bash
python diagnose_supabase.py
```

This will show exactly what's wrong.

---

## 📋 Step 2: Check `.env.local`

Open the file in your editor:

```
c:\Users\gmaevski\Documents\MyAuto Listening Scrapper\.env.local
```

### It should contain:

```bash
# Existing - should already be here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_API_KEY=your-api-key-here
TELEGRAM_BOT_TOKEN=your-bot-token-here
```

---

## 🔑 Step 3: Get Correct Supabase Credentials

### From Supabase Dashboard:

1. **Open:** https://app.supabase.com
2. **Select your project** (the one with MyAuto data)
3. **Go to:** Settings (gear icon) → API
4. **Copy these:**
   - `Project URL` → Use as `SUPABASE_URL`
   - `anon public` key → Use as `SUPABASE_API_KEY`

### Example values (yours will be different):

```bash
SUPABASE_URL=https://jxyzqwerty123.supabase.co
SUPABASE_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## ✏️ Step 4: Update `.env.local`

1. **Open** `.env.local` in text editor
2. **Find** these lines:
   ```bash
   SUPABASE_URL=
   SUPABASE_API_KEY=
   TELEGRAM_BOT_TOKEN=
   ```
3. **Replace** with actual values from Supabase Dashboard
4. **Make sure:**
   - No spaces before/after `=`
   - No quotes around values
   - URLs start with `https://`
   - Keys don't have trailing spaces

### ✅ Correct format:

```bash
SUPABASE_URL=https://jxyzqwerty123.supabase.co
SUPABASE_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9eyJ...
TELEGRAM_BOT_TOKEN=8531271294:AAH7Od2Ul...
```

### ❌ Wrong format:

```bash
SUPABASE_URL = https://jxyzqwerty123.supabase.co   # Spaces around =
SUPABASE_API_KEY="eyJhbGciOi..."                    # Quotes
TELEGRAM_BOT_TOKEN=8531271294:AAH7Od2Ul            # Missing value
```

5. **Save file** (Ctrl+S)

---

## 🧪 Step 5: Verify Connection

```bash
python diagnose_supabase.py
```

### Should see:

```
✅ SUPABASE_URL: Set
✅ SUPABASE_API_KEY: Set
✅ TELEGRAM_BOT_TOKEN: Set
✅ URL looks correct
✅ API key format OK
✅ SUPABASE CONNECTION SUCCESSFUL
```

---

## 🚀 Step 6: Restart Bot

```bash
python telegram_bot_main.py
```

### Should now see:

```
[*] Initializing Telegram Bot Application...
[*] Initializing Supabase database...
[OK] Supabase database initialized
[OK] Scheduler initialized
[*] Bot is now listening for messages...
```

**No connection errors!** ✅

---

## 🆘 Common Issues

### Issue: "Failed to connect to Supabase"

**Likely causes:**
1. Environment variables not set
2. Wrong project (credentials from different Supabase project)
3. API key is inactive/revoked

**Fix:**
1. Run: `python diagnose_supabase.py`
2. Check all values are present
3. Verify you're using correct Supabase project
4. Re-generate API key if needed

---

### Issue: "Authentication failed - Invalid API key"

**Cause:** API key is wrong or from different project

**Fix:**
1. Go to Supabase Dashboard
2. Settings → API
3. Copy "anon public" key (NOT "service role")
4. Replace in `.env.local`
5. Restart bot

---

### Issue: "Table 'user_subscriptions' doesn't exist"

**Cause:** Database tables weren't created

**Fix:**
1. Go to Supabase → SQL Editor
2. Copy: `supabase_schema_telegram_bot.sql`
3. Paste in SQL Editor
4. Click "Run"
5. Wait for success
6. Restart bot

---

### Issue: "Network connection failed"

**Cause:** Internet not working or firewall blocking

**Fix:**
1. Check internet connection
2. Try pinging Supabase: `ping app.supabase.com`
3. Check if corporate proxy/firewall blocking
4. If behind proxy, SSL warnings are normal (bot handles them)

---

## ✅ Quick Checklist

Before restarting bot:

- [ ] `.env.local` has `SUPABASE_URL`
- [ ] `.env.local` has `SUPABASE_API_KEY`
- [ ] `.env.local` has `TELEGRAM_BOT_TOKEN`
- [ ] All values copied from Supabase Dashboard
- [ ] No spaces or quotes around values
- [ ] File saved after editing
- [ ] Run `diagnose_supabase.py` shows ✅
- [ ] Database tables exist in Supabase

---

## 📞 Still Having Issues?

**Share output of:**

```bash
python diagnose_supabase.py
```

This will show exactly what's wrong and I can help fix it.

---

## 🔄 Quick Summary

1. Run: `python diagnose_supabase.py` → See what's wrong
2. Edit: `.env.local` → Add correct credentials
3. Verify: Run diagnostic again → Should show ✅
4. Restart: `python telegram_bot_main.py` → Should work

That's it! 🚀
