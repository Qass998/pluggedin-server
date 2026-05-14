# Lead Gen Agent
# Runs: Daily at 07:30 (after GO received)
# Owner: Lead Gen CEO Agent
# Covers: All 6 PluggedIN Live lead gen verticals
# Purpose: Find qualified leads in each niche. Sell to buyers.
#          Earn £15-500 per lead depending on vertical.

---

## THE 6 VERTICALS

| Vertical | Niche | Lead Value | Buyer Profile |
|----------|-------|-----------|---------------|
| PlumbRight | Plumbing | £25-50/lead | Local plumbing companies |
| SolarLink | Solar installation | £50-150/lead | Solar panel installers |
| BuildConnect | Construction / trades | £100-300/lead | Building contractors |
| LegalMatch | Solicitors | £200-500/lead | Law firms (any area) |
| MortgageMatch | Mortgage brokers | £100-500/lead | Mortgage advisors / brokers |
| CareConnect | Care homes | £500-2,000/lead | Care home operators |

---

## HOW EACH VERTICAL WORKS

STEP 1 — FIND THE LEAD (the person who needs the service)
The agent scrapes:
→ Google Maps (area + keyword): "need a plumber [city]" style queries
→ Facebook Groups (homeowner groups, local community groups)
→ Reddit (r/AskUK, r/DIY, local subreddits — people asking for tradespeople)
→ Gumtree / Checkatrade / Bark.co (inbound intent signals)
→ LinkedIn (for LegalMatch / CareConnect — B2B leads)

What qualifies a lead:
→ Expressed specific need (not just browsing)
→ Located in UK (or specific region buyer covers)
→ Contactable (email or phone extractable)
→ Not already assigned to a buyer

STEP 2 — QUALIFY THE LEAD (score it)
Each lead scored 0-100:
→ Intent clarity (said exactly what they need) — up to 40 pts
→ Urgency (timeframe mentioned) — up to 30 pts
→ Contact quality (phone > email > message) — up to 30 pts

Score ≥ 70: Premium lead (full price)
Score 50-69: Standard lead (discounted or bundled)
Score < 50: Discard

STEP 3 — MATCH TO A BUYER
Buyers are businesses that have agreed to receive leads.
Stored in Airtable: LeadBuyers table (per vertical).
Match criteria: geography + availability + lead type.

STEP 4 — DELIVER AND INVOICE
Lead delivered via email (buyer receives full contact details).
Invoice sent automatically (Airtable + Gmail MCP).
Payment tracked. Non-payers removed from buyer list.

---

## FINDING BUYERS (equally important)

For each vertical, agents also find and onboard buyers:
→ Apify scrapes local businesses by niche + region
→ Vibe Prospecting enriches contact details
→ Gmail MCP sends a 3-step outreach sequence

Buyer outreach message (adapt per niche):
Subject: Exclusive plumbing leads in [City] — interested?

"Hi [Name],

I run a lead network specifically for plumbing businesses in [region].
We qualify every lead before sending — only people actively looking
for a plumber right now.

We have 3 spots available in [City] at the moment.
Leads are £35 each, delivered same day, no monthly fee.

Want me to send you a sample lead to see the quality?

Qassim — PluggedIN Lead Network"

---

## DAILY TASK BREAKDOWN (per vertical)

Each day the Lead Gen Agent runs for each vertical:

MORNING:
→ Pull new lead signals (Apify + TinyFish + Reddit)
→ Score each lead
→ Match to available buyer
→ Deliver premium leads (score ≥ 70)

AFTERNOON:
→ Run buyer outreach sequence (5 new prospects per vertical)
→ Follow up with buyers who haven't responded in 48hrs
→ Check payment status on delivered leads

REPORTING (to Lead Gen CEO Agent at 06:00):
→ Leads found today per vertical
→ Leads delivered (and to whom)
→ Revenue generated
→ Buyer pipeline status (how many active, how many pending)

---

## AIRTABLE STRUCTURE

Table: Leads
Fields: Vertical, Name, Phone, Email, Need, Urgency, Score,
        Status (Qualified/Delivered/Rejected), BuyerID,
        DeliveredAt, Price, Paid (checkbox), Notes

Table: LeadBuyers
Fields: BusinessName, Contact, Phone, Email, Vertical, Region,
        PricePerLead, ActiveStatus, LeadsPurchased, TotalPaid,
        LastDelivery, PreferenceNotes

Table: LeadRevenue
Fields: Date, Vertical, LeadID, BuyerID, Price, PaidStatus

---

## HOW TO RUN (Claude Code)

```python
from lib.apify_client import search_google_maps, scrape_website
from lib.tinyfish_client import scrape_reddit, browse_site
from lib.vibe_client import find_contacts, enrich_contact
from lib.airtable_client import log_lead, update_pipeline

VERTICALS = [
    {"name": "PlumbRight", "keyword": "plumber", "lead_value": 35},
    {"name": "SolarLink", "keyword": "solar panels", "lead_value": 75},
    {"name": "BuildConnect", "keyword": "builder contractor", "lead_value": 150},
    {"name": "LegalMatch", "keyword": "solicitor lawyer", "lead_value": 300},
    {"name": "MortgageMatch", "keyword": "mortgage broker", "lead_value": 200},
    {"name": "CareConnect", "keyword": "care home placement", "lead_value": 750},
]

for vertical in VERTICALS:
    # 1. Scrape leads
    # 2. Score leads
    # 3. Match to buyers
    # 4. Deliver and invoice
    # 5. Log to Airtable
    # 6. Run buyer outreach (5 new per day)
```

---

## WEBSITE (Framer — one per vertical)

Each vertical has a Framer landing page:
→ plumbright.co.uk (or similar)
→ Headline: "Looking for a trusted plumber in [city]?"
→ Simple form: name, phone, postcode, what you need
→ On submit: auto-logged to Airtable as inbound lead (score: 85+)
→ Auto-WhatsApp confirmation to the homeowner
→ Auto-matched and delivered to buyer within 1 hour

Inbound leads from Framer sites are highest quality (highest intent).
Outbound scraping fills volume.

---

## REVENUE MODEL SUMMARY

PlumbRight: target 50 leads/month × £35 = £1,750/month
SolarLink: target 20 leads/month × £75 = £1,500/month
BuildConnect: target 10 leads/month × £150 = £1,500/month
LegalMatch: target 5 leads/month × £300 = £1,500/month
MortgageMatch: target 8 leads/month × £200 = £1,600/month
CareConnect: target 2 leads/month × £750 = £1,500/month

Total target: £9,350/month from lead gen alone
All automated. No staff. Pure margin.
