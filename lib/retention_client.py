"""
lib/retention_client.py — Customer Retention OS Wrapper
PluggedIN Module 9 + Module 1 (WhatsApp inbound).
Never call Twilio/WhatsApp directly. Use this.
Covers: loyalty stamps, churn detection, win-back campaigns,
        review management, seasonal campaigns, inbound WhatsApp.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Optional
from anthropic import Anthropic

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE = os.getenv("AIRTABLE_BASE_PLUGGEDIN")

CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")
claude_client = Anthropic(api_key=CLAUDE_API_KEY)


# ─────────────────────────────────────────────
# WHATSAPP MESSAGING (via Twilio)
# ─────────────────────────────────────────────

def send_whatsapp(
    to_number: str,
    message: str,
    media_url: str = None,
) -> dict:
    """
    Send a WhatsApp message via Twilio.
    to_number: international format e.g. "+447700900000"
    media_url: optional image URL for rich messages
    """
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
    payload = {
        "From": TWILIO_WHATSAPP_FROM,
        "To": f"whatsapp:{to_number}",
        "Body": message,
    }
    if media_url:
        payload["MediaUrl"] = media_url

    r = requests.post(
        url,
        data=payload,
        auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
    )
    r.raise_for_status()
    return r.json()


def send_bulk_whatsapp(
    recipients: list[dict],
    message_template: str,
    personalise: bool = True,
) -> list[dict]:
    """
    Send WhatsApp to a list of recipients.
    recipients: list of {"name": str, "phone": str, "extra": dict}
    message_template: use {name} for personalisation
    Returns list of send results.
    """
    results = []
    for recipient in recipients:
        if personalise:
            msg = message_template.format(
                name=recipient.get("name", "there"),
                **recipient.get("extra", {}),
            )
        else:
            msg = message_template

        try:
            result = send_whatsapp(recipient["phone"], msg)
            results.append({"phone": recipient["phone"], "status": "sent", "sid": result.get("sid")})
        except Exception as e:
            results.append({"phone": recipient["phone"], "status": "failed", "error": str(e)})

    return results


# ─────────────────────────────────────────────
# LOYALTY STAMP SYSTEM
# ─────────────────────────────────────────────

def issue_loyalty_stamp(
    customer_phone: str,
    customer_name: str,
    business_name: str,
    stamps_total: int,
    stamps_needed: int,
    reward: str = "a free item",
    airtable_record_id: str = None,
) -> dict:
    """
    Send a loyalty stamp WhatsApp message.
    Shows progress toward reward.
    Updates Airtable record if ID provided.
    """
    bar = "⭐" * stamps_total + "⬜" * (stamps_needed - stamps_total)
    message = (
        f"Hi {customer_name}! 👋\n\n"
        f"Thanks for visiting {business_name}.\n"
        f"Here's your loyalty stamp:\n\n"
        f"{bar}\n\n"
        f"{stamps_total}/{stamps_needed} stamps\n"
    )
    if stamps_total >= stamps_needed:
        message += (
            f"🎉 Congratulations! You've earned {reward}!\n"
            f"Show this message on your next visit to claim it."
        )
    else:
        remaining = stamps_needed - stamps_total
        message += f"Just {remaining} more stamps to earn {reward}!"

    result = send_whatsapp(customer_phone, message)

    if airtable_record_id:
        _update_airtable_stamps(airtable_record_id, stamps_total)

    return result


def _update_airtable_stamps(record_id: str, stamp_count: int):
    """Internal: update stamp count in Airtable."""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE}/Customers/{record_id}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"fields": {"Stamps": stamp_count, "LastStampDate": datetime.utcnow().isoformat()}}
    requests.patch(url, json=payload, headers=headers)


def check_reward_eligibility(
    customer_phone: str,
    stamps_needed: int = 10,
) -> bool:
    """
    Check if a customer has reached the stamp threshold.
    Queries Airtable by phone number.
    """
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE}/Customers"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    params = {"filterByFormula": f"{{Phone}} = '{customer_phone}'", "maxRecords": 1}
    r = requests.get(url, headers=headers, params=params)
    records = r.json().get("records", [])
    if not records:
        return False
    stamps = records[0]["fields"].get("Stamps", 0)
    return stamps >= stamps_needed


# ─────────────────────────────────────────────
# CHURN DETECTION
# ─────────────────────────────────────────────

def find_at_risk_customers(
    business_base_id: str,
    days_inactive: int = 30,
    min_visits: int = 3,
) -> list[dict]:
    """
    Identify customers who haven't visited in X days
    but previously were regulars (min_visits threshold).
    Returns list of at-risk customers for win-back.
    """
    cutoff = (datetime.utcnow() - timedelta(days=days_inactive)).isoformat()
    url = f"https://api.airtable.com/v0/{business_base_id}/Customers"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    formula = (
        f"AND("
        f"IS_BEFORE({{LastVisit}}, '{cutoff}'), "
        f"{{TotalVisits}} >= {min_visits}"
        f")"
    )
    params = {"filterByFormula": formula, "maxRecords": 500}
    r = requests.get(url, headers=headers, params=params)
    records = r.json().get("records", [])

    at_risk = []
    for rec in records:
        f = rec["fields"]
        at_risk.append({
            "record_id": rec["id"],
            "name": f.get("Name", ""),
            "phone": f.get("Phone", ""),
            "last_visit": f.get("LastVisit", ""),
            "total_visits": f.get("TotalVisits", 0),
            "days_since_visit": (
                datetime.utcnow() - datetime.fromisoformat(f["LastVisit"].replace("Z", ""))
            ).days if f.get("LastVisit") else 999,
        })

    return sorted(at_risk, key=lambda x: x["days_since_visit"], reverse=True)


def send_winback_campaign(
    customers: list[dict],
    business_name: str,
    offer: str,
    offer_expiry: str,
) -> dict:
    """
    Send personalised win-back WhatsApp to at-risk customers.
    customers: output from find_at_risk_customers()
    offer: e.g. "20% off your next visit"
    offer_expiry: e.g. "this weekend only"
    Returns summary of sends.
    """
    template = (
        f"Hi {{name}}, we've missed you at {business_name}! 💛\n\n"
        f"It's been a while and we'd love to see you back.\n\n"
        f"Here's a special offer just for you:\n"
        f"🎁 {offer}\n"
        f"Valid: {offer_expiry}\n\n"
        f"No code needed — just show this message when you visit."
    )

    recipients = [
        {"name": c["name"], "phone": c["phone"]}
        for c in customers
        if c.get("phone")
    ]

    results = send_bulk_whatsapp(recipients, template)
    sent = sum(1 for r in results if r["status"] == "sent")
    failed = len(results) - sent

    return {
        "campaign": "win_back",
        "total_targeted": len(customers),
        "sent": sent,
        "failed": failed,
        "offer": offer,
    }


# ─────────────────────────────────────────────
# REVIEW MANAGEMENT
# ─────────────────────────────────────────────

def get_recent_reviews(
    place_id: str,
    min_rating: int = None,
    max_rating: int = None,
) -> list[dict]:
    """
    Fetch recent Google reviews for a business.
    Requires Google Places API key in env.
    Filter by rating range if provided.
    """
    GOOGLE_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "reviews",
        "key": GOOGLE_API_KEY,
    }
    r = requests.get(url, params=params)
    reviews = r.json().get("result", {}).get("reviews", [])

    if min_rating:
        reviews = [rv for rv in reviews if rv.get("rating", 5) >= min_rating]
    if max_rating:
        reviews = [rv for rv in reviews if rv.get("rating", 5) <= max_rating]

    return reviews


def draft_review_response(
    review_text: str,
    rating: int,
    business_name: str,
    business_type: str = "business",
) -> str:
    """
    Generate a professional response to a Google review.
    Uses Claude (Haiku for speed) via direct API call.
    """
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    tone = "warm and grateful" if rating >= 4 else "empathetic and solution-focused"
    prompt = (
        f"Write a professional response to this {rating}-star review for {business_name} "
        f"({business_type}). Tone: {tone}. Keep it under 100 words. "
        f"Do not use corporate jargon. Sound like a real person.\n\n"
        f"Review: {review_text}"
    )

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def flag_review_for_removal(
    review_url: str,
    review_text: str,
    reason: str,
    business_name: str,
) -> dict:
    """
    Log a review for manual removal process.
    Saves to Airtable with removal reason and status.
    reason: "fake", "competitor", "violates_policy", "defamatory"
    """
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE}/ReviewRemoval"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "fields": {
            "Business": business_name,
            "ReviewURL": review_url,
            "ReviewText": review_text,
            "RemovalReason": reason,
            "Status": "Pending",
            "FlaggedAt": datetime.utcnow().isoformat(),
        }
    }
    r = requests.post(url, json=payload, headers=headers)
    r.raise_for_status()
    return r.json()


# ─────────────────────────────────────────────
# SEASONAL CAMPAIGNS
# ─────────────────────────────────────────────

def launch_seasonal_campaign(
    business_name: str,
    season: str,
    offer: str,
    loyalty_list: list[dict],
    media_url: str = None,
) -> dict:
    """
    Broadcast seasonal campaign to full loyalty list.
    season: "Christmas", "Ramadan", "Valentine's Day", etc.
    loyalty_list: list of {"name": str, "phone": str}
    Returns send summary.
    """
    template = (
        f"🎉 {season} Special from {business_name}!\n\n"
        f"Hi {{name}},\n\n"
        f"To celebrate {season}, we've got something special for you:\n\n"
        f"✨ {offer}\n\n"
        f"Limited time only. Show this message to redeem.\n\n"
        f"Thank you for your loyalty 💛"
    )
    results = send_bulk_whatsapp(loyalty_list, template, personalise=True)
    sent = sum(1 for r in results if r["status"] == "sent")

    return {
        "campaign": f"seasonal_{season.lower().replace(' ', '_')}",
        "business": business_name,
        "sent": sent,
        "total": len(loyalty_list),
        "offer": offer,
    }


# ─────────────────────────────────────────────
# RETENTION ANALYTICS
# ─────────────────────────────────────────────

def retention_summary(
    business_base_id: str,
    period_days: int = 30,
) -> dict:
    """
    Pull retention KPIs for the last N days.
    Returns: total customers, active, at-risk, churned,
             stamps issued, win-back sent.
    """
    url = f"https://api.airtable.com/v0/{business_base_id}/Customers"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    r = requests.get(url, headers=headers, params={"maxRecords": 1000})
    records = r.json().get("records", [])

    now = datetime.utcnow()
    active_cutoff = now - timedelta(days=30)
    at_risk_cutoff = now - timedelta(days=60)

    total = len(records)
    active = 0
    at_risk = 0
    churned = 0

    for rec in records:
        last_visit_str = rec["fields"].get("LastVisit")
        if not last_visit_str:
            churned += 1
            continue
        last_visit = datetime.fromisoformat(last_visit_str.replace("Z", ""))
        if last_visit >= active_cutoff:
            active += 1
        elif last_visit >= at_risk_cutoff:
            at_risk += 1
        else:
            churned += 1

    return {
        "period_days": period_days,
        "total_customers": total,
        "active": active,
        "at_risk": at_risk,
        "churned": churned,
        "retention_rate": f"{(active / total * 100):.1f}%" if total > 0 else "0%",
    }
