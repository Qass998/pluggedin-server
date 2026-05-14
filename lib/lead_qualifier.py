"""
lib/lead_qualifier.py — AI Lead Qualification Engine
=====================================================
Powers the embedded website chat widget.

Flow:
  Visitor opens chat → AI greets warmly → collects name, need, urgency,
  contact info → scores the lead → saves to Airtable → fires WhatsApp
  alert to business owner with lead summary.

Multi-client:
  Each client has their own config (business name, services, tone).
  The widget passes client_id with every message.

Lead stages:
  GREETING   → EXPLORING → QUALIFYING → CONTACT → BOOKED / HANDOFF
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY    = os.getenv("ANTHROPIC_API_KEY")
TWILIO_ACCOUNT_SID   = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN    = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
AIRTABLE_TOKEN       = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE        = os.getenv("AIRTABLE_BASE_PLUGGEDIN")

# ─────────────────────────────────────────────
# IN-MEMORY SESSION STORE
# keyed by session_id (uuid from widget)
# ─────────────────────────────────────────────
_sessions: dict = {}


def _get_session(session_id: str, client_config: dict) -> dict:
    if session_id not in _sessions:
        _sessions[session_id] = {
            "session_id":   session_id,
            "client_id":    client_config.get("client_id", "default"),
            "messages":     [],
            "lead":         {},          # collected lead data
            "stage":        "greeting",
            "started_at":   datetime.utcnow().isoformat(),
            "qualified":    False,
            "notified":     False,
        }
    return _sessions[session_id]


# ─────────────────────────────────────────────
# SYSTEM PROMPT BUILDER
# ─────────────────────────────────────────────

def _build_system_prompt(client_config: dict, lead: dict) -> str:
    business_name = client_config.get("business_name", "us")
    services      = client_config.get("services", "our services")
    industry      = client_config.get("industry", "business")
    tone          = client_config.get("tone", "professional yet warm")
    agent_name    = client_config.get("agent_name", "AI Assistant")
    cal_link      = client_config.get("cal_link", "")
    owner_name    = client_config.get("owner_name", "the team")

    known = ""
    if lead.get("name"):      known += f"\n- Visitor name: {lead['name']}"
    if lead.get("need"):      known += f"\n- What they need: {lead['need']}"
    if lead.get("urgency"):   known += f"\n- Urgency: {lead['urgency']}"
    if lead.get("email"):     known += f"\n- Email: {lead['email']}"
    if lead.get("phone"):     known += f"\n- Phone: {lead['phone']}"

    booking = f"\n\nWhen they're ready to move forward, share this booking link: {cal_link}" if cal_link else ""

    return f"""You are {agent_name}, the AI assistant for {business_name} — a {industry} business.
Your tone is {tone}. Keep messages concise (2-4 sentences max). Use line breaks, never walls of text.

Your goal: qualify this visitor as a lead by naturally collecting:
1. Their name (ask early, warmly)
2. What they're looking for / their problem
3. Timeline / urgency
4. Contact info (email or phone) — only after they've expressed interest

Services you offer: {services}

What you already know about this visitor:{known if known else " Nothing yet — greet them warmly."}
{booking}

Rules:
- Never ask more than one question at a time
- Be conversational, not robotic — like a helpful human receptionist
- When you have their name + need + contact info, tell them {owner_name} will follow up shortly
- If they ask to speak to someone, offer the call button or booking link
- Never make up prices or specific details you don't know — offer to connect them with the team
- Extract and remember any info they share even if you didn't ask for it

Respond in the language the visitor uses."""


# ─────────────────────────────────────────────
# LEAD DATA EXTRACTOR
# Parses the conversation to pull structured data
# ─────────────────────────────────────────────

def _extract_lead_data(messages: list, existing_lead: dict) -> dict:
    """Use Claude to extract structured lead data from conversation so far."""
    conversation = "\n".join([
        f"{'Visitor' if m['role'] == 'user' else 'Agent'}: {m['content']}"
        for m in messages[-10:]  # last 10 messages
    ])

    prompt = f"""Extract any lead information from this conversation. Return JSON only.

Conversation:
{conversation}

Return a JSON object with these fields (use null if not mentioned):
{{
  "name": "visitor's name or null",
  "need": "what they're looking for, their problem or goal, or null",
  "urgency": "their timeline or urgency level or null",
  "email": "email address or null",
  "phone": "phone number or null",
  "budget": "budget if mentioned or null",
  "notes": "any other useful context or null"
}}

Return only the JSON, no explanation."""

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key":         ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type":      "application/json",
            },
            json={
                "model":      "claude-haiku-4-5-20251001",
                "max_tokens": 300,
                "messages":   [{"role": "user", "content": prompt}],
            },
            timeout=15,
        )
        text = resp.json()["content"][0]["text"].strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        extracted = json.loads(text)
        # Merge with existing, don't overwrite with nulls
        merged = dict(existing_lead)
        for k, v in extracted.items():
            if v is not None:
                merged[k] = v
        return merged
    except Exception:
        return existing_lead


def _is_qualified(lead: dict) -> bool:
    """A lead is qualified when we have name + need + contact."""
    return bool(
        lead.get("name") and
        lead.get("need") and
        (lead.get("email") or lead.get("phone"))
    )


# ─────────────────────────────────────────────
# AIRTABLE — Save lead
# ─────────────────────────────────────────────

def _save_lead_to_airtable(session: dict, client_config: dict):
    """Save qualified lead to Airtable Leads table."""
    if not AIRTABLE_TOKEN or not AIRTABLE_BASE:
        return

    lead   = session["lead"]
    fields = {
        "Name":        lead.get("name", "Unknown"),
        "Need":        lead.get("need", ""),
        "Urgency":     lead.get("urgency", ""),
        "Email":       lead.get("email", ""),
        "Phone":       lead.get("phone", ""),
        "Budget":      lead.get("budget", ""),
        "Notes":       lead.get("notes", ""),
        "Source":      "Website Chat Widget",
        "Client":      client_config.get("business_name", ""),
        "Session ID":  session["session_id"],
        "Captured At": datetime.utcnow().isoformat(),
        "Status":      "New Lead",
    }

    try:
        requests.post(
            f"https://api.airtable.com/v0/{AIRTABLE_BASE}/Leads",
            headers={
                "Authorization": f"Bearer {AIRTABLE_TOKEN}",
                "Content-Type":  "application/json",
            },
            json={"fields": fields},
            timeout=10,
        )
    except Exception:
        pass


# ─────────────────────────────────────────────
# WHATSAPP — Notify business owner
# ─────────────────────────────────────────────

def _notify_owner(session: dict, client_config: dict):
    """Send WhatsApp alert to business owner when lead is qualified."""
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        return

    owner_phone = client_config.get("owner_phone") or os.getenv("QASSIM_PHONE")
    if not owner_phone:
        return

    lead         = session["lead"]
    business     = client_config.get("business_name", "your business")
    contact_line = f"📧 {lead['email']}" if lead.get("email") else f"📱 {lead.get('phone', 'no contact yet')}"

    message = f"""🔥 *New Lead — {business}*

👤 *Name:* {lead.get('name', 'Unknown')}
💬 *Needs:* {lead.get('need', 'Not specified')}
⏰ *Urgency:* {lead.get('urgency', 'Not specified')}
{contact_line}
{f"💰 Budget: {lead['budget']}" if lead.get('budget') else ""}
{f"📝 Notes: {lead['notes']}" if lead.get('notes') else ""}

_Via website chat widget · {datetime.utcnow().strftime('%H:%M UTC')}_"""

    wa_to = owner_phone if owner_phone.startswith("whatsapp:") else f"whatsapp:{owner_phone}"

    try:
        requests.post(
            f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json",
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            data={
                "From": TWILIO_WHATSAPP_FROM,
                "To":   wa_to,
                "Body": message,
            },
            timeout=10,
        )
    except Exception:
        pass


# ─────────────────────────────────────────────
# MAIN CHAT HANDLER
# ─────────────────────────────────────────────

def handle_widget_message(
    session_id: str,
    user_message: str,
    client_config: dict,
) -> dict:
    """
    Process a widget chat message and return the AI response.

    Args:
        session_id:    Unique ID for this browser session
        user_message:  What the visitor typed
        client_config: Dict with business_name, services, industry, agent_name, etc.

    Returns:
        {
          "reply":      str,   # AI response to show in widget
          "lead":       dict,  # Current lead data
          "qualified":  bool,  # Whether lead is fully qualified
          "stage":      str,   # Current conversation stage
        }
    """
    session = _get_session(session_id, client_config)

    # Add user message to history
    session["messages"].append({"role": "user", "content": user_message})

    # Extract lead data from conversation so far
    session["lead"] = _extract_lead_data(session["messages"], session["lead"])

    # Build system prompt with current lead data
    system_prompt = _build_system_prompt(client_config, session["lead"])

    # Call Claude
    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key":         ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type":      "application/json",
            },
            json={
                "model":      "claude-haiku-4-5-20251001",
                "max_tokens": 300,
                "system":     system_prompt,
                "messages":   session["messages"],
            },
            timeout=20,
        )
        reply = resp.json()["content"][0]["text"].strip()
    except Exception as e:
        reply = "Sorry, I'm having a moment. Can you try again in a second?"

    # Add assistant reply to history
    session["messages"].append({"role": "assistant", "content": reply})

    # Check qualification
    was_qualified = session["qualified"]
    session["qualified"] = _is_qualified(session["lead"])

    # Fire notifications on first qualification
    if session["qualified"] and not was_qualified and not session["notified"]:
        _save_lead_to_airtable(session, client_config)
        _notify_owner(session, client_config)
        session["notified"] = True

    return {
        "reply":     reply,
        "lead":      session["lead"],
        "qualified": session["qualified"],
        "stage":     session["stage"],
    }


def get_greeting(client_config: dict) -> str:
    """Generate a personalised opening greeting for the widget."""
    business   = client_config.get("business_name", "us")
    agent_name = client_config.get("agent_name", "Assistant")
    services   = client_config.get("services", "help you")

    return f"Hi! 👋 I'm {agent_name} from {business}. I'm here to help with {services}. What can I do for you today?"
