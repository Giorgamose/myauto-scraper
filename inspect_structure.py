#!/usr/bin/env python3
"""
Inspect the actual structure of vehicle elements
"""

from bs4 import BeautifulSoup
import sys
import os

if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

with open("debug_listing.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")

# Find elements with vehicle keywords
print("[*] Analyzing vehicle element structure...\n")

target_keywords = ["Toyota", "Land Cruiser", "2001"]

for keyword in target_keywords:
    print(f"\n[*] Elements containing '{keyword}':")
    elements = soup.find_all(string=lambda text: text and keyword in text)

    for i, elem in enumerate(elements[:3]):  # First 3 matches
        parent = elem.parent
        print(f"\n  Match {i+1}:")
        print(f"    Text: {elem.strip()[:50]}")
        print(f"    Immediate parent: <{parent.name}>")
        print(f"    Parent attributes: {dict(parent.attrs)}")

        # Show parent's children
        if parent.contents:
            print(f"    Parent content ({len(parent.contents)} items):")
            for j, child in enumerate(parent.contents[:3]):
                if isinstance(child, str):
                    child_str = str(child).strip()[:50]
                    if child_str:
                        print(f"      [{j}] Text: {child_str}")
                else:
                    print(f"      [{j}] <{child.name}> {dict(child.attrs)}")

        # Show parent's parent
        grandparent = parent.parent
        if grandparent:
            print(f"    Grandparent: <{grandparent.name}>")
            print(f"    Grandparent classes: {grandparent.get('class', [])}")

print("\n[*] Looking for price-like patterns...")
import re

# Find text that looks like prices
text_content = soup.get_text()
prices = re.findall(r'\$?\s*[\d,]+\s*(\$|₾|USD|GEL|EUR)?', text_content)
print(f"Found {len(prices)} price-like patterns")
if prices:
    for price in prices[:5]:
        print(f"  - {price}")

print("\n[*] Looking for mileage patterns...")
mileages = re.findall(r'[\d,]+\s*(km|mi|miles)', text_content, re.IGNORECASE)
print(f"Found {len(mileages)} mileage-like patterns")
if mileages:
    for mileage in mileages[:5]:
        print(f"  - {mileage}")

print("\n[OK] Inspection complete!")
