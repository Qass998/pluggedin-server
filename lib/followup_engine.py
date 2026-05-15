"""
lib/followup_engine.py — Structured Follow-Up Decision Engine

Every follow-up produces a FollowUpDecision — no ad-hoc prompting.
Actions: send_message | wait | close

Pattern from: github.com/eracle/OpenOutreach
Adapted for: PluggedIN stack (Anthropic Claude, Airtable, multi-client)
"""
from __future__ import annotations
import os
import json
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

MAX_ATTEMPTS    = 3
WAIT_HOURS      = {1: 24, 2: 48, 3: 72}   # hours to wait per attempt number

_FOLLOWUP_PROMPT = """You are managing outreach on behalf of {business_name}.

Lead profile:
{profile_summary}

What we know about this lead (conversation facts):
{chat_summary}

Recent conversation (last 6 messages):
{recent_messages}

Outreach attempts so far: {attempts}

Decide ONE action:

1. send_message — write the next message. Be warm, specific, reference their situation.
   Never repeat a previous message. Never be salesy. Max 3 sentences.

2. wait — it is too early to follow up. Set wait_hours to 24, 48, or 72.

3. close — the conversation is done. Set outcome to one of:
   converted | not_interested | wrong_fit | no_budget | has_solution | bad_timing | unresponsive | unknown

Rules:
- After {max_attempts} unanswered messages → close (unresponsive)
- If they said no in any form → close (not_interested) immediately
- If they expressed interest → focus on booking a call, not more pitching
- If they mentioned a competitor they're happy with → close (has_solution)
- Reference specific facts — never send generic messages

Return ONLY valid JSON:
{{
  "action":     "send_message | wait | close",
  "message":    "message text if action=send_message, else null",
  "outcome":    "outcome if action=close, else null",
  "wait_hours": 24 (number if action=wait, else null),
  "reasoning":  "one sentence explaining this decision"
}}"""


def make_followup_decision(
    lead: dict,
    business_name: str,
    recent_messages: list[dict],
    facts: list[str],
) -> dict:
    """
    Produce a FollowUpDecision for a lead.

    lead: dict with at least {id, Name, Stage, Attempts, ICP Score}
    recent_messages: list of {role: "outbound"|"inbound", content: str, sent_at: str}
    facts: list of fact strings from conversation_memory

    Returns:
    {
      "action":     "send_message" | "wait" | "close",
      "message":    str | None,
      "outcome":    str | None,
      "wait_hours": int | None,
      "reasoning":  str,
    }
    """
    attempts = lead.get("Attempts", 0)

    # Hard rule: max attempts → close unresponsive
    if attempts >= MAX_ATTEMPTS:
        return {
            "action":     "close",
            "message":    None,
            "outcome":    "unresponsive",
            "wait_hours": None,
            "reasoning":  f"Max attempts ({MAX_ATTEMPTS}) reached with no response.",
        }

    # Format recent messages
    msg_lines = []
    for m in recent_messages[-6:]:
        role    = "Us" if m.get("role") == "outbound" else "Them"
        content = m.get("content", "")[:200]
        msg_lines.append(f"{role}: {content}")
    recent_str = "\n".join(msg_lines) if msg_lines else "No messages yet."

    # Profile summary
    profile_lines = [
        f"Name: {lead.get('Name') or lead.get('Company') or 'Unknown'}",
        f"Industry: {lead.get('Industry', 'Unknown')}",
        f"Location: {lead.get('Location', '')}",
        f"ICP Score: {lead.get('ICP Score', 'N/A')}",
    ]
    profile_str = "\n".join(profile_lines)

    # Facts
    from lib.conversation_memory import format_facts_for_prompt
    facts_str = format_facts_for_prompt(facts)

    fallback = {
        "action":     "wait",
        "message":    None,
        "outcome":    None,
        "wait_hours": WAIT_HOURS.get(attempts + 1, 72),
        "reasoning":  "Fallback: API unavailable. Scheduled next check.",
    }

    if not ANTHROPIC_API_KEY:
        return fallback

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

        prompt = _FOLLOWUP_PROMPT.format(
            business_name   = business_name,
            profile_summary = profile_str,
            chat_summary    = facts_str,
            recent_messages = recent_str,
            attempts        = attempts,
            max_attempts    = MAX_ATTEMPTS,
        )

        resp = client.messages.create(
            model     = "claude-sonnet-4-6",
            max_tokens= 500,
            messages  = [{"role": "user", "content": prompt}],
        )
        raw  = resp.content[0].text.strip().replace("```json","").replace("```","")
        data = json.loads(raw)

        # Validate action
        if data.get("action") not in {"send_message", "wait", "close"}:
            return fallback

        return {
            "action":     data["action"],
            "message":    data.get("message"),
            "outcome":    data.get("outcome"),
            "wait_hours": data.get("wait_hours"),
            "reasoning":  data.get("reasoning", ""),
        }

    except Exception as e:
        print(f"[FollowupEngine] decision error: {e}")
        return fallback


def execute_decision(
    lead_id: str,
    decision: dict,
    send_fn,
) -> str:
    """
    Execute a FollowUpDecision.
    send_fn(lead_id, message) → called if action=send_message
    Returns the new stage.
    """
    from lib.pipeline_state import mark_contacted, close_lead, get_lead

    action = decision["action"]
    lead   = get_lead(lead_id)
    attempts = (lead.get("Attempts") or 0)

    if action == "send_message":
        msg = decision.get("message", "")
        if msg:
            try:
                send_fn(lead_id, msg)
                mark_contacted(lead_id, attempts + 1)
                print(f"[FollowupEngine] {lead_id} → message sent (attempt {attempts+1})")
                return "PENDING"
            except Exception as e:
                print(f"[FollowupEngine] send failed: {e}")
                return "PENDING"

    elif action == "close":
        outcome = decision.get("outcome", "unknown")
        note    = decision.get("reasoning", "")
        close_lead(lead_id, outcome, note)
        return "COMPLETED" if outcome == "converted" else "FAILED"

    # wait — do nothing, let scheduler handle timing
    print(f"[FollowupEngine] {lead_id} → wait {decision.get('wait_hours',24)}h ({decision.get('reasoning','')})")
    return lead.get("Stage", "PENDING")


def next_contact_time(attempt_number: int) -> datetime:
    """Returns the UTC datetime when to next contact based on attempt number."""
    hours = WAIT_HOURS.get(attempt_number, 72)
    return datetime.now(timezone.utc) + timedelta(hours=hours)
