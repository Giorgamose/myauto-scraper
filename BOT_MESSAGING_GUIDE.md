# 🤖 How to Message the Bot - Complete Guide

**Your bot is running but you need to message it correctly.** Here's how.

---

## 📱 Step 1: Find Your Bot Username

When you created the bot with @BotFather, you gave it a **username** (not a chat ID).

### Check Your Bot Username

**Look at the message from @BotFather** where it said something like:

```
Done! Congratulations on your new bot. You will find it at:
https://t.me/your_bot_username_here
```

Your bot username is: **`your_bot_username_here`**

### If You Don't Remember

1. Open **@BotFather** in Telegram
2. Send: `/mybots`
3. Select your bot
4. You'll see it at the top: `https://t.me/BOTNAME`
5. That's your bot's username

---

## 💬 Step 2: Message Your Bot

### Method 1: Direct Search (Recommended)

1. **Open Telegram**
2. **Tap the search icon** (top right)
3. **Type your bot's username** (with or without @)
4. **Click your bot** in the results
5. **Tap "START"** (blue button at bottom)
6. **Send:** `/help`

### Method 2: Direct Link

If you have the link from @BotFather:

1. Click: https://t.me/BOTNAME (replace BOTNAME with your bot's username)
2. Click "START"
3. Send: `/help`

### Method 3: Terminal

You can test via curl to verify bot is working:

```bash
# Replace TOKEN with your actual token from .env.local
TOKEN=8531271294:AAH7Od2UldndVviXAPxFXxxolqIjodW4BY4

# Test bot connection
curl "https://api.telegram.org/bot$TOKEN/getMe"

# Should see your bot username in response
```

---

## ✅ Step 3: Verify Bot is Receiving Messages

### Check Terminal Logs

While the bot is running, **look at the terminal** where you started the bot.

When you send a message, you should see:

```
[*] Message from chat 123456789: /help
[OK] Message sent to chat 123456789
```

### If You See These Logs

✅ **Bot is working correctly!** Proceed to Step 4.

### If You DON'T See These Logs

❌ **Messages aren't reaching the bot.** Go to Step 4 (debugging).

---

## 🔧 Step 4: Debug - Messages Not Received

### Issue: "No logs appear when I send messages"

**This means your messages aren't reaching the bot. Check:**

#### A. Bot Token is Correct

```bash
python diagnose_supabase.py
```

Check for: `[OK] SUPABASE CONNECTION SUCCESSFUL`

#### B. Test Bot Token Directly

```bash
# Windows PowerShell or Command Prompt:
python -c "import requests; token='8531271294:AAH7Od2UldndVviXAPxFXxxolqIjodW4BY4'; r=requests.post(f'https://api.telegram.org/bot{token}/getMe'); print(r.json())"
```

Should return something like:
```json
{
    "ok": true,
    "result": {
        "id": 8531271294,
        "is_bot": true,
        "first_name": "MyAuto Bot",
        "username": "myauto_search_bot"
    }
}
```

If it shows `"ok": false`, your token is **WRONG or EXPIRED**.

#### C. Check Internet Connection

```bash
# Test Telegram API is reachable
ping api.telegram.org
```

Should show response (not "Unreachable").

#### D. Check You're Messaging the RIGHT Bot

Make sure you're messaging **exactly the bot created with this token**.

From the test above, look at `"username"`. That's the bot you need to message in Telegram.

#### E. Wait a Moment

Sometimes Telegram takes 1-2 seconds to deliver messages. The bot polls every 30 seconds by default.

---

## 🎯 Step 5: Once Bot is Receiving Messages

If you see logs like `[*] Message from chat XXXXX`, test these commands:

### Test 1: /help
```
Send in Telegram: /help
Expect: Bot menu with all commands
```

### Test 2: /status
```
Send in Telegram: /status
Expect: Bot statistics (users, subscriptions)
```

### Test 3: /set command
```
Send in Telegram: /set https://www.myauto.ge/ka/search?...
Expect: "✅ Search criteria saved!"
```

Replace the URL with an actual MyAuto.ge search URL.

### Test 4: /list
```
Send in Telegram: /list
Expect: List of your saved searches
```

---

## 🆘 Common Issues & Solutions

### Issue: "I can find the bot but clicking START does nothing"

**Solution:**
- The bot might have crashed. Check terminal for errors.
- Stop bot (Ctrl+C) and restart it.
- Wait 5 seconds, then try messaging again.

### Issue: "I see the bot but it's not my bot (wrong name)"

**Solution:**
- You're messaging the wrong bot!
- Get the correct username from @BotFather's `/mybots` list
- Search for the correct username in Telegram

### Issue: "Bot token test shows 'ok': false"

**Solution:**
1. Go back to @BotFather
2. Send: `/mybots`
3. Click your bot
4. Click "Edit Bot"
5. Click "Edit Token"
6. Create a new token
7. Update `.env.local` with the new token
8. Restart bot: `python telegram_bot_main.py`

### Issue: "Still no messages after all this"

**Check your .env.local** for `TELEGRAM_BOT_TOKEN`:

```bash
grep TELEGRAM_BOT_TOKEN .env.local
```

Should show:
```
TELEGRAM_BOT_TOKEN=8531271294:AAH7Od2UldndVviXAPxFXxxolqIjodW4BY4
```

If it's empty or different, update it and restart.

---

## 🚀 Quick Checklist

Before assuming the bot is broken:

- [ ] I found my bot's username from @BotFather
- [ ] I'm messaging the CORRECT bot in Telegram
- [ ] I can see terminal logs when I send messages
- [ ] I sent `/help` and the bot didn't respond (or did it?)
- [ ] I tried restarting the bot with Ctrl+C and `python telegram_bot_main.py`
- [ ] I checked my internet connection works
- [ ] I verified bot token with the `python -c` test above

---

## 📞 Still Need Help?

Share these when asking for help:

1. **Output of bot token test:**
   ```bash
   python -c "import requests; token='YOUR_TOKEN'; r=requests.post(f'https://api.telegram.org/bot{token}/getMe'); print(r.json())"
   ```

2. **Output of bot startup:**
   ```bash
   python telegram_bot_main.py
   ```
   (First 20 lines)

3. **Your bot's username** from @BotFather

4. **Whether you see logs in terminal** when sending `/help`

---

## ✅ Success Indicators

When everything works, you should see:

**In Telegram:**
```
You: /help

Bot: 🚗 MyAuto Search Bot
    This bot helps you monitor MyAuto.ge car listings...

    Available Commands:
    /set <url>
    /list
    /clear
    /status
    /help
```

**In Terminal:**
```
[*] Message from chat 123456789: /help
[OK] Message sent to chat 123456789
```

If you see both of these, **your bot is working!** 🎉

---

## 🎊 Next: Use the Bot

Once you confirm the bot responds to `/help`:

1. Get a MyAuto.ge search URL (set your filters, copy the URL)
2. Send: `/set <paste-the-URL>`
3. Send: `/list` to verify it's saved
4. Wait 15 minutes for first check (default interval)
5. Bot will send notifications when new listings appear

That's it! 🚀
