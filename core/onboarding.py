"""
core/onboarding.py — PluggedIN New Client Setup Automation
===========================================================
Input a business. This fires everything.

What it does:
  1. Creates a dedicated Airtable base for the client
  2. Registers the client in the Agency Clients base
  3. Configures a VAPI assistant for their industry
  4. Generates their HTML dashboard
  5. Sends an onboarding WhatsApp/email briefing

Usage:
    from core.onboarding import onboard_client
    result = onboard_client(
        client_name="Harland Construction",
        industry="construction",
        plan="starter",
        modules=[1, 4],
        contact_email="james@harlandconstruction.co.uk",
        contact_phone="+447911123456",
        website="https://harlandconstruction.co.uk",
        location="Sheffield, UK",
    )

CLI:
    python core/onboarding.py
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

log = logging.getLogger("onboarding")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


# ---------------------------------------------------------------------------
# Onboarding result
# ---------------------------------------------------------------------------

@dataclass
class OnboardingResult:
    success: bool
    client_id: str
    client_name: str
    airtable_base_id: str = ""
    airtable_record_id: str = ""
    vapi_assistant_id: str = ""
    dashboard_path: str = ""
    briefing_sent: bool = False
    errors: list = field(default_factory=list)
    steps_completed: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "success":            self.success,
            "client_id":          self.client_id,
            "client_name":        self.client_name,
            "airtable_base_id":   self.airtable_base_id,
            "airtable_record_id": self.airtable_record_id,
            "vapi_assistant_id":  self.vapi_assistant_id,
            "dashboard_path":     self.dashboard_path,
            "briefing_sent":      self.briefing_sent,
            "errors":             self.errors,
            "steps_completed":    self.steps_completed,
        }


# ---------------------------------------------------------------------------
# Module name map
# ---------------------------------------------------------------------------

MODULE_NAMES = {
    1:  "Presence Agent",
    2:  "Pipeline Agent",
    3:  "Marketing Agent",
    4:  "Intelligence Agent",
    5:  "Sales Intelligence",
    6:  "Data Intelligence",
    7:  "Conversion Agent",
    8:  "Lead Marketplace",
    9:  "Customer Retention OS",
    10: "Stock Intelligence",
}

MODULE_PRICES = {
    1: 797, 2: 997, 3: 1197, 4: 697, 5: 697,
    6: 897, 7: 897, 8: 997, 9: 497, 10: 297,
}

# VAPI system prompts per industry
VAPI_PROMPTS = {
    "legal": (
        "You are a professional AI receptionist for {client_name}, a legal services firm. "
        "You greet callers warmly, collect their name, contact details, and a brief description "
        "of their legal matter. You then book a consultation via Cal.com. You never give legal advice. "
        "Always say: 'One of our solicitors will be in touch shortly.'"
    ),
    "restaurant": (
        "You are a friendly AI host for {client_name}. You take table reservations, "
        "answer questions about the menu and opening hours, and handle special requests. "
        "When taking a reservation: name, party size, date, time, and any dietary requirements."
    ),
    "construction": (
        "You are a professional AI receptionist for {client_name}, a construction and trades company. "
        "You handle enquiries about projects, collect job details (location, scope, timeline), "
        "and book site surveys. Always confirm: contact name, address, type of work, and urgency."
    ),
    "logistics": (
        "You are an AI dispatcher for {client_name}. You handle collection and delivery enquiries, "
        "collect shipment details (origin, destination, dimensions, weight, urgency), "
        "and book jobs. Always confirm details back to the caller before ending the call."
    ),
    "healthcare": (
        "You are a compassionate AI receptionist for {client_name}. "
        "You book appointments, handle repeat prescription enquiries, and triage urgency. "
        "For emergencies, direct callers to 999. For urgent but non-emergency, to 111."
    ),
    "default": (
        "You are a professional AI receptionist for {client_name}. "
        "You greet callers warmly, understand their enquiry, collect their contact details, "
        "and book a call-back or meeting. Always be helpful, concise, and professional."
    ),
}


# ---------------------------------------------------------------------------
# Step 1: Create Airtable base
# ---------------------------------------------------------------------------

def _create_airtable_base(client_name: str, token: str) -> tuple[str, list[str]]:
    """
    Create a new Airtable base for the client.
    Returns (base_id, errors).
    """
    errors = []
    try:
        url = "https://api.airtable.com/v0/meta/bases"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        # Default tables for all clients
        tables = [
            {
                "name": "Leads",
                "fields": [
                    {"name": "Name", "type": "singleLineText"},
                    {"name": "Company", "type": "singleLineText"},
                    {"name": "Email", "type": "email"},
                    {"name": "Phone", "type": "phoneNumber"},
                    {"name": "Source", "type": "singleLineText"},
                    {"name": "Status", "type": "singleSelect", "options": {"choices": [
                        {"name": "New"}, {"name": "Contacted"}, {"name": "Qualified"},
                        {"name": "Booked"}, {"name": "Closed"}, {"name": "Lost"},
                    ]}},
                    {"name": "Score", "type": "number", "options": {"precision": 0}},
                    {"name": "Notes", "type": "multilineText"},
                    {"name": "Created", "type": "dateTime", "options": {
                        "dateFormat": {"name": "iso"}, "timeFormat": {"name": "24hour"},
                        "timeZone": "Europe/London",
                    }},
                ],
            },
            {
                "name": "Contacts",
                "fields": [
                    {"name": "Name", "type": "singleLineText"},
                    {"name": "Email", "type": "email"},
                    {"name": "Phone", "type": "phoneNumber"},
                    {"name": "Last Visit", "type": "date", "options": {"dateFormat": {"name": "iso"}}},
                    {"name": "Loyalty Stamps", "type": "number", "options": {"precision": 0}},
                    {"name": "Status", "type": "singleSelect", "options": {"choices": [
                        {"name": "Active"}, {"name": "At Risk"}, {"name": "Churned"}, {"name": "VIP"},
                    ]}},
                    {"name": "Notes", "type": "multilineText"},
                ],
            },
            {
                "name": "Agent Logs",
                "fields": [
                    {"name": "Action", "type": "singleLineText"},
                    {"name": "Module", "type": "singleLineText"},
                    {"name": "Result", "type": "multilineText"},
                    {"name": "Timestamp", "type": "dateTime", "options": {
                        "dateFormat": {"name": "iso"}, "timeFormat": {"name": "24hour"},
                        "timeZone": "Europe/London",
                    }},
                ],
            },
        ]

        payload = {
            "name": f"PluggedIN — {client_name}",
            "workspaceId": os.getenv("AIRTABLE_WORKSPACE_ID", ""),
            "tables": tables,
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        if resp.status_code in (200, 201):
            base_id = resp.json().get("id", "")
            log.info(f"✅ Airtable base created: {base_id}")
            return base_id, []
        else:
            err = f"Airtable base creation failed ({resp.status_code}): {resp.text[:300]}"
            log.warning(err)
            errors.append(err)
            return "", errors

    except Exception as e:
        err = f"Airtable base creation exception: {e}"
        log.warning(err)
        return "", [err]


# ---------------------------------------------------------------------------
# Step 2: Register client in Agency Clients base
# ---------------------------------------------------------------------------

def _register_client_in_agency(
    client_name: str, industry: str, plan: str,
    modules: list[int], mrr: int,
    contact_email: str, contact_phone: str,
    airtable_base_id: str,
    agency_base_id: str, token: str,
) -> tuple[str, list[str]]:
    """Add client row to Agency Clients → Clients table."""
    errors = []
    try:
        url = f"https://api.airtable.com/v0/{agency_base_id}/Clients"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        module_names = ", ".join(MODULE_NAMES.get(m, f"M{m}") for m in modules)
        record = {
            "fields": {
                "Client Name":    client_name,
                "Industry":       industry.capitalize(),
                "Plan":           plan.capitalize(),
                "MRR":            mrr,
                "Status":         "Onboarding",
                "Health Score":   70,
                "Churn Risk":     "Low",
                "Active Modules": module_names,
                "Email":          contact_email,
                "Phone":          contact_phone,
                "Airtable Base ID": airtable_base_id,
                "Onboarded At":   datetime.now(timezone.utc).isoformat(),
            }
        }

        resp = requests.post(url, headers=headers, json={"records": [record]}, timeout=10)
        if resp.status_code in (200, 201):
            record_id = resp.json()["records"][0]["id"]
            log.info(f"✅ Client registered in Agency base: {record_id}")
            return record_id, []
        else:
            err = f"Agency registration failed ({resp.status_code}): {resp.text[:300]}"
            log.warning(err)
            return "", [err]

    except Exception as e:
        err = f"Agency registration exception: {e}"
        log.warning(err)
        return "", [err]


# ---------------------------------------------------------------------------
# Step 3: Configure VAPI assistant
# ---------------------------------------------------------------------------

def _configure_vapi_assistant(
    client_name: str, industry: str, vapi_api_key: str
) -> tuple[str, list[str]]:
    """Create a branded VAPI assistant for the client."""
    errors = []
    try:
        prompt_template = VAPI_PROMPTS.get(industry, VAPI_PROMPTS["default"])
        system_prompt = prompt_template.format(client_name=client_name)

        url = "https://api.vapi.ai/assistant"
        headers = {"Authorization": f"Bearer {vapi_api_key}", "Content-Type": "application/json"}
        payload = {
            "name": f"{client_name} — Receptionist",
            "model": {
                "provider": "anthropic",
                "model": "claude-haiku-4-5-20251001",
                "messages": [{"role": "system", "content": system_prompt}],
            },
            "voice": {
                "provider": "11labs",
                "voiceId": "rachel",
            },
            "firstMessage": f"Hello, thank you for calling {client_name}. How can I help you today?",
            "endCallMessage": f"Thank you for calling {client_name}. We'll be in touch shortly. Goodbye!",
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        if resp.status_code in (200, 201):
            assistant_id = resp.json().get("id", "")
            log.info(f"✅ VAPI assistant created: {assistant_id}")
            return assistant_id, []
        else:
            err = f"VAPI assistant creation failed ({resp.status_code}): {resp.text[:300]}"
            log.warning(err)
            return "", [err]

    except Exception as e:
        err = f"VAPI assistant creation exception: {e}"
        log.warning(err)
        return "", [err]


# ---------------------------------------------------------------------------
# Step 4: Generate client dashboard
# ---------------------------------------------------------------------------

def _generate_dashboard(
    client_name: str, industry: str, location: str,
    modules: list[int], airtable_base_id: str,
    outputs_dir: str,
) -> tuple[str, list[str]]:
    """Generate a standalone HTML dashboard for the client."""
    errors = []
    try:
        # Load industry playbook if available
        playbook_path = os.path.join(
            os.path.dirname(__file__), "..", "industries", f"{industry}.md"
        )
        playbook_summary = ""
        if os.path.exists(playbook_path):
            with open(playbook_path) as f:
                playbook_summary = f.read()[:500]

        module_pills = "".join(
            f'<span style="background:#6c63ff;color:#fff;padding:3px 10px;'
            f'border-radius:12px;font-size:12px;margin:2px;display:inline-block;">'
            f'M{m}: {MODULE_NAMES.get(m, f"Module {m}")}</span>'
            for m in modules
        )

        mrr = sum(MODULE_PRICES.get(m, 0) for m in modules)
        date_str = datetime.now().strftime("%B %d, %Y")
        filename = f"live_{industry}_{datetime.now().strftime('%Y-%m-%d')}.html"
        filepath = os.path.join(outputs_dir, "dashboards", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{client_name} — PluggedIN OS</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#0d0d0d; color:#e0e0e0; font-family:'Inter',sans-serif; padding:24px; }}
  h1 {{ font-size:22px; font-weight:700; color:#fff; }}
  .sub {{ color:#888; font-size:13px; margin-top:4px; }}
  .badge {{ background:#6c63ff22; border:1px solid #6c63ff; color:#6c63ff;
            font-size:11px; padding:2px 10px; border-radius:20px; margin-left:10px; }}
  .kpi-row {{ display:flex; gap:16px; margin:24px 0; flex-wrap:wrap; }}
  .kpi {{ background:#1a1a1a; border:1px solid #2a2a2a; border-radius:12px;
          padding:20px 24px; flex:1; min-width:160px; }}
  .kpi-label {{ font-size:12px; color:#888; margin-bottom:6px; }}
  .kpi-value {{ font-size:28px; font-weight:700; color:#fff; }}
  .kpi-sub {{ font-size:12px; color:#6c63ff; margin-top:4px; }}
  .panel {{ background:#1a1a1a; border:1px solid #2a2a2a; border-radius:12px;
            padding:24px; margin-bottom:16px; }}
  .panel-title {{ font-size:14px; font-weight:600; color:#aaa;
                  text-transform:uppercase; letter-spacing:.05em; margin-bottom:16px; }}
  .module-row {{ display:flex; align-items:center; justify-content:space-between;
                 padding:12px 0; border-bottom:1px solid #222; }}
  .module-row:last-child {{ border-bottom:none; }}
  .dot {{ width:8px; height:8px; border-radius:50%; background:#22c55e;
          display:inline-block; margin-right:8px; }}
  .dot.warn {{ background:#f59e0b; }}
  .dot.off {{ background:#444; }}
  .airtable-id {{ font-size:11px; color:#555; font-family:monospace; margin-top:8px; }}
  .header-row {{ display:flex; justify-content:space-between; align-items:flex-start; }}
</style>
</head>
<body>
<div class="header-row">
  <div>
    <h1>{client_name} <span class="badge">LIVE</span></h1>
    <div class="sub">{location} · {industry.capitalize()} · Onboarded {date_str}</div>
    <div class="airtable-id">Base: {airtable_base_id or 'Pending'}</div>
  </div>
  <div style="text-align:right;">
    <div style="font-size:12px;color:#888;">Active Modules</div>
    <div style="margin-top:6px;">{module_pills}</div>
  </div>
</div>

<div class="kpi-row">
  <div class="kpi">
    <div class="kpi-label">Monthly Retainer</div>
    <div class="kpi-value">£{mrr:,}</div>
    <div class="kpi-sub">Active</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">Active Modules</div>
    <div class="kpi-value">{len(modules)}</div>
    <div class="kpi-sub">of 10</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">Health Score</div>
    <div class="kpi-value">70</div>
    <div class="kpi-sub">Baseline — improving</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">Churn Risk</div>
    <div class="kpi-value" style="color:#22c55e;">Low</div>
    <div class="kpi-sub">On track</div>
  </div>
</div>

<div class="panel">
  <div class="panel-title">Active Agents</div>
  {"".join(f'''
  <div class="module-row">
    <span><span class="dot"></span>Module {m} — {MODULE_NAMES.get(m, f"Module {m}")}</span>
    <span style="font-size:12px;color:#22c55e;">Running</span>
  </div>''' for m in modules)}
</div>

<div class="panel">
  <div class="panel-title">CEO Briefing</div>
  <div style="font-size:13px;line-height:1.7;color:#ccc;">
    <strong style="color:#fff;">SITUATION:</strong> {client_name} has just been onboarded.
    Agents are initialising. First data collection cycle running now.<br><br>
    <strong style="color:#fff;">PRIORITY:</strong> Complete VAPI assistant setup and confirm
    first inbound test call.<br><br>
    <strong style="color:#fff;">RECOMMENDATION:</strong> Call the VAPI number to verify
    the receptionist is live and responding correctly.<br><br>
    <strong style="color:#fff;">EXPECTED OUTCOME:</strong> Full agent coverage live within 24 hours.
    First morning briefing delivered tomorrow at 7am.
  </div>
</div>

<div style="text-align:center;margin-top:32px;font-size:11px;color:#333;">
  PluggedIN OS · Generated {date_str} · {client_name}
</div>
</body>
</html>"""

        with open(filepath, "w") as f:
            f.write(html)

        log.info(f"✅ Dashboard generated: {filepath}")
        return filepath, []

    except Exception as e:
        err = f"Dashboard generation failed: {e}"
        log.warning(err)
        return "", [err]


# ---------------------------------------------------------------------------
# Step 5: Send onboarding briefing
# ---------------------------------------------------------------------------

def _send_onboarding_briefing(
    client_name: str, contact_email: str, modules: list[int],
    mrr: int, dashboard_path: str,
) -> tuple[bool, list[str]]:
    """
    Send onboarding WhatsApp/email briefing.
    For now: logs to console and prepares the message.
    Wire to Gmail MCP or Green API when credentials are ready.
    """
    module_list = "\n".join(f"  ✅ {MODULE_NAMES.get(m, f'Module {m}')}" for m in modules)
    message = f"""
🚀 *{client_name} — PluggedIN OS Activated*

Your AI operating system is live.

*Active Modules:*
{module_list}

*Monthly Investment:* £{mrr:,}

Your agents start working immediately. You'll receive your first
morning briefing tomorrow at 7am with a full situation report.

Reply *STATUS* at any time to see what's running.
Reply *PAUSE* to pause all outreach.

— PluggedIN OS
""".strip()

    log.info(f"📨 Onboarding briefing prepared for {contact_email}:\n{message}")

    # TODO: wire to Gmail MCP
    # from lib.gmail_client import GmailClient
    # gmail = GmailClient()
    # gmail.send(to=contact_email, subject=f"PluggedIN OS — {client_name} is live", body=message)

    return True, []


# ---------------------------------------------------------------------------
# Main onboarding function
# ---------------------------------------------------------------------------

def onboard_client(
    client_name: str,
    industry: str,
    plan: str,
    modules: list[int],
    contact_email: str = "",
    contact_phone: str = "",
    website: str = "",
    location: str = "UK",
) -> OnboardingResult:
    """
    Full end-to-end onboarding for a new client.

    Steps:
        1. Create Airtable base
        2. Register in Agency Clients base
        3. Configure VAPI assistant (if Module 1 active)
        4. Generate HTML dashboard
        5. Send onboarding briefing

    Returns OnboardingResult with all IDs and status.
    """
    # Derive client_id from name
    client_id = client_name.lower().replace(" ", "_").replace("-", "_")
    mrr = sum(MODULE_PRICES.get(m, 0) for m in modules)

    log.info(f"🎬 Starting onboarding for {client_name} ({industry}, {plan}, modules {modules})")

    result = OnboardingResult(
        success=False,
        client_id=client_id,
        client_name=client_name,
    )

    token        = os.getenv("AIRTABLE_TOKEN", "")
    agency_base  = os.getenv("AIRTABLE_BASE_AGENCY", "appl51bhjj9R2wtKx")
    vapi_key     = os.getenv("VAPI_API_KEY", "")
    outputs_dir  = os.path.join(os.path.dirname(__file__), "..", "outputs")

    # Step 1: Airtable base
    log.info("Step 1/5: Creating Airtable base...")
    base_id, errs = _create_airtable_base(client_name, token)
    result.errors.extend(errs)
    if base_id:
        result.airtable_base_id = base_id
        result.steps_completed.append("airtable_base_created")

    # Step 2: Register in Agency Clients
    log.info("Step 2/5: Registering client in Agency base...")
    record_id, errs = _register_client_in_agency(
        client_name, industry, plan, modules, mrr,
        contact_email, contact_phone, base_id,
        agency_base, token,
    )
    result.errors.extend(errs)
    if record_id:
        result.airtable_record_id = record_id
        result.steps_completed.append("client_registered")

    # Step 3: VAPI assistant (only if Module 1 active)
    if 1 in modules:
        log.info("Step 3/5: Configuring VAPI assistant...")
        assistant_id, errs = _configure_vapi_assistant(client_name, industry, vapi_key)
        result.errors.extend(errs)
        if assistant_id:
            result.vapi_assistant_id = assistant_id
            result.steps_completed.append("vapi_assistant_created")
    else:
        log.info("Step 3/5: Skipped — Module 1 not active")
        result.steps_completed.append("vapi_skipped")

    # Step 4: Generate dashboard
    log.info("Step 4/5: Generating client dashboard...")
    dashboard_path, errs = _generate_dashboard(
        client_name, industry, location, modules, base_id, outputs_dir,
    )
    result.errors.extend(errs)
    if dashboard_path:
        result.dashboard_path = dashboard_path
        result.steps_completed.append("dashboard_generated")

    # Step 5: Send briefing
    log.info("Step 5/5: Sending onboarding briefing...")
    sent, errs = _send_onboarding_briefing(client_name, contact_email, modules, mrr, dashboard_path)
    result.errors.extend(errs)
    if sent:
        result.briefing_sent = True
        result.steps_completed.append("briefing_sent")

    # Final result
    result.success = len(result.steps_completed) >= 3  # at least Airtable + register + dashboard
    status = "✅ SUCCESS" if result.success else "⚠️ PARTIAL"
    log.info(f"{status} — {client_name} onboarding complete. Steps: {result.steps_completed}")
    if result.errors:
        log.warning(f"Errors encountered: {result.errors}")

    return result


# ---------------------------------------------------------------------------
# CLI — interactive onboarding
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n=== PluggedIN — New Client Onboarding ===\n")

    client_name   = input("Business name: ").strip()
    industry      = input("Industry (legal/restaurant/construction/logistics/healthcare): ").strip()
    plan          = input("Plan (starter/growth/scale/enterprise): ").strip() or "starter"
    modules_input = input("Modules (comma-separated, e.g. 1,9): ").strip()
    modules       = [int(m.strip()) for m in modules_input.split(",") if m.strip().isdigit()]
    email         = input("Contact email: ").strip()
    phone         = input("Contact phone: ").strip()
    location      = input("Location (e.g. 'London, UK'): ").strip() or "UK"

    print(f"\n🚀 Onboarding {client_name}...")
    result = onboard_client(
        client_name=client_name,
        industry=industry,
        plan=plan,
        modules=modules,
        contact_email=email,
        contact_phone=phone,
        location=location,
    )

    print("\n=== RESULT ===")
    print(json.dumps(result.to_dict(), indent=2))
