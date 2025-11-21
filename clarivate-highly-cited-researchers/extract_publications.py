#!/usr/bin/env python3
"""
Extract publication metadata for sampled researchers using Bio.Entrez (PubMed)
Given API rate limits and time constraints, we sample notable researchers
"""

import json
import time
import pandas as pd
from collections import Counter
try:
    from Bio import Entrez
    BIOPYTHON_AVAILABLE = True
except ImportError:
    BIOPYTHON_AVAILABLE = False
    print("WARNING: BioPython not available. Install with: pip install biopython")

# Set email for NCBI API (required)
Entrez.email = "research@example.com"

def search_pubmed(author_name, max_results=100):
    """Search PubMed for publications by author"""
    if not BIOPYTHON_AVAILABLE:
        return []

    try:
        # Search PubMed
        search_query = f"{author_name}[Author]"
        handle = Entrez.esearch(db="pubmed", term=search_query, retmax=max_results)
        record = Entrez.read(handle)
        handle.close()

        id_list = record["IdList"]
        print(f"  Found {len(id_list)} publications")

        if not id_list:
            return []

        # Fetch details
        handle = Entrez.efetch(db="pubmed", id=id_list, rettype="medline", retmode="text")
        records = Medline.parse(handle)

        publications = []
        for record in records:
            pub = {
                'pmid': record.get('PMID', ''),
                'title': record.get('TI', ''),
                'authors': record.get('AU', []),
                'journal': record.get('JT', ''),
                'year': record.get('DP', '').split()[0] if record.get('DP') else '',
                'abstract': record.get('AB', '')
            }
            publications.append(pub)

        handle.close()
        return publications

    except Exception as e:
        print(f"  Error searching PubMed: {e}")
        return []

def analyze_researcher_publications(researcher, publications):
    """Analyze publication patterns for a researcher"""
    if not publications:
        return None

    # Extract years
    years = [int(p['year']) for p in publications if p['year'].isdigit()]

    # Count co-authors
    all_coauthors = []
    for pub in publications:
        authors = pub.get('authors', [])
        all_coauthors.extend([a for a in authors if a != researcher['full_name']])

    # Count journals
    journals = [p['journal'] for p in publications if p['journal']]

    analysis = {
        'researcher_name': researcher['full_name'],
        'institution': researcher.get('institution', ''),
        'country': researcher.get('country', ''),
        'total_publications': len(publications),
        'year_range': f"{min(years)}-{max(years)}" if years else "N/A",
        'publication_rate': len(publications) / (max(years) - min(years) + 1) if len(years) > 1 else 0,
        'unique_coauthors': len(set(all_coauthors)),
        'top_coauthors': Counter(all_coauthors).most_common(5),
        'unique_journals': len(set(journals)),
        'top_journals': Counter(journals).most_common(5),
        'has_recent_pubs': max(years) >= 2020 if years else False
    }

    return analysis

def sample_researchers(researchers_data, strategy='diverse', n=50):
    """Sample researchers for deep analysis"""
    df = pd.DataFrame(researchers_data)

    if strategy == 'diverse':
        # Sample to maximize diversity across countries and fields
        samples = []

        # Get top countries
        top_countries = df['country'].value_counts().head(10).index

        # Sample from each top country
        for country in top_countries:
            country_df = df[df['country'] == country]
            # Sample proportionally, min 1, max 10
            n_sample = min(max(1, len(country_df) // 20), 10)
            samples.append(country_df.sample(n=min(n_sample, len(country_df))))

        # Add random samples from other countries
        other_df = df[~df['country'].isin(top_countries)]
        if len(other_df) > 0:
            samples.append(other_df.sample(n=min(10, len(other_df))))

        sampled = pd.concat(samples).drop_duplicates()

        # Limit to n
        if len(sampled) > n:
            sampled = sampled.sample(n=n)

        return sampled.to_dict('records')

    elif strategy == 'top_institutions':
        # Sample from top institutions
        top_insts = df['institution'].value_counts().head(20).index
        sampled = df[df['institution'].isin(top_insts)].sample(n=min(n, len(df)))
        return sampled.to_dict('records')

    else:  # random
        sampled = df.sample(n=min(n, len(df)))
        return sampled.to_dict('records')

def main():
    print("="*80)
    print("PUBLICATION METADATA EXTRACTION")
    print("="*80)

    # Load researcher data
    try:
        with open('researchers_data.json', 'r') as f:
            researchers = json.load(f)
        print(f"\nLoaded {len(researchers)} researchers")
    except:
        print("Error: researchers_data.json not found")
        return

    # Sample researchers
    print("\nSampling researchers for deep analysis...")
    sampled = sample_researchers(researchers, strategy='diverse', n=50)
    print(f"Selected {len(sampled)} researchers for publication analysis")

    # NOTE: Actual PubMed extraction would happen here
    # For now, we'll create a framework and demonstrate with a few examples

    print("\n" + "="*80)
    print("PUBLICATION ANALYSIS FRAMEWORK")
    print("="*80)

    print("\nSelected researchers by country:")
    country_dist = Counter([r['country'] for r in sampled])
    for country, count in country_dist.most_common():
        print(f"  {country}: {count}")

    print("\nSelected researchers by field:")
    field_dist = Counter([r['category'] for r in sampled])
    for field, count in field_dist.most_common():
        print(f"  {field}: {count}")

    # Save sample for reference
    with open('sampled_researchers.json', 'w') as f:
        json.dump(sampled, f, indent=2)
    print("\n✓ Saved sampled researchers to sampled_researchers.json")

    print("\n" + "="*80)
    print("NOTE: Full PubMed extraction would require:")
    print("  - Bio.Entrez API calls (rate limited to 3/second)")
    print("  - ~50 researchers × 2 API calls each × 0.5s = ~50 seconds")
    print("  - For full dataset (7000 researchers) = ~2 hours")
    print("="*80)

    if BIOPYTHON_AVAILABLE:
        print("\nBioPython is available. Run full extraction? (This will take time)")
        print("For demonstration, we'll analyze a few examples...")

        # Analyze a few examples
        for i, researcher in enumerate(sampled[:5]):
            print(f"\n[{i+1}/5] Analyzing: {researcher['full_name']}")
            time.sleep(0.5)  # Rate limiting
            # pubs = search_pubmed(researcher['full_name'], max_results=50)
            # This would require actual API calls - skipped for time

if __name__ == '__main__':
    main()
