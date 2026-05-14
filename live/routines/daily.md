# PluggedIN Live — Daily Operating Routine
# This is what runs every single day. Automatically.
# Qassim's only job: read the briefing, reply GO or DECISIONS.

---

## THE DAILY TIMELINE

### 04:00 — KNOWLEDGE ACQUISITION AGENT
Before anything else, update what the system knows.
→ Pull YouTube transcripts from monitored channels
→ Scrape Reddit: r/entrepreneur, r/ecommerce, r/dropshipping, r/sidehustle
→ Browse 3 industry newsletters (TinyFish)
→ Extract actionable insights per niche
→ Update memory/semantic/ files
→ Flag any new opportunities to Opportunities table (score: 40 — Opportunity Engine will full-score later)

Run: live/agents/knowledge-agent.md
Output: Updated memory files + KnowledgeLog Airtable entry

---

### 05:00 — OPPORTUNITY ENGINE
Find new niches and business opportunities before the market.
→ Scan Instagram, TikTok, Pinterest (Apify)
→ Scan Reddit trending posts
→ Scan Google Trends spikes
→ Scan Amazon BSR movements
→ Score each opportunity 0-100
→ Log all to Opportunities table
→ Flag score ≥ 70 for morning briefing

Run: live/agents/opportunity-engine.md
Output: Opportunities logged. ≥70 scored briefing block ready.

---

### 05:30 — ECOMMERCE INTELLIGENCE AGENT
Product research for ecom businesses.
→ Scan Amazon Best Sellers (10 categories)
→ Scan AliExpress hot products
→ Scan TikTok Shop trending
→ Scan Meta ads (Apify facebook-ad-scraper)
→ Score winning products 0-100
→ Check Gumroad/Etsy for digital product opportunities
→ Monitor active products: flag any to pause or scale
→ Check ad performance vs ROAS thresholds

Run: live/agents/ecommerce-agent.md
Output: Product opportunities + active product health report

---

### 06:00 — ALL CEO AGENTS COMPILE REPORTS
Each business sector CEO Agent reads overnight data and compiles:

LEAD GEN CEO AGENT:
→ Leads found across all 6 verticals (overnight scrapes)
→ Leads delivered to buyers
→ Revenue generated yesterday
→ Buyer pipeline status
→ Outreach sequences running

ECOMMERCE CEO AGENT:
→ Revenue across all products/stores
→ Top performer and worst performer
→ Ad spend vs return
→ New product recommendations (from 05:30 scan)
→ Decisions needed (scale / pause / launch)

CONTENT CEO AGENT:
→ YouTube channel stats (views, CTR, avg view duration)
→ Content pipeline status (what's scripted, produced, scheduled)
→ New video performance (first 48hrs)
→ Pinterest traffic to Gumroad/Etsy
→ Affiliate link clicks and conversions

AGRITRADE CEO AGENT:
→ Deals in pipeline by stage
→ New producers and buyers added
→ Matches made or pending
→ Revenue from completed deals
→ Outreach sequences running

---

### 06:30 — CHIEF OF ALL CHIEFS SYNTHESIS
The master agent reads all 4 CEO reports.
Synthesises into ONE briefing for Qassim.

Format:
📊 *PluggedIN Live — Daily Briefing*
_[Day, Date]_

*LEAD GEN:* [1-2 sentences. Revenue + key flag.]
*ECOMMERCE:* [1-2 sentences. Revenue + key flag.]
*CONTENT:* [1-2 sentences. Progress + key flag.]
*AGRITRADE:* [1-2 sentences. Pipeline + key flag.]
*OPPORTUNITIES:* [Top 1-2 from Opportunity Engine, if ≥70]

*PRIORITY TODAY:* [One thing across the entire portfolio]
*DECISIONS NEEDED:* [Count — or "None, all routine"]

---

*Reply GO to approve all pending actions*
*Reply DECISIONS to see items needing your input*
*Reply PAUSE [business] to hold any specific area*

---

### 07:00 — BRIEFING DELIVERED TO QASSIM
WhatsApp via Twilio.
Qassim reads in under 5 minutes.
Replies GO, DECISIONS, or specific instructions.

---

### 07:01 onwards — EXECUTION (after GO received)
All approved actions execute:

LEAD GEN AGENT:
→ Deliver scored leads to matched buyers
→ Send invoices for leads delivered
→ Run outreach to 5 new buyers per vertical
→ Qualify any new inbound leads from Framer sites

ECOMMERCE AGENT:
→ Scale ads on products above ROAS threshold
→ Pause ads on products below ROAS threshold
→ Upload new digital products to Gumroad/Etsy
→ Post new Pinterest pins (5 per day)

AGRITRADE AGENT:
→ Send match introductions (approved by Qassim)
→ Run VAPI producer qualification calls (queued)
→ Follow up with stalled deals (auto-nudge emails)
→ Run buyer outreach sequences

CONTENT AGENT (Mon/Wed/Fri):
→ Produce video (Creatomate + ElevenLabs + Artlist)
→ Upload to YouTube with metadata
→ Repurpose clip for Instagram Reels + TikTok

---

### THROUGHOUT THE DAY (background, no input needed)
→ Knowledge Agent monitors for breaking news in each niche
→ Ecommerce Agent monitors ad performance (alerts if ROAS drops)
→ Lead Gen Agent captures inbound leads from Framer sites
→ AgriTrade Agent responds to producer/buyer enquiries (email)
→ KPI Agent updates revenue dashboard (Airtable)

---

### END OF DAY — LOGGING
All agents log their day to Airtable by 22:00:
→ Actions taken
→ Revenue generated
→ Issues encountered
→ Tomorrow's queue

This data feeds the 06:00 CEO reports the next morning.

---

## WHAT QASSIM ACTUALLY DOES

Total time required: 5-15 minutes per day.

1. Read the 07:00 WhatsApp briefing (5 minutes)
2. Reply GO (all good) or DECISIONS (list comes through)
3. Review Decisions list (5-10 minutes max)
4. Approve, reject, or adjust — back to agents in seconds
5. Done. Everything else runs.

One decision session per day.
Everything routine executes automatically.
Qassim's job is strategy and approval — not execution.
