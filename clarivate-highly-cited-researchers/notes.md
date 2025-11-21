# Research Notes: Clarivate Highly Cited Researchers Analysis

## Objective
Analyze the Clarivate Highly Cited Researchers list to uncover surprising patterns, hidden stories, and actionable insights about the world's most influential scientists.

## Progress Log

### Step 1: Initial Setup
- Created project folder
- Starting data collection from Clarivate website

### Step 2: Data Source Investigation
- Clarivate website uses dynamic JavaScript loading
- Past Lists page doesn't expose direct download links via WebFetch
- 2025 list: 6,868 individuals, 7,131 awards, 1,300+ institutions, 60 countries
- 2024 list: 6,636 researchers, 1,200+ institutions, 59 countries
- Will attempt to scrape data programmatically

### Step 3: Successful Data Extraction Method
- Found WordPress AJAX endpoint: `wp-admin/admin-ajax.php`
- Action: `clv_hcr_members_filter`
- Returns HTML with researcher data in table format
- Successfully parsed HTML structure:
  - Researchers in `<tbody class="hcr-member">` elements
  - Data fields: name, category/field, institution, country, researcher_id
  - ~10 researchers per page
- Scraping all ~700 pages to collect full dataset (~7,000 researchers) - IN PROGRESS

### Step 4: Initial Analysis Results (Sample: 100 researchers)
- Created comprehensive analysis framework
- Key findings from sample:
  - US dominance: 50% of sample from United States
  - Geographic concentration: Top 3 countries = 65% of researchers
  - MIT leads institutions with 5 researchers (5% of sample)
  - "Cross-Field" category dominates (44% of researchers)
  - High institutional diversity: 71/83 institutions have only 1 researcher
- Generated visualizations: countries, institutions, fields, heatmaps

### Step 5: Publication Metadata Approach
Given the scale (7,000+ researchers), comprehensive publication extraction via APIs would be:
- Time-prohibitive (days of API calls)
- Rate-limited by PubMed/Scopus/Web of Science
- Potentially requiring paid API access

**Pragmatic Approach:**
1. Analyze patterns in Clarivate data (institutions, geography, fields) ✓
2. Use Clarivate's own metadata (ResearcherIDs) to infer patterns ✓
3. Sample notable subsets for deeper publication analysis if needed ✓
4. Focus on insights derivable from the structural data we have ✓

### Step 6: Analysis Complete (Sample: 100 researchers, Full scrape ongoing)

**Completed Analyses:**
- Geographic distribution & concentration metrics
- Institutional analysis & power law patterns
- Research field distribution
- Country-institution interactions
- Country-field specialization patterns
- Comprehensive visualizations (4 charts)

**Key Findings:**
1. Geographic concentration: Top 3 countries = 65% of researchers
2. Institutional power law: Top 10 institutions = 25%, while 85% have only 1 researcher
3. Cross-Field dominance: 44% of researchers classified as interdisciplinary
4. US hegemony: 50% of highly cited researchers despite 4% of global population

**Deliverables:**
- `README.md`: Malcolm Gladwell-style narrative report with executive summary
- `analyze_researchers.py`: Scalable analysis framework
- `viz_*.png`: Four publication-quality visualizations
- `analysis_summary.json`: Structured insights and statistics
- `extract_publications.py`: Framework for PubMed metadata extraction (sampled approach)

**Status:**
- Full scraper running in background (1,410/~7,000 researchers collected)
- Analysis framework tested and validated on sample
- Report can be updated with full dataset once scraping completes

### Step 7: Critical Self-Assessment (MAJOR REVISION)

**Errors Identified:**
- US share: Claimed 50%, actual 37.4% (overstated by 34%)
- China share: Claimed 4%, actual 19.7% (understated by 5×!)
- Top institution: Claimed MIT, actual is CAS with 258 (MIT is #5 with 85)

**Root Cause:**
Sample bias from alphabetical sorting. Names A-B are predominantly Western.
Chinese names (L, W, X, Y, Z) underrepresented in first 100 entries.

**Corrections Applied:**
- Used official Clarivate 2025 statistics
- Completely rewrote analysis with verified numbers
- Added SELF_CRITIQUE.md documenting errors
- Changed narrative from "US dominance" to "US-China duopoly"

### Step 8: New Insights from Corrected Analysis

**Key Findings (Verified):**
1. US-China duopoly: Together account for 57% of all awards
2. CAS leads all institutions globally (258 awards, 1.5× Harvard)
3. 432 exclusions for hyper-prolific authorship (mostly from China)
4. US share actually increased (reversal of multi-year decline)
5. 86% concentrated in just 10 countries

**Researcher Personas Created:**
- Nobel Laureate Type (quality over quantity)
- Prolific Producer (volume strategy)
- Method Maven (tools everyone cites)
- Review Synthesizer (field-defining reviews)
- Consortium Contributor (big science projects)
- Hot Topic Surfer (trending fields)

### Step 9: Final Deliverables

- README.md: Completely revised with correct data + self-critique
- SELF_CRITIQUE.md: Detailed analysis of errors and lessons learned
- researcher_personas.py: Framework for publication pattern analysis
- notes.md: Updated research log
