# Sales Pipeline Skill
# Deal tracking, booking, nurture sequences, stage automation
# Replaces: sales-automator (June 2026)

## When to use this skill

**Triggers:**
- "Book a meeting with this lead"
- "Track the sales pipeline"
- "Automate deal progression"
- "Set up nurture sequences"
- "Schedule follow-up calls"

**Input:** Interested leads (responded to outreach-engine)
**Output:** Booked meetings, tracked deals, automated nurture

---

## PIPELINE STAGES

```
Stage 1: INTEREST (they responded)
  → Send calendar link + brief
  → Wait for confirmation
  → Move to BOOKED

Stage 2: BOOKED (meeting scheduled)
  → Send meeting confirmation + context
  → Create call brief (company intel, what to ask)
  → Set pre-call reminder
  → Move to COMPLETED or NURTURE

Stage 3: COMPLETED (call happened)
  → Log call notes
  → Score outcome: next step?
  → If interested → PROPOSAL
  → If maybe later → NURTURE
  → If not interested → CLOSED

Stage 4: PROPOSAL (sent deal)
  → Track email open/click
  → Set follow-up reminder (3 days)
  → If no response → NURTURE
  → If accepted → WON

Stage 5: NURTURE (long-term follow-up)
  → Monthly value email
  → Alert on company signals (hiring, funding)
  → If signal detected → trigger outreach again
  → Goal: reactivate in 30-60-90 days

Stage 6: WON (closed deal)
  → Log revenue + deal size
  → Transition to onboarding
  → Log in revenue tracker

Stage 7: CLOSED (not a fit)
  → Log reason (budget, timing, etc)
  → Archive for future reference
```

---

## BOOKING INTEGRATION (Cal.com)

**When they want to meet:**

```
You: "Great! Here's my calendar: [cal.com/your-link]"
    ↓
They: Click link, pick time
    ↓
Cal.com: Automatically sends:
  - Confirmation email to them
  - Confirmation email to you
  - Calendar invite to both
  - Zoom/video link (auto-generated)
    ↓
Your system: Creates deal in Airtable
  - Lead record → deal record link
  - Meeting date/time
  - Stage: BOOKED
  - Auto-reminder: 1 day before call
```

---

## CALL BRIEF (Pre-call prep)

**Automatic call brief generated 24 hours before meeting:**

```
📋 CALL BRIEF: John Doe @ Acme Corp
Meeting: 2026-06-14 at 10:00 AM (30 min)

COMPANY INTEL:
- Size: 150 employees
- Funding: Series A $15M (Oct 2025)
- Recent hiring: 12 sales + engineering roles posted
- Latest news: Launched AI pricing engine (May 2026)

PERSON INTEL:
- Title: VP Sales
- Activity: 2-3 LinkedIn posts/week (sales, CRM, hiring)
- Decision maker score: 0.92 (high confidence)
- Employment history: 12 years in sales, VP roles

CALL AGENDA:
  1. Warm-up (2 min) — "Congrats on Series A"
  2. Situation (3 min) — "How are you thinking about sales ops?"
  3. Discovery (10 min) — "What's your current challenge with X?"
  4. Solution fit (10 min) — "Here's what we do for similar teams..."
  5. Next step (5 min) — "Timeline? Budget? Who else should be in?"

RISK FLAGS:
  - ⚠️ Just hired sales manager (may not want external tools)
  - ⚠️ Currently using Salesforce (competitor to our stack)
  ✓ Positive: Hiring aggressively (budget available)

MEETING LINK: [zoom-link-auto-generated]
```

---

## DEAL TRACKING (Airtable)

**Deals table schema:**
```
- deal_id (primary key)
- lead_id (link to Leads table)
- deal_name (company name + opportunity)
- stage (INTEREST, BOOKED, COMPLETED, PROPOSAL, NURTURE, WON, CLOSED)
- value ($)
- probability (% chance of close)
- close_date (expected)
- meeting_date
- call_notes
- next_action
- created_date
- updated_date
- owner (your name or team member)
```

**Track probability by stage:**
- INTEREST: 10%
- BOOKED: 15%
- COMPLETED (warm): 30-50%
- COMPLETED (cold): 5-15%
- PROPOSAL: 25-50%
- NURTURE: 5%
- WON: 100%
- CLOSED: 0%

**Weighted pipeline value:**
```
Pipeline value = (INTEREST × 0.1) + (BOOKED × 0.15) + (COMPLETED × 0.4) + (PROPOSAL × 0.35) + (NURTURE × 0.05)
```

Example: 10 COMPLETED calls with avg $10k deal:
- Expected value = 10 × $10k × 0.4 = **$40k** (realistic forecast)

---

## NURTURE SEQUENCES (If they say "maybe later")

**Month 1 (Week 2, 4, 6):**
```
Email 1: Value-first (useful content, no ask)
Email 2: Social proof (2 new case studies)
Email 3: Education (webinar link)
```

**Month 2-3 (Month 2 check-in):**
```
Email 4: Quick check-in ("Thought of you when...")
Email 5: Alert ("Company just hired 5 more sales reps — busy time!")
Email 6: New feature announcement
```

**Re-activation trigger:**
```
IF company signals detected (hiring, funding, news):
  → Send alert immediately
  → "Saw you're expanding — great timing"
  → Include relevant case study
  → Book another call
```

---

## AUTOMATION WORKFLOWS

**When deal moves to BOOKED:**
1. Send Cal.com confirmation
2. Create Airtable deal record
3. Generate call brief (auto-populated with company intel)
4. Schedule pre-call reminder (24 hrs before)
5. Schedule meeting recap reminder (30 min after)

**When call completed:**
1. Send meeting feedback form (auto-email)
2. Flag call summary area in Airtable for notes
3. If interested: auto-send proposal template
4. If "maybe": move to NURTURE, schedule re-engagement
5. Log timeline for deal analysis

**When proposal sent:**
1. Log send date
2. Track email open/click (via email tracking)
3. Set follow-up reminder (3 days, 7 days)
4. If no response after 10 days → nurture

---

## DEAL SCORING (Quick qualification on calls)

**During or after call, score:**

| Criteria | Score |
|----------|-------|
| Budget: "Yes, approved" | 3 points |
| Budget: "We need approval" | 1 point |
| Budget: "Budget tight now" | 0 points |
| Timeline: "This month" | 3 points |
| Timeline: "This quarter" | 2 points |
| Timeline: "Next year" | 0 points |
| Authority: "I decide" | 3 points |
| Authority: "Committee" | 1 point |
| Authority: "Not my decision" | 0 points |
| Fit: "Perfect fit" | 3 points |
| Fit: "Good fit" | 2 points |
| Fit: "Maybe" | 1 point |

**Total: 0-12 points**
- 10-12: HOT (push for close)
- 7-9: WARM (send proposal, nurture)
- 4-6: COOL (nurture, check in 60 days)
- 0-3: COLD (archive, check in 6 months)

---

## NEXT STEPS OPTIONS

**At end of call, offer:**

"Great conversation! Here's what I'm thinking:
1. I'll send over [proposal/case study] by EOD
2. How about we check in [timeline] to see if it's a fit?
3. In the meantime, if you have questions, just reply to that email"

**Possible outcomes:**
- ✅ "Yes, send proposal" → PROPOSAL stage
- ⏸️ "Let me talk to my team" → NURTURE (1 week check-in)
- ❌ "Not a fit" → CLOSED (log reason)
- 🤔 "Interesting, but timing not right" → NURTURE (3 month check-in)

---

## REPORTING

**Weekly pipeline report:**
```
Total pipeline value (weighted): $487k
- BOOKED: $45k (3 calls)
- COMPLETED: $180k (6 calls, avg 40% close)
- PROPOSAL: $200k (4 proposals, avg 35% close)
- NURTURE: $62k (12 leads, avg 5% close)

Stage progression (last week):
- Moved to BOOKED: 2 new
- Moved to COMPLETED: 1 call
- Moved to PROPOSAL: 1 deal
- Moved to WON: 0 deals
- Moved to CLOSED: 0 deals

Key metrics:
- Meetings scheduled: 3 (target: 2-3) ✓
- Show rate: 100% (target: 90%+) ✓
- Close rate so far: 0% (early stage)
- Avg deal size: $12.2k
- Sales cycle: 14-21 days (early, track longer)
```

---

## ANTI-PATTERNS

❌ **Don't book calls without call briefs.**
You'll show up unprepared. Prep is free — do it.

❌ **Don't drop leads after "maybe later".**
Nurture for 3-6 months. Most deals close with patience.

❌ **Don't ignore stage probabilities.**
If you say every deal is 50% likely, your forecast is useless.

❌ **Don't skip call notes.**
Future you (or team member) won't remember the context.

❌ **Don't schedule back-to-back calls without breaks.**
You'll be exhausted + make bad pitches. Space them out.

---

## TOOLS REQUIRED

- ✅ **Cal.com** (free, booking link) — integrates with your calendar
- ✅ **Airtable** (free tier ok) — deals + pipeline tracking
- ✅ **Zoom** (free) — video calls
- ✅ **Email tracking** (HubSpot free tier, Mailtrack) — track proposal opens
- ✅ **Meeting automation** (Zapier if needed) — trigger nurture emails

---

## VARIABLES (in Airtable)

```
DEAL_STAGES = ["INTEREST", "BOOKED", "COMPLETED", "PROPOSAL", "NURTURE", "WON", "CLOSED"]
PROBABILITY_BY_STAGE = {
  "INTEREST": 0.10,
  "BOOKED": 0.15,
  "COMPLETED": 0.40,
  "PROPOSAL": 0.35,
  "NURTURE": 0.05
}
DEAL_SCORING_THRESHOLD_HOT = 10
DEAL_SCORING_THRESHOLD_WARM = 7
NURTURE_INTERVAL_DAYS = 30
FOLLOW_UP_PROPOSAL_DAYS = 3
```

---

Last updated: June 7, 2026
