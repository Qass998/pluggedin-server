"""
lib/vapi_client.py — VAPI Voice Agent Wrapper
PluggedIN standard. Never call VAPI API directly. Always use this.
Covers: inbound receptionist, outbound sales, onboarding calls,
        lead qualification, WhatsApp handoff.
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Optional

VAPI_API_KEY = os.getenv("VAPI_API_KEY")
VAPI_BASE = "https://api.vapi.ai"

HEADERS = {
    "Authorization": f"Bearer {VAPI_API_KEY}",
    "Content-Type": "application/json",
}


# ─────────────────────────────────────────────
# OUTBOUND — SALES AND QUALIFICATION
# ─────────────────────────────────────────────

def make_outbound_call(
    phone_number: str,
    assistant_id: str,
    customer_name: str = "",
    metadata: dict = None,
    first_message: str = None,
) -> dict:
    """
    Place an outbound call to a prospect or customer.
    assistant_id: VAPI assistant pre-configured per use case.
    Returns call object with call_id for tracking.
    """
    payload = {
        "phoneNumberId": os.getenv("VAPI_PHONE_NUMBER_ID"),
        "assistantId": assistant_id,
        "customer": {
            "number": phone_number,
            "name": customer_name,
        },
    }
    if metadata:
        payload["metadata"] = metadata
    if first_message:
        payload["assistantOverrides"] = {"firstMessage": first_message}

    r = requests.post(f"{VAPI_BASE}/call/phone", json=payload, headers=HEADERS)
    r.raise_for_status()
    return r.json()


def qualify_lead(
    phone_number: str,
    lead_name: str,
    company: str,
    industry: str,
    pain_point: str = "",
) -> dict:
    """
    Send a qualification call to a prospect.
    Uses the PluggedIN lead qualification assistant.
    Passes context so agent personalises opening.
    """
    metadata = {
        "company": company,
        "industry": industry,
        "pain_point": pain_point,
        "type": "lead_qualification",
    }
    first_message = (
        f"Hi {lead_name}, this is Maya calling from PluggedIN. "
        f"I'm reaching out because we help {industry} businesses "
        f"automate their operations — I wanted to see if there's a fit."
    )
    return make_outbound_call(
        phone_number=phone_number,
        assistant_id=os.getenv("VAPI_QUALIFIER_ASSISTANT_ID"),
        customer_name=lead_name,
        metadata=metadata,
        first_message=first_message,
    )


def sales_follow_up_call(
    phone_number: str,
    contact_name: str,
    previous_context: str,
) -> dict:
    """
    Follow-up call after initial contact or demo.
    Passes context from previous interaction.
    """
    metadata = {
        "previous_context": previous_context,
        "type": "sales_follow_up",
    }
    return make_outbound_call(
        phone_number=phone_number,
        assistant_id=os.getenv("VAPI_SALES_ASSISTANT_ID"),
        customer_name=contact_name,
        metadata=metadata,
    )


# ─────────────────────────────────────────────
# INBOUND — RECEPTIONIST
# ─────────────────────────────────────────────

def get_inbound_assistant(client_name: str) -> dict:
    """
    Retrieve the inbound receptionist assistant for a client.
    Each client has their own assistant configured with their:
    - Business name, hours, FAQs, booking link
    - Escalation rules
    - WhatsApp handoff trigger
    """
    assistants = list_assistants()
    for a in assistants:
        if a.get("metadata", {}).get("client") == client_name:
            return a
    raise ValueError(f"No inbound assistant found for client: {client_name}")


def create_inbound_assistant(
    client_name: str,
    business_name: str,
    industry: str,
    cal_link: str,
    faqs: list[dict],
    business_hours: str = "Monday to Friday, 9am to 6pm",
    escalation_phone: str = "",
    client_phone: str = "",
    overflow_only: bool = True,
) -> dict:
    """
    Create a new inbound receptionist for a client.

    overflow_only: True (default) = AI only answers when the client doesn't pick up.
                   The client sets up conditional call forwarding on their phone:
                   "Forward to [VAPI number] if no answer after 20 seconds."
                   This means the human always gets first chance to answer.

    client_phone: The owner's real mobile/landline. If provided and the caller
                  asks to speak to a person, the AI transfers the call to this number.

    faqs: list of {"question": str, "answer": str}
    Returns new assistant object.
    """
    faq_text = "\n".join(
        [f"Q: {f['question']}\nA: {f['answer']}" for f in faqs]
    ) if faqs else ""

    # Overflow context — agent knows it's the fallback
    overflow_context = ""
    if overflow_only:
        overflow_context = (
            f"\nIMPORTANT CONTEXT: You are the overflow receptionist for {business_name}. "
            f"You only answer calls when the team is unavailable or busy. "
            f"Be understanding — the caller may have expected a human. "
            f"Always reassure them they're in good hands and offer to help or take a message."
        )

    # Transfer instruction — only if we have the client's real number
    transfer_instruction = ""
    if client_phone:
        transfer_instruction = (
            f"\n- If the caller insists on speaking with a person, say: "
            f"\"Of course — let me transfer you now.\" "
            f"Then use the transferCall function to forward to {client_phone}."
        )
    else:
        transfer_instruction = (
            "\n- If the caller insists on speaking with a person, say: "
            "\"Of course — let me take your details and someone will call you right back.\""
            " Then collect their name and number."
        )

    system_prompt = f"""You are the AI receptionist for {business_name}.
You handle inbound calls professionally and warmly.
Industry: {industry}
Business hours: {business_hours}
Booking link: {cal_link}
{overflow_context}

Common questions and answers:
{faq_text}

Rules:
- Never say you are an AI unless directly asked
- If asked "are you a bot/AI?" say: "I'm {business_name}'s virtual receptionist — I'm here to help!"
- Always offer to book an appointment if relevant
- If you cannot help, take a message and say someone will follow up within the hour
- Be warm, concise, and professional — this is a phone call, not an essay
- Keep responses SHORT. One or two sentences at a time.{transfer_instruction}
- If caller sounds upset or it is urgent, escalate immediately and take their details
"""

    payload = {
        "name": f"{client_name} Receptionist",
        "voice": {
            "provider": "11labs",
            "voiceId": "paula",   # Warm, natural female voice
        },
        "model": {
            "provider": "anthropic",
            "model":    "claude-haiku-4-5-20251001",
            "messages": [{"role": "system", "content": system_prompt}],
        },
        "firstMessage": (
            f"Thank you for calling {business_name}, this is the virtual reception — "
            f"how can I help you today?"
            if overflow_only else
            f"Thank you for calling {business_name}, how can I help you today?"
        ),
        "metadata": {
            "client":        client_name,
            "industry":      industry,
            "type":          "inbound_receptionist",
            "overflow_only": overflow_only,
            "client_phone":  client_phone,
        },
    }

    # Add call transfer tool if we have a real number to forward to
    if client_phone:
        payload["tools"] = [{
            "type": "transferCall",
            "destinations": [{
                "type":          "number",
                "number":        client_phone,
                "description":   f"Transfer to {business_name} owner/team",
            }],
        }]

    r = requests.post(f"{VAPI_BASE}/assistant", json=payload, headers=HEADERS)
    r.raise_for_status()
    assistant = r.json()
    print(f"[VAPI] Created receptionist for {business_name} — overflow_only={overflow_only} ✓")
    return assistant


# ─────────────────────────────────────────────
# ONBOARDING — CLIENT BRAIN CAPTURE
# ─────────────────────────────────────────────

def run_onboarding_call(
    phone_number: str,
    client_name: str,
    business_name: str,
    industry: str,
    modules_purchased: list[str],
) -> dict:
    """
    Initiate the onboarding call for a new client.
    The onboarding assistant captures:
    - Staff names and roles
    - Services and products
    - Target customers
    - Key competitors
    - Current pain points
    - Goals for the next 90 days
    All responses are stored in metadata and pushed to Airtable.
    """
    modules_text = ", ".join(modules_purchased)
    metadata = {
        "client": client_name,
        "business": business_name,
        "industry": industry,
        "modules": modules_text,
        "type": "onboarding",
    }
    first_message = (
        f"Hi {client_name}, welcome to PluggedIN. "
        f"I'm your onboarding assistant and I'm going to spend about 30 minutes "
        f"learning everything about {business_name} so your agents can hit the ground running. "
        f"Ready to get started?"
    )
    return make_outbound_call(
        phone_number=phone_number,
        assistant_id=os.getenv("VAPI_ONBOARDING_ASSISTANT_ID"),
        customer_name=client_name,
        metadata=metadata,
        first_message=first_message,
    )


# ─────────────────────────────────────────────
# CALL MANAGEMENT
# ─────────────────────────────────────────────

def get_call(call_id: str) -> dict:
    """Get full call record including transcript and summary."""
    r = requests.get(f"{VAPI_BASE}/call/{call_id}", headers=HEADERS)
    r.raise_for_status()
    return r.json()


def list_calls(
    assistant_id: str = None,
    limit: int = 20,
    created_after: str = None,
) -> list[dict]:
    """
    List recent calls. Filter by assistant or date.
    created_after: ISO date string e.g. "2026-04-01"
    """
    params = {"limit": limit}
    if assistant_id:
        params["assistantId"] = assistant_id
    if created_after:
        params["createdAtGt"] = created_after

    r = requests.get(f"{VAPI_BASE}/call", params=params, headers=HEADERS)
    r.raise_for_status()
    return r.json()


def get_call_transcript(call_id: str) -> str:
    """Return clean transcript text from a call."""
    call = get_call(call_id)
    messages = call.get("messages", [])
    lines = []
    for msg in messages:
        role = msg.get("role", "unknown").upper()
        content = msg.get("message", "")
        if content:
            lines.append(f"{role}: {content}")
    return "\n".join(lines)


def get_call_summary(call_id: str) -> str:
    """Return the AI summary of a call."""
    call = get_call(call_id)
    return call.get("summary", "No summary available.")


def wait_for_call_complete(call_id: str, timeout: int = 600) -> dict:
    """
    Poll until call is complete or timeout reached.
    timeout: seconds to wait (default 10 minutes)
    Returns final call object.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        call = get_call(call_id)
        status = call.get("status", "")
        if status in ("ended", "failed"):
            return call
        time.sleep(10)
    raise TimeoutError(f"Call {call_id} did not complete within {timeout}s")


# ─────────────────────────────────────────────
# ASSISTANT MANAGEMENT
# ─────────────────────────────────────────────

def list_assistants() -> list[dict]:
    """List all VAPI assistants in the account."""
    r = requests.get(f"{VAPI_BASE}/assistant", headers=HEADERS)
    r.raise_for_status()
    return r.json()


def update_assistant(assistant_id: str, updates: dict) -> dict:
    """Update an existing assistant's config."""
    r = requests.patch(
        f"{VAPI_BASE}/assistant/{assistant_id}",
        json=updates,
        headers=HEADERS,
    )
    r.raise_for_status()
    return r.json()


def delete_assistant(assistant_id: str) -> bool:
    """Remove an assistant. Irreversible."""
    r = requests.delete(f"{VAPI_BASE}/assistant/{assistant_id}", headers=HEADERS)
    r.raise_for_status()
    return True


# ─────────────────────────────────────────────
# PHONE NUMBERS — CLIENT PROVISIONING
# ─────────────────────────────────────────────

def provision_inbound_phone(
    client_id: str,
    assistant_id: str,
    country: str = "US",
    area_code: str = None,
) -> dict:
    """
    Provision a real phone number for a client's inbound assistant.
    Ties the number to the assistant so incoming calls route automatically.
    
    Args:
        client_id: PluggedIN client ID (used for tracking)
        assistant_id: VAPI assistant ID (created via create_inbound_assistant)
        country: "US" (default) or "GB" for UK (not used in VAPI API)
        area_code: Optional area code (not used in basic VAPI API)
    
    Returns:
        {
            "id": "phone_number_id",
            "assistantId": "asst_123",
            "provider": "vapi",
            "status": "active",
            "created_at": "2026-05-13T01:31:02.471Z"
        }
    """
    payload = {
        "provider": "vapi",
        "assistantId": assistant_id,
    }
    
    try:
        r = requests.post(
            f"{VAPI_BASE}/phone-number",
            json=payload,
            headers=HEADERS,
            timeout=10
        )
        r.raise_for_status()
        phone_data = r.json()
        
        # Enhance with our metadata
        phone_data["client_id"] = client_id
        phone_data["country"] = country
        phone_data["created_at"] = datetime.utcnow().isoformat() + "Z"
        
        return phone_data
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to provision phone for {client_id}: {str(e)}")


def get_phone_number(phone_number_id: str) -> dict:
    """Retrieve details of a provisioned phone number."""
    r = requests.get(
        f"{VAPI_BASE}/phone-number/{phone_number_id}",
        headers=HEADERS,
    )
    r.raise_for_status()
    return r.json()


def release_phone_number(phone_number_id: str) -> bool:
    """Release a provisioned phone number (disables inbound calls)."""
    r = requests.delete(
        f"{VAPI_BASE}/phone-number/{phone_number_id}",
        headers=HEADERS,
    )
    r.raise_for_status()
    return True


# ─────────────────────────────────────────────
# ANALYTICS
# ─────────────────────────────────────────────

def call_analytics(
    assistant_id: str = None,
    days: int = 7,
) -> dict:
    """
    Basic analytics summary across recent calls.
    Returns: total calls, avg duration, completion rate.
    """
    from datetime import datetime, timedelta
    since = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"

    calls = list_calls(assistant_id=assistant_id, limit=100, created_after=since)

    total = len(calls)
    completed = sum(1 for c in calls if c.get("status") == "ended")
    durations = [c.get("duration", 0) for c in calls if c.get("duration")]
    avg_duration = sum(durations) / len(durations) if durations else 0

    return {
        "total_calls": total,
        "completed": completed,
        "completion_rate": f"{(completed / total * 100):.1f}%" if total > 0 else "0%",
        "avg_duration_seconds": round(avg_duration),
        "period_days": days,
    }
