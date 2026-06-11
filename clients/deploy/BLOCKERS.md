# SEGGUINÉE Deployment Blockers

## Current Blockers

### 1. Git Push Blocked (SSH Auth)
**Status:** 🔴 ACTIVE
**Issue:** `git push origin main` fails with "Permission denied (publickey)"
**Root Cause:** No SSH keys configured on this machine
**Impact:** Code changes can't reach GitHub, Railway can't rebuild
**Solution Options:**
- [ ] Generate SSH key: `ssh-keygen -t ed25519 -C "email@example.com"`
- [ ] Add to GitHub: Settings → SSH Keys → Add
- [ ] OR use GitHub Desktop GUI instead of CLI
- [ ] OR use `gh auth login` and use GitHub CLI

**Assigned to:** Qassim (requires GitHub account access)
**Timeline:** Must complete before Phase 2

---

### 2. Railway Build Still Failing (If Redeploy Fails)
**Status:** ⏳ PENDING (depends on #1)
**Issue:** TBD (will know after push + redeploy)
**Likely Causes:**
- Node 20 not being used (check logs for "Node v20")
- Missing Airtable env vars (build succeeds but runtime fails)
- TypeScript compilation error
- Missing import/dependency

**Resolution:** Check Railway logs → match exact error → document here

---

## Resolved Blockers (Archive)

### ✅ RESOLVED: useSearchParams Suspense Error
- **Original Error:** "Missing Suspense boundary with useSearchParams"
- **Root Cause:** "use client" and `export const dynamic` in same file
- **Fixed:** Extracted DashboardContent to separate client file
- **Commit:** 394e585
- **Date:** June 3, 2026

### ✅ RESOLVED: Node.js Version Mismatch
- **Original Error:** "You are using Node.js 18.20.8. For Next.js, Node.js version >=20.9.0 is required."
- **Root Cause:** Next.js 16 requires Node 20+ but system was on Node 18
- **Fixed:** Added to package.json, .nvmrc, railway.json
- **Commit:** 1eb2e71
- **Date:** June 3, 2026

---

## Decision Log

**Why we stopped guessing:**
- 7 failed deploys in a row with no progress
- Root cause was Node version, not component architecture
- Built proper project structure to prevent future circles
- Documented everything so next person doesn't waste time

---

**Last Updated:** June 3, 2026
**Reviewed By:** Claude + Agent investigation
