# Knowledge Acquisition Agent
# Runs: Daily at 04:00 (before all other agents)
# Owner: Intelligence CEO Agent
# Purpose: Make every other agent smarter.
#          Continuously feeds the system with what's working
#          in every niche PluggedIN operates in.

---

## WHY THIS RUNS FIRST

Every other agent in the system is only as good as what it knows.
This agent runs at 04:00 so that by the time the Opportunity Engine,
Lead Gen Agents, and YouTube Agent run, they have the freshest
intelligence available.

Week 1: Agents at baseline knowledge.
Month 3: Agents know what every top practitioner in every niche knows.
Month 12: Impossible to compete with. The gap widens automatically.

---

## WHAT IT LEARNS FROM

YOUTUBE (via youtube-apify-transcript skill):
Channels monitored per niche:

Lead Gen / B2B:
→ Alex Hormozi, Sam Ovens, Jason Wojo, Cole Gordon

Ecommerce / Dropshipping:
→ Biaheza, Arie Scherson, Jordan Welch, Hayden Bowles

Digital Products / Gumroad:
→ Gumroad creator channels, Pat Flynn, Nathan Barry

YouTube Growth:
→ Matt D'Avella, Think Media, Paddy Galloway, Veritasium

AgriTrade / Commodities:
→ Trade finance channels, African business news, commodity desks

AI / Automation:
→ Liam Ottley, Ben's Bites, The AI Breakdown

REDDIT (via lib/tinyfish_client.py):
→ r/entrepreneur (what's working, what's failing)
→ r/ecommerce (product research, supplier tips)
→ r/dropshipping (real data from operators)
→ r/sidehustle (emerging models)
→ r/africanentrepreneurs (AgriTrade signals)
→ r/marketing (copywriting and ad angle trends)
→ r/SEO (content strategy updates)

NEWSLETTERS AND BLOGS (via TinyFish daily read):
→ The Hustle, Morning Brew (business trends)
→ ecommercefuel.com (operator-level ecom insights)
→ GrowthHackers (B2B growth tactics)
→ Demand Curve (conversion and ad copy)
→ Exploding Topics (early trend detection)

COMPETITOR MONITORING:
→ Top 3 AI agency operators — what they're selling, pricing, positioning
→ Lead gen network operators — how they structure deals
→ Top Gumroad sellers in PluggedIN niches — what sells, how priced

---

## WHAT IT DOES WITH KNOWLEDGE

After pulling content, the agent:

1. EXTRACTS INSIGHTS
   Passes transcripts/articles to Claude Sonnet:
   "Extract the 5 most actionable insights from this content
   relevant to [niche]. Format as specific tactics, not summaries."

2. UPDATES MEMORY FILES
   → memory/semantic/icp.md — new buyer language, new pain points
   → copy-framework.md — new hooks, angles, objection handles
   → scoring-criteria.md — updated signals for lead qualification
   → live/businesses/[niche].md — niche-specific intelligence updates

3. FLAGS SKILL IMPROVEMENTS
   If the agent learns a new tactic that requires a new capability:
   → Creates a draft skill improvement note
   → Adds to memory/working/today.md for Qassim review
   → Uses lib/github_client.py to search if a skill exists for it

4. UPDATES COPY FRAMEWORK
   Every week: re-ranks the top 3 hooks for each niche based on
   what's performing on YouTube and Reddit right now.

5. FEEDS OPPORTUNITY ENGINE
   If the Knowledge Agent spots a new trend — a new product category,
   a new business model, a new niche showing early signs —
   it logs it to the Opportunities table (score starts at 40)
   for the Opportunity Engine to pick up and full-score.

---

## OUTPUT FORMAT (daily update to memory)

```
## Knowledge Update — [Date]
Source: [YouTube channel / Reddit / Newsletter]
Niche: [Lead Gen / Ecommerce / AgriTrade / YouTube / Digital]

INSIGHTS:
1. [Actionable tactic or fact — specific enough to execute]
2. [...]
3. [...]

FILES UPDATED:
- [file path]: [what changed]

SKILL GAPS IDENTIFIED:
- [If any — what capability is missing]

OPPORTUNITY FLAGGED:
- [If any — sent to Opportunities table]
```

---

## HOW TO RUN THIS AGENT (Claude Code)

```python
# Daily at 04:00 via scheduled task

from lib.apify_client import scrape_website
from lib.tinyfish_client import scrape_reddit, browse_site
import anthropic

# 1. Pull YouTube transcripts (youtube-apify-transcript skill)
# 2. Pull Reddit posts from target subreddits
# 3. Browse 3 newsletters via TinyFish
# 4. Pass all to Claude Sonnet for extraction
# 5. Write updates to relevant memory files
# 6. Log to Airtable: KnowledgeLog table
```

Prompt template (per content piece):
"You are the Knowledge Acquisition Agent for PluggedIN.
Read this content and extract ONLY specific, actionable insights
that would help our agents perform better in [niche].
No summaries. No generic advice. Specific tactics with numbers
where possible. Max 5 insights. Format as numbered list."

---

## AIRTABLE LOGGING

Table: KnowledgeLog
Fields:
- Date (date)
- Source (text)
- Niche (text)
- InsightsExtracted (number)
- FilesUpdated (text — comma separated)
- SkillGapFlagged (checkbox)
- OpportunityFlagged (checkbox)
- ProcessingTimeSeconds (number)
