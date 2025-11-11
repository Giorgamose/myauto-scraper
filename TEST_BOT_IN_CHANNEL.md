# 🤖 Testing Bot in Telegram Channel

Your channel chat ID: `-1003275746217`

This guide will help you test the bot by sending commands in your channel.

---

## Step 1: Add Bot to Your Channel

### A. Get Bot Username

Your bot username is shown in `.env.local`:
```
TELEGRAM_BOT_TOKEN=8531271294:AAH...
```

The number before the colon (8531271294) is your bot ID. The username should be something like `@myauto_search_bot_XXX`.

### B. Add Bot to Channel

**In Telegram:**

1. Open your channel
2. Click the **channel name** at the top → "Members"
3. Click **"Add Member"** or **"Add Bot"**
4. Search for your bot username (e.g., `@myauto_search_bot`)
5. Click to add it
6. Make sure bot has permission: **"Post Messages"** ✅

---

## Step 2: Verify Bot Has Correct Permissions

1. Open your channel
2. Click channel name → **"Administrators"**
3. Find your bot in the list
4. Check these permissions:
   - ✅ Post Messages
   - ✅ Edit Messages
   - ✅ Delete Messages
   - ✅ View Messages

---

## Step 3: Restart Bot with Channel ID

The bot will now send notifications to `-1003275746217`.

**Make sure bot is running:**

```bash
python telegram_bot_main.py
```

You should see in terminal:
```
[*] Bot is now listening for messages...
[*] Starting Telegram Bot polling...
```

---

## Step 4: Send Commands in Your Channel

**In Telegram, in your channel:**

Send these commands one by one:

### Test 1: /help
```
/help
```

**Expected:** Bot responds with help menu showing all available commands.

**Terminal should show:**
```
[*] Message from chat -1003275746217: /help
[OK] Message sent to chat -1003275746217
```

### Test 2: /status
```
/status
```

**Expected:** Bot shows statistics (number of users, subscriptions, etc.)

### Test 3: /set (with a real MyAuto URL)

```
/set https://www.myauto.ge/ka/search?catID=2&modelID[]=322
```

(Use an actual MyAuto.ge search URL)

**Expected:** Bot confirms search criteria saved

### Test 4: /list
```
/list
```

**Expected:** Bot shows all saved search URLs

---

## Common Issues in Channel

### Issue: Bot doesn't respond in channel

**Reasons:**
1. Bot is not added to the channel
2. Bot doesn't have "Post Messages" permission
3. Channel is a **supergroup** (requires different handling)
4. Bot crashed or isn't running

**Fix:**
1. Verify bot is in member list: Open channel → Members → Search for bot
2. Check permissions: Click bot name → Make sure "Post Messages" is ✅
3. Check if bot is running: Look for logs in terminal
4. Restart bot if needed: `Ctrl+C` then `python telegram_bot_main.py`

### Issue: "I see the message but bot doesn't respond"

**This means:**
- Bot received the message ✅
- But failed to process it ❌

**Check terminal for error messages:**
```
[ERROR] ...
```

Share the error message and we can fix it.

### Issue: Bot responds but message is deleted immediately

**This might mean:**
- Bot doesn't have permission to post messages
- Channel has auto-delete enabled

**Fix:**
- Give bot "Post Messages" permission
- Check channel settings for auto-delete

---

## Testing Checklist

- [ ] Bot username known (e.g., `@myauto_bot`)
- [ ] Bot added to channel `-1003275746217`
- [ ] Bot has "Post Messages" permission ✅
- [ ] Bot is running: `python telegram_bot_main.py`
- [ ] Sent: `/help` in channel
- [ ] Saw log: `[*] Message from chat -1003275746217: /help`
- [ ] Saw log: `[OK] Message sent to chat -1003275746217`
- [ ] Bot responded with help menu in channel
- [ ] Tested other commands: `/status`, `/set`, `/list`

---

## Next Steps

Once `/help` works in channel:

1. **Save a search URL:**
   ```
   /set https://www.myauto.ge/ka/search?catID=2
   ```

2. **Verify it's saved:**
   ```
   /list
   ```

3. **Wait for notifications:**
   - Bot checks every 15 minutes by default
   - When new listings found, bot sends message in channel
   - You'll see: `🆕 NEW LISTINGS`

---

## Debug Commands (in Terminal)

If having issues, run these:

### Check bot is responding to Telegram:
```bash
python test_bot_token.py
```

Should show: `✅ BOT TOKEN IS VALID AND WORKING`

### Check Supabase connection:
```bash
python diagnose_supabase.py
```

Should show: `[OK] SUPABASE CONNECTION SUCCESSFUL`

### View recent logs:
```bash
# On Windows - last 50 lines
python telegram_bot_main.py 2>&1 | tail -50
```

---

## Important Notes

- Channel ID `-1003275746217` will receive all notifications
- Bot checks subscriptions every 15 minutes (default)
- Bot needs internet connection to work
- Bot token must be valid (test with `python test_bot_token.py`)
- Supabase connection must work (test with `python diagnose_supabase.py`)

---

## Example Full Test Session

```
You send in channel: /help

Bot responds:
🚗 MyAuto Search Bot

This bot helps you monitor MyAuto.ge car listings...

Available Commands:
/set <url>
  Save a MyAuto search URL to monitor
/list
  Show all your saved searches
...

---

Terminal shows:
[*] Message from chat -1003275746217: /help
[OK] Message sent to chat -1003275746217
```

If you see this, **bot is working!** ✅
