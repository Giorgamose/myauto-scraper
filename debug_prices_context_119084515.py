#!/usr/bin/env python3
"""
Debug script to show all prices with their context
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
            await page.goto('https://www.myauto.ge/ka/pr/119084515', timeout=30000)
            await page.wait_for_load_state('domcontentloaded')
            html = await page.content()
        finally:
            await browser.close()
        return html

async def main():
    print("\n" + "="*100)
    print("DEBUG: ALL PRICES WITH CONTEXT - LISTING 119084515")
    print("="*100)

    try:
        html = await get_html()
        soup = BeautifulSoup(html, 'lxml')
        full_text = soup.get_text()

        print("\nSearching for all prices with context...")
        print("-" * 100)

        # Find all prices (4-7 digit numbers)
        prices_found = []

        for match in re.finditer(r'\b(\d{4,7})\b', full_text):
            price_str = match.group(1)
            amount = int(price_str)

            if 5000 < amount < 10000000:
                # Get context (200 chars before and after)
                start = max(0, match.start() - 200)
                end = min(len(full_text), match.end() + 200)
                context = full_text[start:end]

                # Clean up context for display
                context_display = context.replace('\n', ' ').strip()
                if len(context_display) > 300:
                    context_display = context_display[:300] + "..."

                prices_found.append({
                    'amount': amount,
                    'price_str': price_str,
                    'position': match.start(),
                    'context': context_display
                })

        # Also find formatted numbers
        for match in re.finditer(r'(\d{1,3}(?:[,\s]\d{3})+)', full_text):
            price_raw = match.group(1)
            price_clean = price_raw.replace(' ', '').replace(',', '')
            amount = int(price_clean)

            if 5000 < amount < 10000000:
                # Check if this amount is already found
                if not any(p['amount'] == amount for p in prices_found):
                    # Get context
                    start = max(0, match.start() - 200)
                    end = min(len(full_text), match.end() + 200)
                    context = full_text[start:end]

                    context_display = context.replace('\n', ' ').strip()
                    if len(context_display) > 300:
                        context_display = context_display[:300] + "..."

                    prices_found.append({
                        'amount': amount,
                        'price_str': price_raw,
                        'position': match.start(),
                        'context': context_display
                    })

        # Sort by position
        prices_found.sort(key=lambda x: x['position'])

        print(f"\nFound {len(prices_found)} unique prices:\n")

        for i, price_info in enumerate(prices_found, 1):
            print(f"[{i}] POSITION {price_info['position']:,}")
            print(f"    Amount: {price_info['amount']:,}")
            print(f"    Formatted: {price_info['price_str']}")
            print(f"    Context: ...{price_info['context']}...")
            print()

        if prices_found:
            print("-" * 100)
            print("\nSUMMARY:")
            print(f"First price found: {prices_found[0]['amount']:,}")
            usd_range = [p for p in prices_found if p['amount'] < 300000]
            if usd_range:
                print(f"First USD-range price (< 300k): {usd_range[0]['amount']:,}")
            else:
                print("No prices in USD range (< 300k) found")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*100)

if __name__ == '__main__':
    asyncio.run(main())
