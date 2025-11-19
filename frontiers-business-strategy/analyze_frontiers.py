#!/usr/bin/env python3
"""
Analyze Frontiers publishing patterns via PubMed to identify topic focus and strategic gaps
"""

import requests
import time
import json
from collections import defaultdict
from datetime import datetime

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

def search_pubmed(query, retmax=0):
    """Search PubMed and return count and PMIDs"""
    search_url = f"{BASE_URL}esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": retmax,
        "retmode": "json"
    }

    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        result = response.json()
        count = int(result["esearchresult"]["count"])
        pmids = result["esearchresult"].get("idlist", [])
        return count, pmids
    except Exception as e:
        print(f"Error searching '{query}': {e}")
        return 0, []
    finally:
        time.sleep(0.35)  # Rate limiting

def analyze_frontiers_focus():
    """Analyze Frontiers' topic distribution"""

    print("=" * 80)
    print("FRONTIERS PUBLISHING PATTERN ANALYSIS")
    print("=" * 80)
    print()

    # Define search queries for different topic areas
    # Time periods: recent (2023-2024) vs historical (2015-2022)

    searches = {
        "CURRENT FRONTIERS FOCUS": {
            "Neurology": '"Front Neurol"[Journal] AND 2023:2024[dp]',
            "Neuroscience": '"Front Neurosci"[Journal] AND 2023:2024[dp]',
            "Aging Neuroscience": '"Front Aging Neurosci"[Journal] AND 2023:2024[dp]',
            "Psychology": '"Front Psychol"[Journal] AND 2023:2024[dp]',
            "Immunology": '"Front Immunol"[Journal] AND 2023:2024[dp]',
            "Oncology": '"Front Oncol"[Journal] AND 2023:2024[dp]',
            "Cardiovascular": '"Front Cardiovasc Med"[Journal] AND 2023:2024[dp]',
            "Public Health": '"Front Public Health"[Journal] AND 2023:2024[dp]',
        },

        "EMERGING AREAS IN FRONTIERS (2023-2024)": {
            "AI in Frontiers": '("Front Artif Intell"[Journal] OR "Front Comput Sci"[Journal]) AND 2023:2024[dp]',
            "Climate/Sustainability": '("Front Environ Sci"[Journal] OR "Front Clim"[Journal] OR "Front Sustain"[Journal]) AND 2023:2024[dp]',
            "Robotics/AI": '"Front Robot AI"[Journal] AND 2023:2024[dp]',
            "Bioengineering": '"Front Bioeng Biotechnol"[Journal] AND 2023:2024[dp]',
            "Microbiology": '"Front Microbiol"[Journal] AND 2023:2024[dp]',
        },

        "ALL FRONTIERS JOURNALS": {
            "Total Frontiers (2023-2024)": 'frontiers[journal] AND 2023:2024[dp]',
            "Total Frontiers (2022)": 'frontiers[journal] AND 2022[dp]',
            "Total Frontiers (2021)": 'frontiers[journal] AND 2021[dp]',
            "Total Frontiers (2020)": 'frontiers[journal] AND 2020[dp]',
            "Total Frontiers (2019)": 'frontiers[journal] AND 2019[dp]',
        },

        "COMPARISON: ALL PUBMED (2023-2024)": {
            "AI/ML (all PubMed)": '(artificial intelligence[tiab] OR machine learning[tiab] OR deep learning[tiab]) AND 2023:2024[dp]',
            "Climate (all PubMed)": '(climate change[tiab] OR sustainability[tiab] OR renewable energy[tiab]) AND 2023:2024[dp]',
            "Synthetic Bio (all PubMed)": '(synthetic biology[tiab] OR bioengineering[tiab]) AND 2023:2024[dp]',
            "Neuroscience (all PubMed)": '(neuroscience[tiab] OR neurology[tiab] OR neurological[tiab]) AND 2023:2024[dp]',
            "Immunology (all PubMed)": '(immunology[tiab] OR immunological[tiab] OR immune[tiab]) AND 2023:2024[dp]',
        },

        "GROWTH POTENTIAL TOPICS (ALL PUBMED)": {
            "Quantum Computing": 'quantum computing[tiab] AND 2023:2024[dp]',
            "CRISPR/Gene Editing": '(CRISPR[tiab] OR gene editing[tiab]) AND 2023:2024[dp]',
            "Longevity/Aging": '(longevity[tiab] OR aging research[tiab] OR senolytics[tiab]) AND 2023:2024[dp]',
            "Precision Medicine": 'precision medicine[tiab] AND 2023:2024[dp]',
            "One Health": 'one health[tiab] AND 2023:2024[dp]',
        }
    }

    results = {}

    for category, queries in searches.items():
        print(f"\n{category}")
        print("-" * 80)
        results[category] = {}

        for name, query in queries.items():
            count, _ = search_pubmed(query)
            results[category][name] = count
            print(f"{name:40s}: {count:>8,} articles")

    # Calculate market share and trends
    print("\n" + "=" * 80)
    print("MARKET SHARE ANALYSIS (2023-2024)")
    print("=" * 80)

    # Neuroscience market share
    frontiers_neuro = results["CURRENT FRONTIERS FOCUS"]["Neuroscience"] + results["CURRENT FRONTIERS FOCUS"]["Neurology"]
    total_neuro = results["COMPARISON: ALL PUBMED (2023-2024)"]["Neuroscience (all PubMed)"]
    if total_neuro > 0:
        neuro_share = (frontiers_neuro / total_neuro) * 100
        print(f"\nNeuroscience: {neuro_share:.2f}% market share ({frontiers_neuro:,} / {total_neuro:,})")

    # Immunology market share
    frontiers_immuno = results["CURRENT FRONTIERS FOCUS"]["Immunology"]
    total_immuno = results["COMPARISON: ALL PUBMED (2023-2024)"]["Immunology (all PubMed)"]
    if total_immuno > 0:
        immuno_share = (frontiers_immuno / total_immuno) * 100
        print(f"Immunology: {immuno_share:.2f}% market share ({frontiers_immuno:,} / {total_immuno:,})")

    # AI/ML market share
    frontiers_ai = results["EMERGING AREAS IN FRONTIERS (2023-2024)"]["AI in Frontiers"]
    total_ai = results["COMPARISON: ALL PUBMED (2023-2024)"]["AI/ML (all PubMed)"]
    if total_ai > 0:
        ai_share = (frontiers_ai / total_ai) * 100
        print(f"AI/ML: {ai_share:.2f}% market share ({frontiers_ai:,} / {total_ai:,})")

    # Climate market share
    frontiers_climate = results["EMERGING AREAS IN FRONTIERS (2023-2024)"]["Climate/Sustainability"]
    total_climate = results["COMPARISON: ALL PUBMED (2023-2024)"]["Climate (all PubMed)"]
    if total_climate > 0:
        climate_share = (frontiers_climate / total_climate) * 100
        print(f"Climate/Sustainability: {climate_share:.2f}% market share ({frontiers_climate:,} / {total_climate:,})")

    # Overall Frontiers volume trend
    print("\n" + "=" * 80)
    print("FRONTIERS VOLUME TRENDS")
    print("=" * 80)

    yr_2019 = results["ALL FRONTIERS JOURNALS"]["Total Frontiers (2019)"]
    yr_2020 = results["ALL FRONTIERS JOURNALS"]["Total Frontiers (2020)"]
    yr_2021 = results["ALL FRONTIERS JOURNALS"]["Total Frontiers (2021)"]
    yr_2022 = results["ALL FRONTIERS JOURNALS"]["Total Frontiers (2022)"]
    yr_2023_2024 = results["ALL FRONTIERS JOURNALS"]["Total Frontiers (2023-2024)"]

    print(f"\n2019: {yr_2019:,} articles")
    print(f"2020: {yr_2020:,} articles ({((yr_2020-yr_2019)/yr_2019*100):+.1f}%)" if yr_2019 > 0 else f"2020: {yr_2020:,} articles")
    print(f"2021: {yr_2021:,} articles ({((yr_2021-yr_2020)/yr_2020*100):+.1f}%)" if yr_2020 > 0 else f"2021: {yr_2021:,} articles")
    print(f"2022: {yr_2022:,} articles ({((yr_2022-yr_2021)/yr_2021*100):+.1f}%)" if yr_2021 > 0 else f"2022: {yr_2022:,} articles")
    print(f"2023-2024: {yr_2023_2024:,} articles (avg {yr_2023_2024/2:,.0f}/year)")

    if yr_2022 > 0:
        trend_2023_2024 = ((yr_2023_2024/2 - yr_2022) / yr_2022) * 100
        print(f"\nYear-over-year trend (2022 → 2023-2024 avg): {trend_2023_2024:+.1f}%")

    # Save results
    with open('publication_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 80)
    print(f"Analysis complete. Results saved to publication_analysis.json")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    return results

if __name__ == "__main__":
    analyze_frontiers_focus()
