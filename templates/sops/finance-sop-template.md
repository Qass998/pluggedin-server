# [BusinessName] — Finance & Admin SOP
# Generated from: brain/departments/finance.md
# Used by: Data Intelligence Agent (Module 6), KPI Agent, CEO Agent
# Version: 1.0 | [Date]

---

## WHAT THE FINANCE AGENT OWNS

→ Invoice triggered automatically on job completion
→ Payment chasing on overdue invoices (Day 7, 14, 30)
→ Weekly revenue summary in CEO briefing
→ Monthly financial snapshot (Remotion video + written report)
→ Upcoming deadline alerts (VAT, corporation tax, payroll)
→ Expense logging from staff portal submissions
→ Flagging cash flow risks before they become crises

---

## INVOICING WORKFLOW

Trigger: Operations Agent marks job complete
Agent action:

Step 1: Pull job details from Airtable (client name, job, amount, date)
Step 2: Generate invoice using [Xero / QuickBooks / template — from finance.md]
Step 3: Send to client via email + WhatsApp notification
   Email: "Hi [Name], please find attached invoice [INV-XXX] for [job].
           Payment is due by [date]. Thank you for your business."
Step 4: Log to InvoiceLog table in Airtable
   Fields: InvoiceID, Client, Amount, SentDate, DueDate, Status

Payment tracking:
→ Day 0 (sent): Status = Sent
→ Day [payment terms] + 1: Status = Overdue → trigger chase sequence
→ Day [payment terms] + 7: First chase message
→ Day [payment terms] + 14: Second chase (firmer tone)
→ Day [payment terms] + 30: Third chase + flag to owner
→ Owner decides: extend, write off, or formal debt collection

---

## PAYMENT CHASE TEMPLATES

Day 7 overdue:
"Hi [Name], just a quick reminder that invoice [INV-XXX]
for £[amount] was due on [date]. If you've already sent payment,
please ignore this — otherwise we'd appreciate settlement when convenient."

Day 14 overdue:
"Hi [Name], following up on invoice [INV-XXX] for £[amount],
now [X] days overdue. Please let us know if there's a query
on the invoice or if we can arrange a call to discuss."

Day 30 overdue:
"Hi [Name], this is our third follow-up on invoice [INV-XXX]
for £[amount]. If this is not resolved by [date + 7 days],
we will need to escalate this to our accounts team.
Please contact us urgently to resolve."
[Flag to owner — human decision required from here]

---

## EXPENSE PROCESSING

Source: Staff portal submissions (Softr)
Agent action on each submission:

If amount ≤ £[threshold from finance.md]:
→ Log to ExpenseLog table
→ Include in weekly financial summary
→ No approval needed

If amount > £[threshold]:
→ Log to ExpenseLog table
→ Flag to owner: "Expense submitted — [Name] — £[amount] — [category] — APPROVE?"
→ Owner replies GO or DECLINE
→ Agent updates status accordingly

---

## FINANCIAL REPORTING

WEEKLY (included in Monday CEO brief):
→ Revenue this week vs target
→ Revenue this month to date vs monthly target
→ Outstanding invoices: count + total value
→ Overdue invoices: count + oldest
→ Top expense this week

MONTHLY (1st of every month):
Remotion narrative video (60-90 seconds):
→ Revenue this month vs last month (bar chart)
→ Revenue vs target (percentage achieved)
→ Top 3 clients by revenue
→ Outstanding invoices summary
→ Next month projection

Written report (saved to outputs/reports/):
→ P&L summary (revenue - costs = profit)
→ Cash position
→ Pipeline value (from Sales Agent)
→ Decisions that affected financials this month
→ Recommendations for next month

---

## DEADLINE TRACKING

[Fill from finance.md — VAT dates, CT deadline, payroll dates]

Alert schedule per deadline:
→ 30 days before: "Heads up — [deadline] due on [date]. Action needed by [date]."
→ 14 days before: "Reminder — [deadline] in 14 days. Has this been prepared?"
→ 7 days before: "Urgent — [deadline] in 7 days. Please confirm status."
→ Day before: "CRITICAL — [deadline] tomorrow. Confirm completed."

---

## KPI MONITORING

Agent tracks daily (logged to Airtable: KPIs table):
→ Revenue today / this week / this month
→ Outstanding invoice total
→ Overdue invoice total
→ Cash position (if bank feed connected)
→ Month-on-month revenue change %

Alert thresholds:
→ Revenue tracking > 20% below monthly target at mid-month → flag to owner
→ Overdue invoices exceed £[threshold] → flag to owner
→ Cash position drops below £[buffer amount] → urgent flag to owner

---

## DAILY REPORTING TO CEO AGENT

FINANCE DAILY:
Revenue today: £[X]
Revenue this month: £[X] vs target £[X] ([%])
Invoices outstanding: [N] worth £[X]
Invoices overdue: [N] worth £[X] (oldest: [X days])
Expenses submitted today: [N] worth £[X]
Upcoming deadlines: [None / list]
Flagged for owner: [Y/N — what]
