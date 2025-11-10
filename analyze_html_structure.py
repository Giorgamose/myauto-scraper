#!/usr/bin/env python3
"""
Analyze the HTML structure around vehicle field labels
"""

from bs4 import BeautifulSoup
import sys
import os

if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

with open("debug_listing.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")

# Find where "მწარმოებელი" appears
print("[*] Finding 'მწარმოებელი' (Make) in HTML structure...\n")

elements = soup.find_all(lambda tag: tag.string and 'მწარმოებელი' in tag.string)
print(f"Found {len(elements)} matches\n")

for i, elem in enumerate(elements[:5]):
    print(f"\n[Match {i+1}]")
    print(f"  Element: <{elem.name}>")
    print(f"  Text: {elem.string[:60]}")
    print(f"  Parent: <{elem.parent.name}>")
    print(f"  Parent HTML: {str(elem.parent)[:200]}")

    # Look at siblings
    parent = elem.parent
    print(f"\n  Siblings of parent:")
    for j, sibling in enumerate(parent.find_next_siblings()[:3]):
        print(f"    [{j}] <{sibling.name}> {sibling.get_text(strip=True)[:60]}")

# Look for structured lists
print("\n\n[*] Looking for property lists...\n")

# Find divs that contain the spec section
spec_divs = soup.find_all('div')
for div in spec_divs:
    text = div.get_text(strip=True)

    if 'მწარმოებელი' in text and 'Toyota' in text and 'Land' in text:
        print(f"Found property section:")
        print(f"  Full text ({len(text)} chars): {text[:300]}")

        # Look at child elements
        print(f"\n  Child elements:")
        for i, child in enumerate(div.children):
            if isinstance(child, str):
                child_text = child.strip()
                if child_text:
                    print(f"    [{i}] Text: {child_text[:50]}")
            else:
                child_text = child.get_text(strip=True) if hasattr(child, 'get_text') else ''
                print(f"    [{i}] <{child.name}> {child_text[:50]}")

# Check for labeled lists
print("\n\n[*] Looking for :  (colon-separated) patterns...\n")

all_text = soup.get_text()
lines = all_text.split('\n')

for line in lines:
    if ':' in line and any(word in line for word in ['მწარმოებელი', 'მოდელი', 'წელი', 'ფასი']):
        print(f"  {line.strip()[:100]}")
