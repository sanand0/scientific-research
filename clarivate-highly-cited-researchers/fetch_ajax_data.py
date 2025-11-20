#!/usr/bin/env python3
"""
Fetch researcher data from Clarivate AJAX endpoint
"""

import requests
import json
import time

def fetch_researchers_ajax(page=1):
    """Fetch researchers via AJAX endpoint"""

    # WordPress AJAX endpoints
    ajax_url = "https://clarivate.com/wp-admin/admin-ajax.php"

    # Try the action we saw in the URL
    params = {
        'action': 'clv_hcr_members_filter',
        'clv-paged': page,
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

    print(f"Fetching page {page}...")
    response = requests.post(ajax_url, data=params, headers=headers)

    print(f"Status code: {response.status_code}")
    print(f"Response length: {len(response.text)} chars")

    # Save first response for inspection
    if page == 1:
        with open('ajax_response.json', 'w', encoding='utf-8') as f:
            try:
                json.dump(response.json(), f, indent=2)
                print("Saved as JSON")
            except:
                # If not JSON, save as text
                with open('ajax_response.html', 'w', encoding='utf-8') as f2:
                    f2.write(response.text)
                print("Saved as HTML/text")

    return response

def main():
    response = fetch_researchers_ajax(1)

    # Try to parse response
    try:
        data = response.json()
        print(f"\nJSON response keys: {data.keys() if isinstance(data, dict) else 'Not a dict'}")
    except:
        print("\nNot JSON, checking HTML structure...")
        if '<' in response.text:
            print("Response contains HTML")
        else:
            print("Response is plain text")

    print(f"\nFirst 500 characters:\n{response.text[:500]}")

if __name__ == '__main__':
    main()
