# 🚀 GitHub Actions Setup - Continuous Bot Monitoring

Run your Telegram bot automatically on GitHub! The bot will check subscriptions every 15 minutes and send notifications.

---

## What This Does

✅ Runs bot check cycle **every 15 minutes** (24/7)
✅ Fetches new listings from saved searches
✅ Sends notifications to your Telegram channel
✅ Logs all activity for debugging
✅ **FREE** - uses GitHub's free runners

---

## Step 1: Set Up GitHub Secrets

Your bot needs credentials stored securely in GitHub.

### A. Go to Your Repository Settings

1. Go to: **https://github.com/YOUR_USERNAME/myauto-scraper/settings/secrets/actions**
2. Click **"New repository secret"**

### B. Add These Secrets

**Secret 1: SUPABASE_URL**
- Name: `SUPABASE_URL`
- Value: (copy from your `.env.local`)
  ```
  https://efohkibukutjvrrhhxdn.supabase.co
  ```
- Click **"Add secret"**

**Secret 2: SUPABASE_API_KEY**
- Name: `SUPABASE_API_KEY`
- Value: (copy from your `.env.local`)
  ```
  sb_secret_AQsUE2fqqZnArFz_WV6qBg_L4kPjXwt
  ```
- Click **"Add secret"**

**Secret 3: TELEGRAM_BOT_TOKEN**
- Name: `TELEGRAM_BOT_TOKEN`
- Value: (from your `.env.local`)
  ```
  8531271294:AAH7Od2UldndVviXAPxFXxxolqIjodW4BY4
  ```
- Click **"Add secret"**

**Secret 4: TELEGRAM_CHAT_ID**
- Name: `TELEGRAM_CHAT_ID`
- Value: (from your `.env.local`)
  ```
  -1003275746217
  ```
- Click **"Add secret"**

---

## Step 2: Verify GitHub Secrets Are Set

1. Go to: **https://github.com/YOUR_USERNAME/myauto-scraper/settings/secrets/actions**
2. You should see 4 secrets listed:
   - ✅ SUPABASE_URL
   - ✅ SUPABASE_API_KEY
   - ✅ TELEGRAM_BOT_TOKEN
   - ✅ TELEGRAM_CHAT_ID

---

## Step 3: Push Workflow to GitHub

The workflow file `.github/workflows/telegram-bot.yml` is already created locally. Now:

1. **Push to GitHub:**
   ```bash
   git add .github/workflows/telegram-bot.yml
   git commit -m "Add: GitHub Actions workflow for Telegram bot"
   git push origin main
   ```

2. **Verify it was added:**
   - Go to: **https://github.com/YOUR_USERNAME/myauto-scraper/actions**
   - You should see: **"Telegram Bot - Continuous Monitoring"** workflow

---

## Step 4: Test the Workflow

### Option A: Manual Trigger (Recommended First)

1. Go to: **https://github.com/YOUR_USERNAME/myauto-scraper/actions**
2. Click: **"Telegram Bot - Continuous Monitoring"**
3. Click: **"Run workflow"** → **"Run workflow"**
4. Watch it run!

---

## Pricing (FREE!)

✅ **GitHub Actions is FREE** for public repositories!

Free limits:
- **2,000 actions minutes/month** (per account)
- **Every 15 min:** ~2,880 runs/month = ~48 hours
- **Remaining:** 1,952 minutes for other workflows

For your use case, **the free plan is more than enough!** 🎉

---

## Next Steps

✅ Set up GitHub Secrets
✅ Push workflow file to GitHub (.github/workflows/telegram-bot.yml)
✅ Test with manual trigger
✅ Receive notifications in Telegram

That's it! Your bot is now running 24/7 on GitHub! 🚀

