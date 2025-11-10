#!/usr/bin/env python3
"""
Debug script to show ALL numbers found on listing 119084515
This helps understand why we're picking 25,200 instead of 15,500
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
    print("DEBUG: ALL NUMBERS EXTRACTION - LISTING 119084515")
    print("="*80)

    try:
        html = await get_html()
        soup = BeautifulSoup(html, 'lxml')
        full_text = soup.get_text()

        print("\n[1] FORMATTED NUMBERS (with separators)")
        print("-" * 80)
        print("Pattern: \\d{1,3}(?:[,\\s]\\d{3})+")
        formatted = re.findall(r'(\d{1,3}(?:[,\s]\d{3})+)', full_text)

        if formatted:
            formatted_dict = {}
            for num_str in formatted:
                clean = num_str.replace(' ', '').replace(',', '')
                if clean.isdigit():
                    amount = int(clean)
                    if 5000 < amount < 10000000:
                        if amount not in formatted_dict:
                            formatted_dict[amount] = num_str

            if formatted_dict:
                print(f"Found {len(formatted_dict)} valid prices in range 5k-10M:")
                for amount in sorted(formatted_dict.keys()):
                    print(f"  {formatted_dict[amount]:>20} = {amount:>10,}")
            else:
                print(f"Found {len(formatted)} formatted numbers but none in valid range")
                print(f"Examples: {formatted[:10]}")
        else:
            print("No formatted numbers found!")

        print("\n[2] RAW NUMBERS (without separators)")
        print("-" * 80)
        print("Pattern: \\b(\\d{4,7})\\b")
        raw = re.findall(r'\b(\d{4,7})\b', full_text)

        if raw:
            raw_dict = {}
            for num_str in raw:
                if num_str.isdigit():
                    amount = int(num_str)
                    if 5000 < amount < 10000000:
                        if amount not in raw_dict:
                            raw_dict[amount] = num_str

            if raw_dict:
                print(f"Found {len(raw_dict)} valid prices in range 5k-10M:")
                for amount in sorted(raw_dict.keys()):
                    print(f"  {raw_dict[amount]:>20} = {amount:>10,}")
            else:
                print(f"Found {len(raw)} raw numbers but none in valid range")
                print(f"All raw numbers: {sorted(set(int(n) for n in raw if n.isdigit()))}")
        else:
            print("No raw numbers found!")

        print("\n[3] COMBINED (Lowest price selection)")
        print("-" * 80)

        # Combine both
        all_prices = {}

        for num_str in formatted:
            clean = num_str.replace(' ', '').replace(',', '')
            if clean.isdigit():
                amount = int(clean)
                if 5000 < amount < 10000000:
                    if amount not in all_prices:
                        all_prices[amount] = num_str

        for num_str in raw:
            if num_str.isdigit():
                amount = int(num_str)
                if 5000 < amount < 10000000:
                    if amount not in all_prices:
                        all_prices[amount] = num_str

        if all_prices:
            print(f"All prices combined: {sorted(all_prices.keys())}")
            lowest = min(all_prices.keys())
            print(f"\n✅ LOWEST (USD): {all_prices[lowest]} = {lowest}")

            # Analysis
            print("\n[ANALYSIS]")
            print(f"Expected USD price: 15,500")
            print(f"Expected GEL price: ~42,800")
            print(f"Actually selected: {all_prices[lowest]} = {lowest}")

            if lowest == 15500 or lowest == 15800:
                print(f"✅ SUCCESS - Correctly picking lower amount as USD")
            else:
                print(f"❌ PROBLEM - Not picking the USD price")
                if 15500 in all_prices:
                    print(f"   15,500 IS on the page: {all_prices[15500]}")
                if 15800 in all_prices:
                    print(f"   15,800 IS on the page: {all_prices[15800]}")
        else:
            print("No valid prices found in range 5k-10M!")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*80)

if __name__ == '__main__':
    asyncio.run(main())
