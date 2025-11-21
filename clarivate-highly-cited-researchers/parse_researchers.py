#!/usr/bin/env python3
"""
Parse Clarivate Highly Cited Researchers from AJAX HTML response
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import csv
from urllib.parse import parse_qs, urlparse

def fetch_and_parse_page(page_num):
    """Fetch and parse a single page of researchers"""

    ajax_url = "https://clarivate.com/wp-admin/admin-ajax.php"

    params = {
        'action': 'clv_hcr_members_filter',
        'clv-paged': page_num,
        'clv-category': '',
        'clv-institution': '',
        'clv-region': '',
        'clv-name': ''
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest'
    }

    print(f"Fetching page {page_num}...", end=' ')
    response = requests.post(ajax_url, data=params, headers=headers)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    researchers = []

    # Find all researcher entries - they're in tbody with class 'hcr-member'
    tbodies = soup.find_all('tbody', class_='hcr-member')

    print(f"Found {len(tbodies)} researchers")

    for tbody in tbodies:
        try:
            researcher = {}

            # Get the tr with class 'info'
            row = tbody.find('tr', class_='info')
            if not row:
                continue

            # Extract ResearcherID from data-rid attribute
            rid = row.get('data-rid', '')
            if rid:
                researcher['researcher_id'] = rid

            # Extract all text content from cells
            cells = row.find_all('td')

            # Structure: [image, name, category, institution, empty, claim_link]
            if len(cells) >= 4:
                # Cell 1: Name
                name_cell = cells[1]
                researcher['full_name'] = name_cell.get_text(strip=True)

                # Cell 2: Category/Field
                category_cell = cells[2]
                researcher['category'] = category_cell.get_text(strip=True)

                # Cell 3: Institution and Country
                institution_cell = cells[3]
                inst_text = institution_cell.get_text(strip=True)

                # Try to split institution and country (usually separated by comma)
                if ',' in inst_text:
                    parts = inst_text.rsplit(',', 1)
                    researcher['institution'] = parts[0].strip()
                    researcher['country'] = parts[1].strip()
                else:
                    researcher['institution'] = inst_text

            # Extract name from claim profile link for verification
            claim_link = tbody.find('a', href=lambda x: x and 'register' in x)
            if claim_link:
                url = claim_link.get('href')
                parsed = parse_qs(urlparse(url).query)
                if 'first_name' in parsed:
                    researcher['first_name'] = parsed['first_name'][0]
                if 'last_name' in parsed:
                    researcher['last_name'] = parsed['last_name'][0]

            # Extract image URL
            img = tbody.find('img')
            if img:
                researcher['image_url'] = img.get('src', '')

            # Assume 2025 for now (can be updated based on actual year field if found)
            researcher['year'] = 2025

            if researcher.get('full_name'):
                researchers.append(researcher)

        except Exception as e:
            print(f"Error parsing tbody: {e}")
            continue

    return researchers

def main():
    print("Starting Clarivate Highly Cited Researchers scraper\n")

    all_researchers = []

    # Fetch ALL pages (approximately 700 pages for ~7000 researchers at 10 per page)
    max_pages = 1000  # Set high limit, will stop when no more data

    for page in range(1, max_pages + 1):
        researchers = fetch_and_parse_page(page)

        if not researchers:
            print(f"No researchers found on page {page}, stopping.")
            break

        all_researchers.extend(researchers)

        # Be polite to the server
        time.sleep(1)

        # Check if this is the last page (might need to adjust based on pagination)
        if len(researchers) < 10:  # Assuming ~10 per page
            print("Reached last page")
            break

    print(f"\n\nTotal researchers collected: {len(all_researchers)}")

    # Save to JSON
    with open('researchers_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_researchers, f, indent=2, ensure_ascii=False)
    print(f"Saved to researchers_data.json")

    # Save to CSV
    if all_researchers:
        # Collect all unique fieldnames
        fieldnames = set()
        for r in all_researchers:
            fieldnames.update(r.keys())
        fieldnames = sorted(list(fieldnames))

        with open('researchers_data.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_researchers)
        print(f"Saved to researchers_data.csv")

        # Print sample
        print("\nSample researchers:")
        for r in all_researchers[:5]:
            print(f"  - {r.get('full_name', 'N/A')} | {r.get('institution', 'N/A')}")

if __name__ == '__main__':
    main()
