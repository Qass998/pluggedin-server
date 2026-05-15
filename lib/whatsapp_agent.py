"""
lib/whatsapp_agent.py — WhatsApp AI Agent (Module 1 — Africa/Global variant)

How it works:
  1. Customer messages client's WhatsApp Business number
  2. Twilio fires webhook to /webhook/whatsapp
  3. Claude Haiku handles the conversation (fast, cheap, WhatsApp-native)
  4. AI qualifies the lead (name, need, timeline)
  5. Offers Cal.com booking link when ready
  6. Fires WhatsApp alert to CEO when lead is hot
  7. Logs everything to Airtable

Multi-client:
  Each client has their own Twilio WhatsApp number.
  Call register_client() when a client is provisioned.
  The 'To' field in Twilio webhook maps to the right client config.

CEO morning briefing:
  Call send_morning_briefing() at 7am via cron/scheduler.
  Summarises all overnight conversations and hot leads.
"""

from __future__ import annotations
import os
import re
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID   = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN    = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
QASSIM_PHONE         = os.getenv("QASSIM_PHONE")
ANTHROPIC_API_KEY    = os.getenv("ANTHROPIC_API_KEY")

# ─────────────────────────────────────────────
# CONVERSATION STORE (in-memory, keyed by from_number)
# Resets after CONVERSATION_TTL_HOURS of inactivity
# ─────────────────────────────────────────────

conversations: dict = {}
CONVERSATION_TTL_HOURS = 24


# ─────────────────────────────────────────────
# CLIENT REGISTRY
# Maps Twilio 'To' number → client config
# ─────────────────────────────────────────────

PHONE_TO_CLIENT: dict = {}

DEFAULT_CLIENT_CONFIG = {
    "client_id":      "default",
    "client_name":    "the team",
    "business_name":  "the business",
    "industry":       "general",
    "cal_link":       "",
    "business_hours": "Monday to Friday, 9am to 6pm",
    "ceo_phone":      None,
    "faqs":           [],
    "tone":           "professional but warm",
    "language":       "English",
}


def register_client(twilio_whatsapp_number: str, config: dict):
    """
    Register a client's WhatsApp number → config.

    Call this when provisioning a new client:
      register_client("+14155238886", {
          "client_id":     "rec_gromatic",
          "business_name": "Gromatic",
          "industry":      "Legal",
          "cal_link":      "https://calendly.com/gromatic/consultation",
          "ceo_phone":     "whatsapp:+447847221722",
          "faqs": [
              {"question": "What do you do?", "answer": "We automate legal workflows."},
          ],
      })
    """
    key = f"whatsapp:{twilio_whatsapp_number}" if not twilio_whatsapp_number.startswith("whatsapp:") else twilio_whatsapp_number
    PHONE_TO_CLIENT[key] = {**DEFAULT_CLIENT_CONFIG, **config}
    print(f"[WhatsApp] Registered client '{config.get('business_name')}' on {key}")


def get_client_config(to_number: str) -> dict:
    """Lookup client config from Twilio 'To' number."""
    return PHONE_TO_CLIENT.get(to_number, DEFAULT_CLIENT_CONFIG)


def list_registered_clients() -> list:
    return [{"number": k, **v} for k, v in PHONE_TO_CLIENT.items()]


# ─────────────────────────────────────────────
# SYSTEM PROMPT BUILDER
# ─────────────────────────────────────────────

def _build_system_prompt(config: dict) -> str:
    business_name = config["business_name"]
    industry      = config["industry"]
    cal_link      = config.get("cal_link", "")
    hours         = config.get("business_hours", "Monday to Friday, 9am to 6pm")
    tone          = config.get("tone", "professional but warm")
    language      = config.get("language", "English")

    faqs_text = ""
    if config.get("faqs"):
        faqs_text = "\n\nFrequently asked questions you know the answers to:\n"
        for faq in config["faqs"]:
            faqs_text += f"Q: {faq['question']}\nA: {faq['answer']}\n"

    booking_line = f"When they're ready to proceed, share the booking link: {cal_link}" if cal_link else \
                   "When they're ready to proceed, let them know the team will follow up to arrange a time."

    return f"""You are the AI assistant for {business_name}, a {industry} business. You handle customer enquiries on WhatsApp.

Your goals:
1. Greet warmly and understand what the customer needs
2. Answer their questions clearly and helpfully
3. Gather their name naturally during conversation (don't ask for it bluntly)
4. Qualify their need (what specifically they want, any timeline or urgency)
5. {booking_line}

Tone: {tone}
Language: Respond in {language}. If customer writes in another language, match their language.
Business hours: {hours}
{faqs_text}

WhatsApp rules — very important:
- Keep messages SHORT. Max 3-4 sentences per reply. This is WhatsApp, not email.
- Use line breaks to separate points, not walls of text
- One emoji max per message, and only when natural
- Never send long lists — keep it conversational
- If you don't know something, say you'll get the right person to follow up

Identity rules:
- Never say you are an AI or a bot unprompted
- If directly asked "are you a bot/AI?", say: "I'm {business_name}'s digital assistant — I'm here to help! 😊"
- Never claim to be a human

Qualification signal — CRITICAL:
When you have gathered ALL of the following, append this exact tag on a new line at the very end of your message (invisible to customer):
[QUALIFIED: name=THEIR_NAME | need=THEIR_NEED_IN_10_WORDS | book=yes/no]

Replace THEIR_NAME, THEIR_NEED_IN_10_WORDS, and yes/no (whether they want to book) with real values.
Only append this tag once — when you are confident you have enough to qualify them.
Do NOT append it in early messages."""


# ─────────────────────────────────────────────
# CONVERSATION MANAGEMENT
# ─────────────────────────────────────────────

def _get_or_create_conversation(from_number: str, client_id: str) -> dict:
    now = datetime.utcnow()

    if from_number in conversations:
        conv = conversations[from_number]
        age = now - conv["last_active"]
        if age > timedelta(hours=CONVERSATION_TTL_HOURS):
            del conversations[from_number]
        else:
            conv["last_active"] = now
            return conv

    conversations[from_number] = {
        "messages":    [],
        "lead_data":   {},
        "stage":       "greeting",
        "client_id":   client_id,
        "started_at":  now.isoformat(),
        "last_active": now,
        "message_count": 0,
    }
    return conversations[from_number]


def get_conversation_summary(from_number: str) -> dict | None:
    """Get a conversation summary for CEO briefing."""
    conv = conversations.get(from_number)
    if not conv:
        return None
    return {
        "from_number":  from_number,
        "stage":        conv["stage"],
        "lead_data":    conv["lead_data"],
        "client_id":    conv["client_id"],
        "message_count": conv["message_count"],
        "started_at":   conv["started_at"],
        "last_active":  conv["last_active"].isoformat(),
    }


def get_all_active_conversations() -> list:
    cutoff = datetime.utcnow() - timedelta(hours=12)
    return [
        get_conversation_summary(num)
        for num, conv in conversations.items()
        if conv["last_active"] > cutoff
    ]


# ─────────────────────────────────────────────
# QUALIFICATION TAG PARSER
# ─────────────────────────────────────────────

def _extract_qualified_tag(text: str) -> tuple:
    """
    Parse [QUALIFIED: name=X | need=Y | book=yes/no] from Claude's response.
    Returns (clean_text, lead_data_dict or None).
    """
    pattern = r'\[QUALIFIED:\s*name=([^|]+)\|\s*need=([^|]+)\|\s*book=(yes|no)\]'
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        clean_text = text[:match.start()].strip()
        lead_data = {
            "name":     match.group(1).strip(),
            "need":     match.group(2).strip(),
            "wants_booking": match.group(3).lower() == "yes",
        }
        return clean_text, lead_data

    return text, None


# ─────────────────────────────────────────────
# TWILIO — SEND WHATSAPP
# ─────────────────────────────────────────────

def send_whatsapp(to: str, body: str, from_number: str = None) -> bool:
    """
    Send a WhatsApp message via Twilio.

    to:          destination (whatsapp:+447...)
    body:        message text
    from_number: sender number (whatsapp:+14155...) — uses client's number if provided
    """
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        print("[WhatsApp] ERROR: Twilio credentials not set")
        return False

    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
    sender = from_number or TWILIO_WHATSAPP_FROM

    try:
        r = requests.post(
            url,
            data={"From": sender, "To": to, "Body": body},
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            timeout=10,
        )
        r.raise_for_status()
        print(f"[WhatsApp] Sent to {to} ✓")
        return True
    except Exception as e:
        print(f"[WhatsApp] Send error to {to}: {e}")
        return False


# ─────────────────────────────────────────────
# CEO ALERTS
# ─────────────────────────────────────────────

def _alert_ceo_hot_lead(config: dict, from_number: str, lead_data: dict):
    """Fire WhatsApp to CEO when a lead is qualified."""
    ceo_phone = config.get("ceo_phone") or QASSIM_PHONE
    if not ceo_phone:
        print("[WhatsApp] No CEO phone configured — skipping alert")
        return

    name     = lead_data.get("name", "Unknown")
    need     = lead_data.get("need", "Not specified")
    booking  = "Wants to book ✅" if lead_data.get("wants_booking") else "Still exploring 🔍"
    customer = from_number.replace("whatsapp:", "")
    biz      = config.get("business_name", "your business")

    msg = (
        f"🔔 *Hot lead — {biz}*\n\n"
        f"👤 {name}\n"
        f"💬 Need: {need}\n"
        f"📅 {booking}\n"
        f"📱 WhatsApp: {customer}\n\n"
        f"_The AI is handling it. Message this number to take over the conversation._"
    )

    send_whatsapp(ceo_phone, msg)


def _alert_ceo_booking_confirmed(config: dict, booking_name: str, booking_time: str):
    """Fire WhatsApp to CEO when a meeting is booked via Cal.com."""
    ceo_phone = config.get("ceo_phone") or QASSIM_PHONE
    if not ceo_phone:
        return

    msg = (
        f"📅 *Meeting booked — {config.get('business_name', '')}*\n\n"
        f"👤 {booking_name}\n"
        f"🕐 {booking_time}\n\n"
        f"_Check your calendar for details._"
    )
    send_whatsapp(ceo_phone, msg)


# ─────────────────────────────────────────────
# AIRTABLE LOGGING
# ─────────────────────────────────────────────

def _log_lead_to_airtable(config: dict, from_number: str, lead_data: dict):
    try:
        from lib import airtable_client
        customer_number = from_number.replace("whatsapp:", "")
        airtable_client.log_lead(
            name=lead_data.get("name", "WhatsApp Lead"),
            phone=customer_number,
            source="WhatsApp",
            notes=lead_data.get("need", ""),
            client_id=config.get("client_id", ""),
        )
        print(f"[WhatsApp] Lead logged to Airtable ✓")
    except Exception as e:
        print(f"[WhatsApp] Airtable log error: {e}")


# ─────────────────────────────────────────────
# CLAUDE — AI RESPONSE
# ─────────────────────────────────────────────

def _get_ai_response(system_prompt: str, messages: list, config: dict) -> str:
    """Call Claude Haiku for fast, cheap WhatsApp responses."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=350,
            system=system_prompt,
            messages=messages,
        )
        return response.content[0].text

    except Exception as e:
        print(f"[WhatsApp] Claude error: {e}")
        biz = config.get("business_name", "us")
        return f"Thanks for reaching out to {biz}! We'll get back to you shortly. 😊"


# ─────────────────────────────────────────────
# MAIN HANDLER
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
# OUTBOUND CALL TRIGGER
# ─────────────────────────────────────────────

CALL_REQUEST_PHRASES = [
    "call me", "give me a call", "can you call", "phone me", "ring me",
    "speak on the phone", "speak by phone", "prefer a call", "rather call",
    "callback", "call back", "call us", "call now",
]

def _customer_wants_call(message: str) -> bool:
    """Detect if the customer is requesting a callback."""
    lowered = message.lower()
    return any(phrase in lowered for phrase in CALL_REQUEST_PHRASES)


def _trigger_callback(from_number: str, config: dict):
    """
    Trigger a VAPI outbound call back to the customer.
    Used when customer asks to be called during a WhatsApp conversation.
    """
    raw_number = from_number.replace("whatsapp:", "")
    business   = config.get("business_name", "the business")
    industry   = config.get("industry", "services")
    cal_link   = config.get("cal_link", "")

    script = (
        f"You are the AI assistant for {business}, a {industry} business. "
        f"You are calling back a customer who requested a callback via WhatsApp. "
        f"Be warm, helpful and concise. Find out how you can help them, "
        f"answer their questions, and if relevant offer to book a meeting"
        + (f" at {cal_link}" if cal_link else "") +
        f". Keep the call under 3 minutes unless they have a lot of questions."
    )

    try:
        from lib import vapi_client
        call = vapi_client.make_outbound_call(
            to_number=raw_number,
            assistant_prompt=script,
            metadata={"type": "whatsapp_callback", "client_id": config.get("client_id")},
        )
        print(f"[WhatsApp] Callback call triggered to {raw_number} ✓ — call_id: {call.get('id')}")
        return call.get("id")
    except Exception as e:
        print(f"[WhatsApp] Callback call error: {e}")
        return None


# ─────────────────────────────────────────────
# PROACTIVE OUTBOUND MESSAGING
# ─────────────────────────────────────────────

def send_proactive_message(
    to_number: str,
    message: str,
    client_whatsapp_number: str = None,
) -> bool:
    """
    Send a proactive WhatsApp message to a customer (agent-initiated).

    Use for:
    - Follow-up after a call: "Hi! Great speaking with you. Here's the booking link..."
    - Appointment reminders: "Your consultation is tomorrow at 2pm..."
    - Re-engagement: "Hi [name], just checking in — still looking for help with [need]?"

    to_number: customer's number (+447...)
    client_whatsapp_number: the client's Twilio number to send from
    """
    wa_to   = to_number if to_number.startswith("whatsapp:") else f"whatsapp:{to_number}"
    from_wa = client_whatsapp_number or TWILIO_WHATSAPP_FROM

    return send_whatsapp(wa_to, message, from_number=from_wa)


def schedule_followup(
    to_number: str,
    message: str,
    delay_seconds: int = 3600,
    client_whatsapp_number: str = None,
):
    """
    Schedule a proactive follow-up message after a delay.

    delay_seconds: default 1 hour — change to 86400 for next-day follow-up
    """
    import threading

    def _send():
        import time
        time.sleep(delay_seconds)
        send_proactive_message(to_number, message, client_whatsapp_number)
        print(f"[WhatsApp] Scheduled follow-up sent to {to_number} ✓")

    t = threading.Thread(target=_send, daemon=True)
    t.start()
    print(f"[WhatsApp] Follow-up scheduled for {to_number} in {delay_seconds}s")


def handle_incoming_message(
    from_number: str,
    to_number: str,
    body: str,
    profile_name: str = "",
) -> str:
    """
    Main entry point — called by /webhook/whatsapp.

    from_number:  customer's WhatsApp number (whatsapp:+447...)
    to_number:    client's Twilio number (whatsapp:+14155...)
    body:         message text
    profile_name: customer's WhatsApp display name (optional)

    Returns the reply text (already sent via Twilio).
    """
    config = get_client_config(to_number)
    conv   = _get_or_create_conversation(from_number, config["client_id"])

    # Add customer message to conversation history
    conv["messages"].append({"role": "user", "content": body})
    conv["message_count"] += 1

    print(f"[WhatsApp] [{config['business_name']}] {from_number}: {body[:60]}...")

    # Build system prompt and get AI response
    system_prompt = _build_system_prompt(config)
    reply_raw     = _get_ai_response(system_prompt, conv["messages"], config)

    # Parse qualification tag
    clean_reply, lead_data = _extract_qualified_tag(reply_raw)

    # Store assistant reply (without internal tag)
    conv["messages"].append({"role": "assistant", "content": clean_reply})

    # Handle newly qualified lead (fire once only)
    if lead_data and conv["stage"] != "qualified":
        conv["stage"]     = "qualified"
        conv["lead_data"] = {**lead_data, "qualified_at": datetime.utcnow().isoformat()}

        print(f"[WhatsApp] Lead qualified: {lead_data}")
        _alert_ceo_hot_lead(config, from_number, lead_data)
        _log_lead_to_airtable(config, from_number, lead_data)

    # Detect callback request — trigger VAPI outbound call
    if _customer_wants_call(body) and conv.get("stage") != "calling":
        conv["stage"] = "calling"
        call_id = _trigger_callback(from_number, config)
        if call_id:
            # Append a note to the reply acknowledging the call
            clean_reply = clean_reply.rstrip()
            if not any(phrase in clean_reply.lower() for phrase in ["calling you", "give you a call", "ring you"]):
                clean_reply += "\n\nI'm calling you now! 📞"

    # Send reply back to customer (from the client's Twilio number)
    send_whatsapp(from_number, clean_reply, from_number=to_number)

    return clean_reply


# ─────────────────────────────────────────────
# CEO MORNING BRIEFING
# ─────────────────────────────────────────────

def send_morning_briefing(ceo_phone: str = None, client_id: str = None):
    """
    Summarise all overnight WhatsApp conversations and send CEO a digest.
    Called by cron at 7am daily.

    Optionally filter by client_id to brief per-client.
    """
    target_phone = ceo_phone or QASSIM_PHONE
    if not target_phone:
        print("[WhatsApp] No CEO phone for briefing")
        return

    active = get_all_active_conversations()

    if client_id:
        active = [c for c in active if c["client_id"] == client_id]

    if not active:
        send_whatsapp(
            target_phone,
            "☀️ *Morning briefing*\n\nNo new WhatsApp conversations overnight. All quiet."
        )
        return

    qualified = [c for c in active if c["stage"] == "qualified"]
    exploring = [c for c in active if c["stage"] != "qualified"]

    lines = [f"☀️ *Morning briefing — {datetime.utcnow().strftime('%d %b')}*\n"]
    lines.append(f"💬 {len(active)} conversations | 🔥 {len(qualified)} qualified leads\n")

    if qualified:
        lines.append("*Hot leads:*")
        for c in qualified:
            ld = c.get("lead_data", {})
            lines.append(f"• {ld.get('name', 'Unknown')} — {ld.get('need', '?')} ({c['from_number'].replace('whatsapp:', '')})")

    if exploring:
        lines.append(f"\n*Still in conversation:* {len(exploring)} people")

    lines.append("\n_Reply to any number above to take over that conversation._")

    send_whatsapp(target_phone, "\n".join(lines))
    print(f"[WhatsApp] Morning briefing sent to {target_phone} ✓")


# ─────────────────────────────────────────────
# VAPI VOICE BRIEFING (optional — call the CEO)
# ─────────────────────────────────────────────

def trigger_voice_briefing(ceo_phone_number: str, client_id: str = None):
    """
    Trigger a VAPI outbound call to brief the CEO by voice.
    Uses the overnight conversation data to build the briefing script.

    ceo_phone_number: e.g. "+447847221722" (no whatsapp: prefix)
    """
    try:
        active    = get_all_active_conversations()
        qualified = [c for c in active if c["stage"] == "qualified"]

        if not qualified:
            print("[WhatsApp] No qualified leads — skipping voice briefing")
            return

        # Build a short brief for the VAPI assistant to read
        brief_lines = [f"You have {len(qualified)} qualified lead{'s' if len(qualified) > 1 else ''} from overnight WhatsApp conversations."]
        for i, c in enumerate(qualified[:3], 1):
            ld = c.get("lead_data", {})
            brief_lines.append(f"Lead {i}: {ld.get('name', 'Unknown')} needs {ld.get('need', 'something')}.")

        brief = " ".join(brief_lines) + " These leads are ready for follow-up. Have a great day."

        from lib import vapi_client
        vapi_client.make_outbound_call(
            to_number=ceo_phone_number,
            assistant_prompt=f"You are a professional briefing assistant. Read this briefing clearly and concisely: {brief}",
            metadata={"type": "morning_briefing", "client_id": client_id or "all"},
        )
        print(f"[WhatsApp] Voice briefing call triggered to {ceo_phone_number} ✓")

    except Exception as e:
        print(f"[WhatsApp] Voice briefing error: {e}")
