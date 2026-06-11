# Client Onboarding Flow
# End-to-end setup from contract to agents running
# Version 1.0 | June 2026

---

## TIMELINE & PHASES

```
Day 1 — Contract signed
Day 2-3 — Discovery call + infrastructure setup
Day 4-7 — Agent configuration + testing
Day 8 — Agents live + monitoring begins
```

---

## PHASE 1: DISCOVERY (Day 1 - 30 min call)

**Who:** Client director + PluggedIN onboarding specialist

**Agenda:**
1. **ICP definition** (15 min)
   - Who's your ideal customer? (industry, size, geography, buying signals)
   - What problem do you solve?
   - What's the typical deal size?

2. **Current systems** (10 min)
   - Do you have HubSpot/Salesforce/Pipedrive/Airtable?
   - Which email do we send from?
   - Do you have a booking calendar (Cal.com)?
   - WhatsApp business account? (if Presence Agent selected)

3. **Agents to activate** (5 min)
   - Review service options
   - Confirm selected services (Pipeline, Presence, Intelligence, etc.)
   - Expected outcomes per agent

**Output:**
- Completed ICP profile (stored in PluggedIN)
- System integrations mapped
- Agents confirmed
- Next: infrastructure setup

---

## PHASE 2: INFRASTRUCTURE SETUP (Day 2-3)

### Step A: CRM Connection (1 hour)

**If client HAS HubSpot/Salesforce/Pipedrive:**
```
1. Client provides admin access (OAuth or API key)
2. PluggedIN validates connection (test read/write)
3. Map CRM tables:
   - Contacts → Leads table
   - Deals → Pipeline deals
   - Companies → Company table
   - Activities → Call logs + notes
4. Test sync (create test contact, verify appears)
5. Confirm ready
```

**If client HAS Airtable:**
```
1. Client shares Airtable base (via link)
2. PluggedIN reads structure (tables + fields)
3. Create PluggedIN-specific tables if needed:
   - Leads (discovered by agents)
   - Pipeline (deals tracked)
   - Outreach Log (email/LinkedIn activity)
   - Signals (buying intent)
   - Inbound (calls + messages from Presence)
4. Test sync
5. Confirm ready
```

**If client HAS NOTHING:**
```
1. Detect: "No CRM connected"
2. Offer: "We'll deploy a free CRM for you"
   ✓ Option A: Free Airtable base (we configure)
   ✓ Option B: Free Twenty instance (we host)
3. Client chooses
4. We provision (15 min)
5. Client gets login credentials
6. Client logs in, reviews setup
7. Confirm ready
```

### Step B: Email Connection (30 min)

**If Pipeline Agent selected:**
```
1. Client provides Gmail/Outlook credentials (OAuth)
2. Test: send test email from client account
3. Verify: client receives it
4. Set up email tracking (optional: Mailgun or Gmail API)
5. Configure: email signature + branding
6. Confirm ready
```

### Step C: Calendar Connection (15 min)

**If Presence Agent or Pipeline Agent selected:**
```
1. Client provides Cal.com access (OAuth or creates new)
2. Test: schedule test meeting
3. Verify: appears in client's calendar
4. Set availability: which hours can agents book?
5. Configure: time zone, buffer between meetings (30 min recommended)
6. Confirm ready
```

### Step D: WhatsApp Connection (30 min)

**If Presence Agent or outreach multi-channel selected:**
```
1. Client registers WhatsApp Business account (if not have)
2. PluggedIN registers as official partner
3. Test: send test WhatsApp message
4. Verify: client receives it
5. Configure: director phone number (for alerts)
6. Set up: auto-responses + escalation rules
7. Confirm ready
```

**Output (End of Phase 2):**
✓ CRM connected + tested
✓ Email configured + tested
✓ Calendar connected + tested
✓ WhatsApp connected + tested (if needed)
✓ All integrations documented
✓ Client credentials securely stored

---

## PHASE 3: AGENT CONFIGURATION (Day 4-7)

### For EACH agent selected:

#### PIPELINE AGENT Config (2 hours)

**Discovery Settings:**
```
1. Lead sources (which platforms?)
   ✓ LinkedIn (profiles matching job titles?)
   ✓ Google Maps (local businesses?)
   ✓ Industry directories?
   ✓ Company registries (Companies House, SEC)?
   
2. Lead discovery frequency?
   - Daily (5 am recommended)
   - Weekly (Monday)
   - Custom schedule
   
3. How many leads per week?
   - Small (50/week) = lower API spend
   - Medium (100/week) = balance
   - Large (200/week) = aggressive growth
```

**Enrichment Settings:**
```
1. Which enrichment sources?
   ✓ Registries (Companies House, SEC) — FREE
   ✓ Website scraping (ScrapeGraphAI) — £0.10/lead
   ✓ LinkedIn (Apify) — £0.05/lead
   ✓ Email finding (Hunter.io free tier)
   
2. Accuracy threshold?
   - Conservative (0.90+) = only high-confidence leads
   - Standard (0.85+) = most leads
   - Aggressive (0.80+) = all leads (more noise)
```

**Outreach Settings:**
```
1. Email sequence?
   ✓ 3-email touch (recommended)
   ✓ 5-email sequence (long nurture)
   ✓ LinkedIn only (B2B high-value)
   ✓ Multi-channel (email + LinkedIn + WhatsApp)
   
2. Timing?
   - Day 1: Email intro
   - Day 3: LinkedIn message
   - Day 7: Email follow-up 1
   - Day 14: Email follow-up 2
   (customizable)
   
3. Email subject lines + copy?
   - Use PluggedIN templates (tested)
   - Or provide custom (we use your voice)
   
4. LinkedIn messaging?
   - Automated connection request?
   - Personalized message after X days?
```

**Qualification Settings:**
```
1. ICP scoring rules
   - Industry fit? (weight: 25%)
   - Company size? (weight: 25%)
   - Decision-maker presence? (weight: 25%)
   - Buying signals (hiring/funding)? (weight: 25%)
   
2. Hot/Warm/Cold thresholds?
   - Hot (>0.75) = auto-book meeting
   - Warm (0.60-0.75) = email nurture
   - Cold (<0.60) = monitor for signals
```

**Booking Settings:**
```
1. Calendar sync? (which calendar?)
2. Meeting duration? (30 min recommended)
3. Time zone? (for correct scheduling)
4. Timezone buffer? (30 min between meetings)
5. Pre-meeting? (send brief + talking points?)
```

**Testing:**
```
1. Run pilot: discover 10 leads
2. Review: are they good fits?
3. Adjust: ICP rules if needed
4. Deploy: full agent activation
5. Monitor: first 2 weeks closely
```

---

#### PRESENCE AGENT Config (1 hour)

**Voice Settings:**
```
1. Greeting message?
   Default: "Hello, this is [company] speaking. How can I help?"
   Custom: provide your preferred greeting
   
2. Behavior?
   - Take detailed notes? (YES, always)
   - Transfer to human? (conditions)
   - Book directly? (conditions)
   
3. Which number?
   - Use existing?
   - PluggedIN assigns new?
   
4. Hours?
   - 24/7 (default)
   - Business hours only (which timezone?)
   - Custom schedule
```

**WhatsApp Settings:**
```
1. Auto-responses?
   - Immediate: "Thanks for contacting us..."
   - Qualify first: ask questions
   
2. Escalation?
   - Who gets urgent WhatsApp alerts?
   - What counts as urgent?
   - Frequency? (don't spam)
```

**Booking Settings:**
```
1. Auto-book conditions?
   - Hot leads? (YES)
   - All leads? (depends on business)
   
2. Calendar available?
   - Check with client
   - Set meeting buffer
   
3. Confirmation?
   - Send email + calendar invite
   - Send WhatsApp reminder (24h before)
```

**Testing:**
```
1. Call agent (test number provided)
2. Go through qualification flow
3. Request meeting booking
4. Verify: meeting appears in calendar
5. Deploy: live
```

---

#### INTELLIGENCE AGENT Config (30 min)

**Signals to Monitor:**
```
1. Which signals matter to you?
   ✓ Hiring (yes/no)
   ✓ Funding (yes/no)
   ✓ News (yes/no)
   ✓ Product launches (yes/no)
   ✓ Pricing changes (yes/no)
   ✓ Partnership announcements (yes/no)
   
2. Which competitors to watch?
   - List top 3-5 competitors
   - List target industries
```

**Briefing Settings:**
```
1. Format?
   ✓ Weekly video (Remotion, 2-3 min)
   ✓ Weekly text summary
   ✓ Daily alerts only (no weekly)
   
2. When?
   - Every Monday 6am?
   - Every Friday 4pm?
   - Custom day/time
   
3. Send to?
   - Client director email?
   - WhatsApp?
   - Slack? (if integrated)
   - All of above?
```

**Testing:**
```
1. Generate sample briefing
2. Client reviews (accurate? useful?)
3. Adjust: signals/frequency if needed
4. Deploy: live
```

---

#### OTHER AGENTS Config (15-30 min each)

**Marketing Agent:**
- Competitor accounts (Google Ads, Meta Ads, LinkedIn)
- Content topics (what to write about?)
- Ad budget (how much to spend?)

**Retention Agent:**
- Customer segmentation (how to identify loyalty members?)
- Churn indicators (what signals customer is leaving?)
- Loyalty rewards (what do you offer?)

**Sales Intelligence:**
- Team members (whose calls to track?)
- Success criteria (what's a good call?)
- Coaching focus (what to improve?)

**Data Intelligence:**
- KPIs to track (revenue, pipeline, conversion?)
- Reporting format (video, email, dashboard?)
- Frequency (weekly, monthly?)

---

## PHASE 4: TESTING & LAUNCH (Day 7-8)

### UAT (User Acceptance Testing)

```
1. For EACH agent:
   ✓ Run 1 test cycle end-to-end
   ✓ Verify outputs appear in CRM
   ✓ Check for data accuracy
   ✓ Confirm notifications work
   
2. Full system test:
   ✓ Test lead discovery → enrichment → outreach → booking flow
   ✓ Verify CRM sync works
   ✓ Check email tracking
   ✓ Confirm calendar updates
   ✓ Test WhatsApp alerts
   
3. Client sign-off:
   ✓ "Ready to go live?"
   ✓ Any adjustments needed?
   ✓ Final approval
```

### Launch

```
1. Agent activation (turn agents on)
2. Send launch notification (WhatsApp + email)
3. Monitor first 24h closely
   - Any errors?
   - Data flowing correctly?
   - CRM updates working?
4. Scale up gradually
   - Day 1: 10% of full volume
   - Day 2: 50% of full volume
   - Day 3: 100% full volume
```

---

## PHASE 5: HANDOFF & MONITORING (Day 8+)

### Handoff Call (30 min)

```
1. Walk through dashboard
   - Where to see leads
   - Where to see outreach metrics
   - Where to see pipeline
   
2. Quick wins (Day 1)
   - First leads discovered
   - First emails sent
   - First meeting booked (hopefully)
   
3. Weekly rhythm
   - When briefings arrive
   - How to read metrics
   - Where to submit feedback
   
4. Q&A + support
   - Slack channel for questions
   - Emergency hotline (WhatsApp)
   - Weekly check-in call (first month)
```

### Ongoing Monitoring

**Week 1-2:**
```
Daily check-in (5 min WhatsApp status)
- Leads discovered (count)
- Meetings booked (count)
- Any issues?
```

**Week 3-4:**
```
Weekly call (30 min)
- Results review
- Adjustments needed?
- Early wins + learnings
```

**Month 2+:**
```
Monthly strategy call (60 min)
- Performance review (vs. targets)
- Optimize agents (ICP, sequences, signals)
- Upsell opportunities (add more agents?)
```

---

## CHECKLIST: GO-LIVE READINESS

```
PRE-LAUNCH CHECKLIST:

CRM Integration:
  ☐ CRM connected (HubSpot/Salesforce/Airtable/Twenty)
  ☐ Tables/fields mapped correctly
  ☐ Test sync working (create contact, verify)
  ☐ Credentials securely stored

Email:
  ☐ Email account connected (Gmail/Outlook)
  ☐ Test email sent + received
  ☐ Email tracking configured
  ☐ Signature/branding added

Calendar:
  ☐ Cal.com connected
  ☐ Test meeting booked, verified
  ☐ Timezone correct
  ☐ Meeting buffer set (30 min)

WhatsApp (if needed):
  ☐ WhatsApp Business account active
  ☐ Test message sent + received
  ☐ Director phone number configured
  ☐ Escalation rules set

Agents Configured:
  ☐ Pipeline Agent: ICP, discovery settings, outreach sequences
  ☐ Presence Agent: greeting, booking rules, hours
  ☐ Intelligence Agent: signals, briefing frequency
  ☐ Other agents: their specific configs

Testing Complete:
  ☐ Each agent tested end-to-end
  ☐ Lead discovery works
  ☐ Email tracking works
  ☐ Calendar booking works
  ☐ CRM updates correct
  ☐ Client approves results

Ready for Live:
  ☐ All systems confirmed working
  ☐ Client sign-off received
  ☐ Launch call scheduled
  ☐ First monitoring period scheduled
  ☐ Support contacts shared
```

---

## SUPPORT & ESCALATION

**Slack Channel:** #[client-name]-support
**WhatsApp:** +[client-director-phone]
**Email:** support@pluggedin.io

**Response Times:**
- Critical issue (agents not running): 1 hour
- High priority (data not syncing): 4 hours
- Standard (question/optimization): 24 hours

---

**Typical Onboarding Time:** 7 days from contract to live agents
**Typical Setup Cost to Us:** £500-1000 (infrastructure + config)
**Typical Client Onboarding Effort:** 4-6 hours (over 8 days)

---

Last updated: June 8, 2026
