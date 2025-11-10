#!/usr/bin/env python3
"""
Debug script to show what Georgian label extraction finds for price
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from parser import MyAutoParser

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
    print("DEBUG: GEORGIAN LABELED FIELD EXTRACTION - LISTING 119084515")
    print("="*80)

    try:
        html = await get_html()
        soup = BeautifulSoup(html, 'lxml')

        # Extract Georgian labeled fields
        fields = MyAutoParser.extract_georgian_labeled_fields(soup)

        print("\nExtracted Georgian Labeled Fields:")
        print("-" * 80)

        if fields:
            for field_name, field_value in fields.items():
                if isinstance(field_value, dict):
                    print(f"\n{field_name}:")
                    for sub_key, sub_val in field_value.items():
                        val_str = str(sub_val)[:100] if sub_val else None
                        print(f"  {sub_key}: {val_str}")
                else:
                    val_str = str(field_value)[:100] if field_value else None
                    print(f"{field_name}: {val_str}")

            # Specifically look for prices
            print("\n" + "-" * 80)
            print("\nPRICE-RELATED FIELDS:")
            price_fields = {k: v for k, v in fields.items() if 'price' in str(k).lower() or (isinstance(v, dict) and any('price' in str(x).lower() for x in v.keys()))}

            if price_fields:
                for field_name, field_value in price_fields.items():
                    print(f"  {field_name}: {field_value}")
            else:
                print("  No price fields found in extracted data")

            # Check the "pricing" or "price" key if it exists
            if 'pricing' in fields:
                print(f"\n  pricing object: {fields['pricing']}")
            if 'price' in fields:
                print(f"  price field: {fields['price']}")

        else:
            print("No Georgian labeled fields found!")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*80)

if __name__ == '__main__':
    asyncio.run(main())
