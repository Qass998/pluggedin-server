"""
trade_broker.py — PluggedIN TradeBridge Brokerage Engine
Digital broker connecting global buyers and sellers.
We find the need. We find the supply. We sit in the middle. We take commission.

Two revenue models:
  TradeBridge (B2B): 1-5% commission on deal value (£10k-£2M+ deals)
  SourcedStore (Ecom): 40-70% margin on products sourced from demand signals

Deal flow:
  Demand Signal → Supplier Match → Buyer Qualification → Intro + NDA →
  Term Sheet → Deal Close → Commission Invoice

Uses:
  lib/market_intel.py — country demand signals
  lib/b2b_scanner.py  — supplier discovery
  lib/vendor_outreach.py — outreach emails
  Apify LinkedIn — buyer discovery + enrichment
"""

import os
import json
import requests
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE = os.getenv("AIRTABLE_BASE_PLUGGEDIN")
APIFY_TOKEN = os.getenv("APIFY_TOKEN")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
AIRTABLE_BASE_URL = "https://api.airtable.com/v0"
APIFY_BASE = "https://api.apify.com/v2"

import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# ─────────────────────────────────────────────
# COMMISSION STRUCTURE
# ─────────────────────────────────────────────

def calculate_commission(deal_value_gbp: float, category: str = "default") -> dict:
    """
    Calculate PluggedIN's commission on a brokered deal.
    Tiered by deal size to stay competitive on large deals.
    """
    if deal_value_gbp < 10_000:
        pct = 5.0
        tier = "micro"
    elif deal_value_gbp < 50_000:
        pct = 4.0
        tier = "small"
    elif deal_value_gbp < 200_000:
        pct = 3.0
        tier = "medium"
    elif deal_value_gbp < 500_000:
        pct = 2.0
        tier = "large"
    else:
        pct = 1.5
        tier = "major"

    # Category adjustments
    category_adjustments = {
        "pharmaceuticals_health": +0.5,   # higher risk = higher margin
        "natural_resources": -0.5,         # volume = lower margin
        "agricultural_commodities": 0,
        "construction_materials": 0,
        "industrial_machinery": +0.25,
    }
    pct += category_adjustments.get(category, 0)
    pct = max(1.0, min(6.0, pct))  # floor 1%, ceiling 6%

    commission = deal_value_gbp * (pct / 100)

    return {
        "deal_value": deal_value_gbp,
        "commission_pct": pct,
        "commission_gbp": round(commission, 2),
        "tier": tier,
        "note": f"£{commission:,.0f} at {pct}% on £{deal_value_gbp:,.0f} deal",
    }


# ─────────────────────────────────────────────
# DEAL MATCHING ENGINE
# ─────────────────────────────────────────────

def match_demand_to_supply(demand_signals: list[dict]) -> list[dict]:
    """
    For each demand signal, find matching supplier countries and
    initiate a deal opportunity record.
    """
    from lib.market_intel import find_supply_for_demand, COUNTRY_INTEL_MAP
    from lib.b2b_scanner import scan_alibaba, scan_1688, scan_tradeindia, scan_europages

    matched_deals = []

    for signal in demand_signals:
        if not signal.get("brokerage_play"):
            continue

        product = signal.get("product", "")
        buyer_country = signal.get("country", "")
        trade_category = signal.get("trade_category", "")

        print(f"[trade_broker] Matching: '{product}' needed in {buyer_country}")

        # Find countries that supply this product
        supplier_countries = find_supply_for_demand(product)

        # Also run a targeted B2B scan for this specific product
        suppliers_found = []

        # Route to best platform based on trade category
        if trade_category == "agricultural_commodities":
            # Africa/India supply chains for agri commodities
            suppliers_found.extend(scan_tradeindia([f"{product} exporter"]))
            suppliers_found.extend(scan_alibaba([f"{product} wholesale bulk"]))
        elif trade_category == "construction_materials":
            suppliers_found.extend(scan_alibaba([f"{product} manufacturer bulk order"]))
            suppliers_found.extend(scan_europages([f"{product} supplier"]))
        elif trade_category == "industrial_machinery":
            suppliers_found.extend(scan_alibaba([f"{product} manufacturer"]))
            suppliers_found.extend(scan_1688([product]))
        elif trade_category == "food_ingredients":
            suppliers_found.extend(scan_tradeindia([f"{product} exporter"]))
            suppliers_found.extend(scan_europages([f"{product} manufacturer"]))
        else:
            suppliers_found.extend(scan_alibaba([product]))

        if not suppliers_found:
            print(f"  No suppliers found for '{product}' — skipping")
            continue

        # Score match quality
        match_score = _score_deal_match(signal, suppliers_found, supplier_countries)

        # Estimate deal value from volume signal
        deal_value = _estimate_deal_value(signal)
        commission_info = calculate_commission(deal_value, trade_category)

        matched_deals.append({
            "product": product,
            "buyer_country": buyer_country,
            "trade_category": trade_category,
            "demand_urgency": signal.get("urgency", "Medium"),
            "buyer_type": signal.get("buyer_type", "SME"),
            "need_description": signal.get("need_description", ""),
            "supplier_countries": supplier_countries,
            "suppliers_found": len(suppliers_found),
            "top_supplier": suppliers_found[0] if suppliers_found else {},
            "match_score": match_score,
            "estimated_deal_value_gbp": deal_value,
            "estimated_commission_gbp": commission_info["commission_gbp"],
            "commission_pct": commission_info["commission_pct"],
            "deal_stage": "Identified",
            "discovered_at": date.today().isoformat(),
        })

        print(f"  ✓ Match found: {len(suppliers_found)} suppliers | £{deal_value:,} deal | £{commission_info['commission_gbp']:,.0f} commission")

    # Sort by estimated commission descending
    matched_deals.sort(key=lambda x: x.get("estimated_commission_gbp", 0), reverse=True)
    return matched_deals


def _score_deal_match(signal: dict, suppliers: list, supplier_countries: list) -> int:
    """Score a demand-supply match 0-100."""
    score = 0

    # Urgency
    urgency_scores = {"High": 30, "Medium": 20, "Low": 10}
    score += urgency_scores.get(signal.get("urgency", "Medium"), 20)

    # Supplier availability
    if len(suppliers) >= 5:
        score += 25
    elif len(suppliers) >= 2:
        score += 15
    elif suppliers:
        score += 8

    # Known supply route
    if supplier_countries:
        score += 20

    # Buyer type (corporate/government = bigger deals)
    buyer_scores = {"government": 25, "corporation": 20, "SME": 15, "individual": 5}
    score += buyer_scores.get(signal.get("buyer_type", "SME"), 10)

    return min(100, score)


def _estimate_deal_value(signal: dict) -> float:
    """Estimate deal value in GBP from the demand signal."""
    volume = str(signal.get("volume", "")).lower()
    product = str(signal.get("product", "")).lower()
    buyer_type = signal.get("buyer_type", "SME")

    # Try to extract a number from volume
    import re
    numbers = re.findall(r"[\d,]+", volume.replace(",", ""))
    base_number = float(numbers[0]) if numbers else 0

    # Estimate by buyer type if no volume data
    if base_number == 0:
        base_estimates = {
            "government": 500_000,
            "corporation": 100_000,
            "SME": 25_000,
            "individual": 5_000,
        }
        return base_estimates.get(buyer_type, 25_000)

    # Units → GBP conversion (rough estimates per commodity)
    unit_prices = {
        "cocoa": 3200,      # £/tonne
        "cashew": 1500,     # £/tonne
        "coffee": 2800,     # £/tonne
        "sesame": 1200,     # £/tonne
        "palm oil": 900,    # £/tonne
        "timber": 200,      # £/m3
        "steel": 600,       # £/tonne
        "cement": 120,      # £/tonne
        "copper": 8000,     # £/tonne
    }

    for commodity, price_per_unit in unit_prices.items():
        if commodity in product:
            return base_number * price_per_unit

    # Default: assume base_number is already in GBP or rough units at £100/unit
    return max(10_000, base_number * 100)


# ─────────────────────────────────────────────
# BUYER QUALIFICATION + OUTREACH
# ─────────────────────────────────────────────

def _call_claude_haiku(prompt: str, system: str = "", max_tokens: int = 600) -> str:
    from lib.ai_client import call_ai
    return call_ai("broker", system=system or "You are a professional trade broker.", prompt=prompt, max_tokens=max_tokens)


def draft_broker_introduction(
    product: str,
    buyer_country: str,
    buyer_company: str = "",
    supplier_country: str = "",
    deal_type: str = "commodity",
    estimated_value: float = 0,
    role: str = "buyer",  # or "seller"
) -> dict:
    """
    Draft an introduction email to either the buyer OR seller side of a deal.
    As broker, we reach out to each party separately, never revealing the other until NDA signed.
    """
    if role == "buyer":
        prompt = f"""
Draft a professional broker introduction email to a potential BUYER.

Context:
- We are PluggedIN TradeBridge, a digital trade brokerage
- Product: {product}
- Buyer's country: {buyer_country}
- Buyer company: {buyer_company or 'the company'}
- We have identified a verified supplier
- Estimated deal size: £{estimated_value:,.0f}

Write an email that:
1. Introduces PluggedIN TradeBridge as a commodity/trade broker
2. States we have identified a reliable supplier for {product}
3. Briefly describes what makes this supplier credible (verified, export-certified, competitive pricing)
4. Asks if they are actively seeking to purchase {product} in the next 90 days
5. Invites them to a brief call to discuss the opportunity
6. Does NOT reveal the supplier's identity yet (standard broker practice)
7. Mentions that if they proceed, our fee is built into the price (transparent but not alarming)

Tone: Professional, confident, direct. This is B2B — no fluff.
Length: 180-220 words.
Sign off from: Qassim Abdul-Karim, Trade Director, PluggedIN TradeBridge
"""
    else:
        prompt = f"""
Draft a professional broker introduction email to a potential SELLER/SUPPLIER.

Context:
- We are PluggedIN TradeBridge, a digital trade brokerage
- Product: {product}
- Supplier's country/region: {supplier_country}
- We have qualified buyers in {buyer_country}
- Estimated volume: £{estimated_value:,.0f}

Write an email that:
1. Introduces PluggedIN TradeBridge as a trade facilitator connecting suppliers with international buyers
2. States we have qualified buyers in {buyer_country} seeking {product}
3. Asks about their export capacity and whether they can supply to {buyer_country}
4. Asks for their export pricing, minimum volume, and lead time
5. Explains we handle all buyer communication, logistics coordination, and payment verification
6. Does NOT reveal the specific buyer yet
7. Our commission comes from the buyer side — this costs the seller nothing

Tone: Partnership-focused, professional, no pressure.
Length: 180-220 words.
Sign off from: Qassim Abdul-Karim, Trade Director, PluggedIN TradeBridge
"""

    body = _call_claude_haiku(prompt)

    return {
        "subject": f"Trade Opportunity — {product} {'Supply Required' if role == 'buyer' else 'Export Interest'}: {buyer_country}",
        "body": body,
        "role": role,
        "product": product,
        "estimated_value": estimated_value,
    }


def _send_email(to_email: str, subject: str, body: str, dry_run: bool = False) -> dict:
    if dry_run:
        print(f"\n[DRY RUN EMAIL → {to_email}]\nSubject: {subject}\n{body[:200]}...\n")
        return {"sent": False, "dry_run": True}
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        return {"sent": False, "error": "Missing Gmail credentials"}
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = GMAIL_USER
        msg["To"] = to_email
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())
        return {"sent": True}
    except Exception as e:
        return {"sent": False, "error": str(e)}


# ─────────────────────────────────────────────
# AIRTABLE DEAL PIPELINE
# ─────────────────────────────────────────────

DEAL_STAGES = [
    "Identified",        # demand signal found
    "SupplierFound",     # matching supplier discovered
    "BuyerIdentified",   # specific buyer company found
    "OutreachSent",      # intro emails sent to both sides
    "IntroMade",         # both parties confirmed interest
    "NDA_Signed",        # NDA executed
    "NegotiatingTerms",  # price/volume/logistics being finalised
    "DealClosed",        # deal confirmed and executing
    "CommissionInvoiced",# invoice sent to buyer
    "CommissionPaid",    # money received
    "Failed",            # deal fell through
]


def log_deal_to_airtable(deal: dict) -> dict:
    """Log or update a brokerage deal in Airtable:BrokerageDeals."""
    if not AIRTABLE_TOKEN or not AIRTABLE_BASE:
        return {"logged": False}

    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}", "Content-Type": "application/json"}
    url = f"{AIRTABLE_BASE_URL}/{AIRTABLE_BASE}/BrokerageDeals"

    record = {
        "fields": {
            "Product": deal.get("product", ""),
            "BuyerCountry": deal.get("buyer_country", ""),
            "BuyerCompany": deal.get("buyer_company", ""),
            "BuyerContact": deal.get("buyer_contact", ""),
            "SupplierCountry": str(deal.get("supplier_countries", [])),
            "SupplierName": deal.get("top_supplier", {}).get("supplier_name", ""),
            "TradeCategory": deal.get("trade_category", ""),
            "DealStage": deal.get("deal_stage", "Identified"),
            "EstimatedValue": deal.get("estimated_deal_value_gbp", 0),
            "EstimatedCommission": deal.get("estimated_commission_gbp", 0),
            "CommissionPct": deal.get("commission_pct", 0),
            "MatchScore": deal.get("match_score", 0),
            "DemandUrgency": deal.get("demand_urgency", "Medium"),
            "Notes": deal.get("need_description", "")[:500],
            "DiscoveredAt": deal.get("discovered_at", date.today().isoformat()),
            "NextAction": deal.get("next_action", "Send buyer introduction email"),
            "NextActionDue": (date.today() + timedelta(days=1)).isoformat(),
        }
    }

    # Check if record exists (by product + buyer_country)
    existing = _find_existing_deal(deal.get("product", ""), deal.get("buyer_country", ""))
    if existing:
        # Update existing
        patch_url = f"{url}/{existing}"
        resp = requests.patch(patch_url, headers=headers, json={"fields": record["fields"]}, timeout=15)
    else:
        resp = requests.post(url, headers=headers, json=record, timeout=15)

    return {"logged": resp.ok, "record_id": resp.json().get("id") if resp.ok else None}


def _find_existing_deal(product: str, buyer_country: str) -> str:
    """Find existing deal record ID in Airtable."""
    if not AIRTABLE_TOKEN or not AIRTABLE_BASE:
        return ""
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    formula = f"AND({{Product}}='{product}', {{BuyerCountry}}='{buyer_country}')"
    url = f"{AIRTABLE_BASE_URL}/{AIRTABLE_BASE}/BrokerageDeals"
    resp = requests.get(url, headers=headers, params={"filterByFormula": formula, "maxRecords": 1}, timeout=10)
    records = resp.json().get("records", []) if resp.ok else []
    return records[0]["id"] if records else ""


def update_deal_stage(record_id: str, new_stage: str, notes: str = "", commission_paid: float = 0) -> bool:
    """Update deal stage in Airtable."""
    if not AIRTABLE_TOKEN or not AIRTABLE_BASE:
        return False
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}", "Content-Type": "application/json"}
    url = f"{AIRTABLE_BASE_URL}/{AIRTABLE_BASE}/BrokerageDeals/{record_id}"
    fields = {"DealStage": new_stage, "Notes": notes, "UpdatedAt": datetime.utcnow().isoformat()}
    if commission_paid:
        fields["CommissionPaid"] = commission_paid
    resp = requests.patch(url, headers=headers, json={"fields": fields}, timeout=15)
    return resp.ok


def get_active_deals() -> list[dict]:
    """Fetch all active deals from Airtable (not Failed, not CommissionPaid)."""
    if not AIRTABLE_TOKEN or not AIRTABLE_BASE:
        return []
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    active_stages = ["Identified", "SupplierFound", "BuyerIdentified", "OutreachSent", "IntroMade", "NDA_Signed", "NegotiatingTerms", "DealClosed"]
    formula = "OR(" + ",".join([f"{{DealStage}}='{s}'" for s in active_stages]) + ")"
    url = f"{AIRTABLE_BASE_URL}/{AIRTABLE_BASE}/BrokerageDeals"
    resp = requests.get(url, headers=headers, params={"filterByFormula": formula, "maxRecords": 100}, timeout=15)
    if not resp.ok:
        return []
    return [{"id": r["id"], **r["fields"]} for r in resp.json().get("records", [])]


# ─────────────────────────────────────────────
# ECOM SOURCING (SourcedStore)
# ─────────────────────────────────────────────

def create_ecom_sourcing_brief(ecom_signals: list[dict]) -> list[dict]:
    """
    Convert ecom demand signals into sourcing briefs for the Ecommerce Agent.
    These become FBA/dropship product launches on Amazon UK.
    """
    briefs = []

    for signal in ecom_signals[:10]:
        product = signal.get("product", "")
        country = signal.get("country", "")

        prompt = f"""
Create a brief ecommerce product sourcing brief.

Demand signal: People in {country} need/want: {product}
Context: {signal.get('need_description', '')}

Write a sourcing brief covering:
PRODUCT: [refined product name — specific, searchable]
SEARCH_TERMS: [3 Amazon UK search terms customers would use]
SOURCE: [best platform to source this: Alibaba / 1688 / TradeIndia / Europages]
KEYWORDS_FOR_SCAN: [2-3 keywords to use when scanning B2B platforms]
TARGET_SELL_PRICE_GBP: [realistic Amazon UK retail price]
TARGET_SOURCE_PRICE_GBP: [target source price to achieve 50%+ margin]
LAUNCH_CHANNEL: [Amazon FBA / TikTok Shop / Shopify / all three]
UNIQUE_ANGLE: [how to position this vs existing Amazon listings]

Be specific and commercial. Numbers required.
"""
        brief_text = _call_claude_haiku(prompt)

        lines = {}
        for line in brief_text.split("\n"):
            if ":" in line:
                key, *val = line.split(":")
                lines[key.strip()] = ":".join(val).strip()

        briefs.append({
            "product": lines.get("PRODUCT", product),
            "source_signal": signal,
            "search_terms": lines.get("SEARCH_TERMS", ""),
            "source_platform": lines.get("SOURCE", "Alibaba"),
            "b2b_scan_keywords": lines.get("KEYWORDS_FOR_SCAN", product),
            "target_sell_price_gbp": lines.get("TARGET_SELL_PRICE_GBP", ""),
            "target_source_price_gbp": lines.get("TARGET_SOURCE_PRICE_GBP", ""),
            "launch_channel": lines.get("LAUNCH_CHANNEL", "Amazon FBA"),
            "unique_angle": lines.get("UNIQUE_ANGLE", ""),
            "created_at": date.today().isoformat(),
        })

    return briefs


# ─────────────────────────────────────────────
# DAILY BROKERAGE RUN
# ─────────────────────────────────────────────

def run_daily_brokerage(market_intel_summary: dict = None, dry_run: bool = False) -> dict:
    """
    Daily brokerage engine run. Called after market_intel at ~05:00.
    Takes demand signals → matches suppliers → logs deals → initiates outreach.
    Returns CEO report summary.
    """
    print(f"\n[trade_broker] Daily brokerage run — {date.today()}")

    # Get today's demand signals from Airtable
    brokerage_signals = []
    ecom_signals = []

    if AIRTABLE_TOKEN and AIRTABLE_BASE:
        headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
        url = f"{AIRTABLE_BASE_URL}/{AIRTABLE_BASE}/DemandSignals"
        params = {
            "filterByFormula": f"AND({{DiscoveredAt}}='{date.today().isoformat()}', {{Status}}='New')",
            "maxRecords": 30,
        }
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        if resp.ok:
            for r in resp.json().get("records", []):
                f = r["fields"]
                signal = {
                    "product": f.get("Product", ""),
                    "country": f.get("Country", ""),
                    "need_description": f.get("NeedDescription", ""),
                    "urgency": f.get("Urgency", "Medium"),
                    "buyer_type": f.get("BuyerType", "SME"),
                    "trade_category": f.get("TradeCategory", ""),
                    "brokerage_play": f.get("BrokeragePlay", False),
                    "ecom_play": f.get("EcomPlay", False),
                }
                if signal["brokerage_play"]:
                    brokerage_signals.append(signal)
                if signal["ecom_play"]:
                    ecom_signals.append(signal)

    # Or use passed summary
    if market_intel_summary and not brokerage_signals:
        brokerage_signals = market_intel_summary.get("top_brokerage", [])
        ecom_signals = market_intel_summary.get("top_ecom", [])

    print(f"  Processing {len(brokerage_signals)} brokerage + {len(ecom_signals)} ecom signals")

    # Match demand to supply
    matched_deals = match_demand_to_supply(brokerage_signals[:5])  # cap at 5/day

    # Log deals and draft outreach
    deals_logged = 0
    emails_drafted = 0
    total_commission_potential = 0

    for deal in matched_deals:
        if deal.get("match_score", 0) >= 50:
            # Log to Airtable
            if not dry_run:
                log_deal_to_airtable(deal)
                deals_logged += 1

            # Draft introduction emails
            seller_email = draft_broker_introduction(
                product=deal["product"],
                buyer_country=deal["buyer_country"],
                supplier_country=str(deal.get("supplier_countries", ["Unknown"])),
                deal_type=deal.get("trade_category", "commodity"),
                estimated_value=deal.get("estimated_deal_value_gbp", 0),
                role="seller"
            )
            buyer_email = draft_broker_introduction(
                product=deal["product"],
                buyer_country=deal["buyer_country"],
                deal_type=deal.get("trade_category", "commodity"),
                estimated_value=deal.get("estimated_deal_value_gbp", 0),
                role="buyer"
            )
            emails_drafted += 2

            total_commission_potential += deal.get("estimated_commission_gbp", 0)

            if dry_run:
                print(f"  [DRY RUN] Deal: {deal['product']} | {deal['buyer_country']} | Score: {deal['match_score']} | Commission: £{deal.get('estimated_commission_gbp', 0):,.0f}")

    # Generate ecom sourcing briefs
    ecom_briefs = create_ecom_sourcing_brief(ecom_signals[:5])

    # Log ecom briefs to Airtable (EcomSourcingBriefs table)
    if not dry_run and ecom_briefs and AIRTABLE_TOKEN and AIRTABLE_BASE:
        headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}", "Content-Type": "application/json"}
        for brief in ecom_briefs:
            record = {
                "fields": {
                    "Product": brief["product"],
                    "SearchTerms": brief["search_terms"],
                    "SourcePlatform": brief["source_platform"],
                    "ScanKeywords": brief["b2b_scan_keywords"],
                    "TargetSellPrice": str(brief["target_sell_price_gbp"]),
                    "TargetSourcePrice": str(brief["target_source_price_gbp"]),
                    "LaunchChannel": brief["launch_channel"],
                    "UniqueAngle": brief["unique_angle"],
                    "Status": "Pending",
                    "CreatedAt": brief["created_at"],
                }
            }
            requests.post(
                f"{AIRTABLE_BASE_URL}/{AIRTABLE_BASE}/EcomSourcingBriefs",
                headers=headers, json=record, timeout=15
            )

    # Get current pipeline stats
    active_deals = get_active_deals()
    pipeline_value = sum(d.get("EstimatedCommission", 0) for d in active_deals)
    closed_this_month = [d for d in active_deals if d.get("DealStage") in ("DealClosed", "CommissionInvoiced", "CommissionPaid")]

    return {
        "date": str(date.today()),
        "brokerage_signals_processed": len(brokerage_signals),
        "ecom_signals_processed": len(ecom_signals),
        "deals_matched": len(matched_deals),
        "deals_logged": deals_logged,
        "emails_drafted": emails_drafted,
        "new_commission_potential": round(total_commission_potential, 2),
        "total_pipeline_commission": round(pipeline_value, 2),
        "active_deals": len(active_deals),
        "closed_this_month": len(closed_this_month),
        "ecom_briefs_created": len(ecom_briefs),
        "top_deals": matched_deals[:3],
    }


def get_brokerage_ceo_summary() -> str:
    """Generate a CEO briefing block for the brokerage pipeline."""
    active = get_active_deals()
    pipeline_value = sum(d.get("EstimatedCommission", 0) for d in active)
    hot = [d for d in active if d.get("DealStage") in ("IntroMade", "NDA_Signed", "NegotiatingTerms")]
    closed = [d for d in active if d.get("DealStage") in ("DealClosed", "CommissionPaid")]

    return {
        "active_deals": len(active),
        "pipeline_commission_gbp": round(pipeline_value, 2),
        "hot_deals": len(hot),
        "closed_deals": len(closed),
        "summary": (
            f"Pipeline: {len(active)} active deals | "
            f"£{pipeline_value:,.0f} commission potential | "
            f"{len(hot)} deals in negotiation | "
            f"{len(closed)} closed"
        )
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--match", type=str, help="Match a specific product to suppliers")
    parser.add_argument("--commission", type=float, help="Calculate commission on deal value")
    parser.add_argument("--category", type=str, default="default")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.match:
        from lib.market_intel import find_supply_for_demand
        countries = find_supply_for_demand(args.match)
        print(f"Supply countries for '{args.match}': {countries}")
    elif args.commission:
        info = calculate_commission(args.commission, args.category)
        print(json.dumps(info, indent=2))
    else:
        summary = run_daily_brokerage(dry_run=args.dry_run)
        print(json.dumps(summary, indent=2))
