# Lead Discovery Skill
# Bulk lead prospecting from 55+ Apify actors
# Consolidated: apify-lead-generation + apify-ultimate-scraper (June 2026)

## When to use this skill

**Triggers:**
- "Find leads from LinkedIn"
- "Scrape Google Maps for businesses"
- "Get Instagram influencer contacts"
- "Find contacts from TikTok"
- "Bulk prospect research"
- "Find all companies in X industry"
- "Get email/phone from business directory"

**Output:** Raw leads (name, title, company, platform, contact info)
**Does NOT:** Score fit, enrich with signals, write outreach
**Next step:** Pass to lead-enrichment for decision-maker + signal enrichment

---

## PLATFORM ACTORS (55+)

### Social Media & Communities
- **LinkedIn:** LinkedIn_profile_scraper, LinkedIn_company_scraper, LinkedIn_recruiter_scraper
- **Instagram:** Instagram_profile_scraper, Instagram_hashtag_followers
- **TikTok:** TikTok_user_followers, TikTok_trending_videos
- **Twitter/X:** Twitter_search, Twitter_followers

### Business & Commerce
- **Google Maps:** Google_Maps_scraper (businesses, reviews, contact)
- **Google Search:** Google_Search_results
- **Yellow Pages:** Yellow_Pages_business_scraper
- **Crunchbase:** Crunchbase_company_data

### Job Boards (hiring signals)
- **LinkedIn Jobs:** LinkedIn_job_listings
- **Indeed:** Indeed_job_scraper
- **Glassdoor:** Glassdoor_company_reviews

### News & Content
- **News sites:** Google_News_scraper
- **Product Hunt:** Product_Hunt_scraper
- **Reddit:** Reddit_subreddit_scraper

### Directories
- **Apollo.io:** Apollo_io_leads
- **Hunter.io:** Hunter_io_domain_search
- **Clearbit:** Clearbit_database

### Events & Communities
- **Luma:** Luma_events_attendees
- **Eventbrite:** Eventbrite_attendees

---

## WORKFLOW: HOW TO FIND LEADS

### Step 1: Identify the source
Ask yourself:
- Where do my target customers hang out?
- LinkedIn (if B2B professionals)
- Google Maps (if local businesses)
- Instagram (if visual/influencer brands)
- Job boards (if hiring = growth signal)

### Step 2: Select the actor
Match source to actor:
```
Source           → Actor
LinkedIn profiles  → LinkedIn_profile_scraper
Google Maps        → Google_Maps_scraper (+ reviews)
Instagram accounts → Instagram_profile_scraper
Job postings       → LinkedIn_job_listings
News articles      → Google_News_scraper
Company directory  → Crunchbase OR Yellow_Pages
```

### Step 3: Define search criteria
Provide to Apify:
- **Search term:** "VP Sales", "SaaS companies", "digital marketing agencies"
- **Location:** "New York", "UK", "Remote"
- **Industry:** "Technology", "Healthcare", "Finance"
- **Min size:** (for companies) "50+ employees"
- **Max pages:** 10 (200 results) to 100 (2,000 results)

### Step 4: Execute & collect
Apify returns:
```json
{
  "name": "John Doe",
  "title": "VP Sales",
  "company": "Acme Corp",
  "location": "San Francisco, CA",
  "linkedin_url": "linkedin.com/in/johndoe",
  "email": null,          // ← Often empty from discovery
  "phone": null,
  "source": "linkedin",
  "scraped_at": "2026-06-07T10:30:00Z"
}
```

### Step 5: Batch and pass to enrichment
Collect 50-1000 leads, then pass to **lead-enrichment** skill for:
- Email + phone lookup (Vibe Prospecting)
- Decision-maker scoring
- Activity signals (LinkedIn posts, comments, intent)
- Accuracy validation

---

## OUTPUT FORMAT

**Raw lead (from discovery):**
```json
[
  {
    "id": "lead_001",
    "name": "Sarah Chen",
    "title": "Chief Marketing Officer",
    "company": "TechVenture Inc",
    "location": "San Francisco, CA",
    "linkedin_url": "linkedin.com/in/sarahchen",
    "instagram_handle": "@sarahchen",
    "company_size": "150 employees",
    "company_industry": "Software Development",
    "source_actor": "LinkedIn_profile_scraper",
    "discovered_at": "2026-06-07T09:15:00Z"
  }
]
```

---

## ANTI-PATTERNS (don't do this)

❌ **Don't enrich in discovery phase.**
You're introducing delays. Discover first (fast batch), enrich second (slower).

❌ **Don't use Google_Search for LinkedIn profiles.**
LinkedIn_profile_scraper exists for a reason. Use the right actor.

❌ **Don't scrape without pagination.**
Setting max_pages=1 gets only 20 results. Go to 10-20 pages minimum for decent sample.

❌ **Don't mix platforms in one run.**
One actor per run. If you need LinkedIn + Google Maps, do two separate discoveries, then merge.

---

## COST & SPEED

| Actor | Cost | Speed | Accuracy |
|-------|------|-------|----------|
| LinkedIn_profile_scraper | $2-5 per 1000 | 5-10 min / 1000 | High (LinkedIn verified) |
| Google_Maps_scraper | $1-3 per 1000 | 3-5 min / 1000 | High (Maps verified) |
| Instagram_profile | $3-8 per 1000 | 8-15 min / 1000 | Medium (public data) |
| Google_News_scraper | $0.50-1 per 1000 | 2-3 min / 1000 | Medium (keywords) |
| Crunchbase | Custom | 5 min / 500 | High (curated) |

---

## NEXT: LEAD ENRICHMENT

Once you have 50+ raw leads, pass them to **lead-enrichment** skill:

```
lead-discovery output
        ↓
lead-enrichment (ScrapeGraphAI + Vibe MCP + Apify LinkedIn + Signal Detection)
        ↓
enriched leads with {name, email, phone, decision-maker score, signals, accuracy}
        ↓
lead-qualification (ICP fit scoring)
        ↓
outreach-engine (email/LinkedIn/WhatsApp sequences)
```

---

## VARIABLES

- `APIFY_API_TOKEN` — in .env (required for API calls)
- `APIFY_ACTOR_ID` — which actor to run (from table above)
- `MAX_PAGES` — pagination limit (10 = ~200 results, 100 = ~2000)
- `SEARCH_TERM` — what to search for
- `LOCATION` — optional geographic filter

---

## TIPS

1. **Start small:** Run 1-2 pages (20-40 leads) to test the search term
2. **Test your search:** "VP Sales" returns more precision than "Sales"
3. **Batch enrichment:** Once you have 100+ leads, enrich all at once (cheaper)
4. **Combine sources:** LinkedIn for roles, Google Maps for locations, Instagram for engaged audiences
5. **Track source:** Always log which actor found each lead (for analysis later)

---

Last updated: June 7, 2026
