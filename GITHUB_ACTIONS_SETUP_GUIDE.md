# GitHub Actions Setup Guide - Telegram Bot Periodic Execution

This guide explains how to run the Telegram bot's periodic search checks on GitHub Actions instead of locally.

## Overview

The bot will automatically run searches every 15 minutes on GitHub's servers. You don't need to keep your local machine running!

- **Runs Every:** 15 minutes (cron: `*/15 * * * *`)
- **Timeout:** 10 minutes per execution
- **Server:** GitHub's Ubuntu runners (free tier)
- **Cost:** FREE for public repos, limited free minutes for private repos

## Prerequisites

1. ✅ Your repository is already on GitHub
2. ✅ The workflow file exists at `.github/workflows/telegram-bot.yml`
3. ✅ You need access to modify repository settings

## Step 1: Add Repository Secrets

GitHub Actions needs your credentials securely stored as **Secrets**.

### How to Add Secrets:

1. Go to your repository on GitHub: https://github.com/Giorgamose/myauto-scraper
2. Click **Settings** (gear icon at the top right)
3. On the left sidebar, click **Secrets and variables** → **Actions**
4. Click the green **New repository secret** button
5. Add each secret with the exact names below:

### Required Secrets:

Add these secrets to GitHub (copy from your `.env.local` file):

| Secret Name | Value | Where to Find |
|---|---|---|
| `SUPABASE_URL` | Your Supabase project URL | `.env.local`: `SUPABASE_URL=` |
| `SUPABASE_API_KEY` | Your Supabase API key | `.env.local`: `SUPABASE_API_KEY=` |
| `TELEGRAM_BOT_TOKEN` | Your bot token from BotFather | `.env.local`: `TELEGRAM_BOT_TOKEN=` |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID | `.env.local`: `TELEGRAM_CHAT_ID=` |

### Optional Secrets:

| Secret Name | Value | Purpose |
|---|---|---|
| `TELEGRAM_NOTIFICATION_CHANNEL_ID` | Your Telegram channel ID | Send all notifications to a channel instead of individual chats |

**⚠️ IMPORTANT:**
- Never commit `.env.local` to Git (it's in `.gitignore`)
- Secrets are encrypted and only visible to GitHub Actions
- You cannot view secrets after saving them

### Example: Adding SUPABASE_URL Secret

```
1. Secrets and variables > Actions
2. New repository secret
3. Name: SUPABASE_URL
4. Value: https://xxxxx.supabase.co
5. Add secret
```

## Step 1.5: Optional - Configure Channel Notifications

If you want all periodic search results sent to a **Telegram channel** instead of individual chats:

### Get Your Channel ID:

1. Create a Telegram channel (if you don't have one)
2. Add your bot as an admin to the channel
3. Send any message to the channel
4. Open Telegram and go to **@userinfobot**
5. Send `/start` to the bot
6. Forward the message from your channel to @userinfobot
7. The bot will show your channel ID (format: `-100xxxxxxxxxx`)
8. Add this as a secret: `TELEGRAM_NOTIFICATION_CHANNEL_ID`

### Why Use a Channel?

| Aspect | Individual Chat | Channel |
|--------|---|---|
| Notifications go to | Each user separately | One shared channel |
| Setup | Simple | Need channel admin |
| Visibility | Private to each user | Public/shared |
| Best for | Personal monitoring | Team/shared monitoring |

## Step 2: Enable GitHub Actions

1. Go to **Settings** → **Actions** → **General**
2. Under "Actions permissions", select **Allow all actions and reusable workflows**
3. Click **Save**

## Step 3: Verify the Workflow

1. Go to **Actions** tab in your repository
2. You should see "Telegram Bot - Continuous Monitoring" workflow
3. Click on it to view details

## Step 4: Test Manual Trigger (Optional)

Before waiting for automatic execution, test it manually:

1. Go to **Actions** tab
2. Click **Telegram Bot - Continuous Monitoring** on the left
3. Click the **Run workflow** dropdown button
4. Click **Run workflow** again to confirm
5. Watch the execution in real-time!

## How It Works

### Automatic Execution

```
Every 15 minutes:
├─ Check all user subscriptions
├─ Fetch listings from MyAuto.ge
├─ Compare with seen listings
├─ Send notifications for new listings
└─ Update database
```

### Workflow Steps:

1. **Checkout code** - Pull latest code from main branch
2. **Setup Python** - Install Python 3.11
3. **Install dependencies** - Install from requirements.txt
4. **Create .env file** - Load secrets into environment
5. **Run bot check cycle** - Execute one complete search cycle
6. **Upload logs** - Save logs on failure

## Monitoring Execution

### View Logs:

1. Go to **Actions** tab
2. Click the latest workflow run
3. Click **Run bot check cycle** step to see output
4. Look for:
   - ✅ `✅ Bot check cycle completed successfully` = All good!
   - ❌ `❌ Error:` = Something failed, check error message

### Example Successful Log Output:

```
Starting bot check cycle...
============================================================
[*] Configuration loaded
[*] Initializing Supabase database...
[OK] Database initialized
[*] Initializing scraper...
[OK] Scraper initialized
[*] Initializing bot backend...
[OK] Bot backend initialized
[*] Initializing notification manager...
[OK] Notification manager initialized
[*] Creating scheduler...
[OK] Scheduler created
============================================================
[*] Running periodic check cycle...
============================================================
============================================================
[+] Found 3 new listings
[OK] Notifications sent
============================================================
✅ Bot check cycle completed successfully
============================================================
```

## Changing the Schedule

To run at different intervals, edit `.github/workflows/telegram-bot.yml`:

```yaml
on:
  schedule:
    # Change cron expression
    - cron: '*/30 * * * *'  # Every 30 minutes
    - cron: '0 * * * *'     # Every hour
    - cron: '0 6,12,18 * * *'  # At 6am, 12pm, 6pm UTC
```

**Cron Format:** `minute hour day month weekday`

Common patterns:
- `*/15 * * * *` = Every 15 minutes ⏱️
- `*/30 * * * *` = Every 30 minutes
- `0 * * * *` = Every hour
- `0 6 * * *` = Daily at 6am UTC
- `0 8-22/2 * * *` = Every 2 hours, 8am-10pm UTC

## Troubleshooting

### ❌ "Workflow file not found"
- Ensure `.github/workflows/telegram-bot.yml` is committed and pushed
- Check file permissions

### ❌ "Secret not set"
- Verify exact secret names match (case-sensitive)
- Re-add secrets if issues persist

### ❌ "Database connection failed"
- Verify `SUPABASE_URL` and `SUPABASE_API_KEY` are correct
- Check if Supabase project is still active
- Verify table names (user_subscriptions, user_seen_listings, bot_events)

### ❌ "Scraper timeout"
- MyAuto.ge might be slow or blocking requests
- Increase timeout in workflow (change timeout-minutes: 10)
- Check MyAuto.ge status

### ❌ "Playwright initialization error"
- Ensure Playwright browsers are installed: add to workflow:
  ```yaml
  - name: Install Playwright browsers
    run: python -m playwright install --with-deps chromium
  ```

## Disabling the Workflow

To temporarily stop automatic execution:

1. Go to **Actions** tab
2. Click **Telegram Bot - Continuous Monitoring**
3. Click **...** (three dots) → **Disable workflow**
4. Workflow won't run until re-enabled

## Local vs. GitHub Actions

| Aspect | Local | GitHub Actions |
|--------|-------|---|
| Setup Time | Immediate | One-time secrets setup |
| Cost | 💰 Your electricity | 🆓 Free (public repo) |
| Uptime | Only when PC running | 24/7 (GitHub's servers) |
| Logs | In your terminal | In GitHub Actions tab |
| Control | Full | Via GitHub interface |

## Next Steps

1. ✅ Add all 4 secrets to GitHub
2. ✅ Enable GitHub Actions
3. ✅ Test with manual trigger
4. ✅ Monitor logs for 24 hours
5. ✅ Confirm notifications are being sent
6. ✅ You can now close your local bot!

## Support

If something goes wrong:

1. Check the detailed error in the **Actions** tab
2. Verify all secrets are correctly set
3. Test locally first: `python telegram_bot_main.py`
4. Check bot logs for more details
5. Review Supabase database for data

---

**You're all set! Your bot is now running 24/7 on GitHub Actions! 🚀**
