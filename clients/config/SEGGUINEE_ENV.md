# SEGGUINÉE Environment Variables

## Railway Production Environment

Set these in Railway dashboard → Project Settings → Environment:

```env
# Airtable
AIRTABLE_TOKEN=pat_xxxxx...
AIRTABLE_BASE_SEGGUINEE=appXXXX...

# Node
NODE_ENV=production

# Deployment
NIXPACKS_NODE_VERSION=20
```

---

## Where to Get Values

### AIRTABLE_TOKEN
- Go to airtable.com → Account → Personal access tokens
- Create new token with scopes:
  - `data.records:read`
  - `data.records:write`
  - `schema.bases:read`
- Copy full token value

### AIRTABLE_BASE_SEGGUINEE
- Go to airtable.com → SEGGUINEE base
- Click Share → Copy base ID from URL or settings
- Format: `appXXXXXXXXXXXXXX`

---

## Local Development (.env.local)

For `npm run dev`, create `.env.local` in portal folder:

```env
AIRTABLE_TOKEN=<same-as-above>
AIRTABLE_BASE_SEGGUINEE=<same-as-above>
NODE_ENV=development
```

---

## Never Commit Secrets

- .env.local is git-ignored
- SEGGUINEE_ENV.md has no actual values (this is a template)
- Only paste actual tokens into Railway dashboard, never into code

