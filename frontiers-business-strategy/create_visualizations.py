#!/usr/bin/env python3
"""
Create visualizations for Frontiers business strategy analysis
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 11

# Load data
with open('publication_analysis.json', 'r') as f:
    data = json.load(f)

# Create figure with subplots
fig = plt.figure(figsize=(16, 12))

# === PLOT 1: Current Frontiers Focus (2023-2024) ===
ax1 = plt.subplot(2, 2, 1)
focus_data = data["CURRENT FRONTIERS FOCUS"]
journals = list(focus_data.keys())
counts = list(focus_data.values())

# Sort by count
sorted_pairs = sorted(zip(journals, counts), key=lambda x: x[1], reverse=True)
journals, counts = zip(*sorted_pairs)

colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(journals)))
bars = ax1.barh(journals, counts, color=colors)
ax1.set_xlabel('Articles Published (2023-2024)', fontsize=12, fontweight='bold')
ax1.set_title('Frontiers Current Focus: Traditional Fields Dominate',
              fontsize=14, fontweight='bold', pad=15)
ax1.grid(axis='x', alpha=0.3)

# Add value labels
for i, (j, c) in enumerate(zip(journals, counts)):
    ax1.text(c + 200, i, f'{c:,}', va='center', fontsize=10)

# === PLOT 2: Market Share Comparison ===
ax2 = plt.subplot(2, 2, 2)

fields = ['Neuroscience', 'Immunology', 'AI/ML', 'Climate']
frontiers_counts = [8381, 12416, 600, 6]
total_counts = [57545, 162999, 110438, 43442]
market_shares = [(f/t)*100 for f, t in zip(frontiers_counts, total_counts)]

x = np.arange(len(fields))
width = 0.35

# Use colors to indicate strong vs weak positions
bar_colors = ['#2ecc71' if share > 5 else '#e74c3c' if share < 1 else '#f39c12'
              for share in market_shares]

bars = ax2.bar(x, market_shares, width, color=bar_colors, alpha=0.8)

ax2.set_ylabel('Market Share (%)', fontsize=12, fontweight='bold')
ax2.set_title('Market Share: Strong in Legacy, Weak in Growth Areas',
              fontsize=14, fontweight='bold', pad=15)
ax2.set_xticks(x)
ax2.set_xticklabels(fields, fontsize=11)
ax2.grid(axis='y', alpha=0.3)

# Add value labels on bars
for i, (bar, share) in enumerate(zip(bars, market_shares)):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{share:.2f}%',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

# Add legend
strong = mpatches.Patch(color='#2ecc71', label='Strong (>5%)', alpha=0.8)
medium = mpatches.Patch(color='#f39c12', label='Medium (1-5%)', alpha=0.8)
weak = mpatches.Patch(color='#e74c3c', label='Weak (<1%)', alpha=0.8)
ax2.legend(handles=[strong, medium, weak], loc='upper right', fontsize=10)

# === PLOT 3: Growth Opportunity Gap ===
ax3 = plt.subplot(2, 2, 3)

growth_topics = data["GROWTH POTENTIAL TOPICS (ALL PUBMED)"]
topics = list(growth_topics.keys())
pubmed_counts = list(growth_topics.values())

# Frontiers presence (estimated from earlier data)
frontiers_presence = [50, 600, 200, 100, 50]  # Rough estimates

sorted_idx = np.argsort(pubmed_counts)[::-1]
topics = [topics[i] for i in sorted_idx]
pubmed_counts = [pubmed_counts[i] for i in sorted_idx]
frontiers_presence = [frontiers_presence[i] for i in sorted_idx]

x = np.arange(len(topics))
width = 0.35

bars1 = ax3.bar(x - width/2, pubmed_counts, width, label='Total Market',
                color='#3498db', alpha=0.8)
bars2 = ax3.bar(x + width/2, frontiers_presence, width, label='Frontiers',
                color='#e74c3c', alpha=0.8)

ax3.set_ylabel('Articles (2023-2024)', fontsize=12, fontweight='bold')
ax3.set_title('The Opportunity Gap: Frontiers Missing High-Growth Fields',
              fontsize=14, fontweight='bold', pad=15)
ax3.set_xticks(x)
ax3.set_xticklabels(topics, rotation=45, ha='right', fontsize=10)
ax3.legend(fontsize=11)
ax3.grid(axis='y', alpha=0.3)
ax3.set_yscale('log')

# Add gap annotations
for i, (pm, fr) in enumerate(zip(pubmed_counts, frontiers_presence)):
    gap = ((pm - fr) / pm) * 100
    ax3.text(i, pm * 0.3, f'{gap:.0f}% gap',
            ha='center', fontsize=9, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))

# === PLOT 4: Strategic Positioning Matrix ===
ax4 = plt.subplot(2, 2, 4)

# Data for positioning: (market_size, frontiers_share, label)
positions = [
    (162999, 7.62, 'Immunology', '#2ecc71'),
    (57545, 14.56, 'Neuroscience', '#2ecc71'),
    (110438, 0.54, 'AI/ML', '#e74c3c'),
    (43442, 0.01, 'Climate', '#e74c3c'),
    (16629, 3.6, 'Gene Editing', '#f39c12'),
    (8662, 1.2, 'Precision Med', '#f39c12'),
]

for market_size, share, label, color in positions:
    # Bubble size proportional to absolute count
    abs_count = (market_size * share) / 100
    size = np.sqrt(abs_count) * 3
    ax4.scatter(market_size, share, s=size, alpha=0.6, color=color)
    ax4.annotate(label, (market_size, share), fontsize=10, fontweight='bold',
                ha='center', va='center')

ax4.set_xlabel('Total Market Size (Articles)', fontsize=12, fontweight='bold')
ax4.set_ylabel('Frontiers Market Share (%)', fontsize=12, fontweight='bold')
ax4.set_title('Strategic Positioning: Current vs. Opportunity',
              fontsize=14, fontweight='bold', pad=15)
ax4.set_xscale('log')
ax4.grid(True, alpha=0.3)

# Add quadrant lines
ax4.axhline(y=5, color='gray', linestyle='--', alpha=0.5, linewidth=1)
ax4.axvline(x=50000, color='gray', linestyle='--', alpha=0.5, linewidth=1)

# Add quadrant labels
ax4.text(150000, 12, 'CURRENT\nSTRENGTH', fontsize=11, fontweight='bold',
        ha='center', va='center', alpha=0.3,
        bbox=dict(boxstyle='round', facecolor='green', alpha=0.1))
ax4.text(100000, 0.2, 'OPPORTUNITY\nGAP', fontsize=11, fontweight='bold',
        ha='center', va='center', alpha=0.3,
        bbox=dict(boxstyle='round', facecolor='red', alpha=0.1))

plt.tight_layout()
plt.savefig('frontiers_strategic_analysis.png', dpi=300, bbox_inches='tight')
print("Visualization saved as 'frontiers_strategic_analysis.png'")

# === Create simplified version for README ===
fig2 = plt.figure(figsize=(14, 8))

# Market share comparison
ax1 = plt.subplot(1, 2, 1)
fields = ['Neuroscience', 'Immunology', 'AI/ML', 'Climate/\nSustainability']
market_shares = [14.56, 7.62, 0.54, 0.01]
colors_simple = ['#2ecc71', '#2ecc71', '#e74c3c', '#e74c3c']

bars = ax1.bar(fields, market_shares, color=colors_simple, alpha=0.8)
ax1.set_ylabel('Market Share (%)', fontsize=13, fontweight='bold')
ax1.set_title('Frontiers: Strong in Legacy, Missing Growth',
              fontsize=15, fontweight='bold', pad=15)
ax1.grid(axis='y', alpha=0.3)

for bar, share in zip(bars, market_shares):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{share:.2f}%',
            ha='center', va='bottom', fontsize=12, fontweight='bold')

# Opportunity gap
ax2 = plt.subplot(1, 2, 2)
topics = ['CRISPR/\nGene Edit', 'Precision\nMedicine', 'Longevity/\nAging',
          'Quantum\nComputing']
market_size = [16629, 8662, 7608, 810]
frontiers_est = [600, 100, 200, 50]
gaps = [(m-f)/m*100 for m, f in zip(market_size, frontiers_est)]

bars = ax2.bar(topics, gaps, color='#e74c3c', alpha=0.8)
ax2.set_ylabel('Market Share Gap (%)', fontsize=13, fontweight='bold')
ax2.set_title('Massive Gaps in Emerging Fields',
              fontsize=15, fontweight='bold', pad=15)
ax2.grid(axis='y', alpha=0.3)
ax2.set_ylim([90, 100])

for bar, gap in zip(bars, gaps):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{gap:.1f}%',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('frontiers_opportunity_gap.png', dpi=300, bbox_inches='tight')
print("Simplified visualization saved as 'frontiers_opportunity_gap.png'")

plt.close('all')
print("\nAll visualizations created successfully!")
