"""
PluggedIN Python Wrappers
lib/airtable_client.py

Airtable API wrapper for CRM operations.
All data flows through this wrapper.
Agent calls these methods directly.
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
BASE_GROMATIC = os.getenv("AIRTABLE_BASE_GROMATIC")
BASE_PLUGGEDIN = os.getenv("AIRTABLE_BASE_PLUGGEDIN")
BASE_URL = "https://api.airtable.com/v0"

HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_TOKEN}",
    "Content-Type": "application/json"
}


def log_lead(base_id: str, firm_name: str, contact_name: str,
             email: str, phone: str, website: str,
             score: int, tier: str, signals: list) -> dict:
    """
    Log a new lead to Airtable.
    
    Example:
    log_lead(
        BASE_GROMATIC,
        "Graham Coffey & Co",
        "Graham Coffey",
        "info@gcoffey.co.uk",
        "0161 826 4875",
        "gcoffey.co.uk",
        85,
        "Tier 1",
        ["hiring housing lawyer", "mentions expert witnesses"]
    )
    """
    url = f"{BASE_URL}/{base_id}/Leads"
    
    payload = {
        "records": [{
            "fields": {
                "Firm Name": firm_name,
                "Contact Name": contact_name,
                "Email": email,
                "Phone": phone,
                "Website": website,
                "Score": score,
                "Tier": tier,
                "Signals": ", ".join(signals),
                "Status": "New",
                "Date Added": datetime.now().isoformat()
            }
        }]
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    return response.json()


def update_pipeline(base_id: str, record_id: str,
                    status: str, notes: str = "") -> dict:
    """
    Update a lead's pipeline status.
    
    Status options:
    New → Contacted → Replied → Interested →
    Meeting Booked → Meeting Done → Referred → Closed
    
    Example:
    update_pipeline(
        BASE_GROMATIC,
        "recXXXXXXXX",
        "Replied",
        "Expressed interest in Gromatic's services"
    )
    """
    url = f"{BASE_URL}/{base_id}/Leads/{record_id}"
    
    payload = {
        "fields": {
            "Status": status,
            "Notes": notes,
            "Last Updated": datetime.now().isoformat()
        }
    }
    
    response = requests.patch(url, headers=HEADERS, json=payload)
    return response.json()


def log_outreach(base_id: str, lead_id: str,
                 channel: str, subject: str,
                 message: str, sent_at: str = None) -> dict:
    """
    Log outreach activity to Airtable.
    
    Example:
    log_outreach(
        BASE_GROMATIC,
        "recXXXXXXXX",
        "Email",
        "Introduction - Graham Coffey x Gromatic",
        "Full email text here..."
    )
    """
    url = f"{BASE_URL}/{base_id}/Outreach"
    
    payload = {
        "records": [{
            "fields": {
                "Lead": [lead_id],
                "Channel": channel,
                "Subject": subject,
                "Message": message,
                "Sent At": sent_at or datetime.now().isoformat(),
                "Status": "Sent"
            }
        }]
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    return response.json()


def get_leads(base_id: str, tier: str = None,
              status: str = None) -> list:
    """
    Get leads from Airtable with optional filtering.
    
    Example:
    tier1_leads = get_leads(BASE_GROMATIC, tier="Tier 1")
    new_leads = get_leads(BASE_GROMATIC, status="New")
    """
    url = f"{BASE_URL}/{base_id}/Leads"
    
    params = {}
    filters = []
    
    if tier:
        filters.append(f"{{Tier}}='{tier}'")
    if status:
        filters.append(f"{{Status}}='{status}'")
    
    if filters:
        params["filterByFormula"] = f"AND({','.join(filters)})"
    
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json().get("records", [])


def create_report(base_id: str, week_ending: str,
                  firms_contacted: int, replies: int,
                  meetings_booked: int, summary: str) -> dict:
    """
    Create a weekly performance report in Airtable.
    
    Example:
    create_report(
        BASE_GROMATIC,
        "2026-04-25",
        10, 3, 1,
        "Good response rate this week..."
    )
    """
    url = f"{BASE_URL}/{base_id}/Reports"
    
    payload = {
        "records": [{
            "fields": {
                "Week Ending": week_ending,
                "Firms Contacted": firms_contacted,
                "Replies": replies,
                "Meetings Booked": meetings_booked,
                "Reply Rate": f"{(replies/firms_contacted*100):.0f}%" if firms_contacted > 0 else "0%",
                "Summary": summary,
                "Created At": datetime.now().isoformat()
            }
        }]
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    return response.json()


# ─────────────────────────────────────────────
# CLIENT INFRASTRUCTURE — VAPI / MODULES
# ─────────────────────────────────────────────

def update_client_vapi(
    client_id: str,
    phone_number: str = None,
    phone_number_id: str = None,
    vapi_assistant_id: str = None,
    module_1_status: str = None,
) -> dict:
    """
    Update client record with VAPI infrastructure details.
    Used when provisioning Presence Agent (Module 1).
    
    Args:
        client_id: Airtable record ID of the client
        phone_number: Real phone number (e.g., +14155238886)
        phone_number_id: VAPI phone number ID
        vapi_assistant_id: VAPI assistant ID for inbound calls
        module_1_status: Status of Presence Agent ("active", "pending", "failed")
    """
    url = f"{BASE_URL}/{BASE_PLUGGEDIN}/Clients/{client_id}"
    
    updates = {
        "Last Updated": datetime.now().isoformat(),
    }
    
    if phone_number:
        updates["VAPI Phone Number"] = phone_number
    if phone_number_id:
        updates["VAPI Phone ID"] = phone_number_id
    if vapi_assistant_id:
        updates["VAPI Assistant ID"] = vapi_assistant_id
    if module_1_status:
        updates["Module 1 Status"] = module_1_status
    
    payload = {"fields": updates}
    
    response = requests.patch(url, headers=HEADERS, json=payload)
    return response.json()


def log_inbound_call(
    base_id: str,
    client_id: str,
    caller_phone: str,
    duration_seconds: int,
    transcript: str,
    agent_action: str,
    lead_score: int = 0,
    next_action: str = "",
) -> dict:
    """
    Log an inbound call to a client's Airtable base.
    Called after each VAPI inbound call completes.
    
    agent_action: "booked", "transferred", "qualified", "voicemail", "hang_up"
    lead_score: 0-100 qualification score
    """
    url = f"{BASE_URL}/{base_id}/Inbound Calls"
    
    payload = {
        "records": [{
            "fields": {
                "Client": [client_id],
                "Caller Phone": caller_phone,
                "Duration (seconds)": duration_seconds,
                "Transcript": transcript[:1000],  # First 1000 chars
                "Agent Action": agent_action,
                "Lead Score": lead_score,
                "Next Action": next_action,
                "Received At": datetime.now().isoformat(),
            }
        }]
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    return response.json()
