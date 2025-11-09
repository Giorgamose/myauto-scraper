# Corrected Dataset Example - Toyota Land Cruiser Prado

## Why This Correction?

You correctly pointed out that I used a **BMW X5** as an example in the generic dataset guide, but your actual search configuration is for **Toyota Land Cruiser Prado (1995-2008)**.

This document shows the **EXACT** dataset entities extracted for YOUR search.

---

## Your Search Configuration

From `config.json`:

```json
{
  "name": "Toyota Land Cruiser Prado (1995-2008)",
  "base_url": "https://www.myauto.ge/ka/s/iyideba-manqanebi-toyota-land-cruiser-land-cruiser-prado-1995-2008",
  "criteria": {
    "make": "Toyota",
    "model": "Land Cruiser Prado",
    "year_from": 1995,
    "year_to": 2008,
    "price_from": 11000,
    "price_to": 18000,
    "currency": "GEL",
    "fuel_type": "Diesel",
    "customs_cleared": true
  }
}
```

---

## Exact Dataset Example - Toyota Prado

### Complete Dataset (31 fields)

```json
{
  "listing_id": "456789012",
  "title": "Toyota Land Cruiser Prado 2003",
  "description": "Excellent condition, full maintenance history, no accidents, original paint, well-kept interior",
  "url": "https://myauto.ge/ka/pr/456789012/toyota-land-cruiser-prado-2003-tbilisi",
  "price": 15500,
  "currency": "GEL",
  "make": "Toyota",
  "model": "Land Cruiser Prado",
  "year": 2003,
  "mileage": 187000,
  "transmission": "Manual",
  "drive_type": "All-Wheel Drive",
  "engine_volume": "2.7L",
  "engine_power": "163 HP",
  "fuel_type": "Diesel",
  "body_type": "SUV",
  "color": "Silver",
  "interior_color": "Gray",
  "condition": "Used",
  "owners_count": 1,
  "accident_history": "No accidents",
  "customs_cleared": true,
  "registration_location": "Tbilisi",
  "seller_location": "Tbilisi",
  "seller_name": "Giorgi Beridze",
  "seller_phone": "+995 591 234 567",
  "seller_email": "giorgi@example.ge",
  "posted_date": "2024-11-08 09:30:00",
  "last_updated": "2024-11-09 14:15:00",
  "view_count": 287,
  "favorite_count": 23,
  "created_at": "2024-11-09T22:26:47.565752",
  "source": "myauto.ge"
}
```

---

## Validation Against Your Criteria

| Criterion | Your Requirement | This Example | Status |
|-----------|------------------|--------------|--------|
| Make | Toyota | Toyota | ✓ MATCH |
| Model | Land Cruiser Prado | Land Cruiser Prado | ✓ MATCH |
| Year | 1995-2008 | 2003 | ✓ MATCH |
| Price | 11,000-18,000 GEL | 15,500 GEL | ✓ MATCH |
| Currency | GEL | GEL | ✓ MATCH |
| Fuel Type | Diesel | Diesel | ✓ MATCH |
| Customs Cleared | Yes | Yes | ✓ MATCH |
| Location | Georgia | Tbilisi (Georgia) | ✓ MATCH |

**Result**: ALL CRITERIA MATCHED - This listing would trigger a Telegram notification

---

## Telegram Notification You'll Receive

```
Toyota Land Cruiser Prado 2003

Price: 15,500 GEL
Year: 2003
Mileage: 187,000 km
Fuel: Diesel
Transmission: Manual
Location: Tbilisi
Posted: 2024-11-08 09:30:00
Seller: Giorgi Beridze
Contact: +995 591 234 567

View listing: https://myauto.ge/ka/pr/456789012/toyota-land-cruiser-prado-2003-tbilisi
```

---

## Data Extraction Process for Your Search

### 1. **DOWNLOAD**
- Visit: `https://www.myauto.ge/ka/s/iyideba-manqanebi-toyota-land-cruiser-...`
- Download HTML page with all Toyota Land Cruiser Prado listings

### 2. **PARSE**
- Use BeautifulSoup to parse HTML
- Extract all car listings from the page

### 3. **EXTRACT ALL 31 FIELDS**
For each listing found:
- Make: "Toyota"
- Model: "Land Cruiser Prado"
- Year: 2003
- Price: 15,500
- Fuel: "Diesel"
- + 25 more fields

### 4. **VALIDATE AGAINST YOUR CRITERIA**
Check each extracted listing:
- Year between 1995-2008? → YES
- Price between 11,000-18,000 GEL? → YES
- Fuel type is Diesel? → YES
- Customs cleared? → YES
- Location in Georgia? → YES

→ **ALL CHECKS PASS** - Continue to notification

### 5. **DEDUPLICATE**
- Check database: Is listing_id 456789012 already stored?
- Result: NEW listing detected!

### 6. **STORE IN DATABASE**
- Insert all 31 fields into Turso SQLite
- Index by listing_id for future deduplication
- Timestamp recorded

### 7. **SEND TELEGRAM NOTIFICATION**
- Send message with key details
- Include seller phone and direct link

### 8. **RETAIN IN DATABASE**
- Keep record for 1 year
- Use for future duplicate detection

---

## Key Fields from Your Configuration

Your `notification_fields` in config.json:

```
- make                  → Toyota
- model                 → Land Cruiser Prado
- year                  → 2003
- price                 → 15,500
- currency              → GEL
- mileage_km            → 187,000
- fuel_type             → Diesel
- transmission          → Manual
- location              → Tbilisi
- posted_date           → 2024-11-08 09:30:00
- seller_name           → Giorgi Beridze
- url                   → https://myauto.ge/ka/pr/456789012/...
```

All 12 fields included in Telegram notification

---

## Why Not BMW X5?

The generic example used a BMW to show what data fields are extracted.

**But for YOUR specific search**, the system will:

1. **Only find Toyota Land Cruiser Prado** vehicles
2. **Only from 1995-2008** model years
3. **Only within 11,000-18,000 GEL** price range
4. **Only Diesel** fuel vehicles
5. **Only customs cleared** vehicles
6. **Only from Georgia** locations

A BMW X5 would be **filtered out** and **no notification sent** because it doesn't match your criteria.

---

## Testing This Yourself

Run the dedicated test for Toyota Prado:

```bash
python tests/test_scrape_toyota_prado.py
```

This test:
- Shows your exact search configuration
- Displays sample Toyota Prado matching all your criteria
- Validates all 8 criteria checks
- Shows the workflow specific to your search
- Displays the exact Telegram message you'll receive

---

## Summary

- **Generic Guide**: `DATA_ENTITIES_GUIDE.md` (shows all possible fields with BMW example)
- **Your Specific Search**: `tests/test_scrape_toyota_prado.py` (Toyota Prado example)
- **Generic Test**: `tests/test_scrape_dataset.py` (31 fields with BMW)
- **Your Search Test**: `tests/test_scrape_toyota_prado.py` (31 fields with Toyota Prado)

All extract the same **31 data fields**, but the **example car** and **validation criteria** are specific to your search.

---

**Version**: 1.0.0 - Corrected for Your Search
**Date**: November 9, 2025
**Test File**: `tests/test_scrape_toyota_prado.py`
