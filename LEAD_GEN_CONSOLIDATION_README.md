# Lead Generation Skills Consolidation
# Unified, consolidated system. Zero overlaps. June 2026.

---

## WHAT CHANGED

### Before (Scattered)
```
7 lead gen skills (overlap + confusion):
- apify-lead-generation
- apify-ultimate-scraper (same as above, different name)
- web-scraper (same as above, third name)
- cold-email
- email-sequence (what cold-email already does)
- linkedin-automation (posting, not prospecting)
- sales-automator (vague, unused)
+ open-outreach (pipeline patterns)
```

**Problem:** Confusing names, overlapping functionality, unclear which to use when.

---

### After (Unified)
```
5 consolidated skills + 1 signal:
- lead-discovery (Apify bulk prospecting, 55+ actors)
- lead-enrichment (ScrapeGraphAI + Vibe MCP + Apify + Signal detection)
- lead-qualification (ICP fit scoring, enhanced with Vibe)
- outreach-engine (Email + LinkedIn + WhatsApp sequences, unified)
- sales-pipeline (Booking, deal tracking, nurture)
- linkedin-presence (LinkedIn posting + profile optimization)
+ signal-detection (buying intent triggers)
```

**Benefit:** Clear names, clear purpose, clear layering. No more "which skill should I use?"

---

## SKILL LAYERS (How they work together)

```
Layer 1: DISCOVERY
  lead-discovery (Apify 55+ sources)
  ↓ produces: raw leads with name, company, LinkedIn URL
  ↓

Layer 2: ENRICHMENT
  lead-enrichment (ScrapeGraphAI + Vibe + LinkedIn signals + intent)
  ↓ produces: enriched leads with email, phone, decision-maker score, activity signals
  ↓

Layer 3: QUALIFICATION
  lead-qualification (ICP fit scoring + Vibe Prospecting)
  ↓ produces: hot/warm/cold scores, fit reasons
  ↓

Layer 4: OUTREACH
  outreach-engine (Email + LinkedIn + WhatsApp sequences)
  ↓ produces: sequences sent, opened, clicked, responded
  ↓

Layer 5: CONVERSION
  sales-pipeline (Booking, deal tracking, nurture)
  ↓ produces: meetings booked, deals tracked, nurture logs
  ↓

Layer 6: PRESENCE
  linkedin-presence (Posts, profile, content)
  ↓ produces: posts published, engagement metrics
  ↓

Layer 7: SIGNALS (Continuous monitoring)
  signal-detection (Hiring, funding, news)
  ↓ produces: intent alerts, buying signals
  ↓ feeds back to discovery (retry when signal detected)
```

---

## FILES & LOCATIONS

**New SKILL.md files:**
```
skills/lead-discovery/SKILL.md          ← 55+ Apify actors, platform selection
skills/lead-enrichment/SKILL.md         ← Multi-source: ScrapeGraphAI + Vibe + Apify + Signals
skills/outreach-engine/SKILL.md         ← Email + LinkedIn + WhatsApp unified
skills/sales-pipeline/SKILL.md          ← Booking, deals, nurture
skills/linkedin-presence/SKILL.md       ← Posts, profile, content
```

**Service definitions:**
```
services/SERVICES.md                    ← All service configs (Pipeline Agent, Presence Agent, etc)
templates/service-driven-portal-config.json ← Portal configuration template
```

**Updated registry:**
```
skills/registry.md                      ← Updated with new skill chains
graphify-out/ACTIVE_SKILLS.md           ← Updated skill index with consolidations
```

---

## KEY IMPROVEMENTS

### Consolidation 1: Discovery (3 → 1)
**Before:** apify-lead-generation + apify-ultimate-scraper + web-scraper
**After:** lead-discovery (unified, clear)
**Why:** All three do the same thing (find bulk leads). Apify is the actor-based solution.

### Consolidation 2: Enrichment (1 renamed, massively enhanced)
**Before:** web-scraper (just ScrapeGraphAI)
**After:** lead-enrichment (ScrapeGraphAI + Vibe MCP + Apify LinkedIn + Signal Detection)
**Why:** Maximum intelligence. You want: name + email + phone + decision-maker + signals + accuracy.

### Consolidation 3: Outreach (3 → 1)
**Before:** cold-email + email-sequence + open-outreach
**After:** outreach-engine (unified, multi-channel)
**Why:** All three are about sequences. Now includes email, LinkedIn, WhatsApp in one skill.

### Consolidation 4: Pipeline (1 renamed, clarified)
**Before:** sales-automator (vague)
**After:** sales-pipeline (booking, deal tracking, nurture)
**Why:** Clear name, clear purpose. Not "automation" but "pipeline management."

### Consolidation 5: Presence (1 renamed, focused)
**Before:** linkedin-automation (confusing — suggests lead prospecting)
**After:** linkedin-presence (posting, profile, engagement)
**Why:** Clear scope. This is for your brand, not for finding leads.

---

## DECISION-MAKER ENRICHMENT (New)

**New capability:** lead-enrichment now enriches with decision-maker scoring.

```
Input:  name, company, LinkedIn URL (raw lead)
        ↓
Process: 
  1. ScrapeGraphAI → org chart, who's the decision maker?
  2. Vibe MCP → email, phone, title level
  3. Apify LinkedIn → recent activity, engagement
  4. Signal Detection → hiring, funding, intent signals
        ↓
Output: {
  name, email, phone,
  decision_maker_score: 0.92,  ← NEW
  activity_signals: {...},     ← NEW
  accuracy_score: 0.95,
  sources: ["LinkedIn", "Vibe", "Company website", "Signal DB"]
}
```

**Why this matters:**
- You're not contacting the receptionist, you're contacting the buyer
- 92% accuracy means you can confidently call + email
- Activity signals mean they're engaged (not dormant)
- Accuracy scoring means you trust the data

---

## SKILL-TO-SERVICE MAPPING

Each **service** in the portal chains multiple **skills**:

```
Presence Agent (£797/month)
  ↓ Skills: VAPI, WhatsApp, Cal.com
  ↓ Result: 24/7 receptionist

Pipeline Agent (£997/month)
  ↓ Skills: lead-discovery → lead-enrichment → lead-qualification → outreach-engine → sales-pipeline
  ↓ Result: Full lead gen + sales pipeline automation

Conversion Agent (£897/month)
  ↓ Skills: lead-enrichment → lead-qualification → sales-pipeline
  ↓ Result: Website chat + auto-booking hot leads

Intelligence Agent (£697/month)
  ↓ Skills: signal-detection, competitor-intel, briefing
  ↓ Result: Weekly briefing + market signals

Marketing Agent (£1,197/month)
  ↓ Skills: competitor-intel, content-creator, linkedin-presence, Creatomate
  ↓ Result: Content + ads + social presence

Customer Retention OS (£497/month)
  ↓ Skills: lead-enrichment, sales-pipeline, signal-detection
  ↓ Result: Loyalty + churn detection + win-back

Sales Intelligence (£697/month)
  ↓ Skills: sales-pipeline, sales-coaching, performance-metrics
  ↓ Result: Call analysis + coaching + pipeline review

Data Intelligence (£897/month)
  ↓ Skills: airtable-automation, reporting, data-visualization
  ↓ Result: Monthly KPI reports + Remotion videos
```

---

## PORTAL ARCHITECTURE (Now config-driven)

**Before:** Hardcoded agents in SEGGUINÉE portal

```jsx
// Hard to change, hard to reuse
const agents = [
  {id: "briefing", name: "Chef de Cabinet", ...},
  {id: "analyste", name: "Analyste Stratégique", ...},
  // ... 7 more hardcoded
]
```

**After:** Service-driven configuration

```json
{
  "selected_services": ["presence-agent", "pipeline-agent", "intelligence-agent"],
  "service_overrides": {
    "presence-agent": {
      "name": "Chef de Cabinet",
      "french_name": "Chef de Cabinet (Réceptionniste)"
    }
  }
}
```

**Benefits:**
- Add a new service → just update the JSON config
- Reuse for new clients → copy config, change Airtable base ID
- No code changes → deployment is instant
- Services auto-load from services/SERVICES.md

---

## HOW TO USE THE NEW SYSTEM

### For a Cold Email Campaign:

```
1. Use lead-discovery
   → Find 100 prospects from LinkedIn
   
2. Use lead-enrichment
   → Get name, email, phone, decision-maker score, signals
   
3. Use lead-qualification
   → Score fit to your ICP
   
4. Filter for hot leads (score > 0.75)

5. Use outreach-engine
   → Generate 3-email sequence + LinkedIn follow-up
   
6. Use sales-pipeline
   → Track opens, clicks, responses
   → Book meetings on Cal.com
   → Track deals by stage
```

**Total time:** 2-3 weeks for first meetings
**Cost:** ~£100-200 in API calls
**Meetings booked:** ~15-30 (on 100 leads @ 2.5% response rate)

---

### For a Full Lead Gen Operation:

Use Pipeline Agent service:
```
✓ Discovers 200 leads/week (lead-discovery)
✓ Enriches with max detail (lead-enrichment)
✓ Qualifies fit (lead-qualification)
✓ Runs outreach sequences (outreach-engine)
✓ Tracks deals + books meetings (sales-pipeline)
✓ Monitors signals for re-engagement (signal-detection)
```

**Output:** 50-70 qualified leads/week, 10-15 meetings booked/week, pipeline growing

---

## TESTING CHECKLIST

- [ ] Read lead-discovery/SKILL.md — understand 55+ actors
- [ ] Read lead-enrichment/SKILL.md — understand multi-source enrichment + decision-maker scoring
- [ ] Read lead-qualification/SKILL.md — understand ICP fit scoring
- [ ] Read outreach-engine/SKILL.md — understand sequence timing + personalization
- [ ] Read sales-pipeline/SKILL.md — understand deal tracking + nurture
- [ ] Read linkedin-presence/SKILL.md — understand posting + engagement
- [ ] Review services/SERVICES.md — understand service composition
- [ ] Review templates/service-driven-portal-config.json — understand portal config structure
- [ ] Test SEGGUINÉE portal with new service system (if applicable)
- [ ] Verify all skills are callable from plan phase (via skills/registry.md)

---

## MIGRATION PATH (For existing clients)

If a client is currently using old skills (cold-email, email-sequence, etc):

```
OLD                              NEW
cold-email                  →    outreach-engine (part 1: email writing)
email-sequence              →    outreach-engine (part 2: sequences)
apify-lead-generation       →    lead-discovery
apify-ultimate-scraper      →    lead-discovery (same actor selection)
web-scraper                 →    lead-enrichment (ScrapeGraphAI layer)
sales-automator             →    sales-pipeline
linkedin-automation         →    linkedin-presence
```

**Action:** Update skills/registry.md to point to new skills. Code still works (new skills are compatible).

---

## VARIABLES & COST

**Per 100 leads:**
- Discovery (Apify): £2-5
- Enrichment (ScrapeGraphAI + Vibe): £12-15
- Enrichment (Apify LinkedIn): £2-5
- Total: ~£16-25 for fully enriched decision-makers

**Messaging sequences:**
- Email hosting: £0 (use Gmail)
- Email tracking: £0-10 (free tiers exist)
- Multi-channel (email + LinkedIn + WhatsApp): included

**Booking + CRM:**
- Cal.com: Free
- Airtable: Free tier (sufficient for 1000 records)

**Total cost per 100 fully-enriched leads:** ~£20-30
**Total cost per meeting booked:** ~£50-75 (assuming 2.5% response → 2-3 meetings per 100 leads)

---

## NEXT STEPS

1. **Update your prompt**: When users ask "find leads and enrich them," load `lead-discovery → lead-enrichment` (not old scattered skills)

2. **Update client portals**: Add service selection to their config (templates/service-driven-portal-config.json)

3. **Document for teams**: Share skills/registry.md + services/SERVICES.md with anyone implementing lead gen

4. **Build new portals**: Copy template, update service selection + Airtable base ID, deploy

---

## QUESTIONS?

- **Which skill for [task]?** → Check skills/registry.md (LEAD GENERATION section)
- **Which service includes [feature]?** → Check services/SERVICES.md
- **How to build a new portal?** → Copy templates/service-driven-portal-config.json, update service selections
- **How are leads enriched?** → See lead-enrichment/SKILL.md (4-source: ScrapeGraphAI, Vibe, Apify, Signals)

---

**Status:** ✅ Consolidated, documented, ready for implementation
**Last updated:** June 7, 2026
