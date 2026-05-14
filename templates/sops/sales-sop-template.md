# [BusinessName] — Sales Department SOP
# Generated from: brain/departments/sales.md
# Used by: Pipeline Agent, Sales Intelligence Agent
# Version: 1.0 | [Date]
# Status: [Draft / Approved / Live]

---

## WHAT THE SALES AGENT OWNS

The Sales Agent is responsible for:
→ Capturing every inbound lead the moment it arrives
→ Qualifying it against the ICP criteria below
→ Logging to Airtable pipeline immediately
→ Moving it through stages with appropriate follow-up
→ Alerting Qassim / owner when action is needed
→ Never letting a lead go cold without at least 3 touchpoints

The Sales Agent does NOT:
→ Send formal proposals (requires human approval)
→ Apply discounts
→ Make commitments on timelines or scope
→ Represent the business in a way that requires human judgment

---

## LEAD SOURCES AND CAPTURE

[Fill from sales.md — how leads come in, which channels]

For each source, the agent:

INBOUND (website / WhatsApp / phone):
→ Immediate acknowledgment sent within 5 minutes
→ Logged to Airtable: Pipeline table, Stage = "New"
→ Qualification sequence triggered (see below)

COLD OUTREACH (agent-generated):
→ Research target using Vibe / Apify before first contact
→ Personalised first message using copy-framework.md
→ Logged to Airtable: Pipeline table, Stage = "Outreach"
→ 3-step sequence runs (Day 1, Day 4, Day 8)

REFERRAL:
→ Log referral source against lead (for tracking)
→ Reference the referrer in first message
→ Move to qualification immediately (skip cold outreach sequence)

---

## IDEAL CUSTOMER PROFILE (ICP)

[Fill from memory/semantic/icp.md or scoring-criteria.md]

Qualifies as a lead (must have ALL of these):
→ [Industry / business type]
→ [Size: staff / revenue / location]
→ [Clear need expressed or inferred]
→ [Decision maker reachable]

Disqualifies as a lead (any one of these):
→ [Outside target geography]
→ [Wrong business type]
→ [Budget clearly mismatched]
→ [Already using a direct competitor under contract]

---

## QUALIFICATION SCORING

Score each lead 0-100 using scoring-criteria.md.
Agent logs score to Airtable immediately.

Score ≥ 80: Priority lead — owner notified same day
Score 60-79: Qualified — enter nurture sequence immediately
Score 40-59: Warm — monitor, light touch sequence
Score < 40: Unqualified — log and close (do not delete)

---

## PIPELINE STAGES AND AGENT ACTIONS

STAGE: NEW
Trigger: Lead received
Agent action: Acknowledge, log, score, assign stage
Human action: None (unless score ≥ 80)
SLA: Acknowledged within 5 minutes

STAGE: CONTACTED
Trigger: First message sent
Agent action: Log send time, set follow-up reminder Day 3
Human action: None
SLA: First contact within 2 hours of lead arriving

STAGE: ENGAGED
Trigger: Lead responds to any outreach
Agent action: Log response, draft follow-up, flag to owner if hot
Human action: Review and send draft if warm/hot
SLA: Response from agent within 1 hour of their reply

STAGE: MEETING BOOKED
Trigger: Cal.com booking confirmed
Agent action: Send confirmation, pre-meeting prep email, reminder Day -1
Human action: Attend the meeting
SLA: Confirmation within 5 minutes of booking

STAGE: PROPOSAL SENT
Trigger: Owner marks stage as Proposal (after meeting)
Agent action: Log date, set follow-up Day 3, Day 7, Day 14
Human action: Create and send proposal
SLA: Proposal chased at Day 3 if no response

STAGE: NEGOTIATING
Trigger: Lead responds to proposal
Agent action: Log, draft response, flag objections to owner
Human action: Handle objection, adjust proposal if needed
SLA: Agent surfaces objection type + recommended response within 1hr

STAGE: WON
Trigger: Owner marks deal closed
Agent action: Trigger onboarding sequence, update revenue log, notify CEO agent
Human action: Sign contract, begin dispatch
SLA: Onboarding confirmation to client within 2 hours of close

STAGE: LOST
Trigger: Owner marks deal lost
Agent action: Log reason, add to 90-day re-engagement list, ask for referral
Human action: None
SLA: Loss reason logged before moving on

---

## FOLLOW-UP SEQUENCES

Standard follow-up (if no response to outreach):
Day 1: First outreach
Day 4: Follow-up ("Just checking in — did you get a chance to look at this?")
Day 8: Final ("Last message from me — happy to help if timing is ever right")

Proposal follow-up (after proposal sent):
Day 3: "Just wanted to make sure the proposal came through — any questions?"
Day 7: "Following up — happy to jump on a quick call to walk through anything"
Day 14: "Final check — is this still on your radar or shall I close the file?"

Re-engagement (lost deals, 90 days later):
Single message: "Hi [Name] — reaching out as we've had a few updates since we last spoke.
Would it be worth a quick catch-up?"

---

## DAILY REPORTING TO CEO AGENT

Format (logged to Airtable by 18:00 daily):

SALES DAILY:
New leads today: [N]
Contacts made: [N]
Replies received: [N]
Meetings booked: [N]
Proposals outstanding: [N] (oldest: [X days])
Pipeline value: £[X]
Won this month: £[X] vs target £[X]
Flagged for owner: [Y/N — what]

---

## TOOLS USED

CRM: Airtable (Pipeline table in [ClientName] base)
Outreach: Gmail MCP (sequences)
Booking: Cal.com
Enrichment: lib/vibe_client.py
Research: lib/apify_client.py, lib/tinyfish_client.py
Scoring: scoring-criteria.md

---

## EXCEPTIONS AND ESCALATIONS

If a lead threatens to go to a competitor:
→ Flag to owner immediately (WhatsApp alert)
→ Draft retention message for owner to approve

If a lead reports a bad experience:
→ Flag to Customer Service SOP
→ Pause sales sequence until resolved

If lead asks a question agent cannot answer:
→ Respond: "Great question — let me get [Owner Name] to come back to you on that directly"
→ Flag to owner with full context
→ Owner responds within 2 hours (target)
