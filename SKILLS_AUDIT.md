# PluggedIN Skills Audit
# Complete inventory of available services
# June 9, 2026

---

## SKILLS BY SERVICE TYPE (50+ total)

### TIER 1: LEAD ACQUISITION (Core Revenue)
- lead-discovery (LinkedIn, Maps, Google, Companies House, Apify, Vibe)
- lead-enrichment (ScrapeGraphAI, registries, website scraping)
- lead-qualification (ICP scoring, decision-maker detection)
- outreach-engine (email, LinkedIn, WhatsApp sequences)
- sales-pipeline (booking, deal tracking, nurture)
- signal-detection (hiring, funding, news, product launches)
- signal-scanner (continuous monitoring)

**Revenue service:** Pipeline Agent (£997/month)

---

### TIER 2: CUSTOMER ACQUISITION (Agency work)
- competitor-intel (tracking competitor moves)
- competitor-ad-intelligence (Meta/Google ad scraping)
- ad-angle-miner (winning ad hooks extraction)
- trending-ad-hook-spotter (what's working now)
- meta-ads-campaign-builder (campaign creation + management)
- google-search-ads-builder (Google Ads campaigns)
- brand-voice-extractor (voice + tone identification)
- visual-brand-extractor (brand identity from websites)

**Revenue service:** Marketing Agent (£1,197/month)

---

### TIER 3: CUSTOMER RETENTION (Growth)
- review-intelligence-digest (monitoring + responding)
- champion-tracker (tracking key contacts)
- signal-detection (churn indicators)

**Revenue service:** Retention Agent (£497-£697/month)

---

### TIER 4: INTELLIGENCE & INSIGHT (Premium)
- industry-scanner (market trends)
- news-signal-outreach (company announcements)
- funding-signal-monitor (growth signals)
- job-posting-intent (hiring signals)
- event-prospecting-pipeline (events + attendees)
- seo-content-audit (website SEO analysis)
- seo-opportunity-finder (ranking opportunities)
- seo-domain-analyzer (domain authority analysis)
- seo-traffic-analyzer (traffic patterns)
- programmatic-seo-planner (at-scale SEO)
- programmatic-seo-spy (competitor SEO)

**Revenue service:** Intelligence Agent (£697/month)

---

### TIER 5: CONTENT & CREATIVITY (Done-for-you)
- content-asset-creator (blog, social, video)
- content-brief-factory (content strategy + calendars)
- campaign-brief-generator (campaign planning)
- email-drafting (cold email copy)
- pain-language-engagers (buyer pain extraction)
- linkedin-message-writer (LinkedIn personalization)
- linkedin-presence (posting + engagement strategy)
- battlecard-generator (sales battlecards)
- create-html-carousel (interactive elements)
- create-html-slides (presentations)

**Revenue service:** Marketing Agent (£1,197/month)

---

### TIER 6: SALES & COACHING (Premium)
- sales-pipeline (pipeline management)
- pipeline-review (health scoring)
- sales-call-prep (meeting briefing)
- meeting-brief (call notes + strategy)
- sales-coaching (call feedback + coaching)
- icp-website-audit (prospect website analysis)
- company-contact-finder (contact research)
- apollo-lead-finder (Apollo.io integration)
- vibe-prospecting (Vibe Prospecting MCP)

**Revenue service:** Sales Intelligence (£697/month)

---

### TIER 7: RESEARCH & ICP DEVELOPMENT (Internal)
- icp-identification (buyer profile definition)
- tam-builder (market size calculation)
- interview-me (client discovery)
- spec-driven-development (requirements capture)
- competitive-pricing-intel (pricing research)
- competitive-market-analysis (market positioning)

**Revenue service:** Intelligence Agent (£697/month)

---

### TIER 8: AGENT ARCHITECTURE & ENGINEERING
- memory-systems (cross-session state)
- multi-agent-patterns (CEO/sub-agent orchestration)
- context-compression (long session management)
- harness-engineering (autonomous agent design)
- filesystem-context (file-based memory)
- planning-and-task-breakdown (complex planning)

**Use case:** Internal agent development

---

### TIER 9: CODE & TECHNICAL (Internal)
- code-review-and-quality (quality gates)
- security-and-hardening (security audit)
- debugging-and-error-recovery (bug fixing)
- performance-optimization (speed improvements)
- frontend-ui-engineering (component building)
- git-workflow-and-versioning (git best practices)
- code-simplification (refactoring)
- vercel-deployment (deployment automation)
- airtable-automation (CRM automation)
- nextjs-best-practices (Next.js patterns)
- react-nextjs-development (React patterns)
- full-stack-orchestration (feature orchestration)
- senior-fullstack (architecture decisions)
- app-builder (rapid prototyping)

**Use case:** Internal development

---

### TIER 10: DESIGN & UI (Client-facing)
- pluggedin-design (unified design system - v4.0)
  - Absorbs: taste-skill, frontend-ui-engineering, huashu-design, soft-skill, brutalist-skill, minimalist-skill, gsap, css-animations, output-skill, accessibility-checklist, redesign-skill, and more
- dashboard (dashboard + demo generation)
- client-portal (portal interface)
- redesign-skill (existing UI improvements)
- baseline-ui (anti-slop enforcement)
- antigravity-design-expert (spatial/glassmorphism)
- canvas-design (data visualisation)

**Use case:** Client portal + dashboards

---

### TIER 11: RESEARCH & DISCOVERY (Internal)
- graphify (codebase knowledge graphs)
- skill-discovery (finding new skills)
- mistake-logging (capturing learnings)

**Use case:** Internal operations

---

## SKILLS NOT YET IN REGISTRY (ADD THESE)

- **Prompt Engineering** (mentioned by user, covers: prompt optimization, few-shot design, chain-of-thought patterns, role activation)
- **Context Engineering** (mentioned by user, deep prompt context optimization)
- **Email Marketing** (email-sequence skill exists, but not as standalone service)
- **SMS/WhatsApp Marketing** (multi-channel outreach)
- **Influencer Outreach** (finding + pitching influencers)
- **Review Removal** (reputation management)
- **AI Image Generation** (Flux integration for ad creatives)
- **Video Generation** (Creatomate + Remotion integration)
- **Affiliate Marketing** (partner program setup)

---

## CONSOLIDATION OPPORTUNITIES

**5 skills → 1 unified service** patterns:

| Service | Composite Skills | Revenue |
|---------|-----------------|---------|
| Full Outreach Campaign | lead-discovery → lead-enrichment → lead-qualification → outreach-engine → sales-pipeline | £1,497 |
| Competitor Analysis Bundle | competitor-intel → competitor-ad-intelligence → ad-angle-miner → trending-ad-hook-spotter | £597 |
| Content Creation Suite | content-asset-creator → content-brief-factory → campaign-brief-generator | £897 |
| Sales Enablement | sales-call-prep → sales-coaching → pipeline-review → battlecard-generator | £797 |
| Market Intelligence | industry-scanner → signal-detector → news-signal-outreach → competitor-intel | £697 |
| AI Agent Development | memory-systems → multi-agent-patterns → harness-engineering | £1,997 |

---

## NEXT: N8N WORKFLOW ORCHESTRATION

Create workflow templates that chain skills:
1. **Lead Gen Workflow** = discovery → enrichment → qualification → outreach
2. **Content Workflow** = strategy → creation → distribution → tracking
3. **Sales Workflow** = prospecting → coaching → closing
4. **Intelligence Workflow** = monitoring → analysis → reporting
5. **Custom Workflows** = client-specific skill combinations

Each workflow:
- Is a .json file
- Can be imported into n8n
- Triggers via webhook (from backend API)
- Returns results to Airtable
- Tracks execution in pipeline

---

**Status:** 50+ skills mapped. Ready to build n8n workflow templates.

Next: Build n8n workflows in `/workflows/` directory?
