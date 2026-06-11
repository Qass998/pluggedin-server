# SEGGUINÉE — Client Operating System
# Updated: 2026-06-06

---

## STATUS: LIVE ✅
Portal live at https://segguinee-portal.vercel.app
Code: github.com/Qass998/segguinee-portal
Airtable: appkTn2GRpIGBFwMU

---

## WHAT SEGGUINÉE IS

Guinea water utility operator. We built their complete digital operating system:
- Operator portal (Next.js 16, Vercel)
- 7 AI agents with direct chat
- Command bar (natural language → executed actions)
- Invoice signing system (WhatsApp → e-sign → PDF)
- Field team coordination
- Airtable as the data backbone

Billing: $2,000 setup + $500/month
First invoice: not yet sent

---

## SESSION START PROTOCOL

1. Read STATUS.md — current state, what's done, what's next
2. Run graphify query if touching code: `graphify-out/graph.json` already built
3. Read ACTIVE_SKILLS.md before writing any code
4. Pull latest: `cd outputs/clients/segguinee/segguinee-portal && git pull origin main`

---

## DEPLOY WORKFLOW

```bash
# Work in /tmp clone (cleaner)
cd /tmp && rm -rf segguinee-portal
git clone https://github.com/Qass998/segguinee-portal.git
cd segguinee-portal

# Make changes, then:
git add -A && git commit -m "description" && git push origin main
vercel --prod --yes
```

---

## KEY FILES

| File | What it does |
|------|-------------|
| src/app/dashboard-client.tsx | Entire portal UI — all panels, command bar, agent chat |
| src/app/api/command/route.ts | AI command engine — interprets + executes director instructions |
| src/app/api/data/invoices/route.ts | Invoice CRUD + WhatsApp send |
| src/app/api/invoices/sign/route.ts | Invoice signing — marks paid, notifies director |
| src/app/sign/[token]/page.tsx | Client-facing signing page |
| src/app/sign/[token]/SignButton.tsx | Sign + download PDF button |
| src/lib/airtable.ts | All Airtable reads/writes — TABLES dict maps names to IDs |
| src/lib/whatsapp.ts | WhatsApp send via Meta Cloud API |

---

## CRITICAL BUGS ALREADY FIXED

1. **singleSelect returns object** — Airtable singleSelect fields return `{name, color}` not a string. All status comparisons use `sel()` helper in command/route.ts
2. **Inter banned** — use DM Sans + JetBrains Mono (Inter = AI fingerprint)
3. **invoices created via command had no Sign_token** — fixed, token generated in CREATE_INVOICE action
4. **Agent chat returned UNKNOWN for conversational questions** — CHAT action added, agent responds in character

---

## AGENTS

All 7 agents in Airtable tblHXVwNrq1bhY6Qn. agent_id field maps to AGENT_META in dashboard-client.tsx for capability display. New agents need both an Airtable record AND a AGENT_META entry.

---

## SKILLS TO USE

Visual changes → pluggedin-design first (DM Sans not Inter, Swiss Rational school)
Any deploy → vercel-deployment skill
Airtable work → airtable-automation skill
Next.js patterns → nextjs-best-practices skill
Before deploy → code-review-and-quality skill
