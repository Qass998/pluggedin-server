---
name: client-portal
version: 1.0.0
description: Generate a bespoke agentic business intelligence portal for any SME client. Covers design system, industry templates (Legal, Restaurant, Construction, Logistics, Healthcare), advisory engine, growth checkpoints, Remotion weekly video briefings, and active agent actions per module.
triggers:
  - generate a portal
  - build a client portal
  - create a portal for
  - portal for client
  - client dashboard
  - SME portal
  - agentic portal
author: PluggedIN OS
---

# SKILL: Agentic SME Client Portal Generator
**Version:** 1.0  
**Owner:** PluggedIN OS  
**Purpose:** Generate a bespoke, agentic business intelligence portal for any SME client — one that doesn't just show data but actively analyses it, advises on financial moves, sets growth checkpoints, and triggers agents that generate real cashflow.

---

## WHAT THIS SKILL BUILDS

Not a dashboard. Not a report. An **active business advisor** that lives in the browser.

The difference between what Fathom/Syft/Spotlight do and what PluggedIN builds:

| Fathom / Syft | PluggedIN Agentic Portal |
|---|---|
| Shows financial data | Analyses data + tells owner what to do |
| Static reports | Agents that execute actions automatically |
| Variance tracking | Growth checkpoints with AI-defined targets |
| Export to PDF | Remotion video briefing delivered weekly |
| Connect your accountant | Connect your AI advisors |
| £50-200/mo SaaS | £500-2,000 setup + £797-2,991/mo retainer |

The SME owner opens their portal and sees their business — their actual numbers, their agents at work, their next move clearly stated. They don't configure anything. The agents do it.

---

## STEP 0: BEFORE YOU GENERATE A PORTAL

Read the client record from PluggedIN OS and extract:

```
CLIENT_NAME        → Business name (used in branding)
INDUSTRY           → Determines layout template (see Section 3)
MODULES_ACTIVE     → List of M1-M10 modules purchased (determines which views appear)
AIRTABLE_BASE_ID   → Source of truth for all data
AIRTABLE_TOKEN     → API key for live data reads
VAPI_ASSISTANT_ID  → For call log integration (M1)
BRAND_COLOR        → Primary colour for portal (default: #7c6fff)
REVENUE_BAND       → Annual revenue estimate (sets growth checkpoint scale)
PORTAL_PASSWORD    → Simple login password (stored hashed in localStorage)
TRIAL_START_DATE   → ISO date, triggers 14-day countdown
```

Never generate a portal without all of these. If any are missing, stop and ask.

---

## SECTION 1: DESIGN SYSTEM

### Philosophy
Dark. Premium. Focused. Inspired by DashCode's depth, DreamsPOS's data density, and Fathom's clarity of hierarchy — but darker, more opinionated, and built for action not observation.

The SME owner should feel like they have a private Bloomberg terminal for their business.

### Colour Palette

```css
:root {
  /* Backgrounds — three layers of depth */
  --bg:        #07090f;   /* Page background — deepest */
  --surface:   #0c1018;   /* Sidebar + topbar */
  --card:      #111622;   /* Card faces */
  --card2:     #161d2b;   /* Card hover / footer */
  --card3:     #1b2335;   /* Input backgrounds */

  /* Borders */
  --border:    #1e2d42;
  --border2:   #26384f;

  /* Brand accent — override with BRAND_COLOR per client */
  --accent:    #7c6fff;
  --accent2:   #a78bfa;
  --accent-glow: #7c6fff20;

  /* Semantic */
  --green:     #22c55e;
  --yellow:    #f59e0b;
  --red:       #ef4444;
  --blue:      #3b82f6;
  --cyan:      #06b6d4;

  /* Text */
  --text:      #e2eaf6;
  --text2:     #8899b4;
  --muted:     #3d4f68;
}
```

### Typography
- Font: **Inter** (Google Fonts) — weights 400, 500, 600, 700, 800
- Page title: 17px / 700 / letter-spacing -0.02em
- Card headers: 11px / 700 / UPPERCASE / letter-spacing 0.1em
- KPI values: 24–32px / 800 / letter-spacing -0.04em
- Body: 13px / 400 / line-height 1.6
- Code/mono: SF Mono or JetBrains Mono

### Core Components

**KPI Card** — always has: icon (SVG), sparkline (inline SVG, 7 data points), label, value, change badge (▲/▼ with colour)

**Insight Card** — AI-generated advisory text. Has: icon (brain/lightbulb), priority badge (HIGH/MED/LOW), headline, 2–3 sentence body, action button ("Apply this →")

**Growth Checkpoint** — milestone card. Has: checkpoint name, target metric, current value, progress ring (0–100%), status (ON TRACK / BEHIND / ACHIEVED), AI note explaining what to do to hit it

**Agent Action Card** — shows what an agent is doing. Has: agent name, last run time, status dot (green pulsing = active), last output summary, "Run Now" button, next scheduled run

**Remotion Report Card** — weekly video briefing. Has: thumbnail (gradient with week number), "Play Briefing" button, duration, key stats overlaid, download link

**Data Table** — dark rows, subtle hover, sortable columns, export button (CSV)

**Activity Feed** — right-side vertical timeline, colour-coded dots per agent, timestamp, short description, link to detail

### Layout Shell
```
┌──────────────────────────────────────────────────────┐
│  SIDEBAR (220px)  │  TOPBAR (60px)                   │
│  Logo + nav       │  Page title + actions + avatar   │
│                   ├──────────────────────────────────│
│                   │  CONTENT AREA (scrollable)        │
│                   │                                   │
│  [Agent status]   │  Main view                        │
│  [Trial timer]    │  (KPIs → Insights → Actions)      │
│  [Next milestone] │                                   │
└──────────────────────────────────────────────────────┘
```

Sidebar always shows:
- Client logo / initials
- Navigation items (only views for purchased modules)
- Live agent status indicators (green dot = running)
- 14-day trial countdown (if in trial)
- Next growth checkpoint progress

---

## SECTION 2: PORTAL VIEWS — THE FIVE PILLARS

Every portal has exactly five pillars, regardless of industry. The content of each pillar changes based on modules and industry. These map directly to what Fathom does — but with agents layered on top of every one.

### PILLAR 1 — COMMAND CENTRE (Home / Overview)
*What Fathom calls "Analysis" — but active, not passive.*

Layout: 2-column. Left = KPI grid + insight feed. Right = agent activity + next actions.

Always present:
- 5 KPI cards with sparklines (revenue, leads, calls, conversions, churn risk)
- AI Insight panel: 3 prioritised insights generated by Claude from this week's data
- Growth Checkpoint hero card: current milestone, % complete, days remaining, what to do next
- Agent Status row: all active agents, last run, next run, health indicator

The AI Insight panel is the most important element. Claude reads all Airtable data for this client, runs the advisory prompt (Section 5), and writes 3 insights ranked by financial impact. Example for a solicitors firm:

> **HIGH IMPACT** — Your Saturday call-answer rate is 23%. Competitors answer 78% of Saturday enquiries. Enabling your Presence Agent on weekends could capture an estimated 4–6 additional consultations per month at your average fee of £450. **→ Enable weekend coverage**

### PILLAR 2 — PIPELINE (Leads & Revenue)
*Requires M1, M2, or M7. Skip if none active.*

Layout: Kanban board (Prospect → Qualified → Proposal → Won → Lost) + conversion funnel chart + lead source breakdown.

Data sources:
- M2 Pipeline Agent → Leads table in Airtable
- M1 Presence Agent → VAPI call log, booking data
- M7 Conversion Agent → Website visitor score, hot leads flagged

Active agent actions visible here:
- "Pipeline Agent scanned 47 new prospects this week — 3 match your ICP" (with "Review leads →" button)
- "Conversion Agent flagged 2 hot leads who visited your pricing page 3+ times" (with "Call now →" button)

### PILLAR 3 — INTELLIGENCE (Competitor & Market)
*Requires M3, M4, or M5. Skip if none active.*

Layout: Competitor comparison table + market movement feed + content calendar (if M3) + sales coaching notes (if M5).

Data sources:
- M4 Intelligence Agent → Competitor tracking table
- M3 Marketing Agent → Content calendar, campaign performance
- M5 Sales Intelligence → Call analysis, coaching flags

Always includes a "Market Position" card: where this business sits vs. competitors on 4 dimensions (price, reviews, online presence, response time). Updated weekly by agents.

### PILLAR 4 — FINANCIALS (Cash & Growth)
*Always present. Pulls from M6 Data Intelligence if active, otherwise uses manual inputs.*

Layout: Three-way cashflow model (revenue / costs / net) + 6-month forecast + variance table (actual vs. last month, actual vs. target) + financial recommendations panel.

This is where Remotion lives. The weekly Remotion video briefing is embedded here as a card.

Financial advisory rules (hardcoded into the advisory prompt):
- Flag if monthly revenue is below target by >10%
- Flag if churn rate exceeds 5%
- Flag if cost-per-lead exceeds 20% of average client value
- Flag if outstanding invoices exceed 30 days
- Flag if Saturday/evening coverage gap exists (M1 data)

### PILLAR 5 — OPERATIONS (Stock, Reviews, Retention)
*Requires M9 or M10. Skip if neither active.*

Layout: Stock alert table (items below threshold, with "Approve order →" buttons) + customer health scores + review monitoring feed + win-back campaign status.

Data sources:
- M10 Stock Intelligence → Stock table, supplier contacts
- M9 Customer Retention → Contact health scores, churn risk, WhatsApp campaign status

Active agent actions:
- "3 stock items are below threshold — supplier orders ready to send" (with "Send orders →")
- "Churn risk HIGH for 4 customers — win-back messages drafted" (with "Send now →")

---

## SECTION 3: INDUSTRY TEMPLATES

### 3A — LEGAL (Solicitors, Law Firms)
**ICP:** 3–20 fee earners, £500K–£5M revenue, no CRM or call tracking

**Primary pain:** Missing enquiries out of hours, no lead pipeline visibility, no way to measure fee earner performance

**KPI labels:** Enquiries This Week / Consultations Booked / Conversion Rate / Avg Fee / Outstanding Invoices

**Accent colour:** Deep navy `#1e3a5f` with gold `#d4a853`

**Priority modules:** M1 (AI receptionist), M2 (lead pipeline), M4 (competitor tracking), M6 (board pack)

**Growth checkpoint targets (by revenue band):**
- Under £1M ARR → Target: 15 qualified enquiries/month
- £1M–3M ARR → Target: 40 consultations/month, 65% conversion
- Over £3M ARR → Target: 3 new fee earners, referral pipeline active

**Unique views:**
- Matter pipeline (like deal pipeline but for legal cases)
- Fee earner performance table (calls handled, conversion rate, avg fee)
- Regulatory deadline tracker (not agent-driven, manual input)

**Advisory prompt additions:**
> "Analyse enquiry-to-consultation conversion rate. If below 50%, flag it as a missed revenue opportunity and calculate the monthly value of closing the gap. Check if the solicitors have weekend VAPI coverage — this is the single highest-ROI change for most law firms."

---

### 3B — RESTAURANT / HOSPITALITY
**ICP:** Single-site or small chain, £300K–£2M revenue, competing with delivery apps, struggling with retention

**Primary pain:** No visibility on customer return rates, reviews affecting new bookings, no system for busy periods

**KPI labels:** Covers This Week / Avg Spend / Return Customer Rate / Review Score / Table Utilisation %

**Accent colour:** Warm amber `#d97706` with deep charcoal `#1c1917`

**Priority modules:** M1 (reservations + enquiries), M9 (customer retention), M3 (marketing + reviews)

**Growth checkpoint targets:**
- Under £500K ARR → Target: 30% return customer rate, 4.5★ average review
- £500K–£1M ARR → Target: 60% table utilisation Friday–Sunday, email list of 500+
- Over £1M ARR → Target: loyalty programme active, second site pipeline started

**Unique views:**
- Cover booking calendar (week view, utilisation by service)
- Review monitoring feed (Google, TripAdvisor, OpenTable aggregated)
- Menu performance table (which dishes drive repeat visits)
- Win-back campaign tracker (lapsed customers, last visit >60 days)

**Advisory prompt additions:**
> "Calculate Saturday utilisation. If below 85%, calculate revenue loss at avg spend × empty covers × 52 weeks. Identify which review platform has lowest score and recommend a targeted response campaign. Check if loyalty/return rate has improved since WhatsApp campaign launched."

---

### 3C — CONSTRUCTION / TRADES
**ICP:** 5–50 employees, £500K–£5M revenue, project-based, quoting manually, no pipeline visibility

**Primary pain:** No way to track which quotes convert, losing leads who call and get no answer, no material/stock visibility

**KPI labels:** Active Projects / Quotes Sent / Quote-to-Win Rate / Avg Project Value / Material Costs This Month

**Accent colour:** Slate `#334155` with orange `#f97316`

**Priority modules:** M1 (enquiry handling), M2 (quote pipeline), M10 (stock/materials), M4 (competitor)

**Growth checkpoint targets:**
- Under £1M ARR → Target: 40% quote-to-win rate, 20 enquiries/month
- £1M–3M ARR → Target: £150K avg project value, 3 recurring commercial clients
- Over £3M ARR → Target: framework contracts signed, materials buying group

**Unique views:**
- Project Kanban (Enquiry → Surveyed → Quoted → Won → In Progress → Complete → Invoiced)
- Quote tracker with conversion analytics
- Material stock dashboard with threshold alerts and supplier order buttons
- Subcontractor availability calendar

**Advisory prompt additions:**
> "Analyse quote-to-win ratio. If below 35%, investigate whether pricing or response speed is the issue. Check if any enquiries went unanswered (VAPI missed calls). Calculate the revenue impact of improving win rate by 10 percentage points. Identify if any materials are consistently running low — recommend automatic reorder thresholds."

---

### 3D — LOGISTICS / TRANSPORT
**ICP:** 5–30 vehicles, £750K–£5M revenue, margin-thin, running on WhatsApp and spreadsheets

**Primary pain:** No job profitability visibility, drivers idle between jobs, customer complaints about ETAs

**KPI labels:** Jobs Completed / On-Time Rate / Cost Per Job / Fleet Utilisation % / Outstanding Invoices

**Accent colour:** Deep teal `#0f766e` with white

**Priority modules:** M1 (inbound bookings), M2 (job pipeline), M6 (financial data), M10 (fleet/asset tracking)

**Growth checkpoint targets:**
- Under £1M ARR → Target: 85% on-time rate, 70% fleet utilisation
- £1M–3M ARR → Target: 3 anchor contracts, automated invoicing active
- Over £3M ARR → Target: dedicated account portal for top 5 clients

**Unique views:**
- Live job board (map + list, status per vehicle)
- Driver performance table (jobs/day, on-time %, customer rating)
- Invoice aging report with automated chaser status
- Profitability by job type / route / client

---

### 3E — HEALTHCARE / CARE
**ICP:** GP practices, dental, physio, care homes — 5–50 staff, regulated, capacity-constrained

**Primary pain:** Missed appointments costing revenue, no CRM for patient communications, referral pipeline invisible

**KPI labels:** Appointments This Week / DNA Rate / Avg Revenue Per Appointment / Referrals Received / Bed/Chair Utilisation

**Accent colour:** Clean indigo `#4f46e5` with light sage

**Priority modules:** M1 (appointment booking + enquiries), M9 (patient retention + recall), M4 (competitor mapping)

**Growth checkpoint targets:**
- Under £500K ARR → Target: DNA rate below 8%, 90% capacity utilisation
- £500K–£2M ARR → Target: automated recall programme active, referral network mapped
- Over £2M ARR → Target: additional practitioner hired, satellite location scoped

**Unique views:**
- Appointment calendar with utilisation heatmap
- DNA (Did Not Attend) tracker with automated recall campaign status
- Referral source map (which GPs/businesses send patients)
- Compliance calendar (CQC, registration renewals — manual input)

---

## SECTION 4: GROWTH CHECKPOINT SYSTEM

Every client has exactly **three active checkpoints** at any time. These are set during onboarding and updated quarterly by the advisory agent.

### Checkpoint Structure

```
CHECKPOINT {
  name:        "Hit 20 Qualified Leads/Month"
  metric:      leads_qualified_this_month
  current:     13
  target:      20
  deadline:    "2025-08-01"
  status:      "BEHIND"  // ON TRACK | BEHIND | ACHIEVED
  gap:         7
  agent:       M2 Pipeline Agent
  ai_note:     "At current rate you'll hit 17 by August. 
                To close the gap: expand scrape to 3 more 
                postcodes and increase outreach from 20 to 
                35 contacts/week. This is a 2-hour config 
                change — click below to do it."
  action_btn:  "Expand pipeline coverage →"
}
```

### Checkpoint Progression
When a checkpoint is ACHIEVED, the agent automatically:
1. Marks it complete with a celebration state in the portal
2. Generates the next logical checkpoint (one level up)
3. Sends a Remotion highlight clip to the client
4. Logs it in the PluggedIN OS agency view

### Default Checkpoint Ladders by Industry

**Legal:**
- L1: 10 qualified enquiries/month → L2: 25 enquiries → L3: 40 enquiries + 65% conversion

**Restaurant:**
- L1: 4.0★ avg review + 25% return rate → L2: 4.5★ + 35% return → L3: 60% utilisation + loyalty programme

**Construction:**
- L1: 35% quote-to-win + 15 enquiries → L2: 45% win rate + £100K avg project → L3: first framework contract

**Logistics:**
- L1: 80% on-time + 60% fleet utilisation → L2: 3 anchor clients + auto-invoicing → L3: fleet expansion

**Healthcare:**
- L1: DNA rate below 10% → L2: 90% utilisation + recall programme → L3: second practitioner onboarded

---

## SECTION 5: ADVISORY ENGINE

This is Claude's role in the portal. Every time the portal loads (or the SME clicks "Refresh Insights"), Claude reads the Airtable data and runs the advisory prompt.

### Master Advisory Prompt

```
You are the AI Business Advisor for [CLIENT_NAME], a [INDUSTRY] business based in [LOCATION].

You have access to the following live data:
[INJECT AIRTABLE DATA SUMMARY — last 30 days]

Your job is to produce exactly 3 insights, ranked by financial impact (highest first).

Each insight must follow this structure:
- PRIORITY: HIGH / MEDIUM / LOW
- HEADLINE: One sentence, specific, quantified if possible
- BODY: 2–3 sentences explaining the finding and the opportunity
- ACTION: One specific action the business owner can take today
- ESTIMATED IMPACT: Revenue or cost figure if calculable

Rules:
- Never be vague. "You should improve conversion" is banned. 
  "Your conversion rate is 31% vs. industry average of 48% — 
  closing that gap on your current lead volume would add £3,200/month" is correct.
- Always connect insights to money. Every observation must trace to revenue gained or cost saved.
- Prioritise actions the agents can execute automatically over manual tasks.
- If an agent can solve the problem — say so and link the "Run now" button.
- Reference specific data points. "17 of your 22 enquiries this month came on weekdays before 5pm" not "most enquiries come during business hours."

Output format: JSON array of 3 insight objects.
```

### Financial Ratio Triggers

These trigger automatic HIGH PRIORITY insights regardless of other data:

| Condition | Insight Type |
|---|---|
| Conversion rate drops >5% week-on-week | Revenue leak alert |
| 3+ unanswered calls in past 7 days | Missed revenue alert |
| Invoice outstanding >45 days | Cash flow alert |
| Review score drops below 4.0 | Reputation alert |
| Stock item at 0 or below threshold | Operations alert |
| Churn rate exceeds 5%/month | Retention alert |
| Lead volume drops >20% vs. 4-week average | Pipeline alert |
| Quote-to-win drops below 30% | Sales efficiency alert |

---

## SECTION 6: REMOTION WEEKLY BRIEFING

Remotion is a React library that renders animated video from code. Every Friday at 08:00, the Remotion agent generates a 90-second video briefing for the SME client.

### Video Structure (90 seconds)

**Seconds 0–10: Identity card**
- Client name + logo
- "Your Week in Review — [Date]"
- Animated gradient background in brand colour

**Seconds 10–30: Three headline numbers**
- Three KPIs animate in with count-up effect
- Each has a delta arrow (▲ or ▼) and % change
- Sparkline animates alongside each number

**Seconds 30–55: Top insight**
- The #1 AI insight from this week
- Key data point animates in
- Estimated financial impact shown
- Recommended action stated

**Seconds 55–75: Growth checkpoint update**
- Active checkpoint shown as animated progress ring
- "You're X% of the way to [milestone]"
- Days remaining shown
- What the agent did this week to move it forward

**Seconds 75–90: Next week preview**
- Three agent actions scheduled for next week
- "Your agents are working. Here's what's happening."
- PluggedIN logo + sign-off

### Remotion Component Structure

```
/remotion
  /compositions
    WeeklyBriefing.tsx    ← master composition
    IdentityCard.tsx
    KPIFrame.tsx
    InsightFrame.tsx
    CheckpointFrame.tsx
    AgentPreview.tsx
  /utils
    countUp.ts
    sparkline.ts
    formatCurrency.ts
  remotion.config.ts
```

### Generation Command

```bash
# Run by the scheduler every Friday 07:45
node remotion/generate.js \
  --client=CLIENT_ID \
  --airtable-base=BASE_ID \
  --output=outputs/briefings/CLIENT_ID_WEEK_N.mp4
```

### Integration in Portal

The Remotion video embeds directly in Pillar 4 (Financials) as a card:

```html
<div class="remotion-card">
  <div class="remotion-thumb">
    <video src="briefings/week_N.mp4" poster="thumb.jpg"></video>
    <div class="remotion-overlay">
      <span>Week N Briefing · 1m 30s</span>
      <button>▶ Play</button>
    </div>
  </div>
  <div class="remotion-stats">
    <span>Revenue: £X (▲Y%)</span>
    <span>Leads: N</span>
    <span>Top action: [X]</span>
  </div>
</div>
```

---

## SECTION 7: ACTIVE AGENT ACTIONS PER MODULE

This is what separates PluggedIN from every reporting tool. Agents don't just show — they **do**.

### M1 — Presence Agent
**Active actions:**
- Answers inbound calls 24/7 (VAPI)
- Books appointments into calendar automatically
- Sends confirmation SMS to caller
- Escalates urgent calls to owner's mobile
- Logs every call: duration, outcome, follow-up needed

**Portal shows:** Call log table, missed call alerts, booking rate, coverage heatmap (hour-by-hour)

**Revenue it generates:** Every answered call that books = avg client value × conversion rate. Show this in portal as "Calls answered this month = estimated £X captured"

---

### M2 — Pipeline Agent
**Active actions:**
- Scrapes target postcodes/sectors for new prospects weekly
- Scores each prospect against ICP
- Drafts personalised outreach emails (not sends — awaits approval)
- Updates pipeline stages based on email responses
- Flags any prospect who opened email 3+ times as "hot"

**Portal shows:** Kanban pipeline, prospect table with ICP scores, outreach queue (approve/edit/skip), hot lead alerts

---

### M3 — Marketing Agent
**Active actions:**
- Monitors competitor Google reviews daily
- Scrapes competitor website for price/offer changes
- Generates weekly content calendar (5 posts, platform-specific)
- Creates content using Creatomate (images + captions)
- Posts approved content to social (awaits one-click approval)

**Portal shows:** Competitor change feed, content calendar, scheduled posts, engagement metrics

---

### M4 — Intelligence Agent
**Active actions:**
- Monitors top 5 competitors weekly (reviews, website, ads)
- Generates competitive positioning report
- Flags any competitor price changes or new services
- Maps competitor online presence score vs. client score

**Portal shows:** Competitor comparison table, market position radar chart, weekly change log

---

### M5 — Sales Intelligence
**Active actions:**
- Analyses VAPI call transcripts for objection patterns
- Flags calls where prospects said "too expensive" / "need to think"
- Generates coaching notes per call
- Identifies highest-converting call openers from transcript data

**Portal shows:** Call analysis table, objection tracker, coaching notes feed, conversion correlation chart

---

### M6 — Data Intelligence
**Active actions:**
- Pulls financial data from Airtable weekly
- Generates board pack (P&L, cashflow, KPI summary)
- Runs three-way cashflow forecast (12 months)
- Flags any ratios outside healthy range
- Produces Remotion video briefing (triggers remotion/generate.js)

**Portal shows:** Financial pillar (full Pillar 4), board pack download, cashflow chart, KPI scorecards

---

### M7 — Conversion Agent
**Active actions:**
- Monitors website visitor behaviour (integration with analytics)
- Scores each visitor by engagement (pages viewed, time on pricing)
- Flags visitors who hit pricing page 3+ times
- Triggers VAPI callback offer to high-score visitors (if configured)

**Portal shows:** Visitor heat score table, hot leads flagged, conversion funnel, A/B insight

---

### M8 — Lead Marketplace
**Active actions:**
- Runs outbound VAPI campaign to purchased lead lists
- Qualifies leads by conversation (budget, timeline, authority)
- Books qualified prospects directly into calendar
- Reports cost-per-qualified-lead and ROI

**Portal shows:** Outbound campaign table, qualified lead log, CPL tracker, ROI summary

---

### M9 — Customer Retention OS
**Active actions:**
- Scores all customers by churn risk (recency, frequency, spend)
- Drafts win-back WhatsApp messages for at-risk customers
- Monitors Google/TripAdvisor/sector reviews daily
- Sends review request SMS to recent customers (post-service)
- Flags any 1–2★ reviews for immediate owner response

**Portal shows:** Customer health table, churn risk heatmap, win-back campaign status, review monitoring feed, NPS tracker

---

### M10 — Stock Intelligence
**Active actions:**
- Monitors stock levels against defined thresholds daily
- Generates supplier order when threshold breached
- Sends WhatsApp/email to supplier with order details (awaits approval)
- Logs all stock movements and supplier lead times
- Forecasts stock needs based on seasonal demand patterns

**Portal shows:** Stock table (green/yellow/red status), threshold settings, pending orders (approve/edit), supplier contact list, demand forecast chart

---

### M11 — Reviews & Reputation Agent
**The dedicated reputation management engine.** M9 watches for new reviews. M11 actively improves them.

**Platforms covered:** Google Business Profile · Trustpilot · TripAdvisor · Facebook Reviews / Yelp

**Active actions:**

*Generation (getting more reviews):*
- Sends personalised review request via SMS and WhatsApp 2–4 hours post-service (timing optimised by industry: restaurants get same-day, trades get next morning)
- Runs re-request sequence for non-responders at 7 days (one follow-up only — never spam)
- Identifies your top 20% happiest customers (highest spend, no complaints, repeat visits) and runs a VIP review campaign monthly
- Filters — only contacts customers who rated their experience ≥8/10 internally (avoids accidentally soliciting negative reviews)

*Response (handling existing reviews):*
- Drafts a personalised response to every new review within 2 hours of it appearing — awaits owner's one-click approval
- Responses reference the specific reviewer's experience where possible (service type, date, staff name if known)
- 1–2★ reviews get a recovery draft: acknowledges issue, offers resolution, moves conversation offline — never defensive, always brand-safe
- Flags reviews that likely violate platform terms (fake, competitor sabotage, wrong business) with evidence and a pre-written dispute submission

*Intelligence (understanding your reputation):*
- Tracks review velocity (reviews per week) — alerts if it drops below baseline for 14 days
- Sentiment analysis on all reviews: top 5 compliment themes, top 5 complaint themes, updated weekly
- Competitor review benchmarking: monitors top 3 local competitors' scores and velocity — alerts when a competitor overtakes you or gets a surge of new reviews
- Identifies operational patterns in 1–3★ reviews (e.g. "3 complaints mention slow service on Saturdays" → flags to CEO Agent as operational issue, not just a reputation issue)

*Recovery (fixing a damaged score):*
- If score drops below 4.0 on any platform: activates a 30-day recovery plan — increases review request frequency, pauses any outreach that's non-urgent, escalates to CEO Agent as Priority 1
- Generates a weekly reputation health report: score by platform, new reviews, response rate, velocity vs. competitors

**Platform-specific nuances:**

| Platform | Request Method | Response Time Target | Dispute Support |
|---|---|---|---|
| Google Business | SMS + WhatsApp | < 2 hours | Yes — flags to Google My Business |
| Trustpilot | Email + WhatsApp | < 4 hours | Yes — TrustPilot dispute form pre-filled |
| TripAdvisor | Email | < 6 hours | Yes — management response only |
| Facebook / Yelp | WhatsApp | < 4 hours | Basic — flags to owner |

**Portal shows:**
- Reputation dashboard: score by platform (4 gauge rings), trend chart (90 days), velocity graph
- Review feed: all new reviews across platforms, sorted by urgency (1★ first), with "Approve response →" button per review
- Sentiment map: word cloud of top complaint and compliment themes
- Competitor comparison table: your score vs. top 3 rivals, updated weekly
- Review request pipeline: who was contacted, when, whether they responded
- Recovery plan tracker (shown when score < 4.0 on any platform): progress, actions taken, days remaining

**Revenue it generates:** Show in portal as: *"Reviews requested this month: N. Estimated new reviews generated: N. Score change: +0.X. Estimated new customers attributed to improved score: N × avg transaction value = £X"*

**Does NOT overlap with M9 because:**
- M9 targets at-risk/lapsed customers for retention
- M11 targets recent happy customers to convert experience into public proof
- M9 sends win-back offers; M11 sends review requests — different message, different list, different goal

---

## SECTION 8: LOGIN SYSTEM

Simple, stateless, client-side auth. No backend required.

### Login Page Design
Full-screen dark background with brand colour gradient glow. Centred card (400px wide). Client logo at top. Single password field. "Access your portal →" button.

```javascript
// Portal login — stored in config block at top of portal.html
const PORTAL_CONFIG = {
  clientName:    "Harland Construction",
  industry:      "construction",
  brandColor:    "#f97316",
  password:      "hc2025",      // plaintext for simplicity (upgrade to SHA-256 hash)
  trialStart:    "2025-05-01",
  trialDays:     14,
  modules:       [1, 2, 10],
  airtableBase:  "appXXXXXXXX",
  airtableToken: "patXXXXXXXX",
};

function login(attempt) {
  if (attempt === PORTAL_CONFIG.password) {
    sessionStorage.setItem('pluggedin_auth', '1');
    showPortal();
  } else {
    showError("Incorrect password");
  }
}
```

### Trial Countdown
Displayed in sidebar as a countdown card. If trial expired (>14 days), portal shows an upgrade prompt instead of data — with a "Book a call" button linking to Calendly.

```javascript
function trialStatus() {
  const start = new Date(PORTAL_CONFIG.trialStart);
  const now = new Date();
  const daysUsed = Math.floor((now - start) / 86400000);
  const daysLeft = PORTAL_CONFIG.trialDays - daysUsed;
  return { daysLeft, expired: daysLeft <= 0 };
}
```

---

## SECTION 9: PORTAL GENERATION PROCESS

When Claude is asked to generate a portal for a client, follow these steps in order.

### Step 1 — Read client config
Pull CLIENT_NAME, INDUSTRY, MODULES_ACTIVE, AIRTABLE_BASE_ID, BRAND_COLOR, REVENUE_BAND from the PluggedIN OS client record.

### Step 2 — Select industry template
Match INDUSTRY to Section 3 template. Load the correct: KPI labels, accent colours, growth checkpoint ladder, unique views, advisory prompt additions.

### Step 3 — Filter views by modules
Only include pillar views for modules the client has purchased. If M1+M2 but not M3/M4/M5 → show Pillars 1, 2, and 4 only.

### Step 4 — Set growth checkpoints
Based on REVENUE_BAND and INDUSTRY, select the correct checkpoint level from Section 4's ladder. Pre-populate the three checkpoints with the right targets.

### Step 5 — Write the portal file
Generate a single self-contained `portal.html` file that includes:
- All CSS (Section 1 design system, client brand colour override)
- PORTAL_CONFIG block (Section 8)
- Login page HTML
- All selected pillar views as JS-rendered HTML
- Airtable API fetch functions (reads live data on load)
- Advisory insight fetch (calls Claude API or uses cached weekly output)
- Remotion video card (links to generated mp4 if exists)
- Growth checkpoint cards
- Agent action cards with API endpoint hooks

### Step 6 — Name and save
Save as: `outputs/portals/[client_id]/portal.html`  
Also save a config snapshot: `outputs/portals/[client_id]/config.json`

### Step 7 — Register in PluggedIN OS
Add portal URL and password to the client record in PluggedIN OS so it appears on the business card.

---

## SECTION 10: PRICING THIS AS A PRODUCT

When pitching to an SME prospect, present it as their **Business Intelligence Platform** — not as "a dashboard."

### Package Names & Prices

| Package | Modules | Setup | Monthly | Pitch Line |
|---|---|---|---|---|
| **Foundation** | M1 | £997 | £797 | "Your AI receptionist + booking system, never miss an enquiry again" |
| **Growth Engine** | M1 + M2 + M9 | £2,497 | £2,091 | "AI handles your calls, builds your pipeline, and keeps your customers" |
| **Intelligence Suite** | M1 + M4 + M6 | £1,997 | £2,291 | "Know your numbers, know your competitors, know your next move" |
| **Reputation Builder** | M11 | £997 | £597 | "More 5-star reviews, every week, on autopilot — across Google, Trustpilot, TripAdvisor and Facebook" |
| **Full Stack** | All 11 | £5,497 | £8,567 | "Your entire business, automated and advised" |

Setup fee includes: portal design + configuration + Airtable setup + agent deployment + onboarding call.

**M11 add-on pricing (bolt-on to any package):** £497 setup · £597/month — making it the easiest upsell on any existing client call. Every business cares about reviews. Every business owner has been burned by a bad one.

### The Demo Script
1. Pull up the demo portal (pre-loaded with their industry, their postcode's competitors, sample data)
2. Show the Command Centre with 3 AI insights (pre-generated for their industry's common pain points)
3. Show the Growth Checkpoint — "This is your first 90-day target. The agents are already set up to hit it."
4. Play a sample Remotion briefing — "Every Friday morning, this lands in your inbox."
5. Show one agent taking action live — run M2 pipeline scrape for their postcode
6. Close: "14-day trial, no setup fee during trial. By day 14 you'll have live data in here. After that it's £[X]/month."

---

## WHAT TO DO WHEN GENERATING A PORTAL

1. Read this entire SKILL.md before writing a single line of HTML
2. Ask for all values in the STEP 0 checklist if any are missing
3. Follow Section 9 steps in strict order
4. Use the Section 1 design system exactly — do not improvise colours or typography
5. Include only the views for purchased modules
6. Pre-populate growth checkpoints using Section 4 ladders
7. Write the advisory prompt using Section 5's master template
8. Make every agent action card link to a real API endpoint on PluggedIN OS
9. Output a single `portal.html` file — self-contained, no dependencies except Google Fonts CDN
10. Test: open the file in browser, log in, confirm all views render, confirm Airtable fetch works

The portal is the product. Make it feel like the SME owner has a private advisor who already knows their business inside out.

---

## SECTION 11: CEO AGENT — THE BRAIN BEHIND EVERY PORTAL

Each client portal has its own **CEO Agent** — a persistent AI orchestrator that coordinates all M1–M10 module agents, synthesises their outputs, and acts as the client's on-call business advisor. The CEO Agent is not a chatbot. It is an autonomous decision-maker that runs daily, reports upward, and surfaces its work inside the portal.

---

### 11.1 — PERSONA

```
You are the CEO Agent for [CLIENT_NAME].

Your role is to run the business intelligence operations for this 
[INDUSTRY] business and advise the owner on their highest-leverage 
moves today.

You coordinate [MODULES_ACTIVE] agents. You read their outputs daily. 
You do not manage people — you manage data, priorities, and timing.

Your personality: Direct. Specific. No platitudes. You talk like a 
Chief Operating Officer who knows this business inside out and is 
giving a 5-minute briefing to the owner before they walk into a 
board meeting.

Never say: "It looks like...", "You might want to...", "Consider..."
Always say: "Revenue is down 11% WoW — the gap is Wednesday evenings. 
Here's what to do." or "3 quotes went unanswered this week. That's 
£12,400 in pipeline risk. Here's the fix."
```

---

### 11.2 — DECISION LOOP

The CEO Agent runs on this loop — triggered daily by the scheduler:

```
1. COLLECT    → Pull all module agent outputs from Airtable (last 24h)
2. SCORE      → Rank all findings by financial impact (revenue risk or upside)
3. PRIORITISE → Select top 3 actions for the business owner today
4. ADVISE     → Write one advisory insight per action (specific, quantified)
5. DECIDE     → Check if any agent action can be triggered automatically
                 (e.g. a win-back message is drafted → flag for 1-click approval)
6. CHECKPOINT → Update growth checkpoint progress (has anything moved?)
7. REPORT UP  → Send report_up() summary to the Master CEO Agent
8. BRIEF      → Write the weekly briefing payload for Remotion (Fridays only)
```

Each step maps directly to a method in `core/ceo_agent.py`.

---

### 11.3 — CEO AGENT DECISION PROMPT TEMPLATE

Used in `CEOAgent._synthesise()` and the Ask Advisor feature:

```
SYSTEM:
You are the CEO Agent for {client_name}, a {industry} business.

You have access to the following data from the past 7 days:
{airtable_data_summary}

Active modules: {modules_active}
Current checkpoints:
{checkpoints}

MODULE AGENT REPORTS:
{agent_reports}

RULES:
- Every insight must trace to a specific monetary figure (revenue gained, revenue at risk, cost saved)
- Every insight must name the specific agent that can act on it
- Every recommendation must be executable today — not "over the next quarter"
- Never repeat last week's insight unless the underlying condition has worsened
- If a checkpoint moved backwards, this is always Priority 1

OUTPUT: A structured JSON briefing (see format below).

USER:
{prompt}
```

**JSON briefing format** (for `weekly_briefing()` and `report_up()`):

```json
{
  "client_id": "...",
  "client_name": "...",
  "industry": "...",
  "week_ending": "YYYY-MM-DD",
  "health_score": 0,
  "one_line_status": "Short status for Master CEO",
  "top_insight": {
    "priority": "HIGH",
    "headline": "...",
    "body": "...",
    "action": "...",
    "estimated_impact": "£X"
  },
  "priorities": [
    { "rank": 1, "action": "...", "agent": "M2", "impact": "£X" },
    { "rank": 2, "action": "...", "agent": "M1", "impact": "£X" },
    { "rank": 3, "action": "...", "agent": "M9", "impact": "£X" }
  ],
  "checkpoint_update": {
    "name": "...",
    "current": 0,
    "target": 0,
    "status": "ON TRACK | BEHIND | ACHIEVED"
  },
  "agents_idle": ["M3", "M5"],
  "needs_attention": true,
  "high_priority_actions": ["...", "..."]
}
```

---

### 11.4 — ASK YOUR ADVISOR

Every portal includes an **Ask your advisor** chat input that talks directly to the CEO Agent. This is the primary human-in-the-loop interface for the SME owner.

**Placement:** Bottom-right floating button in the portal. Opens a modal chat overlay.

**Behaviour:**
1. Owner types a question in natural language
2. Portal sends `POST /clients/{client_id}/ask` with the question
3. Server calls `CEOAgent(tenant).ask(question)` which:
   - Injects the current Airtable data summary into context
   - Runs the decision prompt with the question appended
   - Returns a specific, data-grounded answer
4. Response renders in the chat overlay with a "Take action →" button if applicable

**UI code (embed inside portal.html):**

```html
<!-- Ask Advisor floating button -->
<button class="ask-fab" onclick="openAsk('${CLIENT_ID}','${CLIENT_NAME}')">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
  </svg>
  Ask your advisor
</button>

<!-- Ask Advisor modal -->
<div id="ask-overlay" class="ask-overlay" onclick="closeAsk(event)" style="display:none">
  <div class="ask-modal" onclick="event.stopPropagation()">
    <div class="ask-header">
      <div class="ask-header-left">
        <div class="ceo-pulse active"></div>
        <div>
          <div class="ask-title">CEO Agent</div>
          <div class="ask-sub">${CLIENT_NAME} · Active</div>
        </div>
      </div>
      <button class="ask-close" onclick="document.getElementById('ask-overlay').style.display='none'">✕</button>
    </div>
    <div class="ask-messages" id="ask-messages">
      <div class="ask-msg advisor">
        I've reviewed your data. Ask me anything about your business —
        revenue, pipeline, agents, or your next move.
      </div>
    </div>
    <div class="ask-input-row">
      <input id="ask-input" class="ask-input" type="text"
             placeholder="e.g. Why is revenue down this week?"
             onkeydown="if(event.key==='Enter') sendAsk()"/>
      <button class="ask-send" onclick="sendAsk()">→</button>
    </div>
  </div>
</div>
```

**CSS for Ask Advisor:**

```css
.ask-fab {
  position: fixed; bottom: 28px; right: 28px;
  background: var(--accent); color: #fff; border: none;
  padding: 12px 20px; border-radius: 100px;
  font: 600 13px Inter; cursor: pointer; z-index: 100;
  display: flex; align-items: center; gap: 8px;
  box-shadow: 0 4px 20px #7c6fff44;
  transition: transform 0.2s, box-shadow 0.2s;
}
.ask-fab:hover { transform: translateY(-2px); box-shadow: 0 8px 32px #7c6fff66; }
.ask-fab svg { width:16px; height:16px; stroke:#fff; }

.ask-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.6);
  backdrop-filter: blur(4px); z-index: 200;
  display: flex; align-items: flex-end; justify-content: flex-end;
  padding: 28px;
}
.ask-modal {
  background: var(--card); border: 1px solid var(--border2);
  border-radius: 16px; width: 420px; max-height: 560px;
  display: flex; flex-direction: column;
  box-shadow: 0 24px 80px rgba(0,0,0,0.6);
}
.ask-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px; border-bottom: 1px solid var(--border);
}
.ask-header-left { display: flex; align-items: center; gap: 12px; }
.ask-title { font: 600 14px Inter; color: var(--text); }
.ask-sub { font: 400 11px Inter; color: var(--text2); }
.ask-close { background: none; border: none; color: var(--text2); cursor: pointer; font-size: 16px; }

.ask-messages {
  flex: 1; overflow-y: auto; padding: 16px 20px;
  display: flex; flex-direction: column; gap: 10px;
}
.ask-msg {
  padding: 10px 14px; border-radius: 12px;
  font: 400 13px/1.55 Inter; max-width: 90%;
}
.ask-msg.user {
  background: var(--accent-glow); color: var(--accent2);
  align-self: flex-end; border: 1px solid #7c6fff33;
}
.ask-msg.advisor {
  background: var(--card2); color: var(--text2); align-self: flex-start;
}
.ask-msg.advisor strong { color: var(--text); }

.ask-input-row {
  display: flex; gap: 8px; padding: 14px 20px;
  border-top: 1px solid var(--border);
}
.ask-input {
  flex: 1; background: var(--card3); border: 1px solid var(--border2);
  border-radius: 8px; padding: 10px 14px;
  font: 400 13px Inter; color: var(--text); outline: none;
}
.ask-input:focus { border-color: var(--accent); }
.ask-send {
  background: var(--accent); color: #fff; border: none;
  width: 40px; border-radius: 8px; cursor: pointer; font-size: 16px;
  transition: background 0.2s;
}
.ask-send:hover { background: var(--accent2); }

.ceo-pulse {
  width: 8px; height: 8px; border-radius: 50%; background: var(--muted);
}
.ceo-pulse.active {
  background: var(--green);
  box-shadow: 0 0 6px #22c55e66;
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
```

---

### 11.5 — CEO AGENT CARD IN THE PORTAL

Every portal's **Command Centre pillar** (Pillar 1 / Home view) includes a CEO Agent card at the top of the page — before the KPI grid. This is the highest-priority real estate in the portal.

```
┌─────────────────────────────────────────────────────────────────┐
│  ● CEO Agent — Active                    [Run brief now]        │
│                                                                  │
│  "Your highest-impact move today: Enable weekend VAPI coverage.  │
│   Last Saturday, 6 calls went unanswered at a conversion rate   │
│   of 42%. That's an estimated £1,134 in missed revenue."        │
│                                                                  │
│  Priority 1: Enable weekend coverage → M1 Agent                  │
│  Priority 2: Follow up 3 hot leads → M2 Agent                    │
│  Priority 3: Approve 5 outreach emails → M2 Agent                │
│                                                                  │
│  Last briefed: Today 07:31 · Next: Tomorrow 07:30                │
└─────────────────────────────────────────────────────────────────┘
```

**Card HTML pattern:**

```html
<div class="ceo-card">
  <div class="ceo-card-header">
    <div class="ceo-card-left">
      <div class="ceo-pulse active"></div>
      <div>
        <div class="ceo-card-title">CEO Agent</div>
        <div class="ceo-card-sub">Last briefed: ${lastBriefed} · Next: ${nextBriefed}</div>
      </div>
    </div>
    <button class="btn-secondary" onclick="runCEOBrief()">Run brief now</button>
  </div>
  <div class="ceo-card-insight">"${topInsightHeadline}"</div>
  <div class="ceo-priorities">
    ${priorities.map((p,i) => `
      <div class="ceo-priority-row">
        <span class="ceo-priority-rank">${i+1}</span>
        <span class="ceo-priority-action">${p.action}</span>
        <span class="ceo-priority-agent">${p.agent}</span>
        <span class="ceo-priority-impact">${p.impact}</span>
      </div>
    `).join('')}
  </div>
</div>
```

---

### 11.6 — UPWARD REPORTING: WHAT FLOWS TO MASTER CEO

Every CEO Agent sends a `report_up()` payload to the PluggedIN Master CEO Agent. This is how Pasha's morning brief is built.

The `report_up()` method returns:

```python
{
    "client_id":             tenant.client_id,
    "client_name":           tenant.client_name,
    "industry":              tenant.industry,
    "modules_active":        tenant.modules_active,
    "health_score":          int,          # 0-100, calculated from activity + checkpoint progress
    "one_line_status":       str,          # e.g. "Pipeline strong — 3 hot leads ready"
    "needs_attention":       bool,         # True if health_score < 60 or high-priority action blocked
    "high_priority_actions": list[str],    # Actions needing Pasha's approval today
    "agents_idle":           list[str],    # Modules with no activity in past 48h
    "total_activity":        int,          # Total agent runs in past 7 days
    "top_insight":           str,          # One-liner from the CEO Agent brief
    "checkpoint_status":     str,          # ON TRACK | BEHIND | ACHIEVED
    "generated_at":          str,          # ISO timestamp
}
```

**Health score calculation:**

```python
def _calc_health_score(self, briefing) -> int:
    score = 70  # baseline

    # Checkpoint weight (±20)
    if briefing.checkpoint.status == "ACHIEVED":    score += 20
    elif briefing.checkpoint.status == "ON TRACK":  score += 10
    elif briefing.checkpoint.status == "BEHIND":    score -= 20

    # Agent activity weight (±10)
    active_agents = len(briefing.agents_active)
    total_agents  = len(self.tenant.modules_active)
    if total_agents > 0:
        activity_ratio = active_agents / total_agents
        score += int((activity_ratio - 0.5) * 20)

    # High priority actions reduce score (-5 each, max -15)
    score -= min(len(briefing.insights), 3) * 5

    return max(0, min(100, score))
```

---

### 11.7 — HOW SECTION 11 CHANGES THE PORTAL GENERATION PROCESS

When generating a portal using Section 9's process, add these steps:

**Step 3A — Instantiate the CEO Agent card**
After filtering views by modules, always add the CEO Agent card to the top of Pillar 1 (Command Centre). Pre-populate `lastBriefed` from the client record. Set `topInsightHeadline` to the industry default for this revenue band (from Section 3's advisory prompt additions).

**Step 3B — Add the Ask Advisor FAB**
Inject the Ask Advisor floating button (Section 11.4 HTML) into the portal's body. Wire it to `POST /clients/{client_id}/ask` if the PluggedIN OS backend is running, with fallback to `_localAdvisorAnswer()` for offline demos.

**Step 5A — Configure CEO Agent endpoints**
Add to `PORTAL_CONFIG`:

```javascript
const PORTAL_CONFIG = {
  // ... existing fields ...
  ceoAgentEndpoint:  "http://localhost:8000/clients/{CLIENT_ID}/brief",
  askEndpoint:       "http://localhost:8000/clients/{CLIENT_ID}/ask",
  masterCEOEndpoint: "http://localhost:8000/master/brief",
};
```

**Step 5B — CEO Agent data fetch on load**

```javascript
async function loadCEOBrief() {
  try {
    const res = await fetch(PORTAL_CONFIG.ceoAgentEndpoint, {
      headers: { 'Authorization': 'Bearer ' + PORTAL_CONFIG.airtableToken }
    });
    const brief = await res.json();
    localStorage.setItem('ceo_brief_' + PORTAL_CONFIG.clientId, JSON.stringify(brief));
    renderCEOCard(brief);
  } catch(e) {
    const cached = localStorage.getItem('ceo_brief_' + PORTAL_CONFIG.clientId);
    if (cached) renderCEOCard(JSON.parse(cached));
    else renderCEOCardOffline();
  }
}
```

---

### 11.8 — CEO AGENT IN THE DEMO SCRIPT

Add this step to Section 10's Demo Script (between steps 2 and 3):

> **2b. Show the CEO Agent card**
> "This is your CEO Agent — it's been running since we set this up. It reads all your data every morning and tells you the one thing you should do today. See this insight? That's not a generic tip — it's calculated from your actual call logs and your competitors' response times. Click 'Ask your advisor' and ask it anything."
>
> *Ask it live: "Why did revenue drop last Tuesday?"*
>
> The CEO Agent responds with data-specific reasoning. This is the moment the prospect understands they're not buying a dashboard — they're buying an AI business advisor.

---

### 11.9 — AGENT HIERARCHY SUMMARY

Every portal reflects this chain of command:

```
SME Owner (portal viewer)
    │
    ▼
CEO Agent (per-client, core/ceo_agent.py)
    │  Coordinates and synthesises ↓
    ├── M1  Presence Agent
    ├── M2  Pipeline Agent
    ├── M3  Marketing Agent
    ├── M4  Intelligence Agent
    ├── M5  Sales Intelligence
    ├── M6  Data Intelligence
    ├── M7  Conversion Agent
    ├── M8  Lead Marketplace
    ├── M9  Retention OS
    └── M10 Stock Intelligence
         │
         ▼
    Reports to PluggedIN Master CEO (core/master_ceo.py)
         │
         ▼
    Pasha — PluggedIN OS Dashboard (Command view)
```

This hierarchy surfaces in three places:
1. **Client portal** — CEO Agent card + Ask advisor (this section)
2. **PluggedIN OS dashboard** — Command view shows all CEO Agents + Master brief
3. **Morning Slack message** — Master CEO's `to_slack()` output, sent daily at 07:30

When generating any portal, this hierarchy is always visible. The SME owner should feel that there is an entire team working for their business — and that the CEO Agent is the one coordinating them.
