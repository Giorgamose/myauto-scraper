#!/usr/bin/env python3
"""
Detailed extraction of all vehicle fields from the page
"""

from bs4 import BeautifulSoup
import sys
import os
import re

if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

print("[*] Reading saved HTML...")
with open("debug_listing.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")

print("\n[*] Extracting vehicle information...\n")

# Get all text content
all_text = soup.get_text()

# Look for Georgian text patterns
print("[Georgian Labels Found in Page]")

# Property labels to search for (Georgian)
georgian_labels = {
    'მწარმოებელი': 'Make/Manufacturer',
    'მოდელი': 'Model',
    'წელი': 'Year',
    'კატეგორია': 'Category',
    'გარბენი': 'Mileage',
    'საწვავის ტიპი': 'Fuel Type',
    'ძრავის მოცულობა': 'Engine Displacement',
    'გადაცემის კოლოფი': 'Transmission',
    'ფერი': 'Color',
    'სხეულის ტიპი': 'Body Type',
    'საკიდი': 'Drive Type',
    'რეგისტრაცია': 'Registration',
    'განბაჟება': 'Customs Cleared',
    'ტექ.შემოწმება': 'Technical Inspection',
    'მდგომარეობა': 'Condition',
    'ფასი': 'Price',
    'ადგილი': 'Location',
    'გარკვევილი': 'Clear Title',
}

# Find each label and its corresponding value
found_data = {}

for georgian, english in georgian_labels.items():
    # Search for the Georgian label in the HTML
    if georgian in all_text:
        print(f"  ✓ Found: {english} ({georgian})")

        # Try to find the label element and extract nearby text
        elements = soup.find_all(lambda tag: tag.string and georgian in tag.string)
        for elem in elements[:1]:  # Get first match
            # Look in parent and siblings for the value
            parent = elem.parent
            next_sibling = parent.find_next_sibling()

            text_parts = []
            for part in parent.find_all(string=True):
                text_parts.append(part.strip())

            value = ' '.join([p for p in text_parts if p and georgian not in p])
            if value:
                found_data[english] = value[:100]

# Print found data
print("\n[Extracted Data]")
for field, value in found_data.items():
    print(f"  {field}: {value}")

# Look for the main specs line
print("\n[*] Looking for main spec line...")
spec_line = None
for text in all_text.split('\n'):
    if 'km' in text and ('დიზელი' in text or 'ბენზინი' in text):
        spec_line = text.strip()
        print(f"  Found: {spec_line}")
        break

# Look for price
print("\n[*] Looking for price...")
price_patterns = [
    r'[\d,]+\s*₾',
    r'[\d,]+\s*USD',
    r'\$\s*[\d,]+',
]

for pattern in price_patterns:
    matches = re.findall(pattern, all_text)
    if matches:
        print(f"  Found prices: {matches[:3]}")

# Look for all div/span content that might be structured data
print("\n[*] All divs with structured-looking content...]")
divs = soup.find_all('div')
for div in divs:
    text = div.get_text(strip=True)

    # Look for property patterns
    if ':' in text and 5 < len(text) < 200:
        # Check if it looks like a property
        parts = text.split(':')
        if len(parts) == 2 and len(parts[0]) < 50:
            print(f"  {text[:100]}")

# Extract directly from page structure
print("\n[*] Extracting from specific elements...")

# Find the main title area
h6 = soup.find('h6')
if h6:
    print(f"  H6 Title: {h6.get_text(strip=True)}")

# Find all spans and look for key data
spans = soup.find_all('span')
print(f"\n[*] Found {len(spans)} span elements")

# Look for spans with numbers (price, mileage, year)
for span in spans:
    text = span.get_text(strip=True)

    # Check if contains numbers and is interesting
    if any(char.isdigit() for char in text) and len(text) < 50:
        # Skip if it's just navigation or UI
        if not any(ui in text.lower() for ui in ['page', 'item', 'sort']):
            print(f"  Span: {text}")

print("\n[OK] Extraction complete!")
