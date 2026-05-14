"""
lib/ceo_orchestrator.py — CEO Agent Orchestrator

The business owner's personal AI Chief of Staff.

The CEO Agent owns TWO channels:
  1. Owner's WhatsApp — the owner messages it naturally, it handles everything
  2. VAPI voice briefings — it calls the owner to deliver verbal reports

How it works:
  Owner: "How are leads looking this week?"
  CEO Agent: understands → dispatches to Lead Agent → synthesises → responds

  Owner: "What did the market do yesterday?"
  CEO Agent: understands → dispatches to Market Scout → synthesises → responds

  Owner: "Briefing please"
  CEO Agent: dispatches to ALL agents → synthesises everything → calls owner via VAPI

The CEO Agent knows the owner's team by name:
  "Marcus found 8 leads this week..."
  "Zara is handling 3 active conversations right now..."
  "Aria flagged a negative review that needs your attention."

Owner-facing WhatsApp is SEPARATE from customer-facing WhatsApp.
  Customer WhatsApp → WhatsApp Agent (handles customers)
  Owner WhatsApp   → CEO Orchestrator (handles the owner)

Setup:
  The owner saves the CEO Agent's Twilio number in their contacts.
  They message it like messaging a Chief of Staff.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY    = os.getenv("ANTHROPIC_API_KEY")
TWILIO_ACCOUNT_SID   = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN    = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")
QASSIM_PHONE         = os.getenv("QASSIM_PHONE")

# ─────────────────────────────────────────────
# INTENT CLASSIFIER
# Understands what the owner is asking
# ─────────────────────────────────────────────

INTENT_MAP = {
    "leads":       [2, 3],   # Lead Gen + WhatsApp Agent
    "calls":       [1],      # Presence Agent
    "whatsapp":    [3],      # WhatsApp Agent
    "messages":    [3],
    "reviews":     [7],      # Reviews Agent
    "reputation":  [7],
    "competitors": [5],      # Competitor Intel
    "market":      [6],      # Market Scout
    "trade":       [6, 11],  # Market Scout + TradeBridge
    "deals":       [11],     # TradeBridge
    "content":     [4],      # Content Machine
    "posts":       [4],
    "retention":   [9],      # Retention Agent
    "customers":   [9, 3],
    "churn":       [9],
    "creative":    [12],     # Creative Studio
    "ads":         [12],
    "jobs":        [8],      # Job Hunter
    "briefing":    "all",    # All agents
    "summary":     "all",
    "report":      "all",
    "overview":    "all",
    "everything":  "all",
    "update":      "all",
}


def classify_intent(message: str) -> list[int] | str:
    """
    Classify what the owner is asking about.
    Returns list of module IDs to query, or "all" for a full briefing.
    """
    lowered = message.lower()

    # Check for full briefing request
    for keyword in ["briefing", "summary", "report", "overview", "everything", "update", "morning"]:
        if keyword in lowered:
            return "all"

    # Match specific intents
    matched = set()
    for keyword, modules in INTENT_MAP.items():
        if keyword in lowered:
            if modules == "all":
                return "all"
            matched.update(modules)

    return list(matched) if matched else "all"


# ─────────────────────────────────────────────
# AGENT RUNNERS
# Each module has a run() function that returns intel
# ─────────────────────────────────────────────

def run_agent(module_id: int, client_id: str, team: list) -> dict:
    """
    Run a specific agent and return its intel report.
    Pulls real data from Airtable where available, simulates for demo.
    """
    from lib.agent_factory import get_agent_for_module, simulate_activity
    agent = get_agent_for_module(team, module_id)
    if not agent:
        return {"module_id": module_id, "status": "not_in_team", "summary": ""}

    # Simulate activity for now — replace with real Airtable pulls
    agent = simulate_activity(agent)
    name  = agent["name"]

    reports = {
        1:  lambda a: f"{name} answered {a['stats']['today']} calls today. {a['recent_activity'][0] if a.get('recent_activity') else 'All quiet.'} No missed calls.",
        2:  lambda a: f"{name} found {a['stats']['today']} new prospects today. {a['recent_activity'][0] if a.get('recent_activity') else ''} Pipeline looking healthy.",
        3:  lambda a: f"{name} handled {a['stats']['today']} WhatsApp conversations. {a['recent_activity'][0] if a.get('recent_activity') else ''} Response rate: excellent.",
        4:  lambda a: f"{name} published {a['stats']['today']} pieces of content today. {a['recent_activity'][0] if a.get('recent_activity') else ''} All scheduled.",
        5:  lambda a: f"{name} monitored your competitors. {a['recent_activity'][0] if a.get('recent_activity') else 'No major changes detected.'}",
        6:  lambda a: f"{name} scanned global markets. {a['recent_activity'][0] if a.get('recent_activity') else 'Markets steady — no urgent signals.'}",
        7:  lambda a: f"{name} checked your reviews. {a['recent_activity'][0] if a.get('recent_activity') else 'No new reviews today.'} Reputation: stable.",
        8:  lambda a: f"{name} scanned opportunities. {a['recent_activity'][0] if a.get('recent_activity') else 'Monitoring active boards.'}",
        9:  lambda a: f"{name} checked customer retention. {a['recent_activity'][0] if a.get('recent_activity') else 'All customers healthy.'} No churn risk flagged.",
        11: lambda a: f"{name} monitored trade deals. {a['recent_activity'][0] if a.get('recent_activity') else 'Watching Africa-China and Africa-Europe corridors.'}",
        12: lambda a: f"{name} produced {a['stats']['today']} creative assets. {a['recent_activity'][0] if a.get('recent_activity') else 'Ready for next brief.'}",
    }

    report_fn = reports.get(module_id)
    summary   = report_fn(agent) if report_fn else f"{name}: {agent.get('last_action', 'Active.')}"

    return {
        "module_id":   module_id,
        "agent_name":  name,
        "avatar":      agent["avatar"],
        "status":      "ok",
        "summary":     summary,
        "stats":       agent["stats"],
    }


def run_all_agents(client_id: str, team: list) -> list[dict]:
    """Run all agents in the team and collect their reports."""
    reports = []
    for agent in team:
        mod_id = agent["module_id"]
        if mod_id == 10:  # Skip CEO agent itself
            continue
        report = run_agent(mod_id, client_id, team)
        if report.get("summary"):
            reports.append(report)
    return reports


# ─────────────────────────────────────────────
# RESPONSE SYNTHESISER
# Turns agent reports into a natural, conversational response
# ─────────────────────────────────────────────

def synthesise_response(
    owner_message: str,
    agent_reports: list[dict],
    team: list,
    business_name: str,
    is_full_briefing: bool = False,
) -> str:
    """
    Uses Claude to synthesise agent reports into a natural response
    the CEO Agent sends back to the owner.
    """
    import anthropic
    client_a = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    from lib.agent_factory import get_ceo_agent
    ceo = get_ceo_agent(team)
    ceo_name = ceo["name"] if ceo else "Your Chief of Staff"

    reports_text = "\n".join([
        f"- {r['avatar']} {r['agent_name']}: {r['summary']}"
        for r in agent_reports
    ])

    if is_full_briefing:
        system = f"""You are {ceo_name}, the AI Chief of Staff for {business_name}.
You are delivering a morning briefing to the business owner via WhatsApp.

Style:
- Be concise — this is WhatsApp, not a report. Max 150 words.
- Use your team members' names (they are named agents, not modules)
- Lead with what's most important
- End with the single most important action the owner needs to take
- Use line breaks for readability
- One emoji max
- Sound like a sharp, trusted advisor — not a chatbot

Do NOT say "As an AI" or similar. You ARE {ceo_name}."""

        prompt = f"""The owner said: "{owner_message}"

Agent reports from the team:
{reports_text}

Deliver the briefing."""

    else:
        system = f"""You are {ceo_name}, the AI Chief of Staff for {business_name}.
You answer the owner's questions by synthesising your team's latest intel.

Style:
- Direct and conversational — this is WhatsApp
- Max 100 words
- Use agent names ("Marcus found...", "Zara handled...")
- Give the actual answer first, context second
- Sound like a trusted advisor who knows the business inside out"""

        prompt = f"""The owner asked: "{owner_message}"

Relevant intel from the team:
{reports_text}

Answer their question directly."""

    try:
        resp = client_a.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            system=system,
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.content[0].text.strip()
    except Exception as e:
        print(f"[CEO] Synthesis error: {e}")
        # Fallback — just concatenate reports
        lines = [f"Here's the latest from the team:\n"]
        for r in agent_reports[:4]:
            lines.append(f"{r['avatar']} {r['summary']}")
        return "\n".join(lines)


# ─────────────────────────────────────────────
# VAPI VOICE BRIEFING
# CEO Agent calls the owner to deliver reports verbally
# ─────────────────────────────────────────────

def deliver_voice_briefing(
    owner_phone: str,
    agent_reports: list[dict],
    team: list,
    business_name: str,
) -> dict:
    """
    Trigger a VAPI outbound call where the CEO Agent verbally briefs the owner.
    owner_phone: "+447847221722" (no whatsapp: prefix)
    """
    from lib.agent_factory import get_ceo_agent
    ceo = get_ceo_agent(team)
    ceo_name = ceo["name"] if ceo else "your AI Chief of Staff"

    # Build the verbal briefing script
    report_lines = []
    for r in agent_reports[:5]:  # Max 5 for a good call length
        report_lines.append(r["summary"])

    briefing_text = ". ".join(report_lines)

    # Build a natural-sounding voice script for VAPI
    voice_script = (
        f"You are {ceo_name}, the AI Chief of Staff for {business_name}. "
        f"You are calling the owner to deliver their daily briefing. "
        f"Be warm but concise. Speak naturally, like a trusted advisor. "
        f"Keep it under 60 seconds total. "
        f"Here is the briefing to deliver: {briefing_text}. "
        f"End by asking if they need anything else or want you to take any action. "
        f"If they say yes or give instructions, acknowledge and confirm you'll handle it."
    )

    try:
        from lib import vapi_client
        call = vapi_client.make_outbound_call(
            to_number=owner_phone,
            assistant_prompt=voice_script,
            metadata={
                "type":     "ceo_briefing",
                "business": business_name,
                "agent":    ceo_name,
            }
        )
        print(f"[CEO] Voice briefing call triggered to {owner_phone} — call_id: {call.get('id')}")
        return {"status": "calling", "call_id": call.get("id"), "agent": ceo_name}
    except Exception as e:
        print(f"[CEO] Voice briefing error: {e}")
        return {"status": "failed", "error": str(e)}


# ─────────────────────────────────────────────
# MAIN — HANDLE OWNER MESSAGE
# Called by /webhook/whatsapp when from_number = owner's number
# ─────────────────────────────────────────────

def handle_owner_message(
    owner_message: str,
    owner_phone: str,
    client_id: str,
    team: list,
    business_name: str,
    respond_via_call: bool = False,
) -> str:
    """
    Main entry point. Called when the business OWNER messages the CEO Agent.

    owner_message:    what the owner asked/said
    owner_phone:      owner's WhatsApp number (whatsapp:+447...)
    client_id:        the client record ID
    team:             list of agent dicts from agent_factory
    business_name:    e.g. "Gromatic"
    respond_via_call: if True, trigger VAPI voice call instead of WhatsApp reply
    """
    print(f"[CEO] Owner message: '{owner_message[:60]}' | client: {client_id}")

    # Classify intent
    intent = classify_intent(owner_message)
    is_full_briefing = (intent == "all")

    # Run relevant agents
    if is_full_briefing:
        reports = run_all_agents(client_id, team)
    else:
        reports = [run_agent(mod_id, client_id, team) for mod_id in intent]
        reports = [r for r in reports if r.get("summary")]

    if not reports:
        # Fallback — general response from CEO Agent
        from lib.agent_factory import get_ceo_agent
        ceo = get_ceo_agent(team)
        return f"I'm on it. Let me check with the team and get back to you. — {ceo['name'] if ceo else 'Your Chief of Staff'}"

    # Synthesise the response
    response_text = synthesise_response(
        owner_message=owner_message,
        agent_reports=reports,
        team=team,
        business_name=business_name,
        is_full_briefing=is_full_briefing,
    )

    # Deliver via WhatsApp (send back to owner)
    from lib.whatsapp_agent import send_whatsapp
    wa_phone = owner_phone if owner_phone.startswith("whatsapp:") else f"whatsapp:{owner_phone}"
    send_whatsapp(wa_phone, response_text)

    # Optionally ALSO trigger a voice call for full briefings
    if respond_via_call and is_full_briefing:
        raw_phone = owner_phone.replace("whatsapp:", "")
        deliver_voice_briefing(raw_phone, reports, team, business_name)

    print(f"[CEO] Response delivered to {owner_phone} ✓")
    return response_text


# ─────────────────────────────────────────────
# PROACTIVE BRIEFING (scheduled — 7am daily)
# ─────────────────────────────────────────────

def run_morning_briefing(
    owner_phone: str,
    client_id: str,
    team: list,
    business_name: str,
    voice: bool = False,
) -> str:
    """
    Proactive morning briefing — not triggered by owner, initiated by schedule.
    Called by morning_briefing.py at 7am.
    """
    return handle_owner_message(
        owner_message="morning briefing",
        owner_phone=owner_phone,
        client_id=client_id,
        team=team,
        business_name=business_name,
        respond_via_call=voice,
    )
