# Channel Notifications - Quick Start Guide

## What's New?

The bot now supports sending all periodic search results to a Telegram **channel** instead of individual user chats. Perfect for team monitoring!

## How to Set Up Channel Notifications

### Step 1: Create/Prepare Your Channel

1. Open Telegram
2. Create a new channel (or use existing one)
3. Name it something like: `@CarSearchResults` or `MyAuto Listings`
4. Make it private or public (your choice)

### Step 2: Add Your Bot as Admin

1. Go to your channel
2. Click channel name → **Members** → **Add member**
3. Search for your bot (the one you created with @BotFather)
4. Add it and make it an **Admin**

### Step 3: Get Your Channel ID

1. Open Telegram
2. Go to **@userinfobot**
3. Send `/start` to see your personal chat ID
4. Go back to your channel
5. Send any message in the channel
6. Go to **@userinfobot** → Forward the message from your channel
7. The bot will reply with your **channel ID** (looks like: `-100123456789`)

### Step 4: Add Channel ID to GitHub Actions

1. Go to your GitHub repo: https://github.com/Giorgamose/myauto-scraper
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. **Name:** `TELEGRAM_NOTIFICATION_CHANNEL_ID`
5. **Value:** Your channel ID from Step 3 (e.g., `-100123456789`)
6. Click **Add secret**

### Step 5: Test It

1. Go to **Actions** tab
2. Click **Telegram Bot - Continuous Monitoring**
3. Click **Run workflow** button
4. Wait for execution to complete
5. Check your channel for notifications!

## How It Works

### Before (Individual Chat)
```
Bot → User1's Chat (notification)
Bot → User2's Chat (notification)
Bot → User3's Chat (notification)
```

### After (Channel)
```
Bot → Shared Channel (all notifications aggregated)
       ↓
     User1 sees
     User2 sees
     User3 sees
```

## Configuration Examples

### Local Testing (.env.local)

**Option 1: Individual Notifications (Default)**
```bash
# Don't set this variable, or leave it empty
TELEGRAM_NOTIFICATION_CHANNEL_ID=
```

**Option 2: Send to Channel**
```bash
TELEGRAM_NOTIFICATION_CHANNEL_ID=-100123456789
```

### GitHub Actions

Just add the secret and it will automatically be used!

## Switching Back to Individual Notifications

If you want to go back to individual user notifications:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Find `TELEGRAM_NOTIFICATION_CHANNEL_ID`
3. Click the **Delete** button
4. Done! Bot will send notifications to individual chats again

## Troubleshooting

### ❌ "Failed to send notification to channel"

**Possible causes:**
- Channel ID is incorrect
- Bot is not admin in the channel
- Bot was removed from the channel

**Solutions:**
- Verify channel ID again using @userinfobot
- Re-add bot as admin to the channel
- Check bot hasn't been blocked

### ❌ "Notifications still going to individual chats"

**Possible causes:**
- TELEGRAM_NOTIFICATION_CHANNEL_ID secret not set
- GitHub workflow not reloaded

**Solutions:**
- Double-check the secret is added and spelled correctly
- Re-run the workflow manually (not just waiting for cron)

### ❌ "Can't find my channel ID"

**Detailed steps:**
1. Send a message in your channel yourself
2. Open @userinfobot in Telegram
3. Send `/start` to see your format
4. Go back and **forward** that message to @userinfobot
5. The bot will show you the exact channel ID

## Benefits of Channel Notifications

✅ **Team Monitoring** - Multiple people see the same listings
✅ **Centralized** - All notifications in one place
✅ **Shareable** - Easy to add team members to channel
✅ **No Spam** - Direct messages don't get cluttered
✅ **Organized** - Keep your chat clean

## FAQ

**Q: Can I have both individual and channel notifications?**
A: No, it's either/or. Set the channel ID to get channel notifications, or leave it empty for individual chats.

**Q: What if I have multiple channels?**
A: Currently supports one channel. For multiple channels, you'd need to run multiple bot instances.

**Q: Do I need to change my subscriptions?**
A: No! Your `/set`, `/list`, `/reset` subscriptions work the same way. Only the notification destination changes.

**Q: Can I make my channel public?**
A: Yes! Both public and private channels work the same way.

**Q: What about privacy?**
A: With a channel, all notifications are in one place anyone with access to the channel can see. Make sure the channel visibility matches your privacy needs.

---

**Happy monitoring! 🚀**
