#!/usr/bin/env python3
"""
Debug script to test fallback pattern extraction for prices
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re

async def get_html():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto('https://www.myauto.ge/ka/pr/119084515', timeout=15000)
            await page.wait_for_load_state('domcontentloaded')
            html = await page.content()
        finally:
            await browser.close()
        return html

async def main():
    print("\n" + "="*80)
    print("DEBUG: FALLBACK PATTERN EXTRACTION - LISTING 119084515")
    print("="*80)

    try:
        html = await get_html()
        soup = BeautifulSoup(html, 'lxml')
        full_text = soup.get_text()

        # Test the patterns from scraper.py lines 694-701
        gel_patterns = [
            (r'ფასი\s*[:=]\s*([0-9\s,]+)(?:\s*(?:\$|USD))', 'Georgian label with USD'),
            (r'₾\s*(\d{1,3}(?:\s\d{3})+)', '"₾ 12 000"'),
            (r'₾\s*(\d{1,3}(?:,\d{3})+)', '"₾ 12,000"'),
            (r'(\d{1,3}(?:\s\d{3})+)\s*₾', '"12 000 ₾"'),
            (r'(\d{1,3}(?:,\d{3})+)\s*₾', '"12,000 ₾"'),
            (r'ფასი\s*[:=]\s*([0-9\s,]+)(?:\s*(?:\$|USD|₾|GEL))?', 'Georgian label'),
        ]

        print("\nTesting fallback patterns:")
        print("-" * 80)

        found_prices = {}

        for pattern, desc in gel_patterns:
            print(f"\nPattern: {pattern}")
            print(f"Description: {desc}")

            matches = re.findall(pattern, full_text)
            if matches:
                print(f"  ✅ Found {len(matches)} match(es):")
                for i, match in enumerate(matches[:5]):  # Show first 5
                    # Clean the matched price
                    price_str = match.replace(' ', '').replace(',', '')
                    print(f"    [{i}] Raw: '{match}' -> Clean: '{price_str}'")

                    # Extract first number
                    if price_str:
                        first_match = re.search(r"\d+", price_str)
                        if first_match:
                            num = int(first_match.group())
                            if 5000 < num < 10000000:
                                print(f"        Extracted: {num}")
                                if num not in found_prices:
                                    found_prices[num] = (match, pattern, desc)
            else:
                print(f"  ❌ No matches")

        print("\n" + "=" * 80)
        print("\nSUMMARY OF FOUND PRICES:")
        print("-" * 80)

        if found_prices:
            print(f"Total unique prices found: {len(found_prices)}")
            for amount in sorted(found_prices.keys()):
                match_text, pattern, desc = found_prices[amount]
                print(f"\n  Amount: {amount:,}")
                print(f"    Matched: '{match_text}'")
                print(f"    Pattern: {desc}")

            print(f"\n✅ First price found: {min(found_prices.keys()):,}")
            print(f"✅ Lowest price: {min(found_prices.keys()):,}")

            if min(found_prices.keys()) == 15500 or min(found_prices.keys()) == 15800:
                print(f"\n✅ SUCCESS - Would extract USD correctly")
            elif min(found_prices.keys()) == 25200:
                print(f"\n❌ FAILURE - Would extract 25,200 instead of 15,500")
        else:
            print("No prices found matching any pattern!")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*80)

if __name__ == '__main__':
    asyncio.run(main())
