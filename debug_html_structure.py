#!/usr/bin/env python3
"""
Debug script to inspect and save listing HTML for analysis
"""

import logging
from dotenv import load_dotenv
from scraper import MyAutoScraper
from utils import load_config_file
from bs4 import BeautifulSoup
import json

load_dotenv('.env.local')
load_dotenv('.env')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load config
config = load_config_file('config.json')

# Initialize scraper
scraper = MyAutoScraper(config)

# Test listing ID
test_listing_id = "119084515"

print(f"\n{'='*70}")
print(f"Fetching HTML for listing: {test_listing_id}")
print(f"{'='*70}\n")

# Fetch the page
response = scraper._make_request(f"https://www.myauto.ge/ka/pr/{test_listing_id}")

if response:
    html = response['html']

    # Save to file for inspection
    with open("debug_listing.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[OK] Saved listing HTML to: debug_listing.html ({len(html)} bytes)\n")

    # Parse and analyze structure
    soup = BeautifulSoup(html, "lxml")

    print(f"[*] Analyzing HTML structure...\n")

    # Look for common vehicle data patterns
    print(f"[*] Looking for vehicle information elements:")
    print(f"    - h1 tags: {len(soup.find_all('h1'))}")
    print(f"    - h2 tags: {len(soup.find_all('h2'))}")
    print(f"    - Elements with 'price' in class: {len(soup.find_all(class_=lambda x: x and 'price' in x.lower()))}")
    print(f"    - Elements with 'make' in class: {len(soup.find_all(class_=lambda x: x and 'make' in x.lower()))}")
    print(f"    - Elements with 'model' in class: {len(soup.find_all(class_=lambda x: x and 'model' in x.lower()))}")
    print(f"    - Elements with 'year' in class: {len(soup.find_all(class_=lambda x: x and 'year' in x.lower()))}")
    print(f"    - Elements with 'mileage' in class: {len(soup.find_all(class_=lambda x: x and 'mileage' in x.lower()))}")

    # Look for script tags
    scripts = soup.find_all("script")
    print(f"\n[*] Script tags found: {len(scripts)}")

    # Analyze script tags
    for i, script in enumerate(scripts):
        if not script.string:
            print(f"    [{i}] Empty script")
            continue

        content = script.string[:200] if len(script.string) > 200 else script.string
        has_json = content.count('{')
        has_listing = 'listing' in script.string.lower()
        has_vehicle = 'vehicle' in script.string.lower()

        print(f"    [{i}] {len(script.string)} chars, JSON={{}}x{has_json}, listing={has_listing}, vehicle={has_vehicle}")

        # Try to parse as JSON
        if has_json and (has_listing or has_vehicle):
            try:
                # Find JSON in script
                import re
                json_match = re.search(r'\{.*\}', script.string, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    # Try to load it
                    try:
                        data = json.loads(json_str)
                        print(f"        ✓ Valid JSON found with keys: {list(data.keys())[:5]}")
                    except:
                        print(f"        ! JSON pattern found but parsing failed")
            except:
                pass

    # Extract all text content and look for pricing
    print(f"\n[*] First 2000 characters of body text:")
    print("-" * 70)
    body = soup.body if soup.body else soup
    text = body.get_text()[:2000]
    print(text)
    print("-" * 70)

    # Look for price patterns
    print(f"\n[*] Looking for price patterns in text:")
    import re
    price_patterns = [
        (r'\$\s*[\d,]+', 'USD pattern ($...)'),
        (r'₾\s*[\d,]+', 'GEL pattern (₾...)'),
        (r'[\d,]+\s*\$', 'USD pattern (...$)'),
        (r'[\d,]+\s*₾', 'GEL pattern (...₾)'),
    ]

    for pattern, desc in price_patterns:
        matches = re.findall(pattern, text)
        if matches:
            print(f"    Found {desc}: {matches[:3]}")

    print(f"\n[*] Sample HTML structure (first 5000 chars):")
    print("-" * 70)
    print(html[:5000])
    print("-" * 70)

else:
    print("[ERROR] Failed to fetch page")

scraper.close()
