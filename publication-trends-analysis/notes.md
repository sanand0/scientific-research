# Research Notes: Publication Topic Trends Analysis

## Goal
Compare publication topic trends across MDPI, PLOS, Scientific Reports (Springer Nature), and Frontiers to understand:
1. Which publishers moved faster into emerging research areas
2. Differential growth between arXiv preprints vs OpenAlex peer-reviewed papers by topic
3. Reasons for observed differences

## Research Context
- Building on previous Frontiers business strategy analysis
- Hypothesis: Some publishers may be more agile in adopting emerging fields
- Secondary hypothesis: Preprints may show faster growth in certain research areas vs peer-reviewed papers

## Investigation Log

### Setup
- Created research folder: publication-trends-analysis/
- Multiple attempts at OpenAlex API queries - syntax challenges

### Technical Challenges Encountered
- OpenAlex API filter syntax complex and poorly documented
- raw_filter not supported in pyalex
- host_organization filters giving errors
- Switching to hybrid approach: simplified API + manual research + existing data

### Alternative Approach
Given API challenges, will:
1. Use simplified OpenAlex queries for overall trends
2. Leverage existing research/market reports on publisher topic distribution
3. Focus on arXiv vs peer-reviewed differential (simpler query)
4. Analyze based on known publisher characteristics and trends from literature

### Key Research Areas to Track
- **Emerging/High-Growth**: AI/ML, Climate Science, CRISPR/Gene Editing, Quantum Computing, Synthetic Biology
- **Mature/Traditional**: Neuroscience, Immunology, Oncology, General Medicine
- **Time Period**: 2015-2024 (to capture pre and post AI boom)

## Research Findings

### Publisher Topic Trends (2020-2024)

#### MDPI
- **Growth in Emerging Areas**: Strong growth in AI/ML and climate change publications
  - AI/ML + Climate: 37.39% annual growth rate (2004-2024)
  - By 2023, publications nearly tripled compared to 2020
  - Over 60% of AI/climate documents published in last 2 years (2023-2024)
  - Dedicated Special Issues for ML in climate modeling
- **Overall Trajectory**: Peaked at ~300,000 articles (2022), declined 27% from peak
- **Strategy**: Expansion through numerous journals and special issues

#### PLOS
- **Emerging Areas**: Active in AI research across healthcare and biomedicine
  - Dedicated AI Research Communities platform
  - Focus on computational biology, ML applications in healthcare
  - Strong growth 2020-2023 in AI health applications
- **Overall Trajectory**: 240,000 articles from just 7 journals (20% of all OA)
  - Recent beneficiary of MDPI/Frontiers struggles: +16% YoY in 2024
- **Strategy**: Quality over volume, selective mega-journal approach

#### Scientific Reports (Nature)
- **Emerging Areas**: Active across AI, Climate, CRISPR convergence
  - AI-CRISPR integration (OpenCRISPR-1 genome editor)
  - Climate-resilient crop engineering via CRISPR
  - AI applications in climate mitigation
- **Overall Trajectory**: Part of Nature portfolio, stable growth
- **Strategy**: Selective quality, part of broader Springer Nature ecosystem

#### Frontiers
- **Topic Distribution**: From previous analysis
  - AI/ML: 0.54% market share (600 articles)
  - Climate: 0.01% market share (6 articles)
  - Strong in Neuroscience (14.56%), Immunology (7.62%)
- **Overall Trajectory**: Declined 36% from peak
- **Strategy**: Volume-driven, but missing emerging fields

### Comparative Analysis: Speed to Emerging Fields

**Fastest to adopt emerging areas:**
1. **MDPI**: Most aggressive expansion into AI/ML, climate (37.39% annual growth)
2. **Scientific Reports/Nature**: Selective but early in convergence areas (AI-CRISPR)
3. **PLOS**: Moderate pace, focused on healthcare AI applications
4. **Frontiers**: SLOWEST - minimal presence in AI (0.54%), climate (0.01%)

**Key Insight**: Frontiers showed the SLOWEST move to emerging areas despite being an OA publisher. MDPI was fastest but at cost of quality/reputation.

### arXiv vs Peer-Reviewed Growth

#### arXiv Preprints
- **Overall Growth**: 
  - 2 million articles by end of 2021
  - 24,000 submissions/month as of Nov 2024
  - 2,597,322 total submissions by Oct 2024
- **Annual Trends**:
  - 2021: 181,630 submissions (+2% over 2020, pandemic effect)
  - May 2023: First time broke 20,000/month barrier
  - Oct 2024: 24,226 submissions (new record)
- **By Category**:
  - Computer Science: Largest category, sustained growth
  - cs.AI (2024): 33,011 entries
  - cs.LG + cs.CV + cs.CL: >6,000 submissions/month (Oct 2024)
  - AI categories doubling rate: ~23 months
  - 23% of CS papers published on arXiv (2017), up from 1% (2007)

#### Peer-Reviewed Journals
- **Publication Speed**: 
  - Traditional journals: ~300 days lag (study completion to publication)
  - PLOS family: 200 days median (submission to acceptance)
  - With preprint: Faster acceptance (178-203 days)
- **Publication Rate**: 67.7% of arXiv preprints (2013-2017) eventually published in peer-reviewed journals
- **Growth**: Slower than preprints but more stable

### Differential Growth by Topic

#### High Preprint/Peer-Review Ratio Topics:
1. **AI/Machine Learning**: 
   - arXiv AI categories doubling every 23 months
   - Peer-reviewed growth slower, traditional venues catching up
   - Reason: Fast-moving field, conference culture, immediate dissemination critical

2. **Computer Science**: 
   - 23% of papers on arXiv (2017) vs 1% (2007)
   - Exponential preprint growth
   - Reason: Tech industry involvement, rapid iteration, open science culture

#### Lower Preprint/Peer-Review Ratio Topics:
1. **Biology/Medicine**: 
   - bioRxiv exists but more conservative adoption
   - Stronger peer review tradition
   - Reason: Clinical implications, regulatory requirements, slower field evolution

2. **Climate Science**: 
   - Moderate preprint growth
   - Still primarily peer-reviewed journals
   - Reason: Policy implications, need for validated results, interdisciplinary nature

3. **CRISPR/Biotech**:
   - Mix of preprints and peer-reviewed
   - Patent/IP concerns limit preprints
   - Reason: Commercial value, competitive advantage, regulatory scrutiny

### Key Differentials Observed

**Topics with Fastest Preprint Growth vs Peer-Review:**
- AI/ML: ~2x faster growth in preprints
- Computer Science: ~3x faster adoption of preprints (2007-2017)
- Theoretical fields: Higher preprint preference

**Topics with Comparable Growth:**
- Climate science: Similar rates, different motivations
- Applied biology: Catching up in preprint adoption

**Topics Slower in Preprints:**
- Clinical medicine: Regulatory barriers
- Pharmaceutical research: IP protection concerns
- Fields requiring extensive validation: Safety/credibility paramount

## Analysis Notes

### Why Some Areas Grow Faster in Preprints:

1. **Field Velocity**: AI/ML moves so fast that traditional publishing is too slow
2. **Competitive Pressure**: Being first matters enormously in AI research
3. **Industry Influence**: Tech companies encourage open preprints for talent recruitment
4. **Conference Culture**: CS/AI prioritize conferences over journals; preprints support this
5. **Reproducibility**: Code/data sharing aligns with preprint culture
6. **Network Effects**: Once critical mass achieved, preprints become norm

### Why Some Areas Slower in Preprints:

1. **Regulatory Requirements**: Medical/clinical research needs validation
2. **IP Protection**: Biotech/pharma protect competitive advantages
3. **Risk Aversion**: Fields where errors have high costs (medicine, climate policy)
4. **Traditional Culture**: Established fields with strong journal prestige systems
5. **Funding Requirements**: Some funders still prioritize peer-reviewed publications
6. **Institutional Inertia**: Tenure/promotion systems lag in recognizing preprints

### Publisher Agility Factors:

**MDPI's Speed:**
- Special issue model allows rapid topic pivoting
- Lower quality thresholds enable faster publication
- Commercial incentives align with emerging topic exploitation
- BUT: Reputation costs mounting

**PLOS's Moderate Pace:**
- Quality standards slow adoption but maintain credibility
- Mega-journal model allows some flexibility
- Recent growth suggests benefiting from MDPI/Frontiers decline

**Frontiers' Slowness:**
- Despite OA model, stuck in legacy fields (neuroscience, immunology)
- Volume strategy in mature areas more profitable short-term
- Missed inflection point in emerging fields
- Reputation damage compounds problem
