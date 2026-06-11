# PluggedIN Agent Cards
# Complete specs for all 8 client-facing agents
# Version 1.0 | June 2026

---

## AGENT CARD SCHEMA

Each agent card contains:
- Service name + emoji + price
- Role + description
- Skills it uses
- What it delivers (capabilities + outputs)
- Typical results (quantified)
- Integration points
- Dashboard panels

---

## ACQUISITION OS (3 agents)

### 1. PRESENCE AGENT 📞
**Service ID:** presence-agent  
**Price:** £797/month  
**Role:** 24/7 AI Receptionist (answers calls, WhatsApp, books meetings)

**What it is:**
VAPI voice agent + WhatsApp integration + Cal.com booking. Never misses an inbound lead.

**Skills:**
- VAPI (voice agent for inbound calls)
- WhatsApp Business API (inbound messaging)
- Cal.com (meeting booking)

**Capabilities:**
- ✓ Answers inbound calls 24/7 (AI receptionist)
- ✓ Qualifies leads in natural conversation
- ✓ Books meetings directly to your calendar
- ✓ Sends WhatsApp alerts to director (urgent calls)
- ✓ Handles call transfers to team members
- ✓ Takes detailed call notes
- ✓ Escalates complex requests to human

**Outputs to CRM:**
- Inbound log (calls + WhatsApp messages, timestamps)
- New contacts created from inbound
- Qualified leads (hot/warm/cold scores)
- Booked meetings (datetime, attendees)
- Call transcripts (optional)
- Urgent escalations (separate alert channel)

**Integrations:**
- VAPI API (voice)
- WhatsApp Business API (messaging)
- Cal.com API (booking)
- Client CRM (create contacts + log calls)

**Dashboard Panels:**
- Calls received (today, this week)
- Qualification rate (%)
- Meetings booked
- Urgent escalations (list)
- Response time (average seconds)

**Typical Results:**
- 150 calls/month average
- 65% qualification rate
- 8 meetings booked/month
- 2 second average answer time
- 95% customer satisfaction

---

### 2. PIPELINE AGENT 📈
**Service ID:** pipeline-agent  
**Price:** £997/month  
**Role:** Lead gen + sales automation (replaces £3,000/month BDR)

**What it is:**
Full lead discovery → enrichment → qualification → outreach → booking pipeline. Finds 50-200 leads per week, enriches them, runs sequences, books meetings.

**Skills:**
- lead-discovery (55+ Apify actors + platforms)
- lead-enrichment (multi-source: registry + directory + website + LinkedIn + signals)
- lead-qualification (ICP fit scoring)
- outreach-engine (email + LinkedIn + WhatsApp sequences)
- sales-pipeline (deal tracking + nurture + calendar booking)

**Capabilities:**
- ✓ Discover 50-200 qualified leads per week from your ICP
- ✓ Enrich with: name, email, phone, title, company, decision-maker score, signals
- ✓ Score fit to your buyer profile (hot/warm/cold)
- ✓ Run multi-channel outreach (email 3-touch, LinkedIn follow-up, WhatsApp)
- ✓ Book meetings automatically on Cal.com
- ✓ Track deals through pipeline stages
- ✓ Monitor buying signals (hiring, funding, news)
- ✓ Auto-nurture cold leads
- ✓ Generate weekly pipeline reports

**Outputs to CRM:**
- Leads discovered (by source: LinkedIn, Maps, Google, etc)
- Leads enriched (with decision-maker scores, signals, accuracy metrics)
- Leads qualified (ICP fit percentage)
- Outreach campaigns (email open/click/response rates)
- Pipeline deals (by stage, value, close date)
- Weekly briefing (top opportunities, signals)

**Integrations:**
- Apify API (lead discovery)
- Vibe Prospecting MCP (enrichment)
- Company registries (Companies House, SEC)
- Cal.com (meeting booking)
- Client CRM (create leads, update pipeline)
- Gmail/Mailgun (email sending + tracking)
- WhatsApp Business API (multi-channel outreach)

**Dashboard Panels:**
- Leads discovered (this week + month)
- Enrichment quality (accuracy scores)
- Decision-maker percentage
- Outreach metrics (open rate, click rate, response rate)
- Pipeline value (by stage: interest → booked → completed → proposal → nurture → won)
- Meetings booked (this week, next week)
- Signals detected (hiring, funding, news)

**Typical Results:**
- 200 leads discovered/month
- 0.92 average accuracy score
- 75% decision-maker identification
- 2.5% outreach response rate
- 15 meetings booked/month
- £50-75 cost per meeting booked
- 21 day average sales cycle

---

### 3. CONVERSION AGENT 🤖
**Service ID:** conversion-agent  
**Price:** £897/month  
**Role:** Website AI chat + lead scoring + auto-booking

**What it is:**
AI chat widget on your website. Qualifies visitors in real-time. Auto-books hot leads. Nurtures warm leads.

**Skills:**
- lead-enrichment (visitor profiling + company identification)
- lead-qualification (real-time ICP fit scoring)
- sales-pipeline (booking + nurture sequences)

**Capabilities:**
- ✓ Chat widget embedded on your website
- ✓ Identify visitor company + role
- ✓ Score in real-time (hot/warm/cold)
- ✓ Auto-book hot leads directly to your calendar
- ✓ Send warm leads to email nurture sequence
- ✓ Escalate urgent requests via WhatsApp
- ✓ Collect contact info (if not identified)
- ✓ Provide instant answers to common questions
- ✓ Schedule follow-up meetings

**Outputs to CRM:**
- Visitor engagement log (chats, timestamps, sentiment)
- Visitor identification (company, role, intent)
- Lead scores (hot/warm/cold breakdown)
- Auto-booked meetings
- Chat transcripts
- Conversion metrics

**Integrations:**
- Anthropic API (chat + scoring)
- Client CRM (create contacts, log interactions)
- Cal.com (meeting booking)
- WhatsApp Business API (escalations)
- Google Analytics (visitor data)

**Dashboard Panels:**
- Visitor engagement (chats/day)
- Lead scores (hot/warm/cold split, pie chart)
- Auto-booked meetings (count + rate)
- Chat conversion rate (%)
- Average response time
- Top questions asked (FAQ insights)

**Typical Results:**
- 200 chat conversations/month
- 35% engagement rate (visitors who chat)
- 15% hot leads (auto-booked)
- 50% warm leads (nurture)
- 6 meetings booked/month
- 3% overall conversion rate
- Reduces sales cycle by 30%

---

## GROWTH OS (2 agents)

### 4. MARKETING AGENT 📣
**Service ID:** marketing-agent  
**Price:** £1,197/month  
**Role:** Competitor analysis + content creation + ad management

**What it is:**
Monitor what competitors are doing. Create content (blog, social, video ads). Run Meta/Google ad campaigns. Manage LinkedIn presence.

**Skills:**
- competitor-intel (monitor competitor moves)
- competitor-ad-intelligence (scrape + analyze Meta/Google ads)
- content-asset-creator (write, design, video)
- content-brief-factory (content strategy + calendars)
- ad-angle-miner (extract winning ad hooks)
- trending-ad-hook-spotter (what's working now)
- meta-ads-campaign-builder (build + manage campaigns)
- linkedin-presence (posting + engagement strategy)

**Capabilities:**
- ✓ Monitor competitor ads (Meta, Google, LinkedIn)
- ✓ Extract winning ad angles + hooks
- ✓ Create blog posts (SEO-optimized)
- ✓ Create social media content (LinkedIn, Instagram, TikTok)
- ✓ Design video ads (Creatomate integration)
- ✓ Build and manage Meta/Google ad campaigns
- ✓ Publish LinkedIn posts with optimal timing
- ✓ Track engagement + optimize performance
- ✓ Build monthly content calendar
- ✓ Competitive pricing analysis

**Outputs to CRM:**
- Competitor activity log (new hires, products, ads, pricing)
- Content calendar (published + scheduled)
- Ad campaign performance (impressions, clicks, ROAS, spend)
- Social engagement metrics (likes, comments, shares, followers)
- Content performance (views, engagement rate)
- Competitive analysis report

**Integrations:**
- Meta Ads Library API (competitor ad scraping)
- Google Ads API (competitor tracking)
- Creatomate API (video ad creation)
- LinkedIn API (posting + engagement)
- Client CRM (log competitive moves)
- Google Analytics (content performance)
- Stripe or Ad account (manage ad spend)

**Dashboard Panels:**
- Competitor activity (new hires, products, pricing)
- Content calendar (month view)
- Ad campaign performance (ROAS, CPC, conversion rate)
- Social engagement (followers, engagement rate)
- Content performance (top posts, views)
- Ad spend (budget remaining, burn rate)

**Typical Results:**
- 12 content pieces/month
- 3 active ad campaigns
- 2.5% average ad CTR
- 3.5:1 campaign ROAS
- 15% monthly follower growth
- 45% engagement rate on LinkedIn posts
- 20% reduction in CAC vs competitors

---

### 5. CUSTOMER RETENTION OS ❤️
**Service ID:** retention-agent  
**Price:** £497/month (base) + add-ons  
**Role:** Loyalty stamps + churn detection + win-back campaigns

**What it is:**
Keep existing customers happy. Detect churn risk. Run win-back campaigns. Manage reviews + reputation.

**Skills:**
- lead-enrichment (customer profiling + engagement scoring)
- sales-pipeline (nurture sequences)
- signal-detection (churn indicators)
- review-intelligence-digest (reputation management)

**Capabilities:**
- ✓ Send loyalty stamps (WhatsApp rewards)
- ✓ Detect churn risk (engagement drop, purchase decline)
- ✓ Run win-back campaigns (targeted emails, offers)
- ✓ Manage reviews + ratings across platforms
- ✓ Respond to negative reviews professionally
- ✓ Track NPS + customer satisfaction
- ✓ Monitor customer health scores
- ✓ Identify upsell opportunities
- ✓ Segment customers by value + retention risk

**Outputs to CRM:**
- Active customers (list + engagement score)
- Churn risk (alerts + reasons)
- Win-back campaign results
- Review management log
- NPS survey responses
- Customer health scores
- Upsell opportunities

**Integrations:**
- WhatsApp Business API (loyalty stamps)
- Client CRM (customer data + engagement)
- Google Reviews API (review monitoring)
- Trustpilot API (review management)
- Email platform (win-back campaigns)
- SMS (optional alerts)

**Add-ons (£ per month):**
- Stock Intelligence (£147) — monitor inventory
- Marketing Pack (£197) — seasonal campaigns
- Seasonal Campaigns (£297 per campaign) — holidays, events
- Influencer Outreach (£397) — partnership generation
- Menu Intelligence (£147) — optimize offerings (hospitality)

**Dashboard Panels:**
- Active customers (count + engagement trend)
- Churn risk (count + reasons)
- Win-back success rate (%)
- NPS score (trend)
- Review rating (average + trend)
- Loyalty rewards used (%)
- Customer lifetime value (average)

**Typical Results:**
- 35% churn prevention rate
- 15% win-back success rate
- 65 NPS score
- 4.6/5.0 review rating
- 45% loyalty program participation
- 20% increase in customer lifetime value
- 30% reduction in support tickets

---

## INTELLIGENCE OS (3 agents)

### 6. INTELLIGENCE AGENT 🔍
**Service ID:** intelligence-agent  
**Price:** £697/month  
**Role:** Market intelligence + weekly briefing

**What it is:**
Monitor competitors. Detect buying signals. Send weekly briefing (video or text). Alert on major events.

**Skills:**
- competitor-intel (monitor competitors)
- signal-detection (hiring, funding, news signals)
- signal-scanner (continuous monitoring)
- job-posting-intent (hiring signals)
- funding-signal-monitor (growth signals)
- news-signal-outreach (company announcements)

**Capabilities:**
- ✓ Monitor competitor moves (new hires, products, pricing, partnerships)
- ✓ Detect buying signals (hiring, funding, news mentions)
- ✓ Watch for market opportunities + threats
- ✓ Generate weekly briefing (video or text)
- ✓ Alert on major events affecting your industry
- ✓ Track technology adoption signals
- ✓ Identify emerging trends
- ✓ Competitive positioning analysis

**Outputs to CRM:**
- Competitor activity log (moves + dates)
- Signals detected (hiring, funding, news, tech changes)
- Weekly briefing (video + summary)
- Trend analysis (emerging patterns)
- Opportunity alerts
- Threat alerts

**Integrations:**
- Competitor monitoring sources (news, LinkedIn, job boards)
- Signal detection APIs
- Client CRM (log signals, create alerts)
- Video generation (Remotion for briefings)
- WhatsApp (urgent alerts)

**Dashboard Panels:**
- Competitor activity (last 2 weeks)
- Signals detected (count by type)
- Hiring signals (companies + roles)
- Funding signals (companies + amounts)
- News mentions (relevant stories)
- Briefing archive (last 12 weeks)

**Typical Results:**
- 25 signals detected/week
- 8 competitor changes/week
- 3 new opportunities identified/week
- 1 weekly briefing sent (video or text)
- 90% briefing open rate
- 5 actionable insights/briefing

---

### 7. SALES INTELLIGENCE 📞
**Service ID:** sales-intelligence  
**Price:** £697/month  
**Role:** Sales coaching + call analysis + pipeline review

**What it is:**
Record + transcribe sales calls. Provide coaching feedback. Review pipeline health. Suggest next actions.

**Skills:**
- sales-pipeline (pipeline tracking + deal management)
- sales-coaching (feedback generation + recommendations)
- pipeline-review (health scoring + bottleneck identification)

**Capabilities:**
- ✓ Record + transcribe all sales calls
- ✓ Provide AI coaching feedback (call quality, technique)
- ✓ Review pipeline health (conversion rates, bottlenecks)
- ✓ Suggest next actions (what to do with each deal)
- ✓ Track sales metrics (win rate, cycle, ACV)
- ✓ Identify coaching opportunities (team + individual)
- ✓ Forecast pipeline accuracy
- ✓ Benchmark team performance

**Outputs to CRM:**
- Call transcripts (searchable)
- Coaching feedback (per call, per rep)
- Pipeline health score
- Performance metrics (individual + team)
- Sales forecast (accuracy trend)
- Coaching recommendations

**Integrations:**
- Phone system (call recording)
- Client CRM (pipeline data)
- Whisper API (transcription)
- Slack/WhatsApp (coaching nudges)

**Dashboard Panels:**
- Calls recorded (this week)
- Coaching score (per rep, team average)
- Pipeline health (%)
- Conversion rate (lead → meeting → deal)
- Average deal size
- Sales cycle (average days)
- Win rate (%)

**Typical Results:**
- 40 calls/month recorded
- 7.2/10 average coaching score (improvement month 3+)
- 85% pipeline health score
- 25% conversion rate (interest → deal)
- 45 day average sales cycle
- £15,000 average deal size
- 60% win rate

---

### 8. DATA INTELLIGENCE 📊
**Service ID:** data-intelligence  
**Price:** £897/month  
**Role:** KPI tracking + monthly reports + PowerPoint dashboards

**What it is:**
Auto-track all KPIs. Generate monthly narrative videos. Create board-ready reports. Auto-populate dashboards.

**Skills:**
- airtable-automation (KPI calculation)
- reporting (Remotion narrative videos)
- data-visualization (charts + dashboards)

**Capabilities:**
- ✓ Track all KPIs (revenue, pipeline, conversion, CAC, LTV, etc)
- ✓ Calculate metrics automatically from CRM data
- ✓ Generate monthly narrative videos (Remotion)
- ✓ Create PowerPoint board packs
- ✓ Build auto-updating dashboards
- ✓ Trend analysis + forecasting
- ✓ Performance vs. targets
- ✓ Department breakdowns (sales, marketing, ops)
- ✓ Segment analysis (by product, territory, rep)

**Outputs to CRM:**
- KPI dashboard (real-time)
- Monthly narrative video (Remotion)
- Board pack (PowerPoint)
- Trend analysis
- Forecast (next quarter)
- Performance summary

**Integrations:**
- Client CRM (data source)
- Airtable (KPI calculations)
- Remotion (narrative videos)
- Google Sheets (optional)
- PowerPoint (board packs)
- Slack (weekly alerts)

**Dashboard Panels:**
- Key KPIs (big numbers: revenue, pipeline, conversion)
- Trends (line charts: month-over-month growth)
- Department breakdown (sales, marketing, ops)
- Forecast (next quarter)
- Target vs. actual (gauge charts)
- Top performers (leaderboard)

**Typical Results:**
- 15 KPIs tracked
- 1 monthly narrative video
- 12 board packs/year
- 95% dashboard uptime
- 24-hour update frequency
- 30% faster reporting (vs. manual)
- 20% better data accuracy

---

## SERVICE ECOSYSTEM

**Starter Package (£1,297/month):**
Pick 1 agent (Presence OR Pipeline OR Conversion)

**Growth Package (£2,497/month):**
Pick 3 agents (recommended combos):
- Option A: Presence + Pipeline + Conversion (Acquisition)
- Option B: Pipeline + Marketing + Retention (Growth)
- Option C: Pipeline + Intelligence + Data Intelligence (Intelligence)

**Scale Package (£4,997/month):**
All 8 agents (full suite)

**Empire OS (Multi-business):**
- Starter: £2,497/month (1 business, all agents)
- Growth: £4,997/month (up to 3 businesses)
- Empire: £9,997/month (up to 5 businesses)
- Conglomerate: £20,000+/month (5+ businesses, family office)

---

## AGENT CARD PORTAL RENDERING

Each portal loads agent cards from this file by service ID.

Example (SEGGUINÉE):
```json
{
  "selected_services": [
    "presence-agent",
    "pipeline-agent",
    "intelligence-agent"
  ],
  "agent_cards": [
    // Load from this file by service ID
    // Render with real-time CRM data
    // Show metrics, capabilities, recent activity
  ]
}
```

---

**Last updated:** June 8, 2026
