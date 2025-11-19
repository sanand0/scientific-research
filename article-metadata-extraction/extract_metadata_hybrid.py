#!/usr/bin/env python3
"""
Hybrid approach for extracting metadata from scientific PDFs.

Strategy:
1. Use PyMuPDF to extract text with coordinates (works for typeset PDFs)
2. Use GPT-4 (text API) to structure the extracted text
3. Link structured data back to PDF locations using coordinates

This approach is:
- Fast (text extraction is instant)
- Cheap (text API is 60x cheaper than vision API)
- Accurate for typeset PDFs
- Can be extended with OCR for scanned PDFs
"""

import os
import json
import fitz  # PyMuPDF
from pathlib import Path
from openai import OpenAI

def extract_text_with_coords(pdf_path, max_pages=None):
    """
    Extract text from PDF with coordinate information using PyMuPDF.

    Args:
        pdf_path: Path to PDF file
        max_pages: Maximum pages to extract (None = all)

    Returns:
        dict with text content and coordinate information
    """
    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    if max_pages:
        total_pages = min(total_pages, max_pages)

    print(f"Extracting text from {total_pages} pages...")

    pages_data = []

    for page_num in range(total_pages):
        page = doc[page_num]

        # Extract text blocks with coordinates
        # Each block: (x0, y0, x1, y1, "text", block_no, block_type)
        blocks = page.get_text("blocks")

        # Extract text with detailed position info
        text_dict = page.get_text("dict")

        # Simple text for each page
        page_text = page.get_text()

        pages_data.append({
            "page_num": page_num + 1,
            "text": page_text,
            "blocks": [
                {
                    "bbox": [b[0], b[1], b[2], b[3]],  # x0, y0, x1, y1
                    "text": b[4],
                    "block_no": b[5],
                    "block_type": b[6]
                }
                for b in blocks if b[6] == 0  # Only text blocks (type 0)
            ],
            "width": page.rect.width,
            "height": page.rect.height
        })

    doc.close()

    print(f"✓ Extracted text from {total_pages} pages")

    return {
        "total_pages": total_pages,
        "pages": pages_data
    }


def extract_header_metadata(pages_data, client):
    """
    Extract title, authors, affiliations, and abstract using GPT-4.

    Args:
        pages_data: Extracted text from first few pages
        client: OpenAI client

    Returns:
        dict with structured metadata
    """

    print("\n" + "="*70)
    print("EXTRACTING HEADER METADATA")
    print("="*70)

    # Combine text from first 3 pages (where header info typically is)
    header_text = "\n\n--- PAGE BREAK ---\n\n".join(
        [p["text"] for p in pages_data["pages"][:3]]
    )

    prompt = f"""You are analyzing extracted text from the first few pages of a scientific research paper.
Extract the following metadata in JSON format:

{{
  "title": "Full paper title",
  "authors": [
    {{
      "name": "Full author name",
      "affiliations": ["Affiliation 1", "Affiliation 2"],
      "email": "email if available"
    }}
  ],
  "abstract": "Full abstract text",
  "keywords": ["keyword1", "keyword2"],
  "doi": "DOI if present",
  "publication_info": {{
    "journal": "journal name if available",
    "year": "publication year if available",
    "volume": "volume if available",
    "issue": "issue if available",
    "pages": "page range if available"
  }}
}}

IMPORTANT INSTRUCTIONS:
1. Extract ALL authors with their complete affiliations
2. Author affiliations are often marked with superscript numbers or symbols - match these carefully
3. Extract the complete abstract verbatim
4. Include all keywords if present
5. If a field is not found, use null
6. Be precise and accurate

PAPER TEXT:
{header_text}

Return ONLY valid JSON, no other text or explanation."""

    print("Sending to GPT-4 API...")

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a precise metadata extraction assistant for scientific papers."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=3000
        )

        result_text = response.choices[0].message.content.strip()

        # Parse JSON
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
            result_text = result_text.strip()

        metadata = json.loads(result_text)
        print("✓ Successfully extracted header metadata")

        return metadata

    except Exception as e:
        print(f"✗ Error: {e}")
        return {"error": str(e)}


def find_text_location(pages_data, search_text, start_page=0):
    """
    Find approximate location of text in PDF pages.

    Args:
        pages_data: Extracted page data
        search_text: Text to find
        start_page: Page index to start search

    Returns:
        dict with location info
    """

    search_text_lower = search_text.lower()[:50]  # First 50 chars

    for page in pages_data["pages"][start_page:]:
        page_text_lower = page["text"].lower()

        if search_text_lower in page_text_lower:
            # Find which block contains this text
            for block in page["blocks"]:
                if search_text_lower in block["text"].lower():
                    return {
                        "page": page["page_num"],
                        "bbox": block["bbox"],
                        "found": True
                    }

            # Found in page but not in specific block
            return {
                "page": page["page_num"],
                "found": True
            }

    return {"found": False}


def extract_references(pages_data, client):
    """
    Extract structured references using GPT-4.

    Args:
        pages_data: Extracted text from PDF
        client: OpenAI client

    Returns:
        list of structured references
    """

    print("\n" + "="*70)
    print("EXTRACTING REFERENCES")
    print("="*70)

    total_pages = pages_data["total_pages"]

    # References typically start around 70-80% through the paper
    ref_start_page = max(0, int(total_pages * 0.7))

    print(f"Searching for references in pages {ref_start_page+1} to {total_pages}...")

    # Combine text from reference pages
    ref_text = "\n\n--- PAGE BREAK ---\n\n".join(
        [f"[PAGE {p['page_num']}]\n{p['text']}" for p in pages_data["pages"][ref_start_page:]]
    )

    # Limit text length to avoid token limits
    if len(ref_text) > 50000:  # Roughly 12,500 tokens
        print("⚠ Reference section is very long, truncating...")
        ref_text = ref_text[:50000]

    prompt = f"""You are analyzing the references/bibliography section of a scientific paper.
Extract ALL references in a structured format.

Return a JSON array of references in this format:

[
  {{
    "number": "Reference number or identifier (e.g., [1], [Smith2020])",
    "authors": ["Author 1", "Author 2"],
    "title": "Paper/book title",
    "venue": "Journal name, conference, or publisher",
    "year": "Publication year",
    "volume": "Volume (if journal)",
    "issue": "Issue (if journal)",
    "pages": "Page range",
    "doi": "DOI if present",
    "url": "URL if present"
  }}
]

CRITICAL INSTRUCTIONS:
1. Extract EVERY reference you see
2. Parse each citation as accurately as possible
3. Keep the reference numbering/labels
4. If a field is not present, use null
5. Be thorough - extract all references even if there are many

REFERENCE TEXT:
{ref_text}

Return ONLY a valid JSON array, no other text."""

    print("Sending to GPT-4 API (this may take a moment for long reference lists)...")

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a precise reference extraction assistant for scientific papers."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=4000
        )

        result_text = response.choices[0].message.content.strip()

        # Parse JSON
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
            result_text = result_text.strip()

        references = json.loads(result_text)

        if isinstance(references, list):
            print(f"✓ Successfully extracted {len(references)} references")

            # Try to find page locations for references
            print("Finding page locations for references...")
            for ref in references[:10]:  # Find locations for first 10
                if ref.get('title'):
                    title_snippet = ref['title'][:30]
                    location = find_text_location(pages_data, title_snippet, ref_start_page)
                    if location['found']:
                        ref['location'] = location

            return references
        else:
            print("✗ Unexpected response format")
            return []

    except Exception as e:
        print(f"✗ Error: {e}")
        return []


def main():
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return

    client = OpenAI(api_key=api_key)

    pdf_path = "sample_paper.pdf"

    if not Path(pdf_path).exists():
        print(f"Error: PDF file not found: {pdf_path}")
        return

    print("="*70)
    print("HYBRID PDF METADATA EXTRACTION")
    print("="*70)
    print(f"\nPDF: {pdf_path}")
    print("Method: PyMuPDF (text extraction) + GPT-4 (structuring)\n")

    # Step 1: Extract text with coordinates
    pages_data = extract_text_with_coords(pdf_path)

    # Step 2: Extract header metadata
    header_metadata = extract_header_metadata(pages_data, client)

    # Add location information for header elements
    if "title" in header_metadata and header_metadata["title"]:
        title_location = find_text_location(pages_data, header_metadata["title"][:40])
        header_metadata["title_location"] = title_location

    if "abstract" in header_metadata and header_metadata["abstract"]:
        abstract_snippet = header_metadata["abstract"][:50]
        abstract_location = find_text_location(pages_data, abstract_snippet)
        header_metadata["abstract_location"] = abstract_location

    # Step 3: Extract references
    references = extract_references(pages_data, client)

    # Combine results
    results = {
        "metadata": header_metadata,
        "references": references,
        "extraction_method": "Hybrid (PyMuPDF + GPT-4)",
        "total_pages": pages_data["total_pages"]
    }

    # Save results
    output_file = "hybrid_extraction_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved complete results to: {output_file}")

    # Display summary
    print("\n" + "="*70)
    print("EXTRACTION SUMMARY")
    print("="*70)

    meta = results.get("metadata", {})

    print(f"\n📄 TITLE:")
    print(f"   {meta.get('title', 'N/A')}")
    if meta.get('title_location', {}).get('found'):
        loc = meta['title_location']
        print(f"   📍 Location: Page {loc.get('page', '?')}")
        if 'bbox' in loc:
            print(f"      Bounding box: {loc['bbox']}")

    print(f"\n👥 AUTHORS ({len(meta.get('authors', []))}):")
    for i, author in enumerate(meta.get('authors', [])[:5], 1):
        print(f"   {i}. {author.get('name', 'N/A')}")
        if author.get('email'):
            print(f"      📧 {author['email']}")
        if author.get('affiliations'):
            for aff in author['affiliations']:
                print(f"      🏛 {aff}")

    if len(meta.get('authors', [])) > 5:
        print(f"   ... and {len(meta['authors']) - 5} more authors")

    print(f"\n📝 ABSTRACT:")
    abstract = meta.get('abstract', 'N/A')
    if abstract and abstract != 'N/A':
        print(f"   {abstract[:200]}...")
        if meta.get('abstract_location', {}).get('found'):
            loc = meta['abstract_location']
            print(f"   📍 Location: Page {loc.get('page', '?')}")
    else:
        print("   N/A")

    if meta.get('keywords'):
        print(f"\n🔑 KEYWORDS: {', '.join(meta['keywords'])}")

    if meta.get('doi'):
        print(f"\n🔗 DOI: {meta['doi']}")

    print(f"\n📚 REFERENCES: {len(references)}")
    for i, ref in enumerate(references[:5], 1):
        num = ref.get('number', i)
        print(f"\n   {num}")
        if ref.get('title'):
            print(f"   Title: {ref['title']}")
        if ref.get('authors'):
            authors_display = ', '.join(ref['authors'][:3])
            if len(ref.get('authors', [])) > 3:
                authors_display += ' et al.'
            print(f"   Authors: {authors_display}")
        if ref.get('venue'):
            print(f"   Venue: {ref['venue']}")
        if ref.get('year'):
            print(f"   Year: {ref['year']}")
        if ref.get('doi'):
            print(f"   DOI: {ref['doi']}")
        if ref.get('location', {}).get('found'):
            loc = ref['location']
            print(f"   📍 Found on page {loc.get('page', '?')}")

    if len(references) > 5:
        print(f"\n   ... and {len(references) - 5} more references")

    print("\n" + "="*70)
    print("✓ EXTRACTION COMPLETE")
    print("="*70)

    # Cost estimate
    print("\n💰 COST ESTIMATE:")
    print("   GPT-4o text pricing: $5/1M input tokens, $15/1M output tokens")
    print("   Estimated cost for this extraction: ~$0.02-0.05")
    print("   (60x cheaper than pure vision approach)")

    print("\n✅ ADVANTAGES OF THIS APPROACH:")
    print("   • Fast: Text extraction is near-instant")
    print("   • Cheap: Uses text API instead of vision API")
    print("   • Accurate: GPT-4 excels at structuring text")
    print("   • Coordinates: Links back to source PDF locations")
    print("   • Scalable: Can process thousands of papers efficiently")

    print("\n⚠ LIMITATIONS:")
    print("   • Requires OCR pre-processing for scanned PDFs")
    print("   • May struggle with complex layouts or tables")
    print("   • Text extraction can miss formatting (subscripts, superscripts)")


if __name__ == '__main__':
    main()
