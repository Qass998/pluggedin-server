# PluggedIN Live Agents
# The agents running PluggedIN's own business portfolio
# Version 1.0 | June 2026

---

## CONTEXT

PluggedIN doesn't just sell to clients. We run our own businesses:
- Lead gen verticals (PlumbRight, SolarLink, BuildConnect, etc.)
- Ecommerce stores (winning products on Shopify)
- Digital products (Gumroad templates, Notion dashboards)
- YouTube channels (5 channels generating ad revenue + sponsorship)
- Commodity marketplace (African producers ↔ global buyers)

**These agents run 24/7.** Same skills we sell to clients. But we run them for ourselves.

---

## AGENT ARCHITECTURE

```
INTELLIGENCE LAYER (The Brain)
├─ Knowledge Acquisition Agent
├─ Opportunity Engine Agent
└─ Market Intelligence Agent

BUSINESS CREATION LAYER
├─ Dispatch Agent
├─ Brand Agent
└─ Website Agent

REVENUE LAYER (Money Generators)
├─ Lead Generation Agent (runs all verticals)
├─ Ecommerce Intelligence Agent
├─ Commodity Matching Agent
└─ YouTube Content Agent

CLIENT LAYER
├─ Onboarding Agent
├─ Pipeline Agent (runs for client)
├─ Retention Agent
└─ Marketing Agent

OPERATIONS LAYER
├─ KPI Agent
├─ Narrative Agent
├─ Review Agent
├─ Compliance Agent
├─ Client Success Agent
├─ Investor Relations Agent
└─ Opportunity Scanner Agent

COMMAND LAYER (Hierarchy)
├─ CEO Agent (per business)
├─ Head CEO Agent
└─ Chief of All Chiefs (reports to Qassim)
```

---

## INTELLIGENCE LAYER

### 1. KNOWLEDGE ACQUISITION AGENT
**Purpose:** Continuous learning (updates all skills + templates)

**What it does:**
- Scrapes YouTube transcripts (top 50 videos in each niche we operate)
- Reads Reddit communities (r/ecommerce, r/sales, r/startup)
- Monitors blogs + newsletters (morning.com, Trends, industry news)
- Tracks competitor moves (what are they doing better?)

**Output:**
- Weekly updates to skills/registry.md (new techniques discovered)
- Quarterly updates to copy-framework.md (winning language)
- ICP refinement (who's buying + why)

**Tools:**
- YouTube API (transcript extraction)
- TinyFish (Reddit scraping)
- news + blog feeds

**Schedule:** 3x per week (Tuesday, Thursday, Sunday)

---

### 2. OPPORTUNITY ENGINE AGENT
**Purpose:** Find winning products BEFORE market catches on

**What it does:**
- Scrapes Instagram (hashtags: #newproduct, trending)
- Scrapes TikTok Shop (new launches, engagement)
- Scrapes Pinterest (home decor, fashion, wellness trends)
- Scrapes Gumroad bestsellers (digital products)
- Tracks Amazon bestsellers (what's hot?)

**Scoring:**
```
Opportunity Score = 0-100
  - Engagement rate: weight 30%
  - Search volume trend: weight 25%
  - Supplier availability: weight 20%
  - Margin potential: weight 15%
  - Market saturation: weight 10%

ESCALATE if score > 70 (to Qassim + Ecommerce Agent)
```

**Output:**
- Daily "hot products" alert
- Weekly trend report
- Monthly "opportunity deck" (top 20 products)

**Tools:**
- Apify (scraping)
- Google Trends (search volume)
- product databases

**Schedule:** Daily (5am)

---

### 3. MARKET INTELLIGENCE AGENT
**Purpose:** Understand market movements before they matter

**What it does:**
- Tracks pricing trends (competitor pricing)
- Monitors demand curves (what's growing vs. declining)
- Detects supply chain disruptions
- Watches emerging technologies
- Tracks regulatory changes (affects what we can sell)

**Output:**
- Weekly briefing (market movements)
- Monthly report (trend analysis)
- Alerts (urgent market shifts)

**Tools:**
- Price tracking APIs
- News aggregators
- regulatory databases

**Schedule:** Continuous (real-time alerts)

---

## BUSINESS CREATION LAYER

### 4. DISPATCH AGENT
**Purpose:** Spin up new businesses in hours (not weeks)

**What it does:**
1. Receives opportunity from Opportunity Engine
2. Validates market + margin potential
3. Deploys infrastructure (within 4 hours):
   - Domain registered
   - Branding created (logo, color palette)
   - Website live (Framer or Shopify)
   - Lead/product lists seeded
4. Assigns CEO agent
5. Reports: ready to go

**Typical Output:**
```
Hour 0: Opportunity approved (score 78)
Hour 1: Domain + branding complete
Hour 2: Website live, SEO optimized
Hour 3: Product catalog loaded
Hour 4: First leads or products posted
Hour 5: CEO agent begins execution
```

**Tools:**
- Automation (domain registration)
- Brand Agent (visual identity)
- Website Agent (Framer/Shopify deploy)

**Schedule:** On-demand (whenever opportunity score > 70)

---

### 5. BRAND AGENT
**Purpose:** Create brand identity (used by Dispatch Agent)

**What it does:**
- Creates business name (if needed)
- Designs logo (brand mark)
- Defines color palette
- Writes tagline + brand voice
- Creates brand guidelines

**Output:**
- Logo (2-3 variations)
- Color palette (primary, secondary, accent)
- Tagline (1-2 sentence)
- Brand voice (tone of writing)
- Guidelines (one-pager)

**Tools:**
- Design API (Flux, Pika)
- Brand guidelines template

**Time:** 30 min per brand

---

### 6. WEBSITE AGENT
**Purpose:** Deploy websites instantly (Framer + Shopify)

**What it does:**
- Builds landing pages (Framer, high-converting)
- Builds product stores (Shopify, pre-populated)
- Builds lead capture forms
- SEO optimization (meta tags, structure)
- Analytics setup (Google Analytics, Facebook Pixel)

**Output:**
- Live website (domain pointing)
- Product pages (with images, descriptions)
- Email capture (lead list seeded)
- Analytics connected

**Tools:**
- Framer API
- Shopify API
- SEO automation

**Time:** 1-2 hours per website

---

## REVENUE LAYER

### 7. LEAD GENERATION AGENT (Runs all verticals)
**Purpose:** Find + enrich + sell leads in target verticals

**Verticals:**
1. **PlumbRight** — plumbers needing solar leads
2. **SolarLink** — solar companies needing quality leads
3. **BuildConnect** — construction companies needing labour/equipment
4. **LegalMatch** — solicitors needing case referrals
5. **MortgageMatch** — mortgage brokers needing client leads
6. **CareConnect** — care homes needing staff + residents

**Model:**
```
Step 1: Find leads (e.g., solar companies needing plumber referrals)
Step 2: Enrich (verify contact, decision-maker, buying signals)
Step 3: Score (fit for our buyers)
Step 4: Sell (to plumbers in network)
Step 5: Track (delivery, quality, repeat buyers)

Revenue: £25-50 per lead × 50 leads/week = £1,250-2,500/week per vertical
       × 6 verticals = £7,500-15,000/week = £30k-60k/month
```

**Agent Execution (per vertical):**
```
Daily (5am):
  1. Discover 50-100 raw leads (from sources)
  2. Enrich with emails, phones, decision-makers
  3. Score fit for our buyer network
  
Daily (noon):
  4. Verify quality (spot-check 10 leads)
  5. List as "available for sale" in Airtable
  
Daily (6pm):
  6. Notify buyers (Slack, email)
  7. Track who bought what
  8. Quality check (leads that don't convert = flag supplier)
```

**Expected Output:**
- 50 leads/week per vertical × 6 = 300 leads/week = £7,500-15,000/week revenue
- Cost: £0-2.50 per lead enrichment
- Gross margin: 95%+

**Tools:**
- Apify (discovery)
- Vibe Prospecting (enrichment)
- Airtable (marketplace)

**Schedule:** Daily (continuous)

---

### 8. ECOMMERCE INTELLIGENCE AGENT
**Purpose:** Find winning products → launch stores → scale via Meta ads

**Model:**
```
Step 1: Opportunity Engine finds hot product (score > 70)
Step 2: Deep analysis (margin, supplier, demand)
Step 3: Dispatch Agent deploys Shopify store
Step 4: Ecommerce Agent begins:
  - Upload products
  - Create product descriptions (SEO + conversions)
  - Source supplier (Alibaba, AliExpress)
  - Design product images (Flux)
  - Set pricing (margin calc: cost × 3-5x)
  - Launch Meta ads (find winning angles)
  
Step 5: Optimize (ROAS feedback loop)
  - If ROAS > 2.5x → scale ad spend
  - If ROAS < 2x → pause, test new angle
  - If ROAS < 1.5x → kill product

Revenue: £1k-10k per product per month
         × 10-20 active products = £10k-200k/month
```

**Agent Execution:**
```
Weekly (Monday):
  1. Review top 20 products from Opportunity Engine
  2. Deep-dive: margin, sourcing, competitors
  3. Select: launch 2-3 new stores
  
Wednesday:
  4. Deploy stores (Shopify)
  5. Launch Meta ads (test 3 angles per product)
  
Friday:
  6. Review ROAS data
  7. Optimize: scale winners, kill losers
  8. Compound: reinvest profits into winning products
```

**Expected Output:**
- 2-3 new stores/month
- 50% of products hit £1k+ monthly revenue
- 20% of products hit £5k+ monthly revenue
- Average ROAS: 2.5-3.5x

**Tools:**
- Shopify API
- Meta Ads API
- Product image generation (Flux)
- Supplier database

**Schedule:** Continuous (daily optimization)

---

### 9. COMMODITY MATCHING AGENT
**Purpose:** Connect African producers ↔ global buyers (transaction fee model)

**Model:**
```
Producers: cocoa, cashews, sesame, palm oil, shea butter, timber (Africa)
Buyers: food companies, cosmetics, timber importers (global)

Process:
  1. Find producer (has inventory)
  2. Find buyer (needs product)
  3. Verify both (quality, capacity, pricing)
  4. Facilitate deal (negotiation, contracts, payment)
  5. Take commission: 1-3% per transaction

Revenue: 1% × £500k deal = £5k commission
         × 10 deals/month = £50k/month
```

**Agent Execution:**
```
Continuous:
  1. Monitor producer capacity (WhatsApp, VAPI calls)
  2. Track buyer demand (email monitoring)
  3. Match: when overlap exists, negotiate deal
  4. Process: contracts, payment, logistics
  5. Track: delivery confirmation, quality feedback
```

**Expected Output:**
- 10-15 transactions per month
- Average deal: £500k-£1M
- Commission per deal: £5k-£15k
- Monthly revenue: £50k-£150k

**Tools:**
- VAPI (producer/buyer calls)
- Airtable (deal tracking)
- Stripe (payment processing)

**Schedule:** Continuous

---

### 10. YOUTUBE CONTENT AGENT
**Purpose:** Run 5 YouTube channels (faceless, automated)

**Channels:**
1. Health & Ingredients (wellness, supplements)
2. African History (documentary style)
3. Money & Business (personal finance, startup)
4. True Crime (narration)
5. AI & Tech Explained (data visualization)

**Model:**
```
Per channel: 3 videos/week
All channels: 15 videos/week = 60 videos/month

Revenue per channel: £1k-5k/month (AdSense + sponsorship + affiliate)
× 5 channels = £5k-25k/month

Most successful channel history: 6 month ROI = 500%+
```

**Agent Execution (per channel):**
```
Daily (9am):
  1. Check trending topics (Google Trends, Reddit)
  2. Generate script (ChatGPT or Claude)
  3. Create video (Creatomate + voiceover from ElevenLabs)
  4. Add captions (auto-generated)
  5. Optimize SEO (title, description, tags)
  
3x per week:
  6. Upload to YouTube (schedule for 6pm publish)
  7. Promote on social (clips to TikTok, Instagram)
  
Weekly:
  8. Monitor analytics (views, retention, CTR)
  9. Identify winners (best-performing topics)
  10. Double down (make 3 more videos on winning topic)
```

**Expected Output:**
- 60 videos/month
- 10-50k views per video (varies by topic)
- £1k-5k/month per channel
- Compound: best channels scale to £10k+/month

**Tools:**
- Creatomate (video generation)
- ElevenLabs (voiceover)
- YouTube API (upload, scheduling)
- Artlist (royalty-free music)
- TubeBuddy (SEO optimization)

**Schedule:** Automated (3x per week per channel)

---

## CLIENT LAYER

Agents that run for each signed client are the same as those in AGENT_CARDS.md (Pipeline, Presence, Intelligence, etc.).

These operate identically to our own agents, just in client's CRM.

---

## OPERATIONS LAYER

### 11. KPI AGENT
**Purpose:** Track all metrics across all businesses

**What it tracks:**
```
Lead Gen Verticals:
  - Leads discovered (per vertical)
  - Leads sold (per vertical, per buyer)
  - Revenue (per vertical)
  - Margin (cost vs. selling price)
  - Repeat buyers (loyalty)

Ecommerce:
  - Products active
  - Daily revenue (per product)
  - ROAS (per ad campaign)
  - Conversion rate
  - Refund rate

YouTube:
  - Views (per channel, per video)
  - Watch time (minutes)
  - Revenue (AdSense, sponsorship, affiliate)
  - Growth rate (subscriber gain)

Commodity:
  - Deals completed
  - Average deal value
  - Commission earned
  - Repeat partners

Clients (all):
  - MRR (monthly recurring)
  - Churn rate
  - NRR (net revenue retention)
  - CAC (customer acquisition cost)
  - LTV (lifetime value)
```

**Output:**
- Daily dashboard (KPI snapshot)
- Weekly report (trends)
- Monthly board pack (performance review)

---

### 12. NARRATIVE AGENT
**Purpose:** Create monthly video + PowerPoint reports

**Output:**
```
Monthly (end of month):
  1. Remotion video (2-3 min narrative)
     - "This month we generated £X revenue"
     - "Top product: [name] (£Xk revenue)"
     - "Best opportunity found: [industry] (score 85)"
     - "Portfolio update: 3 new businesses, 2 scaled"
  
  2. PowerPoint deck
     - Revenue breakdown (by business)
     - Growth trends (MoM)
     - Top opportunities (next quarter)
     - Team performance
```

---

### 13. REVIEW AGENT
**Purpose:** Manage reputation across all businesses

**What it does:**
- Monitor Google/Trustpilot reviews (all businesses)
- Respond professionally to negative reviews
- Feature positive reviews on social
- Track rating trends
- Remove defamatory/false reviews (if applicable)

**Output:**
- 4.6+ average rating maintained
- 50+ new reviews per month (aggregate)
- Zero unresponded reviews (within 24h)

---

### 14. COMPLIANCE AGENT
**Purpose:** Ensure legal compliance (licenses, contracts, deadlines)

**Tracks:**
- Business licenses (renewal dates)
- Tax deadlines (quarterly, annual)
- Supplier contracts (auto-renew alerts)
- Data privacy (GDPR, CCPA compliance)
- Insurance (coverage + renewal)

---

### 15. CLIENT SUCCESS AGENT
**Purpose:** Prevent churn + identify upsell opportunities

**What it does (per client):**
```
Monthly:
  1. Calculate health score (0-100)
     - Results delivered? (weight 40%)
     - Agent uptime? (weight 30%)
     - Response time to feedback? (weight 20%)
     - Expansion signals? (weight 10%)
  
  2. If score < 70: flag churn risk
     - Assign: human intervention (call client)
  
  3. If score > 80: identify upsell
     - "You're doing well with Pipeline Agent"
     - "Would Intelligence Agent help?"
     - "Recommend: Data Intelligence (£897/month)"

  4. Track: upsell success rate
     - Target: 30% of Scale clients upsell per year
     - Revenue impact: £10k+ per upsell
```

---

### 16. INVESTOR RELATIONS AGENT
**Purpose:** Track PluggedIN Live revenue + prepare fundraising materials

**Tracks:**
- Monthly revenue (all businesses)
- Growth rate (MoM, YoY)
- Profitability (margin per business)
- Customer metrics (if applicable)
- Competitive positioning

**Output:**
- Monthly revenue report
- Quarterly investor briefing
- Annual cap table + financial statements

---

### 17. OPPORTUNITY SCANNER AGENT
**Purpose:** Find new business verticals (same as Opportunity Engine but broader)

**What it does:**
- Scans Instagram, Reddit, TikTok for emerging niches
- Scores each: 0-100 (market size, margin, competition)
- Escalates scores > 70 to Qassim + CEO Agent
- Quarterly: presents "20 best opportunities next quarter"

**Examples found:**
```
Score 78: HVAC leads (growth signal: hiring spike)
Score 85: Wedding planning tools (niche pain point)
Score 72: Pet grooming supplies (trending on TikTok)
Score 81: AI-powered copywriting (huge market, first-mover advantage)
```

---

## COMMAND LAYER

### 18. CEO AGENT (per business segment)
**Purpose:** Make strategic decisions for a business unit

**Reports to:** Head CEO Agent

**What it does:**
```
Daily (6pm):
  1. Read sub-agent reports (all agents running that business)
  2. Review metrics (revenue, growth, issues)
  3. Make decisions:
     - Should we scale this business?
     - Should we pause this product?
     - Do we have resource constraints?
  4. Issue instructions to sub-agents
  5. Report to Head CEO Agent (tomorrow morning)

Weekly:
  6. Strategic review (quarter, year goals)
  7. Identify bottlenecks
  8. Recommend optimizations
```

**Example (Lead Gen CEO):**
```
Today's status:
  - PlumbRight: £8k revenue, 65 leads sold (healthy)
  - SolarLink: £5k revenue, but 40% quality issues (FIX IT)
  - BuildConnect: new vertical, £2k revenue (scale)

Decision:
  - Pause SolarLink quality issue (investigate supplier)
  - 2x ad spend on BuildConnect (trending up)
  - Monitor PlumbRight (already optimal)
```

---

### 19. HEAD CEO AGENT
**Purpose:** Synthesize across all CEO Agents + recommend strategy

**Reports to:** Chief of All Chiefs (who reports to Qassim)

**What it does:**
```
Weekly (Sunday 6pm):
  1. Read all CEO Agent reports (lead gen, ecommerce, youtube, etc.)
  2. Synthesize: which businesses winning, which struggling?
  3. Identify cross-business opportunities
     - "Lead gen is strong, suggest we sell lead gen as a service"
     - "YouTube is struggling, recommend: double content investment OR pivot"
  4. Recommend portfolio strategy
  5. Report to Chief of All Chiefs
```

---

### 20. CHIEF OF ALL CHIEFS
**Purpose:** One daily briefing for Qassim (synthesizes everything)

**Reads:**
- All business metrics
- All CEO Agent decisions
- All client updates
- All opportunities > 70 score
- All risks/issues

**Output: One WhatsApp message per day (250 words max)**

```
📊 PluggedIN Daily Briefing | June 8, 2026

SITUATION:
Lead gen generating £35k MRR (4 verticals strong, SolarLink under review).
Ecommerce portfolio at £22k MRR (3 products > 5x ROAS).
YouTube: 150k views this week (growth 15% MoM).
Clients: £45k MRR (3 on Scale package), 0% churn.
Total PluggedIN revenue: £102k MRR.

PRIORITY:
Fix SolarLink quality issues (leads bouncing).

RECOMMENDATION:
Investigate supplier → re-qualify or replace.
Expected outcome: restore £5k MRR within 1 week.

DECISIONS NEEDED:
1. Approve 2x ad spend on BuildConnect? (projected ROI: 3.5x)
2. Launch 2 new YouTube channels? (3x content output)

Actions queued. Proceed? GO / ADJUST / CANCEL
```

---

## FINANCIAL MODEL

**Total PluggedIN Monthly Revenue (at scale):**

```
Lead Gen Verticals (6 active):
  - PlumbRight: £8k/month
  - SolarLink: £5k/month (recovering)
  - BuildConnect: £4k/month (scaling)
  - LegalMatch: £6k/month
  - MortgageMatch: £3k/month
  - CareConnect: £2k/month
  Subtotal: £28k

Ecommerce:
  - 15 active products
  - Average: £2k per product
  Subtotal: £30k

YouTube (5 channels):
  - 60 videos/month
  - Average: £2k per channel
  Subtotal: £10k

Commodity Marketplace:
  - 10 deals/month × £5k commission
  Subtotal: £50k

Client Services:
  - 10 clients × £2k average package
  Subtotal: £20k

TOTAL: £138k/month
```

**Gross Margin:** 85%+
**Net Margin (after ops, infrastructure, tools):** 70%+

---

## SCALING PLAYBOOK

**Month 1-3 (MVP):**
- Launch lead gen vertical #1 (PlumbRight)
- Launch 1 ecommerce store (winning product)
- Ops agents only (KPI, Compliance, Narrative)

**Month 4-6:**
- Scale to 3 lead gen verticals
- Launch 5 ecommerce stores (test models)
- Add YouTube agent (1 channel)
- Hire: content creators (YouTube), sourcing specialist (ecommerce)

**Month 7-12:**
- Scale to 6 lead gen verticals (£30k MRR target)
- Scale ecommerce to 15 products (£30k MRR target)
- Scale YouTube to 5 channels (£10k MRR target)
- Launch commodity marketplace (£50k MRR target)
- Target client revenue: £20k MRR (10 clients)

**Year 2:**
- Stabilize at £150k+ MRR
- Focus on profitability + unit economics
- Consider fundraising (Series A for team expansion)

---

**Status:** Ready to deploy
**First agent to launch:** Lead Generation Agent (PlumbRight vertical)
**Timeline:** Week 1 of next month
**Expected revenue (month 1):** £8k-12k (conservative)

---

Last updated: June 8, 2026
