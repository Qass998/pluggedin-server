# PluggedIN Dashboard Skill
# Works in Claude Code, Cursor, any agent — NO Cowork required
#
# DEPENDS ON (load these skills first if available):
#   skills/huashu-design/SKILL.md  — visual design system (20 philosophies)
#
# If huashu-design skill is loaded: use its design philosophies for all visual output.
# If not loaded: fall back to the Design System section below.
#
# HOW TO INSTALL HUASHU DESIGN (run once in terminal):
#   mkdir -p ~/Documents/AI-Agency/PluggedIN/skills/huashu-design
#   curl -L https://raw.githubusercontent.com/alchaincyf/huashu-design/master/SKILL.md \
#     -o ~/Documents/AI-Agency/PluggedIN/skills/huashu-design/SKILL.md
#
# Paired with: Airtable REST API, Chart.js, Remotion (optional)
#
# TRIGGER PHRASES:
# "build a dashboard for [client/industry]"
# "generate a demo for [industry]"
# "create a KPI tracker for [client]"
# "show me the [module] dashboard"
# "build a client demo"

---

## WHAT THIS SKILL DOES

Generates a beautiful, standalone HTML dashboard that:
- Connects directly to Airtable via REST API (no Cowork needed)
- Uses demo data from industry playbooks when no live data exists
- Applies professional design principles (see Design System below)
- Works as a sales demo tool OR a live client portal
- Outputs a single self-contained HTML file — open in browser, share via link, host on Netlify

---

## STEP 1 — GATHER CONTEXT

Before writing any code, ask or infer:

```
1. MODE: "demo" (fake data, for sales calls) OR "live" (real Airtable data)
2. INDUSTRY: construction / legal / healthcare / restaurant / logistics / other
3. CLIENT NAME: e.g. "Harland Construction" or "Gromatic"
4. MODULES: which of the 10 modules did they buy? (or show all for demo)
5. OUTPUT: file path to save the HTML
```

If MODE is not specified: default to "demo"
If INDUSTRY is not specified: ask
If CLIENT NAME is not specified: use the industry demo business name from playbook

---

## STEP 2 — LOAD INDUSTRY DATA

### For DEMO mode — read the industry playbook:
```
industries/construction.md  → use "Harland Construction, Sheffield"
industries/legal.md         → use the legal demo firm
industries/healthcare.md    → use the healthcare demo practice
industries/restaurant.md    → use the restaurant demo business
industries/logistics.md     → use the logistics demo company
```

Extract from the playbook's DEMO DATA section:
- Business name, location
- Key metrics (leads, pipeline value, alerts)
- CEO Briefing sample text
- Active modules for that industry

### For LIVE mode — fetch from Airtable:
```python
import os, requests
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("AIRTABLE_TOKEN")
BASE  = os.getenv("AIRTABLE_BASE_PLUGGEDIN")  # or client's base

headers = {"Authorization": f"Bearer {TOKEN}"}

# Fetch leads
leads = requests.get(
    f"https://api.airtable.com/v0/{BASE}/Leads",
    headers=headers,
    params={"filterByFormula": f"{{ClientID}}='{client_id}'", "maxRecords": 50}
).json().get("records", [])

# Fetch opportunities
opps = requests.get(
    f"https://api.airtable.com/v0/{BASE}/Opportunities",
    headers=headers,
    params={"maxRecords": 20}
).json().get("records", [])

# Fetch CEO reports (today)
reports = requests.get(
    f"https://api.airtable.com/v0/{BASE}/CEOReports",
    headers=headers,
    params={"filterByFormula": "IS_SAME({Date}, TODAY(), 'day')", "maxRecords": 10}
).json().get("records", [])
```

Build a `dashboard_data` dict from the fetched records before generating HTML.

---

## STEP 3 — DESIGN SYSTEM (apply to every dashboard)

### 8 Design Philosophies — NON NEGOTIABLE

**1. DATA HIERARCHY**
Most important number: largest font, top-left or top-center.
Secondary metrics: medium, below or beside.
Supporting detail: small, greyed out.
Never let everything compete for attention.

**2. COLOR SEMANTICS**
```
Primary brand:  #6c63ff  (PluggedIN purple)
Good / up:      #16a34a  (green)
Warning:        #d97706  (amber)
Critical:       #dc2626  (red)
Neutral:        #6b7280  (grey)
Background:     #f4f5f7  (light grey)
Card:           #ffffff  (white)
Text primary:   #1a1a2e  (near black)
Text secondary: #6b7280  (grey)
```
Never use more than 4 colours in one dashboard.

**3. SPATIAL RHYTHM**
Base unit: 8px. All spacing is multiples of 8 (8, 16, 24, 32, 48).
Cards: 10px border-radius, 1px border #e8eaed, subtle shadow.
Grid: 12-column, responsive. KPI cards always in a row at top.

**4. MOTION ECONOMY**
One entrance animation only: fade-in + translateY(10px) on load, 0.3s ease.
Chart animations: 400ms max. No looping animations.
Hover states: 0.15s transition, subtle background shift only.

**5. INFORMATION DENSITY**
KPI row: 4-6 cards max. One number per card. One label. One sub-label.
Charts: one insight per chart. Label it with the "so what" not just the metric name.
Tables: max 5 columns visible. Most important column first.

**6. TRUST SIGNALS**
Always show: last updated timestamp, data source label, record count.
Live data: show "● LIVE" badge in green.
Demo data: show "DEMO" badge in amber — never hide this.

**7. ACTION CLARITY**
Every panel answers: "What should I do about this?"
Add a subtle "Next action" line below any critical metric.
Alerts/flags should be visually distinct — amber left border on card.

**8. PROGRESSIVE DISCLOSURE**
Show summary first. Details expand on click or are in a scrollable table below.
Never put raw data at the top.

---

## STEP 4 — DASHBOARD STRUCTURE

Build the HTML in this exact order:

```
┌─────────────────────────────────────────────────────┐
│  HEADER: Client name | LIVE/DEMO badge | Timestamp  │
│          Refresh button | Module badges active       │
├─────────────────────────────────────────────────────┤
│  KPI ROW: 4-6 headline numbers from active modules  │
├───────────────────────┬─────────────────────────────┤
│  MODULE PANELS        │  CHART (pipeline/status)    │
│  (left, 2/3 width)    │  (right, 1/3 width)         │
│                       │                             │
│  Active modules only  │  Donut or bar chart         │
│  One panel per module │  Legend with counts         │
├───────────────────────┴─────────────────────────────┤
│  LEADS / PIPELINE TABLE (full width, scrollable)    │
├─────────────────────────────────────────────────────┤
│  AGENT ACTIVITY FEED (last 5 actions taken)         │
└─────────────────────────────────────────────────────┘
```

---

## STEP 5 — MODULE PANELS

Show only the modules the client has purchased.
For demo: show the modules most relevant to that industry (from playbook).

### Module Panel Templates:

**Module 1 — Presence Agent**
```
KPI:    Calls handled today | Avg response time
Chart:  Call outcomes (Booked / Followed up / Voicemail)
Table:  Recent calls — Name, Time, Outcome, Score
Alert:  Any missed calls > 30min ago → amber border
```

**Module 2 — Pipeline Agent**
```
KPI:    New leads today | Hot leads | Meetings booked | Pipeline value
Chart:  Lead status funnel (New → Contacted → Replied → Booked)
Table:  Top leads — Company, Score, Status, Last Contact
Alert:  Leads with no contact in 48hrs → amber border
```

**Module 3 — Marketing Agent**
```
KPI:    Posts published | Reach this week | Ad spend | Leads from ads
Chart:  Channel performance (TikTok/Instagram/Pinterest/LinkedIn)
Table:  Content calendar — Date, Platform, Type, Status
Alert:  Any scheduled post not yet published → amber border
```

**Module 4 — Intelligence Agent**
```
KPI:    Competitor moves tracked | Signals found | Alerts
Chart:  Signal categories (Pricing / Hiring / Product / PR)
Table:  Latest signals — Source, Signal, Impact, Date
Alert:  High-impact signals → red border
```

**Module 5 — Sales Intelligence**
```
KPI:    Calls analysed | Avg score | Top objection | Win rate
Chart:  Call score distribution (bar)
Table:  Recent calls — Rep, Score, Top objection, Coaching note
Alert:  Calls scoring < 60 → amber border
```

**Module 6 — Data Intelligence**
```
KPI:    Revenue this month | vs last month | Top performer | Forecast
Chart:  Revenue trend (line chart, last 30 days)
Table:  KPI breakdown by department/product
Alert:  Any KPI below target → red border
```

**Module 7 — Conversion Agent**
```
KPI:    Website visitors | Conversion rate | Leads captured | Score avg
Chart:  Conversion funnel
Table:  Landing pages — Page, Visitors, Conversions, Rate
Alert:  Pages with < 2% conversion → amber border
```

**Module 8 — Lead Marketplace**
```
KPI:    Leads matched today | Delivered | Accepted | Revenue
Chart:  Lead quality distribution
Table:  Recent matches — Niche, Score, Buyer, Status
Alert:  Unaccepted leads > 4hrs → amber border
```

**Module 9 — Customer Retention OS**
```
KPI:    At-risk customers | Reviews received | NPS score | Churn rate
Chart:  Retention health (donut: Healthy / At Risk / Churned)
Table:  At-risk customers — Name, Last visit, Risk reason, Action
Alert:  Customers not seen in 30 days → red border
```

**Module 10 — Stock Intelligence**
```
KPI:    Suppliers monitored | Price alerts | Out-of-stock risks | Savings found
Chart:  Price trend for top 3 products (line)
Table:  Stock alerts — Item, Alert, Action, Urgency
Alert:  Critical stock risk → red border
```

---

## STEP 6 — AIRTABLE LIVE REFRESH

For live mode, add auto-refresh at the top of the HTML `<script>`:

```javascript
// Auto-refresh every 5 minutes
const AIRTABLE_TOKEN = 'pat...'; // injected at build time — never hardcode
const BASE_ID = 'app...';

async function fetchLiveData() {
  // Fetch leads
  const res = await fetch(
    `https://api.airtable.com/v0/${BASE_ID}/Leads?maxRecords=50`,
    { headers: { Authorization: `Bearer ${AIRTABLE_TOKEN}` } }
  );
  const data = await res.json();
  updateDashboard(data.records);
  document.getElementById('lastRefresh').textContent =
    `Updated ${new Date().toLocaleTimeString('en-GB')}`;
}

fetchLiveData();
setInterval(fetchLiveData, 300000); // 5 min
```

IMPORTANT: When injecting the Airtable token into the HTML for a client file,
warn the user: "This file contains your Airtable API token. Do not share publicly.
Host on password-protected Netlify or serve locally only."

For public demos: use hardcoded demo data in JavaScript — NO token in the file.

---

## STEP 7 — REMOTION VIDEO EXPORT (optional)

If user asks for a "video version" or "animated report":

1. Generate a `dashboard-remotion/` folder with:
   ```
   dashboard-remotion/
     src/
       Root.tsx         — registers compositions
       Dashboard.tsx    — main dashboard component
       KPICard.tsx      — animated KPI card
       Chart.tsx        — animated chart
       AgentFeed.tsx    — scrolling activity feed
     package.json
     remotion.config.ts
   ```

2. Dashboard.tsx structure:
   ```tsx
   // 30 seconds total, 30fps
   // 0-3s:   PluggedIN logo + client name fade in
   // 3-8s:   KPI cards animate in one by one (spring animation)
   // 8-18s:  Module panels slide in from left
   // 18-25s: Chart animates (draws itself)
   // 25-30s: Agent activity feed scrolls + CTA
   ```

3. Render command:
   ```bash
   cd dashboard-remotion
   npm install
   npx remotion render src/Root.tsx Dashboard out/dashboard.mp4 \
     --props='{"clientName":"Harland Construction","industry":"construction"}'
   ```

4. Output: `out/dashboard.mp4` — shareable, embeddable in proposals

---

## STEP 8 — OUTPUT

### File naming:
```
demo_{industry}_{date}.html         → demo mode
live_{client_slug}_{date}.html      → live mode
{client_slug}_dashboard.mp4         → remotion export
```

### Save location:
```
~/Documents/AI-Agency/PluggedIN/outputs/dashboards/
```

### Sharing:
- Local: open in browser directly
- Client sharing: drag HTML to netlify.com/drop → instant public URL (free)
- Password protect: Netlify paid tier OR serve via Python: `python3 -m http.server 8080`
- Embed in proposal: screenshot top section + link to hosted file

---

## STEP 9 — QUALITY CHECKLIST

Before saving the file, verify:

- [ ] DEMO/LIVE badge is visible and correct
- [ ] Last updated timestamp is showing
- [ ] All KPI numbers make sense (not 0s everywhere)
- [ ] Chart has data and renders correctly
- [ ] Industry demo data matches the playbook (right city, right metrics)
- [ ] Correct modules shown (not showing modules client hasn't bought)
- [ ] Mobile responsive (test by narrowing browser)
- [ ] No API tokens in demo files
- [ ] File opens without internet (for demo files — all CDN scripts should have fallbacks)
- [ ] Color palette follows design system (no rogue colours)

---

## EXAMPLE INVOCATIONS

```
"Build a construction demo dashboard"
→ DEMO mode, construction industry, Harland Construction data,
  Pipeline + Intelligence modules, saved to outputs/dashboards/

"Build a live dashboard for Gromatic using their Airtable"
→ LIVE mode, legal industry, fetches from AIRTABLE_BASE_GROMATIC,
  Pipeline module, real data, 5-min auto-refresh

"Generate a sales demo for a restaurant client on Growth package"
→ DEMO mode, restaurant industry, Growth package (3 modules),
  show Presence + Pipeline + Marketing panels

"Build a video version of the construction dashboard"
→ Same as demo above + generate Remotion project + render MP4
```

---

## DEPENDENCIES

All available via CDN (no install needed for HTML output):
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.5.0/dist/chart.umd.js"
  integrity="sha384-iU8HYtnGQ8Cy4zl7gbNMOhsDTTKX02BTXptVP/vqAWIaTfM7isw76iyZCsjL2eVi"
  crossorigin="anonymous"></script>
```

For Remotion video export (install once):
```bash
npm install remotion @remotion/cli react react-dom typescript
```

For live Airtable fetch (Python build script):
```bash
pip3 install requests python-dotenv
```

---

## REFERENCES

- Huashu Design:   github.com/alchaincyf/huashu-design
- Chart.js:        chartjs.org
- Remotion:        remotion.dev
- Airtable API:    airtable.com/developers/web/api/introduction
- Industry data:   industries/*.md (this repo)
- Module specs:    memory/semantic/pricing.md
- Demo data:       industries/[industry].md → DEMO DATA section
