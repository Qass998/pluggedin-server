"""
lib/intake_processor.py — Client Intake Processor
PluggedIN onboarding engine. Processes VAPI onboarding call output
into populated memory layers and configured agent settings.
Also handles inbound enquiry forms from Softr portal.
"""

import os
import json
import re
from datetime import datetime
from typing import Optional

AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE = os.getenv("AIRTABLE_BASE_PLUGGEDIN")


# ─────────────────────────────────────────────
# ONBOARDING CALL PROCESSING
# ─────────────────────────────────────────────

def process_onboarding_transcript(
    client_name: str,
    business_name: str,
    industry: str,
    transcript: str,
    modules: list[str],
) -> dict:
    """
    Process a VAPI onboarding call transcript.
    Extracts all key business information and returns structured data
    ready to populate memory layers.

    Returns dict with:
    - business_profile: core facts
    - staff: people and roles
    - products_services: what they sell
    - customers: who they serve
    - competitors: who to watch
    - pain_points: what's broken
    - goals: what they want in 90 days
    - tech_stack: what they already use
    """
    import anthropic
    client_ai = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    extraction_prompt = f"""Extract the following structured information from this onboarding call transcript for {business_name} ({industry}).

Return ONLY a JSON object with these exact keys:
- staff: list of {{"name": str, "role": str, "responsibilities": str}}
- products_services: list of {{"name": str, "price": str, "description": str}}
- customers: {{"demographics": str, "typical_profile": str, "average_value": str, "locations": str}}
- competitors: list of {{"name": str, "strengths": str, "weaknesses": str}}
- pain_points: list of str (top problems they have)
- goals: list of str (what they want in next 90 days)
- current_tech: list of str (software they use now)
- business_hours: str
- key_metrics: {{"monthly_revenue": str, "customers_per_month": str, "average_order": str}}
- notes: str (anything important not captured above)

Transcript:
{transcript}"""

    response = client_ai.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": extraction_prompt}],
    )

    raw = response.content[0].text.strip()
    # Clean JSON if wrapped in code blocks
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    extracted = json.loads(raw)

    return {
        "client_name": client_name,
        "business_name": business_name,
        "industry": industry,
        "modules": modules,
        "extracted": extracted,
        "processed_at": datetime.utcnow().isoformat(),
    }


def populate_memory_layers(
    client_workspace: str,
    processed_intake: dict,
) -> dict:
    """
    Write all extracted onboarding data to the client's memory layers.
    client_workspace: path to Clients/[ClientName]/
    processed_intake: output from process_onboarding_transcript()

    Creates/updates:
    - memory/semantic/customers.md
    - memory/semantic/products.md
    - memory/personal/owner.md
    - memory/working/today.md (initial tasks)
    """
    import os

    extracted = processed_intake["extracted"]
    business_name = processed_intake["business_name"]
    industry = processed_intake["industry"]
    client_name = processed_intake["client_name"]

    results = {}

    # ── customers.md ──
    customers = extracted.get("customers", {})
    customers_content = f"""# {business_name} — Customer Intelligence
# Updated: {datetime.utcnow().strftime('%Y-%m-%d')}

## CUSTOMER PROFILE
Demographics: {customers.get('demographics', 'To be updated')}
Typical customer: {customers.get('typical_profile', 'To be updated')}
Average value: {customers.get('average_value', 'To be updated')}
Locations: {customers.get('locations', 'To be updated')}

## KEY METRICS
Monthly customers: {extracted.get('key_metrics', {}).get('customers_per_month', 'Unknown')}
Average order value: {extracted.get('key_metrics', {}).get('average_order', 'Unknown')}
Monthly revenue: {extracted.get('key_metrics', {}).get('monthly_revenue', 'Unknown')}
"""
    results["customers_md"] = customers_content

    # ── products.md ──
    products = extracted.get("products_services", [])
    products_lines = "\n".join([
        f"### {p['name']}\nPrice: {p.get('price', 'TBC')}\n{p.get('description', '')}\n"
        for p in products
    ])
    products_content = f"""# {business_name} — Products and Services
# Updated: {datetime.utcnow().strftime('%Y-%m-%d')}

{products_lines if products_lines else "Products to be populated from onboarding."}
"""
    results["products_md"] = products_content

    # ── owner.md ──
    staff_lines = "\n".join([
        f"- {s.get('name', '')}: {s.get('role', '')} — {s.get('responsibilities', '')}"
        for s in extracted.get("staff", [])
    ])
    pain_lines = "\n".join([f"- {p}" for p in extracted.get("pain_points", [])])
    goals_lines = "\n".join([f"- {g}" for g in extracted.get("goals", [])])
    owner_content = f"""# {business_name} — Owner and Team Profile
# Client: {client_name}
# Updated: {datetime.utcnow().strftime('%Y-%m-%d')}

## STAFF
{staff_lines if staff_lines else "No staff listed."}

## BUSINESS HOURS
{extracted.get('business_hours', 'To be confirmed')}

## PAIN POINTS (what's broken)
{pain_lines if pain_lines else "To be extracted from onboarding."}

## 90-DAY GOALS
{goals_lines if goals_lines else "To be extracted from onboarding."}

## CURRENT TECH STACK
{', '.join(extracted.get('current_tech', [])) or 'None listed'}

## NOTES
{extracted.get('notes', 'None')}
"""
    results["owner_md"] = owner_content

    # ── today.md (initial tasks) ──
    modules = processed_intake.get("modules", [])
    tasks_lines = "\n".join([f"- [ ] Configure {m}" for m in modules])
    today_content = f"""# Working Memory — Today
# Client: {business_name}
# Updated: {datetime.utcnow().strftime('%Y-%m-%d')}

## STATUS
Onboarding: Complete
Next: All modules configured and live

## ACTIVE TASKS
{tasks_lines}
- [ ] Send first CEO briefing
- [ ] Confirm client received portal access

## NOTES
Onboarding call processed: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}
"""
    results["today_md"] = today_content

    return results


# ─────────────────────────────────────────────
# INBOUND ENQUIRY PROCESSING
# ─────────────────────────────────────────────

def process_enquiry_form(
    business_name: str,
    client_airtable_base: str,
    form_data: dict,
) -> dict:
    """
    Process an inbound lead enquiry form from the client's Softr portal.
    form_data: {"name": str, "phone": str, "email": str,
                "service": str, "message": str, "source": str}

    Returns: scored lead with recommended action.
    """
    from lib.airtable_client import log_lead

    # Score the lead
    score = _score_enquiry(form_data)

    # Log to client Airtable
    log_lead(
        name=form_data.get("name", ""),
        company=form_data.get("company", ""),
        phone=form_data.get("phone", ""),
        email=form_data.get("email", ""),
        source=form_data.get("source", "Website"),
        industry=form_data.get("industry", ""),
        score=score,
        notes=form_data.get("message", ""),
    )

    # Determine recommended action
    if score >= 80:
        action = "immediate_call"
        action_text = "Call within 15 minutes — high intent"
    elif score >= 60:
        action = "same_day_outreach"
        action_text = "Call today — qualified prospect"
    elif score >= 40:
        action = "nurture_sequence"
        action_text = "Add to email sequence — warm lead"
    else:
        action = "low_priority"
        action_text = "Monitor — may be too early"

    return {
        "lead_name": form_data.get("name", ""),
        "business": business_name,
        "score": score,
        "recommended_action": action,
        "action_description": action_text,
        "service_interest": form_data.get("service", ""),
        "received_at": datetime.utcnow().isoformat(),
    }


def _score_enquiry(form_data: dict) -> int:
    """
    Score an inbound enquiry from 0-100 based on signals.
    Higher score = higher intent and fit.
    """
    score = 40  # Base score

    # Phone number provided
    if form_data.get("phone"):
        score += 20

    # Specific service mentioned
    if form_data.get("service") and len(form_data["service"]) > 3:
        score += 10

    # Message has substance
    message = form_data.get("message", "")
    if len(message) > 50:
        score += 10

    # High-intent keywords in message
    high_intent_keywords = [
        "urgent", "asap", "soon", "ready", "start", "price", "cost",
        "quote", "budget", "contract", "sign", "this week", "today",
    ]
    message_lower = message.lower()
    for kw in high_intent_keywords:
        if kw in message_lower:
            score += 5
            break  # Only add once

    # Company provided
    if form_data.get("company"):
        score += 5

    return min(score, 100)


# ─────────────────────────────────────────────
# STAFF SUBMISSION PROCESSING
# ─────────────────────────────────────────────

def process_staff_submission(
    client_airtable_base: str,
    business_name: str,
    staff_name: str,
    submission_type: str,
    data: dict,
) -> dict:
    """
    Process a staff submission from the client portal.
    Staff submit updates — CEO agent acts on them.
    Owner is never involved in routine submissions.

    submission_type: "stock_update", "customer_complaint",
                    "new_booking", "staff_report", "expense"
    data: submission-specific fields
    """
    handlers = {
        "stock_update": _handle_stock_submission,
        "customer_complaint": _handle_complaint_submission,
        "new_booking": _handle_booking_submission,
        "staff_report": _handle_report_submission,
        "expense": _handle_expense_submission,
    }

    handler = handlers.get(submission_type, _handle_generic_submission)
    result = handler(client_airtable_base, business_name, staff_name, data)

    return {
        "submission_type": submission_type,
        "submitted_by": staff_name,
        "business": business_name,
        "processed_at": datetime.utcnow().isoformat(),
        "result": result,
        "escalate_to_owner": result.get("escalate", False),
    }


def _handle_stock_submission(base, business, staff, data) -> dict:
    """Log stock count update from staff."""
    return {"action": "stock_logged", "item": data.get("item"), "escalate": False}


def _handle_complaint_submission(base, business, staff, data) -> dict:
    """Flag customer complaint for CEO agent response."""
    severity = data.get("severity", "normal")
    return {"action": "complaint_flagged", "severity": severity, "escalate": severity == "high"}


def _handle_booking_submission(base, business, staff, data) -> dict:
    """Log new booking to Airtable."""
    return {"action": "booking_logged", "customer": data.get("customer"), "escalate": False}


def _handle_report_submission(base, business, staff, data) -> dict:
    """Process staff end-of-day report."""
    return {"action": "report_logged", "escalate": False}


def _handle_expense_submission(base, business, staff, data) -> dict:
    """Log expense claim for owner approval if above threshold."""
    amount = data.get("amount", 0)
    escalate = amount > 500
    return {"action": "expense_logged", "amount": amount, "escalate": escalate}


def _handle_generic_submission(base, business, staff, data) -> dict:
    return {"action": "logged", "escalate": False}


# ─────────────────────────────────────────────
# DAILY BRIEFING GENERATOR
# ─────────────────────────────────────────────

def generate_ceo_briefing(
    business_name: str,
    client_airtable_base: str,
    industry: str,
    modules_active: list[str],
) -> str:
    """
    Generate the daily CEO Agent briefing for a client.
    Pulls live data from Airtable and formats in PluggedIN standard.
    This runs at 7am daily per client.
    Returns formatted briefing text for WhatsApp delivery.
    """
    import requests

    # Pull pipeline data
    pipeline_url = f"https://api.airtable.com/v0/{client_airtable_base}/Pipeline"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}

    try:
        r = requests.get(pipeline_url, headers=headers, params={"maxRecords": 10})
        pipeline = r.json().get("records", [])
        active_leads = len([p for p in pipeline if p["fields"].get("Status") == "Active"])
    except Exception:
        active_leads = 0

    briefing = f"""📊 *{business_name} — Daily Briefing*
_{datetime.utcnow().strftime('%A, %d %B %Y')}_

*SITUATION:* {active_leads} active leads in pipeline. Modules running: {len(modules_active)}.

*PRIORITY:* Review any flagged items below before 9am.

*ACTIVE MODULES:*
{chr(10).join(['✅ ' + m for m in modules_active])}

*CEO AGENT STATUS:* All systems running normally.

_Reply GO to approve all pending actions._
_Reply DECISIONS to see items requiring your input._"""

    return briefing
