# Production Deployment Guide

## 🚀 Quick Start (5 Minutes)

### Step 1: Create GitHub Repository
If you don't have one yet:
1. Go to https://github.com/new
2. Repository name: `myauto-scraper`
3. Description: `MyAuto.ge Car Listing Monitor with Turso Database`
4. Private or Public (your choice)
5. Click "Create repository"

### Step 2: Add Remote & Push
```bash
cd "c:\Users\gmaevski\Documents\MyAuto Listening Scrapper"

# Add your repository URL
git remote add origin https://github.com/YOUR_USERNAME/myauto-scraper.git

# Or if using SSH:
# git remote add origin git@github.com:YOUR_USERNAME/myauto-scraper.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 3: Configure GitHub Secrets
Go to: **GitHub → Your Repository → Settings → Secrets and Variables → Actions**

Create 4 new secrets:

1. **TURSO_DATABASE_URL**
   - Value: `libsql://your-db-name.turso.io` (from turso.tech)

2. **TURSO_AUTH_TOKEN**
   - Value: Your auth token (from turso.tech)

3. **TELEGRAM_BOT_TOKEN**
   - Value: Your Telegram bot token (from BotFather)

4. **TELEGRAM_CHAT_ID**
   - Value: Your Telegram chat ID (from your chat with the bot)

### Step 4: Enable GitHub Actions
Go to: **GitHub → Your Repository → Actions**
- Click "I understand my workflows, go ahead and enable them"

### Step 5: Test the Workflow
Go to: **GitHub → Your Repository → Actions → MyAuto Car Listing Monitor**
- Click "Run workflow" → "Run workflow" button
- Wait for it to complete (should take 1-2 minutes)
- Check the output for success/failures

---

## 📋 GitHub Secrets Setup (Detailed)

### Finding Your Turso Credentials

1. Go to https://app.turso.tech
2. Log in
3. Click your database "car-listings"
4. In the "Overview" tab, you'll see:
   - **Database URL** → Copy this for `TURSO_DATABASE_URL`
   - **Auth Token** → Copy this for `TURSO_AUTH_TOKEN`

Example values:
```
TURSO_DATABASE_URL=libsql://car-listings-abc123.turso.io
TURSO_AUTH_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Finding Your Telegram Credentials

1. **Bot Token**: From @BotFather on Telegram
   - Send `/newbot` to @BotFather
   - Follow prompts
   - Copy the token (looks like: `123456789:ABCDefGHIjklMNOpqrsTUVwxyz`)

2. **Chat ID**: Send message to your bot, then:
   ```bash
   curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates"
   ```
   - Look for `"chat":{"id":123456789}` → That's your chat ID

Or use @userinfobot to get your chat ID easily.

---

## 🔄 How the Workflow Works

### Trigger Points
The scraper runs automatically:
- **Every 10 minutes** (set via cron: `*/10 * * * *`)
- **Manually anytime** (click "Run workflow" in GitHub Actions)

### Workflow Steps
```
1. Checkout code from GitHub
2. Setup Python 3.11
3. Cache pip packages (faster runs)
4. Install dependencies (from requirements.txt)
5. Run main.py with environment variables
6. On failure: Send Telegram error notification
7. Upload logs as artifacts
```

### Each Run Does:
1. **Scrape MyAuto.ge** for Toyota Prado listings
2. **Parse HTML** to extract 31 fields
3. **Check database** for duplicates
4. **Store in Turso** database
5. **Send Telegram notification** if matches found
6. **Log results** and cleanup

---

## 📊 What Happens After Deployment

### First 24 Hours
- ✅ 144 scraping cycles (10 minutes × 144)
- 📊 Expect: 10-20 Toyota Prado listings
- 📱 Telegram notifications for each new match
- 📈 Database grows incrementally

### First Week
- 📊 ~500-1000 scraping cycles
- 📊 Expected: 40-70 unique listings
- 📈 Pattern: Same cars appear multiple times across cycles
- 💾 Database dedups automatically

### First Month
- 📊 ~4300 scraping cycles
- 📊 Expected: 200-300 unique listings
- 💡 Enough data to analyze:
  - Price trends
  - Availability patterns
  - Model/year distribution

---

## ✅ Verification Checklist

After deployment, verify each component:

### 1. GitHub Actions Workflow
- [ ] Created GitHub repository
- [ ] Pushed code to `main` branch
- [ ] Workflow file exists: `.github/workflows/scrape.yml`
- [ ] Actions tab shows latest run
- [ ] First manual run succeeded

### 2. GitHub Secrets
- [ ] 4 secrets created (TURSO_DATABASE_URL, TURSO_AUTH_TOKEN, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
- [ ] All secrets are non-empty
- [ ] No typos in secret names

### 3. Scraper Execution
- [ ] GitHub Actions run completed without errors
- [ ] Check run logs show "Run car listing monitor" step succeeded
- [ ] Database received data (check next step)

### 4. Database Verification
From your local machine:
```bash
# Set environment variables
$env:TURSO_DATABASE_URL = "your-url"
$env:TURSO_AUTH_TOKEN = "your-token"

# Test connection
python test_db_connection.py

# View data
python view_database.py
```

Expected output:
- ✅ "Connected to Turso database"
- ✅ Record count > 0 (after first run)
- ✅ Toyota Prado listings shown

### 5. Telegram Notifications
- [ ] Received notification from your bot
- [ ] Notification shows listing details
- [ ] Phone number visible
- [ ] Price in correct range (11,000-18,000 GEL)

---

## 🔧 Troubleshooting Deployment

### Issue: "Workflow not triggered"
**Solution**: GitHub Actions might be disabled
- Go to: Settings → Actions → General
- Select: "Allow all actions and reusable workflows"

### Issue: "Secrets not found" error
**Solution**: Check secret names match exactly
- `TURSO_DATABASE_URL` (not `turso_database_url`)
- `TURSO_AUTH_TOKEN` (not `turso_auth_token`)
- `TELEGRAM_BOT_TOKEN` (not `telegram_bot_token`)
- `TELEGRAM_CHAT_ID` (not `telegram_chat_id`)

### Issue: "Connection timeout" in workflow
**Solution**: Usually temporary; GitHub Actions will retry
- Check internet connectivity
- Verify credentials are correct
- Try manual workflow run again

### Issue: No Telegram notifications
**Solution**: Check bot is running
- Verify bot token is correct
- Verify chat ID is correct (use @userinfobot)
- Check Telegram bot privacy settings allow messages

### Issue: No data in database
**Solution**: Workflow might not have run yet
- GitHub Actions runs every 10 minutes
- Wait 10 minutes and check again
- Or trigger manually: Actions → MyAuto Car Listing Monitor → Run workflow

---

## 📈 Monitoring Production

### Daily Checks
```bash
# Every morning, check for new listings:
python view_database.py
```

### Weekly Analysis
```bash
# Export to CSV for analysis:
python query_database.py
# Select option 9 (Export to CSV)
# Open in Excel to analyze prices, models, etc.
```

### Monthly Reporting
```bash
# Compare month-over-month:
# Export at start of month, end of month
# Calculate: new listings, price trends, best deals
```

### GitHub Actions Logs
Go to: **Actions → MyAuto Car Listing Monitor** → Click latest run
- View full output
- See database updates
- Verify execution time

---

## 🛡️ Security & Best Practices

### ✅ What's Already Secure
- Environment variables in GitHub Secrets (not in code)
- `.env` and `.env.local` in .gitignore (won't be pushed)
- No hardcoded credentials
- HTTPS connections to Turso
- TLS encryption to Telegram

### ⚠️ Keep These Safe
- **TURSO_AUTH_TOKEN**: Like a password, never share
- **TELEGRAM_BOT_TOKEN**: Keep private, regenerate if leaked
- **Database credentials**: Store only in GitHub Secrets

### 🚨 If Credentials Are Leaked
1. **Turso**: Go to app.turso.tech → Regenerate auth token
2. **Telegram**: Go to @BotFather → Create new token with `/newbot`
3. **Update GitHub Secrets** with new values
4. Force push (GitHub Actions will use new credentials)

---

## 📊 Expected Production Performance

### Resource Usage
- **GitHub Actions**: ~30-60 seconds per run
- **Turso Database**: Free tier includes unlimited queries
- **Telegram**: Free (up to 30 messages/second)
- **Total cost**: $0/month (free tier for all services)

### Data Retention
- **Turso**: 1 year rolling window (auto-cleanup)
- **GitHub Artifacts**: 7 days retention
- **GitHub Actions**: All logs kept

### Uptime & Reliability
- **GitHub Actions**: 99.9% uptime SLA
- **Turso**: 99.95% uptime SLA
- **Telegram**: 99.9% uptime SLA

Effectively: Production runs should fail <1% of the time

---

## 🔄 Disaster Recovery

### Lost Data?
Turso automatically backs up. Contact Turso support at app.turso.tech

### Lost Code?
GitHub is the source of truth. Can restore anytime.

### Lost Credentials?
Simply regenerate in Turso/Telegram dashboards and update GitHub Secrets.

---

## 📚 Next Steps

1. **Set up GitHub repository** (if not done)
2. **Push code**: `git push -u origin main`
3. **Configure 4 secrets** in GitHub
4. **Enable GitHub Actions**
5. **Run first manual test**
6. **Monitor first cycle** (check database, Telegram)
7. **Let it run automatically** (every 10 minutes)
8. **Check results daily**: `python view_database.py`

---

## 📞 Support & Resources

- **Turso Docs**: https://docs.turso.tech
- **GitHub Actions Docs**: https://docs.github.com/actions
- **Telegram Bot Docs**: https://core.telegram.org/bots
- **MyAuto.ge**: https://myauto.ge

---

**Version**: 1.0.0
**Last Updated**: November 9, 2025
**Status**: Ready for Production Deployment
