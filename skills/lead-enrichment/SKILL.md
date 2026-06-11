# Lead Enrichment Skill
# Deep multi-source enrichment: contacts + decision-maker + signals + accuracy
# Consolidated: web-scraper + ScrapeGraphAI + Vibe Prospecting + Apify + Signal Detection (June 2026)

## When to use this skill

**Triggers:**
- "Enrich leads with phone and email"
- "Get decision maker profiles"
- "Find what a prospect is interested in"
- "Pull contact info and activity signals"
- "Deep profile enrichment"
- "Maximize lead intelligence"

**Input:** Raw leads from lead-discovery (name, company, LinkedIn URL)
**Output:** Enriched leads with contact info, decision-maker score, activity signals, accuracy

---

## ENRICHMENT PIPELINE (6 Sources)

### Source 1: Official Business Registries (FREE)
**What it pulls:** Verified company info, registered officers, addresses, phone numbers, financials, filing history
**How:** Query government APIs directly (free, legal documents, automated via agent-browser)

**By country/region (all FREE):**

| Region | Registry | Data Provided | Tool | Cost |
|--------|----------|--------------|------|------|
| **UK** | Companies House API | Officer names, titles, addresses, filing history, accounts | agent-browser OR direct API | **Free** |
| **US** | SEC Edgar + SoS filings | C-suite names, registered agent, office addresses | agent-browser OR direct API | **Free** |
| **EU** | GLEIF (LEI) + National registries | Legal entity IDs, ownership, beneficial owners | agent-browser OR direct API | **Free** |
| **Australia** | ASIC database | Company officers, director details, reports | agent-browser OR direct API | **Free** |
| **Canada** | Corporations database | Officer names, business addresses, status | agent-browser OR direct API | **Free** |

**Example: Companies House via agent-browser**
```
agent-browser open companieshouse.gov.uk/search/companies
agent-browser fill @searchbox "Acme Corp Ltd"
agent-browser click @search-button
agent-browser snapshot                    # Get accessibility tree
# Extract: officer names, titles, addresses, phone from results
```

**Or direct REST API (also free):**
```
curl "https://api.company-information.service.gov.uk/company/12345678"
# Returns JSON with officers, addresses, filing history
```

**Output:**
```json
{
  "registered_address": "123 High Street, London, UK",
  "company_phone": "+44 20 7946 0958",
  "officers": [
    {"name": "Jane Smith", "title": "Director"},
    {"name": "John Doe", "title": "Secretary"}
  ],
  "company_status": "active",
  "accounts": {"revenue": "£2.5M", "employees": "45"}
}
```

**Cost:** **FREE** (government APIs)
**Speed:** 1-3 seconds per lookup
**Accuracy:** Extremely high (official legal documents)
**Decision-maker confidence:** Officers are verified legal signatories

---

### Source 2: Free Email + Contact Finders
**What it pulls:** Email addresses, phone numbers, social profiles
**How:** Use free tools + OSINT techniques (no paid API required)

| Tool | Coverage | Data | Cost | Method |
|------|----------|------|------|--------|
| **Hunter.io** | Global | Emails, verification status | **Free tier: 50/month** | Pattern matching |
| **Email-format.com** | Global | Email patterns by company | **Free** | Pattern detection |
| **Clearbit** | Global | Emails, social, profiles | **Free tier** | Database + API |
| **RocketReach** | Global | Limited free tier | **Free trial** | Database |
| **agent-browser + LinkedIn** | Global | Email/phone from LinkedIn profiles | **Free** | Web scraping |
| **Google Dorks + OSINT** | Global | Emails from company websites | **Free** | Pattern search |

**Free workflow (no paid tools):**
```
1. Get officer name from Companies House (free API)
   → "John Doe"
   
2. Guess email pattern (most companies use firstname.lastname@domain)
   → john.doe@acmecorp.com
   
3. Verify with Hunter.io free tier or email-format.com
   → Confidence: 75-85%
   
4. If not found, use agent-browser to scrape company website
   → Look at: /about, /team, /contact pages
   → Extract emails + phone numbers
   
5. Verify via LinkedIn (free, no API needed)
   → Check if person still works at company
   → Get last activity date
```

**Example: Free email discovery for "John Doe" at "Acme Corp Ltd"**
```
INPUT: name = "John Doe", company = "Acme Corp Ltd"

Step 1 - Pattern guess:
  Common patterns: john.doe@, jdoe@, j.doe@
  Domain: acmecorp.com
  Guesses: john.doe@acmecorp.com, jdoe@acmecorp.com

Step 2 - Hunter.io free lookup:
  curl "https://api.hunter.io/v2/email-finder?domain=acmecorp.com&first_name=John&last_name=Doe&limit=5"
  Result: john.doe@acmecorp.com (78% confidence)

Step 3 - agent-browser scrape company website:
  agent-browser open acmecorp.com/team
  agent-browser snapshot
  # Extract: "John Doe, VP Sales, john.doe@acmecorp.com, +44 20 7946 0958"

OUTPUT: {
  email: "john.doe@acmecorp.com",
  phone: "+44 20 7946 0958",
  confidence: 0.92,  # Multiple sources confirm
  sources: ["company_website", "hunter_io", "pattern_match"]
}
```

**Cost:** **FREE** (Hunter.io free tier + agent-browser)
**Speed:** 5-15 seconds per lookup (browser automation slower than APIs)
**Accuracy:** 85-92% (verified through multiple free sources)
**Decision-maker confidence:** High when multiple sources confirm

---

### Source 2: Website Scraping (ScrapeGraphAI)

---

### Source 2: Contact Enrichment (Vibe Prospecting MCP)
**What it pulls:** Email, phone, personal details, work history
**How:** B2B database lookup (name + company → contacts)

```
INPUT: {name: "John Doe", company: "Acme Corp", title: "VP Sales"}
↓
Vibe Prospecting MCP queries database
↓
OUTPUT: {
  email: "john.doe@acmecorp.com",
  phone: "+1 555 123 4567",
  mobile_phone: "+1 555 987 6543",
  linkedin: "linkedin.com/in/johndoe",
  personal_website: null,
  employment_history: [
    {company: "TechCorp", title: "Sales Manager", years: 2020-2024},
    {company: "StartupXYZ", title: "Sales Rep", years: 2018-2020}
  ],
  education: "MBA from Stanford",
  decision_maker: true,       // ← KEY SCORING
  decision_maker_reason: "VP level + sales authority"
}
```

**Cost:** $0.05-0.15 per contact (B2B database, accurate)
**Speed:** 2-5 sec per contact (batch: 1000 contacts in 1 min)
**Accuracy:** 85-95% (real B2B data)

---

### Source 3: LinkedIn Activity Signals (Apify LinkedIn Scraper)
**What it pulls:** Posts, comments, engagement, posting frequency, interests
**How:** Apify scrapes LinkedIn profile activity

```
INPUT: linkedin_url = "linkedin.com/in/johndoe"
↓
Apify LinkedIn_profile_scraper
↓
OUTPUT: {
  recent_posts: [
    "Just announced our new sales team expansion 🎉",
    "Excited to implement new CRM system at Acme",
    "3 tips for closing enterprise deals"
  ],
  comments: [
    "Commented on 'The Future of SaaS Pricing'",
    "Engaged with: 'B2B sales hiring trends'",
    "Reacted to: 'Salesforce best practices'"
  ],
  posting_frequency: "2-3 posts per week",
  engagement_rate: "high (avg 45 reactions per post)",
  followers: 3200,
  activity_30days: [
    {date: "2026-06-05", type: "post", topic: "sales"},
    {date: "2026-06-02", type: "comment", topic: "CRM"},
    {date: "2026-06-01", type: "reaction", topic: "hiring"}
  ]
}
```

**Cost:** $2-5 per 1000 profiles (cheap at scale)
**Speed:** 3-10 min per 1000 profiles
**Accuracy:** High (direct LinkedIn data)

---

### Source 4: Signal Detection (Hiring, Funding, News)
**What it pulls:** Recent company events = buying signals
**How:** Monitor job postings, funding announcements, news

```
INPUT: company = "Acme Corp"
↓
Signal Detection agents monitor:
  - New job postings (hiring = budget available, growth)
  - Funding announcements (capital = investment phase)
  - News articles (expansion, product launches)
  - Tech stack changes (implementing new tools)
↓
OUTPUT: {
  hiring_signals: {
    posted: "2026-06-03",
    roles: ["Sales Development Rep", "Account Executive", "Sales Manager"],
    count: 12,
    departments: ["sales", "engineering"],
    urgency: "high"
  },
  funding_signals: {
    series_a: "2025-10-15",
    amount: "$15M",
    investors: ["Sequoia", "Andressen Horowitz"],
    use_case: "expansion into EU + hiring"
  },
  news_signals: [
    "Acme launches AI-powered pricing engine",
    "Acme acquired 3-person team from competitor",
    "Acme announces partnership with Salesforce"
  ],
  intent_score: 85  // ← HIGH BUYING SIGNAL
}
```

**Cost:** Included in signal-detection skill (not separate)
**Speed:** Real-time monitoring
**Accuracy:** Medium-High (public signals)

---

## COMPLETE ENRICHED LEAD (All 4 sources)

```json
{
  "id": "lead_enriched_001",
  
  "contact": {
    "name": "John Doe",
    "title": "VP Sales",
    "company": "Acme Corp",
    "email": "john.doe@acmecorp.com",
    "phone": "+1 555 123 4567",
    "mobile": "+1 555 987 6543",
    "linkedin": "linkedin.com/in/johndoe",
    "location": "San Francisco, CA"
  },
  
  "decision_maker": {
    "score": 0.92,            // 0-1 scale
    "reason": "VP level + sales budget authority + 12+ years experience",
    "title_signals": ["VP", "Director", "Manager"],
    "seniority": "executive",
    "likely_budget_holder": true
  },
  
  "activity_signals": {
    "linkedin": {
      "posting_frequency": "2-3 posts/week",
      "engagement_rate": "high",
      "recent_topics": ["sales", "CRM", "hiring", "deal closing"],
      "followers": 3200,
      "days_since_post": 2
    },
    "company_hiring": {
      "posted": "2026-06-03",
      "roles": 12,
      "departments": ["sales", "engineering"],
      "signal_strength": "high"
    },
    "company_funding": {
      "series_a": "2025-10-15",
      "amount": "$15M",
      "signal_strength": "high"
    }
  },
  
  "enrichment_sources": {
    "website_scrape": {
      "source": "ScrapeGraphAI",
      "accuracy": 0.9,
      "pulled": ["org_structure", "leadership", "technologies"]
    },
    "contact_db": {
      "source": "Vibe Prospecting MCP",
      "accuracy": 0.95,
      "confidence": "high"
    },
    "linkedin_activity": {
      "source": "Apify LinkedIn_profile_scraper",
      "accuracy": 0.98,
      "coverage": "100%"
    },
    "signal_detection": {
      "source": "Signal Detection agents",
      "accuracy": 0.85,
      "real_time": true
    }
  },
  
  "accuracy_score": 0.945,  // ← TRUST METRIC (weighted avg)
  "enrichment_complete": "2026-06-07T10:45:00Z",
  "ready_for_outreach": true,
  "recommended_channel": ["email", "linkedin_message"],
  "timing": "immediate (high hiring + funding signals)"
}
```

---

## WORKFLOW: ENRICHING A BATCH OF LEADS (Free tools only + agent-browser)

### Phase 1: Registry Lookup via agent-browser (parallel, fast) — FREE
```
50 company names (UK = Companies House, US = SEC, etc)
  ↓
agent-browser automates registry navigation
  ↓
Extracts: officers, addresses, phone numbers, filing history
  ↓
Takes: 2-5 minutes (browser slower than API, but free)
Cost: **FREE** (government APIs)
```

### Phase 2: Email Discovery (parallel, medium) — FREE
```
50 leads with names + companies
  ↓
Pattern matching (firstname.lastname@domain) + Hunter.io free tier
  ↓
Candidate emails with confidence scores
  ↓
Takes: 1-3 minutes
Cost: **FREE** (Hunter.io free tier: 50/month)
```

### Phase 3: Website Scraping with agent-browser (parallel, medium) — FREE
```
50 leads + registry data
  ↓
agent-browser scrapes: /about, /team, /contact pages
  ↓
Extracts: org charts, additional officers, direct contact info
  ↓
Takes: 5-10 minutes
Cost: **FREE** (agent-browser is free/open source)
```

### Phase 4: Email Verification (parallel, very fast) — FREE
```
50 candidate emails
  ↓
Use email-format.com OR Hunter.io for pattern verification
  ↓
Confidence score: 75-92% per email
  ↓
Takes: 30-60 seconds
Cost: **FREE** (email-format.com is free)
```

### Phase 5: LinkedIn Activity via Apify (parallel, medium) — LOW COST
```
50 leads with LinkedIn URLs
  ↓
Apify LinkedIn_profile_scraper (batch mode)
  ↓
Posts, comments, engagement, frequency, interests
  ↓
Takes: 5-10 minutes
Cost: **$2.50** (50 × $0.05 averaged)
```

### Phase 6: Signal Detection (real-time, continuous) — FREE
```
50 companies
  ↓
Monitor for: hiring, funding, news, tech changes
  ↓
Score each company's "buying intent"
  ↓
Real-time (continuous)
Cost: **FREE** (included in system)
```

### Total for 50 leads (FREE + minimal cost):
- **Time:** 15-25 minutes
- **Cost:** ~$2.50-5 (only Apify LinkedIn, everything else free)
- **Cost per lead:** **$0.05-0.10** (vs $0.80-2.30 with paid tools)
- **Output:** 50 verified decision-makers with:
  - **Official company info:** Filing history, status, addresses (Companies House/SEC, free)
  - **Verified contact:** Phone + email from registries + website scraping (free)
  - **Email confidence:** 75-92% (Hunter.io free + pattern matching)
  - **LinkedIn activity + engagement:** Recent posts, comments (low-cost Apify)
  - **Buying intent signals:** Hiring, funding, news (free)
  - **Accuracy score:** 0.85-0.92 (backed by official records + website scraping)
  
**Free path with zero paid APIs:**
- Replace Apify LinkedIn with manual LinkedIn scraping via agent-browser
- Total cost: **$0** (completely free)
- Accuracy: still 0.85+, but slower (browser automation ~20-30min for 50 leads)

---

## DECISION-MAKER SCORING (How it works)

**Inputs:**
- Title (CEO, VP, Director, Manager = weights)
- Seniority (years in role, company size)
- Department (Sales, Marketing, Ops, Finance, Tech)
- Budget authority (VP level + sales dept = higher score)
- Activity (recent LinkedIn activity = engaged)
- Signals (hiring, funding = buying mode)

**Formula (simplified):**
```
Score = (title_weight × 0.3) + 
        (seniority_weight × 0.2) + 
        (activity_score × 0.2) + 
        (signal_strength × 0.3)

Result: 0-1 (0 = not a decision maker, 1 = confirmed buyer)
Threshold for outreach: > 0.7
```

**Example calculations:**
- CEO of $50M company + hiring signals = **0.98** (outreach immediately)
- VP Sales + recent posts about sales = **0.87** (outreach immediately)
- Marketing Manager + no activity + no signals = **0.45** (skip or warm up)
- Support Engineer + no signals = **0.15** (not a buyer)

---

## ACCURACY SCORING (How to trust the data)

Each enriched lead gets an **accuracy_score** (0-1):
- **0.95+** = High confidence (email/phone verified, multiple sources)
- **0.85-0.94** = Good (most data confirmed, minor gaps)
- **0.70-0.84** = Fair (useful but may have missing email/phone)
- **<0.70** = Low (use for research only, not outreach)

**How accuracy is calculated:**
```
accuracy = (email_verified × 0.3) +
           (phone_verified × 0.2) +
           (linkedin_active × 0.2) +
           (multiple_sources × 0.2) +
           (recency_score × 0.1)
```

**Trust rules:**
- Email + phone confirmed = outreach immediately
- Email only (no phone) = outreach, but lower expected response
- Phone only = risky (may be old), verify before calling
- Accuracy < 0.7 = don't use, go back to discovery for better leads

---

## NEXT: LEAD QUALIFICATION

Once enriched, pass to **lead-qualification** skill:
- Score fit to YOUR ICP (not just decision-maker ranking)
- Filter out: low-fit, wrong industry, no budget
- Keep: hot (perfect fit), warm (good fit), cold (long-term nurture)

```
enriched leads (contact + signals + decision-maker score)
        ↓
lead-qualification (YOUR ICP rules)
        ↓
hot/warm/cold labels
        ↓
outreach-engine (right message for each temperature)
```

---

## TOOLS REQUIRED (FREE-FIRST APPROACH)

**Free browser automation (PRIMARY):**
- ✅ **agent-browser** — Free, open source (Vercel Labs)
  - Installation: `npm install -g agent-browser && agent-browser install`
  - Use for: Registry navigation, website scraping, team page extraction
  - Speed: ~5-10 sec per company lookup
  - Cost: **FREE**

**Free registry APIs:**
- ✅ **Companies House API (UK)** — Free REST API
  - `https://api.company-information.service.gov.uk/`
  - No auth required for basic lookups
- ✅ **SEC Edgar (US)** — Free via EDGAR search
  - `https://www.sec.gov/edgar/`
  - agent-browser can automate the search
- ✅ **National registries (EU/AU/CA)** — Free government APIs

**Free email finding:**
- ✅ **Hunter.io free tier** — 50 free searches/month
  - Pattern detection + verification
- ✅ **email-format.com** — Free email pattern lookup
  - No API key needed, pure web lookup
- ✅ **agent-browser** — Can scrape company contact pages directly

**LinkedIn activity (optional, low-cost):**
- ✅ **Apify account** (for LinkedIn scraping) — $20-100/month OR skip for $0
  - If using: 50 lookups = ~$2.50
  - If skipping: Use agent-browser to scrape LinkedIn manually (slower, free)

**Signal detection (included):**
- ✅ **Signal Detection agents** — Real-time monitoring, **FREE**

**Configuration (minimal):**
- ✅ **API keys** in .env — HUNTER_API_KEY (optional, free tier)
- ✅ **If using Apify:** APIFY_TOKEN
- ✅ Everything else is FREE

---

## REGISTRY SELECTION BY REGION (Which to use when)

**UK-focused (your ICP is UK companies):**
1. **Start:** Companies House API (free, instant, verified officers)
2. **Depth:** Apollo.io or Hunter.io for direct contact details
3. **Confidence:** ~95%+ accuracy (backed by legal filings)

**US-focused (public companies):**
1. **Start:** SEC Edgar (free, instant, C-suite verified)
2. **Depth:** Apollo.io or RocketReach for all decision makers
3. **Confidence:** ~95%+ accuracy (backed by SEC filings)

**US-focused (private companies):**
1. **Start:** Apollo.io (comprehensive B2B database)
2. **Depth:** Hunter.io for email verification
3. **Add:** Crunchbase for startup/VC-backed companies (funding + investors)
4. **Confidence:** ~85-90% accuracy (aggregated data)

**EU-focused (global companies):**
1. **Start:** GLEIF (Global Legal Entity Identifier, free)
2. **Depth:** Apollo.io or Hunter.io
3. **Add:** National registries (Germany=Handelsregister, France=RCS, etc)
4. **Confidence:** ~90%+ accuracy (backed by national records)

**Multi-region / Australia / Canada:**
1. **Universal:** Apollo.io (covers all regions)
2. **Depth:** RocketReach for phone + email verification
3. **Confidence:** ~85-95% depending on region

**Cost vs. Accuracy tradeoff:**
```
Cheapest (£0-2 per lead):
  → Companies House (UK) + Apollo lite lookup

Balanced (£0.50-1 per lead):
  → Companies House + Apollo.io standard

Most thorough (£1-2 per lead):
  → Companies House + Apollo + Hunter + RocketReach
  → Cross-verification from 4 sources
  → Accuracy: 0.98+ (enterprise-grade)
```

---

## ANTI-PATTERNS

❌ **Don't enrich all 1000 leads at once.**
Cost balloons: 1000 × $0.25 = $250. Start with 50, test outreach response, then scale.

❌ **Don't ignore accuracy scores.**
A lead with 0.65 accuracy will bounce (bad email, old phone). Skip those.

❌ **Don't skip decision-maker scoring.**
You're wasting money on non-buyers. Filter to score > 0.7.

❌ **Don't assume old data is fresh.**
LinkedIn activity from 3 months ago = cold. Recent activity = engaged.

❌ **Don't use signals alone.**
Hiring + funding are good signs, but you still need valid contact info.

---

## VARIABLES

```env
# Registry + Directory APIs
COMPANIES_HOUSE_API_KEY=<free-or-paid>  # UK company data
APOLLO_API_KEY=<your-apollo-key>        # Global B2B contacts
HUNTER_API_KEY=<your-hunter-key>        # Email verification + domain search
ROCKETREACH_API_KEY=<your-rr-key>       # Phone + email + verified
CRUNCHBASE_API_KEY=<your-crunchbase>    # Funding + investor data (optional)

# Existing enrichment APIs
APIFY_API_TOKEN=<your-apify-key>
SCRAPEGRAPH_API_KEY=<your-scrapegraph-key>
VIBE_PROSPECTING_API_KEY=<your-vibe-key>

# Enrichment thresholds
DECISION_MAKER_THRESHOLD=0.70        # Only enrich if score > 70%
ACCURACY_THRESHOLD=0.75              # Only use leads if accuracy > 75%
SIGNAL_STRENGTH_THRESHOLD=0.60       # Only flag if signal confidence > 60%
BATCH_SIZE=50                        # Enrich 50 at a time (cost control)

# Registry lookup priority (by country)
REGISTRY_PRIORITY_UK="companies-house,apollo,hunter"
REGISTRY_PRIORITY_US="sec-edgar,apollo,rocketreach"
REGISTRY_PRIORITY_EU="gleif,apollo,hunter"
REGISTRY_PRIORITY_DEFAULT="apollo,hunter,crunchbase"
```

---

Last updated: June 7, 2026
