# [BusinessName] — Customer Service SOP
# Generated from: brain/departments/customer-service.md
# Used by: Presence Agent, Retention OS Agent, Review Agent
# Version: 1.0 | [Date]

---

## WHAT THE CS AGENT OWNS

→ Every inbound call, WhatsApp, email, and DM acknowledged within 5 minutes
→ FAQ handling without human involvement
→ Booking confirmations and reminders
→ Proactive check-ins on active clients at set frequency
→ Review monitoring, response drafting, and flagging for removal
→ Win-back campaigns to lapsed customers
→ Churn detection and escalation to owner

---

## INBOUND HANDLING (by channel)

[Fill from customer-service.md — channels and hours]

PHONE (VAPI receptionist):
→ Answers every call 24/7
→ Handles: [list FAQs from cs.md]
→ Books appointments via Cal.com
→ Escalates: urgency / complaints / existing client issues
→ Out-of-hours: takes message + sends WhatsApp to client owner

WHATSAPP:
→ Auto-response within 2 minutes (business hours)
→ Out-of-hours: "Thanks for your message — [Name] will get back to you [time]"
→ FAQ answers: direct response
→ Booking requests: sends Cal.com link
→ Complaints: immediate acknowledgment + flag to owner

EMAIL:
→ Auto-acknowledgment within 5 minutes
→ FAQ answers drafted within 30 minutes (owner reviews if complex)
→ Complaints: acknowledged + owner flagged within 15 minutes

SOCIAL DMs:
→ Monitored every 4 hours
→ Standard FAQs answered directly
→ Everything else: "Thanks for reaching out! The best way to reach us is [channel]."

---

## FAQ BANK

[Fill from customer-service.md — top 5 questions and answers]

Q: [Question 1]
A: [Answer 1]

Q: [Question 2]
A: [Answer 2]

Q: [Question 3]
A: [Answer 3]

Q: [Question 4]
A: [Answer 4]

Q: [Question 5]
A: [Answer 5]

[Add more as captured from VAPI onboarding calls]

---

## COMPLAINT HANDLING PROTOCOL

Step 1: Acknowledge immediately (within 5 minutes of receipt)
   "Hi [Name], I'm really sorry to hear about this. I want to make it right.
   Can you give me a little more detail about what happened?"

Step 2: Log complaint to Airtable: Complaints table
   Fields: Customer name, date, channel, description, severity, status

Step 3: Flag to owner if severity = High (legal risk / refund request / public threat)
   Agent sends WhatsApp to owner: "COMPLAINT — [Customer] — [summary] — needs your input"

Step 4: If standard complaint (severity = Medium or Low):
   Agent drafts resolution response for owner approval
   Owner approves or adjusts, agent sends

Step 5: Resolution logged, follow-up sent 48hrs later
   "Hi [Name], just checking — is everything sorted to your satisfaction?"

---

## PROACTIVE CLIENT CHECK-INS

Frequency: [from cs.md — every X days]
Channel: [WhatsApp / email]

Template:
"Hi [Name], just a quick check-in from [Business].
How is everything going with [service/product]?
Anything we can improve or help with?"

If no response after 3 days: log as at-risk, flag to owner.
If negative response: move to complaint handling protocol.

---

## CHURN DETECTION

At-risk signals the agent monitors:
→ No contact in [X] days (from cs.md threshold)
→ Complaint lodged in last 30 days (unresolved)
→ Invoice overdue + no response (Finance SOP flags)
→ Reduced usage / engagement with portal

On detecting at-risk signal:
→ Log to Airtable: AtRisk table
→ Flag in CEO Agent daily brief
→ Send proactive WhatsApp within 24 hours
→ If no response in 48hrs: escalate to owner

Win-back (if already churned):
→ 30 days after last contact: personalised re-engagement message
→ 90 days: final outreach with offer

---

## REVIEW MANAGEMENT

Daily monitoring: Google, Trustpilot, Checkatrade (if applicable)

On NEW POSITIVE REVIEW (4-5 stars):
→ Draft response using retention_client.draft_review_response()
→ Auto-post response within 4 hours
→ Log review to ReviewLog table
→ Include in weekly CEO report

On NEW NEGATIVE REVIEW (1-3 stars):
→ Draft response (empathetic, solution-focused)
→ HOLD — flag to owner with draft
→ Owner reviews, adjusts, approves
→ Posted within 24 hours of receipt
→ If review may violate policy: flag for removal attempt

REMOVAL CANDIDATES:
→ Review from someone who is not a customer
→ Review containing false factual claims
→ Review from a competitor account
→ Review violating Google's content policy
→ Flag via: retention_client.flag_review_for_removal()

---

## DAILY REPORTING TO CEO AGENT

CS DAILY:
Open enquiries: [N]
Responded within SLA: [N] / [N total] — [%]
Complaints active: [N]
New reviews today: [positive: N, negative: N]
At-risk customers flagged: [N]
Win-back messages sent: [N]
Flagged for owner: [Y/N — what]
