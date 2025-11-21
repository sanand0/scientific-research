#!/usr/bin/env python3
"""
Test GPT-4 Vision for extracting metadata from scientific PDFs.
Works with both scanned and typeset PDFs.
"""

import os
import base64
import json
from pathlib import Path
from io import BytesIO
from pdf2image import convert_from_path
from openai import OpenAI

def pdf_to_images(pdf_path, max_pages=None, dpi=150):
    """
    Convert PDF pages to images.

    Args:
        pdf_path: Path to PDF file
        max_pages: Maximum number of pages to convert (None = all)
        dpi: Resolution for conversion (higher = better quality but larger)

    Returns:
        List of PIL Image objects
    """
    print(f"Converting PDF to images (DPI: {dpi})...")

    images = convert_from_path(
        pdf_path,
        dpi=dpi,
        fmt='PNG',
        first_page=1,
        last_page=max_pages
    )

    print(f"✓ Converted {len(images)} pages to images")
    return images


def image_to_base64(image):
    """Convert PIL Image to base64 string."""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


def extract_header_with_gpt4(images, client):
    """
    Extract title, authors, affiliations, and abstract using GPT-4 Vision.

    Args:
        images: List of PIL Images (first few pages)
        client: OpenAI client

    Returns:
        dict with extracted metadata
    """

    print("\n" + "="*70)
    print("EXTRACTING HEADER METADATA (Title, Authors, Abstract)")
    print("="*70)

    # Use first 2-3 pages (header info is typically on first page)
    pages_to_analyze = images[:min(3, len(images))]

    # Convert images to base64
    image_contents = []
    for idx, img in enumerate(pages_to_analyze, 1):
        print(f"Processing page {idx}...")
        b64_image = image_to_base64(img)
        image_contents.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{b64_image}",
                "detail": "high"
            }
        })

    # Construct prompt for GPT-4 Vision
    prompt = """You are analyzing a scientific research paper PDF. Extract the following information in JSON format:

{
  "title": "Full paper title",
  "authors": [
    {
      "name": "Full author name",
      "affiliations": ["Affiliation 1", "Affiliation 2"],
      "email": "email if available",
      "position_on_page": "approximate vertical position (top/middle/bottom) and page number"
    }
  ],
  "abstract": "Full abstract text",
  "abstract_location": "page number and approximate position",
  "keywords": ["keyword1", "keyword2"],
  "doi": "DOI if present",
  "publication_info": {
    "journal": "journal name if available",
    "year": "publication year if available",
    "volume": "volume if available",
    "pages": "page range if available"
  }
}

IMPORTANT:
1. Extract ALL authors with their complete affiliations
2. Link each author to their affiliations correctly (authors often have superscript numbers/letters linking to affiliations)
3. Include the abstract in full
4. Note approximate positions to help with verification
5. If information is not found, use null
6. Be accurate - this is for academic research

Return ONLY valid JSON, no other text."""

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt}
            ] + image_contents
        }
    ]

    print("Sending to GPT-4 Vision API...")

    response = client.chat.completions.create(
        model="gpt-4o",  # GPT-4 with vision
        messages=messages,
        max_tokens=4000,
        temperature=0.1  # Low temperature for factual extraction
    )

    result_text = response.choices[0].message.content.strip()

    # Parse JSON response
    try:
        # Remove markdown code blocks if present
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
            result_text = result_text.strip()

        metadata = json.loads(result_text)
        print("✓ Successfully extracted header metadata")
        return metadata

    except json.JSONDecodeError as e:
        print(f"✗ Failed to parse JSON response: {e}")
        print(f"Raw response: {result_text[:500]}...")
        return {"error": "Failed to parse GPT-4 response", "raw_response": result_text}


def extract_references_with_gpt4(images, client, batch_size=2):
    """
    Extract references using GPT-4 Vision.

    Args:
        images: List of PIL Images (focus on last pages where references are)
        client: OpenAI client
        batch_size: Number of pages to analyze per API call

    Returns:
        list of reference dicts
    """

    print("\n" + "="*70)
    print("EXTRACTING REFERENCES")
    print("="*70)

    # References are typically in the last 20-30% of the paper
    # Start from the end and work backwards
    total_pages = len(images)
    ref_start_idx = max(0, int(total_pages * 0.7))  # Start from 70% through

    print(f"Analyzing pages {ref_start_idx+1} to {total_pages} for references...")

    all_references = []

    # Process in batches to handle many reference pages
    for batch_start in range(ref_start_idx, total_pages, batch_size):
        batch_end = min(batch_start + batch_size, total_pages)
        batch_pages = images[batch_start:batch_end]

        print(f"\nProcessing pages {batch_start+1} to {batch_end}...")

        # Convert images to base64
        image_contents = []
        for img in batch_pages:
            b64_image = image_to_base64(img)
            image_contents.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{b64_image}",
                    "detail": "high"
                }
            })

        # Prompt for reference extraction
        prompt = f"""You are analyzing pages {batch_start+1} to {batch_end} of a scientific paper. Extract ALL references/citations from these pages.

Return a JSON array of references in this format:

[
  {{
    "reference_number": "number or label (e.g., [1], [Smith2020])",
    "authors": ["Author 1", "Author 2", "et al."],
    "title": "Paper title",
    "journal": "Journal name or venue",
    "year": "Publication year",
    "volume": "Volume",
    "issue": "Issue",
    "pages": "Page range",
    "doi": "DOI if present",
    "url": "URL if present",
    "page_location": {batch_start+1}
  }}
]

IMPORTANT:
1. Extract EVERY reference you see
2. Parse the structured citation information as best as possible
3. Keep reference numbers/labels to maintain order
4. If a field is not present, use null
5. Be thorough - missing references defeats the purpose

Return ONLY a valid JSON array, no other text."""

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt}
                ] + image_contents
            }
        ]

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=4000,
                temperature=0.1
            )

            result_text = response.choices[0].message.content.strip()

            # Parse JSON response
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
                result_text = result_text.strip()

            batch_refs = json.loads(result_text)

            if isinstance(batch_refs, list):
                all_references.extend(batch_refs)
                print(f"✓ Extracted {len(batch_refs)} references from this batch")
            else:
                print(f"✗ Unexpected response format")

        except Exception as e:
            print(f"✗ Error processing batch: {e}")

    print(f"\n✓ Total references extracted: {len(all_references)}")
    return all_references


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

    print(f"Processing PDF: {pdf_path}")
    print(f"Using OpenAI API with GPT-4 Vision\n")

    # Convert PDF to images
    images = pdf_to_images(pdf_path, dpi=150)

    # Extract header metadata (title, authors, abstract)
    header_metadata = extract_header_with_gpt4(images[:3], client)

    # Extract references (from later pages)
    references = extract_references_with_gpt4(images, client, batch_size=2)

    # Combine results
    full_results = {
        "metadata": header_metadata,
        "references": references,
        "extraction_method": "GPT-4 Vision (gpt-4o)",
        "total_pages": len(images)
    }

    # Save results
    output_file = "gpt4_vision_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(full_results, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved results to: {output_file}")

    # Display summary
    print("\n" + "="*70)
    print("EXTRACTION SUMMARY")
    print("="*70)

    if "metadata" in full_results and "error" not in header_metadata:
        meta = full_results["metadata"]

        print(f"\n📄 TITLE:")
        print(f"   {meta.get('title', 'N/A')}")

        print(f"\n👥 AUTHORS ({len(meta.get('authors', []))}):")
        for i, author in enumerate(meta.get('authors', [])[:5], 1):
            print(f"   {i}. {author.get('name', 'N/A')}")
            if author.get('email'):
                print(f"      Email: {author['email']}")
            if author.get('affiliations'):
                for aff in author['affiliations']:
                    print(f"      • {aff}")
            if author.get('position_on_page'):
                print(f"      📍 Location: {author['position_on_page']}")

        if len(meta.get('authors', [])) > 5:
            print(f"   ... and {len(meta['authors']) - 5} more")

        print(f"\n📝 ABSTRACT:")
        abstract = meta.get('abstract', 'N/A')
        if abstract and abstract != 'N/A':
            print(f"   {abstract[:300]}...")
            if meta.get('abstract_location'):
                print(f"   📍 Location: {meta['abstract_location']}")
        else:
            print("   N/A")

        if meta.get('keywords'):
            print(f"\n🔑 KEYWORDS:")
            print(f"   {', '.join(meta['keywords'])}")

        if meta.get('doi'):
            print(f"\n🔗 DOI: {meta['doi']}")

    print(f"\n📚 REFERENCES: {len(references)}")
    for i, ref in enumerate(references[:3], 1):
        print(f"\n   [{ref.get('reference_number', i)}]")
        if ref.get('title'):
            print(f"   Title: {ref['title']}")
        if ref.get('authors'):
            authors_display = ', '.join(ref['authors'][:3])
            if len(ref.get('authors', [])) > 3:
                authors_display += ' et al.'
            print(f"   Authors: {authors_display}")
        if ref.get('journal'):
            print(f"   Journal: {ref['journal']}")
        if ref.get('year'):
            print(f"   Year: {ref['year']}")
        if ref.get('doi'):
            print(f"   DOI: {ref['doi']}")
        if ref.get('page_location'):
            print(f"   📍 Found on page: {ref['page_location']}")

    if len(references) > 3:
        print(f"\n   ... and {len(references) - 3} more references")

    print("\n" + "="*70)
    print("✓ EXTRACTION COMPLETE")
    print("="*70)

    # Calculate cost estimate
    print("\n💰 COST ESTIMATE:")
    print("   GPT-4o pricing: ~$0.01 per image (high detail)")
    print(f"   Approximate cost for this extraction: ${0.01 * (3 + len(images[int(len(images)*0.7):])):.2f}")


if __name__ == '__main__':
    main()
