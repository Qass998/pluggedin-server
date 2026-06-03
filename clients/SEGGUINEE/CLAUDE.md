# SEGGUINÉE Water Utility Portal — Operating System
## Deployment Phase | June 3, 2026

---

## STATUS: 🔴 BLOCKED ON GITHUB PUSH

**Current Phase:** 2 of 5 (Push code to GitHub)
**Blocker:** SSH auth — need to fix GitHub SSH keys
**Timeline:** 20 min to live portal once unblocked
**Revenue:** £500/month (retainer) + agents = £1,297/month potential

---

## WHAT IS SEGGUINÉE

Guinea's water utility operator. We're building their complete digital OS:
- **Portal:** Operator dashboard (Next.js 16 on Railway)
- **WhatsApp:** Inbound message handling + voice
- **Invoicing:** Auto-bill + tracking
- **Data:** Real-time KPI dashboards

**Model:** £2,000 setup + £500/month retainer + £797-300/month per agent
**Client Contact:** Director (authenticated via portal token)

---

## DEPLOYMENT PHASES

```
Phase 1: Dev ✅ COMPLETE     (code ready, all bugs fixed)
Phase 2: GitHub 🔴 BLOCKED  (push code → need SSH auth)
Phase 3: Railway ⏳ READY   (set env vars + redeploy)
Phase 4: Verify ⏳ READY    (test portal loads)
Phase 5: Agent ⏳ READY     (enable WhatsApp agent → +£797/month)
```

**Current Blocker:** Phase 2 (GitHub SSH authentication missing)

---

## QUICK DEPLOY (Once GitHub is Fixed)

```bash
# 1. Push code (1 min)
cd ~/Documents/AI-Agency/PluggedIN
git push origin main

# 2. Railway env vars (3 min)
Go to Railway → Environment → Add:
  AIRTABLE_TOKEN=[token]
  AIRTABLE_BASE_SEGGUINEE=[base-id]
  NODE_ENV=production
  NIXPACKS_NODE_VERSION=20

# 3. Redeploy (5 min)
Railway → Deployments → Error → Redeploy → Wait for ✅ Ready

# 4. Test (5 min)
Open Railway URL → Login → Click Agents IA → See agents (no pricing)

Total: 15 min
```

---

## ARCHITECTURE

```
Director's WhatsApp
        ↓
Railway Portal (Node.js 20)
        ↓
    API Routes (/api/data/*)
        ↓
   Airtable Base (SEGGUINEE)
        ↓
[Conversations | Production | Invoices | Incidents | Agents | etc]
```

Every tab reads real-time from Airtable.
Portal authenticates with director's token.
No pricing shown (selling outcomes, not features).

---

## WHAT'S COMPLETE

✅ Authentication (cookie-based login)
✅ Sidebar navigation (7 tabs)
✅ Agents IA panel (no pricing display)
✅ API strips pricing via regex
✅ Dark theme UI (PluggedIN design)
✅ Mobile responsive
✅ Component architecture (Suspense boundaries fixed)
✅ Node.js 20 configured (package.json, .nvmrc, railway.json)
✅ All code ready for production

---

## WHAT'S PENDING

⏳ Push to GitHub (blocked by SSH)
⏳ Deploy to Railway (ready to execute)
⏳ Verify portal loads (ready to execute)
⏳ Activate WhatsApp agent (£797/month)
⏳ Activate Invoicing agent (£300/month)
⏳ Activate Data agent (£200/month)

---

## ROOT CAUSE OF 7-DEPLOY CIRCLE

**Problem:** Not guessing, not following one plan
**Solution:** This document (one source of truth)

Every decision documented:
- Why Railway not Vercel? (£5/month vs Vercel)
- Why no setup fee immediately? (need case studies first)
- Why agents hidden? (sell outcomes, not features)
- Why Node 20 required? (Next.js 16 hard requirement)

---

## FILES & LOCATIONS

| File | Location | Purpose |
|------|----------|---------|
| This file | clients/SEGGUINEE/CLAUDE.md | Operating system |
| STATUS.md | clients/SEGGUINEE/STATUS.md | Current progress |
| QUICK_START.md | clients/SEGGUINEE/QUICK_START.md | Deploy in 20 min |
| DEPLOYMENT_CHECKLIST.md | clients/SEGGUINEE/docs/ | Phase-by-phase guide |
| BLOCKERS.md | clients/SEGGUINEE/deploy/ | Issues + fixes |
| Portal code | outputs/clients/segguinee/segguinee-portal/ | Next.js app |
| Deployment config | outputs/clients/segguinee/segguinee-portal/railway.json | Railway setup |

---

## NEXT STEP

**Qassim:**
1. Fix GitHub SSH auth (generate key + add to GitHub)
2. Run: `git push origin main`
3. Verify on GitHub: see latest commits in main branch

**Claude:** Standing by to push → deploy → verify

---

## COMMAND SUMMARY

```bash
# DEPLOY (phase 2-4)
cd ~/Documents/AI-Agency/PluggedIN && git push origin main
# Then in Railway dashboard: Redeploy
# Then test portal loads

# LOGS
# Railway → Logs tab (watch build)

# DEV
cd outputs/clients/segguinee/segguinee-portal && npm run dev
# Go to http://localhost:3000/login
```

---

**Owner:** Qassim Abdulkarim
**Built by:** Claude Code
**Diagnosed by:** Agent (root cause: Node 18 vs 20 mismatch)
**Last Updated:** June 3, 2026
**Status:** Ready to deploy (blocked on GitHub auth)
