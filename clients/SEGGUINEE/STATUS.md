# SEGGUINÉE Portal — Status
# Updated: 2026-06-06 | Status: LIVE ✅

---

## WHERE EVERYTHING IS

| Asset | Location |
|-------|----------|
| Code | github.com/Qass998/segguinee-portal |
| Local copy | ~/Documents/AI-Agency/PluggedIN/outputs/clients/segguinee/segguinee-portal/ |
| Live URL | https://segguinee-portal.vercel.app |
| Airtable base | appkTn2GRpIGBFwMU (SEGGUINÉE OS) |
| Vercel project | qass998s-projects/segguinee-portal |

---

## HOW TO RESUME NEXT SESSION

```bash
# 1. Pull latest code
cd ~/Documents/AI-Agency/PluggedIN/outputs/clients/segguinee/segguinee-portal
git pull origin main

# 2. Make changes, test, deploy
vercel --prod --yes
# (runs from the portal folder or /tmp clone)
```

Key context for Claude:
- Read clients/SEGGUINEE/CLAUDE.md first
- Graphify map at graphify-out/graph.json — query before touching code
- All skills in skills/ — read ACTIVE_SKILLS.md before building

---

## WHAT IS BUILT ✅

### Portal (Next.js 16, Vercel)
- PIN login → cookie session
- DM Sans + JetBrains Mono (Inter banned — AI fingerprint)
- Swiss Rational design system, dark theme

### 6 Tabs
1. **Vue d'ensemble** — KPI strip, agent activity feed, quick actions, recent invoices, active project cards
2. **Production** — readings table + add form + delete
3. **Facturation** — invoices + filter by status + add form + delete + WhatsApp send
4. **Incidents** — list + report form + delete
5. **Projets** — project cards with budget progress bars + add form + delete
6. **Agents IA** — 7 agent cards with role, capability chips, OpenAI chat per agent

### Command Bar (persistent, top of every screen)
- Director types French instructions → OpenAI executes
- Every command logged to Airtable `tasks` table
- 12 action types: CREATE_INVOICE, SEND_REMINDER, LOG_INCIDENT, RESOLVE_INCIDENT, ADD_PRODUCTION, DISPATCH_TEAM, SUMMARIZE, DAILY_BRIEFING, BOARD_REPORT, SEND_INVOICE_LINK, SEND_WHATSAPP, CHAT
- Agent responds in character when chatting

### 7 AI Agents (Airtable agents_log: tblHXVwNrq1bhY6Qn)
| Name | agent_id | Role |
|------|----------|------|
| Chef de Cabinet | briefing | Daily briefing + dispatches |
| Analyste Stratégique | analyste | KPIs + reports |
| Contrôleur de Gestion | finance | Board reports + financial alerts |
| Contrôleur de Créances | recouvrement | Collections + invoice links |
| Directeur du Développement | croissance | Expansion + tenders |
| Coordinateur Opérationnel | terrain | Field dispatch + missions |
| Responsable Clientèle | clientele | Customer portal + communications |

### Invoice Signing (DocuSign-style)
- Create invoice → client gets WhatsApp with link
- Client opens /sign/[token] → signs → director gets WhatsApp notification
- Notification includes link to signed document
- Signed doc page has "Télécharger PDF" (browser print)

---

## AIRTABLE TABLES

| Table | ID | Used for |
|-------|----|---------|
| WA_Invoices | tblKZJ4KRxVQDnmW8 | Invoices (lib key: "invoices") |
| Production | tbl9XOepDJEeVg8IN | Production readings |
| Incidents | tbl24E7JnKZPZJM08 | Incidents |
| Projets | tblyCYVNIDHjRtazG | Projects |
| Agents_Log | tblHXVwNrq1bhY6Qn | Agent status + insights |
| Staff | tbl8StduMMH4p6i6n | Field team (Name, Phone, Role) |
| Tasks | tblmEMnWlhhsQy2sK | Director commands + history |
| Conversations | tblPfNxS1NI1PltHQ | WhatsApp conversations |
| Messages | tblrWWPlhX1xn8P4X | WhatsApp messages |

CRITICAL BUG FIX (already applied): singleSelect fields return as {name, color} objects from Airtable. Use `sel()` helper in command/route.ts to normalise before comparing status strings.

---

## ENV VARS (Vercel)

```
AIRTABLE_TOKEN=✅ set
SEGGUINEE_AIRTABLE_BASE=appkTn2GRpIGBFwMU ✅
OPENAI_API_KEY=✅ set
WHATSAPP_PHONE_NUMBER_ID=✅ set
WHATSAPP_ACCESS_TOKEN=✅ set
SEGGUINEE_DIRECTOR_PHONE=⚠️ update with real director number
WHATSAPP_VERIFY_TOKEN=Pluggedin
NEXT_PUBLIC_BASE_URL=https://segguinee-portal.vercel.app
```

---

## WHAT TO BUILD NEXT

### High priority
- [ ] Real phone numbers in sample data (fake numbers = WhatsApp fails)
- [ ] Update SEGGUINEE_DIRECTOR_PHONE in Vercel env
- [ ] Production charts (volume trend by zone over time) — use canvas-design skill
- [ ] Invoice status update from portal (mark as paid)
- [ ] Mobile responsive layout (sidebar breaks on phones)

### Medium priority
- [ ] Incident status update (resolve from portal, not just command bar)
- [ ] Real-time auto-refresh (currently static until page reload)
- [ ] PDF export for board report (currently text via WhatsApp)
- [ ] Conversations tab (WhatsApp thread view)

### Billing
- Portal: $2,000 setup + $500/month ← this is what SEGGUINÉE pays
- First invoice not yet sent
