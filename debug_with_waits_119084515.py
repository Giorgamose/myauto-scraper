#!/usr/bin/env python3
"""
Debug script using same wait strategies as scraper
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import time
import re

async def get_html():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            # Same approach as scraper._make_request
            await page.goto('https://www.myauto.ge/ka/pr/119084515', wait_until="load", timeout=30000)

            # Wait for specific elements like scraper does
            try:
                await page.wait_for_selector(
                    'h1, [class*="price"], [class*="make"], [class*="model"], [class*="year"], [class*="mileage"]',
                    timeout=6000
                )
            except:
                print("[DEBUG] Selector wait timed out (OK)")

            # Add delay like scraper does
            time.sleep(3)

            html = await page.content()
        finally:
            await browser.close()
        return html

async def main():
    print("\n" + "="*100)
    print("DEBUG: WITH SCRAPER WAIT STRATEGY - LISTING 119084515")
    print("="*100)

    try:
        html = await get_html()
        soup = BeautifulSoup(html, 'lxml')
        full_text = soup.get_text()

        print(f"\nHTML size: {len(html)} bytes")
        print(f"Text size: {len(full_text)} bytes")

        # Try to find [class*="price"] elements like scraper mentions
        print("\nSearching for elements with 'price' in class...")
        print("-" * 100)

        price_elements = soup.find_all(class_=re.compile('price', re.IGNORECASE))
        print(f"Found {len(price_elements)} elements with 'price' in class")

        for i, elem in enumerate(price_elements[:5]):
            text = elem.get_text(strip=True)[:200]
            print(f"  [{i}] {text}")

        # Also look for h1
        print("\nSearching for h1 elements...")
        h1_elements = soup.find_all('h1')
        for i, elem in enumerate(h1_elements[:3]):
            text = elem.get_text(strip=True)[:200]
            print(f"  [{i}] {text}")

        # Search for all numbers in valid price range
        print("\n" + "-" * 100)
        print("Searching for prices in text...")
        print("-" * 100)

        prices = {}

        for match in re.finditer(r'\b(\d{4,7})\b', full_text):
            num_str = match.group(1)
            num = int(num_str)
            if 5000 < num < 10000000:
                if num not in prices:
                    prices[num] = []
                prices[num].append(match.start())

        for match in re.finditer(r'(\d{1,3}(?:[,\s]\d{3})+)', full_text):
            num_str = match.group(1)
            clean = num_str.replace(' ', '').replace(',', '')
            num = int(clean)
            if 5000 < num < 10000000:
                if num not in prices:
                    prices[num] = []
                prices[num].append(match.start())

        if prices:
            sorted_by_amount = sorted(prices.keys())
            sorted_by_position = sorted(prices.items(), key=lambda x: min(x[1]))

            print(f"\nFound {len(prices)} unique prices:")
            print(f"  By amount: {sorted_by_amount}")
            print(f"  First by position: {sorted_by_position[0][0]}")
            print(f"  Last by position: {sorted_by_position[-1][0]}")
        else:
            print("\nNo prices found!")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*100)

if __name__ == '__main__':
    asyncio.run(main())
