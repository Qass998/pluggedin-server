# PluggedIN — Business Onboarding SOP
# The definitive process for deploying an AI operating system
# into a real business with real departments.
# Version 1.0 | April 2026

---

## THE PROBLEM THIS SOLVES

A business is not one person with one job.
It has Sales, Marketing, Operations, Finance, Customer Service.
Each department has different people, different tools,
different workflows, different KPIs, and different breakdowns.

Agents can't run departments they don't understand.
This SOP is how we learn every department before agents go live.

---

## THE 4-SESSION ONBOARDING MODEL

Session 1 — OWNER BRAIN (Day 1, 30 min, VAPI call)
Session 2 — DEPARTMENT DEEP DIVE (Day 2-3, per department, Softr forms + VAPI)
Session 3 — TECH STACK AND DATA (Day 4, 45 min, VAPI or screen share)
Session 4 — AGENT HANDOVER (Day 5-7, Claude Code builds and deploys)

Total time from client: 2-3 hours across 5-7 days.
Total time from PluggedIN: fully automated after session configuration.

---

## SESSION 1 — OWNER BRAIN (Day 1)

**Who:** Owner / Managing Director
**How:** VAPI call (30 minutes)
**When:** Within 24 hours of signing

**What we capture:**
→ Business overview and how it actually operates today
→ Owner's role — what they do daily vs what they shouldn't do
→ The single biggest operational bottleneck
→ The single biggest growth constraint
→ What winning looks like in 90 days (specific numbers)
→ Who the key people are and what they own
→ What they're most afraid of (that they won't say in a sales call)

**VAPI script for Session 1:**

"Welcome to PluggedIN onboarding. This call takes about 30 minutes
and it's the most important call we'll have — because what you tell
me here shapes exactly how your AI system is built.

There are no wrong answers. The more honest you are about how
things actually work today — including the messy bits —
the better agents we build for you. Ready? Let's start.

1. Walk me through a typical day for you personally.
   What do you actually spend most of your time doing?

2. If you disappeared for a month, what would break first?

3. What's the thing that keeps coming back that you wish
   someone else could just handle permanently?

4. Who else is on your team? Tell me each person,
   their title, and what they actually own day to day.

5. In 90 days, if everything worked the way you wanted,
   what would be different? Give me a specific number —
   revenue, customers, time, whatever matters most to you.

6. What's the one thing your business does better than
   anyone else? And what's the one thing you know you're
   weak at compared to competitors?

7. Last question — what's the thing nobody has asked you about
   your business that if someone understood it,
   they'd understand everything?"

**Output:** Populated memory/personal/owner.md
            Populated memory/semantic/team.md (new file)
            Session 2 department list confirmed

---

## SESSION 2 — DEPARTMENT DEEP DIVE (Day 2-3)

**Who:** Department heads OR owner speaking for each area
**How:** Softr intake forms (async, owner fills at their pace)
         + optional 15-min VAPI follow-up per department
**When:** Day 2-3 after signing

**Departments captured (in order of module relevance):**

Priority 1 — always capture these:
→ Sales (how leads become customers)
→ Customer Service (how customers are managed after signing)
→ Operations (how the actual work gets delivered)

Priority 2 — capture if relevant module purchased:
→ Marketing (Module 3)
→ Finance / Admin (Module 6)
→ Stock / Supply Chain (Module 10)

**Each department form captures:**

WHO:
→ Who runs this department (name, role, contact)
→ How many people are in it
→ Who reports to whom

WHAT THEY DO DAY TO DAY:
→ Describe a typical day for this team
→ What does good look like (measurable)
→ What does bad look like (what triggers a bad week)

CURRENT PROCESS (workflow by workflow):
→ List every repeating task this team does
→ For each task: How often? How long? Who does it? What tool?

TOOLS THEY USE:
→ List every piece of software this team touches
→ For each: what do they use it for, how often, login details (optional)

WHERE IT BREAKS:
→ What takes longest that shouldn't
→ What gets dropped / missed most often
→ What do they spend time on that feels like a waste
→ What would they automate first if they could

KPIs THEY TRACK (or should track):
→ What numbers matter in this department
→ How are they tracked today
→ What's the current number vs what it should be

**Output per department:**
→ brain/departments/[dept].md populated
→ brain/workflows/[workflow-name].md per workflow identified
→ Draft SOP ready for agent configuration (brain/sops/[dept]-sop.md)

---

## SESSION 3 — TECH STACK AND DATA (Day 4)

**Who:** Owner or most technical person on team
**How:** VAPI call (45 min) or Softr form
**When:** Day 4 after signing

**What we capture:**

CURRENT SOFTWARE STACK:
→ CRM: what, how used, how many contacts, export possible?
→ Email: provider, lists size, sequences running?
→ Booking/scheduling: what system, how integrated?
→ Accounting: platform, who has access?
→ Social media: which platforms, who manages, posting frequency?
→ Analytics: Google Analytics? Any dashboard?
→ Communication: WhatsApp Business? Slack? Teams?
→ Any other tools (even basic ones — spreadsheets count)

DATA THAT EXISTS:
→ Customer database: how many contacts, where stored?
→ Lead history: any record of past leads and outcomes?
→ Sales data: revenue by month, by product, by customer?
→ Operational data: any performance metrics tracked?

INTEGRATION POINTS:
→ What tools connect to each other already?
→ What data transfer currently happens manually that shouldn't?
→ What report does someone build manually every week/month?

ACCOUNTS AND ACCESS:
→ Who currently has admin access to each tool?
→ Are there shared logins or individual accounts?
→ Any tools with API access already enabled?

**Output:**
→ memory/semantic/tech-stack.md populated
→ Integration map created (what connects to what)
→ Data migration plan if needed (old CRM → Airtable)
→ API keys and access documented in .env

---

## SESSION 4 — AGENT HANDOVER (Day 5-7)

**Who:** PluggedIN (Claude Code does this automatically)
**How:** Automated from all session data
**When:** Within 48 hours of Session 3

**What gets built:**

FOR EVERY MODULE PURCHASED:
→ Agent configured using department brain data
→ SOPs loaded into agent context
→ Workflows mapped to agent tasks
→ KPIs set as agent monitoring targets
→ Tools connected (CRM, booking, email, WhatsApp)
→ CEO Agent assigned and briefed on full business context

FOR THE CLIENT PORTAL (Softr):
→ Department views set up (staff see their area only)
→ Staff submission forms built per department
→ KPI dashboard showing their metrics
→ CEO Agent briefing visible to owner
→ Module status panel (active / locked)

STAFF TRAINING (async — no calls):
→ 3-minute Loom-style guide per department (Creatomate)
→ "How to submit updates" instruction doc sent via WhatsApp
→ Portal URL and login sent to each staff member
→ Clear rule: all updates go via portal — never call the owner

FIRST MORNING BRIEFING:
→ CEO Agent reads all department data
→ Generates first full briefing (all departments)
→ Delivered 7am Day 7 via WhatsApp
→ Owner replies GO — everything begins

**Output:**
→ All agents live and configured
→ Client portal active
→ Staff onboarded to portal
→ First briefing delivered
→ Onboarding marked complete in Airtable

---

## CLIENT FOLDER STRUCTURE (after full onboarding)

```
Clients/[BusinessName]/
├── CLAUDE.md                    ← AI brain for this client
├── .env                         ← Client API keys
├── brain/
│   ├── departments/
│   │   ├── sales.md             ← Sales department map
│   │   ├── marketing.md         ← Marketing department map
│   │   ├── operations.md        ← Operations department map
│   │   ├── customer-service.md  ← CS department map
│   │   └── finance.md           ← Finance/admin map
│   ├── workflows/
│   │   └── [workflow-name].md   ← One file per captured workflow
│   └── sops/
│       ├── sales-sop.md         ← Generated SOP for Sales agents
│       ├── marketing-sop.md     ← Generated SOP for Marketing agents
│       ├── operations-sop.md    ← Generated SOP for Ops agents
│       ├── customer-service-sop.md
│       └── finance-sop.md
├── memory/
│   ├── working/
│   │   ├── today.md             ← Active tasks and priority
│   │   └── pipeline.md          ← Live lead tracker
│   ├── semantic/
│   │   ├── customers.md         ← Customer intelligence
│   │   ├── products.md          ← Services and products
│   │   ├── team.md              ← Staff profiles and roles
│   │   └── tech-stack.md        ← All tools and integrations
│   ├── episodic/
│   │   └── log.md               ← Session history
│   └── personal/
│       └── owner.md             ← Owner profile, goals, style
├── lib/                         ← Client-specific scripts if needed
└── outputs/
    ├── leads/
    ├── reports/
    └── sequences/
```

---

## WHAT AGENTS READ BEFORE ACTING ON A DEPARTMENT

Before any agent takes action in a client's business, it reads:

1. Clients/[Name]/CLAUDE.md (business context)
2. Clients/[Name]/brain/departments/[dept].md (department map)
3. Clients/[Name]/brain/sops/[dept]-sop.md (how to operate)
4. Clients/[Name]/memory/working/today.md (current priorities)
5. Clients/[Name]/memory/semantic/customers.md (who they serve)

Without these files: agents act generically.
With these files: agents act like they've worked there for years.

---

## SOP GENERATION (automated)

After Session 2 data is captured, Claude Sonnet generates SOPs automatically.

Prompt template:
"You are building an AI operating system for [BusinessName].
Based on the department map below, generate a specific SOP
for AI agents operating in the [Department] department.

Include:
- What the agent is responsible for in this department
- What data it reads daily
- What actions it takes without approval
- What actions require owner approval
- How it handles exceptions
- What it reports and when
- KPIs it monitors and alert thresholds

Department map:
[department file contents]"

Output saved to: brain/sops/[dept]-sop.md
Reviewed by Qassim before agent deployment.

---

## ONBOARDING STATUS TRACKING (Airtable)

Table: OnboardingTracker
Fields:
- ClientName
- Session1Complete (checkbox + date)
- Session2DepartmentsComplete (text — which depts done)
- Session3Complete (checkbox + date)
- Session4Complete (checkbox + date)
- PortalLive (checkbox)
- StaffOnboarded (checkbox)
- FirstBriefingDelivered (checkbox + date)
- OnboardingCompleteAt (date)
- Notes
