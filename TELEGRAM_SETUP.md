# Telegram Bot Setup Guide

**Why Telegram Instead of WhatsApp?**

✅ **Completely FREE** - No limitations whatsoever
✅ **Unlimited messages** - Send as many as you want
✅ **No business verification** - Just create a bot
✅ **Better for automation** - Built for bots and scripts
✅ **Simpler API** - Much easier to implement
✅ **Rich formatting** - HTML, Markdown, inline buttons, images
✅ **Instant setup** - Takes 5 minutes
✅ **No Sandbox limitations** - Everything is production

---

## Step 1: Create a Telegram Bot (5 minutes)

### 1.1 Open Telegram

1. Open Telegram (download from https://telegram.org if needed)
2. Search for: **@BotFather**
3. Click to open the official Telegram bot

### 1.2 Create New Bot

Send the message: `/newbot`

BotFather will ask you questions:

**Question 1: "Alright, a new bot. How are we going to call it?"**
- Answer: `MyAuto Car Monitor` (or any name you like)

**Question 2: "Good. Now let's choose a username for your bot. It must end in `bot`."**
- Answer: `myauto_listing_bot` (must end with `bot`, no spaces, lowercase)

**Example of response:**
```
Done! Congratulations on your new bot. You will find it at t.me/myauto_listing_bot.
Here are your bot credentials:

Bot token: 6123456789:ABCdefg1234567-HIJklmno_PQRstuvWXYZ
You can use this token to access the HTTP Bot API:
https://api.telegram.org/bot6123456789:ABCdefg1234567-HIJklmno_PQRstuvWXYZ/

For a description of the Bot API, see this page:
https://core.telegram.org/bots/api
Keep your token secure and store it safely, it can be used by anyone to control your bot.
```

### ⚠️ IMPORTANT: Copy and save your bot token!

```
TELEGRAM_BOT_TOKEN = "6123456789:ABCdefg1234567-HIJklmno_PQRstuvWXYZ"
```

---

## Step 2: Get Your Chat ID (2 minutes)

Your "Chat ID" is your Telegram user ID. The bot needs this to know where to send messages.

### 2.1 Find Your Chat ID

**Method 1: Using the test script (Easiest)**

1. Update `test_telegram.py`:
   ```python
   TELEGRAM_BOT_TOKEN = "YOUR_TOKEN_HERE"  # Paste token from Step 1
   TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"  # Leave as is for now
   ```

2. Run: `python test_telegram.py`

3. The script will ask you to message your bot

4. Open your bot (search for `@myauto_listing_bot` in Telegram)

5. Send: `/start`

6. Go back to PowerShell and run `test_telegram.py` again

7. It will find your Chat ID!

**Method 2: Manual (Using Bot Token)**

1. Replace `YOUR_BOT_TOKEN` in this URL:
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```

2. Paste the full URL in your browser

3. Send `/start` to your bot first

4. Refresh browser page

5. Look for `"chat":{"id":` - that's your Chat ID!

   Example:
   ```json
   {
     "update_id": 123456789,
     "message": {
       "message_id": 1,
       "date": 1699520400,
       "chat": {
         "id": 987654321,  ← THIS IS YOUR CHAT ID
         "type": "private",
         "username": "yourname"
       },
       "text": "/start"
     }
   }
   ```

### Save your Chat ID:
```
TELEGRAM_CHAT_ID = 987654321
```

---

## Step 3: Test Telegram Connection (2 minutes)

### 3.1 Update test_telegram.py

```python
TELEGRAM_BOT_TOKEN = "6123456789:ABCdefg1234567-HIJklmno_PQRstuvWXYZ"  # Your token
TELEGRAM_CHAT_ID = 987654321  # Your chat ID
```

### 3.2 Run the test

```bash
python test_telegram.py
```

**Expected output:**
```
[OK] Message sent successfully!
[OK] TELEGRAM BOT IS WORKING!
```

**You should receive a test message in Telegram!**

---

## Step 4: Add to GitHub Secrets (2 minutes)

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

**Add two secrets:**

**Secret 1: TELEGRAM_BOT_TOKEN**
- Name: `TELEGRAM_BOT_TOKEN`
- Value: `6123456789:ABCdefg1234567-HIJklmno_PQRstuvWXYZ`
- Click "Add secret"

**Secret 2: TELEGRAM_CHAT_ID**
- Name: `TELEGRAM_CHAT_ID`
- Value: `987654321`
- Click "Add secret"

---

## Step 5: Message Formatting (Optional but cool)

Telegram supports **HTML formatting**:

```python
message = """
<b>Bold text</b>
<i>Italic text</i>
<u>Underlined text</u>
<s>Strikethrough text</s>
<code>Monospace code</code>
<pre>Preformatted text</pre>

<a href="https://example.com">Clickable link</a>
"""
```

**Example car listing notification:**

```python
message = f"""
<b>🚗 NEW CAR LISTING FOUND!</b>

<b>{car['make']} {car['model']} {car['year']}</b>

<b>Price:</b> ${car['price']:,} {car['currency']}
<b>Location:</b> {car['location']}
<b>Mileage:</b> {car['mileage_km']:,} km
<b>Fuel:</b> {car['fuel_type']}
<b>Transmission:</b> {car['transmission']}

<a href="{car['url']}">View full listing</a>
"""
```

---

## Step 6: Sending Images (Bonus)

You can also send images from the car listing:

```python
def send_telegram_photo(token, chat_id, photo_url, caption):
    """Send photo to Telegram"""

    url = f"https://api.telegram.org/bot{token}/sendPhoto"

    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption,
        "parse_mode": "HTML"
    }

    response = requests.post(url, json=payload)
    return response.json()
```

---

## Troubleshooting

### "Message not sent" or timeout error

**Solution:**
- Check internet connection
- Verify bot token is correct
- Verify chat ID is correct
- Make sure you've messaged the bot with `/start`

### "Telegram API error: Bad Request: chat not found"

**Solution:**
- Your Chat ID is wrong
- Run the test script again to find the correct Chat ID
- Check you're using your user ID, not a channel ID

### "Token invalid"

**Solution:**
- Copy the token exactly from BotFather
- No spaces before or after
- Include the colon `:` and dash `-` in the token

### Bot not responding in Telegram

**Solution:**
- Bot might be inactive
- Send `/start` to activate it
- Try sending a message to the bot manually first

---

## Your Credentials

Save these somewhere safe:

```
Bot Name: myauto_listing_bot
Bot Token: 6123456789:ABCdefg1234567-HIJklmno_PQRstuvWXYZ
Chat ID: 987654321

GitHub Secrets:
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID
```

---

## Comparison: Telegram vs WhatsApp

| Feature | Telegram | WhatsApp |
|---------|----------|----------|
| **Cost** | FREE ✅ | FREE in Sandbox, $ in Production |
| **Message Limit** | Unlimited ✅ | Limited (tiered) |
| **Setup** | 5 minutes ✅ | Complex business verification |
| **Bot Automation** | Designed for bots ✅ | For business use |
| **Rich Formatting** | HTML, Markdown ✅ | Limited templates |
| **Images** | Easy ✅ | Requires templates |
| **Scaling** | No cost increase ✅ | Costs per message |
| **For Personal Use** | Perfect ✅ | Overkill |

---

**You're all set! Ready for Telegram integration!** 🤖

Next: Update your scraper code to use Telegram instead of WhatsApp.

