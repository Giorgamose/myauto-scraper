#!/usr/bin/env python3
"""
Extract all vehicle specifications from the detail page
Looks for the "ძირითადი პარამეტრები" (Main Parameters) section
"""

from bs4 import BeautifulSoup
import re
import sys
import os

if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

with open("debug_listing.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")

print("[*] Looking for specification sections...\n")

# Find the section containing main parameters
all_text = soup.get_text()

# Find "ძირითადი პარამეტრები" section
if "ძირითადი პარამეტრები" in all_text:
    print("[OK] Found 'Main Parameters' section\n")

    # Find the div/section containing this text
    specs_divs = soup.find_all(lambda tag: tag.string and "ძირითადი პარამეტრები" in tag.string)

    for specs_div in specs_divs[:1]:  # Get first match
        parent = specs_div.parent

        # Go up to find the container div
        while parent and parent.name != 'main' and len(parent.find_all()) > 20:
            parent = parent.parent

        # Get the text from this section and next siblings
        section_text = parent.get_text(strip=False) if parent else ""

        print(f"[*] Main Parameters section ({len(section_text)} chars):")
        print(f"    {section_text[:500]}\n")

        # Try to extract label:value pairs
        # They appear to be concatenated, e.g. "მწარმოებელი:Toyotaმოდელი:Land Cruiserწელი:2001"
        # Let's use regex to find them

        # Georgian labels we're looking for
        labels = [
            'მწარმოებელი', 'მოდელი', 'წელი', 'კატეგორია', 'გარბენი',
            'საწვავის ტიპი', 'ძრავის მოცულობა', 'ცილინდრები',
            'გადაცემათა კოლოფი', 'წამყვანი თვლები', 'კარები',
            'აირბეგი', 'საჭე', 'ფერი', 'სალონის ფერი', 'სალონის მასალა',
            'გაცვლა', 'ტექ. დათვალიერება', 'კატალიზატორი'
        ]

        print("[*] Extracting label:value pairs...\n")

        # Create pattern to find labels
        for label in labels:
            # Look for pattern: label:value (where value is before the next label)
            pattern = f"{label}:([^:{label}]*)"

            # Search in the section text
            matches = re.findall(pattern, section_text)

            if matches:
                # Get the first match and clean it
                value = matches[0].strip()

                # Remove Georgian and only keep the first word/number
                # Remove Georgian letters but keep numbers, spaces, dots, slashes, %
                value_clean = re.sub(r'[ა-ჰ]', '', value).strip()

                # Take only first token/meaningful part
                if value_clean:
                    first_part = value_clean.split()[0] if value_clean.split() else value_clean

                    print(f"  {label}: {first_part}")

# Alternative: look for structured lists (ul/li with property items)
print(f"\n[*] Looking for structured property lists...\n")

property_lists = soup.find_all('ul')
for ul in property_lists:
    items = ul.find_all('li')

    if len(items) > 3:  # Only interested in longer lists
        text_items = [li.get_text(strip=True) for li in items[:10]]

        # Check if these look like properties
        if any(':' in item for item in text_items):
            print(f"[OK] Found property list with {len(items)} items:")
            for item in text_items[:5]:
                print(f"    {item[:80]}")

print("\n[*] Done!")
