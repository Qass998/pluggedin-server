# [BusinessName] — Operations Department SOP
# Generated from: brain/departments/operations.md
# Used by: Presence Agent, Compliance Agent, CEO Agent
# Version: 1.0 | [Date]

---

## WHAT THE OPERATIONS AGENT OWNS

→ Tracking every active job / client / project from start to completion
→ Sending milestone updates to clients on schedule
→ Monitoring compliance deadlines across all staff and assets
→ Flagging capacity issues before they become problems
→ Generating daily Ops status for CEO Agent
→ Triggering close-out sequence (invoice + review request) on completion

---

## JOB LIFECYCLE MANAGEMENT

[Fill stages from operations.md workflow capture]

ON JOB CREATION (triggered by Sales marking deal Won):
→ Create job record in Airtable: Jobs table
→ Assign job owner (default: [Name from ops.md])
→ Set expected delivery date based on standard timeline
→ Send new job confirmation to client (WhatsApp + email)
→ Trigger setup checklist (see below)

SETUP CHECKLIST (automated, ticked off as done):
→ [ ] Client info complete in Airtable
→ [ ] Intake documents received
→ [ ] Job owner briefed
→ [ ] Tools / accounts set up for client
→ [ ] First delivery date confirmed with client

ACTIVE PHASE (weekly check-ins):
→ Every [X days]: automated client update message
   Format: "Hi [Name], quick update on [Job] — [status]. Next step: [X] by [date]."
→ Daily: job status logged by staff via portal
→ Weekly: CEO Agent reviews all active jobs — flags any at risk

COMPLETION TRIGGER:
→ Staff marks job complete via portal
→ Agent runs completion checklist:
   → Invoice sent (Finance SOP triggered)
   → Review request sent (24hr delay)
   → Satisfaction survey sent (48hr delay)
   → Client file updated to Complete in Airtable
   → Renewal reminder set for [X months]

---

## COMPLIANCE TRACKING

[Fill from operations.md compliance section]

Items tracked per client/staff/asset:
→ [List all certificate types, licence renewals, mandatory checks]

Alert schedule:
→ 30 days before expiry: first alert to owner via WhatsApp
→ 14 days before: second alert + recommended action
→ 7 days before: urgent alert + booking confirmation requested
→ Day of: critical alert if not resolved

Agent does NOT renew or book anything without approval.
Agent surfaces the deadline + recommended action + PROCEED?

---

## CAPACITY MONITORING

Maximum jobs in flight at once: [from ops.md]
Current utilisation: logged weekly to Airtable
Alert threshold: when at 80% capacity → flag to owner
Critical threshold: when at 100% → block new intake, escalate

Formula: Active jobs / Max capacity = utilisation %

---

## CLIENT COMMUNICATION SCHEDULE

[Customise frequency from ops.md]

Frequency: every [X] days for active jobs
Channel: [WhatsApp / email — from ops.md]
Tone: [professional / warm / casual — from owner.md]

Templates (adapt per client):
→ Progress update: "Hi [Name] — [business name] update: [status]. Next: [action] by [date]."
→ Issue flag: "Hi [Name] — we've hit a small delay on [item]. New timeline: [date]. Apologies for any inconvenience."
→ Completion: "Great news — [job] is complete. You'll receive [what] shortly."

---

## DAILY REPORTING TO CEO AGENT

OPERATIONS DAILY:
Active jobs: [N]
Jobs on track: [N]
Jobs at risk: [N] (reason: [brief])
Jobs completed today: [N]
Compliance items expiring in 30 days: [N]
Capacity utilisation: [%]
Flagged for owner: [Y/N — what]

---

## STAFF PORTAL RULES

Staff submit updates only via Softr portal. Never call owner.
Submission types handled automatically:
→ Job status update → logged to Airtable, CEO Agent reads it
→ Issue / blocker → flagged to owner with recommended action
→ Completion report → triggers completion checklist
→ Expense claim → Finance SOP triggered

Anything that doesn't fit a portal category:
→ Staff sends via WhatsApp to job owner (not to client owner)
→ Job owner resolves and logs outcome to portal
