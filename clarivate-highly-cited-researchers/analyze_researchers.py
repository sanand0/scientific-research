#!/usr/bin/env python3
"""
Analyze Clarivate Highly Cited Researchers Data
Focus on patterns, geographic distribution, institutional concentration, field analysis
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import numpy as np

# Set style for publication-quality plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

def load_data(filename='researchers_data.json'):
    """Load researcher data"""
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return pd.DataFrame(data)

def basic_stats(df):
    """Generate basic statistics"""
    print("="*80)
    print("BASIC STATISTICS")
    print("="*80)

    print(f"\nTotal Researchers: {len(df):,}")
    print(f"\nUnique Countries: {df['country'].nunique()}")
    print(f"Unique Institutions: {df['institution'].nunique()}")
    print(f"Unique Categories: {df['category'].nunique()}")

    return {
        'total': len(df),
        'countries': df['country'].nunique(),
        'institutions': df['institution'].nunique(),
        'categories': df['category'].nunique()
    }

def analyze_geographic_distribution(df):
    """Analyze geographic distribution"""
    print("\n" + "="*80)
    print("GEOGRAPHIC DISTRIBUTION")
    print("="*80)

    country_counts = df['country'].value_counts()

    print(f"\nTop 20 Countries by Number of Highly Cited Researchers:")
    print(country_counts.head(20))

    # Calculate concentration
    top_5_pct = (country_counts.head(5).sum() / len(df)) * 100
    print(f"\nTop 5 countries represent {top_5_pct:.1f}% of all researchers")

    return country_counts

def analyze_institutions(df):
    """Analyze institutional concentration"""
    print("\n" + "="*80)
    print("INSTITUTIONAL ANALYSIS")
    print("="*80)

    inst_counts = df['institution'].value_counts()

    print(f"\nTop 25 Institutions by Number of Highly Cited Researchers:")
    print(inst_counts.head(25))

    # Concentration analysis
    top_10_pct = (inst_counts.head(10).sum() / len(df)) * 100
    top_50_pct = (inst_counts.head(50).sum() / len(df)) * 100
    top_100_pct = (inst_counts.head(100).sum() / len(df)) * 100

    print(f"\nInstitutional Concentration:")
    print(f"  Top 10 institutions: {top_10_pct:.1f}% of researchers")
    print(f"  Top 50 institutions: {top_50_pct:.1f}% of researchers")
    print(f"  Top 100 institutions: {top_100_pct:.1f}% of researchers")

    # Single-researcher institutions
    single_researcher_insts = (inst_counts == 1).sum()
    print(f"\n  Institutions with only 1 researcher: {single_researcher_insts:,}")

    return inst_counts

def analyze_fields(df):
    """Analyze research field distribution"""
    print("\n" + "="*80)
    print("RESEARCH FIELD DISTRIBUTION")
    print("="*80)

    field_counts = df['category'].value_counts()

    print(f"\nAll Research Categories:")
    print(field_counts)

    return field_counts

def analyze_country_institution_pairs(df):
    """Analyze country-institution combinations"""
    print("\n" + "="*80)
    print("COUNTRY-INSTITUTION ANALYSIS")
    print("="*80)

    # Top institutions per country
    for country in df['country'].value_counts().head(10).index:
        country_df = df[df['country'] == country]
        inst_counts = country_df['institution'].value_counts()

        print(f"\n{country} (Total: {len(country_df)} researchers):")
        print(f"  Top 5 institutions:")
        for inst, count in inst_counts.head(5).items():
            pct = (count / len(country_df)) * 100
            print(f"    {inst}: {count} ({pct:.1f}%)")

def analyze_field_by_country(df):
    """Analyze research field distribution by country"""
    print("\n" + "="*80)
    print("FIELD SPECIALIZATION BY COUNTRY")
    print("="*80)

    # Top countries
    for country in df['country'].value_counts().head(10).index:
        country_df = df[df['country'] == country]
        field_counts = country_df['category'].value_counts()

        print(f"\n{country}:")
        for field, count in field_counts.items():
            pct = (count / len(country_df)) * 100
            print(f"  {field}: {count} ({pct:.1f}%)")

def create_visualizations(df):
    """Create visualizations"""
    print("\n" + "="*80)
    print("GENERATING VISUALIZATIONS")
    print("="*80)

    # 1. Top 20 Countries
    fig, ax = plt.subplots(figsize=(14, 8))
    country_counts = df['country'].value_counts().head(20)
    country_counts.plot(kind='barh', ax=ax, color='steelblue')
    ax.set_xlabel('Number of Highly Cited Researchers')
    ax.set_title('Top 20 Countries by Highly Cited Researchers (2025)', fontsize=14, fontweight='bold')
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig('viz_top_countries.png', dpi=300, bbox_inches='tight')
    print("  ✓ Saved: viz_top_countries.png")

    # 2. Top 25 Institutions
    fig, ax = plt.subplots(figsize=(14, 10))
    inst_counts = df['institution'].value_counts().head(25)
    inst_counts.plot(kind='barh', ax=ax, color='darkgreen')
    ax.set_xlabel('Number of Highly Cited Researchers')
    ax.set_title('Top 25 Institutions by Highly Cited Researchers (2025)', fontsize=14, fontweight='bold')
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig('viz_top_institutions.png', dpi=300, bbox_inches='tight')
    print("  ✓ Saved: viz_top_institutions.png")

    # 3. Research Fields
    fig, ax = plt.subplots(figsize=(10, 8))
    field_counts = df['category'].value_counts()
    colors = sns.color_palette("Set2", len(field_counts))
    field_counts.plot(kind='bar', ax=ax, color=colors)
    ax.set_xlabel('Research Field')
    ax.set_ylabel('Number of Researchers')
    ax.set_title('Distribution of Highly Cited Researchers by Field (2025)', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('viz_research_fields.png', dpi=300, bbox_inches='tight')
    print("  ✓ Saved: viz_research_fields.png")

    # 4. Country-Field Heatmap (top 15 countries, all fields)
    top_countries = df['country'].value_counts().head(15).index
    df_top = df[df['country'].isin(top_countries)]

    pivot = pd.crosstab(df_top['country'], df_top['category'])
    pivot = pivot.loc[top_countries]  # Maintain order

    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(pivot, annot=True, fmt='d', cmap='YlOrRd', ax=ax, cbar_kws={'label': 'Number of Researchers'})
    ax.set_title('Research Field Distribution by Country (Top 15 Countries)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Research Field')
    ax.set_ylabel('Country')
    plt.tight_layout()
    plt.savefig('viz_country_field_heatmap.png', dpi=300, bbox_inches='tight')
    print("  ✓ Saved: viz_country_field_heatmap.png")

def find_insights(df):
    """Hunt for interesting patterns and insights"""
    print("\n" + "="*80)
    print("INSIGHT DISCOVERY")
    print("="*80)

    insights = []

    # 1. Geographic concentration
    country_counts = df['country'].value_counts()
    top_3_pct = (country_counts.head(3).sum() / len(df)) * 100
    if top_3_pct > 50:
        insights.append(f"HIGH CONCENTRATION: Top 3 countries account for {top_3_pct:.1f}% of all highly cited researchers")

    # 2. Institutional concentration
    inst_counts = df['institution'].value_counts()
    top_inst = inst_counts.iloc[0]
    top_inst_name = inst_counts.index[0]
    top_inst_pct = (top_inst / len(df)) * 100
    if top_inst_pct > 3:
        insights.append(f"DOMINANT INSTITUTION: {top_inst_name} has {top_inst} researchers ({top_inst_pct:.1f}% of total)")

    # 3. Field imbalances
    field_counts = df['category'].value_counts()
    max_field = field_counts.iloc[0]
    min_field = field_counts.iloc[-1]
    ratio = max_field / min_field
    if ratio > 3:
        insights.append(f"FIELD IMBALANCE: {field_counts.index[0]} has {ratio:.1f}x more researchers than {field_counts.index[-1]}")

    # 4. Country-specific field dominance
    for country in country_counts.head(5).index:
        country_df = df[df['country'] == country]
        field_dist = country_df['category'].value_counts()
        if len(field_dist) > 0:
            top_field_pct = (field_dist.iloc[0] / len(country_df)) * 100
            if top_field_pct > 40:
                insights.append(f"SPECIALIZATION: {country}'s researchers are {top_field_pct:.1f}% concentrated in {field_dist.index[0]}")

    print("\nKey Insights:")
    for i, insight in enumerate(insights, 1):
        print(f"  {i}. {insight}")

    return insights

def main():
    print("\n" + "="*80)
    print("CLARIVATE HIGHLY CITED RESEARCHERS 2025 - ANALYSIS")
    print("="*80)

    # Load data
    df = load_data()

    # Run analyses
    stats = basic_stats(df)
    country_dist = analyze_geographic_distribution(df)
    inst_dist = analyze_institutions(df)
    field_dist = analyze_fields(df)
    analyze_country_institution_pairs(df)
    analyze_field_by_country(df)

    # Generate visualizations
    create_visualizations(df)

    # Find insights
    insights = find_insights(df)

    # Save summary
    summary = {
        'statistics': stats,
        'insights': insights,
        'top_countries': country_dist.head(10).to_dict(),
        'top_institutions': inst_dist.head(25).to_dict(),
        'field_distribution': field_dist.to_dict()
    }

    with open('analysis_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print("\nGenerated files:")
    print("  - analysis_summary.json")
    print("  - viz_top_countries.png")
    print("  - viz_top_institutions.png")
    print("  - viz_research_fields.png")
    print("  - viz_country_field_heatmap.png")

if __name__ == '__main__':
    main()
