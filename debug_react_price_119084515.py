#!/usr/bin/env python3
"""
Debug script to show what React data extraction finds
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import asyncio
from playwright.async_api import async_playwright
from parser import MyAutoParser
import json

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
    print("DEBUG: REACT DATA EXTRACTION - LISTING 119084515")
    print("="*80)

    try:
        html = await get_html()

        print("\nExtracting React data...")
        react_data = MyAutoParser.extract_react_data_from_scripts(html)

        if react_data:
            print(f"\n✅ Found React data!")
            print(f"Keys: {list(react_data.keys())}")

            # Pretty print the data
            print("\n" + "-" * 80)
            print("React Data Content:")
            print("-" * 80)

            # Try to pretty print as JSON
            try:
                print(json.dumps(react_data, ensure_ascii=False, indent=2)[:2000])
                print(f"... (truncated)")
            except:
                print(str(react_data)[:2000])

            # Look for price fields
            print("\n" + "-" * 80)
            print("PRICE-RELATED FIELDS IN REACT DATA:")
            print("-" * 80)

            def find_prices(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        new_path = f"{path}.{key}" if path else key
                        if 'price' in key.lower():
                            print(f"  {new_path}: {value}")
                        find_prices(value, new_path)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj[:3]):  # Limit to first 3 items
                        new_path = f"{path}[{i}]"
                        find_prices(item, new_path)

            find_prices(react_data)

        else:
            print("\n❌ No React data found!")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*80)

if __name__ == '__main__':
    asyncio.run(main())
