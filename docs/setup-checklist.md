# PluggedIN — Setup Checklist
# What Qassim needs to do to go from files → operational agents.
# Work through this in order. Do not skip steps.

---

## PHASE 1 — FOUNDATION (do this today, takes 2-3 hours)

### 1.1 Fill the .env file

Open: ~/Documents/AI-Agency/PluggedIN/.env

Keys to fill (in priority order):

CRITICAL (nothing works without these):
→ ANTHROPIC_API_KEY — console.anthropic.com/settings/keys
→ AIRTABLE_TOKEN — airtable.com/create/tokens
   Scopes needed: data.records:read, data.records:write, schema.bases:read

HIGH PRIORITY (needed for first agents):
→ APIFY_TOKEN — console.apify.com/settings/integrations
→ VAPI_API_KEY — dashboard.vapi.ai/account
→ TWILIO_ACCOUNT_SID — console.twilio.com
→ TWILIO_AUTH_TOKEN — console.twilio.com
→ TWILIO_WHATSAPP_FROM — your Twilio WhatsApp sender number

NEEDED SOON:
→ TINYFISH_API_KEY — tinyfish.io/dashboard
→ VIBE_PROSPECTING_KEY — vibe.co/dashboard
→ CREATOMATE_API_KEY — creatomate.com/dashboard
→ CALCOM_API_KEY — cal.com/settings/developer/api-keys
→ GITHUB_TOKEN — github.com/settings/tokens (scope: public_repo)
→ OPENROUTER_API_KEY — openrouter.ai/keys

Add to .env:
→ QASSIM_PHONE=+447XXXXXXXXX (your WhatsApp number for briefings)
→ AIRTABLE_BASE_PLUGGEDIN=[base ID — created in step 1.2]

---

### 1.2 Create Airtable Bases and Tables

Go to: airtable.com → Create new base

BASE 1: "PluggedIN Live"
Create these tables with these fields:

TABLE: Opportunities
Fields: Name (text), Score (number), Source (text),
        SignalData (long text), MarginModel (text),
        Status (single select: Pending/Approved/Monitoring/Passed),
        DiscoveredAt (date), LaunchedAt (date), Notes (text)

TABLE: KnowledgeLog
Fields: Date (date), Source (text), Niche (text),
        InsightsExtracted (number), FilesUpdated (text),
        SkillGapFlagged (checkbox), OpportunityFlagged (checkbox)

TABLE: Leads
Fields: Vertical (text), Name (text), Phone (text), Email (text),
        Need (text), Urgency (text), Score (number),
        Status (single select: Qualified/Delivered/Rejected),
        BuyerID (text), DeliveredAt (date), Price (currency),
        Paid (checkbox), Notes (text)

TABLE: LeadBuyers
Fields: BusinessName (text), Contact (text), Phone (text),
        Email (text), Vertical (text), Region (text),
        PricePerLead (currency), ActiveStatus (checkbox),
        LeadsPurchased (number), TotalPaid (currency),
        LastDelivery (date)

TABLE: CEOReports
Fields: Domain (text), Business (text), Date (date),
        Summary (long text), Revenue (currency),
        LeadsFound (number), ActionsCompleted (number),
        Flags (long text), Status (text)

TABLE: RevenueLog
Fields: Date (date), Business (text), Source (text),
        Amount (currency), Type (text), Notes (text)

TABLE: Clients
Fields: DispatchID (text), ClientName (text), BusinessName (text),
        Industry (text), Phone (text), Email (text),
        ModulesPurchased (text), Package (text),
        MonthlyValue (currency), Status (text), SignedAt (date)

TABLE: Suppliers
Fields: Name (text), Email (text), Phone (text),
        Categories (text), RegionsServed (text),
        LeadTimeDays (number), MinimumOrder (currency),
        Status (text), ClientsServed (number)

TABLE: VendorLeads
Fields: Platform (text), ProductName (text), SupplierName (text),
        PriceRange (text), MOQ (text), Score (number),
        ScoreReasons (long text), Recommendation (text),
        URL (text), ScannedAt (date),
        Status (single select: New/Pursuing/Monitoring/Rejected/Converted)

TABLE: VendorOutreach
Fields: SupplierName (text), ContactEmail (email), PlayType (text),
        Product (text), EmailSubject (text),
        Status (single select: Sent/FollowUp1Sent/FollowUp2Sent/Replied/SupplierInterested/Negotiating/Rejected),
        SentAt (date), FollowUp1Due (date), FollowUp2Due (date),
        Notes (long text), UpdatedAt (date)


TABLE: DemandSignals
Fields: Country (text), Product (text), NeedDescription (long text),
        Urgency (single select: High/Medium/Low), Volume (text),
        BuyerType (text), TradeCategory (text),
        BrokeragePlay (checkbox), EcomPlay (checkbox),
        Source (text), DiscoveredAt (date), Status (text)

TABLE: BrokerageDeals
Fields: Product (text), BuyerCountry (text), BuyerCompany (text),
        BuyerContact (email), SupplierCountry (text), SupplierName (text),
        TradeCategory (text),
        DealStage (single select: Identified/SupplierFound/BuyerIdentified/OutreachSent/IntroMade/NDA_Signed/NegotiatingTerms/DealClosed/CommissionInvoiced/CommissionPaid/Failed),
        EstimatedValue (currency), EstimatedCommission (currency),
        CommissionPct (number), MatchScore (number),
        DemandUrgency (text), Notes (long text),
        DiscoveredAt (date), NextAction (text), NextActionDue (date),
        CommissionPaid (currency), UpdatedAt (date)

TABLE: EcomSourcingBriefs
Fields: Product (text), SearchTerms (text), SourcePlatform (text),
        ScanKeywords (text), TargetSellPrice (text), TargetSourcePrice (text),
        LaunchChannel (text), UniqueAngle (long text),
        Status (single select: New/Pending/Sourcing/Sampling/Launching/Live/Paused),
        CreatedAt (date)

TABLE: ProductOpportunities
Fields: Product (text), TotalScore (number), Tier (text), Action (text),
        MetaAdCount (number), TikTokShopRevenue (currency),
        BestAmazonBSR (number), GoogleTrendDirection (text),
        AvatarName (text), AgeRange (text),
        BuyingMotivation (long text), BestAdHook (long text), BestHeadline (text),
        Status (single select: New/InProgress/GTMReady/Live/Paused),
        DiscoveredAt (date)

TABLE: GTMBriefs
Fields: Product (text), TargetMarket (text), LaunchChannel (text),
        RecommendedAngle (long text), Differentiator (long text),
        MarketSaturation (text), WinningFormat (text),
        VideoHook (long text), StaticHeadline (text),
        SourcingPlatform (text), TargetMarginPct (number),
        Month3Target (text), NextActions (long text),
        Status (single select: Ready/InProgress/Live/Paused),
        CreatedAt (date)

TABLE: CreatorPipeline
Fields: Username (text), Platform (text), ProfileURL (url),
        Followers (number), Tier (text), EngagementRate (number),
        Niche (text), Product (text), HasEmail (checkbox), ContactMethod (text),
        OutreachStatus (single select: OutreachDrafted/OutreachSent/FollowupSent/FinalSent/Interested/ProductSent/Posted/CommissionEarned/Cold/Closed),
        OutreachType (text), RelevanceScore (number), Region (text),
        DiscoveredAt (date), NextAction (text), NextActionDue (date),
        PostURL (url), DiscountCode (text),
        SalesGenerated (number), CommissionOwed (currency)

TABLE: ManualDMQueue
Fields: Username (text), Platform (text), Product (text),
        MessageDraft (long text),
        Status (single select: Pending/Sent/NoResponse),
        CreatedAt (date)

TABLE: CreativeAssets
Fields: Product (text), StaticAdURLs (long text), VideoAdURL (url),
        VoiceoverPath (text), VoiceoverScript (long text),
        SparkAdRequests (number), DriveFolderURL (url),
        Status (single select: Produced/Live/Paused/Archived),
        ProducedAt (date)

TABLE: PostingCalendar
Fields: Brand (text), Product (text), PostDate (date), PostTime (text),
        Platform (single select: TikTok/Instagram/Pinterest/YouTube),
        ContentType (text), AssetURL (url), Caption (long text),
        Hashtags (long text), ProductURL (url),
        Status (single select: scheduled/posted/manual_needed/failed/skipped),
        PostedAt (date), PostID (text), CreatedAt (date)

TABLE: ContentMachines
Fields: Brand (text), Product (text),
        Status (single select: Active/Paused/Completed),
        PostsScheduled (number), PinterestStyleBrief (long text),
        HandDemoBrief (long text), LaunchedAt (date)

Once created: copy the Base ID from the URL
(airtable.com/[BASE_ID]/...)
Add to .env: AIRTABLE_BASE_PLUGGEDIN=[your base ID]

BASE 2: "Gromatic" (create when they sign)
Same structure as template — use dispatch_client.py to auto-create.

---

### 1.3 Install Python Dependencies

Open Terminal. Run:

```bash
cd ~/Documents/AI-Agency/PluggedIN
pip install -r requirements.txt --break-system-packages
pip install google-auth google-auth-httplib2 google-api-python-client cryptography --break-system-packages
```

---

### 1.3b Google Drive Setup (for creative asset storage)

**Step 1: Enable Drive API**
→ console.cloud.google.com → New Project "PluggedIN"
→ APIs & Services → Enable → search "Google Drive API" → Enable

**Step 2: Service Account**
→ APIs & Services → Credentials → Create Credentials → Service Account
→ Name it: "pluggedin-drive-agent"
→ Download JSON key → save to: ~/Documents/AI-Agency/PluggedIN/secrets/google_drive_sa.json

**Step 3: Create Drive folder**
→ drive.google.com → New Folder → name it "PluggedIN Creative"
→ Right-click → Share → paste the service account email (ends in @....iam.gserviceaccount.com)
→ Give it: Editor access

**Step 4: Get folder ID**
→ Open the "PluggedIN Creative" folder
→ Copy the ID from the URL: drive.google.com/drive/folders/[THIS_PART]
→ Paste into .env: GDRIVE_ROOT_FOLDER_ID=[paste here]

The agent will now auto-create subfolders per brand/product and save all creatives there.

---

### 1.3c Social Posting Setup (for organic content machine)

For each platform you want to post to, connect one at a time:

**TikTok** (primary):
→ developers.tiktok.com → Create App → Enable Content Posting API
→ Generate Access Token → paste into .env: TIKTOK_ACCESS_TOKEN

**Instagram** (secondary):
→ developers.facebook.com → My Apps → Create App → Business type
→ Add Instagram Graph API product
→ Connect your Instagram Business account
→ Generate User Access Token (60-day) → paste: INSTAGRAM_ACCESS_TOKEN
→ Get your Business Account ID → paste: INSTAGRAM_BUSINESS_ID

**Pinterest** (discovery):
→ developers.pinterest.com → Create App → Request API access
→ Generate OAuth token → paste: PINTEREST_ACCESS_TOKEN
→ Get a Board ID for product pins → paste: PINTEREST_DEFAULT_BOARD_ID

**Buffer (easiest fallback — start here)**:
→ buffer.com → Connect your TikTok + Instagram + Pinterest accounts
→ buffer.com/developers → Generate token → paste: BUFFER_ACCESS_TOKEN
→ Go to buffer.com/profiles → copy each profile ID into .env

If direct APIs aren't set up yet: the system logs posts to ManualDMQueue for manual upload.
Buffer is the recommended first step — easiest to connect, supports all platforms.

---

### 1.3d Creatomate Template Setup (for auto-rendered ads)

→ creatomate.com → Sign up → Templates → Create Template
→ You need these templates (create one at a time):

1. **static_product_1x1** — 1080x1080 image: ProductImage slot + Headline text + Subheadline + CTA
2. **static_product_9x16** — 1080x1920 image: same layout, vertical
3. **static_product_4x5** — 1080x1350 image: same layout, portrait
4. **video_product_showcase** — 15s video: ProductImage + animated text callouts + voiceover slot + CTA
5. **video_ugc_frame** — 30s video: CreatorClip slot + lower-third text + brand logo + CTA end card

For each template, copy the Template ID from the URL → paste into .env:
CREATOMATE_TMPL_STATIC_1X1=[id]
etc.

Creatomate has a free tier — 10 renders/month to test.

---

### 1.3e ElevenLabs Setup (for AI voiceover)

→ elevenlabs.io → Sign up → API → Copy API Key
→ Paste: ELEVENLABS_API_KEY=[key]

Free tier: 10,000 characters/month (~6-7 minutes of audio). Enough to test.
Default voices are pre-filled in .env — no configuration needed.

---

### 1.4 Confirm Apify MCP in Claude Code (VS Code)

Open VS Code terminal. Run:
```bash
claude mcp list
```

Should show: apify (connected)

If not connected, run:
```bash
claude mcp add apify --transport http https://mcp.apify.com \
  -H "Authorization: Bearer YOUR_APIFY_TOKEN"
```

---

### 1.5 Set Up Gmail MCP (for outreach sequences)

In VS Code terminal:
```bash
claude mcp add gmail
```

Follow the OAuth flow to connect your Gmail account.
This is what sends outreach emails for the Pipeline Agent.

---

## PHASE 2 — FIRST AGENT (do this week, takes 2-4 hours)

### 2.1 Test the Knowledge Agent (safest first)

This is the right first test because:
→ No money spent (reads free sources)
→ No outreach sent (read-only)
→ Proves the full stack works end-to-end

Run manually first:
```bash
cd ~/Documents/AI-Agency/PluggedIN
python orchestrator.py --agent knowledge --dry-run
```

What it should do:
1. Read live/agents/knowledge-agent.md
2. Use TinyFish to browse 3 sources
3. Extract insights with Claude Haiku
4. Write a row to Airtable:KnowledgeLog
5. Print summary to terminal

If this works: the full stack is operational.

---

### 2.2 Create VAPI Assistants

Go to: dashboard.vapi.ai

Create 4 assistants:

ASSISTANT 1: "PluggedIN Qualifier"
Purpose: Qualify inbound leads / cold calls
Model: claude-haiku-4-5-20251001
Voice: ElevenLabs Rachel (or similar professional voice)
System prompt: [From live/agents/lead-gen-agent.md qualification section]
Save the Assistant ID → add to .env: VAPI_QUALIFIER_ASSISTANT_ID

ASSISTANT 2: "PluggedIN Receptionist"
Purpose: 24/7 inbound for clients (Module 1)
Model: claude-haiku-4-5-20251001
Voice: ElevenLabs Rachel
Configured per client during onboarding
Save ID → VAPI_RECEPTIONIST_ASSISTANT_ID

ASSISTANT 3: "PluggedIN Onboarding"
Purpose: Session 1 VAPI onboarding call
Model: claude-sonnet-4-6
Voice: ElevenLabs professional voice
System prompt: [From templates/onboarding-sop.md Session 1 script]
Save ID → VAPI_ONBOARDING_ASSISTANT_ID

ASSISTANT 4: "AgriTrade Producer Qualifier"
Purpose: Qualify commodity producers
Model: claude-sonnet-4-6
System prompt: [From live/agents/agritrade-agent.md VAPI script]
Save ID → VAPI_AGRITRADE_ASSISTANT_ID

Also in VAPI:
→ Buy a UK phone number (+44)
→ Save the Phone Number ID → VAPI_PHONE_NUMBER_ID

---

### 2.3 Set Up Twilio WhatsApp

Go to: console.twilio.com

1. Create account / log in
2. Activate WhatsApp sandbox (for testing):
   → Messaging → Try it out → Send a WhatsApp
   → Send "join [keyword]" from your phone to Twilio number
3. For production: apply for WhatsApp Business API
   (takes 1-3 days, requires Facebook Business Manager)

Add to .env:
TWILIO_ACCOUNT_SID=ACxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxx
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886 (sandbox)
                 OR whatsapp:+44XXXXXXXXXX (your approved number)

Test it:
```python
from lib.retention_client import send_whatsapp
send_whatsapp("+447XXXXXXXXX", "PluggedIN test — stack is operational.")
```

---

## PHASE 3 — ORCHESTRATOR (end of week 1)

### 3.1 Set Up the Cron Job (Mac)

Open Terminal:
```bash
crontab -e
```

Add these lines:
```
# Intelligence phase (knowledge + opportunity engine + vendor scanner)
0 4 * * * cd ~/Documents/AI-Agency/PluggedIN && python orchestrator.py --phase intelligence >> ~/pluggedin-logs/daily.log 2>&1

# CEO agents compile domain reports
0 6 * * * cd ~/Documents/AI-Agency/PluggedIN && python orchestrator.py --phase ceo >> ~/pluggedin-logs/daily.log 2>&1

# Chief of All Chiefs synthesises + delivers WhatsApp briefing
0 7 * * * cd ~/Documents/AI-Agency/PluggedIN && python orchestrator.py --phase briefing >> ~/pluggedin-logs/daily.log 2>&1
```

Create log folder:
```bash
mkdir ~/pluggedin-logs
```

IMPORTANT: Mac must be awake for cron to run.
Set Mac to never sleep when plugged in:
System Settings → Battery → Prevent automatic sleeping when plugged in.

---

### 3.2 Test End-to-End (before going live)

Run the full daily routine manually once:
```bash
python orchestrator.py --phase all --dry-run
```

Dry run means: agents run but don't send emails or make calls.
Check: does Airtable get populated? Does the WhatsApp message
content look right? Are the numbers plausible?

When dry run looks good: run live for real.
```bash
python orchestrator.py --phase all
```

---

## PHASE 4 — CLIENTS (week 2, after Gromatic signs)

### 4.1 Send Gromatic Proposal (today — before anything else)

THIS IS THE ONLY TASK THAT MATTERS TODAY.
Everything above can wait. The proposal cannot.

Use the proposal template. Send it to Damian.
Every day without a signed client is a day with £0 MRR.

### 4.2 Once Gromatic Signs

```python
from lib.dispatch_client import dispatch_new_client
result = dispatch_new_client(
    client_name="Damian",
    business_name="Gromatic",
    industry="Lead Generation",
    phone="[Damian's phone]",
    email="[Damian's email]",
    modules_purchased=["Pipeline Agent"],
    package="Starter",
    monthly_value=797,
)
print(result["deployment_checklist"])
```

This creates the Airtable base, generates CLAUDE.md,
and produces the full deployment checklist.

### 4.3 Book Session 1 VAPI Call With Damian

Within 24 hours of signing.
Use lib/vapi_client.run_onboarding_call()
30 minutes. Captures his full business brain.

---

## PHASE 5 — SCALE (month 2+)

Once Gromatic is live and briefings are running:

→ Launch PlumbRight lead gen vertical (first PluggedIN Live revenue)
→ Launch Gumroad digital products store
→ Launch first YouTube channel (Health & Ingredients)
→ Pursue 3 more clients (restaurant, solicitor, construction)
→ Move orchestrator to VPS (£5/month Hetzner) for 24/7 reliability
→ Build Softr demo portal for sales meetings
→ Build GO command webhook (Twilio → Flask → execution)

---

## SUMMARY: WHAT QASSIM DOES VS WHAT AGENTS DO

QASSIM DOES (once, to set up):
→ Fill .env API keys (2 hours)
→ Create Airtable tables (1 hour)
→ Create VAPI assistants (1 hour)
→ Install Python dependencies (10 mins)
→ Set up cron job (10 mins)
→ Send Gromatic proposal (30 mins — TODAY)

QASSIM DOES (daily, forever):
→ Read WhatsApp briefing (5 mins)
→ Reply GO or DECISIONS (30 seconds)
→ Review decisions list if needed (10 mins)
→ Total: 15 minutes per day maximum

AGENTS DO (automatically, daily):
→ Everything else
