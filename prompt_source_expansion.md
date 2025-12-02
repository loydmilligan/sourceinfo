# Source Database Expansion Request

I'm building a comprehensive database of news sources and content publishers to support content rating and analysis. The database currently contains **121 sources** with credibility ratings (NewsGuard scores 0-100) and political bias ratings (AllSides scale: Left, Lean Left, Center, Lean Right, Right).

## Current Database Analysis

### Political Balance Distribution
- **Left**: 13 sources
- **Lean Left**: 25 sources (overrepresented)
- **Center**: 12 sources
- **Lean Right**: 12 sources
- **Right**: 13 sources

**Gap**: Need more Center sources and slight boost to Right/Lean Right to balance the Lean Left dominance.

### Source Type Distribution
- **News Media**: 115 sources (95%)
- **Fact Check**: 4 sources
- **News Aggregator**: 1 source
- **Think Tank/Policy**: 1 source

**Gap**: Severely lacking diversity in source types. Need more fact-checkers, aggregators, think tanks, specialized verticals.

### Geographic Coverage
**Minimal international representation**. Currently have only:
- BBC (UK)
- Daily Mail (UK)
- CBC (Canada)
- Global News (Canada)
- Independent (UK)
- Al Jazeera (Qatar)
- Deutsche Welle (Germany)

**Gap**: Missing major regions:
- Asia-Pacific (Australia, India, Japan, South Korea, Singapore)
- Europe (France, Spain, Italy, Scandinavia, Eastern Europe)
- Latin America (Brazil, Mexico, Argentina)
- Middle East (beyond Al Jazeera)
- Africa (South Africa, Nigeria, Kenya)

### Industry/Vertical Coverage
**Almost entirely general news and politics**. Missing specialized journalism:

**Technology**: None found
- No TechCrunch, Ars Technica, The Verge, Wired, The Information, Protocol, etc.

**Business/Finance**: Minimal (Bloomberg, WSJ, Forbes, Economist, Fox Business, MarketWatch, FT)
- Could add: Barron's, Business Insider, CNBC, Financial Times, Quartz, etc.

**Entertainment/Culture**: None
- Missing: Variety, Hollywood Reporter, Rolling Stone, Pitchfork, AV Club, Entertainment Weekly

**Science/Health**: None
- Missing: Scientific American, Nature News, Science Magazine, STAT News, MedPage Today

**Sports**: None
- Missing: ESPN, The Athletic, Sports Illustrated, Bleacher Report

**Local/Regional**: Very limited (few city papers like Boston Globe, Dallas News, Chicago Tribune)

---

## Your Task: Recommend Sources to Fill These Gaps

Please analyze the gaps above and recommend **50-75 high-quality sources** to add to the database, organized by category:

### 1. **International Sources** (15-20 sources)
Focus on respected English-language outlets from underrepresented regions:
- Australia, India, Japan, South Korea, Singapore
- France, Germany, Spain, Scandinavia
- Brazil, Mexico
- Middle East, Africa

For each source provide:
- Domain
- Name
- Country/Region
- Brief description of reputation/reach
- Your estimate of political lean if applicable (or "N/A" for international sources where US left/right doesn't apply)

### 2. **Technology Journalism** (10-12 sources)
Both mainstream tech news and specialist publications:
- Consumer tech news
- Enterprise/B2B tech
- Deep technical reporting
- Industry analysis

For each: Domain, Name, Lean (if applicable), distinguishing characteristics

### 3. **Business/Finance** (8-10 sources)
Publications beyond what we already have:
- Financial news
- Business analysis
- Industry-specific outlets
- Economic policy

### 4. **Specialized Verticals** (8-10 sources each)
- **Science/Health**: Medical, scientific, research journalism
- **Entertainment/Culture**: TV, film, music, arts coverage
- **Sports**: General and analysis-focused sports journalism

### 5. **Balance & Quality Additions** (10-15 sources)
Help balance the political spectrum and fill quality gaps:
- **Center sources**: Non-partisan, balanced reporting
- **Lean Right/Right**: Credible conservative outlets (to balance Lean Left dominance)
- **Fact-checkers**: More fact-checking organizations
- **Think tanks**: Policy research organizations across the spectrum

### 6. **Alternative/Independent Media** (5-8 sources)
- Substack publishers with significant reach
- Independent investigative outlets
- Newsletter platforms
- Emerging digital-native publications

---

## Output Format

Please provide recommendations in **JSON format** like this:

```json
{
  "international": [
    {
      "domain": "example.com",
      "name": "Example News",
      "country": "Australia",
      "description": "Major Australian newspaper, centrist, high circulation",
      "estimated_lean": "Center",
      "notes": "English-language, covers Asia-Pacific region extensively"
    }
  ],
  "technology": [
    {
      "domain": "example.com",
      "name": "Example Tech",
      "estimated_lean": "Lean Left",
      "description": "Consumer tech news, reviews, analysis",
      "notes": "One of the most-read tech publications globally"
    }
  ],
  "business": [...],
  "science_health": [...],
  "entertainment": [...],
  "sports": [...],
  "balance_quality": [...],
  "alternative_independent": [...]
}
```

### Important Notes:
1. **Prioritize sources likely to have NewsGuard ratings** (major, established outlets)
2. **Include a mix of US and international** sources
3. **For specialized verticals** (tech, entertainment, sports), US left/right bias may not apply meaningfully - note "N/A" or "Industry-specific" if so
4. **Avoid highly partisan or low-credibility sources** unless they're significant for understanding the media landscape
5. **Include both subscription and free sources**
6. **If uncertain about political lean**, note your reasoning (e.g., "Lean Left - progressive editorial stance but fact-based reporting")

---

## Additional Context

The database will be used to:
- Rate content quality based on source domain
- Provide counternarrative suggestions (e.g., if someone reads NYT, suggest credible right-leaning sources)
- Understand content context by incorporating source reputation
- Support media literacy by surfacing source bias and credibility

Your recommendations will help create a more balanced, globally-aware, and industry-comprehensive database for content analysis.
