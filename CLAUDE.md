# PluggedIN — Operator Brain (Qassim)
# Version 4.0 | April 2026
# Location: ~/Documents/AI-Agency/PluggedIN/CLAUDE.md
# Read every session. Every decision references this.
# This document runs the entire operation.

---

## WHAT PLUGGEDIN IS

PluggedIN is a fully autonomous AI conglomerate and done-for-you
business operating system. It operates on two levels simultaneously:

PLUGGEDIN LIVE — Our own portfolio of businesses built and run
entirely by agents. Zero staff. Pure margin. Compounds daily.

PLUGGEDIN CLIENT — Done-for-you AI retainer for other businesses.
We deploy their entire operating system. Agents run their operations.
They make decisions. Everything else handles itself.

NOT an agency. NOT a SaaS. NOT a chatbot builder.
A done-for-you AI retainer that replaces entire departments.

Tagline: "We don't sell software.
We deploy outcomes. Your AI team starts Monday."

---

## WHO I AM

Qassim Abdulkarim
Founder of PluggedIN
Building a global AI-operated business conglomerate
Based in Rwanda and UK
Claude Pro subscriber

---

## AGENT PSYCHOLOGY — NON NEGOTIABLE

Agents NEVER ask Qassim what to do.
Agents READ all available data.
Agents TELL Qassim what is happening and what should happen next.

Every proactive communication format:

SITUATION: [facts and numbers, no fluff, 3 sentences max]
PRIORITY: [single most important thing right now]
RECOMMENDATION: [specific action, precise enough to execute]
REASONING: [why this, 2 sentences max]
EXPECTED OUTCOME: [what happens if we act today]
PROCEED? [yes / no / adjust]

Never say: "What would you like to do?"
Never say: "Here are some options"
Never say: "It depends on"
Always say: "Data shows X. I recommend Y. Reason: Z. Proceed?"

---

## WORKSPACE STRUCTURE

~/Documents/AI-Agency/
├── PluggedIN/
│   ├── CLAUDE.md                 ← This file. The brain.
│   ├── AGENTS.md                 ← OpenCode version
│   ├── .env                      ← All API keys (never share)
│   ├── .env.example              ← Template
│   ├── requirements.txt          ← Python dependencies
│   ├── scoring-criteria.md       ← ICP scoring rubric
│   ├── copy-framework.md         ← Outreach copy rules
│   ├── skill-scraper.md          ← Skill validation rules
│   ├── core/
│   │   └── tenant.py             ← Multi-tenant config loader (THE OS SPINE)
│   ├── lib/
│   │   ├── apify_client.py       ← Bulk scraping
│   │   ├── tinyfish_client.py    ← Intelligent browsing
│   │   ├── airtable_client.py    ← CRM and data
│   │   ├── vibe_client.py        ← B2B contacts
│   │   ├── creatomate_client.py  ← Video and image ads
│   │   ├── github_client.py      ← Skill discovery
│   │   ├── vapi_client.py        ← Voice agents
│   │   ├── retention_client.py   ← Loyalty and churn
│   │   ├── stock_intel_client.py ← Supply chain
│   │   ├── dispatch_client.py    ← Business deployment
│   │   └── intake_processor.py  ← Client intake
│   ├── memory/
│   │   ├── working/
│   │   │   ├── today.md          ← Active tasks and priority
│   │   │   └── pipeline.md       ← Live lead tracker
│   │   ├── episodic/
│   │   │   └── log.md            ← Session history
│   │   ├── semantic/
│   │   │   ├── icp.md            ← Ideal customer profiles
│   │   │   ├── clients.md        ← Client profiles
│   │   │   └── pricing.md        ← All pricing and packages
│   │   └── personal/
│   │       └── preferences.md    ← Qassim's working style
│   ├── templates/
│   │   ├── client_intake.md      ← Universal intake form
│   │   ├── claude_md_template.md ← Client CLAUDE.md generator
│   │   └── env_template.md       ← .env by module
│   ├── industries/
│   │   ├── restaurant.md
│   │   ├── logistics.md
│   │   ├── construction.md
│   │   ├── legal.md
│   │   └── healthcare.md
│   ├── docs/
│   │   └── demo-system.md        ← 10-minute sales demo playbook
│   ├── live/
│   │   ├── CLAUDE.md             ← PluggedIN Live operating brain
│   │   ├── agents/
│   │   │   ├── opportunity-engine.md  ← Daily niche discovery
│   │   │   ├── knowledge-agent.md     ← Continuous learning system
│   │   │   ├── ecommerce-agent.md     ← Product research and ecom ops
│   │   │   ├── lead-gen-agent.md      ← All 6 lead gen verticals
│   │   │   ├── youtube-agent.md       ← 5 channel management
│   │   │   └── agritrade-agent.md     ← Commodity matching
│   │   ├── businesses/                ← One file per active business
│   │   └── routines/
│   │       ├── daily.md               ← Full daily operating rhythm
│   │       └── weekly.md              ← Weekly review and scaling
│   ├── skills/                   ← Custom skills
│   │   ├── dashboard/
│   │   │   └── SKILL.md          ← Dashboard + demo generator skill
│   │   ├── huashu-design/
│   │   │   └── SKILL.md          ← Visual design system (801 lines, installed)
│   │   └── graphify/
│   │       └── SKILL.md          ← Codebase knowledge graph (install manually)
│   └── outputs/
│       ├── leads/
│       ├── sequences/
│       ├── reports/
│       └── dashboards/           ← Generated HTML dashboards
└── Clients/
    └── [ClientName]/
        ├── CLAUDE.md
        ├── scoring-criteria.md
        ├── copy-framework.md
        ├── lib/
        ├── memory/
        └── outputs/

---

## THE COMMAND STRUCTURE

Every business — ours and clients — runs on this hierarchy:

QASSIM
│
│ ← Daily VAPI briefing or WhatsApp summary
│ ← One decision session per day
│ ← Click any business to dive deeper
│
└── CHIEF OF ALL CHIEFS (Master AI)
    │ Reads all CEO reports across all businesses
    │ Runs weekly cross-business CEO meeting
    │ Synthesises everything into one daily briefing
    │ Only escalates what genuinely needs Qassim
    │
    ├── CEO AGENT per business/sector
    │   └── Sub-agents running specific tasks
    │       └── All actions logged to Airtable
    │           └── Results flow back up the chain

DECISION PROTOCOL:
→ Routine tasks: executed automatically, logged
→ Notable wins: included in daily briefing
→ Anomalies: flagged with recommendation
→ Decisions above threshold: escalated with full context
   + recommendation + one-click approve

HUMAN STAFF PROTOCOL:
→ Staff submit updates via portal (never call Qassim)
→ CEO agent processes, acts, logs
→ Head CEO synthesises across departments
→ Owner only sees what genuinely needs them

---

## THE FULL AGENT ROSTER

INTELLIGENCE LAYER (runs for everything):
→ Knowledge Acquisition Agent — learns from YouTube,
  Reddit, blogs, forums. Updates all skills continuously.
  The brain feeder. Makes every other agent smarter.
→ Opportunity Engine Agent — scrapes Instagram, TikTok,
  Pinterest, Gumroad daily. Finds trending niches and
  winning products before market catches on.
→ Market Intelligence Agent — tracks trends, competitors,
  pricing shifts, demand curves across all sectors.

BUSINESS CREATION LAYER:
→ Dispatch Agent — receives client intake, spins up
  complete infrastructure in hours. Auto-deploys everything.
→ Brand Agent — creates name, visual identity, tone of voice.
→ Website Agent — builds Framer/Gumroad/Etsy presence,
  SEO optimised, lead capture live.

REVENUE LAYER:
→ Ecommerce Intelligence Agent — scrapes Amazon, AliExpress,
  TikTok Shop. Analyses Meta ads, Google Trends, Instagram
  engagement. Identifies winning products with data.
  Finds suppliers. Calculates margins. Recommends launches.
→ Lead Generation Agent — finds and qualifies leads
  per industry. Outreaches. Sells to relevant businesses.
→ Commodity Matching Agent — connects African and global
  commodity producers with buyers. Takes transaction %.
→ YouTube Content Agent — scrapes winning videos,
  analyses what works, generates and posts content
  across all channels automatically.

CLIENT LAYER:
→ Onboarding Agent — captures full business brain via VAPI.
  Populates all memory layers. Configures all other agents.
→ Pipeline Agent — finds leads, outreaches, books meetings.
→ Retention Agent — loyalty stamps, churn detection,
  win-back campaigns, review management.
→ Marketing Agent — ads, content, competitor monitoring,
  Creatomate videos, Artlist assets.
→ Stock Intelligence Agent — monitors stock levels,
  alerts suppliers, auto-orders at threshold.

OPERATIONS LAYER:
→ KPI Agent — tracks all metrics across all businesses.
→ Narrative Agent — Remotion videos + PowerPoint reports.
→ Review Agent — monitors, responds, reports, removes.
→ Compliance Agent — licences, certificates, deadlines.
→ Client Success Agent — monitors client health score,
  flags churn risk, manages 30/60/90 day VAPI check-ins,
  drafts upsell recommendations for Qassim review.
→ Investor Relations Agent — tracks PluggedIN Live revenue,
  prepares monthly conglomerate report, compiles metrics
  for future fundraising or partnership conversations.
→ Opportunity Scanner Agent — monitors Instagram, Reddit,
  TikTok, Google Trends for new niches. Scores each
  opportunity 0-100 and escalates when score > 70.
  Distinct from Opportunity Engine (ecommerce product finder).

COMMAND LAYER:
→ CEO Agent per business sector
→ Head CEO Agent per business
→ Chief of All Chiefs — reports to Qassim daily

---

## PLUGGEDIN LIVE — OUR CONGLOMERATE

Agents find opportunities, build businesses, run them,
report up the chain. Continuously. Automatically.

LEAD GEN VERTICALS (same system, different niche):
→ PlumbRight — plumbing leads, £25-50/lead
→ SolarLink — solar installation leads, £50-150/lead
→ BuildConnect — construction leads, £100-300/lead
→ LegalMatch — solicitor leads, £200-500/lead
→ MortgageMatch — mortgage broker leads, £100-500/lead
→ CareConnect — care home leads, £500-2,000/lead
→ [New verticals spun up weekly by agents]

Each vertical:
→ Agents build the website (Framer)
→ Agents find and qualify leads (Apify + TinyFish + VAPI)
→ Agents find buyers (scraped from trade directories)
→ Match and sell. Log to Airtable. Report to CEO agent.

DIGITAL PRODUCT BUSINESSES:
→ Gumroad Store — templates, guides, prompt packs,
  notion dashboards, business playbooks.
  Agents scrape bestsellers → create similar → upload → sell.
→ Pinterest AI Art Store — Flux generates high quality
  paintings in trending styles. Agent monitors saves,
  doubles down on winners. Links to Etsy/Gumroad.
→ Wedding & Ceremony Design Studio — AI mood boards,
  invitations, seating plans, colour palettes.
  Agents find engaged couples on Instagram → outreach → sell.

ECOMMERCE:
→ Opportunity Engine finds winning products daily
→ Ecommerce agent deep-analyses market demand
→ Sources suppliers from Alibaba/AliExpress
→ Builds store (Shopify/WooCommerce)
→ Meta ads written and managed by agent
→ Option A: Dropshipping (zero inventory)
→ Option B: Digital equivalent (100% margin)
→ Option C: Affiliate content (pure passive)

COMMODITY MARKETPLACE (AgriTrade):
→ Connects African producers with global buyers
→ Cocoa, cashew, sesame, palm oil, shea butter, timber
→ VAPI qualifies both sides
→ 1-3% per transaction facilitated
→ One £500k deal = £5,000-£15,000

YOUTUBE CHANNELS:
→ Health & Ingredients (faceless)
→ African History (documentary style)
→ Money & Business (cartoon)
→ True Crime (narration)
→ AI & Tech Explained (Remotion data viz)
Each: Creatomate + Artlist + ElevenLabs voiceover
Monetised: AdSense + affiliate + sponsorship

NEW BUSINESS AUTO-LAUNCH:
Opportunity Engine flags → Qassim approves →
Hour 1: Research + competitive analysis
Hour 2: Brand identity created
Hour 3: Website/store live, listings uploaded
Hour 4: First outreach sent, CEO agent assigned
Hour 5: Business reporting in OS dashboard

---

## KNOWLEDGE ACQUISITION AGENT — THE BRAIN FEEDER

Most important agent in the system.
Makes every other agent smarter over time.

Sources monitored continuously:
→ YouTube: transcripts extracted from top videos
  in every niche we operate (youtube-apify-transcript)
→ Reddit: relevant subreddits for real practitioner insights
→ Industry blogs and newsletters (TinyFish reads daily)
→ Competitor monitoring (how other operators work)
→ Forums and communities (buyer language extraction)

What it does with knowledge:
→ Updates memory/semantic/ with new facts
→ Drafts skill improvements for Qassim approval
→ Updates copy-framework.md with winning language
→ Refines ICP profiles with real buyer data
→ Flags strategy updates for CLAUDE.md

Compound effect:
Week 1: Agents at baseline
Month 3: Agents operating with knowledge of every
         top practitioner in every niche
Month 12: Impossible to compete with. The gap widens
          every single week automatically.

---

## ARCHITECTURE — MULTI-TENANT AGENT OS

PluggedIN is NOT 10 separate agents. It is ONE Agent OS,
multi-tenant by design, productised into 10 client-facing modules.

THREE LAYERS:

LAYER 1 — CLIENT MODULES (what clients buy and see)
  10 named modules. Each is a productised slice of the OS.
  Clients pay per module. They never see the backend.

LAYER 2 — SHARED AGENT OS (the real product)
  core/tenant.py loads any client's config in one call.
  lib/ scripts handle every integration — one codebase, all clients.
  All agents run from the same lib/. No code duplication.
  Tenant context flows through every agent call.

LAYER 3 — BUSINESS SYSTEM INTEGRATIONS
  VAPI (voice) · Airtable (data) · Cal.com (booking)
  WhatsApp/Green API (messaging) · Apify (scraping)
  Creatomate (creative) · Gmail (outreach)

MULTI-TENANT RULES:
→ Every agent call receives a tenant object from core/tenant.py
→ tenant object carries: client_id, airtable_base, vapi_assistant_id,
  cal_link, modules_active, whatsapp_number, industry, plan
→ No hardcoded client values anywhere in lib/
→ Adding a new client = one new row in Airtable + .env entry
→ lib/ scripts are stateless — they receive tenant, they execute

THREE OS GROUPS (how the 10 modules are organised internally):

ACQUISITION OS — getting clients new business
  Module 1: Presence Agent
  Module 2: Pipeline Agent
  Module 7: Conversion Agent
  Module 8: Lead Marketplace

GROWTH OS — keeping and growing existing customers
  Module 3: Marketing Agent
  Module 9: Customer Retention OS

INTELLIGENCE OS — knowing what's happening before it matters
  Module 4: Intelligence Agent
  Module 5: Sales Intelligence
  Module 6: Data Intelligence
  Module 10: Stock Intelligence

Each OS group shares a logical data layer:
→ Acquisition OS writes to pipeline/leads tables
→ Growth OS writes to loyalty/campaigns/reviews tables
→ Intelligence OS writes to briefings/signals/reports tables

---

## PLUGGEDIN CLIENT — DONE-FOR-YOU RETAINER

THE 10 MODULES:

--- ACQUISITION OS ---

Module 1 — Presence Agent: £797/month
VAPI receptionist + WhatsApp + Cal.com
Never miss an inbound lead. 24/7 coverage.

Module 2 — Pipeline Agent: £997/month
Lead research + signals + outreach + booking.
Replaces £3,000/month BDR salary.

Module 7 — Conversion Agent: £897/month
Website engagement + lead scoring + auto-booking.

Module 8 — Lead Marketplace: £997/month
VAPI outbound + lead qualification + selling.
Agents find buyers and sellers in client's industry.

--- GROWTH OS ---

Module 3 — Marketing Agent: £1,197/month
Competitor analysis + content + video ads.
Creatomate + Artlist + Mobbi AI.
Platforms: LinkedIn, Instagram, TikTok, Facebook.

Module 9 — Customer Retention OS: £497/month
WhatsApp loyalty stamps + churn detection +
personalised win-back + review management.
Add-ons: Stock Intelligence £147, Marketing Pack £197,
Seasonal Campaigns £297/campaign,
Influencer Outreach £397, Menu Intelligence £147.

--- INTELLIGENCE OS ---

Module 4 — Intelligence Agent: £697/month
Competitor monitoring + weekly briefing.
Market signals + opportunity scanning.

Module 5 — Sales Intelligence: £697/month
Call analysis + coaching + pipeline review.

Module 6 — Data Intelligence: £897/month
KPI tracking + Remotion narrative videos +
PowerPoint board packs. Auto-generated monthly.

Module 10 — Stock Intelligence: £297/month
Real-time stock monitoring + supplier alerts +
auto-ordering at threshold.
Supplier portal: live visibility across all clients.

REVIEW REMOVAL (standalone revenue):
Single removal: £75
Starter pack (3): £175
Protection (5): £299
Reputation Shield (unlimited): £497/month

PACKAGES:
Starter: £1,297/month (1 module)
Growth: £2,497/month (3 modules)
Scale: £4,997/month (all modules)
Enterprise: Custom

EMPIRE OS (multi-business owners):
Starter OS: £2,497/month (1 business, all modules)
Growth OS: £4,997/month (up to 3 businesses)
Empire OS: £9,997/month (up to 5 businesses)
Conglomerate: £20,000+/month (5+ businesses, family office)

---

## THE OS DASHBOARD

Every business — ours and clients — runs on one dashboard.

PLUGGEDIN LIVE VIEW (Qassim's ops portal):
→ All conglomerate businesses running
→ CEO agents reporting per sector
→ Chief of All Chiefs daily briefing
→ Revenue across all businesses
→ New opportunities flagged
→ Decisions queued for approval

CLIENT VIEW (per client portal):
→ Their CEO agents running their operations
→ Modules they're paying for (active)
→ Modules locked (visible but greyed — drives upsell)
→ Staff submission portal
→ Weekly performance metrics
→ Monthly Remotion narrative video

DEMO VIEW — SINGLE BUSINESS (for single-business prospects):
→ Industry-specific sample data
→ All modules running
→ CEO agents reporting live
→ Chief Agent briefing running
→ Toggled to their industry before the meeting
→ URL: pluggedin.softr.app/demo/[industry]

DEMO VIEW — EMPIRE OS (for multi-business owners):
→ Portfolio of 3 sample businesses pre-loaded
→ Chief of All Chiefs synthesised briefing at top
→ One tile per business — click to drill in
→ CEO Agent status row (one per business)
→ Portfolio KPI table (revenue, pipeline, compliance)
→ Pending approvals panel (what needs owner input)
→ Full scale package active per business
→ URL: pluggedin.softr.app/demo/empire
→ See docs/demo-system.md for full Empire OS demo script

TECHNOLOGY:
Now: Softr (fast to deploy, Airtable-connected)
Month 6: Custom React/Next.js (dark mode, real-time,
         sleek, Bloomberg-meets-Apple aesthetic)

---

## CLIENT DELIVERY MODEL

1. Prospect sees demo portal — agents running live
2. Signs retainer — module toggle activated
3. Dispatch agent spins up infrastructure
4. VAPI onboarding call — captures business brain
5. All memory layers populated from onboarding
6. CEO agents configured and deployed
7. Client portal live (Softr) — their data, their modules
8. Staff trained to submit via portal (not call owner)
9. First morning briefing delivered next day
10. Weekly reports + monthly Remotion narrative automated

PROTECTION MODEL:
PluggedIN NEVER sends outreach as client.
PluggedIN outreaches AS PluggedIN.
Warms relationships. Makes introductions.
Client appears only when genuine interest exists.

DONE-FOR-YOU PROMISE:
Client never touches the technology.
They interact with results, not systems.
AI evolves → we upgrade quietly → they get better results.
They never know. They never need to.

---

## INDUSTRIES WE SERVE

Legal (solicitors, law firms)
Restaurants and hospitality
Logistics and transport
Construction and trades
Property and real estate
Healthcare and care homes
Recruitment agencies
Import and export
Retail (physical and digital)
Professional services
Multi-business owners and family offices

---

## TECH STACK

Primary agent: Claude Code
Backup agent: OpenCode 1.4.3 + OpenRouter
Scheduling: Claude Code Routines (cloud)
Computer tasks: Claude Cowork

Data collection:
→ lib/apify_client.py (bulk scraping)
→ lib/tinyfish_client.py (intelligent browsing + Reddit)
→ lib/vibe_client.py (B2B contacts)

Storage:
→ lib/airtable_client.py (all CRM and operational data)

Communication:
→ Gmail MCP (outreach and sequences)
→ Google Calendar MCP (booking)
→ VAPI (voice agents — inbound and outbound)
→ Twilio WhatsApp (loyalty stamps, briefings, alerts)

Creative:
→ lib/creatomate_client.py (video + image ads)
→ Artlist (royalty-free music + stock footage)
→ Mobbi AI (vibe editing for custom footage)
→ Remotion (data narrative videos)
→ ElevenLabs (voiceover)
→ Flux (AI image generation — Pinterest art, product images,
        ad creatives. Run via Replicate API or Black Forest Labs)

Ecommerce:
→ Shopify / WooCommerce (stores)
→ Gumroad (digital products)
→ Etsy (AI art and design products)
→ Pinterest (traffic and discovery)

Web presence:
→ Framer (marketing websites and lead gen sites)
→ Softr (client portals and OS dashboard)

Client delivery:
→ lib/dispatch_client.py (infrastructure deployment)
→ lib/retention_client.py (loyalty and churn)
→ lib/stock_intel_client.py (supply chain)
→ lib/vapi_client.py (voice layer)
→ lib/github_client.py (skill discovery)

Free model backup via OpenRouter:
→ google/gemma-4 (research, free)
→ deepseek/deepseek-r2 (coding, cheap)
→ moonshot/kimi-2.5 (reasoning backup)

REMOVED — never suggest again:
Ruflo, Paperclip, Cursor, Antigravity, Manus,
Verdent, NemoClaw, Ollama, Cline, DeerFlow,
Goose agent, Smartlead, Octogent, Higgsfield,
Relevance AI

---

## SKILLS INSTALLED

Capabilities (49): cold-email-outreach, icp-identification,
brand-voice-extractor, visual-brand-extractor,
content-asset-creator, google-ad-scraper,
linkedin-outreach, linkedin-message-writer,
apollo-lead-finder, signal-scanner, job-posting-intent,
tiktok-influencer-finder, kol-discovery, reddit-post-finder,
competitor-post-engagers, youtube-apify-transcript,
and 33 more GTM capabilities.

Composites: meta-ads-campaign-builder, google-search-ads-builder,
ad-angle-miner, competitor-ad-intelligence, ad-campaign-analyzer,
trending-ad-hook-spotter, campaign-brief-generator,
content-brief-factory, messaging-ab-tester,
outbound-prospecting-engine, signal-detection-pipeline,
inbound-lead-qualification, sales-call-prep,
sales-coaching, pipeline-review, and 20 more.

Playbooks: outbound-prospecting-engine,
competitor-monitoring-system, signal-detection-pipeline,
seo-content-engine, event-prospecting-pipeline.

---

## CUSTOM SKILLS (PluggedIN Built)

These are SKILL.md files Claude reads and follows automatically.
Location: ~/Documents/AI-Agency/PluggedIN/skills/

### skills/dashboard/SKILL.md
TRIGGER: "build a dashboard", "generate a demo", "create a KPI tracker",
         "build a client demo", "show me the [module] dashboard"
WHAT IT DOES:
→ Generates standalone HTML dashboard — no Cowork required
→ Demo mode: uses industry playbook data (fake, for sales calls)
→ Live mode: fetches real data from Airtable REST API
→ Applies PluggedIN design system (purple #6c63ff, 8px grid, trust signals)
→ Saves to outputs/dashboards/ with naming: demo_{industry}_{date}.html
→ Reads industry playbooks from industries/*.md for demo data
→ Includes 10 module panel templates, Chart.js charts, auto-refresh

DEPENDENCY: skills/huashu-design/SKILL.md (load first if present)
INSTALL HUASHU DESIGN (run once in terminal):
  mkdir -p ~/Documents/AI-Agency/PluggedIN/skills/huashu-design
  curl -L https://raw.githubusercontent.com/alchaincyf/huashu-design/master/SKILL.md \
    -o ~/Documents/AI-Agency/PluggedIN/skills/huashu-design/SKILL.md

### skills/graphify/SKILL.md
TRIGGER: "map the codebase", "knowledge graph", "understand the repo",
         "what does X connect to", "dependency map", "graph the project"
WHAT IT DOES:
→ Turns the entire PluggedIN folder into a queryable knowledge graph
→ Maps every lib/, agent, skill, memory file and how they connect
→ Generates graph.json + GRAPH_REPORT.md automatically
→ Post-commit hook rebuilds the graph on every git commit
→ Lets Claude Code answer "what calls what" across the full codebase
→ Installed from: github.com/safishamsi/graphify (1,000+ stars)

INSTALL (run once in terminal):
  mkdir -p ~/Documents/AI-Agency/PluggedIN/skills/graphify
  curl -L https://raw.githubusercontent.com/safishamsi/graphify/main/graphify/skill.md \
    -o ~/Documents/AI-Agency/PluggedIN/skills/graphify/SKILL.md

STATUS: Folder created — run install command above to download SKILL.md

### skills/huashu-design/SKILL.md
TRIGGER: any visual output, dashboards, reports, any HTML generation
WHAT IT DOES:
→ 20 design philosophies from github.com/alchaincyf/huashu-design
→ 6,600 GitHub stars — battle-tested visual system
→ Auto-loaded before any dashboard or visual artifact is generated
→ Complements Chart.js, Remotion, Softr outputs

WHEN BUILDING DASHBOARDS:
1. Read skills/huashu-design/SKILL.md FIRST (if file exists)
2. Then read skills/dashboard/SKILL.md
3. Follow dashboard SKILL.md steps 1-9
4. Apply huashu design philosophies to every visual decision

---

## MODEL ROUTING

Opus 4.7: strategy, proposals, complex reasoning,
          Chief of All Chiefs decisions
Sonnet 4.6: building, coding, outreach writing,
            CEO agent operations
Haiku 4.5: data tasks, CRM updates, lookups,
           routine logging and monitoring
Gemma 4 free: research, monitoring, backup tasks
DeepSeek: code generation backup
Kimi 2.5: complex reasoning when Claude limits hit

---

## TOOL RULES — NON NEGOTIABLE

ALWAYS use lib/ wrapper scripts. NEVER call APIs directly.
ALWAYS load tenant context first via core/tenant.py.

| Need | Use |
|------|-----|
| Load client config | core/tenant.py → get_tenant(client_id) |
| Scraping / Google Maps | lib/apify_client.py |
| Web browsing / Reddit | lib/tinyfish_client.py |
| B2B contacts / enrichment | lib/vibe_client.py |
| CRM / data logging | lib/airtable_client.py |
| Video / image ads | lib/creatomate_client.py |
| Voice calls | lib/vapi_client.py |
| Loyalty / reviews / churn | lib/retention_client.py |
| Stock tracking | lib/stock_intel_client.py |
| Client deployment | lib/dispatch_client.py |
| Onboarding processing | lib/intake_processor.py |
| Skill discovery | lib/github_client.py |

Every agent script starts with:
  from core.tenant import get_tenant
  tenant = get_tenant(client_id)
  # All subsequent lib calls use tenant.* for client-specific config

Why: lib/ scripts handle auth, error handling, retry logic,
and logging. Raw API calls bypass all of this and break.
core/tenant.py ensures no client data leaks between tenants.

---

## SKILL VALIDATION RULES

Before installing any skill from GitHub:
→ Minimum 50 GitHub stars
→ Last commit within 180 days
→ Must have SKILL.md in root
→ Must be from approved source list in skill-scraper.md
→ Validate using lib/github_client.py before installing

Run: github_client.validate_skill(url) before every install.
If validation fails: do not install. Find an alternative.

---

## WHATSAPP BRIEFING FORMAT

Daily 7am briefing format (WhatsApp — keep under 250 words):

📊 *[Business Name] — Daily Briefing*
_[Day, Date]_

*SITUATION:* [3 facts with numbers. No fluff.]

*PRIORITY:* [One thing. Always one thing.]

*RECOMMENDATION:* [Specific action — precise enough to execute]

*EXPECTED OUTCOME:* [What happens if we act today]

---
_Reply *GO* to approve all pending actions_
_Reply *DECISIONS* to see items needing your input_
_Reply *PAUSE* to hold all outreach_

Owner approves or redirects. Nothing executes without GO.
Agents NEVER send outreach without approval unless explicitly
set to auto-approve mode for that specific routine task.

---

## SECURITY

All keys in .env — never in markdown files
Never pushed to GitHub (.gitignore protects)
GITHUB_TOKEN for skill discovery (5,000 req/hr)
Airtable scopes: data.records:read/write, schema.bases:read

---

## TOKEN EFFICIENCY

/compact at 50% context always
/clear between unrelated tasks
/recap when returning to sessions
lib/ scripts save 90% tokens vs raw API calls
Skills save 500 tokens per repeated task
Right model every time (see model routing above)

---

## SESSION START PROTOCOL

Every session without exception:
1. Read memory/working/today.md (tasks + priority)
2. Read memory/working/pipeline.md (live pipeline)
3. Read memory/episodic/log.md (last session context)
4. If session involves Live businesses → read live/CLAUDE.md
5. Check Airtable pipeline via MCP
6. Assess revenue status and blockers
7. Identify highest leverage action
8. Deliver proactive briefing in standard format
9. Wait for approval then execute

LIVE BUSINESS SESSIONS — also read:
→ live/agents/[relevant-agent].md before running that agent
→ live/routines/daily.md for the full operating rhythm
→ live/routines/weekly.md on Monday sessions

---

## AIRTABLE STRUCTURE — NON NEGOTIABLE

Three bases. Each has a distinct purpose. Never mix them.

| Base | Env Var | Purpose |
|------|---------|---------|
| PluggedIN Agency Clients | AIRTABLE_BASE_AGENCY | Running the agency. All signed clients, MRR, agent reports, CEO briefings, optimisations. This is the command centre. |
| PluggedIN Lead Gen | AIRTABLE_BASE_PLUGGEDIN | Qassim's own prospecting. Leads, accounts, deals, activities for finding and closing new clients. |
| [ClientName] | AIRTABLE_BASE_[CLIENT] | Each signed client's operational data. Referenced in Agency Clients → Clients table → Airtable Base ID field. |

### Agency Clients Base (appl51bhjj9R2wtKx) — 5 tables:
→ Clients        — one row per signed client. MRR, plan, modules, health score, churn risk.
→ Agent Reports  — daily log of every module run. Status, actions taken, errors, revenue impact.
→ CEO Briefings  — AI briefings per client. Situation / Priority / Recommendation / Outcome.
→ Revenue        — monthly MRR tracker. New clients, churn, net growth.
→ Optimisations  — agent-generated improvement recommendations. Priority, status, result.

### When writing agent output:
→ Operational data (leads found, calls made, signals) → write to client's own base
→ Summary / status / briefing → write to Agency Clients base
→ New prospect contact → write to Lead Gen base (never to Agency Clients)

---

## CURRENT STATUS

Revenue: £0 — CRITICAL URGENCY
Target: First client in 7 days
Gromatic (Damian): £797/month + bonus per closed case
10 solicitor contacts researched and ready

Immediate priorities:
1. Fill .env API keys
2. Send Gromatic proposal today
3. Launch outreach to 10 solicitors
4. Confirm Apify MCP in VS Code

Conglomerate status: Architecture complete.
Build order: Gromatic first. Revenue unlocks everything.

Internal pipeline: Being built
YouTube channels: Not started
Lead gen verticals: Not started
Commodity marketplace: Not started

---

## PLUGGEDIN GROWTH ROADMAP

Week 1: Close Gromatic (£797/month)
Week 2: First lead gen vertical live (plumbing or solar)
Week 3: First two YouTube channels launched
Week 4: AgriTrade commodity marketplace live

Month 2: 5 restaurant clients on Retention OS
Month 2: First Empire OS demo to multi-business owner
Month 3: £10,000 MRR — all streams contributing

Month 6: Custom OS dashboard built (React/Next.js)
Month 6: 3 Empire OS clients (£30,000 MRR from this alone)
Month 12: Conglomerate generating £50,000+/month
          Running itself. Qassim making decisions.
          Everything else handled by agents.
