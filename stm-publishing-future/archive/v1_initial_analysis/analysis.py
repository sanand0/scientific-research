#!/usr/bin/env python3
"""
STM Publishing Evolution Analysis
Visualizations and trend analysis for the future of scientific publishing
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
import seaborn as sns

# Set style for professional-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

# 1. Research Volume Growth (2016-2030 projection)
def plot_volume_growth():
    """Visualize exponential growth in research articles"""
    years = np.arange(2016, 2031)

    # Based on 5.6% annual growth, 3.3M in 2022
    base_2022 = 3.3  # million articles
    traditional_pubs = base_2022 / (1.056 ** (2022 - 2016)) * (1.056 ** (years - 2016))

    # Preprints doubling every 5.6 years (faster growth ~12.8% annually)
    preprints_2024 = 0.056  # bioRxiv + medRxiv in millions
    preprints = preprints_2024 / (1.128 ** (2024 - 2016)) * (1.128 ** (years - 2016))

    # Simulate "reading capacity" - grows much slower (assume 2% annually)
    reading_capacity_base = 100  # arbitrary units
    reading_capacity = reading_capacity_base * (1.02 ** (years - 2016))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # Top plot: Absolute volumes
    ax1.plot(years, traditional_pubs, marker='o', linewidth=2, label='Traditional Publications', color='#2E86AB')
    ax1.plot(years, preprints, marker='s', linewidth=2, label='Preprints', color='#A23B72')
    ax1.axvline(x=2025, color='gray', linestyle='--', alpha=0.5, label='Present')
    ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Articles (Millions)', fontsize=12, fontweight='bold')
    ax1.set_title('The Research Volume Explosion: 2016-2030', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper left', fontsize=11)
    ax1.grid(True, alpha=0.3)

    # Add annotation for key insight
    ax1.annotate('47% growth\n2016→2022',
                xy=(2022, traditional_pubs[6]),
                xytext=(2020, 4.5),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))

    # Bottom plot: The engagement crisis
    ax2.fill_between(years, 0, traditional_pubs, alpha=0.3, color='#2E86AB', label='Total articles published')
    ax2.plot(years, reading_capacity, marker='o', linewidth=3,
             color='#F18F01', label='Scientist reading capacity (est.)', linestyle='--')
    ax2.axvline(x=2025, color='gray', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Volume (Normalized)', fontsize=12, fontweight='bold')
    ax2.set_title('The Deluge Paradox: Growing Output vs. Stagnant Attention',
                 fontsize=14, fontweight='bold')
    ax2.legend(loc='upper left', fontsize=11)
    ax2.grid(True, alpha=0.3)

    # Add shaded "crisis zone"
    crisis_start = 2020
    crisis_idx = np.where(years >= crisis_start)[0]
    ax2.fill_between(years[crisis_idx],
                     reading_capacity[crisis_idx],
                     traditional_pubs[crisis_idx],
                     alpha=0.2, color='red', label='Widening gap')

    plt.tight_layout()
    plt.savefig('/home/user/scientific-research/stm-publishing-future/volume_growth.png',
                dpi=300, bbox_inches='tight')
    print("✓ Saved: volume_growth.png")
    plt.close()


# 2. Business Model Evolution
def plot_business_model_evolution():
    """Visualize the shift from subscription to open access models"""
    years = np.arange(2015, 2031)

    # Modeled market share percentages
    subscription = 100 - 5*(years-2015)**0.7
    subscription = np.clip(subscription, 20, 100)

    gold_oa = 5 + 2.5*(years-2015)
    gold_oa = np.clip(gold_oa, 0, 35)

    diamond_oa = np.zeros_like(years, dtype=float)
    diamond_oa[years >= 2020] = 2 * (years[years >= 2020] - 2020)**1.2
    diamond_oa = np.clip(diamond_oa, 0, 30)

    preprint_first = np.zeros_like(years, dtype=float)
    preprint_first[years >= 2020] = 1.5 * (years[years >= 2020] - 2020)**1.3
    preprint_first = np.clip(preprint_first, 0, 25)

    # Normalize to 100%
    total = subscription + gold_oa + diamond_oa + preprint_first
    subscription = (subscription / total) * 100
    gold_oa = (gold_oa / total) * 100
    diamond_oa = (diamond_oa / total) * 100
    preprint_first = (preprint_first / total) * 100

    fig, ax = plt.subplots(figsize=(14, 8))

    ax.fill_between(years, 0, subscription, alpha=0.7,
                    color='#8B0000', label='Subscription')
    ax.fill_between(years, subscription, subscription + gold_oa,
                    alpha=0.7, color='#FFD700', label='Gold OA (APCs)')
    ax.fill_between(years, subscription + gold_oa,
                    subscription + gold_oa + diamond_oa,
                    alpha=0.7, color='#4169E1', label='Diamond OA (No fees)')
    ax.fill_between(years, subscription + gold_oa + diamond_oa, 100,
                    alpha=0.7, color='#32CD32', label='Preprint-First')

    ax.axvline(x=2025, color='white', linestyle='--', linewidth=2, label='Present')
    ax.axvline(x=2024, color='orange', linestyle='--', linewidth=2,
               alpha=0.7, label='Plan S ends transformative deals')

    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Market Share (%)', fontsize=12, fontweight='bold')
    ax.set_title('The Great Business Model Transition: From Paywalls to Open Access',
                fontsize=14, fontweight='bold')
    ax.legend(loc='center left', fontsize=11, framealpha=0.9)
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.3, axis='y')

    # Add annotation
    ax.annotate('Gates Foundation\nstops paying APCs',
                xy=(2024, 50),
                xytext=(2021, 70),
                arrowprops=dict(arrowstyle='->', color='white', lw=2),
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='orange', alpha=0.8),
                color='white')

    plt.tight_layout()
    plt.savefig('/home/user/scientific-research/stm-publishing-future/business_models.png',
                dpi=300, bbox_inches='tight')
    print("✓ Saved: business_models.png")
    plt.close()


# 3. Research Consumption Evolution
def plot_consumption_evolution():
    """Visualize how researchers consume scientific literature"""
    categories = ['Traditional\nJournal Reading', 'Preprint\nServers',
                  'AI\nSummarization', 'Social Media\nDiscovery',
                  'Executable\nNotebooks', 'Nano-\npublications']

    usage_2020 = [85, 25, 5, 30, 5, 2]
    usage_2025 = [45, 60, 70, 50, 25, 10]
    usage_2030_projected = [25, 75, 90, 60, 60, 40]

    x = np.arange(len(categories))
    width = 0.25

    fig, ax = plt.subplots(figsize=(14, 8))

    bars1 = ax.bar(x - width, usage_2020, width, label='2020',
                   color='#003f5c', alpha=0.8)
    bars2 = ax.bar(x, usage_2025, width, label='2025 (Current)',
                   color='#bc5090', alpha=0.8)
    bars3 = ax.bar(x + width, usage_2030_projected, width, label='2030 (Projected)',
                   color='#ffa600', alpha=0.8)

    ax.set_xlabel('Consumption Method', fontsize=12, fontweight='bold')
    ax.set_ylabel('Adoption Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title('The Fragmentation of Research Consumption: 2020-2030',
                fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=10)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(0, 100)

    # Add value labels on bars
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            if height > 5:
                ax.text(bar.get_x() + bar.get_width()/2., height - 5,
                       f'{int(height)}%',
                       ha='center', va='top', fontweight='bold',
                       fontsize=8, color='white')

    plt.tight_layout()
    plt.savefig('/home/user/scientific-research/stm-publishing-future/consumption_evolution.png',
                dpi=300, bbox_inches='tight')
    print("✓ Saved: consumption_evolution.png")
    plt.close()


# 4. File Format Evolution Timeline
def plot_format_timeline():
    """Timeline showing evolution of publication formats"""
    fig, ax = plt.subplots(figsize=(14, 6))

    # Define eras and formats
    eras = [
        {'start': 1990, 'end': 2010, 'name': 'Print Era', 'color': '#8B4513', 'y': 0},
        {'start': 2000, 'end': 2015, 'name': 'PDF Era', 'color': '#DC143C', 'y': 1},
        {'start': 2010, 'end': 2025, 'name': 'HTML/XML Era', 'color': '#4169E1', 'y': 2},
        {'start': 2020, 'end': 2035, 'name': 'Interactive/Executable Era', 'color': '#32CD32', 'y': 3},
    ]

    milestones = [
        {'year': 1991, 'text': 'arXiv\nlaunched', 'y': 0.5},
        {'year': 2013, 'text': 'bioRxiv\nlaunched', 'y': 1.5},
        {'year': 2024, 'text': 'SciPy Proceedings\nJupyter integration', 'y': 2.8},
        {'year': 2025, 'text': 'Jupyter Book 2.0\nExecutable papers', 'y': 3.2},
        {'year': 2025, 'text': 'openRxiv\nformed', 'y': 2.2},
    ]

    # Draw eras
    for era in eras:
        width = era['end'] - era['start']
        rect = Rectangle((era['start'], era['y'] - 0.3), width, 0.6,
                         facecolor=era['color'], alpha=0.6, edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(era['start'] + width/2, era['y'], era['name'],
               ha='center', va='center', fontweight='bold', fontsize=11, color='white')

    # Draw milestones
    for milestone in milestones:
        ax.plot([milestone['year'], milestone['year']], [0, 3.5],
               'k--', alpha=0.3, linewidth=1)
        ax.scatter(milestone['year'], milestone['y'], s=200,
                  color='yellow', edgecolor='black', linewidth=2, zorder=5)
        ax.text(milestone['year'], milestone['y'] + 0.5, milestone['text'],
               ha='center', va='bottom', fontsize=9, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

    # Current year marker
    ax.axvline(x=2025, color='red', linestyle='-', linewidth=3, alpha=0.7, label='Present')

    ax.set_xlim(1988, 2037)
    ax.set_ylim(-0.5, 4)
    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_title('Evolution of Scientific Publication Formats',
                fontsize=14, fontweight='bold')
    ax.set_yticks([])
    ax.grid(True, alpha=0.2, axis='x')
    ax.legend(loc='upper left', fontsize=10)

    plt.tight_layout()
    plt.savefig('/home/user/scientific-research/stm-publishing-future/format_timeline.png',
                dpi=300, bbox_inches='tight')
    print("✓ Saved: format_timeline.png")
    plt.close()


# 5. Opportunities and Challenges Matrix
def plot_opportunity_challenge_matrix():
    """Quadrant plot showing opportunities vs challenges"""

    # Define stakeholders with impact and difficulty scores
    items = [
        # (x=feasibility, y=impact, label, category)
        (8, 9, 'AI-Powered\nDiscovery Tools', 'opportunity'),
        (7, 8, 'Executable\nNotebooks', 'opportunity'),
        (9, 7, 'Preprint-First\nPublishing', 'opportunity'),
        (6, 9, 'Diamond OA\nScaling', 'opportunity'),
        (8, 6, 'Nanopublications', 'opportunity'),
        (7, 7, 'Interactive\nVisualizations', 'opportunity'),

        (3, 9, 'Information\nOverload', 'challenge'),
        (4, 8, 'Peer Review\nCrisis', 'challenge'),
        (2, 8, 'Quality\nControl at Scale', 'challenge'),
        (5, 7, 'Citation\nGaming', 'challenge'),
        (4, 7, 'Sustainability\nof Diamond OA', 'challenge'),
        (3, 6, 'Platform\nFragmentation', 'challenge'),
    ]

    fig, ax = plt.subplots(figsize=(12, 10))

    # Separate opportunities and challenges
    opportunities = [item for item in items if item[3] == 'opportunity']
    challenges = [item for item in items if item[3] == 'challenge']

    # Plot
    opp_x = [item[0] for item in opportunities]
    opp_y = [item[1] for item in opportunities]
    opp_labels = [item[2] for item in opportunities]

    chal_x = [item[0] for item in challenges]
    chal_y = [item[1] for item in challenges]
    chal_labels = [item[2] for item in challenges]

    ax.scatter(opp_x, opp_y, s=500, alpha=0.6, color='#32CD32',
              edgecolor='black', linewidth=2, label='Opportunities', zorder=3)
    ax.scatter(chal_x, chal_y, s=500, alpha=0.6, color='#DC143C',
              edgecolor='black', linewidth=2, label='Challenges', zorder=3)

    # Add labels
    for x, y, label, _ in opportunities:
        ax.text(x, y, label, ha='center', va='center',
               fontsize=8, fontweight='bold', color='white')

    for x, y, label, _ in challenges:
        ax.text(x, y, label, ha='center', va='center',
               fontsize=8, fontweight='bold', color='white')

    # Add quadrant lines
    ax.axhline(y=5, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax.axvline(x=5, color='gray', linestyle='--', linewidth=1, alpha=0.5)

    # Quadrant labels
    ax.text(7.5, 9.5, 'HIGH PRIORITY', ha='center', va='top',
           fontsize=11, fontweight='bold', alpha=0.3)
    ax.text(2.5, 9.5, 'HARD PROBLEMS', ha='center', va='top',
           fontsize=11, fontweight='bold', alpha=0.3)

    ax.set_xlabel('Feasibility / Ease of Implementation →', fontsize=12, fontweight='bold')
    ax.set_ylabel('Impact / Importance →', fontsize=12, fontweight='bold')
    ax.set_title('STM Publishing: Opportunities vs Challenges (2025-2030)',
                fontsize=14, fontweight='bold')
    ax.set_xlim(1, 10)
    ax.set_ylim(5, 10)
    ax.legend(loc='lower right', fontsize=11, framealpha=0.9)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('/home/user/scientific-research/stm-publishing-future/opportunity_matrix.png',
                dpi=300, bbox_inches='tight')
    print("✓ Saved: opportunity_matrix.png")
    plt.close()


# 6. Summary Statistics Table
def generate_summary_stats():
    """Create summary statistics visualization"""

    stats_data = {
        'Metric': [
            'Total Articles (2022)',
            'Annual Growth Rate',
            'Preprint Growth Rate',
            'Open Access Percentage',
            'AI Tool Adoption',
            'Diamond OA Journals',
            'Attention Span Decline',
            'Market Size (2022)',
        ],
        'Value': [
            '3.3M',
            '+5.6%/yr',
            '+12.8%/yr',
            '~50%',
            '70%+',
            '29,000',
            '2.5min → 47sec',
            '$12.65B',
        ],
        'Trend': [
            '↑',
            '↑',
            '↑↑',
            '↑',
            '↑↑',
            '↑',
            '↓',
            '↑',
        ]
    }

    df = pd.DataFrame(stats_data)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('tight')
    ax.axis('off')

    table = ax.table(cellText=df.values, colLabels=df.columns,
                    cellLoc='center', loc='center',
                    colWidths=[0.5, 0.3, 0.2])

    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.5)

    # Style header
    for i in range(len(df.columns)):
        table[(0, i)].set_facecolor('#2E86AB')
        table[(0, i)].set_text_props(weight='bold', color='white')

    # Style rows
    for i in range(1, len(df) + 1):
        for j in range(len(df.columns)):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#E8E8E8')
            else:
                table[(i, j)].set_facecolor('#FFFFFF')

            # Highlight trend column
            if j == 2:
                if '↑↑' in table[(i, j)].get_text().get_text():
                    table[(i, j)].set_facecolor('#90EE90')
                elif '↑' in table[(i, j)].get_text().get_text():
                    table[(i, j)].set_facecolor('#FFFFE0')
                elif '↓' in table[(i, j)].get_text().get_text():
                    table[(i, j)].set_facecolor('#FFB6C6')

    ax.set_title('Key Metrics: STM Publishing Landscape 2025',
                fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig('/home/user/scientific-research/stm-publishing-future/summary_stats.png',
                dpi=300, bbox_inches='tight')
    print("✓ Saved: summary_stats.png")
    plt.close()


if __name__ == '__main__':
    print("Generating visualizations for STM Publishing Evolution Analysis...")
    print()

    plot_volume_growth()
    plot_business_model_evolution()
    plot_consumption_evolution()
    plot_format_timeline()
    plot_opportunity_challenge_matrix()
    generate_summary_stats()

    print()
    print("✓ All visualizations generated successfully!")
    print()
    print("Files created:")
    print("  - volume_growth.png")
    print("  - business_models.png")
    print("  - consumption_evolution.png")
    print("  - format_timeline.png")
    print("  - opportunity_matrix.png")
    print("  - summary_stats.png")
