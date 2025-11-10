#!/usr/bin/env python3
"""
Debug script to find all prices on listing 119084515
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
        await page.goto('https://www.myauto.ge/ka/pr/119084515', timeout=15000)
        await page.wait_for_load_state('domcontentloaded')
        html = await page.content()
        await browser.close()
        return html

async def main():
    html = await get_html()
    soup = BeautifulSoup(html, 'lxml')
    full_text = soup.get_text()

    # Find all price-like numbers
    all_prices = re.findall(r'(\d{1,3}(?:[,\s]\d{3})+)', full_text)

    print('=== ALL PRICES FOUND ON PAGE ===\n')
    prices_dict = {}
    for price_raw in all_prices:
        price_clean = price_raw.replace(' ', '').replace(',', '')
        if price_clean.isdigit() and 5000 < int(price_clean) < 10000000:
            amount = int(price_clean)
            if amount not in prices_dict:
                prices_dict[amount] = price_raw

    if prices_dict:
        for amount in sorted(prices_dict.keys()):
            print(f'  {prices_dict[amount]} = {amount}')

        print(f'\n=== ANALYSIS ===')
        lowest = min(prices_dict.keys())
        highest = max(prices_dict.keys())

        print(f'Lowest price: {prices_dict[lowest]} = {lowest}')
        print(f'Highest price: {prices_dict[highest]} = {highest}')

        print(f'\n=== COMPARISON WITH ACTUAL ===')
        print(f'Expected USD price: 15,500')
        print(f'Expected GEL price: depends on rate')
        print(f'Current extraction: 25,200')
        print(f'Lowest on page: {lowest}')

        if lowest == 15500:
            print(f'\n✅ Lowest price IS 15,500 - our logic should work!')
        else:
            print(f'\n❌ Lowest price is NOT 15,500 - something else is lower')

            # Check if 15500 is even on the page
            if 15500 in prices_dict:
                print(f'   But 15,500 IS on the page!')
                print(f'   So there are prices lower than it: {[a for a in sorted(prices_dict.keys()) if a < 15500]}')
    else:
        print('No prices found in valid range')

if __name__ == '__main__':
    asyncio.run(main())
