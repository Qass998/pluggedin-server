"""
lib/client_manager.py — PluggedIN Multi-Tenant Client Manager

Handles all per-client operations:
- Fetching active clients from Airtable
- Generating personalised briefings per client
- Sending WhatsApp + email to each client
- Filtering Airtable data by ClientID so each client sees only their data

Clients table (Airtable — PluggedIN base):
  Name, CompanyName, Phone, Email, Plan, Active, BriefingEnabled,
  AirtableBaseID, CalComLink, OnboardedAt, Notes

Usage:
  from lib.client_manager import deliver_all_client_briefings
  deliver_all_client_briefings(dry_run=False)
"""

import os
import smtplib
import requests
from datetime import date, datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

AIRTABLE_TOKEN      = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE       = os.getenv("AIRTABLE_BASE_PLUGGEDIN")
TWILIO_ACCOUNT_SID  = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN   = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM         = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
GMAIL_USER          = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD  = os.getenv("GMAIL_APP_PASSWORD")
OPENROUTER_KEY      = os.getenv("OPENROUTER_API_KEY")

AT_HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_TOKEN}",
    "Content-Type": "application/json"
}
AT_BASE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE}"


# ─────────────────────────────────────────────
# AIRTABLE HELPERS
# ─────────────────────────────────────────────

def _at_read(table: str, filter_formula: str = None, max_records: int = 100) -> list:
    url = f"{AT_BASE_URL}/{table}"
    params = {"maxRecords": max_records}
    if filter_formula:
        params["filterByFormula"] = filter_formula
    r = requests.get(url, headers=AT_HEADERS, params=params, timeout=15)
    r.raise_for_status()
    return r.json().get("records", [])


def _at_write(table: str, fields: dict) -> dict:
    url = f"{AT_BASE_URL}/{table}"
    r = requests.post(url, headers=AT_HEADERS, json={"fields": fields}, timeout=15)
    r.raise_for_status()
    return r.json()


# ─────────────────────────────────────────────
# CLIENT FETCHING
# ─────────────────────────────────────────────

def get_active_clients() -> list:
    """
    Fetch all active clients from the Clients table.
    Returns list of client dicts with fields unpacked.

    Example client dict:
    {
        "id": "recXXXXXXXX",
        "name": "John Smith",
        "company": "Acme Ltd",
        "phone": "+447911123456",
        "email": "john@acme.com",
        "plan": "Growth",
        "briefing_enabled": True,
        "airtable_base_id": "appXXXXXX",  # their own base (optional)
        "cal_com_link": "https://cal.com/john",
        "onboarded_at": "2026-04-01",
        "notes": ""
    }
    """
    try:
        records = _at_read("Clients", filter_formula="AND({Active}=1, {BriefingEnabled}=1)")
        clients = []
        for r in records:
            f = r.get("fields", {})
            clients.append({
                "id": r["id"],
                "name": f.get("Name", ""),
                "company": f.get("CompanyName", ""),
                "phone": f.get("Phone", ""),
                "email": f.get("Email", ""),
                "plan": f.get("Plan", "Starter"),
                "briefing_enabled": bool(f.get("BriefingEnabled", True)),
                "airtable_base_id": f.get("AirtableBaseID", AIRTABLE_BASE),
                "cal_com_link": f.get("CalComLink", ""),
                "onboarded_at": f.get("OnboardedAt", ""),
                "notes": f.get("Notes", ""),
                "brand": f.get("Brand", f.get("CompanyName", "")),
            })
        return clients
    except Exception as e:
        print(f"[client_manager] Could not fetch clients: {e}")
        return []


# ─────────────────────────────────────────────
# PER-CLIENT DATA FETCHING
# ─────────────────────────────────────────────

def get_client_leads(client: dict, status: str = None) -> list:
    """Fetch leads linked to this client."""
    base_id = client.get("airtable_base_id", AIRTABLE_BASE)
    url = f"https://api.airtable.com/v0/{base_id}/Leads"
    formula = f"{{ClientID}} = '{client['id']}'"
    if status:
        formula = f"AND({formula}, {{Status}} = '{status}')"
    params = {"filterByFormula": formula, "maxRecords": 50}
    r = requests.get(url, headers=AT_HEADERS, params=params, timeout=15)
    return r.json().get("records", []) if r.ok else []


def get_client_opportunities(client: dict) -> list:
    """Fetch opportunities linked to this client."""
    base_id = client.get("airtable_base_id", AIRTABLE_BASE)
    url = f"https://api.airtable.com/v0/{base_id}/Opportunities"
    params = {
        "filterByFormula": f"AND({{ClientID}} = '{client['id']}', {{Score}} >= 60)",
        "maxRecords": 10,
        "sort[0][field]": "Score",
        "sort[0][direction]": "desc",
    }
    r = requests.get(url, headers=AT_HEADERS, params=params, timeout=15)
    return r.json().get("records", []) if r.ok else []


def get_client_ceo_reports(client: dict) -> list:
    """Fetch today's CEO reports for this client's domain/brand."""
    brand = client.get("brand", "")
    formula = f"AND(IS_SAME({{Date}}, TODAY(), 'day'), {{ClientID}} = '{client['id']}')"
    try:
        return _at_read("CEOReports", filter_formula=formula, max_records=10)
    except Exception:
        return []


# ─────────────────────────────────────────────
# BRIEFING GENERATION
# ─────────────────────────────────────────────

def generate_client_briefing(client: dict) -> str:
    """
    Generate a personalised WhatsApp briefing for a single client.
    Pulls their leads, opportunities, and CEO reports.
    """
    leads = get_client_leads(client)
    opps = get_client_opportunities(client)
    reports = get_client_ceo_reports(client)

    new_leads = [r for r in leads if r["fields"].get("Status") == "New"]
    hot_leads = [r for r in leads if r["fields"].get("Status") in ("Replied", "Interested", "Meeting Booked")]
    top_opp = opps[0]["fields"] if opps else {}

    report_text = "\n".join([
        f"{r['fields'].get('Domain', '')}: {r['fields'].get('Summary', '')}"
        for r in reports
    ]) if reports else "Agent activity running."

    # Build briefing via AI
    prompt = f"""
You are writing a personalised daily WhatsApp briefing for {client['name']} at {client['company']}.
Today is {date.today().strftime('%A, %d %B %Y')}.
Plan: {client['plan']}

Their data today:
- New leads found: {len(new_leads)}
- Hot leads (replied/interested): {len(hot_leads)}
- Top opportunity: {top_opp.get('Name', 'None')} (Score: {top_opp.get('Score', 0)}/100 if top_opp else '')
- Agent activity: {report_text[:500]}

Write a concise WhatsApp briefing (max 200 words) in this format:
📊 *PluggedIN — Your Daily Update*
_{date.today().strftime('%d %b %Y')}_

[2-3 lines summarising their specific results]

*NEW LEADS:* [N]
*HOT LEADS:* [N]
*TOP OPPORTUNITY:* [name or None]

*NEXT ACTION:* [one specific thing they or the agent should do]

---
_Reply *MORE* for full lead list_
_Reply *PAUSE* to hold agent activity_

Keep it personalised, specific to their data, and encouraging but honest.
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
                "max_tokens": 400,
                "messages": [
                    {"role": "system", "content": "You write concise, personalised WhatsApp business briefings. Use *bold* for emphasis."},
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=30,
        )
        if r.ok:
            return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[client_manager] Briefing AI call failed for {client['name']}: {e}")

    # Fallback: plain text briefing without AI
    return (
        f"📊 *PluggedIN — Your Daily Update*\n"
        f"_{date.today().strftime('%d %b %Y')}_\n\n"
        f"*{client['company']}* — agents running.\n\n"
        f"*NEW LEADS:* {len(new_leads)}\n"
        f"*HOT LEADS:* {len(hot_leads)}\n"
        f"*TOP OPP:* {top_opp.get('Name', 'None')}\n\n"
        f"---\n_Reply *MORE* for full lead list_"
    )


# ─────────────────────────────────────────────
# DELIVERY — WHATSAPP
# ─────────────────────────────────────────────

def send_whatsapp_to_client(client: dict, message: str, dry_run: bool = False) -> bool:
    """Send WhatsApp briefing to a client via Twilio."""
    phone = client.get("phone", "").strip()
    if not phone:
        print(f"[client_manager] No phone for {client['name']} — skipping WhatsApp")
        return False

    if dry_run:
        print(f"[DRY RUN] Would WhatsApp {client['name']} ({phone}):\n{message}\n")
        return True

    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        print(f"[client_manager] Twilio not configured — skipping WhatsApp for {client['name']}")
        return False

    try:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
        r = requests.post(url, data={
            "From": TWILIO_FROM,
            "To": f"whatsapp:{phone}",
            "Body": message,
        }, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN), timeout=15)

        if r.ok:
            print(f"[client_manager] ✓ WhatsApp sent to {client['name']} ({phone})")
            return True
        else:
            print(f"[client_manager] ✗ WhatsApp failed for {client['name']}: {r.status_code} {r.text[:100]}")
            return False
    except Exception as e:
        print(f"[client_manager] WhatsApp error for {client['name']}: {e}")
        return False


# ─────────────────────────────────────────────
# DELIVERY — EMAIL
# ─────────────────────────────────────────────

def send_email_to_client(client: dict, subject: str, body: str, dry_run: bool = False) -> bool:
    """Send email briefing/report to a client via Gmail."""
    email = client.get("email", "").strip()
    if not email:
        print(f"[client_manager] No email for {client['name']} — skipping email")
        return False

    if dry_run:
        print(f"[DRY RUN] Would email {client['name']} ({email}): {subject}")
        return True

    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print(f"[client_manager] Gmail not configured — skipping email for {client['name']}")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"PluggedIN AI <{GMAIL_USER}>"
        msg["To"] = email

        # Plain text version
        text_part = MIMEText(body, "plain")

        # HTML version (simple formatting)
        html_body = body.replace("\n", "<br>").replace("*", "<b>").replace("*", "</b>")
        html_part = MIMEText(
            f"""<html><body style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:20px;">
            <p>{html_body}</p>
            <hr><p style="color:#888;font-size:12px;">
            PluggedIN AI Agency | Automated Daily Briefing<br>
            Manage your account: <a href="https://pluggedin.ai">pluggedin.ai</a>
            </p></body></html>""",
            "html"
        )
        msg.attach(text_part)
        msg.attach(html_part)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, email, msg.as_string())

        print(f"[client_manager] ✓ Email sent to {client['name']} ({email})")
        return True

    except Exception as e:
        print(f"[client_manager] Email error for {client['name']}: {e}")
        return False


# ─────────────────────────────────────────────
# LOG DELIVERY
# ─────────────────────────────────────────────

def log_briefing_delivery(client: dict, channel: str, success: bool):
    """Log that a briefing was sent to a client."""
    try:
        _at_write("ClientBriefings", {
            "ClientID": client["id"],
            "ClientName": client["name"],
            "Date": date.today().isoformat(),
            "Channel": channel,
            "Status": "Delivered" if success else "Failed",
            "SentAt": datetime.now().isoformat(),
        })
    except Exception:
        pass  # Non-critical — don't fail the whole run


# ─────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────

def deliver_all_client_briefings(dry_run: bool = False) -> dict:
    """
    Main function. Called by orchestrator at 07:00 after Qassim's briefing.
    Loops through all active clients and sends each a personalised briefing.

    Returns summary dict:
    {
        "total_clients": 3,
        "whatsapp_sent": 3,
        "emails_sent": 3,
        "failed": 0,
        "clients": ["John Smith", "Jane Doe", ...]
    }
    """
    print(f"\n[client_manager] Delivering briefings to all active clients...")
    clients = get_active_clients()

    if not clients:
        print("[client_manager] No active clients with briefing enabled. Add clients to the Clients table in Airtable.")
        return {"total_clients": 0, "whatsapp_sent": 0, "emails_sent": 0, "failed": 0}

    print(f"[client_manager] Found {len(clients)} active client(s): {[c['name'] for c in clients]}")

    results = {
        "total_clients": len(clients),
        "whatsapp_sent": 0,
        "emails_sent": 0,
        "failed": 0,
        "clients": [],
    }

    for client in clients:
        print(f"\n[client_manager] Processing {client['name']} ({client['company']})...")
        try:
            # Generate personalised briefing
            briefing = generate_client_briefing(client)

            # Send WhatsApp
            if client.get("phone"):
                ok = send_whatsapp_to_client(client, briefing, dry_run=dry_run)
                if ok:
                    results["whatsapp_sent"] += 1
                    log_briefing_delivery(client, "WhatsApp", True)
                else:
                    log_briefing_delivery(client, "WhatsApp", False)

            # Send email
            if client.get("email"):
                subject = f"PluggedIN Daily Briefing — {date.today().strftime('%d %b %Y')}"
                ok = send_email_to_client(client, subject, briefing, dry_run=dry_run)
                if ok:
                    results["emails_sent"] += 1
                    log_briefing_delivery(client, "Email", True)
                else:
                    log_briefing_delivery(client, "Email", False)

            results["clients"].append(client["name"])

        except Exception as e:
            print(f"[client_manager] ERROR for {client['name']}: {e}")
            results["failed"] += 1

    print(f"\n[client_manager] Done — {results['whatsapp_sent']} WhatsApp, {results['emails_sent']} email, {results['failed']} failed")
    return results


# ─────────────────────────────────────────────
# ONBOARDING HELPER
# ─────────────────────────────────────────────

def onboard_client(
    name: str,
    company: str,
    email: str,
    phone: str,
    plan: str = "Starter",
    brand: str = "",
    cal_com_link: str = "",
    notes: str = "",
    dry_run: bool = False,
) -> dict:
    """
    Add a new client to Airtable and send them a welcome WhatsApp + email.
    Called manually or triggered by intake form.

    Plans: Starter / Growth / Scale
    """
    print(f"[client_manager] Onboarding {name} ({company}) on {plan} plan...")

    if dry_run:
        print(f"[DRY RUN] Would create client record and send welcome messages")
        return {"success": True, "client_id": "dry_run"}

    # Create client record
    record = _at_write("Clients", {
        "Name": name,
        "CompanyName": company,
        "Email": email,
        "Phone": phone,
        "Plan": plan,
        "Brand": brand or company,
        "CalComLink": cal_com_link,
        "Active": True,
        "BriefingEnabled": True,
        "OnboardedAt": date.today().isoformat(),
        "Notes": notes,
    })

    client_id = record.get("id", "")
    client = {
        "id": client_id,
        "name": name,
        "company": company,
        "email": email,
        "phone": phone,
        "plan": plan,
        "brand": brand or company,
    }

    # Welcome WhatsApp
    welcome_whatsapp = (
        f"👋 Welcome to *PluggedIN*, {name.split()[0]}!\n\n"
        f"Your AI agent system is now active for *{company}*.\n\n"
        f"You'll receive your first daily briefing tomorrow at 07:00.\n\n"
        f"What the agents are doing for you:\n"
        f"• 🔍 Scanning for leads and opportunities\n"
        f"• 📊 Monitoring your market daily\n"
        f"• 📧 Running outreach on autopilot\n\n"
        f"Questions? Reply to this message anytime.\n"
        f"---\n_PluggedIN AI Agency_"
    )
    send_whatsapp_to_client(client, welcome_whatsapp)

    # Welcome email
    welcome_email = (
        f"Hi {name.split()[0]},\n\n"
        f"Welcome to PluggedIN. Your AI agent system is now active for {company}.\n\n"
        f"You'll receive your first daily briefing tomorrow at 07:00 (WhatsApp + email).\n\n"
        f"Your portal: {f'https://app.softr.io (login: {email})' if email else 'coming soon'}\n"
        f"Your booking link: {cal_com_link or 'Being set up'}\n\n"
        f"What happens next:\n"
        f"- Agents will begin scanning your market tonight\n"
        f"- First briefing arrives at 07:00 tomorrow\n"
        f"- Your Airtable dashboard is live — check your portal\n\n"
        f"Any questions, reply to this email.\n\n"
        f"Best,\nPluggedIN AI\n"
    )
    send_email_to_client(client, f"Welcome to PluggedIN — {company} is live", welcome_email)

    print(f"[client_manager] ✓ {name} onboarded successfully (ID: {client_id})")
    return {"success": True, "client_id": client_id, "client": client}
