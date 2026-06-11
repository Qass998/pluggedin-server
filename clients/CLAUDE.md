# SEGGUINÉE Water Utility Portal
## Client Operating System v1.0

---

## WHAT SEGGUINÉE IS

SEGGUINÉE is Guinea's water utility operator (ONEE). We are building their complete digital operating system:
- **Portal:** Operator dashboard (Next.js 16, deployed on Railway)
- **API:** Data backend (Airtable + Node.js)
- **Agents:** WhatsApp + voice + reporting automation

**Billing Model:** $2,000 setup + $500/month
**Current Status:** Deployed (pending first agent activation)
**Contact:** Director (authenticated via portal)

---

## DEPLOYMENT ENVIRONMENT

### Railway Project
- **URL:** [production-url-here]
- **Node Version:** 20 (required for Next.js 16)
- **Build Command:** `cd outputs/clients/segguinee/segguinee-portal && npm install && npm run build`
- **Start Command:** `cd outputs/clients/segguinee/segguinee-portal && npm start`
- **Environment Variables:** See SEGGUINEE_ENV.md

### GitHub Repository
- **Repo:** github.com/qassim-abdulkarim/PluggedIN (private)
- **Portal Folder:** `outputs/clients/segguinee/segguinee-portal/`
- **Root Config:** `railway.json` (must have NIXPACKS_NODE_VERSION=20)

---

## CURRENT SYSTEM STATE

### ✅ COMPLETE
- [x] Authentication system (cookie-based login)
- [x] Sidebar navigation (7 tabs)
- [x] Agents IA panel (displays agents without pricing)
- [x] API endpoint strips pricing data (/api/data/agents)
- [x] Dark theme UI (PluggedIN design system)
- [x] Mobile responsive layout
- [x] Component architecture fixed (useSearchParams Suspense boundaries)
- [x] Node.js 20 configured (package.json, .nvmrc, railway.json)

### 🔄 IN PROGRESS
- [ ] Deploy build to Railway (push commits + redeploy)
- [ ] Verify portal loads live
- [ ] Test login flow with director

### ⏳ TODO (Agents)
- [ ] WhatsApp Presence Agent (£797/month) — inbound message handling
- [ ] Facturation Agent (£300/month) — invoice generation + payment tracking
- [ ] Data Analysis Agent (£200/month) — KPI dashboards
- [ ] Each agent activation = +revenue

---

## DEPLOYMENT CHECKLIST — DO THIS IN ORDER

### Step 1: Push Code to GitHub
```bash
cd ~/Documents/AI-Agency/PluggedIN
git push origin main
```
**Status:** ⏳ Waiting (SSH auth needed)

### Step 2: Configure Railway Environment
Go to Railway dashboard → Production environment:
```
AIRTABLE_TOKEN=<token>
AIRTABLE_BASE_SEGGUINEE=<base-id>
NODE_ENV=production
NIXPACKS_NODE_VERSION=20
```
**Status:** ⏳ Waiting

### Step 3: Redeploy on Railway
Click the Error/Stale deployment → Redeploy
**Status:** ⏳ Waiting

### Step 4: Verify Live
- [ ] Portal loads at [railway-url]
- [ ] Login works (authenticate with director's token)
- [ ] Agents IA tab shows agents (no pricing)
- [ ] Sidebar navigation works
- [ ] Mobile layout renders correctly

### Step 5: Enable First Agent (WhatsApp Presence)
Once portal verified live:
- [ ] Create VAPI receptionist (takes 5 min)
- [ ] Connect to director's WhatsApp number
- [ ] Test inbound message → AI response
- [ ] Log activation to Airtable

---

## ARCHITECTURE — WHAT RUNS WHERE

```
SEGGUINÉE Director's Phone
        ↓
    WhatsApp ← VAPI Agent (voice + messaging)
        ↓
   Railways Portal (Node.js)
        ↓
    /api/data/* (real-time data)
        ↓
   Airtable Base (SEGGUINEE data)
        ↓
   Conversations | Production | Invoices | Incidents | Agents Log
```

Every tab in the portal reads from Airtable in real-time.

---

## NEXT REVENUE MILESTONES

**This Week:**
- Deploy portal live ✅
- Activate WhatsApp agent (+£797/month)

**Next Week:**
- Facturation agent live (+£300/month)
- Invoice PDF generation working

**Month 2:**
- Data Analysis agent (+£200/month)
- KPI dashboards auto-updating
- **Total MRR: £1,297/month**

---

## DECISION LOG

**Why Railway not Vercel?**
Simple Node.js + Airtable stack. Railway's $5/month baseline cheaper than Vercel. No edge functions needed.

**Why no setup fee immediately?**
First client. Need case studies. Building proof of value first. $500/month ongoing = revenue + runway.

**Why agents not shown with pricing?**
Selling outcomes, not features. Once director sees WhatsApp agent working, they'll adopt. Then upsell additional agents.

---

## FILES & LOCATIONS

| File | Purpose | Location |
|------|---------|----------|
| CLAUDE.md | This file — operating system | `/Clients/SEGGUINEE/CLAUDE.md` |
| SEGGUINEE_ENV.md | Environment variables | `/Clients/SEGGUINEE/config/SEGGUINEE_ENV.md` |
| SEGGUINEE_CHECKLIST.md | Deployment & agent checklist | `/Clients/SEGGUINEE/docs/SEGGUINEE_CHECKLIST.md` |
| railway.json | Deployment config | `/PluggedIN/outputs/clients/segguinee/segguinee-portal/railway.json` |
| portal code | Next.js app | `/PluggedIN/outputs/clients/segguinee/segguinee-portal/src/` |
| Airtable base | Live data | SEGGUINEE base (ID: [BASE_ID]) |

---

## COMMANDS

**Deploy:**
```bash
cd ~/Documents/AI-Agency/PluggedIN && git push origin main
# Then redeploy on Railway dashboard
```

**Development:**
```bash
cd ~/Documents/AI-Agency/PluggedIN/outputs/clients/segguinee/segguinee-portal
npm install
npm run dev
# Navigate to http://localhost:3000/login
```

**Logs:**
```bash
# Railway production logs
# Go to Railway dashboard → Logs tab (or use Railway CLI)
```

---

## WHO DOES WHAT

**Qassim:** Approvals, business decisions, client calls
**Claude Code:** Build, deploy, troubleshoot, automate
**SEGGUINÉE Director:** Provides feedback, approves agents, uses portal

---

## SUPPORT / ESCALATION

If deployment fails:
1. Check Railway logs for exact error
2. Verify all env vars set correctly
3. Verify code pushed to GitHub main
4. Check Node.js version (must be 20+)
5. If blocked: document issue in /deploy/BLOCKERS.md and escalate

---

**Last Updated:** June 3, 2026
**Status:** Deployment in progress
**Owner:** Qassim Abdulkarim
