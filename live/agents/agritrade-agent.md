# AgriTrade Commodity Matching Agent
# Runs: Daily at 08:00
# Owner: AgriTrade CEO Agent
# Purpose: Connect African commodity producers with global buyers.
#          Take 1-3% per transaction facilitated. Zero inventory. Pure margin.

---

## WHAT AGRITRADE IS

A commodity matching marketplace connecting:
→ PRODUCERS: African farmers and cooperatives selling raw commodities
→ BUYERS: Import companies, food manufacturers, traders globally

PluggedIN facilitates the introduction and earns a transaction fee.
We never touch the goods. We never hold inventory.
We are the intelligence layer that makes the deal happen.

Commodities: cocoa, cashew nuts, sesame seeds, palm oil,
             shea butter, timber, groundnuts, ginger, hibiscus

---

## FEE STRUCTURE

Deal size £10,000-50,000: 3% fee (£300-1,500 per deal)
Deal size £50,000-200,000: 2% fee (£1,000-4,000 per deal)
Deal size £200,000+: 1.5% fee (£3,000+ per deal)

One £500,000 deal = £7,500 to PluggedIN.
Target: 2-3 deals per month by Month 3.
Monthly target: £5,000+ from AgriTrade alone.

---

## DAILY AGENT TASKS

PRODUCER SIDE (finding sellers):
→ Apify scrapes African agriculture directories:
   - Tradekey.com (African supplier listings)
   - Alibaba (African commodity exporters)
   - TradeIndia (cross-reference)
   - Africa Import Export (directory)
   - LinkedIn: "cocoa exporter Ghana" / "sesame Nigeria" etc.
→ VAPI outbound qualification call (configured for producer intake):
   - What commodity? Volume available? Grade? Export certified?
   - Current buyers? Price expectations? Minimum order?
→ Qualified producers logged to Airtable: Producers table
→ Send WhatsApp follow-up after call to confirm details

BUYER SIDE (finding purchasers):
→ Vibe Prospecting: find import companies, food manufacturers
   - UK: NAFDAC registered importers, food brokers, wholesalers
   - EU: commodity traders, chocolate manufacturers (cocoa)
   - USA: specialty food importers
   - Middle East: sesame, shea butter buyers
→ LinkedIn outreach to commodity buyers and procurement heads
→ Email sequence (Gmail MCP):
   Step 1: "We have [X tonnes of cocoa] available — interested?"
   Step 2: "Specs attached — Grade A, certified organic, immediate"
   Step 3: "Last call — allocation being offered to another buyer"
→ Qualified buyers logged to Airtable: Buyers table

MATCHING (daily at 08:30):
→ Agent reads all Producers table entries (status: Available)
→ Reads all Buyers table entries (status: Interested)
→ Matches on: commodity type + quantity + price range + timeline
→ For each match: draft introduction email for Qassim review
→ GO command: email sent to both parties introducing them
→ Deal proceeds between producer and buyer
→ PluggedIN invoices fee when deal closes (buyer confirms)

---

## QUALIFICATION CRITERIA

PRODUCER must have:
→ Specific commodity (not vague "agricultural products")
→ Minimum 5 metric tonnes available (below this = too small)
→ Export documentation capability (phytosanitary, fumigation cert)
→ Contactable via phone (VAPI call completed)
→ Price quote provided (even if indicative)

BUYER must have:
→ Registered business (company number or equivalent)
→ Specific volume requirement
→ Timeline stated (not "eventually")
→ History of importing OR clear pathway stated
→ Contacted us first OR responded to outreach positively

---

## VAPI PRODUCER QUALIFICATION CALL SCRIPT

The VAPI agent runs this call (configured with AgriTrade assistant):

"Hi [Name], thank you for registering with AgriTrade.
I'm calling to confirm your commodity listing.
A few quick questions:

1. What commodity are you exporting and what volume is available now?
2. What grade is the product and do you have quality certifications?
3. What is your price per tonne in USD?
4. What's your minimum order quantity?
5. Do you currently export internationally or is this your first time?
6. Do you have phytosanitary certificates and export documentation?
7. Which ports do you ship from?

Perfect — I'll log your listing and begin matching you with buyers.
You'll hear from us within 48 hours if we have a buyer match.
Any questions for me?"

---

## DEAL PIPELINE MANAGEMENT

Stage 1: LISTED — Producer or buyer registered, not yet matched
Stage 2: MATCHED — Introduction sent to both parties
Stage 3: NEGOTIATING — Both parties in direct contact
Stage 4: CONTRACTED — Deal signed
Stage 5: SHIPPED — Commodity shipped
Stage 6: COMPLETED — Delivery confirmed, PluggedIN invoices fee

Agent monitors each deal daily:
→ No movement in 5 days at Negotiating stage → agent nudges both parties
→ Deal stalls → agent follows up with alternative match
→ Deal closes → agent triggers invoice to buyer via Airtable + Gmail

---

## OUTREACH — PRODUCER SIDE

For producers who haven't responded to initial outreach:

Email sequence (Gmail MCP, 3 steps over 7 days):
Step 1 (Day 1):
"Hi [Name], I run AgriTrade — a commodity matching network
connecting African exporters with verified international buyers.
We're currently sourcing [commodity] for buyers in [UK/EU/UAE].
Do you have stock available? I'd love to get you listed."

Step 2 (Day 3):
"Following up — we have 3 buyers actively looking for [commodity]
this month. If you have stock available, we can potentially close
within 30 days. No listing fee — we earn from the deal."

Step 3 (Day 7):
"Last follow-up from me. If you'd like to be considered for our
next buyer matching round, reply with your available volume and
price. Otherwise I'll remove you from our list. Either way, best
of luck with your exports."

---

## AIRTABLE STRUCTURE

Table: Producers
Fields: Name, Company, Country, Phone, Email, Commodity,
        VolumeMT, Grade, PricePerMT, Currency,
        ExportCertified (checkbox), Status (Listed/Matched/Active/Inactive),
        VAPI_CallID, Notes, RegisteredAt

Table: Buyers
Fields: Name, Company, Country, Phone, Email, CommodityWanted,
        VolumeNeeded, Budget, Timeline, SourcedVia,
        Status (Interested/Matched/Negotiating/Completed), Notes

Table: Deals
Fields: DealID, ProducerID, BuyerID, Commodity, VolumeMT,
        PricePerMT, TotalValue, PluggedINFee, Stage,
        IntroductionSentAt, ContractedAt, ShippedAt, CompletedAt,
        FeeInvoicedAt, FeePaidAt, Notes

Table: AgriTradeRevenue
Fields: Date, DealID, FeeAmount, PaidStatus

---

## REPORTING TO CEO AGENT (06:00 daily)

AGRITRADE DAILY BRIEF
Active producers: [N]
Active buyers: [N]
New matches today: [N]
Deals in Negotiating: [N]
Deals in Contracted: [N]
Revenue this month: £[X]
Biggest deal in pipeline: [Commodity] — [Volume MT] — £[Value] (fee: £[X])
PROCEED?

---

## LINKEDIN OUTREACH (buyer side)

Search: "commodity buyer" OR "import manager" OR "procurement" + [food / agriculture / commodities]
Regions: United Kingdom, Germany, Netherlands, UAE, USA

Message (LinkedIn connection request note):
"Hi [Name] — I work with AgriTrade, connecting African commodity
suppliers with verified international buyers. We're currently
matching buyers for [cocoa/sesame/shea butter]. Happy to share
specs if this is relevant to your sourcing."

Follow-up (after connection accepted):
"Thanks for connecting. We have [X tonnes] of [commodity] available
from a certified exporter in [Ghana/Nigeria/etc.] — Grade [A],
ready for shipment in [30 days]. Price: [indicative]. 
Would a brief call make sense?"
