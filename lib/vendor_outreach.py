"""
vendor_outreach.py — PluggedIN Vendor Correspondence Engine
Automates outreach to manufacturers, distributors, and white-label suppliers
found by b2b_scanner.py. Drafts personalised emails, tracks responses,
and manages the correspondence pipeline.

Plays supported:
  1. UK/EU Exclusive Distributor — "We want to be your UK partner"
  2. White-Label Deal — "Manufacture this under our brand"
  3. Drop-Ship Agreement — "Ship direct to our customers"
  4. Commodity Purchase — "We're a buyer for X tonnes"
  5. Joint Venture Inquiry — "We market, you fulfil, we split"
"""

import os
import json
import smtplib
import requests
from datetime import datetime, date, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE = os.getenv("AIRTABLE_BASE_PLUGGEDIN")
AIRTABLE_BASE_URL = "https://api.airtable.com/v0"

# ─────────────────────────────────────────────
# EMAIL TEMPLATES (Claude-generated, personalised per outreach)
# ─────────────────────────────────────────────

OUTREACH_TEMPLATES = {

    "exclusive_distributor": {
        "subject": "UK Distribution Partnership Inquiry — {product_category}",
        "context": """
You are writing a professional B2B outreach email on behalf of PluggedIN,
a UK-based trade and distribution company looking to establish exclusive
distribution partnerships for quality products in the UK market.

Tone: Professional, direct, warm. NOT salesy. You're a serious buyer.
Length: 150-200 words max. Short paragraphs.
Goal: Get a response expressing interest in discussing a distribution deal.

Details to personalise:
- Supplier name: {supplier_name}
- Product/category: {product_category}
- Their location/country: {location}
- Specific product of interest: {specific_product}

The email should:
1. Introduce PluggedIN as a UK distribution partner (not an agency)
2. Reference their specific product/category
3. Express interest in exclusive UK distribution rights
4. Mention our UK market reach and distribution capability
5. Request a brief call or email exchange to discuss terms
6. Include a professional sign-off from Qassim Abdul-Karim, Director

Do NOT mention pricing yet. Do NOT use generic phrases like "I hope this email finds you well."
""",
    },

    "white_label": {
        "subject": "White-Label Manufacturing Inquiry — {product_category}",
        "context": """
You are writing a professional white-label manufacturing inquiry email on behalf
of PluggedIN, a UK brand looking to launch a private-label product line.

Tone: Professional, concise, buyer-led. You have budget and a brand ready.
Length: 150-200 words.
Goal: Get a response about their OEM/white-label capabilities.

Details:
- Supplier name: {supplier_name}
- Product they make: {product_category}
- Specific product: {specific_product}
- Their platform: {platform}

The email should:
1. State we're a UK brand seeking a manufacturing partner for private label
2. Reference their specific product we found
3. Ask about their OEM/white-label/custom branding capabilities
4. Ask about MOQ for branded production
5. Ask for their product catalogue or spec sheet
6. Professional sign-off from Qassim Abdul-Karim, Brand Director

Be specific. Mention the product. Don't be vague.
""",
    },

    "dropship_agreement": {
        "subject": "Drop-Shipping Partnership Proposal — {product_category}",
        "context": """
You are writing a drop-shipping partnership proposal email on behalf of PluggedIN,
a UK ecommerce operator with multiple active channels.

Tone: Business-focused, efficient. You know what you want.
Length: 150-200 words.
Goal: Establish if they drop-ship and what their terms are.

Details:
- Supplier: {supplier_name}
- Product category: {product_category}
- Their platform source: {platform}

The email should:
1. Identify PluggedIN as a UK ecommerce operator (Amazon, Shopify, TikTok Shop)
2. Express interest in a drop-shipping arrangement
3. Ask: Do they offer drop-shipping? What are integration options (API/manual)?
4. Ask about their UK shipping times and packaging options
5. Ask if they offer branded packaging for drop-ship
6. Sign-off from Qassim Abdul-Karim, Operations Director
""",
    },

    "commodity_buyer": {
        "subject": "Commodity Purchase Inquiry — {product_category}",
        "context": """
You are writing a commodity purchase inquiry on behalf of PluggedIN AgriTrade,
a commodity trading division dealing in agricultural products.

Tone: Very professional, formal. Commodity trading is serious business.
Length: 150-200 words.
Goal: Establish if they can supply at commercial volume.

Details:
- Supplier: {supplier_name}
- Commodity: {product_category}
- Location: {location}
- Volume interest: {volume}

The email should:
1. Introduce PluggedIN AgriTrade as a commodity trader and distributor
2. State the specific commodity and volume we're interested in purchasing
3. Ask for their current price per tonne/unit (CIF or FOB UK)
4. Ask for product specification/grading documents
5. Ask about payment terms and delivery lead time
6. Professional sign-off from Qassim Abdul-Karim, Trade Director
""",
    },

    "joint_venture": {
        "subject": "Joint Venture Proposal — UK Market Expansion for {product_category}",
        "context": """
You are writing a joint venture proposal on behalf of PluggedIN,
proposing a partnership where the supplier handles fulfilment and
PluggedIN handles UK marketing, sales, and distribution.

Tone: Entrepreneurial, collaborative, confident. Not corporate.
Length: 180-220 words.
Goal: Open a conversation about a revenue-share partnership.

Details:
- Supplier: {supplier_name}
- Their product: {product_category}
- Location: {location}

The email should:
1. Open by referencing their product directly — be specific
2. Propose a joint venture: we market and sell in the UK, they supply
3. Suggest a revenue-share model (we keep 40-60%, they supply at cost)
4. Highlight why this is low-risk for them: they just ship what we sell
5. Reference our UK market presence and digital marketing capability
6. Invite them to a brief call to explore the idea
7. Sign-off from Qassim Abdul-Karim, Director
""",
    },
}


# ─────────────────────────────────────────────
# EMAIL GENERATOR (Claude API)
# ─────────────────────────────────────────────

def draft_outreach_email(
    play_type: str,
    supplier_name: str,
    product_category: str,
    specific_product: str = "",
    location: str = "",
    platform: str = "",
    volume: str = "1-5 tonnes per month",
    custom_notes: str = "",
) -> dict:
    """
    Use Claude Haiku to draft a personalised outreach email.
    Returns: {subject, body, play_type, supplier_name}
    """
    template = OUTREACH_TEMPLATES.get(play_type, OUTREACH_TEMPLATES["exclusive_distributor"])

    # Format the context prompt
    context = template["context"].format(
        supplier_name=supplier_name,
        product_category=product_category,
        specific_product=specific_product or product_category,
        location=location or "your region",
        platform=platform or "your platform",
        volume=volume,
    )

    subject = template["subject"].format(product_category=product_category)

    prompt = f"""
{context}

Additional notes to incorporate: {custom_notes if custom_notes else 'None'}

Write ONLY the email body. No subject line. No "Subject:" prefix.
Start directly with the opening line.
"""

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 500,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        from lib.ai_client import call_ai
        body = call_ai("outreach", system="You are a B2B outreach specialist.", prompt=prompt, max_tokens=500)
    except Exception as e:
        body = f"[Email generation failed: {e}]"

    return {
        "subject": subject,
        "body": body,
        "play_type": play_type,
        "supplier_name": supplier_name,
        "product_category": product_category,
    }


def draft_followup_email(
    original_email: dict,
    days_since_sent: int,
    follow_up_number: int = 1,
) -> dict:
    """
    Draft a follow-up to an unanswered outreach email.
    follow_up_number: 1 = gentle nudge, 2 = final attempt.
    """
    if follow_up_number == 1:
        tone = "polite, brief, just checking in"
        length = "3-4 sentences max"
    else:
        tone = "final attempt, keep the door open, no pressure"
        length = "2-3 sentences"

    prompt = f"""
Draft a follow-up email (follow-up #{follow_up_number}) to an unanswered B2B outreach email.

Original email context:
- Supplier: {original_email.get('supplier_name')}
- About: {original_email.get('product_category')}
- Play type: {original_email.get('play_type')}
- Days since sent: {days_since_sent}

Tone: {tone}
Length: {length}

Just write the email body. Start with something like "I wanted to follow up on..." or similar.
Sign off from Qassim Abdul-Karim.
"""
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 200,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        from lib.ai_client import call_ai
        body = call_ai("outreach", system="You are a B2B outreach specialist.", prompt=prompt, max_tokens=200)
    except Exception as e:
        body = f"[Follow-up generation failed: {e}]"

    return {
        "subject": f"Re: {original_email.get('subject', '')}",
        "body": body,
        "play_type": original_email.get("play_type"),
        "supplier_name": original_email.get("supplier_name"),
        "follow_up_number": follow_up_number,
    }


# ─────────────────────────────────────────────
# EMAIL SENDER
# ─────────────────────────────────────────────

def send_email(to_email: str, subject: str, body: str, dry_run: bool = False) -> dict:
    """
    Send email via Gmail SMTP.
    Requires GMAIL_USER and GMAIL_APP_PASSWORD in .env.
    dry_run=True prints instead of sending.
    """
    if dry_run:
        print(f"\n[DRY RUN] Would send to: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body:\n{body}\n")
        return {"sent": False, "dry_run": True, "to": to_email}

    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        return {"sent": False, "error": "Missing GMAIL_USER or GMAIL_APP_PASSWORD in .env"}

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = GMAIL_USER
        msg["To"] = to_email
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())

        return {"sent": True, "to": to_email, "subject": subject}
    except Exception as e:
        return {"sent": False, "error": str(e)}


# ─────────────────────────────────────────────
# AIRTABLE OUTREACH TRACKER
# ─────────────────────────────────────────────

def log_outreach(
    supplier_name: str,
    contact_email: str,
    play_type: str,
    product: str,
    email_subject: str,
    status: str = "Sent",
) -> dict:
    """Log outreach email to Airtable:VendorOutreach table."""
    if not AIRTABLE_TOKEN or not AIRTABLE_BASE:
        return {"logged": False, "error": "Missing Airtable credentials"}

    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }
    record = {
        "fields": {
            "SupplierName": supplier_name,
            "ContactEmail": contact_email,
            "PlayType": play_type,
            "Product": product,
            "EmailSubject": email_subject,
            "Status": status,
            "SentAt": datetime.utcnow().isoformat(),
            "FollowUp1Due": (date.today() + timedelta(days=4)).isoformat(),
            "FollowUp2Due": (date.today() + timedelta(days=9)).isoformat(),
        }
    }

    url = f"{AIRTABLE_BASE_URL}/{AIRTABLE_BASE}/VendorOutreach"
    resp = requests.post(url, headers=headers, json=record, timeout=15)
    return {"logged": resp.ok, "record_id": resp.json().get("id") if resp.ok else None}


def get_followups_due() -> list[dict]:
    """
    Fetch outreach records from Airtable where follow-up is due today.
    Returns list of records needing follow-up.
    """
    if not AIRTABLE_TOKEN or not AIRTABLE_BASE:
        return []

    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    today = date.today().isoformat()

    # Check Follow-Up 1 due
    url = f"{AIRTABLE_BASE_URL}/{AIRTABLE_BASE}/VendorOutreach"
    params = {
        "filterByFormula": f"AND(OR(FollowUp1Due='{today}', FollowUp2Due='{today}'), Status='Sent')",
        "maxRecords": 50,
    }

    resp = requests.get(url, headers=headers, params=params, timeout=15)
    if not resp.ok:
        return []

    records = resp.json().get("records", [])
    return [{"id": r["id"], **r["fields"]} for r in records]


def update_outreach_status(record_id: str, status: str, notes: str = "") -> bool:
    """Update the status of an outreach record in Airtable."""
    if not AIRTABLE_TOKEN or not AIRTABLE_BASE:
        return False

    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }
    url = f"{AIRTABLE_BASE_URL}/{AIRTABLE_BASE}/VendorOutreach/{record_id}"
    data = {"fields": {"Status": status, "Notes": notes, "UpdatedAt": datetime.utcnow().isoformat()}}
    resp = requests.patch(url, headers=headers, json=data, timeout=15)
    return resp.ok


# ─────────────────────────────────────────────
# OUTREACH CAMPAIGNS (batch)
# ─────────────────────────────────────────────

def run_outreach_from_scan(
    scan_results: list[dict],
    play_type: str = "exclusive_distributor",
    max_emails: int = 10,
    dry_run: bool = False,
) -> dict:
    """
    Take scored opportunities from b2b_scanner, draft and send outreach emails.
    Only contacts suppliers with score ≥70 and a contact URL/email.

    For suppliers without a direct email, logs them as "NeedsManualContact"
    so Qassim can reach out via the platform's messaging system.
    """
    sent = 0
    manual_needed = []
    failed = []

    # Filter to pursue-worthy opportunities
    targets = [r for r in scan_results if r.get("opportunity_score", 0) >= 70][:max_emails]
    print(f"[vendor_outreach] {len(targets)} targets identified for {play_type} outreach")

    for target in targets:
        supplier = target.get("supplier_name", target.get("company_name", "Supplier"))
        product = target.get("product_name", target.get("products", "your products"))
        location = target.get("location", target.get("country", ""))
        platform = target.get("platform", "")
        url = target.get("url", "")

        # Draft the email
        email = draft_outreach_email(
            play_type=play_type,
            supplier_name=supplier,
            product_category=product[:80] if product else "your product range",
            specific_product=product[:80] if product else "",
            location=location,
            platform=platform,
        )

        # Most B2B directory listings don't expose email directly
        # We flag them for manual contact via platform messenger
        contact_email = target.get("email", "")

        if contact_email:
            result = send_email(contact_email, email["subject"], email["body"], dry_run=dry_run)
            if result.get("sent") or dry_run:
                sent += 1
                log_outreach(supplier, contact_email, play_type, product, email["subject"])
                print(f"  ✓ Sent to: {supplier} ({contact_email})")
            else:
                failed.append({"supplier": supplier, "error": result.get("error")})
        else:
            # No email — needs platform messenger or LinkedIn approach
            manual_needed.append({
                "supplier": supplier,
                "platform": platform,
                "url": url,
                "suggested_email": email,
                "note": "Use platform messenger or contact form at URL above",
            })

    return {
        "sent": sent,
        "manual_contact_needed": len(manual_needed),
        "failed": len(failed),
        "manual_targets": manual_needed[:5],  # top 5 for WhatsApp briefing
        "dry_run": dry_run,
    }


def run_followup_sequence(dry_run: bool = False) -> dict:
    """
    Check for outreach records due follow-up today and send them.
    Called by orchestrator as part of daily vendor routine.
    """
    due = get_followups_due()
    print(f"[vendor_outreach] {len(due)} follow-ups due today")

    sent = 0
    for record in due:
        # Determine follow-up number
        follow_up_num = 1 if record.get("FollowUp1Due") == str(date.today()) else 2

        original = {
            "subject": record.get("EmailSubject", ""),
            "supplier_name": record.get("SupplierName", ""),
            "product_category": record.get("Product", ""),
            "play_type": record.get("PlayType", ""),
        }
        days_since = 4 if follow_up_num == 1 else 9

        followup_email = draft_followup_email(original, days_since, follow_up_num)

        contact_email = record.get("ContactEmail", "")
        if contact_email:
            result = send_email(contact_email, followup_email["subject"], followup_email["body"], dry_run=dry_run)
            if result.get("sent") or dry_run:
                sent += 1
                status = f"FollowUp{follow_up_num}Sent"
                update_outreach_status(record.get("id"), status)
                print(f"  ✓ Follow-up #{follow_up_num} sent to: {record.get('SupplierName')}")

    return {"followups_sent": sent, "due": len(due)}


# ─────────────────────────────────────────────
# RESPONSE TRACKER (manual update)
# ─────────────────────────────────────────────

def log_supplier_response(
    record_id: str,
    response_type: str,  # "Interested" | "NotInterested" | "RequestingInfo" | "NeedsCall"
    notes: str = "",
) -> dict:
    """
    Log a supplier's response to outreach. Call this when Qassim
    receives a reply and wants to update the pipeline.
    Moves the record to the appropriate next stage.
    """
    status_map = {
        "Interested": "SupplierInterested",
        "NotInterested": "Rejected",
        "RequestingInfo": "InfoRequested",
        "NeedsCall": "CallScheduled",
    }
    status = status_map.get(response_type, "Replied")
    updated = update_outreach_status(record_id, status, notes)
    return {"updated": updated, "new_status": status}


def get_outreach_summary() -> dict:
    """Return current state of the vendor outreach pipeline."""
    if not AIRTABLE_TOKEN or not AIRTABLE_BASE:
        return {}

    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    url = f"{AIRTABLE_BASE_URL}/{AIRTABLE_BASE}/VendorOutreach"
    resp = requests.get(url, headers=headers, params={"maxRecords": 100}, timeout=15)

    if not resp.ok:
        return {}

    records = [r["fields"] for r in resp.json().get("records", [])]
    statuses = {}
    for r in records:
        s = r.get("Status", "Unknown")
        statuses[s] = statuses.get(s, 0) + 1

    return {
        "total_outreach": len(records),
        "by_status": statuses,
        "interested": statuses.get("SupplierInterested", 0),
        "in_conversation": statuses.get("InfoRequested", 0) + statuses.get("CallScheduled", 0),
        "deals_in_progress": statuses.get("Negotiating", 0),
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--draft", type=str, help="Draft an outreach email for a supplier name")
    parser.add_argument("--play", type=str, default="exclusive_distributor")
    parser.add_argument("--product", type=str, default="health products")
    parser.add_argument("--followups", action="store_true", help="Run today's follow-up sequence")
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.draft:
        email = draft_outreach_email(
            play_type=args.play,
            supplier_name=args.draft,
            product_category=args.product,
        )
        print(f"\nSubject: {email['subject']}\n\n{email['body']}")
    elif args.followups:
        result = run_followup_sequence(dry_run=args.dry_run)
        print(json.dumps(result, indent=2))
    elif args.summary:
        print(json.dumps(get_outreach_summary(), indent=2))
