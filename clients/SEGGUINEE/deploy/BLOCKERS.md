# SEGGUINÉE Blockers & Resolution

## 🔴 ACTIVE BLOCKER #1: GitHub SSH Auth

**Status:** BLOCKING DEPLOYMENT
**Issue:** `git push origin main` → "Permission denied (publickey)"
**Root Cause:** No SSH keys configured on this machine
**Impact:** Code changes can't reach GitHub → Railway can't rebuild → portal stays down

### Solution (Choose One)

**Option A: Generate SSH Key (Recommended)**
```bash
# Generate new SSH key
ssh-keygen -t ed25519 -C "your-email@example.com"
# Press Enter 3 times (accept defaults)
# Copy public key
cat ~/.ssh/id_ed25519.pub

# Then on GitHub:
# Go to Settings → SSH and GPG Keys → New SSH Key
# Paste public key, click Add
```

**Option B: Use GitHub CLI (If Installed)**
```bash
gh auth login
# Follow prompts
# Then: git push origin main
```

**Option C: Use GitHub Desktop GUI**
- Install GitHub Desktop
- Authenticate
- Clone repo → make changes → push

**Assigned to:** Qassim (GitHub account holder)
**Timeline:** 5 min to fix
**Verification:** `git push origin main` succeeds + see commits on GitHub

---

## ⏳ POTENTIAL BLOCKER #2: Railway Build Fails (After Push)

**Status:** UNKNOWN (depends on Phase 1)
**Will trigger if:** Phase 3 redeploy shows "❌ Failed"

### Likely Causes & Fixes

**Cause A: Node 20 Not Being Used**
- Check logs: look for "Using Node v20"
- Fix: Already set in 3 places (package.json, .nvmrc, railway.json)
- If still fails: Railway might not have picked up new env var
  - Delete current Deployment
  - Create new deployment from scratch
  - Set env vars again

**Cause B: Airtable Env Vars Missing**
- Logs will show: "AIRTABLE_TOKEN is undefined"
- Fix: Go to Railway → Environment → verify all 4 vars set
- Common mistake: Typo in variable name (must be EXACT)

**Cause C: TypeScript Compilation Error**
- Logs will show: "error TS2xxx: ..."
- Likely locations:
  - `/src/app/dashboard-client.tsx` (import path issue)
  - `/src/lib/airtable.ts` (type error)
- Fix: Check Portal code locally:
  ```bash
  cd outputs/clients/segguinee/segguinee-portal
  npm run build
  ```

**Cause D: Missing Dependency**
- Logs will show: "Cannot find module..."
- Fix: Check package.json has all required deps
- Most likely: Missing airtable-node or similar

**Assigned to:** Claude (debugging)
**If appears:** Document exact error + screenshot

---

## ✅ RESOLVED #1: useSearchParams Suspense Error

**Original Issue:**
```
Error: Missing Suspense boundary with useSearchParams
```

**Root Cause:** Both "use client" and `export const dynamic = "force-dynamic"` in same file

**Fix Applied:**
- Extracted DashboardContent to separate client file (`dashboard-client.tsx`)
- Page.tsx is now pure Server Component
- DashboardContent is Client Component in separate file
- Wrapped in Suspense boundary

**Commit:** 394e585 (June 3, 2026)
**Status:** ✅ Resolved

---

## ✅ RESOLVED #2: Node.js Version Mismatch

**Original Issue:**
```
You are using Node.js 18.20.8. For Next.js, Node.js version ">=20.9.0" is required.
```

**Root Cause:** Next.js 16 requires Node 20+ but environment had Node 18

**Why It Was Silent:** Build process checked Node version, failed, didn't display exact error in Railway UI (truncated logs)

**Fix Applied:**
- Added `engines` field to package.json: `"node": ">=20.9.0"`
- Created `.nvmrc` file: `20`
- Updated `railway.json`: Added `NIXPACKS_NODE_VERSION=20`
- Updated root `railway.json`: Added same env var globally

**Commits:**
- 1eb2e71 (June 3, 2026)
- Plus this is why we're still waiting for Phase 1

**Status:** ✅ Fixed (waiting for Phase 1)

---

## ESCALATION PATH

**If stuck > 30 min:**

1. Screenshot exact error from Railway logs
2. Paste into BLOCKERS.md under "New Issue"
3. Include: timestamp, phase, exact error message
4. Escalate to Claude with context

**If truly stuck:** Call Qassim with exact error + screenshot

---

## DECISION LOG

Why we're not guessing anymore:

**Problem:** 7 failed deployments in a row with no progress
- Deploy attempt 1: Component architecture issue
- Deploy attempt 2: Suspense boundary issue
- Deploy attempt 3: Config issue
- Deploy attempt 4-7: Node version issue (root cause, finally found)

**Root Cause:** Node 18 vs Node 20 mismatch, silent failure in Railway logs (truncated)

**Solution:** Stop guessing, build proper operating system:
- One source of truth (CLAUDE.md)
- Clear phases (DEPLOYMENT_CHECKLIST.md)
- Issue tracking (this file)
- No surprises

---

**Last Updated:** June 3, 2026
**Active Blockers:** 1 (GitHub SSH auth)
**Resolved:** 2 (Suspense, Node version)
**Status:** Ready to deploy once Phase 1 is unblocked
