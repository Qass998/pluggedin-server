# PluggedIN — Orchestration Architecture
# How agents actually run, communicate, and coordinate.
# Version 1.0 | April 2026

---

## THE CORE QUESTION

You have files defining what agents should do.
You have lib/ scripts that wrap every API.
You have memory files and SOPs.

But who starts the agents? How do they talk to each other?
How does the Lead Gen Agent hand off to the CEO Agent?

This document answers that.

---

## THE ARCHITECTURE IN ONE SENTENCE

Claude Code is the agent runtime.
Airtable is the message bus between agents.
A scheduled Python script is the conductor.
Twilio WhatsApp is the delivery channel to Qassim.

---

## HOW AGENTS COMMUNICATE (THE MESSAGE BUS)

Agents do NOT call each other directly.
They speak through Airtable.

This is intentional:
→ Every action is logged and auditable
→ If one agent fails, others still run
→ Qassim can inspect any agent's output at any time
→ No tight coupling — agents are independent

THE FLOW:

Agent A runs a task
    → writes result to Airtable table
    → marks status: "complete"

Agent B runs next
    → reads Agent A's Airtable output
    → builds on it
    → writes its own result

CEO Agent runs
    → reads all its domain tables
    → compiles summary block
    → writes to: CEOReports table

Chief of All Chiefs runs
    → reads all CEOReports rows
    → synthesises into one briefing
    → sends via Twilio WhatsApp to Qassim

Qassim replies GO
    → Execution agents run approved actions

---

## THE THREE LAYERS

LAYER 1 — SCHEDULER (what starts everything)
A cron job on your Mac runs a Python script at set times.
The script imports Claude Code subagents or calls Claude API directly.
No server needed. Your Mac runs it while you sleep.

LAYER 2 — AGENT RUNTIME (what does the work)
Claude Code (primary) — each agent is a Claude Code session
reading its specific files + running its lib/ scripts.
Claude API (direct) — for simpler tasks: call claude-haiku-4-5
with the agent's prompt + data directly in Python.

LAYER 3 — DATA LAYER (how agents communicate)
Airtable is the single source of truth.
Every agent reads from and writes to Airtable.
This is the memory that persists between runs.

---

## THE DAILY CONDUCTOR (orchestrator.py)

One Python script runs the entire day.
It calls each agent in sequence.
Agents write to Airtable. Next agents read from Airtable.

```
04:00 → knowledge_agent.run()
05:00 → opportunity_engine.run()
05:30 → ecommerce_agent.run()
06:00 → lead_gen_ceo.compile()
         ecommerce_ceo.compile()
         content_ceo.compile()
         agritrade_ceo.compile()
06:30 → chief_of_all_chiefs.synthesise()
07:00 → send_whatsapp_briefing(to=QASSIM_PHONE)
07:01 → wait_for_go_command()
07:01+ → execution_agents.run(approved_actions)
```

For CLIENT agents (runs separately per client):
```
06:30 → [ClientName]_ceo.compile()
07:00 → send_whatsapp_briefing(to=CLIENT_PHONE)
```

---

## HOW EACH AGENT ACTUALLY RUNS

TWO MODES depending on complexity:

MODE A — DIRECT API (simple data tasks, Haiku model)
Used for: logging, scraping, scoring, formatting
The Python script calls Anthropic API directly with a prompt.
Agent reads data, processes it, writes result to Airtable.
Fast. Cheap. No Claude Code session needed.

```python
import anthropic
client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1000,
    system="You are the Opportunity Engine for PluggedIN...",
    messages=[{"role": "user", "content": f"Score these opportunities: {data}"}]
)
# Parse response, write to Airtable
```

MODE B — CLAUDE CODE SUBAGENT (complex multi-step tasks)
Used for: research, content creation, SOP execution
Claude Code spawns a subagent with full file access.
Subagent reads its agent file, runs lib/ scripts, logs results.

```bash
claude --print "Read live/agents/knowledge-agent.md and execute 
today's knowledge acquisition run. Log results to Airtable."
```

ROUTING RULE:
Haiku (Mode A): data tasks, logging, scoring, monitoring
Sonnet (Mode B): research, writing, complex decisions
Opus: Chief of All Chiefs synthesis, major strategic decisions

---

## THE AIRTABLE TABLES NEEDED (message bus)

PLUGGEDIN LIVE BASE (AIRTABLE_BASE_PLUGGEDIN):

Agent communication tables:
→ KnowledgeLog — Knowledge Agent daily output
→ Opportunities — Opportunity Engine scored results
→ CEOReports — One row per business per day (all CEO outputs)
→ ApprovedActions — What Qassim said GO to
→ ExecutionLog — What was actually executed

Business operation tables:
→ Leads (LeadGenPipeline) — all 6 verticals
→ LeadBuyers — solicitors, plumbers etc. who buy leads
→ Products — ecommerce product tracking
→ Businesses — PluggedIN Live portfolio
→ AgriTrade (Producers + Buyers + Deals)
→ YouTubeChannels + ContentPipeline
→ RevenueLog — every revenue event

CLIENT BASE (one per client, e.g. AIRTABLE_BASE_GROMATIC):
→ Pipeline — lead pipeline
→ Jobs — active delivery
→ Customers — customer profiles
→ Reviews — Google review log
→ Invoices — invoice tracking
→ Complaints — CS log
→ KPIs — daily metrics
→ StaffSubmissions — portal submissions

---

## THE GO COMMAND HANDLER

After Qassim receives the briefing and replies GO,
something needs to receive that reply and trigger execution.

MECHANISM: Twilio webhook → Python Flask endpoint → execution

1. Qassim replies "GO" to the WhatsApp briefing
2. Twilio receives the reply and fires a webhook to a URL
3. A small Flask server running locally (or on a cheap VPS) catches it
4. Checks message content: "GO" → run all pending approved actions
5. "DECISIONS" → send the decisions list back
6. "PAUSE [X]" → pause a specific business/module

For now (before revenue) — simpler version:
→ Skip the webhook
→ Qassim sends GO and manually triggers orchestrator.py
→ Or: set a schedule where execution runs at 07:30 regardless
   (Qassim pauses manually if needed before that time)

Full webhook version: build in Month 2 when first client revenue lands.

---

## SETUP — WHAT YOU NEED TO BUILD THIS

See docs/setup-checklist.md for the exact step-by-step.

Short version:
1. Fill .env API keys (Anthropic, Airtable, VAPI, Twilio, Apify)
2. Create Airtable bases with the right tables
3. Install Python deps (pip install -r requirements.txt)
4. Create VAPI assistants (receptionist, qualifier, onboarding)
5. Set up cron job on Mac to run orchestrator.py at 04:00
6. Test one agent end-to-end (Knowledge Agent is safest first)
7. Layer in agents one at a time

---

## WHAT RUNS WHERE

YOUR MAC (for now):
→ orchestrator.py (cron job, runs daily)
→ Claude Code sessions (spawned by orchestrator)
→ All lib/ Python scripts
→ Local .env with API keys

CLOUD (external services you pay for):
→ Airtable (message bus + CRM)
→ VAPI (voice calls)
→ Twilio (WhatsApp)
→ Anthropic API (agent intelligence)
→ Apify (scraping)
→ Creatomate (video/image rendering)

WHEN TO MOVE TO A SERVER (Month 3):
When Mac reliability becomes a problem (Mac asleep = agents don't run).
Move orchestrator.py to a £5/month VPS (Hetzner or DigitalOcean).
Same code. Just runs 24/7 reliably.

---

## AGENT-TO-AGENT COMMUNICATION — WORKED EXAMPLE

Lead Gen Agent → CEO Agent → Chief of All Chiefs → Qassim

STEP 1: Lead Gen Agent runs (07:30, after GO)
```python
# Finds 5 qualified leads for PlumbRight
leads = apify_client.search_google_maps("plumber needed London")
scored = score_leads(leads)  # returns list with scores
for lead in scored:
    if lead["score"] >= 70:
        airtable_client.log_lead(...)  # writes to Airtable:Leads
        deliver_to_buyer(lead)         # emails matched buyer
# Writes daily summary to Airtable:CEOReports
# Row: {business: "PlumbRight", date: today, leads_found: 5, delivered: 3, revenue: 105}
```

STEP 2: Lead Gen CEO Agent compiles (next 06:00)
```python
# Reads all 6 verticals from Airtable:CEOReports for today
rows = airtable.get(table="CEOReports", filter="business IN lead_gen_verticals")
summary = claude_haiku.summarise(rows)
# Writes one consolidated CEO report row:
# {domain: "LeadGen", date: today, summary: "...", revenue: 105, flags: []}
```

STEP 3: Chief of All Chiefs synthesises (06:30)
```python
# Reads ALL CEO report rows for today
all_reports = airtable.get(table="CEOReports", filter="date = today")
briefing = claude_opus.synthesise(all_reports, format="whatsapp_briefing")
# Output: The full WhatsApp message Qassim reads at 7am
```

STEP 4: Briefing delivered (07:00)
```python
twilio_client.send_whatsapp(to=QASSIM_PHONE, message=briefing)
```

Every piece of this is traceable. Every number came from Airtable.
If something looks wrong in the briefing, Qassim can open Airtable
and see exactly which agent wrote what.

---

## THE CLIENT AGENT LOOP (simpler version)

For a client like Gromatic:

Pipeline Agent runs (after GO, daily):
1. Reads Airtable:Pipeline (Gromatic base)
2. Checks which leads need follow-up today
3. Drafts and sends follow-up emails (Gmail MCP)
4. Logs all actions back to Airtable
5. Writes daily summary to CEOReports

Gromatic CEO Agent compiles (06:30):
1. Reads Airtable:Pipeline + CEOReports for today
2. Generates Damian's morning briefing
3. Sends via Twilio to Damian's WhatsApp at 07:00

Damian replies GO → his pipeline runs for the day.

PluggedIN's CEO Agent reads Gromatic's CEO Report:
→ Included in Qassim's portfolio view
→ Revenue from Gromatic visible in Qassim's briefing

---

## WHAT TO BUILD FIRST (in order)

1. orchestrator.py — the conductor
2. Airtable tables — the message bus
3. knowledge_agent.py — safest first test (no outreach, no spend)
4. opportunity_engine.py — scoring and logging only
5. lead_gen_agent.py (PlumbRight only) — first revenue test
6. chief_of_all_chiefs.py — once 2+ agents producing data
7. whatsapp_delivery.py — once briefing is worth sending
8. client_pipeline_agent.py — once Gromatic signs
