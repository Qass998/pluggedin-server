"""
lib/demo_flow.py — One-Button Prospect Demo Orchestration

The full demo flow when sitting with a prospect:

  STEP 1 — Press "Launch Demo"
    → Provisions AI agent configured for their business
    → Sends prospect a WhatsApp intro from the agent
    → They can text back and forth live (two-way conversation)

  STEP 2 — Press "Call Demo"
    → VAPI makes an outbound call to the prospect's phone
    → They hear the AI voice agent introduce itself for their business
    → Call is real, live, impressive

  STEP 3 — Press "Send Payment Link"
    → WhatsApp message sent with Stripe link
    → Clean, professional close

All three steps tracked in _active_demos dict.
Dashboard polls /demo/status/{demo_id} for live progress.
"""

from __future__ import annotations
import os
import uuid
import time
import threading
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

STRIPE_PAYMENT_LINK = os.getenv("STRIPE_PAYMENT_LINK", "https://buy.stripe.com/your-link")
QASSIM_PHONE        = os.getenv("QASSIM_PHONE")

# ─────────────────────────────────────────────
# DEMO STATE STORE
# ─────────────────────────────────────────────

_active_demos: dict = {}


def get_demo(demo_id: str) -> dict | None:
    return _active_demos.get(demo_id)


def list_demos() -> list:
    return list(_active_demos.values())


# ─────────────────────────────────────────────
# STEP 1 — LAUNCH DEMO
# ─────────────────────────────────────────────

def launch_demo(
    prospect_name: str,
    prospect_phone: str,
    business_name: str,
    industry: str,
    cal_link: str = "",
    custom_greeting: str = "",
    faqs: list = None,
    language: str = "English",
) -> dict:
    """
    Step 1: Provision AI agent + send welcome WhatsApp to prospect.

    prospect_phone: e.g. "+447847221722" or "whatsapp:+447847221722"
    Returns demo_id for tracking.

    Call this while sitting with the prospect — they'll feel the agent
    arrive on their phone in real time.
    """
    demo_id = str(uuid.uuid4())[:8].upper()
    wa_phone = prospect_phone if prospect_phone.startswith("whatsapp:") else f"whatsapp:{prospect_phone}"

    demo = {
        "demo_id":        demo_id,
        "prospect_name":  prospect_name,
        "prospect_phone": wa_phone,
        "business_name":  business_name,
        "industry":       industry,
        "cal_link":       cal_link,
        "language":       language,
        "created_at":     datetime.utcnow().isoformat(),
        "steps": {
            "whatsapp_sent":   {"status": "pending", "at": None},
            "demo_call":       {"status": "pending", "at": None, "call_id": None},
            "payment_sent":    {"status": "pending", "at": None},
        },
        "status": "active",
    }
    _active_demos[demo_id] = demo

    # Register as a temporary client in the WhatsApp agent
    # (uses the agency's own Twilio number for the demo)
    try:
        from lib import whatsapp_agent
        agency_wa_number = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

        whatsapp_agent.register_client(
            twilio_whatsapp_number=agency_wa_number,
            config={
                "client_id":      f"demo_{demo_id}",
                "client_name":    prospect_name,
                "business_name":  business_name,
                "industry":       industry,
                "cal_link":       cal_link,
                "faqs":           faqs or [],
                "ceo_phone":      QASSIM_PHONE,
                "tone":           "professional but warm",
                "language":       language,
            }
        )
    except Exception as e:
        print(f"[Demo] WhatsApp agent registration error: {e}")

    # Build the welcome message
    if custom_greeting:
        greeting = custom_greeting
    else:
        booking_line = f"\n\nTo book a meeting: {cal_link}" if cal_link else ""
        greeting = (
            f"Hi {prospect_name}! 👋\n\n"
            f"I'm the AI assistant for *{business_name}*. "
            f"I handle customer enquiries 24/7 — so your team never misses a lead.\n\n"
            f"I work over WhatsApp, voice calls, and can proactively follow up with your customers too. "
            f"Try me — send me anything.{booking_line}"
        )

    # Send the welcome WhatsApp
    from lib.whatsapp_agent import send_whatsapp
    sent = send_whatsapp(wa_phone, greeting)

    demo["steps"]["whatsapp_sent"] = {
        "status": "done" if sent else "failed",
        "at": datetime.utcnow().isoformat(),
        "message": greeting,
    }

    print(f"[Demo {demo_id}] Launched for {prospect_name} ({business_name}) — WhatsApp {'sent ✓' if sent else 'FAILED'}")
    return demo


# ─────────────────────────────────────────────
# STEP 2 — TRIGGER DEMO CALL
# ─────────────────────────────────────────────

def trigger_demo_call(demo_id: str, raw_phone: str = None) -> dict:
    """
    Step 2: VAPI makes an outbound call to the prospect.

    The AI introduces itself as the business's receptionist,
    demonstrates how it handles a real customer call.

    raw_phone: override phone if different from demo prospect_phone
    """
    demo = _active_demos.get(demo_id)
    if not demo:
        return {"error": f"Demo {demo_id} not found"}

    # Phone number for the call (no whatsapp: prefix)
    call_to = raw_phone or demo["prospect_phone"].replace("whatsapp:", "")

    business_name = demo["business_name"]
    industry      = demo["industry"]
    prospect_name = demo["prospect_name"]
    cal_link      = demo.get("cal_link", "")

    demo_script = (
        f"You are the AI receptionist for {business_name}, a {industry} business. "
        f"You are calling {prospect_name} to introduce yourself as their new AI assistant. "
        f"Be warm, brief, and impressive. Say something like: "
        f"'Hi {prospect_name}, this is the AI assistant for {business_name}. "
        f"I just sent you a WhatsApp — I'll be handling your customer enquiries 24 hours a day, 7 days a week. "
        f"I can qualify leads, answer questions, and book meetings automatically. "
        + (f"Clients can even book at {cal_link}. " if cal_link else "") +
        f"Any questions for me right now?' "
        f"Keep it under 45 seconds. Be natural, not robotic."
    )

    demo["steps"]["demo_call"]["status"] = "calling"
    demo["steps"]["demo_call"]["at"] = datetime.utcnow().isoformat()

    try:
        from lib import vapi_client
        call = vapi_client.make_outbound_call(
            to_number=call_to,
            assistant_prompt=demo_script,
            metadata={
                "type":        "demo_call",
                "demo_id":     demo_id,
                "business":    business_name,
            }
        )
        call_id = call.get("id", "unknown")
        demo["steps"]["demo_call"]["status"]  = "done"
        demo["steps"]["demo_call"]["call_id"] = call_id
        print(f"[Demo {demo_id}] Demo call triggered → call_id: {call_id}")
        return {"status": "calling", "call_id": call_id, "demo_id": demo_id}

    except Exception as e:
        demo["steps"]["demo_call"]["status"] = "failed"
        demo["steps"]["demo_call"]["error"]  = str(e)
        print(f"[Demo {demo_id}] Demo call FAILED: {e}")
        return {"status": "failed", "error": str(e), "demo_id": demo_id}


# ─────────────────────────────────────────────
# STEP 3 — SEND PAYMENT LINK
# ─────────────────────────────────────────────

def send_payment_link(
    demo_id: str,
    stripe_link: str = None,
    custom_message: str = "",
) -> dict:
    """
    Step 3: Send the Stripe payment link to the prospect via WhatsApp.

    Closes the deal while they're still excited from the demo.
    """
    demo = _active_demos.get(demo_id)
    if not demo:
        return {"error": f"Demo {demo_id} not found"}

    link         = stripe_link or STRIPE_PAYMENT_LINK
    business     = demo["business_name"]
    prospect     = demo["prospect_name"]
    wa_phone     = demo["prospect_phone"]

    if custom_message:
        msg = custom_message
    else:
        msg = (
            f"Glad you liked the demo, {prospect}! 🎉\n\n"
            f"Your AI assistant for *{business}* is ready to go live.\n\n"
            f"*Activate your agent here:*\n{link}\n\n"
            f"Takes 2 minutes. Once you're set up, I'll configure everything "
            f"to your business and you'll be live today. 🚀"
        )

    from lib.whatsapp_agent import send_whatsapp
    sent = send_whatsapp(wa_phone, msg)

    demo["steps"]["payment_sent"] = {
        "status": "done" if sent else "failed",
        "at":     datetime.utcnow().isoformat(),
        "link":   link,
    }

    if sent:
        demo["status"] = "payment_sent"
        print(f"[Demo {demo_id}] Payment link sent to {wa_phone} ✓")
    else:
        print(f"[Demo {demo_id}] Payment link send FAILED")

    return {"status": "done" if sent else "failed", "demo_id": demo_id}


# ─────────────────────────────────────────────
# QUICK DEMO — ALL-IN-ONE (no button pressing needed)
# ─────────────────────────────────────────────

def quick_demo(
    prospect_name: str,
    prospect_phone: str,
    business_name: str,
    industry: str,
    cal_link: str = "",
    call_delay_seconds: int = 120,
    payment_delay_seconds: int = 300,
) -> dict:
    """
    Fire-and-forget full demo sequence.
    Useful for remote demos — sends WhatsApp, waits, calls, waits, sends payment link.

    call_delay_seconds:    wait before calling (default 2 min — gives them time to read WhatsApp)
    payment_delay_seconds: wait before sending payment link (default 5 min — after call ends)
    """
    demo = launch_demo(prospect_name, prospect_phone, business_name, industry, cal_link)
    demo_id = demo["demo_id"]

    def _sequence():
        time.sleep(call_delay_seconds)
        trigger_demo_call(demo_id)
        time.sleep(payment_delay_seconds)
        send_payment_link(demo_id)

    t = threading.Thread(target=_sequence, daemon=True)
    t.start()

    print(f"[Demo {demo_id}] Automated sequence started — call in {call_delay_seconds}s, payment link in {call_delay_seconds + payment_delay_seconds}s")
    return demo
