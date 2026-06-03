# Working Memory — Today
# Updated: 2026-05-30

---

## REVENUE STATUS
MRR: £0 — CRITICAL URGENCY
Active deal: SEGGUINÉE (water utility, Guinea) — deployed, WhatsApp blocked on Meta phone number

## TODAY'S PRIORITY
Get a real Guinea (+224) SIM registered with Meta so WhatsApp webhook can receive inbound messages. The Meta test number (+1 555 657-0856) is outbound-only — cannot receive WhatsApp from real users.

## ACTIVE TASKS
- [x] SEGGUINÉE portal deployed — https://segguinee.vercel.app (PIN: 2580)
- [x] WhatsApp webhook code complete — agentic routing, customer context injection, billing reminders, daily briefing, operational data parsing (prod/facture/incident/paiement)
- [x] OpenAI GPT-4o-mini customer inquiry with full Supabase context injection
- [x] Supabase schema live (8 tables: conversations, messages, briefings, staff, production, invoices, incidents, billing_reminders)
- [x] .env fixed — colons converted to equals, SEGGUINEE_DIRECTOR_PHONE added, OPENAI_API_KEY uncommented, duplicate WhatsApp token removed
- [x] Public /privacy and /terms pages live (Meta compliance)
- [ ] **BLOCKER: Get real +224 Guinea phone number registered with Meta** — test number doesn't receive inbound
- [ ] Verify Meta access token is permanent (System User, never expires) vs temporary (24hr expiry)
- [ ] Configure webhook callback URL in Meta: https://segguinee.vercel.app/api/webhook/whatsapp (verify token: Pluggedin)
- [ ] Subscribe to "messages" webhook field in Meta
- [ ] Push code to GitHub
- [ ] Send director the URL + PIN for review once WhatsApp works end-to-end

## WHATSAPP BLOCKER DETAILS
- Meta test number +1 555 657-0856 = outbound API only, cannot receive WhatsApp messages
- Twilio US number +17698881480 exists but Meta verification SMS doesn't arrive (virtual number)
- Solution: Director buys Guinea SIM ($2), registers it in Meta Business Suite, receives verification code directly
- Director's UK number (+447495255315) is set as SEGGUINEE_DIRECTOR_PHONE for commands
- Architecture: Business number (AI agent, +224 Guinea) + Director number (commands, UK)

## ENV STATUS (PluggedIN/.env)
Fixed formatting bugs that would break local dev:
- Colons → equals on all WhatsApp/Supabase lines
- OPENAI_API_KEY uncommented
- SEGGUINEE_DIRECTOR_PHONE=447495255315 added
- Duplicate WHATSAPP_ACCESS_TOKEN line removed

## VIDEO INSIGHTS (watched 2026-05-30)
Video: "Build a WhatsApp AI Agent with Claude Code" — confirmed our architecture is correct
Key finding: Access token MUST be via System User (never expires), not "Generate access token" button (24hr expiry)
We should verify which type we have

## PIPELINE
| Lead | Stage | Next Action |
|------|-------|-------------|
| SEGGUINÉE (Guinea) | Deployed | Director gets Guinea SIM → register Meta → test webhook → close |
| Gromatic (Damian) | Proposal ready | Send (hold until SEGGUINÉE closed) |
| 10 solicitors | Researched | Outreach not started |

## NEXT SESSION
1. Ask: Did the director get a Guinea SIM?
2. If yes: Register it in Meta, configure webhook, test end-to-end
3. If no: Push on why this is the only blocker — everything else is built and waiting
4. Verify access token type (System User permanent vs temporary 24hr)
