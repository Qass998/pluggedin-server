# SEGGUINÉE Quick Start

## 🚀 Deploy Right Now (If GitHub is Fixed)

```bash
# Step 1: Push code
cd ~/Documents/AI-Agency/PluggedIN
git push origin main

# Step 2: Go to Railway dashboard
# - Select SEGGUINEE project
# - Environment tab → add these 4 vars:
#   AIRTABLE_TOKEN=<your-token>
#   AIRTABLE_BASE_SEGGUINEE=<your-base-id>
#   NODE_ENV=production
#   NIXPACKS_NODE_VERSION=20

# Step 3: Redeploy
# - Deployments tab
# - Click Error/Stale deployment
# - Click three dots → Redeploy
# - Wait for "✅ Ready"

# Step 4: Test
# - Copy Railway URL
# - Open in browser
# - Login with director credentials
# - Click "Agents IA" → should see agent cards
```

**Total Time:** 15 min
**Cost:** £0 (Railway free tier + Airtable)
**Revenue:** £500/month starts immediately

---

## 📁 Folder Structure

```
~/Documents/AI-Agency/
├── Clients/
│   └── SEGGUINEE/                    ← All client files here
│       ├── CLAUDE.md                 ← Operating system
│       ├── QUICK_START.md            ← This file
│       ├── STATUS.md                 ← Current progress
│       ├── config/
│       │   └── SEGGUINEE_ENV.md      ← Environment variables
│       ├── docs/
│       │   └── DEPLOYMENT_CHECKLIST.md
│       ├── deploy/
│       │   ├── BLOCKERS.md           ← Issues tracker
│       │   └── ROLLBACK_PLAN.md      ← If deployed fails
│       └── outputs/
│           └── [generated files go here]
│
└── PluggedIN/
    ├── outputs/clients/segguinee/segguinee-portal/  ← Portal code
    ├── railway.json                  ← Deployment config
    └── [rest of PluggedIN system]
```

---

## 🔑 Critical Files

| File | Purpose | Do This |
|------|---------|---------|
| CLAUDE.md | Master operating doc | Read once, reference always |
| STATUS.md | Where are we now? | Check before every session |
| DEPLOYMENT_CHECKLIST.md | Step-by-step deploy | Follow exactly in order |
| BLOCKERS.md | What's broken? | Check if stuck |
| QUICK_START.md | Just deploy | You're reading it |

---

## ✅ Deployment Phases

**Phase 1:** Dev ✅ DONE
**Phase 2:** Push to GitHub 🔴 BLOCKED (SSH auth)
**Phase 3:** Deploy to Railway ⏳ READY
**Phase 4:** Verify live ⏳ READY
**Phase 5:** Activate first agent ⏳ READY

**Current Blocker:** Need to push code to GitHub (fix SSH auth first)

---

## 🎯 What Each Person Does

### Qassim
- [ ] Fix GitHub SSH auth (generate key + add to GitHub)
- [ ] Confirm code pushed: check GitHub main branch
- [ ] Set 4 env vars in Railway
- [ ] Click "Redeploy" on Railway dashboard
- [ ] Test portal loads + login works
- [ ] Next: Call director with live URL

### Claude Code
- [ ] Monitor build logs
- [ ] Troubleshoot if build fails
- [ ] Help debug any runtime issues

---

## 🚨 If Something Breaks

1. Check `/Clients/SEGGUINEE/deploy/BLOCKERS.md` — is your issue listed?
2. If not listed: add it with exact error + timestamp
3. Check Railway logs: Dashboard → Logs tab
4. Reference `/Clients/SEGGUINEE/docs/DEPLOYMENT_CHECKLIST.md` — did you skip a step?

**Never guess. Always check the docs first.**

---

## 📞 Contact

- **Qassim:** Decision maker + GitHub access
- **Claude:** Build + deploy + troubleshoot
- **Director (SEGGUINEE):** Portal user (authenticate via token)

---

## 💰 Revenue Tracking

**Current:** £0 (not live yet)
**Once Deployed:** £500/month retainer
**With WhatsApp Agent:** +£797/month = £1,297/month
**With 2 more agents:** +£500/month = £1,797/month

---

**Status:** 🔴 Blocked on GitHub push
**Action:** Fix SSH auth, push code, deploy
**Timeline:** 20 min once unblocked

Read `/Clients/SEGGUINEE/CLAUDE.md` for full operating system.
