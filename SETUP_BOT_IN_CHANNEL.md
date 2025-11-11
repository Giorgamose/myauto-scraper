# 🤖 Setup Bot to Work in Channel -1003275746217

Configure the bot so you can send commands directly in your channel and receive notifications there.

---

## Step 1: Make Bot an Admin in Channel

**In Telegram:**

1. Open your **channel** (-1003275746217)
2. Click the **channel name** at the top
3. Click **"Administrators"**
4. Click **"Add Administrator"**
5. Search for: **@myauto_listining_bot**
6. Select it to add as admin

---

## Step 2: Grant Bot Permissions

After adding the bot as admin, **click on the bot** in the Administrators list.

Make sure these permissions are **ENABLED** (blue checkmark):

- ✅ **Post Messages** - Bot can send messages
- ✅ **Edit Messages** - Bot can edit sent messages
- ✅ **Delete Messages** - Bot can delete old messages
- ✅ **Read Messages** - Bot can see channel messages (IMPORTANT)
- ✅ **Pin Messages** - Optional, not needed
- ✅ **Manage Topics** - Optional, not needed

**The most important is "Read Messages"** - without this, bot won't see your commands.

---

## Step 3: Verify Bot Settings in Code

The bot is already configured to accept commands from any chat ID, including channels.

Check that `.env.local` has:

```
TELEGRAM_CHAT_ID=-1003275746217
```

This tells the bot to send notifications to your channel.

---

## Step 4: Restart Bot

In your terminal:

```bash
Ctrl+C  # Stop the bot if running
python telegram_bot_main.py  # Start it again
```

You should see:

```
[*] Bot is now listening for messages...
[*] Starting Telegram Bot polling...
```

---

## Step 5: Test Commands in Channel

Now send commands **in your channel** (-1003275746217):

### Test 1: /help

Send in channel:
```
/help
```

**Watch terminal** for:
```
[*] Message from chat -1003275746217: /help
[OK] Message sent to chat -1003275746217
```

If you see this, the bot is receiving messages! ✅

### Test 2: /set (Add Search)

Send in channel:
```
/set https://myauto.ge/ka/s/iyideba-motociklebi-ktm-690-smc?vehicleType=2&bargainType=0&mansNModels=105.3177&currId=1&mileageType=1&customs=1&page=1&layoutId=1
```

Bot should respond:
```
✅ Search criteria saved!

URL: https://myauto.ge/ka/s/iyideba-motociklebi-ktm-690-smc?...

I'll check this search periodically and notify you when new listings appear.
```

### Test 3: /list (View Searches)

Send in channel:
```
/list
```

Bot should show all saved searches for that channel.

### Test 4: /status (Check Stats)

Send in channel:
```
/status
```

Bot should show:
```
📊 Bot Statistics

Your Status:
• Active searches: 1

Overall Statistics:
• Active users: 1
• Total searches: 1
...
```

---

## Step 6: Wait for Notifications

Once a search is saved:

1. Bot checks for new listings **every 15 minutes** (by default)
2. When new listings are found, bot sends message in **your channel**
3. You'll see in terminal:
   ```
   [*] Sending notification to chat -1003275746217: 🆕 NEW LISTINGS
   ```

---

## Complete Checklist

- [ ] Added bot as **Admin** in channel
- [ ] Enabled **"Read Messages"** permission
- [ ] Enabled **"Post Messages"** permission
- [ ] Restarted bot: `python telegram_bot_main.py`
- [ ] Sent `/help` in channel
- [ ] Saw terminal log: `[*] Message from chat -1003275746217: /help`
- [ ] Bot responded in channel with help menu
- [ ] Sent `/set <URL>` with valid MyAuto URL
- [ ] Bot confirmed: `✅ Search criteria saved!`
- [ ] Sent `/list` and saw the URL listed
- [ ] Sent `/status` and saw bot statistics

---

## Troubleshooting

### "Bot doesn't respond in channel"

**Check 1: Is bot an admin?**
- Channel → Administrators → Search for @myauto_listining_bot
- Should be there with blue checkmark

**Check 2: Does bot have "Read Messages" permission?**
- Channel → Administrators → Click bot
- Make sure "Read Messages" is ✅

**Check 3: Is bot running?**
- Terminal should show: `[*] Bot is now listening for messages...`
- If not, start it: `python telegram_bot_main.py`

**Check 4: Do you see logs in terminal?**
- Send `/help` in channel
- Terminal should show: `[*] Message from chat -1003275746217: /help`
- If NO logs, bot isn't receiving messages - check steps 1-2

### "Bot responds but says 'Invalid URL'"

Make sure your URL:
1. Starts with `https://`
2. Contains `myauto.ge`
3. Contains either `/search?` or `/s/`
4. Has proper format: `https://myauto.ge/ka/search?...` or `https://myauto.ge/ka/s/...`

Example of valid URLs:
```
https://myauto.ge/ka/search?catID=2&modelID[]=322
https://myauto.ge/ka/s/iyideba-motociklebi-ktm-690-smc?vehicleType=2
https://www.myauto.ge/ka/search?...
```

### "Bot doesn't send notifications to channel"

Check:
1. `.env.local` has: `TELEGRAM_CHAT_ID=-1003275746217`
2. Bot has "Post Messages" permission ✅
3. Bot is running continuously (don't close the terminal)
4. Wait 15+ minutes for first check cycle
5. Check terminal logs for:
   ```
   [*] Checking subscription...
   [*] Found N new listings
   [*] Sending notification to chat -1003275746217
   ```

---

## How It Works

1. **You send commands in channel** (via `/set`, `/list`, etc.)
2. **Bot receives them** (because it's an admin with "Read Messages")
3. **Bot processes commands** and responds in the channel
4. **Bot checks searches periodically** (every 15 minutes)
5. **When new listings found**, bot sends notification to channel
6. **You get notified** in the channel with new car listings!

---

## Next Steps After Setup

Once the bot is working in your channel:

1. Add more searches:
   ```
   /set <another-myauto-url>
   ```

2. Verify they're all saved:
   ```
   /list
   ```

3. Check bot status:
   ```
   /status
   ```

4. Bot will monitor all of them and send notifications when matches are found

---

## Important Notes

- The channel chat ID `-1003275746217` is where:
  - You send `/set` commands to add searches
  - You receive notifications when new listings found
- Bot checks every 15 minutes (configurable in code)
- Notifications are sent to the **same channel**
- All searches for this channel are stored in Supabase
- Bot runs continuously (keep terminal open)

That's it! The bot is now fully configured for your channel. 🚀
