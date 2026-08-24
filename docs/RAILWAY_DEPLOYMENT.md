# PluggedInOS on Railway

## Project topology

Create one Railway project with four service types sharing the same private network:

1. **Postgres** — add Railway Postgres and expose `DATABASE_URL` to the application services.
2. **deal-api** — repository root, config path `/railway.json`.
3. **deal-worker** — same repository, config path `/railway.worker.json`.
4. **deal-collector** — same repository, config path `/railway.cron.json`, with a UTC cron schedule and one `DEAL_DESK` value per collector service.

Do not deploy `backend/server.js`; it is the legacy acquisition API. FastAPI is the single V1 backend.

## Required variables

Set these as Railway sealed variables; never commit their values:

- `DATABASE_URL` — reference the Railway Postgres variable.
- `PLUGGEDIN_INTERNAL_API_KEY` — long random secret for internal bearer authentication.
- `PLUGGEDIN_TENANT_ID` — UUID for PluggedIN's internal tenant.
- `ALLOW_ACCEPTANCE_FIXTURES=false` — true only for an explicit test environment.
- Provider credentials only when the corresponding live source adapter is installed.

Every protected API request must include:

```text
Authorization: Bearer <PLUGGEDIN_INTERNAL_API_KEY>
X-PluggedIn-Tenant: <PLUGGEDIN_TENANT_ID>
```

## Collector and worker behavior

Railway cron starts a short-lived process that inserts a queued `agent_jobs` record and exits. The worker claims jobs using `FOR UPDATE SKIP LOCKED`, preventing duplicate execution across worker replicas. Live jobs fail closed until a live source provider is explicitly wired; acceptance fixtures never masquerade as live data.

Start with one collector service per desk on a conservative schedule. Railway skips overlapping cron executions, so collectors enqueue work rather than performing long research inline.

## Data protection

- Enable daily Railway volume backups before production collection.
- Add point-in-time recovery before outreach begins.
- Schedule an off-platform `pg_dump` restore drill.
- Require `tenant_id` in every repository query.
- Replace the initial schema loader with versioned migrations before the second production schema change.

## Deployment boundary

Repository configuration does not provision or deploy anything by itself. Merge, Railway project creation, database provisioning, secrets, and deployment remain separate human-approved actions.

