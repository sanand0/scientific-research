#!/usr/bin/env python3
"""
Analysis and visualization of dye screening results
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

# Load results
df = pd.read_csv('dye_screening_results.csv')

print("="*80)
print("DETAILED ANALYSIS OF DYE SCREENING RESULTS")
print("="*80)
print()

# =============================================================================
# 1. SCAFFOLD ANALYSIS
# =============================================================================
print("1. SCAFFOLD ANALYSIS")
print("-" * 80)

# Identify scaffolds by key structural features
def identify_scaffold(smiles):
    """Identify the core scaffold from SMILES"""
    if 'O=C1c2ccccc2C(=O)c' in smiles:
        return 'Anthraquinone'
    elif 'N=N' in smiles and 'O=C' not in smiles:
        return 'Azo'
    elif 'N=N' in smiles and 'O=C1c2ccccc2C(=O)' in smiles:
        return 'Anthraquinone-Azo'
    elif 'O=C1/C(=C' in smiles:
        return 'Indigo-like'
    elif 'O=C1Nc' in smiles:
        return 'Benzimidazolone'
    elif 'C=C' in smiles and 'O=C1Oc' in smiles:
        return 'Coumarin'
    else:
        return 'Other'

df['scaffold'] = df['smiles'].apply(identify_scaffold)

scaffold_stats = df.groupby('scaffold').agg({
    'composite_score': ['count', 'mean', 'max'],
    'light_fastness_score': 'mean',
    'washing_fastness_score': 'mean'
}).round(3)

print(scaffold_stats)
print()

# =============================================================================
# 2. PROPERTY CORRELATIONS
# =============================================================================
print("\n2. PROPERTY CORRELATIONS")
print("-" * 80)

# Correlation matrix
corr_cols = ['light_fastness_score', 'washing_fastness_score', 'molecular_weight',
             'logp', 'num_aromatic_rings', 'conjugation_score', 'chromophore_score']
corr_matrix = df[corr_cols].corr()

print("Correlation with Light Fastness:")
print(corr_matrix['light_fastness_score'].sort_values(ascending=False))
print()

print("Correlation with Washing Fastness:")
print(corr_matrix['washing_fastness_score'].sort_values(ascending=False))
print()

# =============================================================================
# 3. NOVEL CANDIDATE DEEP DIVE
# =============================================================================
print("\n3. NOVEL CANDIDATE ANALYSIS")
print("-" * 80)

novel_df = df[df['source'] == 'generated'].sort_values('composite_score', ascending=False)

print(f"Total novel candidates: {len(novel_df)}")
print(f"\nTop 5 Novel Candidates:")
print()

for idx, (i, row) in enumerate(novel_df.head(5).iterrows()):
    print(f"{idx+1}. {row['name']} (Score: {row['composite_score']:.3f})")
    if pd.notna(row.get('description')):
        print(f"   Description: {row['description']}")
    print(f"   Color: {row['color_family']}, λmax: {row['estimated_lambda_max']:.0f} nm")
    print(f"   Light: {row['light_fastness_rating']}/8, Wash: {row['washing_fastness_rating']}/5")
    print(f"   MW: {row['molecular_weight']:.1f}, LogP: {row['logp']:.2f}")
    print(f"   Scaffold: {row['scaffold']}")
    print()

# =============================================================================
# 4. IDENTIFY LESSER-KNOWN HIGH-PERFORMERS
# =============================================================================
print("\n4. LESSER-KNOWN DYES WITH SUPERIOR PROPERTIES")
print("-" * 80)

# Focus on known dyes that aren't commonly used but have high scores
lesser_known = [
    'Vat_Orange_1', 'Quinizarin', 'Perinone_Orange', 'Isoindolinone_Yellow',
    'Naphthol_AS', 'Benzodifuranone', 'Quinophthalone_Yellow', 'Dioxazine_Violet_Base'
]

lesser_known_df = df[df['name'].isin(lesser_known)].sort_values('composite_score', ascending=False)

print(f"Found {len(lesser_known_df)} lesser-known high-performing dyes:")
print()

for idx, (i, row) in enumerate(lesser_known_df.head(10).iterrows()):
    print(f"{idx+1}. {row['name']} (Score: {row['composite_score']:.3f})")
    print(f"   Color: {row['color_family']}, Light: {row['light_fastness_rating']}/8, Wash: {row['washing_fastness_rating']}/5")
    print(f"   SMILES: {row['smiles']}")
    print()

# =============================================================================
# 5. RECOMMENDATIONS BY APPLICATION
# =============================================================================
print("\n5. APPLICATION-SPECIFIC RECOMMENDATIONS")
print("-" * 80)

print("\nA. TEXTILE INDUSTRY (High washing fastness priority):")
textile_candidates = df[df['washing_fastness_score'] >= 4.5].sort_values(
    'composite_score', ascending=False
).head(5)

for idx, (i, row) in enumerate(textile_candidates.iterrows()):
    print(f"  {idx+1}. {row['name']}: {row['color_family']}, Wash {row['washing_fastness_rating']}/5, Score {row['composite_score']:.3f}")

print("\nB. OUTDOOR APPLICATIONS (High light fastness priority):")
outdoor_candidates = df[df['light_fastness_score'] >= 5.5].sort_values(
    'composite_score', ascending=False
).head(5)

for idx, (i, row) in enumerate(outdoor_candidates.iterrows()):
    print(f"  {idx+1}. {row['name']}: {row['color_family']}, Light {row['light_fastness_rating']}/8, Score {row['composite_score']:.3f}")

print("\nC. POLYMER INDUSTRY (Balance of properties, easy synthesis):")
polymer_candidates = df[df['sa_score'] <= 5.0].sort_values(
    'composite_score', ascending=False
).head(5)

for idx, (i, row) in enumerate(polymer_candidates.iterrows()):
    print(f"  {idx+1}. {row['name']}: {row['color_family']}, SA {row['sa_score']:.1f}, Score {row['composite_score']:.3f}")

# =============================================================================
# 6. GENERATE VISUALIZATIONS
# =============================================================================
print("\n6. GENERATING VISUALIZATIONS...")
print("-" * 80)

# Plot 1: Score distribution by source
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1a. Composite score by source
axes[0, 0].hist([df[df['source']=='known']['composite_score'],
                 df[df['source']=='generated']['composite_score']],
                label=['Known', 'Novel'], bins=15, alpha=0.7)
axes[0, 0].set_xlabel('Composite Score')
axes[0, 0].set_ylabel('Count')
axes[0, 0].set_title('Composite Score Distribution')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# 1b. Light vs Washing Fastness
for source, color in [('known', 'blue'), ('generated', 'red')]:
    data = df[df['source'] == source]
    axes[0, 1].scatter(data['light_fastness_score'], data['washing_fastness_score'],
                      alpha=0.6, s=100, c=color, label=source.capitalize())
axes[0, 1].set_xlabel('Light Fastness Score')
axes[0, 1].set_ylabel('Washing Fastness Score')
axes[0, 1].set_title('Light vs Washing Fastness')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

# 1c. Scaffold performance
scaffold_means = df.groupby('scaffold')['composite_score'].mean().sort_values()
scaffold_means.plot(kind='barh', ax=axes[1, 0], color='steelblue')
axes[1, 0].set_xlabel('Average Composite Score')
axes[1, 0].set_title('Performance by Scaffold Type')
axes[1, 0].grid(True, alpha=0.3, axis='x')

# 1d. Color family distribution
color_counts = df['color_family'].value_counts()
axes[1, 1].pie(color_counts.values, labels=color_counts.index, autopct='%1.1f%%',
               startangle=90)
axes[1, 1].set_title('Color Family Distribution')

plt.tight_layout()
plt.savefig('dye_screening_analysis.png', dpi=300, bbox_inches='tight')
print(f"Saved: dye_screening_analysis.png")

# Plot 2: Top candidates comparison
fig, ax = plt.subplots(figsize=(14, 8))

top_15 = df.nsmallest(15, 'composite_score').sort_values('composite_score')
x = np.arange(len(top_15))
width = 0.25

ax.barh(x - width, top_15['light_fastness_score']/8, width, label='Light Fastness (normalized)', alpha=0.8)
ax.barh(x, top_15['washing_fastness_score']/5, width, label='Washing Fastness (normalized)', alpha=0.8)
ax.barh(x + width, top_15['composite_score'], width, label='Composite Score', alpha=0.8)

ax.set_yticks(x)
ax.set_yticklabels([f"{row['name'][:25]}" for _, row in top_15.iterrows()], fontsize=8)
ax.set_xlabel('Score (normalized)')
ax.set_title('Top 15 Dye Candidates - Multi-Property Comparison')
ax.legend()
ax.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig('top_candidates_comparison.png', dpi=300, bbox_inches='tight')
print(f"Saved: top_candidates_comparison.png")

# Plot 3: Property correlations heatmap
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
            square=True, linewidths=1, ax=ax, fmt='.2f')
ax.set_title('Property Correlation Matrix')
plt.tight_layout()
plt.savefig('property_correlations.png', dpi=300, bbox_inches='tight')
print(f"Saved: property_correlations.png")

print()
print("="*80)
print("ANALYSIS COMPLETE")
print("="*80)
