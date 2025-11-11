# GitHub Actions Scheduler Setup Guide

## ✅ You Already Have GitHub Actions Setup!

Your scheduler is already configured to run automatically on GitHub Actions every 15 minutes!

---

## What You Have

### 1. **telegram-bot-scheduler.yml** (NEW & BEST)
- Runs every 15 minutes automatically
- 24/7 coverage (no computer needed)
- Better logging & error handling
- Location: `.github/workflows/telegram-bot-scheduler.yml`

### 2. **telegram-bot.yml** (ORIGINAL)
- Also works fine
- Same functionality as new one
- Location: `.github/workflows/telegram-bot.yml`

---

## Step 1: Add GitHub Secrets (Required!)

Your workflows need 4 secrets. Go to your GitHub repository:

### How to Add Secrets:
1. Click **Settings** (top right)
2. Click **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret below:

### Secret #1: SUPABASE_URL
```
Name: SUPABASE_URL
Value: https://xxxxx.supabase.co
```
(Find in Supabase Dashboard → Settings → API)

### Secret #2: SUPABASE_API_KEY
```
Name: SUPABASE_API_KEY
Value: eyJhbGc...
```
(Find in Supabase Dashboard → Settings → API → anon key)

### Secret #3: TELEGRAM_BOT_TOKEN
```
Name: TELEGRAM_BOT_TOKEN
Value: 123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh
```
(Get from @BotFather on Telegram)

### Secret #4: TELEGRAM_NOTIFICATION_CHANNEL_ID
```
Name: TELEGRAM_NOTIFICATION_CHANNEL_ID
Value: 123456789
```
(Get your chat ID from @userinfobot on Telegram)

**All 4 should appear in your Secrets list after adding!**

---

## Step 2: Stop Running Bot Locally

Since scheduler now runs on GitHub:

```bash
# Stop the running bot (Ctrl+C if running)
# Don't run: python telegram_bot_main.py anymore

# If running in background, kill it:
pkill -f "telegram_bot_main"
```

---

## Step 3: Test It

### Manual Run (Right Now)
1. Go to GitHub → **Actions** tab
2. Click **"🤖 Telegram Bot Scheduler"** workflow
3. Click **"Run workflow"** button
4. Select **main** branch
5. Click **"Run workflow"**
6. Wait 30-60 seconds
7. Click the running job to see logs

### View Logs
1. Go to **Actions** tab
2. Click any "🤖 Telegram Bot Scheduler" run
3. Click **"Run Scheduler Check Cycle"** step
4. See full output and any errors

---

## Schedule

**Automatic runs:** Every 15 minutes at :00, :15, :30, :45

Examples:
- 00:00 - runs
- 00:15 - runs
- 00:30 - runs
- 00:45 - runs
- 01:00 - runs
... continues 24/7

### Change Schedule (Optional)

Edit `.github/workflows/telegram-bot-scheduler.yml`:

Find:
```yaml
- cron: '*/15 * * * *'
```

Options:
- **Every 10 min:** `*/10 * * * *`
- **Every 30 min:** `*/30 * * * *`
- **Every hour:** `0 * * * *`
- **Daily 9 AM UTC:** `0 9 * * *`

---

## FAQ

**Q: Where does it run?**
A: GitHub's servers (ubuntu-latest). Not your computer!

**Q: Do I need to keep my PC on?**
A: No! GitHub runs it for you 24/7.

**Q: What if I get an error?**
A: Check GitHub Actions logs for the error message. Usually it's a wrong secret or missing config.json.

**Q: Cost?**
A: Free! GitHub includes 2000 minutes/month. Your bot uses ~5 min per run.

**Q: How do I test?**
A: Go to Actions → "Run workflow" button → runs immediately.

---

## Common Issues & Solutions

### Issue: "Failed to load config"
**Solution:** Make sure `config.json` exists in your repository

### Issue: "Failed to connect to Supabase"
**Solution:** Check SUPABASE_URL and SUPABASE_API_KEY secrets are correct

### Issue: "Telegram error"
**Solution:** Check TELEGRAM_BOT_TOKEN is correct

### Issue: No runs appearing
**Solution:** GitHub Actions might be disabled. Go to Actions tab and enable it.

---

## Summary

✅ Scheduler configured
✅ Runs every 15 minutes automatically
✅ 24/7 monitoring (no computer needed)
✅ Full logging available
✅ Can manually trigger anytime

### Next Steps:
1. Add 4 GitHub Secrets
2. Click "Run workflow" to test
3. Check logs for success
4. Stop running bot locally
5. Done! It runs automatically now

---

## Monitoring

### How to know it's working:
- ✅ Check GitHub Actions logs (show successful runs)
- ✅ Receive Telegram notifications for new listings
- ✅ See "✅ SCHEDULER CHECK COMPLETED SUCCESSFULLY" in logs

### How to check:
1. Go to **Actions** tab
2. Click **"🤖 Telegram Bot Scheduler"**
3. See list of past runs with status (✓ or ✗)

That's it! Your scheduler is now automated! 🚀
