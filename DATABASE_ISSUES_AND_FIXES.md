# Database Storage Issues - Analysis and Solutions

## Current Status (As of Nov 10, 2025)

### ✅ Working
- `seen_listings` table: Populated correctly with listing IDs
- `search_configurations` table: Now populated with search configs from config.json
- Web scraping: Successfully finding 30+ listings from MyAuto.ge
- Listing detection: Correctly identifying new vs seen listings

### ❌ Not Working
- `vehicle_details` table: All fields are NULL (make, model, year, price, etc.)
- Detailed listing information: Not being extracted from listing pages

---

## Root Cause Analysis

### The Problem

The parser's `_parse_listing_details()` function is not extracting any vehicle data. Example:
```
Expected: Toyota | Land Cruiser | 2006 | 45,000 km | $15,500
Actual:   None   | None          | None | None      | None
```

### Why This Happens

**MyAuto.ge is a React Single Page Application (SPA)**

1. **Search results HTML**: Contains only listing cards with minimal info
   - Has: listing_id, URL, title text
   - Missing: make, model, year, price, mileage, engine specs

2. **Detail pages HTML**: Content is loaded dynamically by React
   - Initial HTML returned by Playwright: Only shell/skeleton content
   - Vehicle details: Injected by JavaScript after page loads
   - CSS selectors used in parser (`.price`, `.make`, `.title`) don't exist in initial HTML

3. **Parser ineffectiveness**:
   ```python
   # These selectors return nothing because React hasn't rendered yet
   price_text = MyAutoParser.extract_text(soup, ".price, .listing-price")  # Returns None
   make = MyAutoParser.extract_text(soup, ".make, [data-make]")            # Returns None
   ```

---

## Current Data Flow

```
[Search Results]
    ↓
[Parse Summaries] → Extract: ID, URL, title only
    ↓
[New Listing Detected]
    ↓
[Fetch Detail Page] → Playwright loads page
    ↓
[Parse Details] → CSS selectors fail to find data (React not rendered)
    ↓
[Store with NULL values] ← Database ends up with NULL make/model/year/price
```

---

## Solution Options

### Option 1: Extract from React State (Recommended)
**Approach**: Extract data from JavaScript embedded in the page

```python
# Instead of searching for .price, look for React data:
import json
scripts = soup.find_all("script")
for script in scripts:
    if "listing" in script.string:
        data = json.loads(script.string)
        make = data.get("vehicle", {}).get("make")
        model = data.get("vehicle", {}).get("model")
        # etc...
```

**Pros:**
- Data is always available in the HTML
- No additional wait time needed
- Faster parsing

**Cons:**
- Requires reverse-engineering the JSON structure
- May change if website updates

### Option 2: Wait for React to Render (Current Issue)
**The problem**: Playwright's `wait_until="load"` doesn't wait for React rendering

```python
# Current (broken):
page.goto(url, wait_until="load", timeout=20000)
html = page.content()  # Returns HTML before React renders

# Should be:
page.goto(url, wait_until="load", timeout=20000)
page.wait_for_selector('[class*="price"]', timeout=5000)  # Wait for React-rendered content
page.wait_for_selector('[class*="make"]', timeout=5000)
html = page.content()  # Now React has rendered
```

**Pros:**
- HTML will have rendered content
- Existing CSS selectors would work
- Uses current approach

**Cons:**
- Slower (adds 5+ seconds per listing)
- Network unreliable, timeouts possible

### Option 3: Use Website API
**Approach**: Some sites expose an API endpoint for listing details

```python
# Instead of scraping HTML, use API:
response = requests.get(f"https://api.myauto.ge/listings/{listing_id}")
data = response.json()
make = data["vehicle"]["make"]
# etc...
```

**Status**: Unknown if MyAuto.ge has public API

---

## Recommended Solution: Hybrid Approach

### Step 1: Improve Playwright Waiting (Immediate)
Add explicit waits for React-rendered content in scraper.py:

```python
# After page.goto(), add:
page.wait_for_selector('body', timeout=5000)  # Wait for basic content
time.sleep(3)  # Give React time to render
html = page.content()
```

### Step 2: Improve Parser (Short Term)
Update `_parse_listing_details()` to handle both:
1. React state data in `<script>` tags
2. CSS selector-based parsing as fallback

```python
# Try extracting from React state first
json_data = extract_json_from_page(soup)
if json_data.get("vehicle", {}).get("make"):
    make = json_data["vehicle"]["make"]  # Use React data
else:
    make = extract_text(soup, ".make")  # Fallback to CSS
```

### Step 3: Validate Data Quality (Ongoing)
Add validation to ensure required fields are populated:

```python
if not listing_data.get("vehicle", {}).get("make"):
    logger.warning(f"Listing {listing_id}: Missing make/model")
    # Alert or retry
```

---

## Implementation Steps

### Immediate (This commit)
```python
# In scraper.py, modify _make_request():

# Add after page.goto():
try:
    page.wait_for_selector(
        '.price, [class*="price"], h1, .title',
        timeout=3000
    )
except:
    pass  # Continue anyway

time.sleep(1.5)  # Give React time
html = page.content()
```

### Short Term
Update parser.py's `_parse_listing_details()` to:
1. Check for React data in script tags
2. Use JSON parsing for structured data
3. Fallback to CSS selectors

### Testing Required
- Fetch 10 real listings
- Verify all fields populated (not NULL)
- Check for any missing data
- Validate data accuracy

---

## Current Database State

```
Database: efohkibukutjvrrhhxdn

✓ seen_listings: 3 records
  - ID, created_at, notified: ✅ Populated

✓ search_configurations: 1 record
  - name, is_active: ✅ Populated

✗ vehicle_details: 3 records (ALL NULL)
  - listing_id: ✅ Populated
  - make, model, year, price, mileage: ❌ NULL
  - All other fields: ❌ NULL
```

---

## Files to Modify

1. **scraper.py** → Improve Playwright waiting
2. **parser.py** → Add React data extraction
3. **database_rest_api.py** → Add validation
4. **main.py** → Already updated with detail fetching ✅

---

## Testing Commands

```bash
# Check database status
python debug_database.py

# Test detail fetching
python test_detail_fetch.py

# Run full monitoring with debug logging
LOG_LEVEL=DEBUG python main.py
```

---

## Priority

**HIGH**: Vehicle details (make, model, year) are essential for the monitoring system

This must be fixed before the system goes to production in GitHub Actions.

---

## Next Steps

1. Implement Step 1 (Playwright waiting)
2. Test with `test_detail_fetch.py`
3. Implement Step 2 (Parser improvements)
4. Run full monitoring cycle
5. Verify database population
6. Deploy to GitHub Actions
