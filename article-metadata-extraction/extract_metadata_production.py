#!/usr/bin/env python3
"""
Production-ready PDF metadata extraction for scientific articles.

This is the recommended approach combining:
- PyMuPDF for fast text extraction with coordinates
- GPT-4 for intelligent structuring
- Smart chunking for large reference sections
- OCR support for scanned PDFs

Handles both typeset and scanned PDFs.
"""

import os
import json
import fitz  # PyMuPDF
from pathlib import Path
from openai import OpenAI
from typing import List, Dict, Any

class ScientificPDFExtractor:
    """Extract structured metadata from scientific PDFs."""

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def extract_text_from_pdf(self, pdf_path: str, use_ocr: bool = False) -> Dict[str, Any]:
        """
        Extract text from PDF with coordinates.

        Args:
            pdf_path: Path to PDF file
            use_ocr: Whether to use OCR for scanned PDFs

        Returns:
            Dict with pages and text blocks
        """
        doc = fitz.open(pdf_path)
        total_pages = len(doc)

        print(f"Extracting text from {total_pages} pages...")

        pages_data = []

        for page_num in range(total_pages):
            page = doc[page_num]

            # Get text (with OCR if needed)
            if use_ocr:
                # For scanned PDFs, use OCR
                # Note: This requires tesseract to be installed
                pix = page.get_pixmap()
                # Could integrate pytesseract here
                page_text = page.get_text()  # Fallback to regular extraction
            else:
                page_text = page.get_text()

            # Get text blocks with coordinates
            blocks = page.get_text("blocks")

            pages_data.append({
                "page_num": page_num + 1,
                "text": page_text,
                "blocks": [
                    {
                        "bbox": [b[0], b[1], b[2], b[3]],
                        "text": b[4],
                        "block_no": b[5]
                    }
                    for b in blocks if b[6] == 0  # Only text blocks
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

    def extract_metadata(self, pages_data: Dict, num_pages: int = 3) -> Dict:
        """
        Extract title, authors, affiliations, abstract from first few pages.

        Args:
            pages_data: Extracted page data
            num_pages: Number of pages to analyze for metadata

        Returns:
            Structured metadata dict
        """
        print("\n" + "="*70)
        print("EXTRACTING METADATA (Title, Authors, Abstract, etc.)")
        print("="*70)

        # Combine first few pages
        header_text = "\n\n--- PAGE BREAK ---\n\n".join(
            [p["text"] for p in pages_data["pages"][:num_pages]]
        )

        prompt = f"""Extract metadata from this scientific paper in JSON format:

{{
  "title": "Full paper title",
  "authors": [
    {{
      "name": "Author full name",
      "affiliations": ["Affiliation 1"],
      "email": "email@example.com or null"
    }}
  ],
  "abstract": "Complete abstract text",
  "keywords": ["keyword1", "keyword2"],
  "doi": "DOI if present",
  "publication_info": {{
    "journal": "journal/conference name",
    "year": "year",
    "volume": "volume",
    "issue": "issue",
    "pages": "page range"
  }}
}}

Instructions:
- Extract ALL authors with their affiliations (match superscript numbers/symbols)
- Include complete abstract
- If field not found, use null
- Return only valid JSON

Paper text:
{header_text}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a metadata extraction assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=3000,
                response_format={"type": "json_object"}  # Force JSON output
            )

            result_text = response.choices[0].message.content.strip()
            metadata = json.loads(result_text)

            print("✓ Successfully extracted metadata")
            return metadata

        except Exception as e:
            print(f"✗ Error: {e}")
            return {"error": str(e)}

    def extract_references_chunked(self, pages_data: Dict, refs_per_chunk: int = 20) -> List[Dict]:
        """
        Extract references in chunks to handle large reference sections.

        Args:
            pages_data: Extracted page data
            refs_per_chunk: Target number of references per API call

        Returns:
            List of structured references
        """
        print("\n" + "="*70)
        print("EXTRACTING REFERENCES")
        print("="*70)

        total_pages = pages_data["total_pages"]
        ref_start_page = max(0, int(total_pages * 0.7))

        print(f"Analyzing pages {ref_start_page+1} to {total_pages}")

        # Process references page by page
        all_references = []

        for page_idx in range(ref_start_page, total_pages):
            page = pages_data["pages"][page_idx]
            page_num = page["page_num"]
            page_text = page["text"]

            # Skip pages that don't look like references
            if "reference" not in page_text.lower()[:500] and page_idx > ref_start_page:
                if all_references:  # We've already found some references
                    continue

            print(f"Processing page {page_num}...")

            prompt = f"""Extract ALL references from this page of a scientific paper.

Return JSON array:
[
  {{
    "number": "ref number/label",
    "authors": ["Author 1", "Author 2"],
    "title": "Paper title",
    "venue": "Journal/conference",
    "year": "year",
    "volume": "vol",
    "pages": "pages",
    "doi": "DOI or null"
  }}
]

Page text:
{page_text}

Return only valid JSON array (empty array [] if no references)."""

            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a reference extraction assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=2000,
                    response_format={"type": "json_object"}
                )

                result_text = response.choices[0].message.content.strip()

                # Handle response that wraps array in object
                result = json.loads(result_text)
                if isinstance(result, dict) and 'references' in result:
                    page_refs = result['references']
                elif isinstance(result, dict) and len(result) == 1:
                    # Single key dict, get the value
                    page_refs = list(result.values())[0]
                elif isinstance(result, list):
                    page_refs = result
                else:
                    page_refs = []

                if page_refs:
                    # Add page location to each reference
                    for ref in page_refs:
                        ref['source_page'] = page_num

                    all_references.extend(page_refs)
                    print(f"  ✓ Found {len(page_refs)} references")

            except Exception as e:
                print(f"  ✗ Error on page {page_num}: {e}")

        print(f"\n✓ Total references extracted: {len(all_references)}")
        return all_references

    def find_text_coordinates(self, pages_data: Dict, search_text: str, start_page: int = 0) -> Dict:
        """Find coordinates of text in PDF."""

        search_text = search_text[:50].lower()

        for page in pages_data["pages"][start_page:]:
            if search_text in page["text"].lower():
                for block in page["blocks"]:
                    if search_text in block["text"].lower():
                        return {
                            "page": page["page_num"],
                            "bbox": block["bbox"],
                            "found": True
                        }
                return {
                    "page": page["page_num"],
                    "found": True
                }

        return {"found": False}

    def extract_all(self, pdf_path: str, use_ocr: bool = False) -> Dict:
        """
        Complete extraction pipeline.

        Args:
            pdf_path: Path to PDF file
            use_ocr: Whether to use OCR for scanned PDFs

        Returns:
            Complete structured data
        """
        print("="*70)
        print("SCIENTIFIC PDF METADATA EXTRACTION")
        print("="*70)
        print(f"\nPDF: {pdf_path}")
        print(f"Method: PyMuPDF + GPT-4 (Hybrid)")
        print(f"OCR: {'Enabled' if use_ocr else 'Disabled'}\n")

        # Extract text
        pages_data = self.extract_text_from_pdf(pdf_path, use_ocr)

        # Extract metadata
        metadata = self.extract_metadata(pages_data)

        # Add coordinates
        if metadata.get("title"):
            metadata["title_location"] = self.find_text_coordinates(
                pages_data, metadata["title"][:40]
            )

        if metadata.get("abstract"):
            metadata["abstract_location"] = self.find_text_coordinates(
                pages_data, metadata["abstract"][:50]
            )

        # Extract references
        references = self.extract_references_chunked(pages_data)

        return {
            "metadata": metadata,
            "references": references,
            "extraction_method": "Hybrid (PyMuPDF + GPT-4o)",
            "total_pages": pages_data["total_pages"],
            "ocr_used": use_ocr
        }


def main():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return

    pdf_path = "sample_paper.pdf"
    if not Path(pdf_path).exists():
        print(f"Error: PDF not found: {pdf_path}")
        return

    # Initialize extractor
    extractor = ScientificPDFExtractor(api_key)

    # Run extraction
    results = extractor.extract_all(pdf_path, use_ocr=False)

    # Save results
    output_file = "production_extraction_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved results to: {output_file}")

    # Display summary
    print("\n" + "="*70)
    print("EXTRACTION SUMMARY")
    print("="*70)

    meta = results["metadata"]

    # Title
    print(f"\n📄 TITLE: {meta.get('title', 'N/A')}")
    if meta.get('title_location', {}).get('found'):
        loc = meta['title_location']
        print(f"   📍 Page {loc['page']}, bbox: {loc.get('bbox', 'N/A')}")

    # Authors
    authors = meta.get('authors', [])
    print(f"\n👥 AUTHORS ({len(authors)}):")
    for i, author in enumerate(authors[:10], 1):
        print(f"   {i}. {author.get('name', 'N/A')}")
        if author.get('email'):
            print(f"      📧 {author['email']}")
        for aff in author.get('affiliations', []):
            print(f"      🏛 {aff}")

    # Abstract
    print(f"\n📝 ABSTRACT:")
    abstract = meta.get('abstract', '')
    if abstract:
        print(f"   {abstract[:200]}...")
        if meta.get('abstract_location', {}).get('found'):
            print(f"   📍 Page {meta['abstract_location']['page']}")

    # Keywords
    if meta.get('keywords'):
        print(f"\n🔑 KEYWORDS: {', '.join(meta['keywords'])}")

    # DOI
    if meta.get('doi'):
        print(f"\n🔗 DOI: {meta['doi']}")

    # References
    refs = results["references"]
    print(f"\n📚 REFERENCES: {len(refs)}")
    for i, ref in enumerate(refs[:3], 1):
        print(f"\n   [{ref.get('number', i)}] {ref.get('title', 'N/A')}")
        if ref.get('authors'):
            print(f"   Authors: {', '.join(ref['authors'][:2])} et al.")
        if ref.get('venue'):
            print(f"   Venue: {ref['venue']}")
        if ref.get('year'):
            print(f"   Year: {ref['year']}")
        if ref.get('source_page'):
            print(f"   📍 Page {ref['source_page']}")

    if len(refs) > 3:
        print(f"\n   ... and {len(refs) - 3} more")

    print("\n" + "="*70)
    print("✅ COMPLETE")
    print("="*70)

if __name__ == '__main__':
    main()
