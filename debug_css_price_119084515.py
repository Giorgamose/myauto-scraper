#!/usr/bin/env python3
"""
Debug script to show exactly what CSS selectors find for price
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
    print("DEBUG: CSS SELECTOR PRICE EXTRACTION - LISTING 119084515")
    print("="*80)

    try:
        html = await get_html()
        soup = BeautifulSoup(html, 'lxml')

        # Try the CSS selectors used in scraper.py line 554
        selectors = [
            ".price",
            ".listing-price",
            "[data-price]",
            # Also try some additional common selectors
            ".price-amount",
            ".product-price",
            "[class*='price']",
            "p.text-\\[24px\\]",  # From the user's example
            "p[class*='text-']"
        ]

        print("\nTesting CSS selectors:")
        print("-" * 80)

        for selector in selectors:
            print(f"\nSelector: {selector}")
            try:
                elements = soup.select(selector)
                if elements:
                    print(f"  Found {len(elements)} element(s):")
                    for i, elem in enumerate(elements[:3]):  # Show first 3
                        text = elem.get_text(strip=True)[:100]  # First 100 chars
                        print(f"    [{i}] {text}")
                else:
                    print(f"  Found 0 elements")
            except Exception as e:
                print(f"  ERROR: {e}")

        # Try to find any element with numbers and "USD" or "$" in it
        print("\n" + "-" * 80)
        print("\nSearching for price patterns in HTML...")

        all_text = soup.get_text()

        # Look for USD patterns
        usd_matches = re.findall(r'(\d+[\s,]*\d*)\s*(\$|USD)', all_text)
        if usd_matches:
            print(f"\nFound {len(usd_matches)} USD pattern(s):")
            for amount, symbol in usd_matches[:10]:
                print(f"  {amount} {symbol}")

        # Look for GEL patterns
        gel_matches = re.findall(r'(\d+[\s,]*\d*)\s*(₾|GEL)', all_text)
        if gel_matches:
            print(f"\nFound {len(gel_matches)} GEL pattern(s):")
            for amount, symbol in gel_matches[:10]:
                print(f"  {amount} {symbol}")

        # Try extract_text simulation
        print("\n" + "-" * 80)
        print("\nSimulating extract_text for '.price, .listing-price, [data-price]'...")

        for selector in [".price", ".listing-price", "[data-price]"]:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                print(f"  Found via '{selector}': {text[:200]}")

                # Now simulate extract_number on this text
                text_clean = text.replace(" ", "").replace(",", "")
                match = re.search(r"\d+", text_clean)
                if match:
                    num = int(match.group())
                    print(f"    Extract number result: {num}")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*80)

if __name__ == '__main__':
    asyncio.run(main())
