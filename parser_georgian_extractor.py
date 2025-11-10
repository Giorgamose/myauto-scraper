#!/usr/bin/env python3
"""
Extract vehicle fields from Georgian-labeled HTML structure
This module handles the MyAuto.ge detail page structure where labels are in one span
and values are in an adjacent span with font-medium class
"""

from bs4 import BeautifulSoup
import re
import sys
import os

if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

def extract_vehicle_details_georgian(html):
    """
    Extract all vehicle details using Georgian labels
    Handles structure: <span>label:</span><span class="font-medium">value</span>
    """
    soup = BeautifulSoup(html, "lxml")

    data = {}

    # Find all labeled property pairs
    # Look for divs containing property labels with values
    divs = soup.find_all('div')

    for div in divs:
        # Get text content
        text = div.get_text(strip=True)

        # Check if this looks like a property pair
        if ':' not in text:
            continue

        # Split on first colon
        parts = text.split(':', 1)
        if len(parts) != 2:
            continue

        label = parts[0].strip()
        value = parts[1].strip()

        # Skip if label or value is empty
        if not label or not value:
            continue

        # Skip UI labels
        if any(skip in label for skip in ['მთავარი', 'გვერდი', 'იყიდება', 'შენახვა', 'გაზიარება']):
            continue

        # Store the raw label-value pair
        print(f"  Found: {label}: {value}")
        data[label] = value

    # Now map Georgian labels to database fields
    mapping = {
        'მწარმოებელი': 'make',
        'მოდელი': 'model',
        'წელი': 'year',
        'კატეგორია': 'category',
        'გარბენი': 'mileage_km',
        'საწვავის ტიპი': 'fuel_type',
        'ძრავის მოცულობა': 'displacement_liters',
        'ძრავი': 'displacement_liters',  # Alternative label
        'ცილინდრები': 'cylinders',
        'გადაცემათა კოლოფი': 'transmission',
        'კოლოფი': 'transmission',  # Alternative
        'წამყვანი თვლები': 'drive_type',
        'კარები': 'doors',
        'აირბეგი': 'seats',
        'საჭე': 'wheel_position',
        'ფერი': 'color',
        'სალონის ფერი': 'interior_color',
        'სალონის მასალა': 'interior_material',
        'ფასი': 'price',
        'განბაჟება': 'customs_cleared',
        'ტექ. დათვალიერება': 'technical_inspection',
        'კატალიზატორი': 'has_catalytic_converter',
        'გაცვლა': 'exchange_possible',
    }

    extracted = {}

    for georgian, english_field in mapping.items():
        if georgian in data:
            value = data[georgian]

            # Convert value based on field type
            if english_field in ['year', 'cylinders', 'doors', 'seats', 'view_count']:
                # Extract number
                match = re.search(r'\d+', value)
                extracted[english_field] = int(match.group()) if match else None

            elif english_field in ['mileage_km']:
                # Extract number, remove 'km'
                match = re.search(r'\d+', value.replace(',', ''))
                extracted[english_field] = int(match.group()) if match else None

            elif english_field == 'price':
                # Extract number, remove commas and currency
                match = re.search(r'\d+', value.replace(',', ''))
                extracted[english_field] = int(match.group()) if match else None

            elif english_field == 'displacement_liters':
                # Extract float
                match = re.search(r'\d+\.?\d*', value)
                extracted[english_field] = float(match.group()) if match else None

            elif english_field in ['customs_cleared', 'technical_inspection', 'has_catalytic_converter', 'exchange_possible']:
                # Boolean: check for Georgian "კი" (yes) or similar
                extracted[english_field] = 1 if any(x in value.lower() for x in ['კი', 'true', 'yes']) else 0

            else:
                # String field
                extracted[english_field] = value

            if extracted.get(english_field) is not None:
                print(f"    Mapped to {english_field}: {extracted[english_field]}")

    return extracted


if __name__ == "__main__":
    print("[*] Testing Georgian field extraction...\n")

    with open("debug_listing.html", "r", encoding="utf-8") as f:
        html = f.read()

    print("[*] Extracting fields...\n")
    result = extract_vehicle_details_georgian(html)

    print(f"\n[*] Extracted {len(result)} fields:")
    import json
    print(json.dumps(result, indent=2, default=str, ensure_ascii=False))
