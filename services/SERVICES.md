# PluggedIN Services Registry
# Pluggable, modular services built from consolidated skills
# Version 1.0 | June 2026

## Overview

Each service is a **composable module** that chains skills together. Clients select which services they want. Portals dynamically render service configurations.

```
Skill layer (lead-discovery, lead-enrichment, etc.)
    ↓
Service layer (Pipeline Agent = discovery + enrichment + outreach + pipeline)
    ↓
Portal layer (SEGGUINÉE, SaaS Client, Restaurant Client)
    ↓
Agent layer (AI agents running services, displaying results)
```

---

## ACQUISITION OS SERVICES

### Service: Presence Agent
**Price:** £797/month
**Description:** Voice + WhatsApp receptionist. Never misses inbound.

**Skills:**
- VAPI (voice agent, inbound calls, transfers)
- WhatsApp integration (inbound messages, auto-respond)
- Cal.com booking (schedule calls)

**What it does:**
- Answers phones 24/7 (AI receptionist)
- Responds to WhatsApp messages
- Qualifies inbound leads
- Books meetings on your calendar
- Notifies you of urgent calls

**Output to portal:**
- Inbound log (calls, messages, timestamps)
- Booking confirmations
- Lead scores from qualification
- Urgent escalations (WhatsApp to director)

**Integration points:**
- WhatsApp API
- Twilio voice
- Cal.com API
- Airtable (log conversations)

---

### Service: Pipeline Agent
**Price:** £997/month
**Description:** Lead discovery, enrichment, outreach, booking. Replaces a £3k/month BDR.

**Skills:**
- lead-discovery (Apify bulk prospecting)
- lead-enrichment (contact info + decision-maker + signals)
- lead-qualification (ICP fit scoring)
- outreach-engine (email + LinkedIn + WhatsApp sequences)
- sales-pipeline (booking, deal tracking)

**What it does:**
- Finds 50-200 leads per week from your ICP
- Enriches them: name, email, phone, decision-maker score, signals
- Qualifies fit to your ICP
- Runs multi-channel outreach sequences
- Books meetings on Cal.com
- Tracks deals in Airtable

**Output to portal:**
- Leads discovered (by source: LinkedIn, Maps, etc)
- Leads enriched (accuracy scores, signals)
- Leads qualified (hot/warm/cold split)
- Outreach metrics (open rate, click rate, response rate)
- Pipeline value (weighted by stage)
- Meetings booked (this week, next week)

**Integration points:**
- Apify API (lead discovery)
- Vibe Prospecting MCP (enrichment)
- Cal.com (booking)
- Airtable (pipeline tracking)
- Gmail/Mailgun (email sending + tracking)
- WhatsApp API (multi-channel outreach)

---

### Service: Conversion Agent
**Price:** £897/month
**Description:** Website AI chat, lead scoring, auto-booking hot leads.

**Skills:**
- lead-enrichment (visitor profiling)
- lead-qualification (real-time fit scoring)
- sales-pipeline (booking + nurture)

**What it does:**
- Chat widget on your website
- Qualifies visitors in real-time (hot/warm/cold)
- Auto-books hot leads directly to your calendar
- Sends warm leads to nurture sequence
- Escalates urgent requests via WhatsApp

**Output to portal:**
- Visitor engagement (chats, sentiment, intent)
- Lead scores (hot/warm/cold breakdown)
- Auto-booked meetings
- Conversion metrics (chat → meeting %)

**Integration points:**
- Anthropic API (chat + scoring)
- Airtable (visitor log)
- Cal.com (booking)
- WhatsApp API (escalations)

---

### Service: Lead Marketplace (custom, upcoming)
**Price:** £997/month
**Description:** Be the middleman. Find leads, sell to businesses in your niche.

**Skills:**
- lead-discovery (bulk prospecting)
- lead-enrichment (max detail for quality)
- lead-qualification (your own scoring)
- sales-pipeline (sell to your buyers, not the leads)

**What it does:**
- You identify a niche (e.g., "plumbers needing solar leads")
- Find leads (e.g., solar companies in need of quality plumbers)
- Enrich & qualify them (accuracy + decision-maker + signals)
- Sell access to your network (plumbers pay £25-50/lead)
- Scale: 50 leads/week × £40 = £2,000/week, £8,000/month pure margin

**Output to portal:**
- Leads discovered + enriched (by quality tier)
- Buyers qualified (who's buying)
- Revenue per lead (tracking margin)
- Repeat buyers (your recurring revenue)

---

## GROWTH OS SERVICES

### Service: Marketing Agent
**Price:** £1,197/month
**Description:** Competitor analysis, content creation, video ads.

**Skills:**
- competitor-intel (what are competitors doing?)
- content-asset-creator (write, design, video)
- linkedin-presence (posting, engagement)
- Creatomate (video ads for Meta/Google)

**What it does:**
- Analyzes competitor ads (Meta, Google, LinkedIn)
- Creates content (blog, social, video ads)
- Runs your LinkedIn presence
- Designs and publishes video ads
- Tracks ad performance

**Output to portal:**
- Competitor analysis (what's working for them)
- Content calendar (published + scheduled)
- Ad performance (impressions, clicks, cost)
- Engagement metrics (likes, comments, shares)

---

### Service: Customer Retention OS
**Price:** £497/month (base) + add-ons
**Description:** Loyalty stamps, churn detection, win-back campaigns.

**Skills:**
- lead-enrichment (customer profiling)
- sales-pipeline (nurture sequences)
- WhatsApp loyalty (stamps, rewards)
- signal-detection (churn risk alerts)

**What it does:**
- Sends loyalty stamps (WhatsApp)
- Detects churn risk (engagement drop)
- Runs win-back campaigns
- Manages reviews + reputation
- Tracks NPS + satisfaction

**Output to portal:**
- Active customers (engagement score)
- Churn risk (alerts + reasons)
- Win-back success rate
- Review management (responses + rating)

**Add-ons:**
- Stock Intelligence (£147/month) — monitor inventory
- Marketing Pack (£197/month) — seasonal campaigns
- Seasonal Campaigns (£297 per campaign)
- Influencer Outreach (£397/month)
- Menu Intelligence (£147/month) — optimize offerings

---

## INTELLIGENCE OS SERVICES

### Service: Intelligence Agent
**Price:** £697/month
**Description:** Competitor monitoring, market signals, weekly briefing.

**Skills:**
- competitor-intel (monitor competitors)
- signal-detection (hiring, funding, news)
- briefing (Remotion narrative video)

**What it does:**
- Monitors competitor moves
- Watches for market signals (buying intent)
- Sends weekly briefing (video or text)
- Alerts on major events

**Output to portal:**
- Competitor activity (new hires, products, ads)
- Market signals (relevant for your niche)
- Briefing archive (weekly videos)

---

### Service: Sales Intelligence
**Price:** £697/month
**Description:** Call analysis, coaching, pipeline review.

**Skills:**
- sales-pipeline (pipeline tracking)
- sales-coaching (Slack/WhatsApp reminders)
- performance-optimization (metrics + insights)

**What it does:**
- Records + transcribes calls
- Provides coaching feedback
- Reviews pipeline health
- Suggests next actions

**Output to portal:**
- Call transcripts (searchable)
- Coaching feedback
- Pipeline health score
- Performance trends

---

### Service: Data Intelligence
**Price:** £897/month
**Description:** KPI tracking, narrative reports, PowerPoint dashboards.

**Skills:**
- airtable-automation (KPI calculation)
- reporting (Remotion narrative videos)
- data-visualization (charts, dashboards)

**What it does:**
- Tracks all KPIs (revenue, pipeline, conversion)
- Generates monthly Remotion narrative videos
- Creates PowerPoint board packs
- Auto-populated dashboards

**Output to portal:**
- KPI dashboard (real-time)
- Monthly narrative video
- Board pack (PowerPoint)
- Trend analysis

---

### Service: Stock Intelligence
**Price:** £297/month
**Description:** Real-time stock monitoring, supplier alerts.

**Skills:**
- signal-detection (inventory drops)
- sales-pipeline (auto-reorder)

**What it does:**
- Monitors inventory levels
- Alerts when stock drops below threshold
- Auto-orders from suppliers
- Tracks supplier performance

**Output to portal:**
- Stock levels (by product)
- Reorder alerts
- Supplier status
- Inventory trends

---

## REVIEW REMOVAL (Standalone)

### Service: Review Removal & Reputation
**Price:** Tiered
- Single removal: £75
- Starter pack (3 removals): £175
- Protection (5 removals): £299
- Reputation Shield (unlimited): £497/month

**What it does:**
- Monitors reviews across platforms
- Flags negative reviews
- Handles removal (legal, escalation)
- Responds to reviews professionally

---

## CLIENT PACKAGES (Pre-configured bundles)

### Starter Package
**Price:** £1,297/month
**Services:** 1 module (pick one)
- Pick: Presence OR Pipeline OR Conversion

---

### Growth Package
**Price:** £2,497/month
**Services:** 3 modules (recommended combo)
**Option A (Acquisition):**
- Presence (£797)
- Pipeline (£997)
- Conversion (£897) — total £2,691 → £2,497

**Option B (Growth):**
- Pipeline (£997)
- Marketing (£1,197)
- Customer Retention (£497) — total £2,691 → £2,497

**Option C (Intelligence):**
- Pipeline (£997)
- Intelligence (£697)
- Data Intelligence (£897) — total £2,591 → £2,497

---

### Scale Package
**Price:** £4,997/month
**Services:** All 7 modules (£4,882 individual → £4,997)
- Presence (£797)
- Pipeline (£997)
- Conversion (£897)
- Marketing (£1,197)
- Intelligence (£697)
- Sales Intelligence (£697)
- Data Intelligence (£897)

---

### Empire OS (Multi-business)
**Price:** Tiered
**Starter:** £2,497/month (1 business, all modules)
**Growth:** £4,997/month (up to 3 businesses)
**Empire:** £9,997/month (up to 5 businesses)
**Conglomerate:** £20,000+/month (5+ businesses, family office)

**What you get:**
- Master dashboard (all businesses in one view)
- Chief of All Chiefs AI (synthesizes across businesses)
- Weekly portfolio briefing
- Cross-business intel (market trends, opportunities)

---

## SERVICE SCHEMA (Portal Config)

Each service config looks like:

```json
{
  "service_id": "pipeline-agent-001",
  "name": "Pipeline Agent",
  "price_monthly": 997,
  "description": "Lead discovery, enrichment, outreach, booking",
  "skills": [
    {
      "skill_id": "lead-discovery",
      "skill_name": "lead-discovery",
      "capability": "Find 50-200 leads per week"
    },
    {
      "skill_id": "lead-enrichment",
      "skill_name": "lead-enrichment",
      "capability": "Name, email, phone, decision-maker, signals"
    },
    {
      "skill_id": "lead-qualification",
      "skill_name": "lead-qualification",
      "capability": "Score fit to your ICP"
    },
    {
      "skill_id": "outreach-engine",
      "skill_name": "outreach-engine",
      "capability": "Email, LinkedIn, WhatsApp sequences"
    },
    {
      "skill_id": "sales-pipeline",
      "skill_name": "sales-pipeline",
      "capability": "Booking, deal tracking, nurture"
    }
  ],
  "integrations": [
    "apify",
    "vibe-prospecting",
    "cal.com",
    "airtable",
    "gmail",
    "whatsapp"
  ],
  "output_tables": [
    "leads_discovered",
    "leads_enriched",
    "leads_qualified",
    "outreach_log",
    "pipeline_deals"
  ],
  "dashboard_panels": [
    "leads_discovered_this_week",
    "pipeline_value_by_stage",
    "outreach_metrics",
    "meetings_booked",
    "deal_progression"
  ],
  "features": [
    "Bulk lead discovery (55+ sources)",
    "Multi-source enrichment",
    "Decision-maker scoring",
    "Activity signals (LinkedIn)",
    "Buying intent signals",
    "Multi-channel outreach",
    "Cal.com booking",
    "Airtable pipeline tracking",
    "Email open/click tracking",
    "Deal stage automation"
  ],
  "typical_results": {
    "leads_per_month": 200,
    "enrichment_cost": 50,
    "accuracy_score": 0.92,
    "decision_maker_pct": 0.75,
    "outreach_response_rate": 0.025,
    "meetings_booked_per_month": 15,
    "sales_cycle_days": 21
  }
}
```

---

## NEXT: PORTAL IMPLEMENTATION

Each client portal loads services from this registry:

```
Portal receives: selected_services = ["pipeline-agent", "presence-agent"]
    ↓
Load service configs from this registry
    ↓
Render agent cards (one per service)
    ↓
Each agent card shows:
  - Service name
  - Skills it uses
  - Key outputs
  - Real-time data from Airtable
```

No hardcoding. Everything config-driven.

---

Last updated: June 7, 2026
