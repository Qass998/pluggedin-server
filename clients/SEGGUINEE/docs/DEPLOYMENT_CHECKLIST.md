# SEGGUINÉE Deployment Checklist (Exact Steps)

## PHASE 1: GITHUB PUSH
**Estimated Time:** 1 min
**Blocker Status:** 🔴 BLOCKED (SSH auth missing)

- [ ] Open terminal: `cd ~/Documents/AI-Agency/PluggedIN`
- [ ] Run: `git push origin main`
- [ ] Verify: Go to GitHub → click "main" branch → see latest 2 commits
- [ ] If fails with "Permission denied": Fix SSH key (see BLOCKERS.md)

**Expected:** All commits now on origin/main

---

## PHASE 2: RAILWAY ENVIRONMENT
**Estimated Time:** 3 min
**Blocker Status:** ✅ Ready

- [ ] Go to: railway.app → SEGGUINEE project
- [ ] Click: "Environment" tab
- [ ] Select: "production" environment
- [ ] Click: "New Variable" button
- [ ] Add Variable #1:
  - Key: `AIRTABLE_TOKEN`
  - Value: [paste from airtable.com → Account → Personal access tokens]
- [ ] Add Variable #2:
  - Key: `AIRTABLE_BASE_SEGGUINEE`
  - Value: [paste base ID from Airtable URL or settings]
- [ ] Add Variable #3:
  - Key: `NODE_ENV`
  - Value: `production`
- [ ] Add Variable #4:
  - Key: `NIXPACKS_NODE_VERSION`
  - Value: `20`
- [ ] Click "Save" on each

**Expected:** All 4 variables visible in Environment tab

---

## PHASE 3: BUILD & DEPLOY
**Estimated Time:** 5-7 min
**Blocker Status:** ✅ Ready

- [ ] Go to: Railway → SEGGUINEE project → Deployments tab
- [ ] Find: Deployment marked "Error" or "Stale" (should say "created 13 hours ago" or similar)
- [ ] Click: The three dots (⋮) menu on that deployment
- [ ] Click: "Redeploy"
- [ ] Watch status change:
  - First: "Building..."
  - Then: "Deploying..."
  - Finally: "✅ Ready" or "❌ Failed"
- [ ] If building: Click "Logs" → watch output
  - Should see: "Using Node v20.x.x"
  - Should see: "npm install... done"
  - Should see: "npm run build... done"
  - Should NOT see: errors
- [ ] If deployment is "✅ Ready": continue to Phase 4
- [ ] If deployment "❌ Failed": Check logs for exact error → note in BLOCKERS.md

**Expected:** Deployment shows "✅ Ready" status

---

## PHASE 4: VERIFY LIVE
**Estimated Time:** 5 min
**Blocker Status:** ✅ Ready

- [ ] Go to: Railway → SEGGUINEE project → Overview
- [ ] Copy: The public URL (should be: https://[project].up.railway.app)
- [ ] Open: In new browser tab (incognito mode recommended)
- [ ] You should see: SEGGUINÉE login page
- [ ] Enter: Director's authentication token
- [ ] Click: Login
- [ ] You should see: Dark dashboard with sidebar on left
- [ ] Click: "Agents IA" tab in sidebar
- [ ] You should see: 5-6 agent cards displaying:
  - Icon (emoji like 🤖)
  - Agent name (e.g., "WhatsApp Presence Agent")
  - Description (what it does)
  - **NO PRICES** (this is the goal)
- [ ] Click: Each tab to verify all work:
  - [ ] Conversations
  - [ ] Production
  - [ ] Factures (Invoices)
  - [ ] Incidents
  - [ ] Projets (Projects)
  - [ ] Terrain (Field)
  - [ ] Agents IA
- [ ] Click: "Déconnexion" (logout button)
- [ ] You should: Return to login page
- [ ] Note: Write down the Railway URL for director

**Expected:** All tabs accessible, no errors, agents visible without prices

---

## PHASE 5: FIRST AGENT ACTIVATION
**Estimated Time:** 15 min (next session)
**Blocker Status:** ⏳ Not yet (depends on Phase 4)

*This happens AFTER portal is live:*

- [ ] Create VAPI receptionist assistant (5 min)
- [ ] Connect to director's WhatsApp number
- [ ] Test: Send message → get AI response
- [ ] Log to Airtable agents_log table
- [ ] Bill: +£797/month WhatsApp Presence Agent
- [ ] Revenue: Now £500 + £797 = £1,297/month

---

## SUCCESS CRITERIA

✅ **Minimal Success:** Portal loads + login works + Agents IA tab visible
✅ **Good Success:** All 7 tabs navigate + mobile responsive + no console errors
✅ **Perfect Success:** <1s load time + smooth animations + pricing completely hidden

---

## ROLLBACK (If Phase 3 Fails)

If build fails and won't fix in 30 min:

1. `git revert HEAD` (undo last commit)
2. `git push origin main`
3. Railway → Redeploy (will pull previous working code)
4. Document exact error in `deploy/BLOCKERS.md`
5. Escalate with exact error message + timestamp

---

## TIMING SUMMARY

| Phase | Task | Time | Status |
|-------|------|------|--------|
| 1 | Push to GitHub | 1 min | 🔴 Blocked |
| 2 | Railway env vars | 3 min | ✅ Ready |
| 3 | Redeploy | 5-7 min | ✅ Ready |
| 4 | Verify live | 5 min | ✅ Ready |
| 5 | Agent activation | 15 min | ⏳ Next |
| **Total** | **Deploy** | **15-20 min** | **Once unblocked** |

---

## NOTES

- Don't skip a single checkbox
- If you get error: screenshot → paste exact error → check BLOCKERS.md
- If stuck: This document explains WHAT, not HOW → check BLOCKERS.md for HOW
- Once "✅ Ready": Portal is live forever (until you redeploy again)
- Revenue starts immediately upon "✅ Ready"

---

**Created:** June 3, 2026
**For:** Clear, repeatable deployment
**Next review:** After first successful deployment
