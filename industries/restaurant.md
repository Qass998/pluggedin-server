# PluggedIN — Restaurant & Hospitality Industry Playbook
# Use for: restaurants, cafes, bars, pubs, takeaways,
#           catering, food trucks, hotel F&B

---

## THE 3 REAL PROBLEMS RESTAURANTS HAVE

1. RETENTION — Customers come once and never return.
   No system to bring them back. No loyalty. No win-back.

2. STOCK — Running out of ingredients without warning.
   Over-ordering and wasting margin. No supplier relationship automation.

3. REVIEWS — 1 bad review destroys a whole week's reputation.
   No system to respond, monitor, or flag removable reviews.

Everything else is noise. Lead with these three.

---

## BEST ENTRY MODULE

Module 9 — Customer Retention OS (£497/month)
→ WhatsApp loyalty stamps (replaces paper cards)
→ Churn detection (who hasn't come back in 30+ days)
→ Win-back campaigns (personalised WhatsApp offer)
→ Review monitoring + response drafting

Module 10 — Stock Intelligence (£297/month)
→ Stock level tracking per ingredient
→ Supplier alert when threshold reached
→ Auto-reorder email drafted
→ Days-remaining calculation

These two together = £794/month. Start here.

---

## TYPICAL ICP

- 1-3 location restaurant, café, or bar
- Owner-operator (often the chef or manager)
- 10-50 covers per session
- £15-40 average spend
- 2-8 staff
- No CRM — everything in their head
- Reviews on Google — checks them manually and emotionally
- Stock counted weekly at best

Decision maker: Owner or general manager
Pain: "We're always busy but never seem to make enough money"
Real problem: No retention system. Loyal customers drift away.

---

## ICP SCORE MULTIPLIERS

+15 pts: Multiple locations
+10 pts: Has Google reviews (especially negative ones)
+10 pts: Mentioned losing regulars
+10 pts: Currently no loyalty system
+5 pts: Has WhatsApp on their business number
+5 pts: Competitor nearby doing well

-10 pts: Chain/franchise (too much bureaucracy)
-10 pts: Tiny margins already (pubs in decline etc.)

---

## DEMO DATA (pre-load in Softr)

Business: "Olive & Spice Restaurant"
Location: Manchester
Customers in loyalty list: 847
Stamps issued this week: 234
Bookings today: 12
Reviews monitored: Google (4.2 stars, 3 recent)
Recent 1-star: "Service was slow on Friday evening"
At-risk customers (30+ days inactive): 127
Stock alert: Chicken thighs — 4 days remaining
Competitor: "Casa Bella opened on Church Street, dropped prices 10%"

CEO Briefing sample:
"SITUATION: 127 customers haven't visited in 30+ days.
Friday one-star review getting views. Stock alert: chicken thighs.
PRIORITY: Win-back campaign before weekend.
RECOMMENDATION: Push 20% Friday offer to 127 WhatsApp.
Expected uplift: 18-24 additional covers this week.
PROCEED?"

---

## MODULES PITCH ORDER

1. Retention OS + Stock Intel (entry — clear ROI)
2. Presence Agent (never miss a booking enquiry)
3. Marketing Agent (weekend social content auto-created)
4. Intelligence Agent (what's competitor doing this weekend?)
5. Data Intelligence (monthly board pack showing true profitability)

---

## OBJECTIONS SPECIFIC TO THIS INDUSTRY

"I don't have time to manage another system"
→ "You don't manage it. It runs. You get a WhatsApp every morning."

"My customers don't use WhatsApp loyalty"
→ "847 of your customers do. At [X restaurant] 91% opted in."

"We're full most weekends anyway"
→ "What about Tuesday and Wednesday? That's where the margin is."

"I already have a loyalty app"
→ "How many customers have it installed?
   WhatsApp has a 95% open rate. Apps have 11%."

---

## REVIEW REMOVAL UPSELL

After selling Retention OS, pitch review removal:
"You have 3 reviews that could be flagged for policy violation.
Want me to run a removal attempt? £175 for up to 3."

High close rate because:
- Owner is already emotionally invested in their reviews
- £175 feels small vs the damage one bad review does
- Immediate result they can see

---

## TECH NOTES

Loyalty stamps: WhatsApp via Twilio (retention_client.py)
Stock tracking: Airtable Stock table (stock_intel_client.py)
Review monitoring: Google Places API (retention_client.py)
Win-back: WhatsApp bulk send (retention_client.py)
Briefing: 7am WhatsApp via intake_processor.py

Demo portal: pluggedin.softr.app/demo/restaurant
Airtable base ID for demo: AIRTABLE_DEMO_BASE env var

---

## PRICING ANCHOR

"A part-time marketing assistant costs £800-1,200/month
and handles one thing. This handles everything — loyalty,
stock, reviews — for £497. And it never calls in sick."
