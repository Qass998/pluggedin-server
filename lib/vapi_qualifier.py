"""
lib/vapi_qualifier.py — VAPI Inbound Call Qualifier + Cal.com Booking

How it works:
  1. Lead calls client's VAPI phone number
  2. VAPI answers, qualifies the lead (budget, pain, timeline, decision maker)
  3. Call ends → VAPI sends webhook to webhook_server.py
  4. This module analyses the transcript, scores the lead
  5. If qualified (score ≥ 60): books a meeting via Cal.com API
  6. Sends WhatsApp to client: meeting booked + lead summary
  7. Logs everything to Airtable (Leads + Opportunities)

WhatsApp is only used for:
  - Meeting booked
  - Hot lead replied (score ≥ 80, no meeting yet)
  - Decision needed (something that requires the client)
  - Weekly digest (Sunday only)

Setup per client:
  1. Call setup_client_inbound(client) once per onboarded client
  2. Give client their VAPI phone number to use as their business line / call forward
  3. VAPI handles everything from there automatically
"""

import os
import json
import requests
from datetime import date, datetime
from dotenv import load_dotenv

load_dotenv()

VAPI_API_KEY        = os.getenv("VAPI_API_KEY")
CALCOM_API_KEY      = os.getenv("CALCOM_API_KEY")
AIRTABLE_TOKEN      = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE       = os.getenv("AIRTABLE_BASE_PLUGGEDIN")
TWILIO_ACCOUNT_SID  = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN   = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM         = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
OPENROUTER_KEY      = os.getenv("OPENROUTER_API_KEY")

VAPI_BASE    = "https://api.vapi.ai"
CALCOM_BASE  = "https://api.cal.com/v2"
AT_BASE_URL  = f"https://api.airtable.com/v0/{AIRTABLE_BASE}"

VAPI_HEADERS  = {"Authorization": f"Bearer {VAPI_API_KEY}", "Content-Type": "application/json"}
AT_HEADERS    = {"Authorization": f"Bearer {AIRTABLE_TOKEN}", "Content-Type": "application/json"}
CALCOM_HEADERS = {"Authorization": f"Bearer {CALCOM_API_KEY}", "cal-api-version": "2024-08-13"}


# ─────────────────────────────────────────────
# VAPI ASSISTANT SETUP (run once per client)
# ─────────────────────────────────────────────

def setup_client_inbound(client: dict) -> dict:
    """
    Create a VAPI inbound assistant for a client.
    Returns the assistant + phone number to give to the client.

    Call this once when onboarding a new client.
    Client forwards their business line to the VAPI number,
    or uses it directly as their business number.

    client dict requires: name, company, brand, cal_com_link, plan
    """
    company    = client.get("company", "the business")
    brand      = client.get("brand", company)
    cal_link   = client.get("cal_com_link", "")
    industry   = client.get("industry", "business")
    client_id  = client.get("id", "")

    system_prompt = f"""You are the AI receptionist and lead qualifier for {brand}.

Your job:
1. Answer inbound calls professionally and warmly
2. Find out why they are calling
3. If they are a potential customer, qualify them with these 4 questions (naturally, not like a script):
   - What specific problem are they trying to solve?
   - What is their rough budget for solving it?
   - What is their timeline — when do they need this done?
   - Are they the decision maker, or is someone else involved?
4. Based on their answers, decide if they are a good fit
5. If they ARE a fit: offer to book a call with {brand}'s team
6. If they ARE NOT a fit: be polite, wish them well, end gracefully

Rules:
- Never say you are an AI unless directly asked. If asked, say: "I'm a digital assistant for {brand}."
- Always be warm, human, and natural — not robotic
- Do not read the questions as a list. Weave them into conversation
- Keep calls under 10 minutes
- If the caller is upset or it is an emergency, say: "Let me get someone on this right away" and collect their details

Booking:
- If the lead qualifies, say: "Great — let me find a time that works. Can I take your email address so I can send you a calendar invite?"
- Collect: full name, email address, best phone number
- Confirm the booking and tell them they will receive a confirmation email

After the call, a summary will be automatically sent to the {brand} team.

Business: {brand} | Industry: {industry}
Booking: {cal_link if cal_link else "handled by the team"}
Client ID: {client_id}
"""

    payload = {
        "name": f"{brand} — Inbound Qualifier",
        "model": {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "systemPrompt": system_prompt,
            "temperature": 0.7,
        },
        "voice": {
            "provider": "elevenlabs",
            "voiceId": "21m00Tcm4TlvDq8ikWAM",  # Rachel — warm, professional
        },
        "firstMessage": f"Thank you for calling {brand}, how can I help you today?",
        "endCallMessage": "Perfect — you'll receive a confirmation shortly. Have a great day!",
        "endCallPhrases": ["goodbye", "bye", "thanks bye", "cheers", "speak soon"],
        "recordingEnabled": True,
        "silenceTimeoutSeconds": 30,
        "maxDurationSeconds": 600,
        "metadata": {
            "client_id": client_id,
            "client_name": client.get("name", ""),
            "company": company,
            "brand": brand,
            "type": "inbound_qualifier",
        },
        "serverUrl": os.getenv("WEBHOOK_BASE_URL", "") + "/webhook/vapi",
        "serverMessages": ["end-of-call-report"],
    }

    r = requests.post(f"{VAPI_BASE}/assistant", json=payload, headers=VAPI_HEADERS, timeout=15)
    r.raise_for_status()
    assistant = r.json()

    # Log assistant ID to Airtable Clients table
    try:
        requests.patch(
            f"{AT_BASE_URL}/Clients/{client_id}",
            headers=AT_HEADERS,
            json={"fields": {"VAPIAssistantID": assistant["id"]}},
            timeout=10,
        )
    except Exception:
        pass

    print(f"[vapi_qualifier] ✓ Inbound assistant created for {brand}: {assistant['id']}")
    return assistant


# ─────────────────────────────────────────────
# WEBHOOK HANDLER — called by webhook_server.py
# ─────────────────────────────────────────────

def handle_call_completed(webhook_payload: dict) -> dict:
    """
    Main entry point called when VAPI sends end-of-call-report webhook.
    Runs the full pipeline: analyse → score → book → notify → log.

    Returns summary of what happened.
    """
    call      = webhook_payload.get("call", {})
    call_id   = call.get("id", "")
    metadata  = call.get("metadata", {})
    client_id = metadata.get("client_id", "")
    brand     = metadata.get("brand", "")

    transcript   = _extract_transcript(call)
    summary      = call.get("summary", "")
    duration     = call.get("duration", 0)
    caller_phone = call.get("customer", {}).get("number", "")

    print(f"[vapi_qualifier] Call completed — {call_id} | {brand} | {duration}s")

    if duration < 30:
        print(f"[vapi_qualifier] Call too short ({duration}s) — skipping qualification")
        return {"action": "skipped", "reason": "call_too_short"}

    # Analyse transcript
    lead_data = analyse_call_transcript(transcript, summary, brand)
    score     = lead_data.get("score", 0)
    qualified = score >= 60

    print(f"[vapi_qualifier] Lead score: {score}/100 | Qualified: {qualified}")
    print(f"[vapi_qualifier] Lead: {lead_data.get('name')} | {lead_data.get('email')}")

    # Fetch client from Airtable
    client = _get_client(client_id)

    result = {
        "call_id": call_id,
        "lead": lead_data,
        "score": score,
        "qualified": qualified,
        "action": "none",
    }

    if qualified and lead_data.get("email"):
        # Book appointment via Cal.com
        booking = book_appointment(lead_data, client)
        result["booking"] = booking
        result["action"] = "booked"

        # WhatsApp: meeting booked
        notify_client_whatsapp(
            client=client,
            notification_type="meeting_booked",
            data={
                "lead": lead_data,
                "booking": booking,
                "score": score,
                "call_summary": summary,
            }
        )

    elif score >= 80:
        result["action"] = "hot_lead"
        # WhatsApp: hot lead, no email captured — needs manual follow up
        notify_client_whatsapp(
            client=client,
            notification_type="hot_lead",
            data={
                "lead": lead_data,
                "score": score,
                "caller_phone": caller_phone,
                "call_summary": summary,
            }
        )

    # Log to Airtable regardless
    log_qualified_lead(lead_data, score, call_id, client_id, client.get("name", ""))

    return result


# ─────────────────────────────────────────────
# TRANSCRIPT ANALYSIS
# ─────────────────────────────────────────────

def analyse_call_transcript(transcript: str, summary: str, brand: str) -> dict:
    """
    Use AI to extract lead info and score the call.
    Returns structured lead data dict.
    """
    prompt = f"""
Analyse this inbound sales call transcript for {brand}.

TRANSCRIPT:
{transcript[:3000]}

CALL SUMMARY (if available):
{summary}

Extract the following and return as valid JSON only (no markdown, no explanation):
{{
  "name": "caller's full name or empty string",
  "email": "caller's email or empty string",
  "phone": "caller's phone or empty string",
  "company": "caller's company or empty string",
  "pain_point": "their main problem in 1-2 sentences",
  "budget": "budget mentioned or 'not discussed'",
  "timeline": "timeline mentioned or 'not discussed'",
  "decision_maker": true or false,
  "interest_level": "high / medium / low",
  "score": integer 0-100 based on:
    - Clear pain point (0-25)
    - Budget mentioned or implied (0-25)
    - Short timeline (0-25)
    - Is decision maker (0-25)
  "recommendation": "book_meeting / follow_up / not_a_fit",
  "notes": "any other relevant info from the call"
}}
"""

    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://pluggedin.ai",
                "X-Title": "PluggedIN OS",
            },
            json={
                "model": "anthropic/claude-haiku-4-5",
                "max_tokens": 600,
                "messages": [
                    {"role": "system", "content": "You are a sales analyst. Return only valid JSON. No markdown."},
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=30,
        )
        if r.ok:
            raw = r.json()["choices"][0]["message"]["content"].strip()
            return json.loads(raw)
    except Exception as e:
        print(f"[vapi_qualifier] Transcript analysis failed: {e}")

    # Fallback
    return {
        "name": "", "email": "", "phone": "", "company": "",
        "pain_point": "Unable to extract", "budget": "unknown",
        "timeline": "unknown", "decision_maker": False,
        "interest_level": "unknown", "score": 0,
        "recommendation": "follow_up", "notes": "Analysis failed — review transcript manually",
    }


# ─────────────────────────────────────────────
# CAL.COM BOOKING
# ─────────────────────────────────────────────

def get_available_slots(event_type_id: int, days_ahead: int = 7) -> list:
    """
    Fetch available booking slots from Cal.com for the next N days.
    Returns list of slot dicts: {"start": ISO, "end": ISO}
    """
    from datetime import timedelta
    start = datetime.utcnow().isoformat() + "Z"
    end   = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + "Z"

    r = requests.get(
        f"{CALCOM_BASE}/slots",
        headers=CALCOM_HEADERS,
        params={"eventTypeId": event_type_id, "start": start, "end": end},
        timeout=15,
    )
    if r.ok:
        return r.json().get("data", {}).get("slots", [])
    return []


def book_appointment(lead_data: dict, client: dict) -> dict:
    """
    Book a Cal.com appointment for a qualified lead.
    Uses the first available slot unless a preference was captured.

    Returns booking confirmation dict.
    """
    event_type_id = client.get("cal_event_type_id") or os.getenv("CALCOM_DEFAULT_EVENT_TYPE_ID")
    if not event_type_id:
        print("[vapi_qualifier] No Cal.com event type ID — cannot book")
        return {"error": "no_event_type_id"}

    # Get first available slot
    slots = get_available_slots(int(event_type_id), days_ahead=7)
    if not slots:
        print("[vapi_qualifier] No available slots in Cal.com")
        return {"error": "no_slots_available"}

    first_slot = slots[0]
    start_time  = first_slot.get("time") or first_slot.get("start")

    payload = {
        "eventTypeId": int(event_type_id),
        "start": start_time,
        "attendee": {
            "name": lead_data.get("name") or "Lead",
            "email": lead_data.get("email"),
            "timeZone": "Europe/London",
            "language": "en",
        },
        "metadata": {
            "source": "PluggedIN VAPI qualifier",
            "pain_point": lead_data.get("pain_point", ""),
            "budget": lead_data.get("budget", ""),
            "score": str(lead_data.get("score", 0)),
        },
    }

    if lead_data.get("phone"):
        payload["attendee"]["phoneNumber"] = lead_data["phone"]

    r = requests.post(
        f"{CALCOM_BASE}/bookings",
        headers=CALCOM_HEADERS,
        json=payload,
        timeout=15,
    )

    if r.ok:
        booking = r.json().get("data", {})
        print(f"[vapi_qualifier] ✓ Meeting booked: {lead_data.get('name')} at {start_time}")
        return {
            "id": booking.get("id"),
            "start": start_time,
            "uid": booking.get("uid"),
            "status": "confirmed",
        }
    else:
        print(f"[vapi_qualifier] Cal.com booking failed: {r.status_code} {r.text[:200]}")
        return {"error": "booking_failed", "status": r.status_code}


# ─────────────────────────────────────────────
# WHATSAPP NOTIFICATIONS (targeted, high-value only)
# ─────────────────────────────────────────────

def notify_client_whatsapp(client: dict, notification_type: str, data: dict):
    """
    Send a targeted WhatsApp notification to a client.

    notification_type options:
      "meeting_booked"  — lead qualified + meeting in the calendar
      "hot_lead"        — score ≥ 80, no email, needs manual follow-up
      "decision_needed" — something requires client input
      "weekly_digest"   — Sunday summary (only scheduled send)

    WhatsApp is NOT used for daily briefings — Softr handles that.
    Only fires for things that need the client's attention right now.
    """
    phone = client.get("phone", "").strip()
    if not phone:
        return

    message = _build_notification_message(notification_type, data, client)
    if not message:
        return

    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        print(f"[vapi_qualifier] Twilio not set — would send to {phone}:\n{message}")
        return

    try:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
        r = requests.post(url, data={
            "From": TWILIO_FROM,
            "To": f"whatsapp:{phone}",
            "Body": message,
        }, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN), timeout=15)

        if r.ok:
            print(f"[vapi_qualifier] ✓ WhatsApp [{notification_type}] sent to {client.get('name')} ({phone})")
        else:
            print(f"[vapi_qualifier] ✗ WhatsApp failed: {r.status_code}")
    except Exception as e:
        print(f"[vapi_qualifier] WhatsApp error: {e}")


def _build_notification_message(notification_type: str, data: dict, client: dict) -> str:
    """Build the WhatsApp message text for each notification type."""
    brand = client.get("brand") or client.get("company", "")
    name  = client.get("name", "").split()[0]

    if notification_type == "meeting_booked":
        lead    = data.get("lead", {})
        booking = data.get("booking", {})
        score   = data.get("score", 0)
        summary = data.get("call_summary", "")

        # Format datetime nicely
        start_raw = booking.get("start", "")
        try:
            dt = datetime.fromisoformat(start_raw.replace("Z", "+00:00"))
            meeting_time = dt.strftime("%A %-d %B, %-I:%M%p").replace("AM", "am").replace("PM", "pm")
        except Exception:
            meeting_time = start_raw

        return (
            f"📅 *Meeting Booked — {brand}*\n\n"
            f"*Lead:* {lead.get('name', 'Unknown')} | {lead.get('company', '')}\n"
            f"*Time:* {meeting_time}\n"
            f"*Score:* {score}/100\n\n"
            f"*Why they called:* {lead.get('pain_point', 'See transcript')}\n"
            f"*Budget:* {lead.get('budget', 'Not discussed')}\n"
            f"*Timeline:* {lead.get('timeline', 'Not discussed')}\n"
            f"*Decision maker:* {'Yes ✓' if lead.get('decision_maker') else 'No — involves others'}\n\n"
            f"_A calendar invite has been sent to {lead.get('email', 'the lead')}._\n"
            f"_Reply *PREP* for a call preparation brief_"
        )

    elif notification_type == "hot_lead":
        lead   = data.get("lead", {})
        score  = data.get("score", 0)
        caller = data.get("caller_phone", "unknown")
        summary = data.get("call_summary", "")

        return (
            f"🔥 *Hot Lead — {brand}*\n\n"
            f"*Name:* {lead.get('name', 'Unknown')}\n"
            f"*Phone:* {caller}\n"
            f"*Score:* {score}/100\n\n"
            f"*Pain:* {lead.get('pain_point', 'See transcript')}\n"
            f"*Budget:* {lead.get('budget', 'Not discussed')}\n\n"
            f"⚠️ *No email captured — needs manual follow-up*\n\n"
            f"_Reply *CALL* to get a call back script_\n"
            f"_View transcript in your portal_"
        )

    elif notification_type == "decision_needed":
        items = data.get("items", [])
        items_text = "\n".join([f"  {i+1}. {item}" for i, item in enumerate(items)])
        return (
            f"⚡ *Decision Needed — {brand}*\n\n"
            f"Hey {name}, your agents flagged {len(items)} item(s) needing your input:\n\n"
            f"{items_text}\n\n"
            f"_Reply *YES ALL* to approve / *NO* to reject / or reply with specific instructions_"
        )

    elif notification_type == "weekly_digest":
        stats = data.get("stats", {})
        return (
            f"📊 *Weekly Digest — {brand}*\n"
            f"_Week ending {date.today().strftime('%d %b %Y')}_\n\n"
            f"*Calls handled:* {stats.get('calls', 0)}\n"
            f"*Leads qualified:* {stats.get('qualified', 0)}\n"
            f"*Meetings booked:* {stats.get('meetings', 0)}\n"
            f"*Hot leads:* {stats.get('hot_leads', 0)}\n\n"
            f"_Full report in your portal_"
        )

    return ""


# ─────────────────────────────────────────────
# AIRTABLE LOGGING
# ─────────────────────────────────────────────

def log_qualified_lead(lead_data: dict, score: int, call_id: str, client_id: str, client_name: str):
    """Log the qualified lead to Airtable Leads table."""
    try:
        fields = {
            "Firm Name": lead_data.get("company") or lead_data.get("name", "Unknown"),
            "Contact Name": lead_data.get("name", ""),
            "Email": lead_data.get("email", ""),
            "Phone": lead_data.get("phone", ""),
            "Score": score,
            "Tier": "Tier 1" if score >= 80 else "Tier 2" if score >= 60 else "Tier 3",
            "Status": "New",
            "Source": "VAPI Inbound Call",
            "Signals": f"Pain: {lead_data.get('pain_point', '')} | Budget: {lead_data.get('budget', '')} | Timeline: {lead_data.get('timeline', '')}",
            "Date Added": date.today().isoformat(),
            "ClientID": client_id,
            "Notes": f"Call ID: {call_id} | Recommendation: {lead_data.get('recommendation', '')} | {lead_data.get('notes', '')}",
        }
        requests.post(
            f"{AT_BASE_URL}/Leads",
            headers=AT_HEADERS,
            json={"records": [{"fields": fields}]},
            timeout=15,
        )
        print(f"[vapi_qualifier] ✓ Lead logged to Airtable: {lead_data.get('name')}")
    except Exception as e:
        print(f"[vapi_qualifier] Airtable log failed: {e}")


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _extract_transcript(call: dict) -> str:
    """Extract clean transcript text from VAPI call object."""
    messages = call.get("messages", [])
    lines = []
    for msg in messages:
        role    = msg.get("role", "unknown").upper()
        content = msg.get("message", "") or msg.get("content", "")
        if content and role in ("USER", "ASSISTANT", "BOT"):
            label = "CALLER" if role == "USER" else "AGENT"
            lines.append(f"{label}: {content}")
    return "\n".join(lines) if lines else call.get("transcript", "No transcript available")


def _get_client(client_id: str) -> dict:
    """Fetch a client record from Airtable by record ID."""
    try:
        r = requests.get(
            f"{AT_BASE_URL}/Clients/{client_id}",
            headers=AT_HEADERS,
            timeout=10,
        )
        if r.ok:
            f = r.json().get("fields", {})
            return {
                "id": client_id,
                "name": f.get("Name", ""),
                "company": f.get("CompanyName", ""),
                "phone": f.get("Phone", ""),
                "email": f.get("Email", ""),
                "brand": f.get("Brand", f.get("CompanyName", "")),
                "cal_com_link": f.get("CalComLink", ""),
                "cal_event_type_id": f.get("CalEventTypeID", ""),
                "plan": f.get("Plan", "Starter"),
            }
    except Exception as e:
        print(f"[vapi_qualifier] Could not fetch client {client_id}: {e}")
    return {"id": client_id}


# ─────────────────────────────────────────────
# WEEKLY DIGEST (called by orchestrator on Sundays)
# ─────────────────────────────────────────────

def send_weekly_digests():
    """
    Send weekly digest to all active clients every Sunday.
    Called by orchestrator --phase briefing on Sundays.
    """
    from lib.client_manager import get_active_clients
    clients = get_active_clients()

    for client in clients:
        try:
            # Pull this week's stats from Airtable
            client_id = client["id"]
            leads_this_week = _count_records("Leads", f"AND({{ClientID}}='{client_id}', {{Date Added}} >= DATEADD(TODAY(),-7,'day'))")
            meetings         = _count_records("Leads", f"AND({{ClientID}}='{client_id}', {{Status}}='Meeting Booked', {{Date Added}} >= DATEADD(TODAY(),-7,'day'))")

            stats = {
                "calls": leads_this_week,
                "qualified": leads_this_week,
                "meetings": meetings,
                "hot_leads": 0,
            }
            notify_client_whatsapp(client, "weekly_digest", {"stats": stats})
        except Exception as e:
            print(f"[vapi_qualifier] Weekly digest failed for {client.get('name')}: {e}")


def _count_records(table: str, formula: str) -> int:
    """Count matching records in an Airtable table."""
    try:
        r = requests.get(
            f"{AT_BASE_URL}/{table}",
            headers=AT_HEADERS,
            params={"filterByFormula": formula, "fields[]": "Status"},
            timeout=10,
        )
        return len(r.json().get("records", [])) if r.ok else 0
    except Exception:
        return 0
