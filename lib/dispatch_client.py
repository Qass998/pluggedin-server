"""
lib/dispatch_client.py — Business Deployment Engine
PluggedIN Dispatch System. Auto-spins infrastructure for:
  - New client onboarding (modules purchased → systems live)
  - PluggedIN Live new business launch (Opportunity Engine → live)
Never build client infrastructure manually. Always use this.
"""

import os
import json
import requests
from datetime import datetime
from typing import Optional

AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE = os.getenv("AIRTABLE_BASE_PLUGGEDIN")


# ─────────────────────────────────────────────
# CLIENT DISPATCH — NEW CLIENT INTAKE
# ─────────────────────────────────────────────

def dispatch_new_client(
    client_name: str,
    business_name: str,
    industry: str,
    phone: str,
    email: str,
    modules_purchased: list[str],
    package: str,
    monthly_value: float,
    notes: str = "",
) -> dict:
    """
    Primary entry point for new client deployment.
    Call this when a client signs. It:
    1. Creates client Airtable base entry
    2. Generates their CLAUDE.md config
    3. Logs deployment plan with timeline
    4. Returns the deployment checklist

    modules_purchased: list of module names e.g. ["Presence Agent", "Pipeline Agent"]
    package: "Starter" / "Growth" / "Scale" / "Empire OS"
    """
    dispatch_id = f"DISPATCH-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

    # Log to Airtable
    client_record = _create_client_record(
        dispatch_id=dispatch_id,
        client_name=client_name,
        business_name=business_name,
        industry=industry,
        phone=phone,
        email=email,
        modules=modules_purchased,
        package=package,
        monthly_value=monthly_value,
        notes=notes,
    )

    # Generate deployment checklist
    checklist = _build_deployment_checklist(
        client_name=client_name,
        business_name=business_name,
        industry=industry,
        modules=modules_purchased,
    )

    # Generate CLAUDE.md config text
    claude_md = _generate_client_claude_md(
        client_name=client_name,
        business_name=business_name,
        industry=industry,
        phone=phone,
        email=email,
        modules=modules_purchased,
        package=package,
    )

    return {
        "dispatch_id": dispatch_id,
        "client_name": client_name,
        "business_name": business_name,
        "modules": modules_purchased,
        "package": package,
        "monthly_value": monthly_value,
        "airtable_record_id": client_record.get("id"),
        "deployment_checklist": checklist,
        "claude_md": claude_md,
        "status": "dispatched",
        "dispatched_at": datetime.utcnow().isoformat(),
    }


def provision_presence_agent(
    client_id: str,
    client_name: str,
    business_name: str,
    industry: str,
    cal_link: str,
    faqs: list[dict] = None,
    business_hours: str = "Monday to Friday, 9am to 6pm",
    country: str = "US",
    area_code: str = None,
    whatsapp_number: str = None,
    ceo_phone: str = None,
    tone: str = "professional but warm",
    language: str = "English",
) -> dict:
    """
    Provision Module 1 (Presence Agent) for a client.

    This function:
    1. Creates the VAPI inbound receptionist assistant (voice)
    2. Provisions a real phone number
    3. Ties the number to the assistant
    4. Registers the WhatsApp agent for this client
    5. Stores everything in Airtable

    For African/UK clients: pass whatsapp_number (their Twilio WhatsApp number)
    instead of relying on VAPI native phone provisioning.

    Returns phone number, assistant, and WhatsApp details.
    """
    from lib import vapi_client, airtable_client
    
    if faqs is None:
        faqs = [
            {"question": f"What are your hours?", "answer": business_hours},
            {"question": "How can I book a consultation?", "answer": f"Visit {cal_link}"},
        ]
    
    try:
        # Step 1: Create inbound assistant
        assistant = vapi_client.create_inbound_assistant(
            client_name=client_name,
            business_name=business_name,
            industry=industry,
            cal_link=cal_link,
            faqs=faqs,
            business_hours=business_hours,
            escalation_phone="",  # Optional
        )
        assistant_id = assistant.get("id")
        
        # Step 2: Provision phone number
        phone_data = vapi_client.provision_inbound_phone(
            client_id=client_id,
            assistant_id=assistant_id,
            country=country,
            area_code=area_code,
        )
        # VAPI phone endpoint returns id and status, not a readable phone number
        # The phone number will be assigned by VAPI backend
        phone_number_id = phone_data.get("id")
        
        # For now, we'll use a placeholder since VAPI doesn't return the actual number
        # in the provisioning response. The client would get this from the VAPI dashboard.
        phone_number = f"VAPI-{phone_number_id}"  # Placeholder
        
        # Step 3: Update client record in Airtable with phone info
        airtable_client.update_client_vapi(
            client_id=client_id,
            phone_number=phone_number,
            phone_number_id=phone_number_id,
            vapi_assistant_id=assistant_id,
            module_1_status="active",
        )

        # Step 4: Register WhatsApp agent for this client
        whatsapp_registered = False
        if whatsapp_number:
            try:
                from lib import whatsapp_agent
                whatsapp_agent.register_client(
                    twilio_whatsapp_number=whatsapp_number,
                    config={
                        "client_id":      client_id,
                        "client_name":    client_name,
                        "business_name":  business_name,
                        "industry":       industry,
                        "cal_link":       cal_link,
                        "business_hours": business_hours,
                        "faqs":           faqs or [],
                        "ceo_phone":      ceo_phone,
                        "tone":           tone,
                        "language":       language,
                    }
                )
                whatsapp_registered = True
            except Exception as e:
                print(f"[Dispatch] WhatsApp registration error: {e}")

        return {
            "client_id":          client_id,
            "phone_number_id":    phone_number_id,
            "assistant_id":       assistant_id,
            "business_name":      business_name,
            "whatsapp_number":    whatsapp_number or "not configured",
            "whatsapp_active":    whatsapp_registered,
            "status":             "active",
            "provisioned_at":     datetime.utcnow().isoformat(),
            "message":            f"✓ Presence Agent live for {business_name}. Voice + {'WhatsApp ✓' if whatsapp_registered else 'WhatsApp not configured'}",
            "note":               "Check VAPI dashboard for allocated voice number. WhatsApp ready if number provided.",
        }
    except Exception as e:
        return {
            "client_id": client_id,
            "status": "failed",
            "error": str(e),
        }


def _create_client_record(
    dispatch_id: str,
    client_name: str,
    business_name: str,
    industry: str,
    phone: str,
    email: str,
    modules: list[str],
    package: str,
    monthly_value: float,
    notes: str,
) -> dict:
    """Create the client record in Airtable."""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE}/Clients"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "fields": {
            "DispatchID": dispatch_id,
            "ClientName": client_name,
            "BusinessName": business_name,
            "Industry": industry,
            "Phone": phone,
            "Email": email,
            "ModulesPurchased": ", ".join(modules),
            "Package": package,
            "MonthlyValue": monthly_value,
            "Status": "Onboarding",
            "SignedAt": datetime.utcnow().isoformat(),
            "Notes": notes,
        }
    }
    r = requests.post(url, json=payload, headers=headers)
    r.raise_for_status()
    return r.json()


def _build_deployment_checklist(
    client_name: str,
    business_name: str,
    industry: str,
    modules: list[str],
) -> list[dict]:
    """
    Build a step-by-step deployment checklist based on modules purchased.
    Returns ordered list of tasks with owner and ETA.
    """
    base_steps = [
        {"step": 1, "task": f"Create Clients/{client_name}/ workspace folder", "owner": "Claude Code", "eta": "Hour 1"},
        {"step": 2, "task": f"Generate {client_name}/CLAUDE.md from template", "owner": "Claude Code", "eta": "Hour 1"},
        {"step": 3, "task": f"Copy scoring-criteria.md and copy-framework.md", "owner": "Claude Code", "eta": "Hour 1"},
        {"step": 4, "task": f"Create Airtable base for {business_name}", "owner": "Claude Code", "eta": "Hour 1"},
        {"step": 5, "task": f"Set up Softr client portal", "owner": "Claude Code", "eta": "Hour 2"},
        {"step": 6, "task": f"Book VAPI onboarding call with {client_name}", "owner": "VAPI Agent", "eta": "Hour 2"},
    ]

    module_steps = {
        "Presence Agent": {"task": "Configure VAPI receptionist + Cal.com booking", "owner": "VAPI Agent", "eta": "Hour 3"},
        "Pipeline Agent": {"task": "Set up Apify + Vibe scraper for lead research", "owner": "Claude Code", "eta": "Hour 3"},
        "Marketing Agent": {"task": "Connect Creatomate + Artlist + platform accounts", "owner": "Claude Code", "eta": "Hour 4"},
        "Intelligence Agent": {"task": "Configure competitor monitoring + signal sources", "owner": "Claude Code", "eta": "Hour 3"},
        "Sales Intelligence": {"task": "Set up call recording analysis pipeline", "owner": "Claude Code", "eta": "Hour 4"},
        "Data Intelligence": {"task": "Configure KPI dashboard + Remotion template", "owner": "Claude Code", "eta": "Hour 4"},
        "Conversion Agent": {"task": "Connect website + set up lead scoring rules", "owner": "Claude Code", "eta": "Hour 4"},
        "Lead Marketplace": {"task": "Configure VAPI outbound + Airtable matching", "owner": "VAPI Agent", "eta": "Hour 4"},
        "Customer Retention OS": {"task": "Set up WhatsApp loyalty + churn detection", "owner": "Claude Code", "eta": "Hour 3"},
        "Stock Intelligence": {"task": "Configure stock thresholds + supplier alerts", "owner": "Claude Code", "eta": "Hour 3"},
    }

    step_num = len(base_steps) + 1
    for module in modules:
        if module in module_steps:
            step = module_steps[module].copy()
            step["step"] = step_num
            base_steps.append(step)
            step_num += 1

    # Final steps
    base_steps.extend([
        {"step": step_num, "task": "Complete VAPI onboarding call — capture business brain", "owner": "VAPI Agent", "eta": "Day 2"},
        {"step": step_num + 1, "task": "Populate all memory layers from onboarding data", "owner": "Claude Code", "eta": "Day 2"},
        {"step": step_num + 2, "task": "Deploy CEO Agent and configure daily briefing", "owner": "Claude Code", "eta": "Day 2"},
        {"step": step_num + 3, "task": "Send first morning briefing to client", "owner": "CEO Agent", "eta": "Day 3 7am"},
        {"step": step_num + 4, "task": "30-day check-in call scheduled", "owner": "VAPI Agent", "eta": "Day 30"},
    ])

    return base_steps


def _generate_client_claude_md(
    client_name: str,
    business_name: str,
    industry: str,
    phone: str,
    email: str,
    modules: list[str],
    package: str,
) -> str:
    """
    Generate the CLAUDE.md content for a new client workspace.
    This becomes the AI brain for all client operations.
    """
    modules_text = "\n".join([f"→ {m}" for m in modules])
    return f"""# {business_name} — AI Operating System
# Client: {client_name}
# Industry: {industry}
# Package: {package}
# Managed by PluggedIN

---

## BUSINESS PROFILE

Business: {business_name}
Industry: {industry}
Owner: {client_name}
Phone: {phone}
Email: {email}
Package: {package}
Status: Active

---

## ACTIVE MODULES

{modules_text}

---

## AGENT PSYCHOLOGY

Same rules as PluggedIN master brain.
Never ask what to do. Read data. Report findings.
Use the standard briefing format for all proactive updates.

---

## MEMORY STRUCTURE

memory/working/today.md — active tasks and priority
memory/working/pipeline.md — live lead tracker
memory/episodic/log.md — session history
memory/semantic/customers.md — customer profiles
memory/semantic/products.md — services and products
memory/personal/owner.md — owner preferences

---

## RULES

All API calls via lib/ scripts — never raw.
All data logged to Airtable immediately.
All briefings delivered at 7am via WhatsApp.
CEO Agent runs daily without prompting.
Human staff submit via portal — never call owner.

---

## STATUS

Deployed: {datetime.utcnow().strftime('%Y-%m-%d')}
Onboarding: Pending VAPI call
First briefing: Pending onboarding completion
"""


# ─────────────────────────────────────────────
# PLUGGEDIN LIVE — NEW BUSINESS LAUNCH
# ─────────────────────────────────────────────

def launch_new_business(
    business_name: str,
    niche: str,
    business_type: str,
    opportunity_score: float,
    initial_investment: float,
    revenue_model: str,
    target_market: str,
    approved_by: str = "Qassim",
) -> dict:
    """
    Launch a new PluggedIN Live business.
    Called by Opportunity Engine after Qassim approval.
    business_type: "lead_gen", "digital_product", "ecommerce",
                  "youtube", "commodity", "saas_tool"
    Returns launch plan with 5-hour deployment timeline.
    """
    launch_id = f"LAUNCH-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

    # Log to Airtable
    _log_business_launch(
        launch_id=launch_id,
        business_name=business_name,
        niche=niche,
        business_type=business_type,
        opportunity_score=opportunity_score,
        initial_investment=initial_investment,
        approved_by=approved_by,
    )

    # Build launch timeline
    timeline = _build_launch_timeline(business_type, business_name, niche)

    return {
        "launch_id": launch_id,
        "business_name": business_name,
        "niche": niche,
        "type": business_type,
        "revenue_model": revenue_model,
        "target_market": target_market,
        "opportunity_score": opportunity_score,
        "initial_investment": initial_investment,
        "timeline": timeline,
        "approved_by": approved_by,
        "status": "launched",
        "launched_at": datetime.utcnow().isoformat(),
    }


def _log_business_launch(
    launch_id: str,
    business_name: str,
    niche: str,
    business_type: str,
    opportunity_score: float,
    initial_investment: float,
    approved_by: str,
) -> dict:
    """Log new business launch to PluggedIN Airtable."""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE}/PluggedINLive"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "fields": {
            "LaunchID": launch_id,
            "BusinessName": business_name,
            "Niche": niche,
            "Type": business_type,
            "OpportunityScore": opportunity_score,
            "InitialInvestment": initial_investment,
            "ApprovedBy": approved_by,
            "Status": "Launching",
            "LaunchedAt": datetime.utcnow().isoformat(),
        }
    }
    r = requests.post(url, json=payload, headers=headers)
    r.raise_for_status()
    return r.json()


def _build_launch_timeline(
    business_type: str,
    business_name: str,
    niche: str,
) -> list[dict]:
    """Build 5-hour launch timeline based on business type."""
    common = [
        {"hour": 1, "task": f"Research top 5 competitors in {niche}", "agent": "Intelligence Agent"},
        {"hour": 1, "task": f"Create brand name, tagline, colour palette for {business_name}", "agent": "Brand Agent"},
        {"hour": 2, "task": "Register domain + set up email", "agent": "Brand Agent"},
    ]

    type_specific = {
        "lead_gen": [
            {"hour": 2, "task": "Build Framer landing page with lead capture form", "agent": "Website Agent"},
            {"hour": 3, "task": "Scrape buyer list from trade directories", "agent": "Lead Gen Agent"},
            {"hour": 4, "task": "Configure VAPI for lead qualification calls", "agent": "VAPI Agent"},
            {"hour": 5, "task": "Launch first outreach sequence to buyers", "agent": "Pipeline Agent"},
        ],
        "digital_product": [
            {"hour": 2, "task": "Scrape bestselling products in niche on Gumroad/Etsy", "agent": "Ecommerce Agent"},
            {"hour": 3, "task": "Create first 3 digital products (templates/guides)", "agent": "Marketing Agent"},
            {"hour": 4, "task": "Set up Gumroad store + Etsy listings", "agent": "Website Agent"},
            {"hour": 5, "task": "Create Pinterest boards + first 20 pins for traffic", "agent": "Marketing Agent"},
        ],
        "ecommerce": [
            {"hour": 2, "task": "Source winning products with margin analysis", "agent": "Ecommerce Agent"},
            {"hour": 3, "task": "Contact top 3 AliExpress/Alibaba suppliers", "agent": "Ecommerce Agent"},
            {"hour": 4, "task": "Build Shopify store with product listings", "agent": "Website Agent"},
            {"hour": 5, "task": "Write first 3 Meta ad creatives via Creatomate", "agent": "Marketing Agent"},
        ],
        "youtube": [
            {"hour": 2, "task": "Scrape top 20 videos in niche — extract hooks and formats", "agent": "YouTube Agent"},
            {"hour": 3, "task": "Create channel brand + first 5 video scripts", "agent": "Brand Agent"},
            {"hour": 4, "task": "Produce first 2 videos via Creatomate + Artlist + ElevenLabs", "agent": "Marketing Agent"},
            {"hour": 5, "task": "Upload and optimise with SEO titles/descriptions/thumbnails", "agent": "YouTube Agent"},
        ],
        "commodity": [
            {"hour": 2, "task": "Research commodity pricing + supply chain contacts", "agent": "Intelligence Agent"},
            {"hour": 3, "task": "Source 5 producer contacts via Apify + LinkedIn", "agent": "Lead Gen Agent"},
            {"hour": 4, "task": "Source 5 buyer contacts via Vibe Prospecting", "agent": "Lead Gen Agent"},
            {"hour": 5, "task": "Configure VAPI qualification calls for both sides", "agent": "VAPI Agent"},
        ],
    }

    specifics = type_specific.get(business_type, [])
    all_tasks = common + specifics

    # Add final task
    all_tasks.append({
        "hour": 5,
        "task": f"Assign CEO Agent — {business_name} now reporting to Chief of All Chiefs",
        "agent": "CEO Agent",
    })

    return all_tasks


# ─────────────────────────────────────────────
# DEPLOYMENT STATUS
# ─────────────────────────────────────────────

def get_deployment_status(dispatch_id: str) -> dict:
    """
    Check the status of a client or business deployment.
    Queries Airtable for the dispatch record.
    """
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE}/Clients"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    params = {
        "filterByFormula": f"{{DispatchID}} = '{dispatch_id}'",
        "maxRecords": 1,
    }
    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()
    records = r.json().get("records", [])
    if not records:
        return {"error": f"No deployment found for {dispatch_id}"}
    return records[0]["fields"]


def list_active_deployments() -> list[dict]:
    """
    List all active client deployments.
    Useful for morning briefing: who's onboarding, who's live.
    """
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE}/Clients"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    params = {
        "filterByFormula": "OR({Status} = 'Onboarding', {Status} = 'Active')",
        "sort[0][field]": "SignedAt",
        "sort[0][direction]": "desc",
    }
    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()
    records = r.json().get("records", [])

    return [
        {
            "client": rec["fields"].get("ClientName", ""),
            "business": rec["fields"].get("BusinessName", ""),
            "industry": rec["fields"].get("Industry", ""),
            "package": rec["fields"].get("Package", ""),
            "monthly_value": rec["fields"].get("MonthlyValue", 0),
            "status": rec["fields"].get("Status", ""),
            "signed_at": rec["fields"].get("SignedAt", ""),
            "dispatch_id": rec["fields"].get("DispatchID", ""),
        }
        for rec in records
    ]
