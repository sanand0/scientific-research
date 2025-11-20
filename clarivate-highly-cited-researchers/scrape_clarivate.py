#!/usr/bin/env python3
"""
Scrape Clarivate Highly Cited Researchers list
"""

import requests
import json
import time
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd

def scrape_researchers_page(page_num=1):
    """Scrape a single page of researchers"""
    url = f"https://clarivate.com/highly-cited-researchers/?action=clv_hcr_members_filter&clv-paged={page_num}&clv-category=&clv-institution=&clv-region=&clv-name="

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print(f"Fetching page {page_num}...")
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error: Status code {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    # Save raw HTML for inspection
    if page_num == 1:
        with open('page_sample.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print("Saved sample HTML to page_sample.html")

    return soup

def extract_researchers_from_soup(soup):
    """Extract researcher data from parsed HTML"""
    researchers = []

    # Try multiple possible selectors
    possible_selectors = [
        'div.researcher-card',
        'div.hcr-member',
        'div.member-card',
        'article.researcher',
        'li.researcher',
        'tr.researcher-row'
    ]

    for selector in possible_selectors:
        elements = soup.select(selector)
        if elements:
            print(f"Found {len(elements)} elements with selector: {selector}")
            break

    # If no structured elements found, look for JSON data
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string and 'researcher' in script.string.lower():
            print("Found potential JSON data in script tag")
            # Try to extract JSON
            try:
                # Look for common patterns
                if 'var researchers' in script.string or 'window.researchers' in script.string:
                    print("Found researchers variable in JavaScript")
            except:
                pass

    return researchers

def main():
    print("Starting Clarivate Highly Cited Researchers scraper...")

    # Try to scrape first page
    soup = scrape_researchers_page(1)

    if soup:
        researchers = extract_researchers_from_soup(soup)
        print(f"\nExtracted {len(researchers)} researchers")

        # Look for pagination info
        pagination = soup.select('div.pagination, nav.pagination, ul.pagination')
        if pagination:
            print(f"Found pagination elements: {len(pagination)}")

        # Try to find total count
        for text in soup.stripped_strings:
            if 'researcher' in text.lower() and any(char.isdigit() for char in text):
                print(f"Potential count text: {text}")

if __name__ == '__main__':
    main()
