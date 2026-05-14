# Opportunity Engine Agent
# Runs: Daily at 05:00
# Owner: Intelligence CEO Agent
# Purpose: Find new business niches before the market catches on.
#          Score them. Escalate winners to Qassim.

---

## WHAT IT DOES

Scans social platforms and market signals daily.
Finds trending niches, products, and business models.
Scores each on a 0-100 scale.
Anything ≥ 70 goes into the morning briefing for Qassim.
Anything below 70 is logged but not actioned.

---

## DAILY SCAN SOURCES

SOCIAL SIGNALS (via Apify):
→ Instagram: Reels with >100k views in last 48hrs in business/money/product niches
→ TikTok Shop: trending products (views + sold count + comment sentiment)
→ Pinterest: boards gaining saves in decorating, wedding, art, food, wellness
→ Reddit: r/entrepreneur, r/sidehustle, r/ecommerce, r/dropshipping
  (posts with 500+ upvotes about specific products or niches)

MARKET SIGNALS (via TinyFish + Apify):
→ Google Trends: spikes in product or service searches
→ Amazon Best Sellers: movement in rankings (rising = opportunity)
→ AliExpress Hot Products: volume + margin indicators
→ Gumroad discover page: digital products gaining traction
→ Etsy trending searches: what buyers are searching for now

COMPETITOR SIGNALS:
→ New Shopify stores in trending niches (BuiltWith / Apify)
→ New YouTube channels with fast early growth
→ New Gumroad products getting traction (recent + reviews growing)

---

## SCORING FRAMEWORK (0-100)

Each opportunity scored on 5 dimensions (20 pts each):

1. DEMAND SIGNAL (0-20)
   20: Multiple platforms showing signal simultaneously
   15: Strong signal on one platform
   10: Moderate signal
   5: Weak / single data point
   0: No signal

2. COMPETITION LEVEL (0-20)
   20: Niche is emerging — fewer than 5 established players
   15: Growing niche — under 20 players
   10: Established — room for differentiation
   5: Saturated — difficult to enter
   0: Dominated by brands we can't compete with

3. MARGIN POTENTIAL (0-20)
   20: >60% margin possible (digital products, affiliate, lead gen)
   15: 40-60% margin (dropshipping premium products)
   10: 25-40% margin (physical product with branding)
   5: <25% margin
   0: Commodity pricing, no margin

4. AGENT BUILDABILITY (0-20)
   20: Fully automatable with current stack
   15: Mostly automated, minor manual touchpoints
   10: Hybrid — agents + some Qassim time
   5: Significant manual work required
   0: Not automatable with current tools

5. SPEED TO REVENUE (0-20)
   20: First revenue possible within 7 days
   15: First revenue within 30 days
   10: 30-90 days
   5: 90+ days
   0: Speculative / long horizon

SCORE ≥ 70 → Brief Qassim in morning report
SCORE 50-69 → Log and monitor for 7 days — rescore
SCORE < 50 → Log and discard

---

## OUTPUT FORMAT (for morning briefing)

Each opportunity presented as:

OPPORTUNITY: [Name/Description]
SCORE: [X/100]
SIGNAL: [What triggered this — specific data point]
DEMAND: [Search volume / views / sales data]
COMPETITION: [How many players, how strong]
MARGIN MODEL: [How PluggedIN makes money — lead gen / affiliate / product]
BUILD TIME: [Hours 1-5 deployment timeline]
FIRST REVENUE: [Estimated days to first £]
RECOMMENDATION: Launch / Monitor / Pass
PROCEED?

---

## HOW TO RUN THIS AGENT (Claude Code)

```python
# Daily at 05:00 via scheduled task

from lib.apify_client import search_google_maps, scrape_website
from lib.tinyfish_client import scrape_reddit, browse_site
from lib.airtable_client import log_lead  # repurpose for opportunity logging
import anthropic

# 1. Pull signals from all sources
# 2. Pass to Claude Sonnet for scoring and analysis
# 3. Log all opportunities to Airtable (Opportunities table)
# 4. Filter score >= 70
# 5. Format briefing block for Chief of All Chiefs
# 6. Chief of All Chiefs includes in 06:30 synthesis
```

Prompt to use (pass to claude-sonnet-4-6):

"You are the Opportunity Engine for PluggedIN, an AI business
conglomerate. Analyse the following market signals and identify
the top 3 opportunities for new businesses we can launch using
our current agent stack. Score each 0-100 using the scoring
framework. Format as briefing blocks ready for Qassim's review."

---

## AIRTABLE LOGGING

Table: Opportunities
Fields:
- OpportunityName (text)
- Score (number)
- Source (text — where signal came from)
- SignalData (long text — raw data)
- MarginModel (text)
- Status (Pending / Approved / Monitoring / Passed)
- DiscoveredAt (date)
- LaunchedAt (date — filled if approved)
- LaunchID (link to Businesses table)

---

## CADENCE

Daily: Full scan of all sources → score → brief
Weekly: Review all Monitoring opportunities → rescore
Monthly: Performance review of launched opportunities
         (did the ones we launched actually make money?)
         Feed results back into scoring calibration.
