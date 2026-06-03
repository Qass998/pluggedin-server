# SEGGUINÉE Quick Start (20 min)

## RIGHT NOW (IF GITHUB AUTH IS FIXED)

```bash
# Step 1: Push (1 min)
cd ~/Documents/AI-Agency/PluggedIN
git push origin main

# Step 2: Railway Env Vars (3 min)
# Go to Railway dashboard → SEGGUINEE project → Environment
# Click "New Variable" for each:
AIRTABLE_TOKEN=<paste-from-airtable>
AIRTABLE_BASE_SEGGUINEE=<paste-base-id>
NODE_ENV=production
NIXPACKS_NODE_VERSION=20

# Step 3: Redeploy (5 min)
# Railway → Deployments → Find "Error" → Click three dots → "Redeploy"
# Watch logs until "✅ Ready"

# Step 4: Test (5 min)
# Copy Railway URL from dashboard
# Open in browser
# Login with director token
# Click Agents IA → see agent cards (no pricing)
```

**Total: 15-20 minutes**

---

## IF YOU GET STUCK

1. Check `clients/SEGGUINEE/deploy/BLOCKERS.md` — is your error listed?
2. Check Railway logs: exact error message is there
3. Reference `docs/DEPLOYMENT_CHECKLIST.md` — did you skip a step?
4. Ask Claude: describe exact error + screenshot of Rails logs

---

## EXPECTED SUCCESS STATE

```
Portal loads at: https://[railway-url]
Login page appears
Enter director token
Click "Agents IA"
See 5-6 agent cards:
  - Icon (🤖)
  - Name (e.g., "WhatsApp Presence")
  - Description (what it does)
  - NO PRICES (that's the point)
Sidebar navigation works
Can logout
```

---

## REVENUE IMPACT

✅ **Deploy = +£500/month**
✅ **First agent = +£797/month**
✅ **3 agents = +£1,297/month**

---

## ONE SENTENCE

"Fix GitHub SSH, push code, set 4 env vars on Railway, click Redeploy, wait 5 min, test portal."

Done.
