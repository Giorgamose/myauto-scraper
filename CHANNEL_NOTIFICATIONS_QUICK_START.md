# Telegram Notifications Setup - Quick Start

## Simple Setup (Recommended for Personal Use)

The simplest way to use GitHub Actions is to send notifications to **your personal Telegram chat**.

### Step 1: Get Your Telegram Chat ID

1. Open Telegram
2. Go to **@userinfobot**
3. Send `/start`
4. The bot will show you your chat ID (looks like: `1234567890`)
5. Copy this ID

### Step 2: Add to GitHub Actions

1. Go to your repository: https://github.com/Giorgamose/myauto-scraper
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. **Name:** `TELEGRAM_NOTIFICATION_CHANNEL_ID`
5. **Value:** Your chat ID from Step 1 (just the number, e.g., `1234567890`)
6. Click **Add secret**

### Step 3: Test It

1. Go to **Actions** tab
2. Click **Telegram Bot - Continuous Monitoring**
3. Click **Run workflow** button
4. Check your Telegram personal chat for results!

---

## Advanced Setup (For Teams or Channels)

If you want to send to a **Telegram channel** or **group chat** instead:

### For Telegram Channels:

1. Create a channel (e.g., `@CarSearchResults`)
2. Add your bot as admin
3. Send a message in the channel
4. Go to **@userinfobot** → Forward the channel message
5. Copy the channel ID (format: `-100xxxxxxxxxxxxx`)
6. Add to GitHub Actions as `TELEGRAM_NOTIFICATION_CHANNEL_ID`

### For Telegram Group Chats:

1. Create a group with your bot
2. Add your bot to the group
3. Forward any group message to **@userinfobot**
4. Copy the group ID (usually negative number like `-1234567890`)
5. Add to GitHub Actions as `TELEGRAM_NOTIFICATION_CHANNEL_ID`

---

## Configuration Summary

| Setup Type | Value Type | Where Notifications Go |
|---|---|---|
| **Personal Chat** (Simple) | Chat ID (e.g., `1234567890`) | Your personal Telegram chat |
| **Group Chat** | Group ID (e.g., `-1234567890`) | Shared group with others |
| **Channel** (Broadcast) | Channel ID (e.g., `-100xxxxx`) | Public/private Telegram channel |

---

## How It Works

```
GitHub Actions (every 15 min)
  ↓
  Checks MyAuto.ge for new listings
  ↓
  Finds new listings matching subscriptions
  ↓
  Sends notification to TELEGRAM_NOTIFICATION_CHANNEL_ID
  ↓
  You see it in Telegram!
```

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
