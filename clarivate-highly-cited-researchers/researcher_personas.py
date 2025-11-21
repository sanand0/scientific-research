#!/usr/bin/env python3
"""
Researcher Persona Clustering Framework

This script creates archetypes based on publication patterns.
Without full publication data, we define the conceptual framework
and methodology for future analysis.

Based on citation research literature, we hypothesize these personas:
"""

import json
import pandas as pd
import numpy as np
from collections import Counter

# =============================================================================
# CONCEPTUAL PERSONA FRAMEWORK
# =============================================================================

RESEARCHER_PERSONAS = {
    "The Nobel Laureate": {
        "description": "Publishes sparingly but each paper is transformative",
        "characteristics": {
            "papers_per_year": "1-5",
            "citations_per_paper": "Very high (100+)",
            "h_index_growth": "Slow but steady",
            "collaboration_pattern": "Small, selective teams",
            "typical_fields": ["Physics", "Chemistry", "Medicine"]
        },
        "citation_source": "Quality over quantity - each paper becomes a reference point",
        "example_pattern": "Einstein published ~300 papers in 50 years (6/year avg)"
    },

    "The Prolific Producer": {
        "description": "High volume publisher, citations come from breadth",
        "characteristics": {
            "papers_per_year": "20-50+",
            "citations_per_paper": "Moderate (10-50)",
            "h_index_growth": "Rapid",
            "collaboration_pattern": "Large networks, many co-authors",
            "typical_fields": ["Medicine", "Biology", "Materials Science"]
        },
        "citation_source": "Volume strategy - many papers = many citation opportunities",
        "risk": "May be flagged for 'hyper-prolific authorship' (432 excluded in 2025)"
    },

    "The Method Maven": {
        "description": "Creates widely-used tools, methods, or datasets",
        "characteristics": {
            "papers_per_year": "5-15",
            "citations_per_paper": "Extremely high (1000+) for key papers",
            "h_index_growth": "Moderate overall, spike papers",
            "collaboration_pattern": "Tool development teams",
            "typical_fields": ["Bioinformatics", "Statistics", "Computer Science"]
        },
        "citation_source": "Everyone uses their method and must cite it",
        "example": "BLAST, ImageNet, CRISPR protocol papers"
    },

    "The Review Synthesizer": {
        "description": "Writes influential review articles that define fields",
        "characteristics": {
            "papers_per_year": "5-15",
            "citations_per_paper": "Very high for reviews (200+)",
            "h_index_growth": "Steady",
            "collaboration_pattern": "Often solo or small teams",
            "typical_fields": ["Cross-Field", "Clinical Medicine"]
        },
        "citation_source": "Reviews become default citation for field overview",
        "note": "Reviews often cited more than original research"
    },

    "The Consortium Contributor": {
        "description": "Part of large collaborative projects (CERN, GWAS, etc.)",
        "characteristics": {
            "papers_per_year": "10-30",
            "citations_per_paper": "High (100+) due to project visibility",
            "h_index_growth": "Rapid but collaborative",
            "collaboration_pattern": "Hundreds of co-authors per paper",
            "typical_fields": ["Physics", "Genomics", "Climate Science"]
        },
        "citation_source": "Big Science projects get big citations",
        "controversy": "Authorship dilution - who deserves credit?"
    },

    "The Hot Topic Surfer": {
        "description": "Quickly pivots to emerging high-citation fields",
        "characteristics": {
            "papers_per_year": "15-30",
            "citations_per_paper": "Variable, high in trending topics",
            "h_index_growth": "Boom-bust cycles",
            "collaboration_pattern": "Opportunistic, changing networks",
            "typical_fields": ["AI/ML", "COVID research", "Nanomaterials"]
        },
        "citation_source": "Field momentum - early papers in hot areas get cited",
        "risk": "May lack depth; citations decline as field matures"
    }
}

def analyze_publication_patterns(publications):
    """
    Analyze publication patterns to classify researcher persona.

    Metrics needed:
    - Total publications
    - Publications per year
    - Citations per paper (average, median, max)
    - Number of co-authors (average, max)
    - Field consistency vs. diversity
    - Review vs. original research ratio
    """
    if not publications:
        return None

    # Calculate metrics
    years = [int(p['year']) for p in publications if p.get('year', '').isdigit()]
    if not years:
        return None

    career_length = max(years) - min(years) + 1
    pubs_per_year = len(publications) / career_length

    # Citation metrics (would need citation data)
    # citations_per_paper = ...

    # Author count (would need from publication data)
    # avg_coauthors = ...

    return {
        'total_publications': len(publications),
        'career_years': career_length,
        'pubs_per_year': pubs_per_year,
        'year_range': f"{min(years)}-{max(years)}"
    }

def classify_persona(metrics):
    """
    Classify researcher into persona based on metrics.

    Decision tree:
    1. pubs_per_year > 30 AND many coauthors → Prolific Producer or Consortium
    2. pubs_per_year < 5 AND high citations/paper → Nobel Laureate type
    3. Has 1-2 papers with 1000+ citations → Method Maven
    4. High review ratio → Review Synthesizer
    5. Field diversity high → Hot Topic Surfer or Cross-Field
    """
    if not metrics:
        return "Unknown"

    ppy = metrics.get('pubs_per_year', 0)

    # Simplified classification without full data
    if ppy > 30:
        return "Prolific Producer"
    elif ppy < 5:
        return "Nobel Laureate Type"
    else:
        return "Standard Researcher"

# =============================================================================
# ANALYSIS OF CLARIVATE DATA
# =============================================================================

def analyze_cross_field_phenomenon():
    """
    The Cross-Field category (44% of HCR) suggests many researchers
    don't fit traditional single-discipline molds.

    This aligns with:
    - Method Maven (tools used across fields)
    - Hot Topic Surfer (pivoting between areas)
    - Review Synthesizer (synthesizing multiple fields)
    """
    return {
        "cross_field_percentage": 44,
        "interpretation": """
        The dominance of 'Cross-Field' (44%) in Highly Cited Researchers
        suggests that the most influential scientists are:

        1. BOUNDARY SPANNERS: Working at intersections of disciplines
        2. METHOD DEVELOPERS: Creating tools used across many fields
        3. SYNTHESIZERS: Integrating knowledge from multiple domains

        This challenges the traditional academic reward structure which
        favors deep specialization over breadth.
        """
    }

def analyze_hyper_prolific_exclusions():
    """
    432 researchers excluded for 'hyper-prolific authorship' in 2025.
    Majority from Mainland China, second highest from US.

    This suggests:
    - Some 'Prolific Producers' cross ethical lines
    - Cultural/systemic differences in authorship practices
    - Gaming of citation metrics is a real problem
    """
    return {
        "excluded_count": 432,
        "primary_country": "Mainland China",
        "secondary_country": "United States",
        "interpretation": """
        The exclusion of 432 hyper-prolific authors reveals:

        1. GAMING THE SYSTEM: Some researchers optimize for metrics not impact
        2. CULTURAL DIFFERENCES: Chinese research incentive structures
           may reward volume over novelty
        3. INTEGRITY CONCERNS: Clarivate actively policing list integrity

        Note: China would have even higher share if not for exclusions.
        """
    }

def main():
    print("="*80)
    print("RESEARCHER PERSONA FRAMEWORK")
    print("="*80)

    print("\n## Hypothesized Personas:\n")
    for name, details in RESEARCHER_PERSONAS.items():
        print(f"### {name}")
        print(f"    {details['description']}")
        print(f"    Papers/year: {details['characteristics']['papers_per_year']}")
        print(f"    Citation source: {details['citation_source']}")
        print()

    print("\n## Cross-Field Analysis:")
    cf = analyze_cross_field_phenomenon()
    print(cf['interpretation'])

    print("\n## Hyper-Prolific Exclusions Analysis:")
    hp = analyze_hyper_prolific_exclusions()
    print(hp['interpretation'])

    print("\n" + "="*80)
    print("NOTE: Full persona classification requires publication metadata")
    print("(years, citation counts, co-author networks) not available in")
    print("Clarivate's public list. Framework ready for enrichment.")
    print("="*80)

if __name__ == '__main__':
    main()
