#!/usr/bin/env python3
"""
Test GROBID for extracting metadata from scientific PDFs.
Uses GROBID's public demo service.
"""

import requests
import json
import xml.etree.ElementTree as ET
from pathlib import Path

def extract_with_grobid(pdf_path, grobid_url="https://cloud.science-miner.com/grobid"):
    """
    Extract metadata from PDF using GROBID service.

    Args:
        pdf_path: Path to PDF file
        grobid_url: GROBID service URL (default: public demo service)

    Returns:
        dict with extracted metadata
    """

    # GROBID API endpoints
    endpoints = {
        'header': f'{grobid_url}/api/processHeaderDocument',
        'full': f'{grobid_url}/api/processFulltextDocument',
        'references': f'{grobid_url}/api/processReferences',
    }

    results = {}

    print(f"Processing PDF: {pdf_path}")
    print(f"Using GROBID service: {grobid_url}\n")

    # Read PDF file
    with open(pdf_path, 'rb') as pdf_file:
        files = {'input': pdf_file}

        # Extract header (title, authors, abstract, affiliations)
        print("1. Extracting header metadata (title, authors, abstract, affiliations)...")
        try:
            response = requests.post(
                endpoints['header'],
                files={'input': open(pdf_path, 'rb')},
                data={'consolidateHeader': '1'},
                timeout=60
            )

            if response.status_code == 200:
                results['header_xml'] = response.text
                results['header_parsed'] = parse_grobid_header(response.text)
                print("✓ Header extraction successful")
            else:
                print(f"✗ Header extraction failed: {response.status_code}")
                results['header_error'] = response.text
        except Exception as e:
            print(f"✗ Header extraction error: {e}")
            results['header_error'] = str(e)

        # Extract full document (includes references)
        print("\n2. Extracting full document (includes references)...")
        try:
            response = requests.post(
                endpoints['full'],
                files={'input': open(pdf_path, 'rb')},
                data={
                    'consolidateHeader': '1',
                    'consolidateCitations': '1',
                    'includeRawCitations': '1',
                    'includeRawAffiliations': '1',
                    'teiCoordinates': ['biblStruct', 'persName', 'figure', 'ref', 'formula', 's']
                },
                timeout=120
            )

            if response.status_code == 200:
                results['full_xml'] = response.text
                results['full_parsed'] = parse_grobid_full(response.text)
                print("✓ Full document extraction successful")
            else:
                print(f"✗ Full document extraction failed: {response.status_code}")
                results['full_error'] = response.text
        except Exception as e:
            print(f"✗ Full document extraction error: {e}")
            results['full_error'] = str(e)

    return results


def parse_grobid_header(xml_text):
    """Parse GROBID header XML to extract structured metadata."""

    try:
        # Define TEI namespace
        ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

        root = ET.fromstring(xml_text)

        metadata = {
            'title': None,
            'authors': [],
            'affiliations': [],
            'abstract': None,
            'keywords': [],
            'date': None
        }

        # Extract title
        title_elem = root.find('.//tei:titleStmt/tei:title[@type="main"]', ns)
        if title_elem is not None and title_elem.text:
            metadata['title'] = title_elem.text.strip()

        # Extract authors and affiliations
        author_elems = root.findall('.//tei:sourceDesc//tei:author', ns)

        for idx, author_elem in enumerate(author_elems):
            author_info = {
                'id': idx,
                'first_name': None,
                'middle_name': None,
                'last_name': None,
                'full_name': None,
                'email': None,
                'affiliations': []
            }

            # Name components
            persName = author_elem.find('.//tei:persName', ns)
            if persName is not None:
                forename_elems = persName.findall('.//tei:forename', ns)
                for fn in forename_elems:
                    fn_type = fn.get('type', '')
                    if fn_type == 'first':
                        author_info['first_name'] = fn.text
                    elif fn_type == 'middle':
                        author_info['middle_name'] = fn.text

                surname = persName.find('.//tei:surname', ns)
                if surname is not None and surname.text:
                    author_info['last_name'] = surname.text

            # Construct full name
            name_parts = [
                author_info.get('first_name'),
                author_info.get('middle_name'),
                author_info.get('last_name')
            ]
            author_info['full_name'] = ' '.join(filter(None, name_parts))

            # Email
            email_elem = author_elem.find('.//tei:email', ns)
            if email_elem is not None and email_elem.text:
                author_info['email'] = email_elem.text.strip()

            # Affiliations
            affil_elems = author_elem.findall('.//tei:affiliation', ns)
            for affil in affil_elems:
                affil_info = {
                    'institution': None,
                    'department': None,
                    'laboratory': None,
                    'address': {},
                    'raw_text': None
                }

                # Get coordinates if available
                coords = affil.get('coords', '')
                if coords:
                    affil_info['coordinates'] = coords

                # Institution
                org = affil.find('.//tei:orgName[@type="institution"]', ns)
                if org is not None and org.text:
                    affil_info['institution'] = org.text.strip()

                # Department
                dept = affil.find('.//tei:orgName[@type="department"]', ns)
                if dept is not None and dept.text:
                    affil_info['department'] = dept.text.strip()

                # Lab
                lab = affil.find('.//tei:orgName[@type="laboratory"]', ns)
                if lab is not None and lab.text:
                    affil_info['laboratory'] = lab.text.strip()

                # Address components
                addr_elem = affil.find('.//tei:address', ns)
                if addr_elem is not None:
                    for child in addr_elem:
                        tag = child.tag.replace('{http://www.tei-c.org/ns/1.0}', '')
                        if child.text:
                            affil_info['address'][tag] = child.text.strip()

                # Raw text
                raw_text_parts = [affil_info.get('department'), affil_info.get('laboratory'),
                                 affil_info.get('institution')]
                raw_text_parts.extend(affil_info['address'].values())
                affil_info['raw_text'] = ', '.join(filter(None, raw_text_parts))

                author_info['affiliations'].append(affil_info)

            metadata['authors'].append(author_info)

        # Extract abstract
        abstract_elem = root.find('.//tei:profileDesc/tei:abstract/tei:div/tei:p', ns)
        if abstract_elem is not None:
            # Get text content, preserving structure
            abstract_text = ET.tostring(abstract_elem, encoding='unicode', method='text')
            metadata['abstract'] = abstract_text.strip()

        # Extract keywords
        keyword_elems = root.findall('.//tei:keywords/tei:term', ns)
        metadata['keywords'] = [kw.text.strip() for kw in keyword_elems if kw.text]

        return metadata

    except Exception as e:
        return {'error': f"Failed to parse header XML: {e}"}


def parse_grobid_full(xml_text):
    """Parse GROBID full document XML to extract references and coordinates."""

    try:
        ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
        root = ET.fromstring(xml_text)

        data = {
            'references': [],
            'has_coordinates': False
        }

        # Extract references
        ref_elems = root.findall('.//tei:back/tei:div[@type="references"]/tei:listBibl/tei:biblStruct', ns)

        for idx, ref_elem in enumerate(ref_elems):
            ref_info = {
                'id': idx,
                'raw_text': None,
                'title': None,
                'authors': [],
                'journal': None,
                'volume': None,
                'issue': None,
                'pages': None,
                'year': None,
                'doi': None,
                'coordinates': None
            }

            # Get coordinates if available
            coords = ref_elem.get('coords', '')
            if coords:
                ref_info['coordinates'] = coords
                data['has_coordinates'] = True

            # Title
            title_elem = ref_elem.find('.//tei:analytic/tei:title[@type="main"]', ns) or \
                        ref_elem.find('.//tei:monogr/tei:title', ns)
            if title_elem is not None and title_elem.text:
                ref_info['title'] = title_elem.text.strip()

            # Authors
            author_elems = ref_elem.findall('.//tei:analytic/tei:author', ns)
            for auth in author_elems:
                persName = auth.find('.//tei:persName', ns)
                if persName is not None:
                    first_name = None
                    last_name = None

                    forename = persName.find('.//tei:forename[@type="first"]', ns)
                    if forename is not None and forename.text:
                        first_name = forename.text.strip()

                    surname = persName.find('.//tei:surname', ns)
                    if surname is not None and surname.text:
                        last_name = surname.text.strip()

                    if first_name or last_name:
                        full_name = f"{first_name or ''} {last_name or ''}".strip()
                        ref_info['authors'].append(full_name)

            # Journal/venue
            journal_elem = ref_elem.find('.//tei:monogr/tei:title', ns)
            if journal_elem is not None and journal_elem.text:
                ref_info['journal'] = journal_elem.text.strip()

            # Volume, issue, pages
            imprint = ref_elem.find('.//tei:monogr/tei:imprint', ns)
            if imprint is not None:
                volume = imprint.find('.//tei:biblScope[@unit="volume"]', ns)
                if volume is not None and volume.text:
                    ref_info['volume'] = volume.text.strip()

                issue = imprint.find('.//tei:biblScope[@unit="issue"]', ns)
                if issue is not None and issue.text:
                    ref_info['issue'] = issue.text.strip()

                pages = imprint.find('.//tei:biblScope[@unit="page"]', ns)
                if pages is not None:
                    from_page = pages.get('from')
                    to_page = pages.get('to')
                    if from_page and to_page:
                        ref_info['pages'] = f"{from_page}-{to_page}"
                    elif pages.text:
                        ref_info['pages'] = pages.text.strip()

                # Year
                date_elem = imprint.find('.//tei:date[@type="published"]', ns)
                if date_elem is not None:
                    year = date_elem.get('when', '')
                    if year:
                        ref_info['year'] = year[:4]  # Extract year

            # DOI
            doi_elem = ref_elem.find('.//tei:idno[@type="DOI"]', ns)
            if doi_elem is not None and doi_elem.text:
                ref_info['doi'] = doi_elem.text.strip()

            data['references'].append(ref_info)

        return data

    except Exception as e:
        return {'error': f"Failed to parse full document XML: {e}"}


def main():
    pdf_path = "sample_paper.pdf"

    if not Path(pdf_path).exists():
        print(f"Error: PDF file not found: {pdf_path}")
        return

    # Extract metadata using GROBID
    results = extract_with_grobid(pdf_path)

    # Save raw XML results
    if 'header_xml' in results:
        with open('grobid_header.xml', 'w') as f:
            f.write(results['header_xml'])
        print("\n✓ Saved header XML to: grobid_header.xml")

    if 'full_xml' in results:
        with open('grobid_full.xml', 'w') as f:
            f.write(results['full_xml'])
        print("✓ Saved full document XML to: grobid_full.xml")

    # Save parsed results as JSON
    parsed_data = {}
    if 'header_parsed' in results:
        parsed_data['header'] = results['header_parsed']
    if 'full_parsed' in results:
        parsed_data['full'] = results['full_parsed']

    with open('grobid_results.json', 'w') as f:
        json.dump(parsed_data, f, indent=2)
    print("✓ Saved parsed results to: grobid_results.json")

    # Display summary
    print("\n" + "="*70)
    print("EXTRACTION SUMMARY")
    print("="*70)

    if 'header_parsed' in results:
        header = results['header_parsed']

        print(f"\n📄 TITLE: {header.get('title', 'N/A')}")

        print(f"\n👥 AUTHORS ({len(header.get('authors', []))}):")
        for i, author in enumerate(header.get('authors', [])[:5], 1):  # Show first 5
            print(f"   {i}. {author.get('full_name', 'N/A')}")
            if author.get('email'):
                print(f"      Email: {author['email']}")
            if author.get('affiliations'):
                for affil in author['affiliations']:
                    print(f"      Affiliation: {affil.get('raw_text', 'N/A')}")

        if len(header.get('authors', [])) > 5:
            print(f"   ... and {len(header['authors']) - 5} more")

        print(f"\n📝 ABSTRACT:")
        abstract = header.get('abstract', 'N/A')
        if abstract and abstract != 'N/A':
            print(f"   {abstract[:300]}...")
        else:
            print("   N/A")

    if 'full_parsed' in results:
        full = results['full_parsed']

        print(f"\n📚 REFERENCES ({len(full.get('references', []))}):")
        for i, ref in enumerate(full.get('references', [])[:3], 1):  # Show first 3
            print(f"   {i}. {ref.get('title', 'N/A')}")
            if ref.get('authors'):
                authors_str = ', '.join(ref['authors'][:3])
                if len(ref['authors']) > 3:
                    authors_str += ' et al.'
                print(f"      Authors: {authors_str}")
            if ref.get('journal'):
                print(f"      Journal: {ref['journal']}")
            if ref.get('year'):
                print(f"      Year: {ref['year']}")
            if ref.get('doi'):
                print(f"      DOI: {ref['doi']}")
            if ref.get('coordinates'):
                print(f"      📍 Coordinates: {ref['coordinates']}")

        if len(full.get('references', [])) > 3:
            print(f"   ... and {len(full['references']) - 3} more")

        if full.get('has_coordinates'):
            print("\n✓ Coordinate information is available for linking to source PDF!")

    print("\n" + "="*70)


if __name__ == '__main__':
    main()
