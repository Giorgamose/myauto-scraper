#!/usr/bin/env python3
"""
Simple regex-based extraction of Georgian fields
"""

import re
import sys
import os

if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

with open("debug_listing.html", "r", encoding="utf-8") as f:
    html = f.read()

# Remove HTML tags to get just text
# But keep structure somewhat
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, "lxml")
text = soup.get_text()

print("[*] Searching for specifications in page text...\n")

# Georgian labels and what to search for
specs = {
    'გარბენი': r'გარბენი[\s:]*(\d+[,\d]*\s*km|\d+)',
    'საწვავის ტიპი': r'საწვავის ტიპი[\s:]*([ბდ][^:\n]*)',  # ბენზინი, დიზელი
    'ძრავის მოცულობა': r'ძრავის მოცულობა[\s:]*([0-9.]+)',
    'ძრავი': r'ძრავი[\s:]*([0-9.]+)',
    'ცილინდრები': r'ცილინდრები[\s:]*(\d+)',
    'გადაცემათა კოლოფი': r'გადაცემათა კოლოფი[\s:]*([^\n:]+)',
    'კოლოფი': r'კოლოფი[\s:]*([^\n:]+)',
    'წამყვანი თვლები': r'წამყვანი თვლები[\s:]*([^\n:]+)',
    'კარები': r'კარები[\s:]*([^\n:]+)',
    'აირბეგი': r'აირბეგი[\s:]*(\d+)',
    'საჭე': r'საჭე[\s:]*([^\n:]+)',
    'ფერი': r'^ფერი[\s:]*([^\n:]+)',
    'სალონის ფერი': r'სალონის ფერი[\s:]*([^\n:]+)',
    'სალონის მასალა': r'სალონის მასალა[\s:]*([^\n:]+)',
    'მწარმოებელი': r'მწარმოებელი[\s:]*([^\n:]+)',
    'მოდელი': r'მოდელი[\s:]*([^\n:]+)',
    'წელი': r'წელი[\s:]*(\d{4})',
    'კატეგორია': r'კატეგორია[\s:]*([^\n:]+)',
    'ფასი': r'ფასი[\s:]*([0-9,]+)',
}

found = {}

for label, pattern in specs.items():
    matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)

    if matches:
        # Take the first match
        value = matches[0].strip()

        # Clean up the value
        value = value.replace('  ', ' ').strip()

        # Remove Georgian letters for some fields to get cleaner values
        if label in ['გარბენი', 'ძრავი', 'ძრავის მოცულობა']:
            # Keep just numbers
            value_clean = re.sub(r'[ა-ჰ\s]', '', value)
            value = value_clean if value_clean else value

        print(f"  {label}: {value}")
        found[label] = value

print(f"\n[OK] Found {len(found)} specifications")

# Now also look for key-value pairs in plain text
print(f"\n[*] Looking for all colon-separated pairs in specs section...\n")

# Extract the part with specs
if "მწარმოებელი:Toyota" in text and "ძირითადი პარამეტრები" in text:
    # Find the relevant section
    spec_start = text.find("მწარმოებელი:Toyota")

    if spec_start > 0:
        # Get 2000 chars from this point
        spec_section = text[spec_start:spec_start+2000]

        print(f"Specification section ({len(spec_section)} chars):")
        print(f"  {spec_section[:400]}\n")

        # Try to parse Georgian label:value pairs
        # They are concatenated like: "მწარმოებელი:Toyotaმოდელი:Land..."
        # So value ends when we hit the next Georgian word (label)

        all_labels = [
            'მწარმოებელი', 'მოდელი', 'წელი', 'კატეგორია', 'გარბენი',
            'საწვავის ტიპი', 'ძრავის მოცულობა', 'ცილინდრები',
            'გადაცემათა კოლოფი', 'წამყვანი თვლები', 'კარები', 'აირბეგი',
            'საჭე', 'ფერი', 'სალონის ფერი', 'სალონის მასალა'
        ]

        print("[*] Parsing label:value pairs from concatenated text:\n")

        # Create pattern that matches label:value sequences
        # value is anything until the next label
        for i, label in enumerate(all_labels):
            # Find this label in the text
            idx = spec_section.find(label + ":")

            if idx >= 0:
                # Extract value - goes from after ':' until we hit another label or a digit followed by space
                value_start = idx + len(label) + 1

                # Find where the value ends (look for next Georgian label or end)
                value_end = len(spec_section)

                for other_label in all_labels:
                    if other_label != label:
                        next_idx = spec_section.find(other_label + ":", value_start)
                        if next_idx > 0 and next_idx < value_end:
                            value_end = next_idx

                value = spec_section[value_start:value_end].strip()

                # Clean up - remove Georgian letters to see the values
                value_display = value[:50]
                print(f"  {label}: {value_display}")

