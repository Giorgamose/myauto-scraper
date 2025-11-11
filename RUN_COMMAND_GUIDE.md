# 🚀 /run Command Guide - Immediate Search Execution

The new `/run <number>` command allows you to **immediately check a specific saved search** for new listings without waiting for the automatic 15-minute checks.

---

## Quick Start

### Syntax
```
/run <number>
```

**Where `<number>` is:**
- `1` = First saved search
- `2` = Second saved search
- `3` = Third saved search
- etc.

---

## Examples

### Example 1: Check First Saved Search
```
You send: /run 1

Bot responds:
⏳ Checking for new listings... (this may take a moment)

[Results show either:]
✅ Found N NEW LISTINGS!
[Lists all new listings with details]

OR

✅ Check Complete
No new listings found for search #1.
Note: Already seen 5 existing listings in this search.
```

### Example 2: Check Multiple Searches
```
You send: /run 1
[Bot shows results for search 1]

You send: /run 2
[Bot shows results for search 2]

You send: /run 3
[Bot shows results for search 3]
```

---

## How It Works

1. **You send `/run 1`** → Bot receives command
2. **Bot fetches listings** → Connects to MyAuto.ge and gets current listings
3. **Bot checks for new** → Compares with listings you've already seen
4. **Bot sends results** → Shows new listings or "no new" message
5. **Bot updates DB** → Marks new listings as seen
6. **Bot updates timer** → Resets the `last_checked` timestamp

---

## What You'll See

### ✅ New Listings Found

When new listings are found, you see:

```
✅ Found 3 NEW LISTINGS!

Search #1

1. Toyota Land Cruiser 2005
   ₾15,500 | 📍 Tbilisi
   View listing →

2. Honda Civic 2010
   ₾8,900 | 📍 Batumi
   View listing →

3. BMW 3 Series 2012
   ₾12,300 | 📍 Gori
   View listing →
```

### ✅ No New Listings

If all listings are already seen:

```
✅ Check Complete

No new listings found for search #1.

Note: Already seen 5 existing listings in this search.
```

### ✅ No Listings At All

If the search URL has no results:

```
✅ Check Complete

No new listings found for search #1.

https://myauto.ge/ka/s/iyideba-motociklebi...
```

---

## Error Cases

### ❌ No Number Specified

```
You send: /run

Bot responds:
❌ Error: Please specify which search to run

/run 1 - checks first search
/run 2 - checks second search
```

### ❌ Invalid Number

```
You send: /run abc

Bot responds:
❌ Error: Search number must be a number

Example: /run 1
```

### ❌ Number Out of Range

```
You send: /run 5
[But you only have 2 saved searches]

Bot responds:
❌ Error: You only have 2 search(es).

Use /list to see all searches.
```

### ❌ No Saved Searches

```
You send: /run 1
[But you haven't saved any searches]

Bot responds:
📋 You don't have any saved searches.

Use /set to add a search.
```

---

## Workflow: Set → List → Run → Check

**Complete example:**

1. **Add a search:**
   ```
   /set https://myauto.ge/ka/search?catID=2&modelID[]=322
   ```
   Response: `✅ Search criteria saved!`

2. **View your searches:**
   ```
   /list
   ```
   Response:
   ```
   📋 Your saved searches:

   1. https://myauto.ge/ka/search?catID=2&modelID[]=322
      (Created: 2025-11-11 14:30:45)
   ```

3. **Immediately check it:**
   ```
   /run 1
   ```
   Response: Shows new listings if any

4. **Check statistics:**
   ```
   /status
   ```
   Response: Shows active users, subscriptions, etc.

---

## When to Use /run

### ✅ Good Use Cases

- **Right after adding a new search** - Verify the URL works and see initial results
- **Want to manually check** - Don't wait 15 minutes for automatic check
- **Testing a URL** - Before saving permanently
- **Looking for urgent listings** - Need results immediately
- **Quick verification** - Confirm your searches are working

### ⏰ Compare with Automatic Checks

**Automatic Checks (every 15 minutes):**
- ✅ No manual action needed
- ✅ Runs continuously 24/7
- ❌ Can't manually trigger
- ❌ Wait up to 15 minutes for results

**Manual `/run` Command:**
- ✅ Results immediately
- ✅ Run anytime you want
- ✅ Check specific searches
- ❌ Must type the command

**Best Practice:** Use both!
- Let automatic checks run 24/7
- Use `/run` when you need immediate results

---

## Tips & Tricks

### Speed Up Checks

The `/run` command may take a few seconds because:
1. It connects to MyAuto.ge
2. It fetches current listings
3. It compares with your seen listings
4. It formats the response

So be patient! ⏳

### Check All Searches Quickly

```
You send: /run 1
[Wait for results]

You send: /run 2
[Wait for results]

You send: /run 3
[Wait for results]
```

### Use /list First

Always use `/list` to see which search number to run:

```
/list
→ Shows: 1. URL_1
         2. URL_2
         3. URL_3

/run 2
→ Checks search #2
```

---

## Integration with Other Commands

### After /clear (Remove All Searches)

```
/clear
[Removes all searches]

/run 1
→ Error: You don't have any saved searches

/set https://myauto.ge/...
[Add new search]

/run 1
[Now it works!]
```

### After /set (Add New Search)

```
/set https://myauto.ge/ka/search?...
✅ Search criteria saved!

/run 1
[Immediately check the new search]
```

---

## Development Notes

### How /run Differs from Automatic Checks

| Aspect | /run Command | Automatic (15 min) |
|--------|---|---|
| Trigger | Manual (user types `/run 1`) | Scheduled (every 15 min) |
| Scope | Single search only | All active searches |
| Response | Sent to user directly | Sent to configured channel |
| Logging | Logged as manual run | Logged as scheduled check |
| Database | Marks listings as seen | Marks listings as seen |
| Timing | Immediate | Every 15 minutes |

### What Happens Inside

When you run `/run 1`:

1. Bot retrieves subscription #1 from database
2. Bot creates search config from the URL
3. Bot calls `scraper.fetch_search_results()`
4. For each listing, checks if chat_id has seen it
5. Collects "new" listings (not seen before)
6. Marks each new listing as seen in DB
7. Formats listings into message
8. Sends message to user
9. Updates `last_checked` timestamp

---

## Future Enhancements (Ideas)

- `/run all` - Check all searches at once
- `/run 1-3` - Check searches 1, 2, and 3
- `/run "name"` - Run search by name (instead of number)
- `/run --notify-channel` - Send results to channel instead of DM
- `/run --format json` - Get results in JSON format

---

## Support

If `/run` is not working:

1. **Check the help:** `/help` - Verify command exists
2. **List searches:** `/list` - Verify you have searches saved
3. **Verify number:** Make sure the number matches the `/list` output
4. **Check bot logs:** Look at terminal output for error messages
5. **Restart bot:** Sometimes a restart helps

---

That's it! Enjoy your `/run` command! 🚀
