# SEGGUINÉE Deployment Checklist

## PHASE 1: CODE TO GITHUB (5 min)

- [ ] Open terminal in ~/Documents/AI-Agency/PluggedIN
- [ ] Run: `git push origin main`
- [ ] Verify: Go to GitHub → main branch → see latest commits
- [ ] **If blocked on SSH:** Use GitHub Desktop or `gh` CLI with auth

**Expected state:** All local commits now on origin/main

---

## PHASE 2: RAILWAY ENVIRONMENT (3 min)

Go to Railway dashboard:

- [ ] Select SEGGUINÉE project
- [ ] Click "Environment" → select "production"
- [ ] Click "New Variable" and add these:

| Key | Value |
|-----|-------|
| `AIRTABLE_TOKEN` | [paste from Airtable account settings] |
| `AIRTABLE_BASE_SEGGUINEE` | [paste base ID from Airtable] |
| `NODE_ENV` | `production` |
| `NIXPACKS_NODE_VERSION` | `20` |

- [ ] Save all variables

**Expected state:** All 4 variables set in Railway production

---

## PHASE 3: BUILD & DEPLOY (5-10 min)

Go to Railway Deployments tab:

- [ ] Find deployment labeled "Error" or "Stale" (13 hours old)
- [ ] Click the three dots (⋮)
- [ ] Click "Redeploy"
- [ ] Watch status change:
  - First: "Building..." (3-5 min)
  - Then: "Deploying..." (1-2 min)
  - Finally: "✅ Ready" or "❌ Failed"

**What you'll see in logs:**
```
> Using Node v20.x.x
> npm install
> npm run build
> Build successful
> Starting server
```

**If build fails:** Check logs for exact error → note in /deploy/BLOCKERS.md

**Expected state:** Deployment shows "✅ Ready"

---

## PHASE 4: VERIFY LIVE (5 min)

Once deployment is "✅ Ready":

- [ ] Copy the Railway URL from dashboard
- [ ] Open in browser (incognito mode)
- [ ] You should see: SEGGUINÉE login page
- [ ] Enter auth credentials (director's token)
- [ ] You should see: Sidebar + Conversations tab
- [ ] Click "Agents IA" tab
- [ ] You should see: Agent cards with NO pricing (only icon, name, description)
- [ ] Click "Déconnexion" to logout

**Expected outcome:** Portal fully functional, all tabs accessible

---

## PHASE 5: FIRST AGENT ACTIVATION (Next step)

Once portal is live:

- [ ] Create VAPI receptionist (5 min setup)
- [ ] Connect to director's WhatsApp: [number]
- [ ] Test: Send message → get AI response
- [ ] Log to Airtable agents_log table
- [ ] Bill: +£797/month WhatsApp Presence Agent

---

## ROLLBACK PLAN

If deployment fails and can't be fixed in 30 min:

1. Revert last commit: `git revert HEAD`
2. Push: `git push origin main`
3. Redeploy on Railway (will pull old working code)
4. Document issue in /deploy/BLOCKERS.md
5. Escalate to Claude with exact error

---

## SUCCESS CRITERIA

✅ **Minimal:** Portal loads + login works + Agents IA visible
✅ **Good:** All 7 tabs navigate + sidebar works + mobile responsive
✅ **Perfect:** Zero console errors + performance <1s load time

---

## TIMING

- **Total time:** 15-20 min (if no blockers)
- **Longest step:** Build (3-5 min)
- **Most likely blocker:** Env vars not set correctly

---

**Last Updated:** June 3, 2026
**Next Review:** After first successful deployment
