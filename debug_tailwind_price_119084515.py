#!/usr/bin/env python3
"""
Debug script looking for prices in specific Tailwind-styled elements
Based on user example: <p class="...text-[24px]...text-raisin-100...">15,800</p>
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
    print("DEBUG: TAILWIND-STYLED PRICE ELEMENTS - LISTING 119084515")
    print("="*100)

    try:
        html = await get_html()
        soup = BeautifulSoup(html, 'lxml')

        # Try different CSS selectors for price elements
        selectors = [
            # User's example selector
            'p[class*="text-[24px]"]',
            'p[class*="text-raisin"]',
            # More general Tailwind price selectors
            'p[class*="font-bold"]',
            # Elements with numbers and currency symbols
            'p:contains("USD")',
            'p:contains("$")',
            # Try finding by text pattern
            'p, div, span',
        ]

        print("\nSearching for price elements...")
        print("-" * 100)

        # Get all text elements and look for prices
        all_numbers = {}

        for elem_type in ['p', 'div', 'span']:
            for elem in soup.select(elem_type):
                text = elem.get_text(strip=True)
                if not text:
                    continue

                # Look for numbers with currency symbols or USD/GEL keywords
                has_price_keyword = any(k in text for k in ['$', 'USD', '₾', 'GEL', 'ფასი'])

                if has_price_keyword and len(text) < 500:  # Reasonable length for a price element
                    # Extract numbers from this element
                    numbers = re.findall(r'\d+', text)
                    if numbers:
                        price_nums = [int(n) for n in numbers if 5000 < int(n) < 10000000]
                        if price_nums:
                            elem_class = elem.get('class', 'no-class')
                            key = (elem_type, str(elem_class))
                            if key not in all_numbers:
                                all_numbers[key] = (text, price_nums)

        if all_numbers:
            print(f"\nFound {len(all_numbers)} price-related elements:\n")
            for (elem_type, class_attr), (text, numbers) in sorted(all_numbers.items()):
                print(f"[{elem_type}] {class_attr}")
                print(f"  Text: {text[:150]}")
                print(f"  Numbers found: {numbers}")
                print()
        else:
            print("\nNo price-related elements found with direct selection")

        # Also try a brute force approach - find any element with 4-7 digit numbers
        print("\n" + "-" * 100)
        print("\nBrute force: All elements containing 4-7 digit numbers...")
        print("-" * 100)

        number_elements = []

        for elem in soup.find_all(['p', 'div', 'span', 'h1', 'h2', 'h3']):
            text = elem.get_text(strip=True)
            if re.search(r'\d{4,7}', text) and len(text) < 300:
                # Extract the first number in valid price range
                for match in re.finditer(r'\b(\d{4,7})\b', text):
                    num = int(match.group(1))
                    if 5000 < num < 10000000:
                        class_attr = elem.get('class', 'no-class')
                        number_elements.append({
                            'tag': elem.name,
                            'class': class_attr,
                            'text': text[:200],
                            'number': num,
                            'position': len(elem.get_text(strip=True))
                        })
                        break  # Only first number per element

        # Sort by position in document
        number_elements.sort(key=lambda x: x['position'])

        if number_elements:
            print(f"\nFound {len(number_elements)} elements with price-range numbers:\n")
            for i, elem_info in enumerate(number_elements[:10], 1):  # Show first 10
                print(f"[{i}] <{elem_info['tag']}> - {elem_info['number']:,}")
                print(f"    Class: {elem_info['class']}")
                print(f"    Text: {elem_info['text']}...")
                print()
        else:
            print("No elements with price-range numbers found")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*100)

if __name__ == '__main__':
    asyncio.run(main())
