---
name: open-outreach
description: >
  Pipeline Agent enhancement patterns extracted from OpenOutreach (1.7k stars).
  Covers lead lifecycle state machine, fact-based conversation memory,
  structured follow-up decisions, and ICP confidence gating.
  SKIP: LinkedIn browser automation, email sending, lead finding — covered by Apify/Gmail/Vibe.
---

# Open-Outreach Pipeline Patterns

Extracted from github.com/eracle/OpenOutreach. Only the patterns we were missing.
Adapted to PluggedIN stack: Airtable (not SQLite), Claude (not configurable LLM), Anthropic SDK.

---

## PATTERN 1 — Lead State Machine

Every lead has a lifecycle. Never skip states. Track in Airtable `Leads` table as `Stage` field.

```
QUALIFIED → READY → PENDING → CONNECTED → COMPLETED
                                        ↘ FAILED
```

**Stage definitions:**
- `QUALIFIED` — passed ICP scoring, confidence ≥ threshold
- `READY` — approved to contact (confidence gate passed)
- `PENDING` — connection/message sent, awaiting response
- `CONNECTED` — responded, conversation active
- `COMPLETED` — closed (any outcome)
- `FAILED` — unresponsive after max attempts, or disqualified mid-conversation

**Outcome field** (set when COMPLETED or FAILED):
`converted | not_interested | wrong_fit | no_budget | has_solution | bad_timing | unresponsive | unknown`

**Rules:**
- `Lead.disqualified = True` = permanent exclusion — never re-enter pipeline
- LLM rejections during conversation → FAILED + `wrong_fit` outcome
- Unanswered after 3 attempts → FAILED + `unresponsive` outcome
- Always write state transitions to Airtable — never hold state only in memory

**Airtable fields required:**
`Stage (single select) | Outcome (single select) | Disqualified (checkbox) | Attempts (number) | Last Contacted (date) | Connected At (date)`

---

## PATTERN 2 — Fact-Based Conversation Memory

Each lead has a `chat_summary` — a JSON list of facts extracted from the conversation.
Facts are ADD/UPDATE/DELETE operations, not appended transcripts.

```python
# Structure stored in Airtable Lead record — Chat Summary field (long text, JSON)
chat_summary = [
  {"fact": "works at a 20-person law firm", "confidence": "high"},
  {"fact": "currently using a VA for inbound calls", "confidence": "medium"},
  {"fact": "decision maker is the managing partner", "confidence": "high"},
  {"fact": "budget: £500-800/month range mentioned", "confidence": "low"},
]
```

**Extraction prompt (use with Claude Haiku):**
```
You are extracting facts about a prospect from their messages.
Read the new messages and the existing fact list.
Return JSON with operations: {"add": [...], "update": [...], "delete": [...]}
Only extract facts ABOUT THE LEAD — never extract seller messages as facts.
Facts should be: company size, role, pain, budget signals, timeline, objections, interest level.
```

**Rules:**
- Only extract from INBOUND messages (lead's words) — never seller messages
- One re-scrape per lead lifetime for profile enrichment
- Combine profile summary + chat summary + last 6 messages when building follow-up context
- Store as JSON string in Airtable — parse on read

---

## PATTERN 3 — Follow-Up Decision Engine

Every follow-up produces a structured decision. No ad-hoc prompting.

```python
# FollowUpDecision — one of three actions
decision = {
  "action": "send_message",   # send_message | wait | close
  "message": "...",           # populated if action == send_message
  "outcome": None,            # populated if action == close (converted|not_interested|...)
  "reasoning": "...",         # always populated — why this decision
  "wait_hours": None,         # populated if action == wait
}
```

**Decision prompt (use with Claude Sonnet):**
```
You are managing outreach for {business_name}.

Lead profile: {profile_summary}
Conversation facts: {chat_summary}
Last 6 messages: {recent_messages}
Attempts so far: {attempts}

Decide ONE action:
1. send_message — write the next message (warm, specific, references their situation)
2. wait — too soon to follow up (return wait_hours: 24/48/72)
3. close — conversation is done (return outcome: converted/not_interested/wrong_fit/...)

Rules:
- Never send the same message twice
- After 3 unanswered messages → close (unresponsive)
- If they expressed interest → move toward booking, not more pitching
- If they said no → close immediately (not_interested)
- Reference specific facts from their profile — never generic messages

Return JSON only: {"action": "...", "message": "...", "outcome": "...", "reasoning": "...", "wait_hours": null}
```

**Rate limiting:**
- connect attempt: wait 24h before checking response
- follow-up #1: 48h after connect
- follow-up #2: 72h after #1
- follow-up #3 (final): 96h after #2
- After 3 unanswered → mark FAILED + unresponsive

---

## PATTERN 4 — ICP Confidence Gating

Don't contact a lead until confidence is high enough. Two-stage gate:

**Stage 1 — Score (0-100):**
```python
icp_score = {
  "industry_fit":    0-25,   # matches target industries
  "size_fit":        0-25,   # 5-50 staff
  "role_fit":        0-25,   # decision maker or strong influencer
  "signal_strength": 0-25,   # job posting, funding, review complaint, etc.
}
total = sum(icp_score.values())
```

**Stage 2 — Gate:**
- Score < 60 → discard
- Score 60-79 → `QUALIFIED`, needs manual review before advancing
- Score ≥ 80 → `QUALIFIED`, auto-advance to `READY`

**Rule:** Never send outreach to a lead with score < 60. Flag leads 60-79 for human approval.

---

## PATTERN 5 — Reconciliation (Self-Healing Queue)

When the task queue is idle, scan all active leads and recreate missing tasks.
This means crashed tasks auto-recover without manual intervention.

```python
def reconcile_pipeline(client_id: str):
    """
    Walk all active leads. For any lead in a non-terminal state
    with no pending follow-up task, recreate the task.
    Terminal states: COMPLETED, FAILED, disqualified.
    """
    active_stages = ["READY", "PENDING", "CONNECTED"]
    leads = get_leads_by_stage(client_id, active_stages)
    for lead in leads:
        if not has_pending_task(lead["id"]):
            schedule_next_action(lead)
```

Run reconciliation:
- On server startup
- Every time the task queue goes idle
- Never more than once per 30 minutes

---

## Implementation Guide for PluggedIN

### Files to create/enhance:
- `lib/pipeline_state.py` — state machine + transitions + outcome tracking
- `lib/conversation_memory.py` — fact extraction + Airtable storage
- `lib/followup_engine.py` — FollowUpDecision + rate limiting
- `lib/icp_gate.py` — confidence scoring + gating logic

### Airtable fields to add to Leads table:
```
Stage            single select: QUALIFIED | READY | PENDING | CONNECTED | COMPLETED | FAILED
Outcome          single select: converted | not_interested | wrong_fit | no_budget | has_solution | bad_timing | unresponsive | unknown
ICP Score        number (0-100)
Attempts         number
Disqualified     checkbox
Last Contacted   date
Chat Summary     long text (JSON)
Profile Summary  long text (JSON)
Next Action At   date
```

### Stack mapping:
| OpenOutreach | PluggedIN |
|---|---|
| Django/SQLite | Airtable via `lib/airtable_client.py` |
| Playwright/Voyager | Apify MCP + Vibe Prospecting |
| Configurable LLM | Anthropic Claude (Haiku for facts, Sonnet for decisions) |
| Task model | In-memory queue + Airtable `Next Action At` field |
| Django Admin | Portal dashboard |

### What NOT to implement from OpenOutreach:
- Browser automation (Playwright, stealth plugins) → use Apify
- LinkedIn Voyager API scraping → use Vibe Prospecting
- Email sending → use Gmail MCP
- Lead finding → use Apollo, Vibe, Apify
- Django CRM → use Airtable
